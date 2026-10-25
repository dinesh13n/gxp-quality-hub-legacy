---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "metrics-spec.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/obs/catalog.py", "hub/obs/collect.py", "hub/web/obs_http.py", "hub/obs/expo.py", "hub/obs/resilience_samples.py", "hub/runs/cli.py", "docs/12-specs/observability-spec.md", "tests/hub/test_tst_hub_stg31_catalog.py", "hub/obs/log.py", "hub/obs/metrics.py", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
The metric catalogue is code (`hub/obs/catalog.py`) and the table below is generated from it (test D03 checks that every name is documented here, test C05 that every OBS-4 name is catalogued). 19 metrics are exported today, 11 come from Stage 31 functions that nothing calls by default (10 resilience metrics and `telemetry_lint_findings_total`, which the evaluator computes), and 6 are specified in OBS-4 but not exported (gaps). Labels are closed sets; the lint rejects anything else.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### MS-1 Catalogue (generated from `hub.obs.catalog.CATALOG`)
| Metric | Kind | Labels | Status | Purpose |
|---|---|---|---|---|
| `audit_chain_verify_ok` | gauge | - | gap | PNFR-09 audit chain verified (needs the F-29-01 fix first) |
| `auth_failures_total` | counter | reason | implemented | PNFR-07 authentication failures |
| `db_busy_total` | counter | - | gap | CT-17 / H-14 busy evidence |
| `decision_events_total` | counter | event_type | implemented | decision volume |
| `defaulted_outputs_total` | counter | function | implemented | FR-POL-06 defaulted outputs |
| `egress_attempts_total` | counter | - | implemented | tripwire, must be 0 (FR-CO-04) |
| `exception_age_hours_p90` | gauge | queue | gap | FR-MET-05 exception age |
| `exception_queue_depth` | gauge | queue | implemented | BR-12 exception queue depth |
| `http_request_duration_ms` | histogram | op_id | implemented | PNFR-06 latency (measure-only) |
| `http_requests_total` | counter | op_id, status | implemented | PNFR-01 availability proxy |
| `intake_items_total` | counter | source, outcome | implemented | PNFR-11 intake volume by outcome |
| `intake_noop_duplicate_total` | counter | source | implemented | FR-INT-02 replay evidence |
| `model_calls_total` | counter | - | implemented | tripwire, must be 0 (PNFR-18, OD-08) |
| `override_total` | counter | action | implemented | PNFR-15 override rate |
| `projection_mismatch_count` | gauge | - | gap | FR-DEC-02 projection mismatches |
| `quarantine_depth` | gauge | queue | implemented | FR-REV-02 quarantine depth |
| `resilience_attempts_total` | counter | dependency | built_unwired | attempts sent to the dependency |
| `resilience_breaker_opened_total` | counter | dependency | built_unwired | times the breaker tripped |
| `resilience_breaker_rejected_total` | counter | dependency | built_unwired | calls refused by an open breaker |
| `resilience_breaker_state` | gauge | dependency | built_unwired | 0 closed, 1 open, 2 half-open |
| `resilience_bulkhead_in_flight` | gauge | dependency | built_unwired | calls in flight now |
| `resilience_bulkhead_rejected_total` | counter | dependency | built_unwired | calls refused by the concurrency cap |
| `resilience_calls_total` | counter | dependency | built_unwired | guarded calls |
| `resilience_retries_denied_total` | counter | dependency | built_unwired | retries refused: storm prevented |
| `resilience_retries_granted_total` | counter | dependency | built_unwired | retries paid from the budget |
| `resilience_retry_budget_tokens` | gauge | dependency | built_unwired | whole retry tokens left |
| `run_backlog_remaining` | gauge | job | implemented | FR-RUN-03 backlog |
| `run_duration_seconds` | histogram/gauge | job | implemented | PNFR-02 run duration |
| `run_finished_before_0600_local` | gauge | job | gap | PNFR-02 (reported by hub.runs.detector, not stored) |
| `run_missed_total` | counter | job | implemented | PNFR-14 missed runs (schedule enabled only) |
| `search_engine` | gauge | engine | implemented | OD-S12-12 search engine in use |
| `telemetry_lint_findings_total` | counter | - | built_unwired | privacy / schema findings in the evaluated samples |
| `unmatched_reference_rate` | gauge | source | gap | FR-MET-07 unmatched references |
| `zone_h_attempts_total` | counter | action, outcome | implemented | FR-GATE-01 Zone H attempts |
| `zone_h_service_actor_accepted` | counter | - | implemented | tripwire, must be 0 (FR-GATE-03) |
| `zone_h_service_actor_rejections_total` | counter | action | implemented | AC-GATE-09 evidence |

