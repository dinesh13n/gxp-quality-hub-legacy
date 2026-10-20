"""Rule divergence report (OP-POL-07, BEH-POL-10, FR-POL-05, AC-POL-24; INC-09).

Runs every LOADED rule set that publishes the normalised boolean `amount_over_limit` (f03 F03-2; A-12-F03-1: a spec convenience, it does not assert the
rule sets are meant to agree) over a list of inputs and lists the inputs where the non-null outputs differ, with each set's trace:
  PRIORITY (as-found-python)   amount > the limit of the rule row whose condition is `amount gt <limit>`
  AMOUNT_LIMIT (as-found-js)   NOT allowed, i.e. amount > regional threshold x tolerance factor (engine evaluation, defaulted marker kept)
  SHIFT_FLAG (as-found-batch)  value(amount) > threshold, the threshold given in the input or looked up in the set's register by region +
                               policy_code; no threshold -> null (not comparable), counted per set
It resolves nothing, names no 'correct' set, activates nothing and changes no state; the count is recorded in one audit record
(RULE_DIVERGENCE_REPORTED). Pure apart from that audit record.
"""
from hub.policy import engine
from hub.policy import inputs as _in
from hub.policy.errors import InputInvalid
from hub.security import audit

ROLES = ("quality_lead", "compliance")
NOTE = "divergence is reported, not resolved: no rule set is named correct (A-12-F03-1, OD-S12-04)"


def _dec(v):
    try:
        return _in.to_decimal(v, "amount")
    except InputInvalid:
        return None


def _priority(doc, inp):
    for r in sorted(doc["rows"], key=lambda r: r["ordinal"]):
        o = r["outcome"]
        if o.get("function") != "PRIORITY" or o.get("kind") != "rule":
            continue
        for c in r["conditions"]:
            if c["field"] == "amount" and c["op"] == "gt":
                amt, lim = _dec(inp.get("amount")), _dec(c["value"])
                over = None if amt is None or lim is None else amt > lim
                return over, [{"row_id": r["row_id"], "inputs_used": {"amount": None if amt is None else _in.text(amt), "limit": c["value"]},
                               "matched": bool(over)}]
    return None, [{"row_id": None, "reason": "no amount rule row"}]


def _amount_limit(doc, inp):
    try:
        res = engine.evaluate(doc, "AMOUNT_LIMIT", {"amount": inp.get("amount"), "region": inp.get("region"), "year": inp.get("year")})
    except InputInvalid:
        return None, [{"row_id": None, "reason": "amount not numeric"}]
    allowed = res["outcome"]["allowed"]
    tr = list(res["trace"])
    if res["defaulted"]:
        tr.append({"row_id": "defaulted", "reason": res["defaulted_reason"]})
    return (None if allowed is None else not allowed), tr


def _shift(doc, inp):
    amt = _dec(inp.get("amount"))
    thr = _dec(inp["threshold"]) if inp.get("threshold") is not None else None
    src = "input"
    if thr is None and inp.get("region") and inp.get("policy_code"):
        src = "register"
        for r in doc["rows"]:
            o = r["outcome"]
            if o.get("function") == "SHIFT_FLAG" and o.get("kind") == "register" and o.get("region") == inp["region"] \
                    and o.get("policy_code") == inp["policy_code"] and o.get("active") == 1:
                thr = _dec(o["threshold"])
                break
    if amt is None or thr is None:
        return None, [{"row_id": "BATCH-2", "reason": "no threshold (needs threshold or region + policy_code)", "matched": False}]
    over = amt > thr
    return over, [{"row_id": "BATCH-2", "inputs_used": {"value": _in.text(amt), "threshold": _in.text(thr), "threshold_source": src}, "matched": over}]


NORMALISERS = (("PRIORITY", _priority), ("AMOUNT_LIMIT", _amount_limit), ("SHIFT_FLAG", _shift))


def publishing_sets(policy_service):
    """[(ruleset_ref, doc, normaliser)] for every loaded set serving one of the three functions, in ruleset_ref order."""
    out = []
    for rs in policy_service.list_rulesets():
        doc = policy_service.get_ruleset(rs["ruleset_ref"])
        for fn, norm in NORMALISERS:
            if fn in doc["functions"]:
                out.append((rs["ruleset_ref"], doc, norm))
                break
    return out


def report(policy_service, inputs):
    sets = publishing_sets(policy_service)
    divergent, nulls = [], dict((ref, 0) for ref, _, _ in sets)
    for inp in inputs:
        outputs, traces = {}, {}
        for ref, doc, norm in sets:
            over, tr = norm(doc, inp)
            outputs[ref], traces[ref] = over, tr
            if over is None:
                nulls[ref] += 1
        vals = set(v for v in outputs.values() if v is not None)
        if len(vals) > 1:
            divergent.append({"input": dict(inp), "outputs": outputs, "traces": traces})
    return {"compared_sets": [ref for ref, _, _ in sets], "output_key": "amount_over_limit", "inputs": len(inputs), "divergent": divergent,
            "count": len(divergent), "null_outputs": nulls, "note": NOTE, "label": "synthetic, unvalidated"}


def run(con, clock, anchor, sess, policy_service, inputs, correlation_id="divergence"):
    """Role-checked report + one audit record carrying the count (the only write)."""
    from hub.security.errors import AuthForbidden, AuthUnauthenticated
    if sess is None:
        raise AuthUnauthenticated()
    p = sess.principal
    if not any(r in p.roles for r in ROLES):
        raise AuthForbidden({"reason": "role"})
    rep = report(policy_service, inputs)
    audit.append(con, clock, anchor=anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="RULE_DIVERGENCE_REPORTED", outcome="success",
                 correlation_id=correlation_id, object_ref="OP-POL-07",
                 details={"compared_sets": rep["compared_sets"], "inputs": rep["inputs"], "divergent": rep["count"], "null_outputs": rep["null_outputs"]})
    return rep


def legacy_case_inputs(handle):
    """The shipped cases as divergence inputs from an open READ-ONLY legacy snapshot handle (AD-01): id, amount, region, year, status, severity."""
    rows = handle.execute("SELECT id, amount, region, created_at, status, severity FROM cases ORDER BY id")
    return [{"case_id": r[0], "amount": r[1], "region": r[2], "year": (r[3] or "")[:4] or None, "status": r[4], "severity": r[5]} for r in rows]
