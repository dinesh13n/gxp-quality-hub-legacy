"""R2 search service (OP-REV-03, BEH-REV-03..06, AC-REV-09..17; INC-09) over the derived corpus in the hub store.

Additive subclass of the INC-08 fallback `hub.review.search.SearchService` (that module is frozen): same roles, same fixed grammar, same error
codes, same hit shape. Two engines, chosen at run time by hub.search.fts.select:
  fts5      `search.fts = auto` AND FTS5 + trigram available AND the derived index built. Candidate rows come from `search_fts MATCH ?` (every term
            and phrase double-quoted inside ONE bound parameter: OR / NOT / NEAR / * / : have no effect) joined to search_doc with the access and
            field filters in the same SQL; CJK terms use `search_tri MATCH ?` (>= 3 characters) or instr() on the folded text (1-2 characters).
            Rank = bm25(search_fts).
  fallback  everything else: the same filters in Python over search_doc and the same bm25 formula (hub.search.text.bm25, whole-corpus statistics
            exactly as FTS5 computes them), so both engines return the same order.
Order: bm25 (rounded to 1e-9) ascending, then effective_at descending, then doc_id. Access first: rows the caller may not read are excluded in the
query, before ranking and counting; totals never include them. C3 rule (BEH-SEC-10, MA-2): when the PERMITTED result contains restricted rows,
a non-empty `reason` is required (E-SEC-REASON-REQUIRED, nothing returned) and the read is audited with the reason (C3_READ). No answer / summary /
recommendation field exists. No generation, no model call.
"""
import html
import re
import sqlite3

from hub.decision import access
from hub.review import search as rsearch
from hub.review.errors import QueryInvalid, QueryTooLong, SearchDisabled
from hub.search import fts, schema, settings as ssettings, text
from hub.security import audit
from hub.security.errors import AuthForbidden, AuthUnauthenticated

FIELDS = rsearch.FIELDS
_FIELD_COL = {"ref": "reference", "doc": "doc_id", "locale": "locale", "version": "version"}


def parse_query(query):
    """INC-08 grammar with the INC-09 token rule -> {terms: [str], phrases: [[str]], cjk: [str], filters: {}}."""
    if not isinstance(query, str) or not query.strip():
        raise QueryInvalid({"reason": "empty query"})
    if len(query) > rsearch.MAX_CHARS:
        raise QueryTooLong({"length": len(query), "limit": rsearch.MAX_CHARS})
    if query.count('"') % 2:
        raise QueryInvalid({"reason": "unbalanced double quote"})
    parts = re.findall(r'"[^"]*"|\S+', query)
    if len(parts) > rsearch.MAX_TERMS:
        raise QueryTooLong({"terms": len(parts), "limit": rsearch.MAX_TERMS})
    terms, phrases, cjk, flt = [], [], [], {}
    for p in parts:
        if p.startswith('"'):
            inner = p[1:-1]
            if text.is_cjk(inner):
                c = text.fold(inner).strip()
                if not c:
                    raise QueryInvalid({"reason": "empty phrase"})
                cjk.append(c)
                continue
            tk = text.tokens(inner)
            if not tk:
                raise QueryInvalid({"reason": "empty phrase"})
            phrases.append(tk)
            continue
        if ":" in p:
            field, _, value = p.partition(":")
            if field.lower() not in FIELDS or not value or field.lower() in flt:
                raise QueryInvalid({"reason": "unknown or repeated field, or empty filter value", "field": field[:20]})
            field = field.lower()
            if field in ("from", "to") and not rsearch._DATE.match(value):
                raise QueryInvalid({"reason": "from/to need an ISO date YYYY-MM-DD", "field": field})
            flt[field] = value
            continue
        for t in text.tokens(p):
            (cjk if text.is_cjk(t) else terms).append(t)
    if not terms and not phrases and not cjk and not flt:
        raise QueryInvalid({"reason": "no searchable term"})
    return {"terms": terms, "phrases": phrases, "cjk": cjk, "filters": flt}


def match_expression(q):
    """The FTS5 MATCH string: every term / phrase double-quoted (tokens hold letters and digits only), implicit AND. None when no word term."""
    parts = ['"%s"' % t for t in q["terms"]] + ['"%s"' % " ".join(ph) for ph in q["phrases"]]
    return " ".join(parts) if parts else None


def _readable_levels(roles):
    return [lv for lv in access.LEVELS if access.can_read(roles, lv)]


