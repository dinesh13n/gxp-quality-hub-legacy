"""Alert rules as data and a deterministic evaluator (Stage 31; docs/31-observability/alert-catalog.md).

Alerts are CANDIDATES: no paging channel, on-call rota or alert manager exists (OD-04, docs/37-operating-model), so "firing" means "listed in the
output of `python -m hub.obs evaluate` and in hub report health"; nothing is sent anywhere. Severities reuse the Stage 29 scale (SEV-A / SEV-B / SEV-C).
Quality rules enforced by tests/hub/test_tst_hub_stg31_alerts.py: every rule has an owner role, an action and a runbook anchor that exists in
operational-runbook.md; every rule is actionable (no "FYI" alerts); a metric that is ABSENT is "no_data", never "ok", except for the tripwires,
where an absent sensor is itself a finding (RR-32-01: a tripwire that reads 0 only because nothing counts is weak evidence).

Rule types: gt (sum of matching samples > threshold), delta_gt (increase since the previous evaluation > threshold), ratio_gt (numerator / denominator >
threshold once the denominator reaches `min_den`), state_eq (every matching sample equals `value`), slo (an SLO state in `states`).
"""
import decimal

D = decimal.Decimal

RULES = (
    {"id": "ALT-01", "name": "Model call recorded", "severity": "SEV-B", "type": "gt", "metric": "model_calls_total", "threshold": 0,
     "absent_fires": True, "owner": "RL-02 service owner (Dinesh Naik, interim)", "action": "Stop the release (G5); find the caller of record_model_call; do not clear",
     "runbook": "RB-01"},
    {"id": "ALT-02", "name": "Egress attempt recorded", "severity": "SEV-B", "type": "gt", "metric": "egress_attempts_total", "threshold": 0,
     "absent_fires": True, "owner": "RL-02 service owner (Dinesh Naik, interim)", "action": "Identify the destination from the egress guard record; contain",
     "runbook": "RB-02"},
    {"id": "ALT-03", "name": "Zone H act accepted for a non-human actor", "severity": "SEV-A", "type": "gt", "metric": "zone_h_service_actor_accepted",
     "threshold": 0, "absent_fires": True, "owner": "Engagement lead (Dinesh Naik)", "action": "Treat as a regulated-act breach: freeze, verify the audit chain",
     "runbook": "RB-03"},
    {"id": "ALT-04", "name": "Audit chain verification failed", "severity": "SEV-A", "type": "state_eq", "metric": "audit_chain_verify_ok", "value": 0,
     "absent_fires": False, "owner": "Engagement lead (Dinesh Naik)", "action": "Run verify-audit on a sandbox copy; restore per dr-plan if confirmed",
     "runbook": "RB-04", "needs": "metric not exported yet (GAP, F-29-01)"},
    {"id": "ALT-05", "name": "Projection mismatch", "severity": "SEV-B", "type": "gt", "metric": "projection_mismatch_count", "threshold": 0,
     "absent_fires": False, "owner": "RL-02 service owner (Dinesh Naik, interim)", "action": "Run projection verify; rebuild from the decision events",
     "runbook": "RB-04", "needs": "metric not exported yet (GAP)"},
    {"id": "ALT-06", "name": "Server-error ratio high", "severity": "SEV-C", "type": "ratio_gt", "metric": "http_requests_total", "numerator_labels": {"status": "5*"},
     "threshold": "0.01", "min_den": 20, "absent_fires": False, "owner": "RL-02 service owner (Dinesh Naik, interim)",
     "action": "Find the op_id with the 5xx status; read its log lines by correlation id", "runbook": "RB-05"},
    {"id": "ALT-07", "name": "Failed-login burst", "severity": "SEV-C", "type": "delta_gt", "metric": "auth_failures_total",
     "labels": {"reason": ("bad_credentials", "locked")}, "threshold": 10, "absent_fires": False,
     "owner": "RL-02 service owner (Dinesh Naik, interim)", "action": "Check lockouts; confirm the callers are known; rotate credentials if not", "runbook": "RB-06"},
    {"id": "ALT-08", "name": "Requests are being rate limited", "severity": "SEV-C", "type": "delta_gt", "metric": "auth_failures_total",
     "labels": {"reason": ("rate_limited",)}, "threshold": 0, "absent_fires": False, "owner": "RL-02 service owner (Dinesh Naik, interim)",
     "action": "Identify the caller; decide whether the limit or the caller is wrong", "runbook": "RB-06"},
    {"id": "ALT-09", "name": "Scheduled run missed", "severity": "SEV-C", "type": "gt", "metric": "run_missed_total", "threshold": 0, "absent_fires": False,
     "owner": "RL-02 service owner (Dinesh Naik, interim)", "action": "Manual idempotent catch-up run (OD-28); record why it was missed", "runbook": "RB-07"},
    {"id": "ALT-10", "name": "Circuit breaker open", "severity": "SEV-C", "type": "state_eq", "metric": "resilience_breaker_state", "value": 1,
     "absent_fires": False, "owner": "RL-02 service owner (Dinesh Naik, interim)", "action": "Check the source (failure-injection F01); wait for the cooldown probe",
     "runbook": "RB-08", "needs": "GuardedGateway is not wired into gateway-pull (D-28-01)"},
    {"id": "ALT-11", "name": "Retry budget refused a retry", "severity": "SEV-C", "type": "delta_gt", "metric": "resilience_retries_denied_total",
     "threshold": 0, "absent_fires": False, "owner": "RL-02 service owner (Dinesh Naik, interim)",
     "action": "A storm was prevented; look for the failing dependency and the first error", "runbook": "RB-08", "needs": "GuardedGateway is not wired (D-28-01)"},
    {"id": "ALT-12", "name": "Telemetry privacy or schema finding", "severity": "SEV-B", "type": "gt", "metric": "telemetry_lint_findings_total",
     "threshold": 0, "absent_fires": False, "owner": "RL-02 service owner (Dinesh Naik, interim)",
     "action": "Run the lint to see the position and kind (never the text); stop exporting that sample; treat as IS-04 if a secret was involved",
     "runbook": "RB-09"},
    {"id": "ALT-13", "name": "Error budget exhausted or nearly", "severity": "SEV-C", "type": "slo", "states": ("RED", "EXHAUSTED"), "absent_fires": False,
     "owner": "Engagement lead (Dinesh Naik)", "action": "Apply error-budget-policy.md EB-3", "runbook": "RB-10"},
)
FIELDS = ("id", "name", "severity", "type", "owner", "action", "runbook")


