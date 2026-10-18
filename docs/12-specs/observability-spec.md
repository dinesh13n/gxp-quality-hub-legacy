---
stage: "12 — Spec-Driven Design"
artifact: "observability-spec.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/adrs/ADR-016-observability.md", "docs/00-preflight/discovery/security-observability-overview.md", "docs/09-initial-prd/nfrs.md (PNFR-02, 06, 14, 18)", "docs/10-architecture/adrs/ADR-010-run-orchestration-scheduling.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Observability specification: structured-log contract with prohibited-content list, 23 normative metrics (including the model_calls_total = 0 and egress tripwires), 8 behaviours, health/latency/KPI-coverage reports, and 9 acceptance criteria. Stdlib only; no external telemetry.

## Findings
### OBS-1 Principles [Inference: ADR-016; Verified Fact: shipped code has no logging]
Observability is built from three stdlib-only sources: **structured logs**, **run records / event tables**, and **metric tables** (ADR-016). All are PII-light, correlation-id-linked, and feed the R1 measurements the PRD requires (PNFR-06 latency baseline, PNFR-14 visibility, PNFR-02 timeliness, PNFR-18 tripwire). There is no external APM, no outbound telemetry (FR-CO-04, ADR-015).

### OBS-2 Structured log contract (JSON lines to stdout and optionally a file)
| Field | Type | Rule |
|---|---|---|
| `ts` | ISO UTC | server clock |
| `level` | DEBUG/INFO/WARN/ERROR | default INFO |
| `event` | string | stable snake_case name from OBS-3 |
| `correlation_id` | string | from `X-Correlation-Id` or generated; same value in audit record and error envelope |
| `run_id` | string/null | for jobs |
| `actor` | string/null | principal id (never a name or e-mail) |
| `actor_kind` | human/service/rule/system | |
| `route` / `op_id` | string | `OP-*` id |
| `outcome` | success/denied/error | |
| `error_code` | string/null | `E-*` |
| `duration_ms` | number | for timed calls |
| `object_ref` | string/null | ids only (case, raw, link); no free text |
| `code_version`, `config_version` | string | |
Prohibited in logs: passwords, tokens, session ids, credential hashes, raw bodies of intake items, free text from Untrusted fields (log `raw_id` and `content_hash` instead), full SQL. A log-scan test (AC-OBS-04) fails on these patterns.

### OBS-3 Event names (log) and where they come from
`http_request`, `auth_login`, `auth_denied`, `zone_h_attempt`, `decision_appended`, `policy_changed`, `intake_received`, `intake_outcome`, `run_started`, `run_finished`, `run_failed`, `run_abandoned`, `projection_verify`, `audit_verify`, `golden_compare`, `config_loaded`, `db_busy`, `fts_engine_selected`, `startup_selfcheck`.

### OBS-4 Metrics (stored in `obs_metric` rows; names and meaning are normative)
| Metric | Type | Labels | Purpose / requirement |
|---|---|---|---|
| `http_request_duration_ms` | histogram (p50/p95/p99 computed from stored samples) | op_id, status | PNFR-06 baseline (R1 measures, no target) |
| `http_requests_total` | counter | op_id, status | PNFR-01 availability proxy |
| `auth_failures_total` | counter | reason | PNFR-07 |
| `zone_h_attempts_total` | counter | action, outcome | FR-GATE-01/03; alert if `outcome=accepted` ever occurs with schedule/service actor (must be 0) |
| `zone_h_service_actor_rejections_total` | counter | action | evidence for AC-GATE-09 |
| `decision_events_total` | counter | event_type | volume |
| `audit_chain_verify_ok` | gauge 0/1 | | PNFR-09 |
| `projection_mismatch_count` | gauge | | FR-DEC-02 |
| `intake_items_total` | counter | source, outcome | PNFR-11 |
| `intake_noop_duplicate_total` | counter | source | FR-INT-02 |
| `quarantine_depth` / `exception_queue_depth` | gauge | queue | FR-REV-02, BR-12 |
| `exception_age_hours_p90` | gauge | queue | FR-MET-05 |
| `unmatched_reference_rate` | gauge | source | FR-MET-07 |
| `run_duration_seconds` | histogram | job | PNFR-02 |
| `run_backlog_remaining` | gauge | job | FR-RUN-03 |
| `run_missed_total` | counter | job | PNFR-14 (only when schedule enabled) |
| `run_finished_before_0600_local` | gauge 0/1 per scheduled run | job | PNFR-02 (timezone config unknown -> labelled) |
| `model_calls_total` | counter | | **PNFR-18 tripwire; must equal 0** (Stage 32) |
| `egress_attempts_total` | counter | | FR-CO-04; must equal 0 |
| `db_busy_total` | counter | | CT-17 / H-14 evidence |
| `override_total` | counter | action | PNFR-15 (override rate) |
| `defaulted_outputs_total` | counter | function, reason | FR-POL-06 |
| `search_engine` | gauge label | fts5/fallback | OD-S12-12 |

