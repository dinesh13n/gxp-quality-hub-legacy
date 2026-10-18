---
stage: "12 — Spec-Driven Design"
artifact: "features/f06-scheduled-runs.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/partner_feeds.py (reconcile)", "app/gateway_bridge.py", "legacy_batch/shift_reconciliation.py", "docs/07-repo-assessment/baseline-behaviour.md (BB-05, BB-07)", "docs/10-architecture/adrs/ADR-010-run-orchestration-scheduling.md", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md (HAR-10)", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Feature spec for run orchestration (CAP-06): CLI/HTTP jobs, run records, checkpoints, no silent capacity cap, schedule disabled by default (HAR-10 question left open and specified in both states). 9 behaviours, 15 acceptance criteria for FR-RUN-01..03.

## Findings
### F06-1 Scope and traceability [Verified Fact: requirement text and legacy behaviour; Inference: design]
Feature **F06 Scheduled Runs & Run Records** = CAP-06, component C8, ADR-010 (idempotent CLI jobs + run records; trigger external and configurable; schedule held pending OPD-11), ADR-016 (run records as observability), data contract DC-15.

| Implements | FR-RUN-01, FR-RUN-02, FR-RUN-03 (all R1) |
|---|---|
| Also constrained by | FR-GATE-01/03, FR-INT-01/02, FR-MET-07, PNFR-02, PNFR-11, PNFR-14; BR-06, BR-12; RC-5; CT-07, CT-08, CT-10 |
| Open decisions | OD-S12-10 (is a deterministic scheduler an 'automated action' under HAR-10?) |
| Legacy evidence | `reconcile(limit=1000)` silently processes 1,000 rows per call and reports only totals (`app/partner_feeds.py` L60-63); night shift `--limit 500` covers only 118 distinct objects because of row multiplication (BB-07); `batch_runs` has 60 rows and is untouched by reconcile (CT-08); runs are manual CLIs, no scheduler exists |

### F06-2 Job catalogue (closed list in R1)
| Job | Purpose | Touches Zone H? |
|---|---|---|
| `intake_partner_feed`, `intake_gateway`, `intake_source_messages`, `intake_vendor_csv` | receive + validate + classify + match (F04) | never |
| `backfill_legacy` | idempotent read-only load of legacy rows into raw_intake (BEH-INT-10) | never |
| `rebuild_projection` / `verify_projection` | F01 projection checks | never |
| `verify_audit` | recompute hash chain, compare anchor (F09) | never |
| `metrics_snapshot` | compute KPI rows (F07) | never |
Jobs have no import path to GateService; a job that tries a Zone H action is refused (E-GATE-NOT-AUTHORISED) and the run is marked failed.

### F06-3 Behaviours
| ID | Behaviour (binding once approved) | Implements |
|---|---|---|
| BEH-RUN-01 | **Invocation.** `hub run <job> [--trigger manual|scheduled] [--batch-size N] [--until-empty]`; HTTP `POST /api/v2/runs` is the manual equivalent. Manual trigger requires an authenticated principal with role quality_lead, compliance or integration (E-AUTH-FORBIDDEN otherwise). | FR-RUN-01, FR-SEC-01 |
| BEH-RUN-02 | **Schedule disabled by default.** The schedule is a documented OS-level entry outside the repository calling `hub run <job> --trigger scheduled`. A `scheduled` trigger is accepted only while `schedule.enabled = true`; enabling or disabling is Zone H ZH-09 (audited event with authority_ref). While false: E-RUN-SCHEDULE-DISABLED, a run record with `outcome = refused` is still written. The question whether this is an 'automated action' under HAR-10 is OD-S12-10; both states (disabled-manual-only; enabled-non-Zone-H-jobs-only) are specified and tested. | FR-RUN-01, FR-GATE-01 |
| BEH-RUN-03 | **Run record** (SCH-RUN-RECORD). Append-only events RUN_STARTED (written before any work), RUN_CHECKPOINT, RUN_FINISHED or RUN_FAILED. Final fields: `run_id`, `job`, `trigger`, `triggered_by`, `started_at`, `ended_at`, `inputs_seen`, `outcomes_by_type` (counts per reason/outcome), `errors[]`, `limit_reached` (bool), `batch_size`, `backlog_remaining`, `checkpoint`, `config_version`, `code_version`. A run that dies leaves RUN_STARTED with a stale heartbeat; the next invocation writes RUN_ABANDONED for it. | FR-RUN-02, PNFR-14 |
| BEH-RUN-04 | **Totals reconcile.** `sum(outcomes_by_type)` equals the count of `intake_outcome` rows carrying that `run_id`; a mismatch fails the run (E-RUN-TOTALS-MISMATCH) and is reported. | FR-RUN-02 |
| BEH-RUN-05 | **No silent cap.** A capacity limit (`batch_size`, default configured explicitly, no hidden constant) may stop a run early; then `limit_reached = true`, `backlog_remaining` = exact count of unprocessed eligible items, and the checkpoint stores the ordering key (`receipt_time, raw_id`) of the last processed item. The next run resumes from the checkpoint. With `--until-empty` the job loops until `backlog_remaining = 0`. | FR-RUN-03 |
| BEH-RUN-06 | **Single flight.** One active run per job: a lock row with heartbeat (default stale after 15 min, configurable). A second start returns E-RUN-ALREADY-RUNNING and writes a refused run record. | FR-RUN-02, PNFR-11 |
| BEH-RUN-07 | **Idempotent resume.** Killing a run at any point and re-running yields the same final store as an uninterrupted run (no duplicate effects), because intake outcomes are keyed by (`raw_id`, stage) and skipped when present. | FR-RUN-03, PNFR-11 |
| BEH-RUN-08 | **Missing-run detector.** When `schedule.enabled = true` the detector lists expected-but-absent runs (expected times from configuration); with schedule disabled it reports 'schedule disabled' instead of failures. | FR-RUN-01, PNFR-14 |
| BEH-RUN-09 | **Timeliness record.** Each run records `ended_at`; the report 'finished before 06:00 local business time' uses configuration `site.timezone` (Unknown; default UTC labelled as such) so PNFR-02 is measurable once a schedule exists. | PNFR-02 |

