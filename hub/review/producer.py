"""Automatic rule-trace producer (Stage 20 DW-08; FR-REV-01, FR-GATE-06, PNFR-15; RTD-69 / PCH-23).

Before Stage 20 a rule trace existed only after an operator piped a hand-made JSON request into `python -m hub.web record-trace`. This
producer evaluates ONE rule function for every case of the decision record with the rule service itself and stores each result as a
rule trace (ReviewService.record_trace, insert-only, one audit record per trace), so explanations (OP-REV-02) and the override / dismiss /
refuse flags (OP-GATE-04) exist without manual work:
  * the rule set is the ACTIVE set of the function (authoritative) or an explicitly named set (what-if, authoritative = false). Nothing is
    active in the shipped build (OD-S12-04), so without --ruleset-ref the producer refuses with E-POL-NO-ACTIVE-RULESET and stores nothing;
  * inputs are the case attributes read through the read-only legacy snapshot adapter (the same reader as the R2 divergence report);
    only the fields the function declares are passed (hub.policy.engine.FUNCTIONS);
  * idempotent: a case whose latest trace for (function, rule set) has the same inputs and result is skipped (`unchanged`);
  * an input the rule service refuses (E-POL-INPUT-INVALID) is counted, not stored: a refusal is not a rule output;
  * it decides nothing, changes no case state and imports nothing from hub.gate (AC-GATE-11): actor `rule-trace-producer`, kind `rule`.
No model call, no clock of its own, no network.
"""
import json

from hub.policy import engine
from hub.policy.errors import InputInvalid, NoActiveRuleset, UnknownFunction
from hub.review.service import ReviewService
from hub.security.canonical import canonical

ACTOR = "rule-trace-producer"


def load_case_inputs(legacy_root, run_dir):
    """The shipped cases (id, amount, region, year, status, severity) from the hash-gated READ-ONLY legacy snapshot (AD-01); same columns
    as the R2 divergence reader, read here so hub.review does not import hub.r2 (no new package cycle)."""
    from hub.adapters import legacy_sqlite
    h = legacy_sqlite.open_snapshot(legacy_root, "legacy.sqlite3", run_dir, pinned=True)
    try:
        rows = h.execute("SELECT id, amount, region, created_at, status, severity FROM cases ORDER BY id")
    finally:
        h.close()
    return [{"case_id": r[0], "amount": r[1], "region": r[2], "year": (r[3] or "")[:4] or None, "status": r[4], "severity": r[5]} for r in rows]


def _fields(function):
    spec = engine.FUNCTIONS[function]
    return spec["required_numeric"] + spec["optional_numeric"] + spec["null_fields"]


def produce(con, s, clock, anchor, policy_service, case_inputs, function, ruleset_ref=None, correlation_id="trace-producer"):
    """Evaluate `function` for every case in `case_inputs` ({case_id, ...attributes}) that exists in the decision record. Returns the report."""
    if function not in engine.FUNCTIONS:
        raise UnknownFunction({"function": str(function)[:40], "catalogue": sorted(engine.FUNCTIONS)})
    active = policy_service.active().get(function)
    ref = ruleset_ref or active
    if ref is None:
        raise NoActiveRuleset({"function": function, "hint": "no active rule set (OD-S12-04): name one with --ruleset-ref for a what-if trace"})
    policy_service.get_ruleset(ref)  # E-POL-NOT-FOUND for an unknown set, before anything is written
    review = ReviewService(con, s, clock, anchor)
    known = set(r[0] for r in con.execute("SELECT case_id FROM case_state"))
    rep = {"function": function, "ruleset_ref": ref, "authoritative": ref == active, "cases_in": len(case_inputs), "stored": 0,
           "unchanged": 0, "no_case": 0, "input_invalid": 0, "trace_ids": [], "label": "synthetic, unvalidated"}
    fields = _fields(function)
    for c in sorted(case_inputs, key=lambda x: str(x.get("case_id"))):
        cid = c.get("case_id")
        if cid not in known:
            rep["no_case"] += 1
            continue
        inputs = dict((k, c.get(k)) for k in fields)
        try:
            result = policy_service.evaluate(function, inputs, ref)
        except InputInvalid:
            rep["input_invalid"] += 1
            continue
        last = con.execute('SELECT inputs, result FROM rule_trace WHERE case_id = ? AND "function" = ? AND ruleset_ref = ? ORDER BY trace_id DESC'
                           " LIMIT 1", (cid, function, ref)).fetchone()
        if last is not None and last[0] == canonical(inputs) and json.loads(last[1]) == json.loads(canonical(result)):
            rep["unchanged"] += 1
            continue
        t = review.record_trace(ACTOR, "rule", cid, function, ref, inputs, result, correlation_id)
        rep["stored"] += 1
        rep["trace_ids"].append(t["trace_id"])
    return rep


def flag_trail(con, flag_id):
    """Every human action on a flag, oldest first, each with the audit record that carries it. For an intake-queue flag whose item matches
    no case, this is the record of the action (there is no case to append an OVERRIDE_RECORDED event to; RTD-69): the insert-only
    flag_action row plus its hash-chained audit record (FLAG_<ACTION>, object_ref flag:<id>)."""
    out = []
    for aid, action, reason, actor, at, case_id, event_id in con.execute(
            "SELECT action_id, action, reason, actor, acted_at, case_id, event_id FROM flag_action WHERE flag_id = ? ORDER BY rowid", (flag_id,)):
        seq = None
        for a_seq, details in con.execute("SELECT audit_seq, details FROM audit_log WHERE object_ref = ? AND action = ? ORDER BY audit_seq",
                                          ("flag:" + flag_id, "FLAG_" + action.upper())):
            if json.loads(details).get("action_id") == aid:
                seq = a_seq
        out.append({"action_id": aid, "action": action, "reason": {"text": reason, "trust": "untrusted"}, "actor": actor, "acted_at": at,
                    "case_id": case_id, "case_event_id": event_id, "audit_seq": seq})
    return out
