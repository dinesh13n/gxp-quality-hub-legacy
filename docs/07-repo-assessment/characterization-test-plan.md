---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "characterization-test-plan.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/07-repo-assessment/baseline-behaviour.md", "docs/07-repo-assessment/baseline-test-results.md", "docs/07-repo-assessment/critical-workflow-inventory.md", "docs/07-repo-assessment/evidence/golden/*.json", "docs/07-repo-assessment/evidence/scripts/*", "docs/07-repo-assessment/evidence/analysis/golden_mutation_replay_*.json", "docs/00-preflight/operating-contract/repository-write-boundaries.md", "tests/*.py"]
supersedes: "none"
---
## Summary

A plan, not an implementation (no source or tests were added to the repository). It converts the golden captures made in this stage into an **executable characterisation suite** to be built before any refactoring (Stage 14 plans, Stage 15 builds on a `stage-NN-*` branch, Stage 16 compares). Every critical workflow in `critical-workflow-inventory.md` has at least one planned test (CT-01..CT-16). Design principles: **hermetic** (each test or test class works on a fresh copy of the dataset in a temp dir - never the repo `data/`), **golden-file driven** (assertions compare to the committed goldens after documented normalisation), **mutation-validated** (the suite must kill the 15 reference mutants M1-M15, which the existing suite does not), **no behaviour changes** (tests pin current behaviour, including defects).

Proof-of-concept already done in this stage (sandbox only): the three capture scripts, run on a pristine copy, regenerate the goldens byte-for-byte on two consecutive runs and kill 14/14 replayed mutants (13 via API/batch goldens, M9 via the library golden). They are the prototype of CT-01..CT-16.

## Findings

### Harness requirements (CT-H)

| ID | Requirement | Reason |
|---|---|---|
| CT-H1 | Test fixture copies the baseline dataset (hash-verified against `c254649f...d70aa`) into a temp directory per test class and sets `LEGACY_DB` **before any import of `app.store`** (or reloads it), and for the 5 writers that ignore `LEGACY_DB` (`enterprise_legacy.py`, `shift_reconciliation.py`, `archived_documents.py`, `generate_documents.py`, `historical_fixture.py` default target) passes explicit paths or runs in a full repo copy | TQ-01, WB-F1 |
| CT-H2 | Servers started on `127.0.0.1` with ephemeral ports (`PORT`/`SOURCE_PORT`), terminated in `tearDown` | ENV-R1 |
| CT-H3 | Normalisation: drop ports, absolute sandbox paths, wall-clock fields (`received_at`, `last_sync`); keep all data-derived fields | A-07-05 |
| CT-H4 | Golden update is a deliberate, reviewed action (`--update-golden` flag + diff in PR); goldens versioned in `tests/characterization/golden/` | prevents "fixing the test" drift |
| CT-H5 | Pin interpreter versions: run on 3.10 and 3.12; JDK 11+; Node >= 18 | TR-12 |
| CT-H6 | Add a mutation gate: run M1-M15 (`evidence/scripts/mutation_probe.sh`) in CI nightly; suite must kill all | TQ-05 |
| CT-H7 | Tooling in BUILD stage: branch coverage (`coverage.py`), but code-coverage % is secondary to mutation kill rate | TQ-04 |

### Planned tests

Priority P1 = must exist before any change to the workflow; P2 = before Stage 16; P3 = nice to have.