### F06-4 Error cases
E-RUN-SCHEDULE-DISABLED, E-RUN-ALREADY-RUNNING, E-RUN-TOTALS-MISMATCH, E-RUN-UNKNOWN-JOB, E-RUN-CHECKPOINT-INVALID, E-RUN-ABANDONED, E-AUTH-FORBIDDEN, E-GATE-NOT-AUTHORISED (error-handling-spec.md).

### F06-5 Acceptance criteria
| ID | Given | When | Then | Implements | Kind |
|---|---|---|---|---|---|
| AC-RUN-01 | schedule enabled for a non-Zone-H job via ZH-09 | the scheduled trigger fires at the configured time in a test clock | a run starts, a run record exists with trigger = scheduled | FR-RUN-01 | positive |
| AC-RUN-02 | fresh install (schedule disabled) | a scheduled trigger is attempted | E-RUN-SCHEDULE-DISABLED and a run record with outcome refused | FR-RUN-01, BEH-RUN-02 | negative |
| AC-RUN-03 | schedule disabled | a service actor attempts ZH-09 | rejected E-GATE-NOT-AUTHORISED; schedule remains disabled | FR-RUN-01, FR-GATE-03 | negative |
| AC-RUN-04 | an authenticated reviewer (no manual-run role) | POST /runs | E-AUTH-FORBIDDEN; with role quality_lead the run starts | FR-RUN-01 | negative |
| AC-RUN-05 | 10 runs of mixed jobs | run records are listed | 100% of runs have a record with all fields of BEH-RUN-03 populated | FR-RUN-02, PNFR-14 | positive |
| AC-RUN-06 | a run processing 500 items | totals compared | outcomes_by_type sums to 500 and equals the count of outcome rows with that run_id | FR-RUN-02 | positive |
| AC-RUN-07 | a run killed mid-way (process terminated) | the next run is started | RUN_ABANDONED is written for the old run, the new run resumes, and the final store equals an uninterrupted run (row-set equality on outcomes) | FR-RUN-03, BEH-RUN-07 | edge |
| AC-RUN-08 | a seeded backlog of 2,500 eligible items and batch_size 1,000 | three consecutive runs | run 1 reports limit_reached = true, backlog_remaining = 1,500; run 2 backlog 500; run 3 backlog 0, limit_reached false; every item processed exactly once | FR-RUN-03 | positive |
| AC-RUN-09 | the same backlog with `--until-empty` | one run | backlog_remaining 0 at end, one record | FR-RUN-03 | positive |
| AC-RUN-10 | the source code and config | searched by a test | no hard-coded row cap (e.g. LIMIT 1000) exists outside configuration; the cap used is printed in the run record | FR-RUN-03 | negative |
| AC-RUN-11 | two simultaneous starts of the same job | started | exactly one runs; the other gets E-RUN-ALREADY-RUNNING | BEH-RUN-06 | negative |
| AC-RUN-12 | any job code path | an import-graph test runs | no job module can reach GateService write methods; a job forced to call it fails with E-GATE-NOT-AUTHORISED and the run is RUN_FAILED | FR-GATE-01 | negative |
| AC-RUN-13 | an unreachable source | the intake job runs | RUN_FINISHED with errors[] = SOURCE_UNREACHABLE, outcomes_by_type empty, no fabricated items | FR-RUN-02 | edge |
| AC-RUN-14 | a corrupt checkpoint value | the job starts | E-RUN-CHECKPOINT-INVALID, run refused, no data change | BEH-RUN-05 | negative |
| AC-RUN-15 | schedule enabled, expected 02:00 run absent | the missing-run detector runs | the absent run is listed; with schedule disabled it reports 'schedule disabled' | PNFR-14 | edge |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-F06-1 Default heartbeat staleness (15 min) and the role set for manual trigger are spec proposals.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-F06-1 Production schedule, time zone and business calendar (none in repo).
- U-12-F06-2 Real data volumes per run (OD-04).

## Unresolved Issues
- OD-S12-10 blocks enabling any schedule; manual-only operation is fully specified.

## Residual Risks
- PNFR-02 (06:00 completion) cannot be demonstrated until a schedule is approved.
- A hand-rolled lock on SQLite may misbehave across NFS/shared mounts (CT-17 concurrency is Unknown).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
