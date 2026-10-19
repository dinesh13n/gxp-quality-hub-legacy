"""L3 declared-contract check (BEH-INT-06): the bundled copy of integration/source-contract-v1.json (byte-identical, test TST_HUB_INC06_S) is
evaluated with the minimal JSON-Schema subset the file uses: type object, `required`, per-property `type` string. Pure."""
import json
import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contracts")
_TYPES = {"string": str, "object": dict, "number": (int, float), "integer": int, "boolean": bool, "array": list}


def available():
    return sorted(f[:-5] for f in os.listdir(DIR) if f.endswith(".json"))


def load(name):
    if name not in available():
        raise KeyError(name)
    with open(os.path.join(DIR, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def check(contract, payload):
    """(result, missing): result 'pass' | 'fail'; `missing` = sorted keys that are absent or of the wrong type."""
    required = list(contract.get("required", []))
    props = contract.get("properties", {})
    if not isinstance(payload, dict):
        return "fail", sorted(required)
    bad = set(k for k in required if k not in payload)
    for k, spec in props.items():
        t = _TYPES.get(spec.get("type"))
        if k in payload and t is not None and (not isinstance(payload[k], t) or (t is not bool and isinstance(payload[k], bool))):
            bad.add(k)
    return ("pass", []) if not bad else ("fail", sorted(bad))
