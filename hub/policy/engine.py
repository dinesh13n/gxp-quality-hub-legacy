"""Pure, table-driven rule evaluation (BEH-POL-06/09/11, PNFR-17, AC-POL-22).

`evaluate(ruleset, function, inputs)` is a pure function of (rule-set content, inputs): no clock, randomness, file,
network or database access happens inside it, and this module imports only `decimal` and `re` (plus hub.policy.inputs /
errors, themselves pure). A rule set is a dict {ruleset_id, version, functions[], rows[]}; each row is
{row_id, ordinal, conditions[{field, op, value}], outcome{function, kind, ...}, is_default}:

  kind 'rule'      first-match-wins by ordinal; conditions are ANDed; an empty list matches everything; the outcome
                   carries `value`; a row with is_default=1 marks `defaulted` when it is the matching row
                   (outcome.defaulted_reason, default NO_MATCH_REGION_YEAR)
  kind 'domain'    {field, values[]}: an input outside the declared values sets defaulted=UNKNOWN_INPUT_VALUE
  kind 'param'     {name, value}: function parameter (AMOUNT_LIMIT tolerance_factor)
  kind 'register'  {fields...}: reference data (SHIFT_FLAG policy_register rows, looked up by region + policy_code)

A condition value may be {"$input": name} (compare with another input). Ops: eq in gt gte lt lte starts_with is_null
not_null (rule-set.schema.json). `defaulted` precedence: NULL_INPUT > UNKNOWN_INPUT_VALUE > matched default row.
The result is the rule-result.schema.json object; `authoritative` is False here - only the service, which knows the
active pointer, may set it True.
"""
import decimal

from hub.policy import inputs as _in
from hub.policy.errors import InputInvalid, UnknownFunction

OPS = ("eq", "in", "gt", "gte", "lt", "lte", "starts_with", "is_null", "not_null")
KINDS = ("rule", "domain", "param", "register")
REASONS = ("NO_MATCH_REGION_YEAR", "UNKNOWN_INPUT_VALUE", "NULL_INPUT")

# function catalogue: numeric inputs (required ones raise E-POL-INPUT-INVALID), fields whose absence is NULL_INPUT
FUNCTIONS = {
    "PRIORITY": {"required_numeric": ["amount"], "optional_numeric": [], "null_fields": ["status", "severity"]},
    "MANUAL_REVIEW": {"required_numeric": [], "optional_numeric": [], "null_fields": ["status", "severity"]},
    "AMOUNT_LIMIT": {"required_numeric": ["amount"], "optional_numeric": [], "null_fields": ["region", "year"]},
    "SHIFT_FLAG": {"required_numeric": ["value"], "optional_numeric": ["threshold"], "null_fields": ["status"]},
}


def _num(x):
    return isinstance(x, decimal.Decimal)


def _coerce(left, right):
    """Numeric comparison needs both sides as Decimal; return (l, r) or None when not comparable."""
    if _num(left) and isinstance(right, (int, float, str)) and not isinstance(right, bool):
        try:
            return left, _in.to_decimal(right, "rule value")
        except InputInvalid:
            return None
    if _num(left) and _num(right):
        return left, right
    return None


def _holds(op, left, right):
    if op == "is_null":
        return left is None
    if op == "not_null":
        return left is not None
    if left is None:
        return False
    if op == "eq":
        if _num(left):
            c = _coerce(left, right)
            return c is not None and c[0] == c[1]
        if _num(right):
            return False
        return left == right
    if op == "in":
        return isinstance(right, list) and any(_holds("eq", left, r) for r in right)
    if op == "starts_with":
        return isinstance(left, str) and isinstance(right, str) and left.startswith(right)
    c = _coerce(left, right)
    if c is None:
        return False
    return {"gt": c[0] > c[1], "gte": c[0] >= c[1], "lt": c[0] < c[1], "lte": c[0] <= c[1]}[op]


def _jsonable(v):
    return _in.text(v) if _num(v) else v


def _norm(function, ruleset, raw):
    """Normalised input dict: Decimals for numeric fields, year as text, SHIFT_FLAG threshold lookup."""
    spec = FUNCTIONS[function]
    data = dict(raw)
    for f in spec["required_numeric"]:
        data[f] = _in.to_decimal(data.get(f), f)
    for f in spec["optional_numeric"]:
        if data.get(f) is not None:
            data[f] = _in.to_decimal(data[f], f)
    lookup_miss = False
    if function == "AMOUNT_LIMIT":
        y = data.get("year")
        data["year"] = str(y) if isinstance(y, int) and not isinstance(y, bool) else (y if isinstance(y, str) else None)
    if function == "SHIFT_FLAG" and "threshold" not in raw and data.get("region") and data.get("policy_code"):
        data["threshold"] = None
        lookup_miss = True
        for r in ruleset["rows"]:
            o = r["outcome"]
            if o.get("function") == function and o.get("kind") == "register" and o.get("region") == data["region"] \
                    and o.get("policy_code") == data["policy_code"] and o.get("active") == 1:
                data["threshold"] = _in.to_decimal(o["threshold"], "threshold")
                lookup_miss = False
                break
    return data, lookup_miss


