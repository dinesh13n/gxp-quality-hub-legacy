"""Rule-set documents: validation, canonical content hash, ref parsing (rule-set.schema.json, BEH-POL-07).

A document is {ruleset_id, version, name, origin, read_only, functions[], rows[]}. `origin = as-found` forces
`read_only = true`. Pure helpers (no I/O).
"""
import re

from hub.policy import engine
from hub.policy.errors import NotFound, PolicyInvalid
from hub.security.canonical import canonical, sha256_hex

_REF = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]{0,63})@([1-9][0-9]{0,8})$")
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def parse_ref(ref):
    m = _REF.match(ref) if isinstance(ref, str) else None
    if not m:
        raise NotFound({"ruleset_ref": ref if isinstance(ref, str) else None, "reason": "expected <ruleset_id>@<version>"})
    return m.group(1), int(m.group(2))


def make_ref(ruleset_id, version):
    return "%s@%d" % (ruleset_id, version)


def validate(doc):
    """Raise E-POL-INVALID when the document does not satisfy the rule-set schema subset the engine understands."""
    bad = []
    if not _ID.match(str(doc.get("ruleset_id", ""))):
        bad.append("ruleset_id")
    if not isinstance(doc.get("version"), int) or isinstance(doc.get("version"), bool) or doc["version"] < 1:
        bad.append("version")
    if doc.get("origin") not in ("as-found", "custom"):
        bad.append("origin")
    if doc.get("origin") == "as-found" and doc.get("read_only") is not True:
        bad.append("read_only (as-found must be true)")
    if not doc.get("name"):
        bad.append("name")
    fns = doc.get("functions")
    if not isinstance(fns, list) or not fns or any(f not in engine.FUNCTIONS for f in fns):
        bad.append("functions")
    rows = doc.get("rows")
    if not isinstance(rows, list) or not rows:
        bad.append("rows")
        rows = []
    seen = set()
    for r in rows:
        rid = r.get("row_id")
        if not rid or rid in seen or not isinstance(r.get("ordinal"), int) or isinstance(r.get("ordinal"), bool):
            bad.append("row %s" % (rid,))
            continue
        seen.add(rid)
        o = r.get("outcome")
        if not isinstance(o, dict) or o.get("kind") not in engine.KINDS or o.get("function") not in (fns or []):
            bad.append("row %s outcome" % rid)
        for c in r.get("conditions", None) or []:
            if set(c) != {"field", "op", "value"} or c["op"] not in engine.OPS:
                bad.append("row %s condition" % rid)
        if not isinstance(r.get("conditions"), list):
            bad.append("row %s conditions" % rid)
        if isinstance(o, dict) and o.get("kind") == "rule" and "value" not in o:
            bad.append("row %s value" % rid)
    if bad:
        raise PolicyInvalid({"ruleset": doc.get("ruleset_id"), "problems": sorted(set(map(str, bad)))})
    return doc


def content_hash(doc):
    """sha256 over the canonical content (identity, origin, functions and rows), independent of storage order."""
    rows = sorted(({"row_id": r["row_id"], "ordinal": r["ordinal"], "conditions": r["conditions"], "outcome": r["outcome"],
                    "effective_from": r.get("effective_from"), "effective_to": r.get("effective_to"),
                    "owner": r.get("owner"), "is_default": 1 if r.get("is_default") else 0} for r in doc["rows"]),
                  key=lambda r: (r["ordinal"], r["row_id"]))
    return sha256_hex(canonical({"ruleset_id": doc["ruleset_id"], "version": doc["version"], "name": doc["name"],
                                 "origin": doc["origin"], "read_only": bool(doc["read_only"]),
                                 "functions": sorted(doc["functions"]), "rows": rows}))
