"""Wire helpers: JSON encoding, strict request-body parsing and the error envelope (error-handling-spec ER-1; INC-08)."""
import decimal
import json
import urllib.parse as _up

from hub.core.unitext import has_lone_surrogate
from hub.web.errors import ReqInvalid

RETRYABLE = frozenset(["E-DEC-SEQ-CONFLICT", "E-GATE-PACK-STALE", "E-GATE-REAUTH-REQUIRED", "E-AUTH-LOCKED", "E-RUN-ALREADY-RUNNING",
                       "E-STORE-DB-BUSY", "E-REQ-RATE-LIMITED", "E-STORE-UNAVAILABLE"])


def _default(o):
    if isinstance(o, decimal.Decimal):
        return format(o, "f")
    if isinstance(o, (set, frozenset, tuple)):
        return sorted(o) if not isinstance(o, tuple) else list(o)
    if isinstance(o, bytes):
        return o.decode("utf-8", "replace")
    return str(o)


def dumps(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=_default)


def _no_dups(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise ReqInvalid({"pointer": "/" + str(k)[:40], "reason": "duplicate key"})
        seen[k] = v
    return seen


def parse_json(body):
    if not body:
        raise ReqInvalid({"pointer": "", "reason": "a JSON body is required"})
    try:
        doc = json.loads(body.decode("utf-8"), object_pairs_hook=_no_dups)
    except ReqInvalid:
        raise
    except (ValueError, UnicodeDecodeError, RecursionError):
        raise ReqInvalid({"pointer": "", "reason": "body is not valid UTF-8 JSON"})
    if not isinstance(doc, dict):
        raise ReqInvalid({"pointer": "", "reason": "the body must be a JSON object"})
    if has_lone_surrogate(doc):  # Stage 27 S26-F-03: json.loads accepts \\ud800, SQLite can not store it (was HTTP 500)
        raise ReqInvalid({"pointer": "", "reason": "a string holds a lone UTF-16 surrogate (not valid Unicode text)"})
    return doc


def parse_form(body):
    try:
        pairs = _up.parse_qsl(body.decode("utf-8"), keep_blank_values=True, strict_parsing=bool(body), max_num_fields=50)
    except (ValueError, UnicodeDecodeError):
        raise ReqInvalid({"pointer": "", "reason": "malformed form body"})
    out = {}
    for k, v in pairs:
        if k in out:
            raise ReqInvalid({"pointer": "/" + k[:40], "reason": "duplicate field"})
        out[k] = v
    return out


def check(body, spec):
    """spec: {name: (types, required)}; unknown field, missing required field or wrong type -> E-REQ-INVALID listing JSON pointers."""
    bad = []
    for k in sorted(body):
        if k not in spec:
            bad.append({"pointer": "/" + str(k)[:40], "reason": "unknown field"})
    for k, (types, required) in sorted(spec.items()):
        if k not in body:
            if required:
                bad.append({"pointer": "/" + k, "reason": "required"})
            continue
        v = body[k]
        if v is None and not required:
            continue
        ok = isinstance(v, types) and not (isinstance(v, bool) and bool not in (types if isinstance(types, tuple) else (types,)))
        if not ok:
            bad.append({"pointer": "/" + k, "reason": "wrong type"})
    if bad:
        raise ReqInvalid({"errors": bad})
    return body


def envelope(err, cid):
    code = getattr(err, "code", "E-HUB-INTERNAL")
    return {"error": {"code": code, "message": getattr(err, "message", "internal error"), "correlation_id": cid,
                      "details": getattr(err, "details", None), "retryable": code in RETRYABLE}}