class R2SearchService(rsearch.SearchService):
    """cfg: the hub config (search.* keys); probe_fn: test hook for an FTS-less runtime."""

    def __init__(self, cfg=None, probe_fn=None, clock=None, anchor=None):
        self.settings = ssettings.resolve(cfg)
        rsearch.SearchService.__init__(self, self.settings["enabled"], None)
        self.probe_fn, self.clock, self.anchor = probe_fn, clock, anchor
        self._stats = {}

    def engine_for(self, con):
        return fts.select(con, self.settings, self.probe_fn)

    def engine(self):  # INC-08 signature (no connection): the configured intent only
        return "fts5" if self.settings["fts"] == "auto" else "fallback"

    # ------------------------------------------------------------------ public
    def search(self, sess, query, limit=None, cursor=None, latest_only=False, con=None, reason=None, correlation_id="search"):
        if sess is None:
            raise AuthUnauthenticated()
        p = sess.principal
        if not any(r in p.roles for r in rsearch.ROLES):
            raise AuthForbidden({"reason": "role"})
        if not self.enabled:
            raise SearchDisabled({"hint": "search.enabled is false"})
        q = parse_query(query)
        try:
            limit = rsearch.LIMIT_DEFAULT if limit is None else int(limit)
            offset = 0 if cursor is None else int(cursor)
        except (TypeError, ValueError):
            raise QueryInvalid({"field": "limit/cursor"})
        limit, offset = max(1, min(limit, rsearch.LIMIT_MAX)), max(0, offset)
        schema.require(con)
        load = con.execute("SELECT event FROM search_corpus_load ORDER BY load_id DESC LIMIT 1").fetchone()
        if load is None or load[0] != "LOADED":
            from hub.r2.errors import IndexAbsent  # function-level since Stage 27: breaks the r2 <-> search package cycle (OD-27 debt)
            raise IndexAbsent({"hint": "python -m hub.search build-index"})
        engine, why, _ = self.engine_for(con)
        levels = _readable_levels(p.roles)
        rows = self._fts(con, q, levels) if engine == "fts5" else self._fallback(con, q, levels)
        if latest_only:
            best = {}
            for h in rows:
                k = h["doc_id"]
                if k not in best or str(h["version"]) > str(best[k]["version"]):
                    best[k] = h
            rows = list(best.values())
        text.order_key_sort(rows)
        c3 = [h for h in rows if h["access_level"] == "restricted"]
        why_c3 = reason.strip() if isinstance(reason, str) else ""
        if c3 and self.settings["require_c3_reason"]:
            if not why_c3:
                from hub.r2.errors import ReasonRequired  # function-level (cycle debt, Stage 27)
                raise ReasonRequired({"op": "OP-REV-03", "c3_rows": len(c3)})
            audit.append(con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="C3_READ", outcome="success",
                         correlation_id=correlation_id, object_ref="OP-REV-03", reason=why_c3[:500],
                         details={"op": "OP-REV-03", "c3_rows": len(c3), "engine": engine})
        page = rows[offset:offset + limit]
        items = [self._hit(con, h, q) for h in page]
        return {"engine": engine, "engine_reason": why, "items": items, "total": len(rows),
                "next": str(offset + limit) if offset + limit < len(rows) else None, "label": "synthetic, unvalidated"}

    # ------------------------------------------------------------------ engines
    @staticmethod
    def _filters_sql(q, levels):
        where, args = ["d.access_level IN (%s)" % ",".join("?" * len(levels))], list(levels)
        f = q["filters"]
        for k, col in sorted(_FIELD_COL.items()):
            if k in f:
                where.append("d.%s = ?" % col)
                args.append(f[k])
        if "from" in f:
            where.append("substr(COALESCE(d.effective_at, ''), 1, 10) >= ? AND d.effective_at IS NOT NULL")
            args.append(f["from"])
        if "to" in f:
            where.append("substr(COALESCE(d.effective_at, ''), 1, 10) <= ? AND d.effective_at IS NOT NULL")
            args.append(f["to"])
        return where, args

    def _fts(self, con, q, levels):
        if not levels:
            return []
        where, args = self._filters_sql(q, levels)
        for c in q["cjk"]:
            if len(c) >= 3:
                where.append("d.rowid IN (SELECT rowid FROM search_tri WHERE search_tri MATCH ?)")
                args.append('"%s"' % c.replace('"', '""'))
            else:
                where.append("instr(d.folded, ?) > 0")
                args.append(c)
        cols = "d.doc_id, d.version, d.effective_at, d.source, d.locale, d.access_level, d.reference, d.hash, d.body, d.ocr_confidence"
        mx = match_expression(q)
        try:
            if mx is not None:
                sql = ("SELECT " + cols + ", bm25(search_fts) FROM search_fts JOIN search_doc d ON d.rowid = search_fts.rowid"
                       " WHERE search_fts MATCH ? AND " + " AND ".join(where))
                res = con.execute(sql, [mx] + args).fetchall()
            else:
                res = [r + (0.0,) for r in con.execute("SELECT " + cols + " FROM search_doc d WHERE " + " AND ".join(where), args).fetchall()]
        except sqlite3.OperationalError:
            raise QueryInvalid({"reason": "query not searchable"})  # never leak FTS syntax text (AC-REV-11)
        keys = ("doc_id", "version", "effective_at", "source", "locale", "access_level", "reference", "hash", "body", "ocr_confidence", "_score")
        return [dict(zip(keys, r)) for r in res]

    def _corpus(self, con):
        """Whole-corpus token statistics (all rows, every access level, like FTS5), cached per load."""
        lid = con.execute("SELECT max(load_id) FROM search_corpus_load").fetchone()[0]
        if self._stats.get("load_id") != lid:
            rows = con.execute("SELECT doc_id, version, effective_at, source, locale, access_level, reference, hash, body, ocr_confidence, folded"
                               " FROM search_doc ORDER BY rowid").fetchall()
            keys = ("doc_id", "version", "effective_at", "source", "locale", "access_level", "reference", "hash", "body", "ocr_confidence", "folded")
            docs = []
            total = 0
            for r in rows:
                d = dict(zip(keys, r))
                d["_tk"] = text._TOKEN.findall(d["folded"])
                total += len(d["_tk"])
                docs.append(d)
            self._stats = {"load_id": lid, "docs": docs, "n": len(docs), "avgdl": (float(total) / len(docs)) if docs else 1.0}
        return self._stats

    def _fallback(self, con, q, levels):
        st = self._corpus(con)
        phrases = [[t] for t in q["terms"]] + q["phrases"]
        if phrases:
            hits = [sum(1 for d in st["docs"] if text.phrase_count(d["_tk"], ph)) for ph in phrases]
            idfs = [text.idf(st["n"], h) for h in hits]
        f = q["filters"]
        out = []
        for d in st["docs"]:
            if d["access_level"] not in levels:
                continue  # access first
            if any(k in f and str(d.get(col)) != f[k] for k, col in _FIELD_COL.items()):
                continue
            eff = (d.get("effective_at") or "")[:10]
            if "from" in f and not (eff and eff >= f["from"]):
                continue
            if "to" in f and not (eff and eff <= f["to"]):
                continue
            if any(c not in d["folded"] for c in q["cjk"]):
                continue
            score = 0.0
            if phrases:
                freqs = [text.phrase_count(d["_tk"], ph) for ph in phrases]
                if not all(freqs):
                    continue
                score = text.bm25(idfs, freqs, float(len(d["_tk"])), st["avgdl"])
            h = dict((k, d[k]) for k in ("doc_id", "version", "effective_at", "source", "locale", "access_level", "reference", "hash", "body",
                                         "ocr_confidence"))
            h["_score"] = score
            out.append(h)
        return out

    # ------------------------------------------------------------------ hit shape (INC-08 shape + linked case from the crosswalk)
    @staticmethod
    def _linked_case(con, doc_id):
        r = con.execute("SELECT l.to_id FROM crosswalk_link l WHERE l.from_type = 'document' AND l.from_id = ? AND l.to_type = 'case' AND NOT EXISTS"
                        " (SELECT 1 FROM crosswalk_link_event e WHERE e.link_id = l.link_id AND e.event_type = 'LINK_RETRACTED') ORDER BY l.link_id LIMIT 1",
                        (doc_id,)).fetchone()
        return r[0] if r else "no linked case"

    def _hit(self, con, h, q):
        ocr = h.get("ocr_confidence")
        first = (q["terms"] + [w for ph in q["phrases"] for w in ph[:1]] + q["cjk"] or [None])[0]
        return {"doc_id": h["doc_id"], "version": h["version"], "effective_at": h["effective_at"], "source": h["source"], "locale": h["locale"],
                "access_label": h["access_level"], "hash_prefix": (h.get("hash") or "")[:12],
                "snippet": html.escape(rsearch.SearchService._snippet(h.get("body") or "", first), quote=True), "trust": "untrusted",
                "label": rsearch.UNTRUSTED_LABEL, "ocr_confidence": "unknown" if ocr is None else ocr, "ocr_low": ocr is not None and ocr < rsearch.OCR_LOW,
                "linked_case": self._linked_case(con, h["doc_id"]), "score": round(-h["_score"], 6) + 0.0, "reference": h.get("reference")}

