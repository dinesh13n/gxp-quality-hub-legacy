---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "alert-catalog.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/obs/alerts.py", "docs/29-incident-bcdr/incident-severity-matrix.md", "docs/37-operating-model/escalation-model.md", "docs/32-finops/production-token-dashboard-spec.md DS-2", "tests/hub/test_tst_hub_stg31_slo_alerts.py", "hub/obs/log.py", "hub/obs/collect.py", "hub/obs/metrics.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
Thirteen alert rules, defined as data in `hub/obs/alerts.py` and evaluated deterministically by `python -m hub.obs evaluate`. **There is no pager, on-call rota, ticketing or alert manager (OD-04), so "firing" means "listed in the evaluation output and in the runbook's first step"; nothing is delivered.** Severity reuses the Stage 29 scale. Three rules (the tripwires) treat a missing sensor as firing; four depend on metrics or wiring that do not exist yet and report no_data. Alert quality is enforced by tests A01 (every rule has an owner, an action and an existing runbook entry; ids unique; closed rule types) and A02 (semantics).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AC-1 Rules (generated from `hub.obs.alerts.RULES`; test D03 checks every id is here)
| ID | Alert | Severity | Condition | If metric absent | Owner role | Action | Runbook |
|---|---|---|---|---|---|---|---|
| ALT-01 | Model call recorded | SEV-B | sum of `model_calls_total` > 0 | fires | RL-02 service owner (Dinesh Naik, interim) | Stop the release (G5); find the caller of record_model_call; do not clear | RB-01 |
| ALT-02 | Egress attempt recorded | SEV-B | sum of `egress_attempts_total` > 0 | fires | RL-02 service owner (Dinesh Naik, interim) | Identify the destination from the egress guard record; contain | RB-02 |
| ALT-03 | Zone H act accepted for a non-human actor | SEV-A | sum of `zone_h_service_actor_accepted` > 0 | fires | Engagement lead (Dinesh Naik) | Treat as a regulated-act breach: freeze, verify the audit chain | RB-03 |
| ALT-04 | Audit chain verification failed | SEV-A | `audit_chain_verify_ok` = 0 | no_data | Engagement lead (Dinesh Naik) | Run verify-audit on a sandbox copy; restore per dr-plan if confirmed | RB-04 - needs: metric not exported yet (GAP, F-29-01) |
| ALT-05 | Projection mismatch | SEV-B | sum of `projection_mismatch_count` > 0 | no_data | RL-02 service owner (Dinesh Naik, interim) | Run projection verify; rebuild from the decision events | RB-04 - needs: metric not exported yet (GAP) |
| ALT-06 | Server-error ratio high | SEV-C | 5xx share of `http_requests_total` > 1.0% once >= 20 requests | no_data | RL-02 service owner (Dinesh Naik, interim) | Find the op_id with the 5xx status; read its log lines by correlation id | RB-05 |
| ALT-07 | Failed-login burst | SEV-C | increase of `auth_failures_total` {reason in bad_credentials/locked} since the previous evaluation > 10 | no_data | RL-02 service owner (Dinesh Naik, interim) | Check lockouts; confirm the callers are known; rotate credentials if not | RB-06 |
| ALT-08 | Requests are being rate limited | SEV-C | increase of `auth_failures_total` {reason in rate_limited} since the previous evaluation > 0 | no_data | RL-02 service owner (Dinesh Naik, interim) | Identify the caller; decide whether the limit or the caller is wrong | RB-06 |
| ALT-09 | Scheduled run missed | SEV-C | sum of `run_missed_total` > 0 | no_data | RL-02 service owner (Dinesh Naik, interim) | Manual idempotent catch-up run (OD-28); record why it was missed | RB-07 |
| ALT-10 | Circuit breaker open | SEV-C | `resilience_breaker_state` = 1 | no_data | RL-02 service owner (Dinesh Naik, interim) | Check the source (failure-injection F01); wait for the cooldown probe | RB-08 - needs: GuardedGateway is not wired into gateway-pull (D-28-01) |
| ALT-11 | Retry budget refused a retry | SEV-C | increase of `resilience_retries_denied_total` since the previous evaluation > 0 | no_data | RL-02 service owner (Dinesh Naik, interim) | A storm was prevented; look for the failing dependency and the first error | RB-08 - needs: GuardedGateway is not wired (D-28-01) |
| ALT-12 | Telemetry privacy or schema finding | SEV-B | sum of `telemetry_lint_findings_total` > 0 | no_data | RL-02 service owner (Dinesh Naik, interim) | Run the lint to see the position and kind (never the text); stop exporting that sample; treat as IS-04 if a secret was involved | RB-09 |
| ALT-13 | Error budget exhausted or nearly | SEV-C | any SLO in RED/EXHAUSTED | no_data | Engagement lead (Dinesh Naik) | Apply error-budget-policy.md EB-3 | RB-10 |