| ID | Workflow | What it pins | Golden source | Type | Pri | Currently covered? | Notes |
|---|---|---|---|---|---|---|---|
| CT-01 | CW-01 | `priority()` truth table, 120 combinations (statuses x severities x {0,1,50000,50000.01,99999,-1}) | `batch_golden.priority_truth_table` | unit | P1 | partially (2 asserts) | pins the 50,000 boundary, which no shipped case exercises |
| CT-02 | CW-01 | priority of all 125 shipped cases via the API (id, priority) and distribution archive 36 / queue 70 / review 17 / urgent 2 | `api_golden.api_all_cases_priority` | API | P1 | no | |
| CT-03 | CW-01/02 | `manual_review_required()` truth table (20) and flag in `/api/cases/<id>` for CRITICAL, CLOSED, ESCALATED, REOPENED, HIGH cases | `manual_review_truth_table`, `api_golden.api` | unit + API | P1 | no | CLOSED+HIGH is True (preserve until RC-3 decided) |
| CT-04 | CW-02/10/13 | all HTTP responses of BB-02: status, content-type, body (or sha256), pagination clamps, 400/404/501 behaviour, advertised route list, static incident | `api_golden.api` (39 requests) | API | P1 | no | includes `/api/domain/*`, `/api/partners/*` |
| CT-05 | CW-03/11 | `app.baseline` and `app.operational_report` outputs on shipped DB (and, as a second dataset, 6,000/4326) | `batch_golden.app.baseline`, `operational_report*`, `baseline_6000_seed4326` | CLI | P1 | no (asserts `==125`, `>0`) | |
| CT-06 | CW-04 | source gateway: all 16 responses incl. failure modes, `0.9` schema cadence, message_id derivation, paging | `api_golden.gateway` | API | P1 | no | |
| CT-07 | CW-04 | bridge: ingest sequence, checkpoint, idempotency, invalid handling (unknown key, missing fields, non-dict, SQL-meta key), unreachable source | `batch_golden.gateway_bridge_sequence`, `lib_golden` | integration | P1 | partially (valid + `bad`) | needs a local gateway process (CT-H2) |
| CT-08 | CW-05 | reconcile: 4 outcome rules, 1000-row cap, ordering, 10-run sequence, final status/error-reason distribution, `batch_runs` untouched | `batch_golden.partner_reconcile_sequence`, `partner_status_after_all`, `partner_error_reasons` | integration | P1 | no | mutants M5-M7 |
| CT-09 | CW-06 | file import: first/second import, blank-amount storage, digest key | `batch_golden.historical_estate_*`, `vendor_rows_after` | integration | P2 | no | |
| CT-10 | CW-07 | night shift: `processed`/`flagged_count`/`by_tenant` for limits 50, 100, 500, 12500; 118-distinct-object finding | `batch_golden.shift_reconciliation`, `shift_distinct_objects_in_first_500_joined_rows` | integration | P1 | partially | needs explicit DB path (hard-coded) |
| CT-11 | CW-08 | Java totals/skips on tiny + bundled CSV, usage rc 2; cross-check against `decimal` reference | `batch_golden.java_*`, `csv_reference_*` | cross-language | P1 | no | requires JDK in CI |
| CT-12 | CW-08 | SQL report 1 rows and the 742,956.61 vs 622,826.44 discrepancy; report 2 rows | `batch_golden.sql_report_*` | SQL | P1 | no | |
| CT-13 | CW-09 | JS threshold table (32 pairs), tolerance cases (26250/26250.01/negative/null/"abc"), cwd-dependence | `batch_golden.js_policy_table`, `node_*` | node | P1 | no | |
| CT-14 | CW-12 | regeneration equivalence: `generate 125/4100`, `enterprise_legacy`, `historical_fixture tiny`, `archived_documents`, `generate_documents` equal shipped (table hashes / bytes); partner feeds are NOT reproducible - document as expected-difference | `batch_golden.*_regen_*` | provisioning | P2 | partially (counts only) | |
| CT-15 | CW-12 | readiness scripts: `workshop_check`, `offline_inventory`, `rehearse_local` outputs on pristine DB and failure on empty DB | `batch_golden.workshop_check*`, `R7_readonly_scripts.log` | CLI | P2 | no | |
| CT-16 | CW-14 | boundary/absence: POST/PUT/DELETE -> 501 on all routes; no module other than generators executes `INSERT/UPDATE/DELETE` on `cases`; no `batch_disposition` handler; AST/grep guard | `api_golden.api['METHOD *']`, source scan | static + API | P1 | no | guards HAR-12/STOP-07 |
| CT-17 | cross | concurrency smoke: API + bridge + reconcile concurrently on one SQLite file - characterise lock timeouts (`busy_timeout` 15 s) | none yet (Unknown U-07-05) | non-functional | P3 | no | capture needed before parallelising |
| CT-18 | cross | docker/compose smoke (E2 tier) | none (Docker unavailable) | environment | P3 | no | after HAR-05 |

### Coverage assurance

* Replay results (sandbox): golden detects M1-M8, M10, M12-M15 via API/batch captures; M9 only via library golden (`golden_mutation_replay_summary.txt`). M11 (partners pagination) is covered by the API golden's `/api/partners/partner_feeds?limit=2&offset=8566` request by construction but was not part of the replay set - include in CT-H6 run.
* Exit criterion for "characterisation complete": all CT P1 tests green on the untouched baseline, 15/15 reference mutants killed, golden determinism verified twice.

## Evidence References

Scripts `evidence/scripts/capture_api.py`, `capture_batch.py`, `capture_lib.py`, `golden_replay.py`, `mutation_probe.sh`; goldens `evidence/golden/*.json`; results in `baseline-test-results.md` TQ-04/TQ-05.

## Assumptions

- A-07-08: Stage 14/15 will implement this plan on a BUILD branch (write rights to `tests/` per WB-04). Confirm: orchestrator.
- A-07-03 (dataset choice, OD-02) governs the goldens.

## Unknowns

- U-07-05 concurrency behaviour; U-07-04 Docker/3.12.
- Whether the client wants characterisation on the 6,000-case dataset as well (README/CI). Owner: Engagement lead (Dinesh Naik), Stage 14.

## Unresolved Issues

- CT-H1 depends on how the store resolves `LEGACY_DB` (import-time). Whether to adapt the harness (subprocess per test) or change the code (a refactor) is a Stage 14/15 design decision - not made here.

## Residual Risks

- R-07-05: Goldens depend on the shipped DB; any silent change to `data/` (git-ignored, backup-only) invalidates them. Mitigation: hash gate CT-H1 and the backup `SHA256SUMS.txt`.
- R-07-06: Captures were made on Python 3.10.12/JDK 11; minor output differences on other runtimes (e.g. dict ordering is stable, float repr stable) are not expected but unverified.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial plan with prototype evidence. |
