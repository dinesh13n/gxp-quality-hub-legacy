"""Fixed-grammar keyword/field search, FALLBACK engine only (OP-REV-03, BEH-REV-03..06, R2; INC-08). Disabled by default (`search.enabled` false):
E-REV-SEARCH-DISABLED, the R1 behaviour.

Scope in INC-08 (partial coverage of R2, recorded as DEV-81/RTD-68): the deterministic fallback engine and its contract. The FTS5 / trigram engine and
the corpus loader (documents + archive items) are INC-09; documents come from an injected provider (synthetic, unvalidated fixtures in tests).
  grammar     whitespace-separated terms (implicit AND), "double quoted phrases", field filters ref: doc: locale: version: from: to:
              (from/to = ISO effective dates); at most 200 characters and 12 terms; an unknown field or malformed filter -> E-REV-QUERY-INVALID.
              Operators OR NOT NEAR * : have no effect (they are ordinary tokens); the query text is never passed to SQL or to a MATCH.
  matching    case- and diacritic-insensitive whole-token match (phrase = consecutive tokens). No stemming, no synonyms, no query rewriting.
  access      the access_level filter is applied BEFORE ranking and counting; denied rows are never counted (hub.decision.access).
  order       score (number of matched token occurrences) descending, then effective_at descending, then doc_id: deterministic, no randomness.
  response    {engine, items[], total, next}. A hit carries stored metadata and an escaped snippet only: no answer / summary / recommendation field.
"""
import html
import re
import unicodedata

from hub.decision import access
from hub.review.errors import QueryInvalid, QueryTooLong, SearchDisabled
from hub.security.errors import AuthForbidden, AuthUnauthenticated

ROLES = ("reviewer", "quality_lead", "compliance", "dispositioner")
FIELDS = ("ref", "doc", "locale", "version", "from", "to")
MAX_CHARS, MAX_TERMS = 200, 12
LIMIT_DEFAULT, LIMIT_MAX = 25, 100
ENGINE = "fallback"
UNTRUSTED_LABEL = "untrusted source text"
OCR_LOW = 0.70
_TOKEN = re.compile(r"\w+", re.UNICODE)
_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_CASE = re.compile(r"^C[0-9]{8}$")


def fold(text):
    """NFKD, drop combining marks, casefold: 'Ünïcode' and 'unicode' meet (AC-REV-13 es/de without diacritics)."""
    d = unicodedata.normalize("NFKD", text)
    return "".join(c for c in d if not unicodedata.combining(c)).casefold()


def tokens(text):
    return _TOKEN.findall(fold(text))


def parse_query(query):
    """-> {terms: [token], phrases: [[token]], filters: {field: value}}; raises E-REV-QUERY-INVALID / E-REV-QUERY-TOO-LONG."""
    if not isinstance(query, str) or not query.strip():
        raise QueryInvalid({"reason": "empty query"})
    if len(query) > MAX_CHARS:
        raise QueryTooLong({"length": len(query), "limit": MAX_CHARS})
    if query.count('"') % 2:
        raise QueryInvalid({"reason": "unbalanced double quote"})
    parts = re.findall(r'"[^"]*"|\S+', query)
    if len(parts) > MAX_TERMS:
        raise QueryTooLong({"terms": len(parts), "limit": MAX_TERMS})
    terms, phrases, flt = [], [], {}
    for p in parts:
        if p.startswith('"'):
            tk = tokens(p[1:-1])
            if not tk:
                raise QueryInvalid({"reason": "empty phrase"})
            phrases.append(tk)
            continue
        if ":" in p:
            field, _, value = p.partition(":")
            if field.lower() not in FIELDS or not value or field.lower() in flt:
                raise QueryInvalid({"reason": "unknown or repeated field, or empty filter value", "field": field[:20]})
            field = field.lower()
            if field in ("from", "to") and not _DATE.match(value):
                raise QueryInvalid({"reason": "from/to need an ISO date YYYY-MM-DD", "field": field})
            flt[field] = value
            continue
        terms += tokens(p)
    if not terms and not phrases and not flt:
        raise QueryInvalid({"reason": "no searchable term"})
    return {"terms": terms, "phrases": phrases, "filters": flt}


