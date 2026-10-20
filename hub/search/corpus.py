"""Corpus loader: a DERIVED, rebuildable index of the document corpus (BEH-REV-03, retrieval-strategy R1; INC-09).

Reads only from a SANDBOX COPY of the legacy tree (hub.guards.sandbox refuses the working tree and the backup): `data/documents/source_documents.jsonl`
(1,200 documents, sha256 pinned below; a mismatch fails closed with E-FX-HASH) and `data/archive_documents/*.eml|*.html` (420 archive items; each
file's sha256 is recorded). Nothing is written to the source tree. The index lives in the hub store (M007 `search_doc` + the FTS5 tables when the
runtime offers them); dropping it (`drop`) is the rollback and loses nothing that cannot be rebuilt.

Archive items carry no access_level, so they are stored as `restricted` with access_level_given = 0 (MA-1: missing access level = restricted).
Every load and drop is one transaction with one audit record (SEARCH_CORPUS_LOADED / SEARCH_CORPUS_DROPPED) and one insert-only provenance row.
Document text is Untrusted: stored as given, never interpreted (planted instruction lines stay ordinary text, PNFR-13). Synthetic, unvalidated.
"""
import email
import email.policy
import hashlib
import html.parser
import json
import os
import re

from hub.core.errors import FixtureMismatch
from hub.guards import sandbox
from hub.search import fts, schema, text

DOC_REL = os.path.join("data", "documents", "source_documents.jsonl")
ARCHIVE_REL = os.path.join("data", "archive_documents")
JSONL_SHA256 = "d97b444c069d338baacb7a86d7cdc1509efece7add6dcc74720df2a8008acb48"  # Stage 0A backup SHA256SUMS.txt (OD-03, OD-09)
LEVELS = ("engineering", "quality", "operations", "restricted")
LABEL = "synthetic, unvalidated"
COLS = ("doc_id", "version", "effective_at", "source", "locale", "access_level", "access_level_given", "reference", "hash", "body", "folded",
        "ocr_confidence", "origin", "load_id")
_SRC_DATE = re.compile(r"Source date ([0-9]{4}-[0-9]{2}-[0-9]{2})")


