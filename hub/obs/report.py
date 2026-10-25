"""One evaluation of a sample list (Stage 31): lint -> SLO positions -> alerts. Pure; the caller supplies the samples and any measured reports.

`evaluate(samples, previous, availability, timeliness)`: `availability` / `timeliness` are the dicts of hub.web.nfr (measured on supplied probe and run
logs; their own labels say so). An SLO whose SLI source is missing is reported as NO_DATA with its reason, never as met. The result carries the label
'synthetic, unvalidated' and states that nothing is a commitment.
"""
from hub.obs import alerts, catalog, slo

LABEL = "synthetic, unvalidated"
CLAIM = "SLOs are CANDIDATES and alerts are listed, not sent; no SLA is committed to anyone (OD-04)"


def _slo_rows(samples, availability, timeliness):
    rows = []
    for s in slo.SLOS:
        inputs = {"SLO-01": availability and slo.counts_availability(availability), "SLO-02": timeliness and slo.counts_timeliness(timeliness),
                  "SLO-03": slo.counts_http(samples)}.get(s["id"])
        if inputs is None:
            rows.append({"slo": s["id"], "status": s["status"], "state": "NO_DATA", "reason": "no SLI source: " + s["source"]})
        else:
            rows.append(slo.evaluate(s, *inputs))
    return rows


def evaluate(samples, previous=None, availability=None, timeliness=None):
    findings = catalog.lint_samples(samples)
    work = list(samples) + [catalog.sample("telemetry_lint_findings_total", "counter", {}, len(findings))]
    rows = _slo_rows(samples, availability, timeliness)
    states = dict((r["slo"], r["state"]) for r in rows)
    result = alerts.evaluate(work, previous, states)
    return {"label": LABEL, "claim": CLAIM, "lint": findings, "slo": rows, "alerts": result,
            "tripwires": dict((s["name"], s["value"]) for s in samples if s["name"] in
                              ("model_calls_total", "egress_attempts_total", "zone_h_service_actor_accepted"))}
