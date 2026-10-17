---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "baseline-test-results.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["tests/*.py", "scripts/verify.sh", "scripts/smoke.py", "scripts/offline_inventory.py", "scripts/rehearse_local.py", "scripts/verify_preloaded.py", "app/workshop_check.py", "docs/07-repo-assessment/evidence/test-logs/R1..R7", "docs/07-repo-assessment/evidence/analysis/coverage_trace_unittest.json", "docs/07-repo-assessment/evidence/analysis/mutation_probe.log", "docs/00-preflight/discovery/test-overview.md", "docs/00-preflight/operating-contract/repository-write-boundaries.md"]
supersedes: "none"
---
## Summary

All existing tests were executed **only inside disposable full copies of the repository** outside the working tree (sandbox `$HOME/fde_sbx/stage7/`, outside `$HOME/mnt/Case-Execution`), per OD-03a and Stage 0B WB-10. Result: **15 of 15 `unittest` tests pass, 0 failures, 0 errors, 0 skips; `scripts/verify.sh` passes end to end; the read-only inventory scripts report `ready: true`.** The suite is deterministic (identical output and identical post-run DB hash on two fresh copies) but it is **not isolated** (it rewrites `data/legacy.sqlite3`, and the resulting DB depends on module load order) and it is **weak as a behaviour baseline**: statement coverage by the suite is 47.9 % (stdlib `trace`), and in a 15-mutant probe the suite caught 1 mutant (M4) and let 14 survive. The failing/flaky-test count is nil; the findings are about test design, not red tests. No code, threshold or dataset was modified in the real repository.

## Findings

### Execution environment (reproducibility record)

| Item | Value | Class |
|---|---|---|
| Date/time of runs | 2026-10-17 ~18:33-18:50 UTC (device clock) | [Verified Fact] |
| Host | Linux 6.8.0-138-generic (Cowork VM), single user | [Verified Fact] |
| Python | 3.10.12 (CI/Dockerfile use 3.12 - **not exercised**, see TR-12) | [Verified Fact] |
| Java | OpenJDK 11.0.32.1 (source-launcher `java File.java`; no `javac` on PATH) | [Verified Fact] |
| Node | v22.23.2 | [Verified Fact] |
| Third-party Python packages | none used; `coverage`, `pytest`, linters not installed | [Verified Fact] |
| Env | `PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1`; `LEGACY_DB`, `HOST`, `PORT` unset unless stated | [Verified Fact] |
| Network | servers bound to `127.0.0.1` on ephemeral ports; no outbound calls issued by the suite; Docker not installed (no Compose run) | [Verified Fact] |
| Source commit | `3b9876a8d7c4ec7563ef7ecfeb16057195cf1d7d` (HEAD at stage start; source files unchanged since `a6eb4e8`, tag `baseline-as-found`) | [Verified Fact] |
| Sandbox | `$HOME/fde_sbx/stage7/repo` (pristine copy, `cp -a` of the repo incl. `data/`); every run starts from a **fresh copy** `t1..t7` | [Verified Fact] |
| Pre-run DB hashes (copy == real == backup) | `legacy.sqlite3` `c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa`; `enterprise_legacy.sqlite3` `210f4bafd858155f79dd4654fd3c9f4817c6e3d9325bc320bea4a8945fdb4c0b`; `lake/bundled/finance` `c0eff33d...a1843ba`; `lake/bundled/reference` `47fd1a1f...b034`; `lake/tiny/finance` `17bfd3e5...9d5`; `lake/tiny/reference` `47fd1a1f...b034` | [Verified Fact] |
| Real-repo integrity before run | `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` -> no output, rc 0 (1,512 entries); `git status --porcelain` empty | [Verified Fact] |
| Real-repo integrity after run | see "Post-run integrity" below | [Verified Fact] |
| Runner | `evidence/scripts/run_tests.sh` (exact commands); logs in `evidence/test-logs/` | [Verified Fact] |

### Results table

| ID | Command (cwd = fresh sandbox copy) | Result | Evidence | Class |
|---|---|---|---|---|
| TR-01 | `python3 -m unittest discover -s tests -v` (fresh copy) | `Ran 15 tests in 0.617s` `OK`, exit 0 | `test-logs/R1_unittest_fresh.log` | [Verified Fact] |
| TR-02 | same, re-run on the already-mutated copy | `Ran 15 tests in 0.628s` `OK`; DB hash changed again (`750336f3...` -> `efc82d76...`) | `R2_unittest_rerun_mutated.log` | [Verified Fact] |
| TR-03 | same, on a second fresh copy | `Ran 15 tests in 0.605s` `OK`; post-run DB hash identical to TR-01 (`750336f3...459c`) -> deterministic from a fresh state | `R3_unittest_fresh_again.log` | [Verified Fact] |
| TR-04 | each of the 7 test modules alone on fresh copies | all `OK` (counts 1,2,2,1,2,3,4 = 15); **no DB mutation** in isolation | `R4_per_module_isolation.log` | [Verified Fact] |
| TR-05 | `unittest tests.test_workflow tests.test_source_gateway tests.test_enterprise tests.test_domain` (alternate order) | 10 tests `OK`; post-run DB has **180 cases** (vs 125 in default order) | `R5_alt_order.log` | [Verified Fact] |
| TR-06 | `sh scripts/verify.sh` (workshop_check -> unittest -> smoke) | workshop_check `ok: true`; 15 tests OK; smoke `{"api":"pass","database":"pass"}`; total 1.0 s; exit 0 | `R6_verify_sh.log` | [Verified Fact] |
| TR-07 | `python3 scripts/offline_inventory.py`, `verify_preloaded.py`, `rehearse_local.py` (pristine copy) | `ready: true`, no problems, integrity ok, 0 FK errors on 6 DBs; tiny/bundled manifests match counts and SHA-256; 1 `documents` file, 421 `archive_documents` files; `rehearse_local` `offline_ready: true` | `R7_readonly_scripts.log` | [Verified Fact] |
| TR-08 | `python3 -m compileall -q app services legacy_batch tests scripts ops`; `python3 -W error -c "import app.server, app.partner_feeds"` | compile OK; no warnings on import | static-analysis run | [Verified Fact] |
| TR-09 | CI workflow `.github/workflows/verify.yml` (unittest, `generate --count 6000 --seed 4326 --reset`, `baseline`) | **Not executed here** (no GitHub runner; Python 3.12). Equivalent commands were run in the sandbox: generation + baseline reproduced (`evidence/golden/batch_golden_run1.json` key `baseline_6000_seed4326`: records 6000, open 4251, urgent 159, mean 4403.0, hours/case 0.601) | golden | [Verified Fact] (commands) / [Unknown] (CI ever ran, U-20) |
| TR-10 | Java: `java legacy_java/ReconcileLegacy.java <csv>` (no tests exist) | runs; see `baseline-behaviour.md` BB-08 | golden `java_*` | [Verified Fact] |
| TR-11 | Node: `node legacy_js/legacy_policy.js` (no tests exist) | runs from repo root (rc 0); fails (`ENOENT contracts/...`, rc 1) from another cwd | golden `node_*` | [Verified Fact] |
| TR-12 | Python 3.12 / Docker / Compose parity | **Not tested** - only 3.10.12 and no Docker on device | - | [Unknown] |

Summary count: **15 passed / 0 failed / 0 errors / 0 skipped; flaky: none observed in 3 full runs + 7 isolated + 1 reordered run.**

### Test-suite quality findings (measured)

| ID | Finding | Class | Evidence | Impact | Confidence |
|---|---|---|---|---|---|
| TQ-01 | **Test isolation defect reproduced and characterised precisely.** `tests/test_enterprise.py` L2 and `tests/test_source_gateway.py` L4 import `app.store` at module-import time, fixing `store.DB` to `data/legacy.sqlite3` (`app/store.py` L4). `unittest discover` imports all modules before any `setUp` sets `LEGACY_DB`, so `test_domain` (180 cases) and `test_workflow` (125 cases) call `generate(..., reset=True)` against the **real** DB. In isolation (module loaded alone) the temp DB is honoured and nothing is mutated. Net effect of a default-order run: shipped DB (hash `c254649f...`) -> rewritten DB (hash `750336f3...`, same counts, because the last writer `test_workflow` uses the same `generate(125, 4100)` that produced the shipped DB). In another order the DB ends with **180 cases**. | [Verified Fact] | TR-01..TR-05 | Running the suite in the working tree silently changes the baseline; the outcome depends on order. | High |
| TQ-02 | `tests/test_source_gateway.py::test_idempotent_ingestion` inserts message `CHECK-batch_quality` into the real `gateway_inbox`; **the shipped DB already contains exactly this row** (`gateway_inbox` = 1 row) i.e. the shipped baseline carries test residue. | [Verified Fact] | `R1` pre-run counts (`gateway_inbox: 1`); `batch_golden` `gateway_inbox_after` 126 = 125 + 1 | Baseline counts for the gateway inbox include one non-business row. | High |
| TQ-03 | `scripts/verify.sh` runs `workshop_check` then the mutating unittest suite then smoke. The README, `PRELOADED_DATA.md` ("do not run any generator or reset ... no-generation quick start" lists `python -m unittest discover`) and `DATA_READINESS.md` all instruct running the suite while claiming data is preserved. | [Verified Fact] | `PRELOADED_DATA.md` quick start; TQ-01 | Documentation leads users to overwrite the preserved baseline. | High |
| TQ-04 | **Line coverage of the suite = 312 / 651 executable lines = 47.9 %** (stdlib `trace`, sandbox; `coverage.py` not installed). 0 % for `app/server.py`, `services/source_gateway/server.py`, `app/historical_estate.py`, `app/archived_documents.py`, `app/generate_documents.py`, `app/workshop_check.py`, all `scripts/*` (smoke covers server only via a subprocess, invisible to `trace`); 21.5 % for `app/partner_feeds.py` (reconcile never run by tests); 61.5 % gateway_bridge. JS, Java and SQL: no tests at all. Many "covered" lines are one-line multi-statement lines, so line coverage over-states branch coverage. | [Verified Fact] | `analysis/coverage_trace_unittest.json` | Most critical workflows are not executed by any test. | High (numbers) / Medium (as a quality proxy) |
| TQ-05 | **Mutation probe**: 15 deliberate single-line behaviour changes applied one at a time to sandbox copies; the existing suite stayed green for **14 of 15** (killed: M4 "CLOSED no longer archived"). Survivors include: urgent threshold 50000->1, removal of the `review` tier, `manual_review_required` always False, negative-quantity rejection removed, replay-duplicate detection removed, schema/key validation removed, night-shift threshold inverted, unknown-business-key acceptance, API manual-review flag hard-wired false, `/api/partners` pagination ignoring limit/offset, baseline `urgent_cases` hard-wired 0, JS tolerance 5%->50%, idempotent file import removed, gateway 503->200. | [Verified Fact] | `analysis/mutation_probe.log` | The suite cannot detect regressions in any decision rule except one; it cannot serve as the Stage 15/16 safety net. | High |
| TQ-06 | Tests assert counts, FK integrity and reproducibility of generated fixtures (characterising the **generator**, not the **workflows**). Assertions such as `assertIn(one['accepted'],(0,1))` and `assertIsInstance(list)` are non-discriminating. No HTTP, reconcile, bridge-pagination, file-import, Java, JS, SQL tests. | [Verified Fact] | `tests/*.py` | See `characterization-test-plan.md`. | High |
| TQ-07 | `tests/test_domain.py` and `test_workflow.py` hard-code counts (30 materials; 125 cases) that equal the generator formula, so they pass on any DB regenerated with the same parameters but also overwrite whatever DB is current. | [Verified Fact] | test sources | Coupled to generator internals. | High |
| TQ-08 | `scripts/offline_inventory.py` validates integrity/FK/manifest consistency but not expected business row counts; a 125-case or 6,000-case `legacy.sqlite3` both report `ready`. `app.workshop_check` runs DDL (`init()`), so it is not strictly read-only. | [Verified Fact] | scripts source; TR-07 | "Ready" is not "equal to baseline". | High |
| TQ-09 | Suite run time is 0.6 s; whole `verify.sh` 1.0 s - cheap enough to run on every change once isolated. | [Verified Fact] | R1, R6 | Positive. | High |

### Post-run integrity (real repository)

Executed after all sandbox work: `cd gxp-quality-hub-legacy && sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` and `git status --porcelain`. Results are recorded in `repo-assessment.md` section "Integrity attestation" (written last). [Verified Fact]

## Evidence References

`docs/07-repo-assessment/evidence/test-logs/R1_unittest_fresh.log` ... `R7_readonly_scripts.log`; `evidence/scripts/run_tests.sh`; `evidence/analysis/coverage_trace_unittest.json`; `evidence/scripts/coverage_trace.py`; `evidence/analysis/mutation_probe.log`; `evidence/scripts/mutation_probe.sh`; `evidence/SHA256SUMS-evidence.txt`.

## Assumptions

- A-07-01: The sandbox copy (`cp -a`) is behaviourally identical to the working tree, including SQLite file content (verified by equal SHA-256 pre-run). Confirm: not required.
- A-07-02: Python 3.10.12 results are representative of the 3.12 runtime used by CI/Docker. Owner to confirm: Engagement lead (Dinesh Naik), Stage 14/15 (run suite on 3.12 in a BUILD sandbox).

## Unknowns

- U-07-01: Whether CI has ever run and passed (carried U-20). Resolution: first push (OD-05) at orchestrator level.
- U-07-02: Behaviour under Python 3.12 / Docker / Compose (E2 tier unavailable). Resolution: Stage 14 environment plan.

## Unresolved Issues

- TQ-01..TQ-03: isolation defect and misleading docs are **findings routed to remediation** (technical-debt-register TD-01); not fixed here by design.
- Coverage numbers are line-based via `trace`; a branch-coverage tool is needed (route: Stage 14 tooling).

## Residual Risks

- R-01 (carried): any future run in the working tree re-creates the TQ-01 hazard.
- R-07-01: because only 1 of 15 probed regressions is detected by the existing suite, a green suite must **never** be used as evidence of preserved behaviour in Stage 15/16 - use the golden baseline (`baseline-behaviour.md`).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial test execution record (sandbox, Python 3.10.12). |