class _Text(html.parser.HTMLParser):
    def __init__(self):
        html.parser.HTMLParser.__init__(self, convert_charrefs=True)
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("title", "script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("title", "script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip and data.strip():
            self.parts.append(data.strip())


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _norm_doc(d, origin):
    level = d.get("access_level")
    given = level in LEVELS
    body = d.get("body") if isinstance(d.get("body"), str) else ""
    ocr = d.get("ocr_confidence")
    return {"doc_id": str(d["doc_id"]), "version": str(d.get("version") or "v1"), "effective_at": d.get("effective_at"), "source": d.get("source"),
            "locale": d.get("locale"), "access_level": level if given else "restricted", "access_level_given": 1 if given else 0,
            "reference": d.get("reference"), "hash": d.get("hash") or _sha(body.encode("utf-8")), "body": body,
            "ocr_confidence": ocr if isinstance(ocr, (int, float)) and not isinstance(ocr, bool) else None, "origin": origin}


def parse_archive_item(name, raw):
    """One archive file -> a document dict (body = visible text; untrusted)."""
    stem, ext = os.path.splitext(name)
    if ext == ".eml":
        msg = email.message_from_bytes(raw, policy=email.policy.default)
        part = msg.get_body(preferencelist=("plain",))
        body = (str(msg.get("Subject") or "") + "\n" + (part.get_content() if part is not None else "")).strip()
        source = "archive-eml"
    else:
        p = _Text()
        p.feed(raw.decode("utf-8", "replace"))
        body = "\n".join(p.parts)
        source = "archive-html"
    body = re.sub(r"[ \t\r\f\v]+", " ", body)
    m = _SRC_DATE.search(body)
    return {"doc_id": "ARC-" + stem, "version": "v1", "effective_at": m.group(1) if m else None, "source": source, "locale": None,
            "reference": None, "hash": _sha(raw), "body": body, "ocr_confidence": None}


def read_shipped(legacy_root, pinned=True):
    """-> (documents, archive_items, inputs) from a sandbox copy. Missing files are reported in `inputs`, never an error."""
    legacy_root = sandbox.assert_safe_path(legacy_root, "legacy source root")
    inputs = {"jsonl": None, "archive": None}
    docs, arch = [], []
    path = os.path.join(legacy_root, DOC_REL)
    if os.path.isfile(path):
        with open(path, "rb") as f:
            raw = f.read()
        digest = _sha(raw)
        if pinned and digest != JSONL_SHA256:
            raise FixtureMismatch({"file": DOC_REL, "expected": JSONL_SHA256[:16], "actual": digest[:16]})
        for line in raw.decode("utf-8").splitlines():
            if line.strip():
                docs.append(json.loads(line))
        inputs["jsonl"] = {"path": DOC_REL, "sha256": digest, "pinned": bool(pinned), "rows": len(docs)}
    adir = os.path.join(legacy_root, ARCHIVE_REL)
    if os.path.isdir(adir):
        agg = hashlib.sha256()
        for name in sorted(os.listdir(adir)):
            if not name.endswith((".eml", ".html")):
                continue
            with open(os.path.join(adir, name), "rb") as f:
                raw = f.read()
            agg.update(name.encode("utf-8") + b"\0" + _sha(raw).encode("ascii") + b"\n")
            arch.append(parse_archive_item(name, raw))
        inputs["archive"] = {"path": ARCHIVE_REL, "files": len(arch), "sha256_of_file_digests": agg.hexdigest()}
    return docs, arch, inputs


def _next_id(con):
    return "LOAD-%06d" % (con.execute("SELECT count(*) FROM search_corpus_load").fetchone()[0] + 1)


def build(con, clock, anchor, actor, documents, archive_items=(), inputs=None, origin="shipped", max_doc_chars=20000, probe_fn=None,
          correlation_id="search-build"):
    """Replace the derived corpus with `documents` + `archive_items` (one transaction, audited). FTS tables are (re)built when FTS5 + trigram are
    available, otherwise dropped (the fallback engine reads search_doc). Returns the provenance row."""
    from hub.security import audit
    schema.require(con)
    pr = (probe_fn or fts.probe)(con)
    rows, cut, seen, total = [], 0, set(), 0
    for kind, src in (("document", documents), ("archive", archive_items)):
        for d in src:
            total += 1
            r = _norm_doc(d, origin if kind == "document" else origin + "-archive")
            if len(r["body"]) > max_doc_chars:
                r["body"], cut = r["body"][:max_doc_chars], cut + 1
            key = (r["doc_id"], r["version"])
            if key in seen:
                continue  # first row wins; duplicates are counted in the load record
            seen.add(key)
            r["folded"] = text.fold(r["body"])
            rows.append(r)
    n_doc = sum(1 for r in rows if not r["origin"].endswith("-archive"))
    rec = {}
    with audit.change(con, clock, anchor=anchor, actor=actor, actor_kind="human" if actor != "hub" else "system", action="SEARCH_CORPUS_LOADED",
                      outcome="success", correlation_id=correlation_id, object_ref="search:corpus", details={}) as ctx:
        load_id = _next_id(con)
        con.execute("DELETE FROM search_doc")
        fts.drop_index(con)
        for r in rows:
            r["load_id"] = load_id
            con.execute("INSERT INTO search_doc(" + ", ".join(COLS) + ") VALUES (" + ",".join("?" * len(COLS)) + ")", tuple(r[c] for c in COLS))
        built = bool(pr["fts5"] and pr["trigram"])
        if built:
            fts.create_index(con)
        ftsinfo = {"built": built, "fts5": pr["fts5"], "trigram": pr["trigram"], "sqlite": pr["sqlite"]}
        rec = {"load_id": load_id, "event": "LOADED", "occurred_at": clock(), "actor": actor, "origin": origin, "documents": n_doc,
               "archive_items": len(rows) - n_doc, "inputs": json.dumps(dict(inputs or {}, cut=cut, duplicates=total - len(rows)), sort_keys=True),
               "fts": json.dumps(ftsinfo, sort_keys=True), "label": LABEL}
        con.execute("INSERT INTO search_corpus_load(load_id, event, occurred_at, actor, origin, documents, archive_items, inputs, fts, label)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)", tuple(rec[k] for k in ("load_id", "event", "occurred_at", "actor", "origin", "documents",
                                                                          "archive_items", "inputs", "fts", "label")))
        ctx.fields["details"] = {"load_id": load_id, "documents": n_doc, "archive_items": len(rows) - n_doc, "fts_built": built, "origin": origin}
    return rec


def drop(con, clock, anchor, actor, correlation_id="search-drop"):
    """Rollback of the derived index: drop the FTS tables and empty search_doc (audited; the provenance log keeps a DROPPED row)."""
    from hub.security import audit
    schema.require(con)
    with audit.change(con, clock, anchor=anchor, actor=actor, actor_kind="human" if actor != "hub" else "system", action="SEARCH_CORPUS_DROPPED",
                      outcome="success", correlation_id=correlation_id, object_ref="search:corpus", details={}) as ctx:
        n = con.execute("SELECT count(*) FROM search_doc").fetchone()[0]
        fts.drop_index(con)
        con.execute("DELETE FROM search_doc")
        load_id = _next_id(con)
        con.execute("INSERT INTO search_corpus_load(load_id, event, occurred_at, actor, origin, documents, archive_items, inputs, fts, label)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)", (load_id, "DROPPED", clock(), actor, "rollback", 0, 0, json.dumps({"rows_dropped": n}), "{}", LABEL))
        ctx.fields["details"] = {"load_id": load_id, "rows_dropped": n}
    return {"load_id": load_id, "rows_dropped": n}


def current(con):
    """The latest provenance row (LOADED or DROPPED) or None."""
    row = con.execute("SELECT load_id, event, occurred_at, origin, documents, archive_items, fts FROM search_corpus_load ORDER BY load_id DESC LIMIT 1").fetchone()
    if row is None:
        return None
    return dict(zip(("load_id", "event", "occurred_at", "origin", "documents", "archive_items", "fts"), row))