def _index(samples):
    idx = {}
    for s in samples or ():
        if s["value"].lstrip("-").isdigit():
            idx.setdefault(s["name"], []).append((s["labels"], int(s["value"])))
    return idx


def _match(labels, want):
    for k, v in (want or {}).items():
        have = str(labels.get(k, ""))
        ok = have.startswith(v[:-1]) if isinstance(v, str) and v.endswith("*") else (have in v if isinstance(v, tuple) else have == v)
        if not ok:
            return False
    return True


def _sum(idx, metric, want=None):
    rows = [n for labels, n in idx.get(metric, ()) if _match(labels, want)]
    return (sum(rows) if rows else None), len(rows)


def _gt(r, idx, prev, slo):
    v, _ = _sum(idx, r["metric"], r.get("labels"))
    return None if v is None else (v > r["threshold"], {"value": v})


def _delta(r, idx, prev, slo):
    now, _ = _sum(idx, r["metric"], r.get("labels"))
    before, _ = _sum(prev, r["metric"], r.get("labels"))
    if now is None or before is None:
        return None
    return (now - before > r["threshold"], {"increase": now - before})


def _ratio(r, idx, prev, slo):
    den, _ = _sum(idx, r["metric"])
    if den is None or den < r["min_den"]:
        return None
    num, _ = _sum(idx, r["metric"], r["numerator_labels"])
    ratio = D(num or 0) / D(den)
    return (ratio > D(r["threshold"]), {"numerator": num or 0, "denominator": den})


def _state(r, idx, prev, slo):
    rows = [n for labels, n in idx.get(r["metric"], ())]
    return None if not rows else (any(n == r["value"] for n in rows), {"readings": len(rows)})


def _slo(r, idx, prev, slo):
    states = dict(slo or {})
    if not states:
        return None
    hit = sorted(k for k, v in states.items() if v in r["states"])
    return (bool(hit), {"slos": hit})


_EVAL = {"gt": _gt, "delta_gt": _delta, "ratio_gt": _ratio, "state_eq": _state, "slo": _slo}


def evaluate(samples, previous=None, slo_states=None, rules=RULES):
    """-> {firing: [...], ok: [...], no_data: [...]}, each entry {id, name, severity, detail?, reason?}. Deterministic; the inputs are not modified.
    `previous` = the samples of the earlier evaluation (needed by delta rules); `slo_states` = {slo_id: state} from hub.obs.slo.evaluate."""
    idx, prev = _index(samples), _index(previous)
    out = {"firing": [], "ok": [], "no_data": []}
    for r in rules:
        head = {"id": r["id"], "name": r["name"], "severity": r["severity"]}
        res = _EVAL[r["type"]](r, idx, prev, slo_states)
        if res is None:
            if r.get("absent_fires"):
                out["firing"].append(dict(head, reason="sensor_absent"))
            else:
                out["no_data"].append(dict(head, reason="no_data"))
        elif res[0]:
            out["firing"].append(dict(head, reason="threshold", detail=res[1]))
        else:
            out["ok"].append(dict(head, detail=res[1]))
    return out