Status meanings: `implemented` = exported by `hub.obs.collect` / `hub.web.obs_http` today; `built_unwired` = produced by a Stage 31 function that no shipped command calls (S31-DEV-01); `gap` = in observability-spec OBS-4, not exported.

### MS-2 Rules [Verified Fact: tests C01, C02]
1. Names end in `_total` for counters (monotonic over the stored rows, recomputable), gauges are current values, histograms are a closed JSON shape (`count`, `sum_*`, `max_*`; no percentiles are stored).
2. Label names come from the metric's closed set; label values must match `^[A-Za-z0-9._:@#=-]{1,80}$`; values are decimal numbers (or the histogram shape).
3. At most 500 series per metric (A-31-05); beyond that the lint reports `cardinality`.
4. No sample may contain a prohibited pattern (credential assignment, 64-hex digest, markup / SQL fixtures); the lint reports the position and kind, not the text.

### MS-3 Findings on the existing metrics
- F-31-02 [Verified Fact] HTTP counters live in memory and reach `obs_metric` only through `WebApp.flush_metrics()` when `serve` stops (`hub/web/cli.py:70`); a killed process loses them. Confidence High.
- F-31-03 [Verified Fact] Label/kind drift against OBS-4: `http_request_duration_ms` is labelled by `op_id` only (spec: `op_id`, `status`); `defaulted_outputs_total` by `function` only (spec: `function`, `reason`); `run_duration_seconds` is a histogram in `collect.samples` but a gauge in `run_end_samples` (the catalogue accepts both kinds and the lint stays quiet; a consumer must handle both). Confidence High.
- F-31-04 [Verified Fact] Six OBS-4 metrics are not exported: `audit_chain_verify_ok` (blocked by defect F-29-01, verify-audit KeyError), `projection_mismatch_count`, `exception_age_hours_p90`, `unmatched_reference_rate`, `run_finished_before_0600_local` (computed by `hub.runs.detector`, not stored), `db_busy_total`. Alerts ALT-04 and ALT-05 and SLO-04 depend on them and report NO_DATA, not OK. Confidence High.
- F-31-08 [Inference] `source`, `function`, `event_type`, `queue` label values come from stored rows or code constants; all are identifier-shaped today. The lint is what keeps a future free-text source name out; cardinality is bounded only by the 500-series check.
- F-31-09 [Verified Fact] Percentiles: histograms store only count / sum / max, so p50 / p95 (PNFR-06) come from `hub report latency` (measure-only), not from `obs_metric`.

### MS-4 Registered gaps (not built; owner Engagement lead (Dinesh Naik), due Stage 30 unless stated)
G-1 `audit_chain_verify_ok` after the F-29-01 fix; G-2 `projection_mismatch_count`; G-3 `exception_age_hours_p90`; G-4 `unmatched_reference_rate`; G-5 `run_finished_before_0600_local` (store the detector's result); G-6 `db_busy_total` (needs a hook in `hub/store/db.py`, a behaviour-adjacent edit); G-7 persisted p50/p95. Reason not built: each needs a non-add edit of shipped code or a decision (D-31-06); the stage rule is not to change default behaviour.

### MS-5 Exposition
`python -m hub.obs expo --samples FILE` prints Prometheus text (`# HELP`, `# TYPE`, labelled lines; histograms as `_count`, `_sum`, `_max`, typed `summary`). There is no HTTP route: the route registry is frozen (TST-SEC-01); a `/metrics` route is D-31-04.

### MS-6 Resilience telemetry
`hub.obs.resilience_samples.samples(dependency, breaker, budget, bulkhead, gateway)` reads counters the Stage 28 objects already keep (test C04, including a real `GuardedGateway` with a failing stub: 2 calls, 6 attempts under `max_retries` 2). `dependency` must be an identifier, never a URL.

## Evidence References
`hub/obs/catalog.py`, `hub/obs/collect.py` docstring (implemented and not-yet lists), `hub/web/obs_http.py`, `hub/web/cli.py:60-72`, `docs/12-specs/observability-spec.md` OBS-4, tests C01-C05.

## Assumptions
- A-31-05 500 series per metric is a defect threshold, not a measured limit.
- A-31-10 Gauges and counters are read from the latest `obs_metric` rows per name+labels (not specified by OBS-4; used by the offline evaluator, which is given a samples file).

## Unknowns
- U-31-05 Whether any consumer needs percentiles stored.
- U-31-06 Real request volumes (none exist), so every threshold is untested against traffic.

## Unresolved Issues
- G-1..G-7 above; F-31-02 flush gap; F-31-03 drift (spec addendum or code change - D-31-06).

## Residual Risks
- RR-31-05 Counters lost on crash (F-31-02). Medium.
- RR-31-06 Two kinds for `run_duration_seconds`. Low.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
