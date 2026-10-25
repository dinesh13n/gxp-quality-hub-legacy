---
stage: "31 — Observability + SLO/SLA Engineering"
artifact: "observability-validation.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["tests/hub/test_tst_hub_stg31_catalog.py", "tests/hub/test_tst_hub_stg31_slo_alerts.py", "tests/hub/test_tst_hub_stg31_trace_cli.py", "tests/hub/test_tst_hub_stg31_static_docs.py", "tests/hub/test_tst_hub_stg31_egress_guard.py", "docs/31-observability/evidence/", "tests/hub/regression_groups.json", "tests/characterization/run_characterization.py", "hub/obs/log.py", "hub/obs/collect.py", "hub/obs/metrics.py", "hub/web/obs_http.py", "docs/12-specs/observability-spec.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic, unvalidated (a synthetic repository, validated against no organisation). Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08) and loopback-only; `zone_h.holders` ships EMPTY. Every SLO, alert threshold, window and budget number is a CANDIDATE written by the agent under OD-32 (scope defaults), not a measured need and not approved by Dinesh Naik. No SLA is committed to anyone.**

## Summary
**Gate outcome (the agent's computation, a recommendation to the Engagement lead): CONDITIONAL PASS.** Telemetry covers every signal in scope that applies to a No-AI loopback product; AI and agent telemetry are N/A with the tripwire made observable; SLOs and alerts are defined, as candidates, and validated by 19 tests; telemetry is privacy safe by construction and by lint. It is not a PASS because (1) nothing is wired: no shipped command calls the new modules and HTTP metrics reach `obs_metric` only when `serve` stops; (2) six specified metrics are not exported, so two alerts and one SLO report no_data; (3) no SLO is measured on real traffic and no alert has a delivery channel; (4) only 4 of the 21 declared log events are emitted. No blocking condition remains: Stage 32 (already merged) and later stages can proceed. Nothing here accepts a risk (OD-32).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### OV-1 Completion gate
| Condition | Status | Evidence |
|---|---|---|
| Telemetry covers all listed signals (agents N/A) | MET with documented gaps | observability-architecture OA-5; ai-telemetry-spec; agent-telemetry-spec (N/A); metrics-spec MS-4 gaps |
| SLOs and alerts defined and validated | MET as CANDIDATES | slo-sla-definitions; alert-catalog; tests S01-S03, A01-A04 |
| Telemetry is privacy-safe | MET by construction (whitelist, lint, trace drop) | logging-spec LS-2; tests C02, D04, T01 |
| All 12 artifacts exist | MET | `docs/31-observability/`; test D02 |
| Critical gaps resolved or documented | MET | OV-5 open items with owner |
| Evidence supports the conclusion | MET for what is claimed | `evidence/` |

### OV-2 Analysis dimensions
| Dimension | Finding | Confidence |
|---|---|---|
| Coverage | requests, errors, business outcomes and tripwires are covered; log events 4/21 emitted (F-31-01); 6 OBS-4 metrics absent (F-31-04); HTTP counters volatile (F-31-02); freshness absent | High |
| Privacy safety | 14-field whitelist, closed label sets, lint with no echo, trace drop of leaky lines; residual: id-shaped strings may carry an e-mail (RR-31-03); principal-id personal-data status Unknown | High (mechanism) / Low (future callers) |
| Alert quality | 13 rules, each with owner, action, runbook; tripwires fire on absence; thresholds are untested guesses; no delivery channel | Medium |
| SLO appropriateness | availability, timeliness and error ratio are reasonable *measurements* of PNFR targets; PNFR-02 at 100 % has no budget (D-31-03); latency deliberately has no SLO; two SLOs lack an SLI | Medium |

### OV-3 Findings register (new in Stage 31; severities are agent Inference)
| ID | Finding | Class | Severity | Route |
|---|---|---|---|---|
| F-31-01 | 17 of 21 declared log events are never emitted (audit_log / run_event hold the facts); `http_request`, `fts_engine_selected`, `startup_selfcheck` only | Verified Fact | Medium | D-31-09 |
| F-31-02 | HTTP counters are in memory and flushed only on graceful `serve` stop | Verified Fact | Medium | D-31-01, Stage 30 |
| F-31-03 | label/kind drift vs OBS-4 (`http_request_duration_ms`, `defaulted_outputs_total`, `run_duration_seconds` kind) | Verified Fact | Low | D-31-06, spec addendum |
| F-31-04 | six OBS-4 metrics not exported | Verified Fact | Medium | D-31-06 |
| F-31-05 | logs to stderr only; no file, rotation, retention (BEH-OBS-07) | Verified Fact | Medium | D-31-05 |
| F-31-06 | `actor` / `object_ref` accept any id-shaped string, e-mail included | Inference | Low | D-31-09 |
| F-31-07 | outbound gateway GET carries no correlation id | Verified Fact | Low | D-31-07 |
| F-31-08 | label values from stored rows (`source`, `function`) are bounded only by the lint | Inference | Low | A-31-05 |
| F-31-09 | no stored percentiles; latency is measure-only | Verified Fact | Low | none |
| F-31-10 | the tripwire sensor path was untested end to end before this stage; now tested; bypass of `record_model_call` remains guarded by deny-list only | Verified Fact | Low | RR-31-08 |

### OV-4 Test evidence (run on the reference laptop, Python 3.10.12, sandbox copies, checksum gate rc 0 before and after every call)
| Group | Selectors | Executed methods | Counts | Wall s |
|---|---|---|---|---|
| B | TST_CO_01 TST_CO_02 TST_CO_04 TST_CO_05 TST_CO_06 TST_CO_07 TST_CO_11 TST_CO_13 TST_CO_14 INC02 | 42 of 42 | {'ERROR': 0, 'FAIL': 0, 'ok': 41, 'skipped': 1} | 126.7 |
| E31 | E31EGRESS | 1 of 1 | {'ERROR': 0, 'FAIL': 0, 'ok': 1, 'skipped': 0} | 57.9 |
| S20 | STG20 | 18 of 18 | {'ERROR': 0, 'FAIL': 0, 'ok': 18, 'skipped': 0} | 80.1 |
| S27 | STG27 | 25 of 25 | {'ERROR': 0, 'FAIL': 0, 'ok': 25, 'skipped': 0} | 62.0 |
| S31 | STG31 | 19 of 19 | {'ERROR': 0, 'FAIL': 0, 'ok': 19, 'skipped': 0} | 58.8 |

Characterization harness: 133/134 CT checks passed; OVERALL FAIL only from CT-13 (Node patch drift, S24-DEV-04); CT-17 and CT-18 NOT-RUN as before (U-07-05, HAR-05)
Data backup checksum (`sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt`): rc 0 before and rc 0 after.
Not run on the laptop (speed rule, S31-DEV-05): the other groups; the orchestrator runs the full regression in the cloud workspace (OD-23).

### OV-5 Open items and decisions for Dinesh Naik (recommended default in brackets; defaults are NOT approvals)
| ID | Item | Owner | Due |
|---|---|---|---|
| D-31-01 | Persist HTTP metrics periodically (flush on an interval and a `hub runs obs-snapshot`-style job) [yes, at Stage 30; edit to `hub/web/app.py`] | Engagement lead (Dinesh Naik) | Stage 30 |
| D-31-02 | Wire `resilience_samples` into the snapshot together with `GuardedGateway` (D-28-01) [yes, together] | Engagement lead (Dinesh Naik) | Stage 30 |
| D-31-03 | SLO-02: keep PNFR-02 at 100 % of nights or adopt 95 % [95 % as the SLO, 100 % stays the requirement] | Engagement lead (Dinesh Naik) | Stage 34 |
| D-31-04 | A read-only `/metrics` route (route-registry change) [defer; file exposition suffices] | Engagement lead (Dinesh Naik) | Stage 30 |
| D-31-05 | Log destination and hold-all retention [append-only file by the launcher; no rotation that deletes] | Engagement lead (Dinesh Naik) | Stage 30 |
| D-31-06 | Export the six gap metrics and align OBS-4 labels (spec addendum or code) [after the F-29-01 fix] | Engagement lead (Dinesh Naik) | Stage 30 |
| D-31-07 | Send `X-Correlation-Id` on the gateway GET [yes; non-add edit in `hub/adapters`] | Engagement lead (Dinesh Naik) | Stage 30 |
| D-31-08 | Alert delivery channel / on-call [none until a second human exists; manual evaluation RB-00] | Engagement lead (Dinesh Naik) | before real data |
| D-31-09 | Emit or retire the 17 never-emitted log events; tighten the id pattern [emit auth_denied, zone_h_attempt, decision_appended; retire the rest; no e-mail-shaped ids] | Engagement lead (Dinesh Naik) | Stage 30 |
| D-31-10 | Re-derive all SLO / alert numbers after 30 days of real use; decide whether any becomes a commitment [no SLA before a measured window] | Engagement lead (Dinesh Naik) | after first real use |

### OV-6 Deviations (proposed; none approved by Dinesh)
| ID | Deviation | Default taken |
|---|---|---|
| S31-DEV-01 | New modules in `hub/obs/`; nothing wired into a shipped command or route | no behaviour change; wiring needs D-31-01/02 |
| S31-DEV-02 | The only non-add edits: `tests/hub/regression_groups.json` (groups S31, E31 appended) and `tests/hub/non_add_edits.json` (reset) | listed in `non_add_edits.json` |
| S31-DEV-03 | "Dashboards" are text reports and Prometheus-style text, not a visual stack (none is chosen) | spec + `hub.obs evaluate` |
| S31-DEV-04 | AI telemetry = tripwire only; agent telemetry N/A | OD-08, OD-27 |
| S31-DEV-05 | Laptop verification limited to the new tests, groups B, S20, S27 and the characterization harness | orchestrator runs the full regression |
| S31-DEV-06 | SLO-02 candidate 95 % differs from PNFR-02's 100 % | recorded, D-31-03 |
| S31-DEV-07 | The CLI `python -m hub.obs` is a new entry point; exit codes 0 / 1 / 2 are local to it | documented in `hub/obs/cli.py` |

## Evidence References
`docs/31-observability/evidence/results.json` (test and harness counts), `tests/hub/regression_groups.json` (groups S31, E31), the five STG31/E31 test modules.

## Assumptions
- A-31-16 The laptop's results stand in for the orchestrator's cloud regression until it runs. Confirm: orchestrator.

## Unknowns
- U-31-14 Whether production-like load would change any threshold (no load exists).

## Unresolved Issues
- See OV-5. CT-13 of the characterization harness fails only from Node patch drift (S24-DEV-04) when it fails; it is an environment item, not a Stage 31 effect.

## Residual Risks
- RR-31-01, RR-31-05, RR-31-13 (see the other artifacts). Nothing in this stage reduces them to zero.

## Change History
- v0.1 (2026-10-25) first issue, Stage 31 BUILD. No prior version.