### OBS-5 Behaviours
| ID | Behaviour | Implements |
|---|---|---|
| BEH-OBS-01 | Every request and job step emits one `http_request`/step log line with correlation id and duration; the same correlation id is on the audit record and error envelope. | PNFR-14 |
| BEH-OBS-02 | Run records (F06) are the system of record for job health; the **missing-run detector** compares expected runs (when `schedule.enabled`) with `run_event`; absent runs are listed and counted. | FR-RUN-02, PNFR-14 |
| BEH-OBS-03 | `startup_selfcheck` logs Python, SQLite, FTS5/trigram availability, config hash, gate status (mode, holders count, schedule flag). | OD-S12-12, FR-GATE-04 |
| BEH-OBS-04 | Latency timers wrap each operation and queue/search call; `hub report latency` (read-only) prints p50/p95 on the 125-case baseline fixture for PNFR-06. No threshold is enforced. | PNFR-06, OPD-14 |
| BEH-OBS-05 | A KPI is "computed" when a `metric_value` row exists for each R1 KPI in the registry; `hub report kpi-coverage` lists KPIs lacking values (expected: most event-derived KPIs on the shipped baseline, with reason). | PNFR-14, PNFR-16 |
| BEH-OBS-06 | Tripwires `model_calls_total`, `egress_attempts_total`, `zone_h_service_actor_accepted` are exported at every run end; any non-zero value fails the release gate G5/G8. | PNFR-18, FR-GATE-03 |
| BEH-OBS-07 | Log and metric retention is hold-all until a retention policy exists (OPD-09); rotation by file size is allowed only if rotated files are kept (no deletion). | PNFR-10 |
| BEH-OBS-08 | Alerts are manual in R1 (no platform): `hub report health` prints red/amber items (audit verify failing, projection mismatch, queue depth growth, missed runs, db_busy bursts, tripwires non-zero). | ADR-016 |

### OBS-6 Dashboards/reports (documentation level)
`hub report health`, `hub report latency`, `hub report kpi-coverage`, `hub report queues`. All output carries the label 'synthetic, unvalidated' while `data_origin = synthetic`. A visual dashboard is not specified (no platform exists; Stage 31 owns SLO/SLA design).

### OBS-7 Acceptance criteria (observability)
| ID | Given | When | Then | Implements | Kind |
|---|---|---|---|---|---|
| AC-OBS-01 | any API call | it completes | one log line with correlation_id, op_id, outcome, duration_ms; the same correlation id appears in the audit record (for writes) and in any error envelope | PNFR-14, BEH-OBS-01 | positive |
| AC-OBS-02 | 10 job runs | `hub report health` runs | every run is listed; a seeded killed run appears as abandoned | FR-RUN-02, PNFR-14 | positive |
| AC-OBS-03 | schedule enabled, one expected run absent | the detector runs | `run_missed_total` = 1 and the run is listed | PNFR-14 | edge |
| AC-OBS-04 | logs produced by the full acceptance suite (including failed logins and injection fixtures) | scanned for passwords, tokens, hashes, raw notes text | 0 matches | PNFR-08, BEH-SEC-07 | negative |
| AC-OBS-05 | the 125-case baseline fixture | `hub report latency` runs 200 calls per key operation | p50 and p95 per operation are printed; no pass/fail | PNFR-06 | positive |
| AC-OBS-06 | the acceptance suite | finishes | `model_calls_total = 0`, `egress_attempts_total = 0`, `zone_h_service_actor_accepted = 0` | PNFR-18, FR-GATE-03 | negative |
| AC-OBS-07 | start-up | selfcheck runs | prints Python, SQLite, FTS5 status, config hash, gate status | OD-S12-12 | positive |
| AC-OBS-08 | the KPI registry on the shipped baseline | kpi-coverage runs | lists each R1 KPI with a value or a stated reason (e.g. `no_completed_cycles`) | PNFR-14, PNFR-16 | positive |
| AC-OBS-09 | a duplicate replay of 100 items | metrics are read | `intake_noop_duplicate_total` +100 and queue depths unchanged | FR-INT-02, PNFR-11 | positive |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-OBS-1 Latency percentiles computed from stored samples are adequate at 125 cases.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-OBS-1 Log retention and monitoring platform (none exists; Stage 31).
- U-12-OBS-2 Site time zone for the 06:00 completion metric.

## Unresolved Issues
- No alerting channel exists; manual reports only in R1.

## Residual Risks
- Self-measured availability (PNFR-01) is unprovable without HA or an external prober.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
