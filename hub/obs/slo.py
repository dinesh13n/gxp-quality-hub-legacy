"""SLO CANDIDATES, error-budget arithmetic and burn rates (Stage 31; docs/31-observability/slo-sla-definitions.md).

Every objective here is a CANDIDATE written by the agent from the working targets in the PRD (PNFR-01, PNFR-02, A-09-04). None is measured against real
traffic, agreed with a business owner, or promised to anyone: no SLA exists (OD-04). `status` is always "CANDIDATE" and nothing in this module is
connected to a release gate, an alert channel or a freeze. Integer / Decimal arithmetic only; no clock; a window with no events is NO_DATA, never 100 %.

States of an evaluated SLO (error-budget-policy.md EB-2): NO_DATA (no events), GREEN (>= 50 % of the budget left), AMBER (10 % to < 50 %),
RED (> 0 % to < 10 %), EXHAUSTED (no budget left). Thresholds are Assumption A-31-03.
"""
import decimal

D = decimal.Decimal
HUNDRED = D(100)
GREEN_AT, AMBER_AT = D("50"), D("10")

SLOS = (
    {"id": "SLO-01", "name": "Availability in scheduled hours", "sli": "minutes with a successful /healthz self-probe / window minutes",
     "target_pct": "99.5", "window_days": 30, "basis": "PNFR-01 / A-09-04 (archived working target, not measured)",
     "source": "hub.web.nfr.availability_report", "sli_available": True},
    {"id": "SLO-02", "name": "Overnight run finished before 06:00 local", "sli": "scheduled nights finished before the deadline / scheduled nights",
     "target_pct": "95", "window_days": 28, "basis": "PNFR-02 asks 100 % of nights (a zero budget); 95 % is the agent's budgetable candidate (D-31-03)",
     "source": "hub.web.nfr.timeliness_report", "sli_available": True},
    {"id": "SLO-03", "name": "Requests answered without a server error", "sli": "HTTP responses with status < 500 / HTTP responses",
     "target_pct": "99", "window_days": 30, "basis": "agent candidate (Assumption A-31-02); 4xx are client outcomes and count as good",
     "source": "http_requests_total", "sli_available": True},
    {"id": "SLO-04", "name": "Audit chain verifies", "sli": "audit_chain_verify_ok readings equal to 1 / readings",
     "target_pct": "100", "window_days": 30, "basis": "PNFR-09; integrity, so no budget (an exhausted budget = SEV-A)",
     "source": "audit_chain_verify_ok (GAP: not exported; F-29-01)", "sli_available": False},
    {"id": "SLO-05", "name": "Partner source freshness", "sli": "pulls newer than the staleness limit / pulls",
     "target_pct": "95", "window_days": 30, "basis": "PNFR-04 (stale signal max 24 h, R2); no freshness timestamp is exported",
     "source": "none (GAP)", "sli_available": False},
)
for _s in SLOS:
    _s["status"] = "CANDIDATE"
    _s["sla"] = "none: no SLA is committed to anyone"

INVARIANTS = (
    {"id": "INV-01", "metric": "model_calls_total", "rule": "= 0", "basis": "PNFR-18, OD-08"},
    {"id": "INV-02", "metric": "egress_attempts_total", "rule": "= 0", "basis": "FR-CO-04"},
    {"id": "INV-03", "metric": "zone_h_service_actor_accepted", "rule": "= 0", "basis": "FR-GATE-03"},
)


def by_id(slo_id):
    return [s for s in SLOS if s["id"] == slo_id][0]


def _pct(x, places="0.01"):
    return format(D(x).quantize(D(places), rounding=decimal.ROUND_HALF_EVEN), "f")


def evaluate(slo, good, total):
    """Error-budget position for `good` of `total` events in the window. -> dict of strings / ints (JSON-ready)."""
    good, total = int(good), int(total)
    if good < 0 or total < 0 or good > total:
        raise ValueError("good must be within 0..total")
    target = D(slo["target_pct"])
    out = {"slo": slo["id"], "status": slo["status"], "target_pct": slo["target_pct"], "good": good, "total": total, "bad": total - good}
    if total == 0:
        return dict(out, state="NO_DATA", sli_pct=None, allowed_bad=None, budget_remaining_pct=None, low_volume=None)
    sli = D(good) * HUNDRED / D(total)
    allowed = D(total) * (HUNDRED - target) / HUNDRED
    bad = D(total - good)
    if allowed == 0:
        remaining = HUNDRED if bad == 0 else D(0)
    else:
        remaining = max(D(0), (allowed - bad) * HUNDRED / allowed)
    return dict(out, sli_pct=_pct(sli), allowed_bad=_pct(allowed), budget_remaining_pct=_pct(remaining), state=state_of(remaining, bad, allowed),
                low_volume=bool(allowed < 1))


def state_of(remaining_pct, bad, allowed):
    if bad > allowed or (allowed == 0 and bad > 0) or remaining_pct <= 0:
        return "EXHAUSTED"
    if remaining_pct >= GREEN_AT:
        return "GREEN"
    return "AMBER" if remaining_pct >= AMBER_AT else "RED"


def burn_rate(bad, total, target_pct):
    """Speed of budget use: 1.0 = exactly on budget, > 1 = faster. None when there are no events or the target is 100 % (no budget)."""
    bad, total = int(bad), int(total)
    budget = (HUNDRED - D(target_pct)) / HUNDRED
    if total == 0 or budget == 0:
        return None
    return _pct(D(bad) / D(total) / budget, "0.1")


# Multi-window burn-rate pairs (Google SRE workbook shape). Numbers are Assumption A-31-04; windows are in the unit the caller's data has.
BURN_PAIRS = (("fast", "5m and 1h", 14.4), ("slow", "30m and 6h", 6.0), ("ticket", "6h and 3d", 1.0))


def burn_verdict(short_rate, long_rate, threshold):
    """Both windows must burn at or above the threshold (short window = still happening, long window = big enough to matter)."""
    if short_rate is None or long_rate is None:
        return "NO_DATA"
    return "BURNING" if D(short_rate) >= D(str(threshold)) and D(long_rate) >= D(str(threshold)) else "OK"


def counts_http(samples):
    """(good, total) for SLO-03 from http_requests_total samples."""
    total = bad = 0
    for s in samples:
        if s["name"] == "http_requests_total" and s["value"].isdigit():
            n = int(s["value"])
            total += n
            bad += n if str(s["labels"].get("status", "")).startswith("5") else 0
    return total - bad, total


def counts_availability(report):
    """(good, total) for SLO-01 from hub.web.nfr.availability_report."""
    return report["window_minutes"] - report["down_minutes"], report["window_minutes"]


def counts_timeliness(report):
    """(good, total) for SLO-02 from hub.web.nfr.timeliness_report."""
    return report["finished_before_deadline"], report["nights_count"]
