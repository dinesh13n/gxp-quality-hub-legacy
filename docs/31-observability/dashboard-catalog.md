---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "dashboard-catalog.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/32-finops/production-token-dashboard-spec.md", "hub/obs/report.py", "hub/obs/expo.py", "hub/runs/reports.py", "docs/12-specs/observability-spec.md OBS-6", "hub/obs/log.py", "hub/obs/collect.py", "hub/obs/metrics.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
No dashboard platform exists or is chosen (ADR-015), so the catalogue defines **five dashboards as read-only text reports** with their data source and the question each answers. Two are built (`python -m hub.obs evaluate` for D-1..D-3 inputs, `hub report health` for D-4); the rest are specifications. Panels that need unexported metrics are marked and show NO_DATA, never zero. Every panel carries the label 'synthetic, unvalidated' while `data_origin = synthetic`.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DC-1 Catalogue
| ID | Dashboard | Audience role | Panels (metric / source) | Built? |
|---|---|---|---|---|
| D-1 | Tripwires and controls | service owner RL-02 | `model_calls_total`, `egress_attempts_total`, `zone_h_service_actor_accepted` (all must read 0), `zone_h_attempts_total`, `override_total`; release gate G5 | built: `hub.obs evaluate` -> `tripwires` + ALT-01..03 |
| D-2 | Service health and SLOs | RL-02, Engagement lead | SLO-01..05 position, state and budget remaining; `http_requests_total` by status class; 5xx ratio; `auth_failures_total{reason}` | built: `hub.obs evaluate` -> `slo`, ALT-06..08, ALT-13 (SLO-01/02 need the measured reports as input) |
| D-3 | Data flow | reviewers RL-08 | `intake_items_total{source,outcome}`, `intake_noop_duplicate_total`, `quarantine_depth`, `exception_queue_depth{queue}`, `run_backlog_remaining{job}`, `run_missed_total`, `run_duration_seconds` | spec; data from `obs_metric` rows, `hub report queues` |
| D-4 | Run health | RL-02 | run list, abandoned / failed runs, missing runs, audit anchor status | built: `hub report health` (Stage 15) |
| D-5 | Resilience | RL-02 | `resilience_breaker_state`, `resilience_retries_denied_total`, `resilience_bulkhead_rejected_total`, `resilience_retry_budget_tokens` per dependency | spec; samples function built, not wired (D-31-02) |
| D-6 | Cost guard (Stage 32 P1-P3) | cost owner RL-09 (VACANT) | the D-1 tripwire panel is Stage 32's primary cost panel (P1, P2); toolchain cost lines are manual (P8) | covered by D-1 |

### DC-2 Rules
1. A panel whose metric is absent shows NO_DATA, not 0 (except tripwires, where absence is a finding).
2. No forecast, benchmark or comparison against a real organisation is shown (nothing to compare with).
3. Latency is shown as measured p50 / p95 with no threshold (PNFR-06 measure-only; `hub report latency`).
4. Access follows the permission matrix TP-01..TP-15; reading restricted evidence by reviewer / finance / integration roles stays refused (Stage 27 A-27-02).
5. No viewer, share or schedule feature exists; reports are produced on demand.

### DC-3 Rendering
Text/JSON from `python -m hub.obs evaluate` (exit 0 = clean, 1 = something fires or lint finding, 2 = unreadable input) and Prometheus text from `expo`. A visual layer is deferred until a host and a stack exist (U-31-01).

## Evidence References
`docs/32-finops/production-token-dashboard-spec.md` DS-1/DS-2, `hub/runs/reports.py` (health), `hub/obs/report.py`, tests A03/A04/T03.

## Assumptions
- A-31-14 Text reports are an acceptable dashboard form while one person operates the hub. Confirm: Dinesh.

## Unknowns
- U-31-01 Hosting and stack. U-31-09 Who would view the dashboards beyond Dinesh (all roles but RL-01 VACANT, OD-34).

## Unresolved Issues
- D-3 and D-5 are specifications without a runner (the data exists in `obs_metric`, the join is not built).

## Residual Risks
- RR-31-10 Dashboards nobody opens; same as RR-31-01.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