def evaluate(ruleset, function, inputs):
    if function not in FUNCTIONS or function not in ruleset["functions"]:
        raise UnknownFunction({"function": function, "served": list(ruleset["functions"])})
    spec = FUNCTIONS[function]
    data, lookup_miss = _norm(function, ruleset, inputs)
    fn_rows = sorted((r for r in ruleset["rows"] if r["outcome"].get("function") == function), key=lambda r: r["ordinal"])
    null_flag = any(data.get(f) is None for f in spec["null_fields"])
    unknown_flag = False
    for r in fn_rows:
        o = r["outcome"]
        if o.get("kind") == "domain":
            v = data.get(o["field"])
            if v is not None and (not isinstance(v, str) or v not in o["values"]):
                unknown_flag = True
    trace, matched_row = [], None
    for r in fn_rows:
        if r["outcome"].get("kind") != "rule":
            continue
        used = {}
        ok = True
        for c in r["conditions"]:
            used[c["field"]] = _jsonable(data.get(c["field"]))
            right = c["value"]
            if isinstance(right, dict) and "$input" in right:
                used[right["$input"]] = _jsonable(data.get(right["$input"]))
                right = data.get(right["$input"])
                if right is None:
                    ok = False
                    continue
            if not _holds(c["op"], data.get(c["field"]), right):
                ok = False
        trace.append({"row_id": r["row_id"], "ordinal": r["ordinal"], "matched": ok, "inputs_used": used})
        if ok:
            matched_row = r
            break
    reason = None
    explicit_null_threshold = function == "SHIFT_FLAG" and "threshold" in inputs and inputs["threshold"] is None
    if null_flag or explicit_null_threshold:
        reason = "NULL_INPUT"
    elif unknown_flag:
        reason = "UNKNOWN_INPUT_VALUE"
    elif matched_row is None:
        reason = "NO_MATCH_REGION_YEAR"
    elif matched_row.get("is_default"):
        reason = matched_row["outcome"].get("defaulted_reason", "NO_MATCH_REGION_YEAR")
    elif lookup_miss:
        reason = "NO_MATCH_REGION_YEAR"
    value = None if matched_row is None else matched_row["outcome"].get("value")
    outcome = value
    if function == "AMOUNT_LIMIT":
        factor = decimal.Decimal(1)
        for r in fn_rows:
            if r["outcome"].get("kind") == "param" and r["outcome"].get("name") == "tolerance_factor":
                factor = _in.to_decimal(r["outcome"]["value"], "tolerance_factor")
        allowed = None
        if value is not None:
            allowed = data["amount"] <= _in.to_decimal(value, "threshold") * factor
        outcome = {"allowed": allowed, "threshold": value}
        trace.append({"row_id": "AMOUNT_LIMIT-compare", "ordinal": 1000, "matched": bool(allowed),
                      "inputs_used": {"amount": _in.text(data["amount"]), "threshold": value,
                                      "tolerance_factor": _in.text(factor)}})
    return {"outcome": outcome, "trace": trace, "defaulted": reason is not None, "defaulted_reason": reason,
            "ruleset_ref": "%s@%s" % (ruleset["ruleset_id"], ruleset["version"]), "authoritative": False}


def render_text(result):
    """Plain-text explanation regenerated from the trace; the defaulted marker is always shown (AC-POL-19)."""
    lines = ["rule set %s%s" % (result["ruleset_ref"], "" if result["authoritative"] else " (not the active set: what-if)")]
    for t in result["trace"]:
        lines.append("  row %s (#%s): %s; inputs %s" % (t["row_id"], t["ordinal"], "MATCHED" if t["matched"] else "no match",
                                                         ", ".join("%s=%s" % (k, t["inputs_used"][k]) for k in sorted(t["inputs_used"]))))
    lines.append("outcome: %s" % (result["outcome"],))
    if result["defaulted"]:
        lines.append("DEFAULTED: %s" % result["defaulted_reason"])
    return "\n".join(lines)