def _count_phrase(tk, phrase):
    n, k = 0, len(phrase)
    for i in range(len(tk) - k + 1):
        if tk[i:i + k] == phrase:
            n += 1
    return n


class SearchService(object):
    """documents: a callable returning an iterable of dicts {doc_id, version, effective_at, source, locale, access_level, reference, hash, body,
    ocr_confidence}. None -> an empty corpus."""

    def __init__(self, enabled=False, documents=None):
        self.enabled, self.documents = bool(enabled), documents

    def engine(self):
        return ENGINE

    def search(self, sess, query, limit=None, cursor=None, latest_only=False):
        if sess is None:
            raise AuthUnauthenticated()
        p = sess.principal
        if not any(r in p.roles for r in ROLES):
            raise AuthForbidden({"reason": "role"})
        if not self.enabled:
            raise SearchDisabled({"hint": "search.enabled is false (R1)"})
        q = parse_query(query)
        try:
            limit = LIMIT_DEFAULT if limit is None else int(limit)
            offset = 0 if cursor is None else int(cursor)
        except (TypeError, ValueError):
            raise QueryInvalid({"field": "limit/cursor"})
        limit, offset = max(1, min(limit, LIMIT_MAX)), max(0, offset)
        hits = []
        for d in (self.documents() if self.documents else ()):
            if not access.can_read(p.roles, d.get("access_level", "restricted")):
                continue  # access first: never ranked, never counted
            h = self._match(d, q)
            if h is not None:
                hits.append(h)
        if latest_only:
            best = {}
            for h in hits:
                k = h["doc_id"]
                if k not in best or h["version"] > best[k]["version"]:
                    best[k] = h
            hits = list(best.values())
        hits.sort(key=lambda h: h["doc_id"])
        hits.sort(key=lambda h: h["effective_at"] or "", reverse=True)
        hits.sort(key=lambda h: h["score"], reverse=True)
        page = hits[offset:offset + limit]
        return {"engine": ENGINE, "items": page, "total": len(hits), "next": str(offset + limit) if offset + limit < len(hits) else None,
                "label": "synthetic, unvalidated"}

    @staticmethod
    def _match(d, q):
        f = q["filters"]
        if "ref" in f and d.get("reference") != f["ref"]:
            return None
        if "doc" in f and d.get("doc_id") != f["doc"]:
            return None
        if "locale" in f and d.get("locale") != f["locale"]:
            return None
        if "version" in f and str(d.get("version")) != f["version"]:
            return None
        eff = (d.get("effective_at") or "")[:10]
        if "from" in f and not (eff and eff >= f["from"]):
            return None
        if "to" in f and not (eff and eff <= f["to"]):
            return None
        body = d.get("body") or ""
        tk = tokens(body)
        score = 0
        for t in q["terms"]:
            c = tk.count(t)
            if c == 0:
                return None
            score += c
        for ph in q["phrases"]:
            c = _count_phrase(tk, ph)
            if c == 0:
                return None
            score += c
        ocr = d.get("ocr_confidence")
        ref = d.get("reference")
        first = (q["terms"] + [w for ph in q["phrases"] for w in ph[:1]] or [None])[0]
        return {"doc_id": d["doc_id"], "version": d.get("version"), "effective_at": d.get("effective_at"), "source": d.get("source"),
                "locale": d.get("locale"), "access_label": d.get("access_level"), "hash_prefix": (d.get("hash") or "")[:12],
                "snippet": html.escape(SearchService._snippet(body, first), quote=True), "trust": "untrusted", "label": UNTRUSTED_LABEL,
                "ocr_confidence": "unknown" if ocr is None else ocr, "ocr_low": ocr is not None and ocr < OCR_LOW,
                "linked_case": ref if isinstance(ref, str) and _CASE.match(ref) else "no linked case", "score": score}

    @staticmethod
    def _snippet(body, term, width=80):
        if not body:
            return ""
        if term:
            i = fold(body).find(term)
            if i >= 0:
                a = max(0, i - width // 2)
                return body[a:a + width]
        return body[:width]
