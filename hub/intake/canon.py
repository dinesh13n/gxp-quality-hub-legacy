"""Canonical forms for intake (SBR-INT-01/02, SC-5). Pure, stdlib only.

identity_key  = sha256(canonical([source, partner, record_kind, ref_id, source_ts])) - the natural key decided in OD-18. `business_key` and
                `feed_id` are NOT identities (FND-INT-2). Strings are Unicode-NFC + trimmed; source_ts is normalised to the canonical UTC form.
                An item whose identity is incomplete (a component missing or source_ts unparseable) cannot be re-delivery-matched by a partial
                key (two different broken items would otherwise look like revisions of each other): its identity falls back to
                sha256(canonical(["unkeyed", source, source_key, content_hash])) (design note D-05).
content_hash  = sha256(canonical({schema_rev, payload})): payload = the parsed JSON value (sorted keys, no insignificant whitespace), or
                {"unparsed_text": text} when it is not JSON. Transport fields are never part of it.
"""
import datetime
import json
import re

from hub.crosswalk.registry import normalise
from hub.security.canonical import canonical, sha256_hex

_TS = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d{1,6})?(Z|\+00:00)$")


def norm_source_ts(value):
    """Canonical UTC form YYYY-MM-DDTHH:MM:SS[.ffffff]Z, or None when the value is not an ISO-8601 UTC timestamp."""
    if not isinstance(value, str):
        return None
    m = _TS.match(value.strip())
    if not m:
        return None
    try:
        datetime.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    return m.group(1) + (m.group(2) or "") + "Z"


def parse_payload(text):
    """(value, ok). ok is False when `text` is not a str or not valid JSON (NaN/Infinity constants are refused)."""
    if not isinstance(text, str):
        return None, False

    def refuse(name):
        raise ValueError(name)
    try:
        return json.loads(text, parse_constant=refuse), True
    except ValueError:
        return None, False


def content_hash(schema_rev, payload_text):
    value, ok = parse_payload(payload_text)
    payload = value if ok else {"unparsed_text": payload_text if isinstance(payload_text, str) else None}
    return sha256_hex(canonical({"schema_rev": schema_rev if isinstance(schema_rev, str) else None, "payload": payload}))


def identity_key(source, partner, record_kind, ref_id, source_ts, source_key, chash):
    """(identity_key, complete)."""
    parts = [normalise(partner), normalise(record_kind), normalise(ref_id), norm_source_ts(source_ts)]
    if all(isinstance(p, str) and p for p in parts):
        return sha256_hex(canonical([source] + parts)), True
    return sha256_hex(canonical(["unkeyed", source, source_key if isinstance(source_key, str) else None, chash])), False


def raw_bytes(raw):
    """Verbatim delivered row as canonical UTF-8 JSON bytes (the raw record, BEH-INT-01)."""
    return canonical(raw).encode("utf-8")
