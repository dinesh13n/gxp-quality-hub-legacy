---
stage: "21 — Enterprise Integration"
artifact: "failure-semantics.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/adapters/gateway_client.py", "hub/adapters/legacy_sqlite.py", "hub/intake/service.py, validate.py, reasons.py, replay.py", "hub/runs/sources.py, jobs.py", "docs/12-specs/error-handling-spec.md", "tests/hub/test_tst_hub_stg21_integration.py S01-S07", "tests/hub/test_tst_int_01_08_core.py, test_tst_int_09_16_validation.py, test_tst_int_17_29_match_untrusted_sources.py", "tests/hub/test_inc06_supplementary.py S05-S09", "tests/hub/test_tst_run_01_15_runs.py TST-RUN-07/13/14", "tests/hub/test_tst_co_04_readonly_adapters.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Semantics below are what the built code does (Verified Fact by test), not an approved design change. Stage 21 changed no behaviour.**

## Summary
Every integration has defined failure semantics and each failure mode is covered by at least one test (FS matrix below). The governing rules: (1) a **source failure is a run failure, never data** - no item is fabricated (RUN_FAILED + audit, 0 rows); (2) **only idempotent reads are retried** (GET; bounded retries with exponential back-off), and a run is one transaction, so a partial run leaves nothing; (3) an **item problem is a reason code, never an exception** - malformed, unknown, duplicate or conflicting items are stored verbatim and classified (quarantine / exception / NOOP), nothing is dropped; (4) **legacy sources fail closed** on drift or hash mismatch and are never written.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### FS-1 Failure-mode matrix
| ID | Integration | Failure mode | Behaviour | Retry? | Idempotency / data effect | Test evidence | Tag |
|---|---|---|---|---|---|---|---|
| FS-NET-01 | INT-06 | connection refused (source down) | retried `retries` times, back-off 0.5 x 2^i, then E-INT-SOURCE-UNREACHABLE; CLI writes RUN_FAILED + audit `INTAKE_RUN_FAILED` | yes (GET) | 0 raw rows, 0 outcomes, checkpoint unchanged | TST-INT-26 | [Verified Fact] |
| FS-NET-02 | INT-06 | timeout (accepts, never answers) | each attempt ends at `timeout` (5 s shipped), bounded retries, then E-INT-SOURCE-UNREACHABLE (`last_error` TimeoutError) | yes | 0 rows; no checkpoint | STG21 S04 (new) | [Verified Fact] |
| FS-NET-03 | INT-06 | 503 / 429 (stub bodies) | retried with back-off; success on a later attempt continues normally | yes | none until success | STG21 S03 (stub bodies), INC06 S09 | [Verified Fact] |
| FS-NET-04 | INT-06 | other 4xx (e.g. 400 bad pagination, 404) | not retried; run error | no | 0 rows | S03, INC06 S09 | [Verified Fact] |
| FS-NET-05 | INT-06 | 200 with unexpected shape (stub `schema` mode), invalid JSON | treated as unusable response: retried (bounded), then run error | yes (see AF-02) | 0 rows | S03, INC06 S09 | [Verified Fact] |
| FS-NET-06 | INT-06 | redirect, oversized body (> 5 MiB), non-loopback / non-http URL | redirect / size -> run error; URL -> E-INT-URL-SCHEME-REFUSED before any connection | no (URL) | 0 rows | TST-INT-25, INC06 S09 | [Verified Fact] |
| FS-ITEM-01 | INT-03..07 | malformed item (invalid JSON, missing envelope / payload field, unknown kind / unit / currency, bad identifier, blank / negative amount, unsupported revision) | stored verbatim; reason code(s); one primary reason and queue | n/a | counted; never dropped | TST-INT-09..16 (re-run ok), TST-INT-21, TST-INT-27 | [Verified Fact] |
| FS-ITEM-02 | INT-03..07 | contract `source-contract-v1` fails | `record_only`: recorded on the outcome only; `enforce` (holder needed): CONTRACT_VIOLATION quarantine | n/a | see data-contracts DC-S21-2 | S01, TST-INT-12/13/14 | [Verified Fact] |
| FS-DUP-01 | INT-03..07 | exact re-delivery (same natural key + content) | new raw row, outcome NOOP_DUPLICATE, not counted in totals | n/a | replay-safe | TST-INT-04/05, S02 stale re-pull (125 -> NOOP) | [Verified Fact] |
| FS-DUP-02 | INT-03..07 | backfill re-run | `idempotent_backfill` skips (source, source_key, content hash) already stored | n/a | 0 new rows | TST-INT-29, S07 | [Verified Fact] |
| FS-DUP-03 | INT-03..07 | corrected replay (same natural key, different content) | REVISED_CONFLICT quarantine; human resolution with reason; both versions kept | n/a | no case state touched | TST-INT-07/08 | [Verified Fact] |
| FS-STALE-01 | INT-06 | stale re-pull from an old offset | items NOOP_DUPLICATE; totals and queue snapshot unchanged | n/a | none | S02 | [Verified Fact] |
| FS-STALE-02 | INC-07 jobs over INT-03..05 | late delivery with `source_ts` before the job checkpoint (RTD-61) | not seen by a resumed job; picked up by the idempotent catch-up ingest | n/a | delayed, not lost, if catch-up runs | S07 (new) | [Verified Fact] |
| FS-STALE-03 | INT-01..05 | legacy DB changed / schema drift | fail closed (E-FX-HASH pinned, E-CO-LEGACY-SCHEMA-DRIFT unpinned); nothing read | no | none | TST-CO-04 e | [Verified Fact] |
| FS-DB-01 | INT-01..05 | write attempt through the adapter | refused (E-CO-LEGACY-WRITE-REFUSED); files byte-identical | no | none | TST-CO-04 b/c, S06 | [Verified Fact] |
| FS-RUN-01 | all intake | crash inside a run | one transaction per run: nothing of the run persists; rerun is clean | operator rerun (idempotent) | none | INC06 S06 / S07 | [Verified Fact] |
| FS-RUN-02 | INC-07 jobs | crash between batch commit and checkpoint | next run marks RUN_ABANDONED, resumes, final rows equal an uninterrupted run | job rerun | no duplicates | TST-RUN-07 | [Verified Fact] |
| FS-RUN-03 | INC-07 jobs | corrupt checkpoint / unreachable source | run refused / finished with error, no items | no | none | TST-RUN-13/14 | [Verified Fact] |
| FS-FILE-01 | INT-07 | missing CSV / outside sandbox | OSError / sandbox guard refusal: run error | no | none | sandbox guard (TST-CO-06) | [Verified Fact] |
| FS-API | INT-11 | request errors | error envelope; request-level errors write nothing | client decides | none | INC06 S07, I8 tests | [Verified Fact] |