### AC-2 Quality criteria applied [Verified Fact: tests A01, A02]
| Criterion | How met |
|---|---|
| Actionable | every rule has an `action` and a runbook entry (RB-nn); no "FYI" alert exists; informational counters are on dashboards instead |
| Owned | every rule names a role (RL-02 interim Dinesh, or the Engagement lead); no one else exists (OD-34) |
| Symptom or invariant, not cause noise | invariants (ALT-01..05) fire on a single event; symptoms (ALT-06..08) use a ratio with a minimum volume or a delta; no CPU / memory style alert exists |
| No flapping | state-based, evaluated on demand; delta rules compare two evaluations so a restart (counters reset) cannot produce a false negative that stays hidden: a decreasing counter gives a negative increase, which does not fire (documented limit) |
| Missing data is not "fine" | no_data is reported separately; tripwires fire on absence |
| Privacy | evaluator output carries ids, counts and reasons only; lint findings are never echoed (A04) |

### AC-3 Severity routing (candidate)
SEV-A: stop work, follow `docs/29-incident-bcdr`, Dinesh decides. SEV-B: stop the release, contain, Dinesh decides. SEV-C: handle in the working session, record in the run notes. The agent may not clear or waive a SEV-A or SEV-B (HAR-11, TP-14).

### AC-4 Thresholds
All numeric thresholds (10 failed logins per evaluation interval, 1 % server errors with at least 20 requests, any missed run, any retry refused) are AGENT ASSUMPTIONS A-31-06 / A-31-07 with no traffic behind them. They are meant to be wrong in the safe direction (sensitive) and to be re-derived from the first 30 days of real data (D-31-10).

### AC-5 What is not alerted
Latency (no target, PNFR-06), queue depth growth (no target), disk usage / host (no host), source freshness (no metric), per-user behaviour (privacy).

### AC-6 Evaluation procedure
Collect samples (`obs-snapshot` or the latest `obs_metric` rows exported to a file), keep the previous file, run `python -m hub.obs evaluate --samples NOW --previous BEFORE [--availability FILE --timeliness FILE]`. The exit code is 1 when anything fires or the lint finds something.

## Evidence References
`hub/obs/alerts.py`, `docs/29-incident-bcdr/incident-severity-matrix.md` (SEV-A/B/C), `docs/32-finops/production-token-dashboard-spec.md` DS-2 (P1 / P2 route), tests A01-A04, T03.

## Assumptions
- A-31-06 Failed-login burst threshold 10 per interval. A-31-07 5xx ratio 1 % with minimum 20 requests. Confirm after real traffic: Dinesh.

## Unknowns
- U-31-10 Whether an alert delivery channel will ever exist (D-31-08).

## Unresolved Issues
- ALT-04, ALT-05 need metrics that are not exported; ALT-10, ALT-11 need the guarded gateway wired (D-28-01).
- No delivery: the stage proves the rules, not that a human is told.

## Residual Risks
- RR-31-11 Alert fatigue cannot be assessed without traffic. Low now.
- RR-31-12 A restart resets process-local counters; delta rules then under-report for one interval. Low.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
