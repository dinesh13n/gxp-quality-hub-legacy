"""Item validation, layers L1 envelope (DC-01), L2 payload (DC-02/05) and the L3 contract result (BEH-INT-05/06). Pure, deterministic.

`validate(profile, delivery)` -> (reasons set, detail dict, facts dict). It never raises on item content and never mutates its input: every
problem is a reason code (SCH-REASON), never an exception (error-handling-spec rule 4). Decimal arithmetic only for amounts (FR-MET-04).
Layer L3 and the identity checks (REVISED_CONFLICT) are applied by the service because they need the binding / the store.
"""
import decimal
import json
import re
import unicodedata

from hub.core.unitext import has_lone_surrogate
from hub.intake import canon
from hub.intake.profiles import get_path

Decimal = decimal.Decimal


def _blank(v):
    return not isinstance(v, str) or not unicodedata.normalize("NFC", v).strip()


def parse_object(text):
    """(dict|None, error) with numbers parsed as Decimal (exact) and NaN / Infinity refused."""
    if not isinstance(text, str):
        return None, "not_text"

    def refuse(name):
        raise ValueError(name)
    try:
        value = json.loads(text, parse_float=Decimal, parse_constant=refuse)
    except ValueError:
        return None, "invalid_json"
    if not isinstance(value, dict):
        return None, "not_object"
    if has_lone_surrogate(value):  # Stage 27 S26-F-03: not storable text; a reason code (INVALID_JSON -> quarantine), never an exception
        return None, "invalid_json"
    return value, None


def to_decimal(value):
    """Decimal for a JSON number or numeric text; None when it is not a finite decimal (bool, null, blank, NaN are not)."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, Decimal)):
        d = Decimal(value)
    elif isinstance(value, str):
        t = value.strip()
        if not t:
            return None
        try:
            d = Decimal(t)
        except decimal.InvalidOperation:
            return None
    else:
        return None
    return d if d.is_finite() else None


def _text(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, Decimal):
        return str(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def validate(profile, d):
    reasons, detail = set(), {}
    # ---- L1 envelope
    missing = []
    for key in profile["envelope_required"]:
        v = d.get(key)
        if key == "source_ts":
            if canon.norm_source_ts(v) is None:
                missing.append(key)
        elif _blank(v):
            missing.append(key)
    names = profile["envelope_names"]
    if profile["partners"] is not None and not _blank(d.get("partner")) and d["partner"].strip() not in profile["partners"]:
        missing.append("partner")  # outside the closed source-system set: no dedicated reason code exists (design note D-07)
    if missing:
        reasons.add("MISSING_ENVELOPE_FIELD")
        detail["MISSING_ENVELOPE_FIELD"] = sorted(set(names.get(k, k) for k in missing))
    rev = d.get("schema_rev")
    if profile["schema_revs"] is not None and not _blank(rev) and rev.strip() not in profile["schema_revs"]:
        reasons.add("UNSUPPORTED_REVISION")
        detail["UNSUPPORTED_REVISION"] = {"schema_rev": rev.strip()[:40]}
    kind = d.get("record_kind")
    if profile["record_kinds"] is not None and not _blank(kind) and kind.strip() not in profile["record_kinds"]:
        reasons.add("UNKNOWN_RECORD_KIND")
        detail["UNKNOWN_RECORD_KIND"] = {"record_kind": kind.strip()[:40]}
    # ---- L2 payload
    payload, err = parse_object(d.get("payload_text"))
    facts = {"payload": payload, "amount_text": None}
    if err in ("invalid_json", "not_object"):
        reasons.add("INVALID_JSON")
        detail["INVALID_JSON"] = {"error": err}
        return reasons, detail, facts
    if err == "not_text":
        return reasons, detail, facts  # payload absent: already MISSING_ENVELOPE_FIELD
    absent = sorted(k for k in profile["payload_required"] if k not in payload or payload[k] is None)
    if absent:
        reasons.add("MISSING_PAYLOAD_FIELD")
        detail["MISSING_PAYLOAD_FIELD"] = absent
    bk = profile["business_key"]
    if bk is not None and _blank(payload.get(bk)):
        reasons.add("NO_BUSINESS_KEY")
    q = profile["quantity"]
    if q is not None and q in payload:
        facts["amount_text"] = _text(payload[q])
        dec = to_decimal(payload[q])
        if dec is None:
            reasons.add("UNPARSABLE_AMOUNT")
        elif dec < 0:
            reasons.add("NEGATIVE_VALUE")
    if profile["unit"] is not None and profile["units"] is not None and payload.get(profile["unit"]) is not None \
            and payload[profile["unit"]] not in profile["units"]:
        reasons.add("UNKNOWN_UNIT")
    if profile["currency"] is not None and profile["currencies"] is not None and profile["currency"] in payload \
            and payload[profile["currency"]] not in profile["currencies"]:
        reasons.add("UNKNOWN_CURRENCY")
    if profile["identifier"] is not None and profile["identifier"] in payload:
        v = payload[profile["identifier"]]
        if not isinstance(v, str) or not re.match(profile["identifier_pattern"], v):
            reasons.add("IDENTIFIER_PATTERN")
    return reasons, detail, facts


def attrs(profile, payload):
    """source_* attributes and the (Untrusted) notes text as plain str|None; the caller wraps them (BEH-INT-09)."""
    out = {}
    if isinstance(payload, dict):
        for name, path in profile["attrs"].items():
            out[name] = _text(get_path(payload, path))
        out["notes"] = _text(get_path(payload, profile["notes"])) if profile["notes"] else None
    return out