### FS-2 Non-idempotent operations
[Verified Fact] No integration operation of the hub is retried unless it is a read: the gateway client issues only GET (S03 static check); ingest, binding changes, conflict resolutions and job runs are never retried automatically - a failed run is re-run by an operator or the next job, and re-running is safe by construction (FS-DUP-01/02, FS-RUN-01/02).

### FS-3 Gaps (non-blocking)
| ID | Gap | Risk | Owner | Due |
|---|---|---|---|---|
| FG-01 | Shape errors retried (AF-02) | Low | Engagement lead (Dinesh Naik) DQ-S21-03 | Stage 28 |
| FG-02 | Late items need a catch-up run (FS-STALE-02); no automatic catch-up while the scheduler is OFF | Medium | Engagement lead (Dinesh Naik) DQ-S21-06 | Stage 28 |
| FG-03 | No circuit breaker / back-pressure across runs (each run retries independently) | Low (single loopback source) | Stage 28 resilience | Stage 28 |

## Evidence References
- `evidence/test-runs-laptop.json` (STG21 7/7, E21 1/1, TST-INT-09..16 8/8, TST-CO-04/05 9/9); other cited tests ran green in the Stage 20 full regression (orchestrator, 419 / 419) and run again before merge.

## Assumptions
- A-21-FS-1 [Assumption] Treating a source outage as a failed run (no partial data) is the desired semantics for GxP evidence integrity (FR-INT / AC-INT-26). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-21-FS-1 Retry budget, timeout and freshness targets for real sources (Stage 28 / 31).

## Unresolved Issues
- FG-01..FG-03.

## Residual Risks
- RR-21-FS-1 Sustained source outage is visible only as failed runs; alerting is a Stage 31 item (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
