---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "test-execution-log.md"
version: "v0.2"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)"]
supersedes: "v0.1 (INC-01 only)"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
Every execution of legacy code in INC-01, all inside `~/fde_sbx/s15-inc01/<label>/` (outside the working tree), Python 3.10.12, SQLite 3.37.2, OpenJDK 11.0.32.1, Node v22.23.2. Backup checksum rc 0 after every session.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| # | Label | HEAD | Command (from `~/fde_sbx/s15-inc01`) | Result | Wall | Checksum rc | Tag |
|---|---|---|---|---|---|---|---|
| 0 | guard self-test | 2633062 (pre-commit tree) | runner with 6 unsafe `--sandbox-root` values | all refused rc 2, nothing executed | <1 s | 0 | [Verified Fact] |
| 1 | run-1 | 2633062 | `run_characterization.py --label run-1 --keep` | 127/134 (7 supplement checks without golden); shipped suite as-found | 50 s | 0 | [Verified Fact] |
| 2 | golden-supp (attempt 1) | 2633062 | background launch | terminated by device shell at call end; no output | — | 0 (checked after #3) | [Verified Fact] |
| 3 | golden-supp | 2633062 | `--update-golden supplement --reviewed-by ... --no-legacy-suite` | wrote `golden/inc01/supplement_golden_v1.json`; 127/134 | 36 s | 0 | [Verified Fact] |
| 4 | det-run-A | 0283660 | default | 134/134, shipped as-found, PASS | 35 s | 0 | [Verified Fact] |
| 5 | det-run-B | 0283660 | default | 134/134, PASS; digests == A | 34 s | 0 | [Verified Fact] |
| 6 | mut-1 | e1eb1d2 | `--mutation-gate --mutants M1,M2,M3,M4,M5 --no-legacy-suite` | 134/134; 5/5 KILLED | 144 s | 0 | [Verified Fact] |
| 7 | mut-2 | e1eb1d2 | `... --mutants M6,M7,M8,M9` | 4/4 KILLED | 106 s | 0 | [Verified Fact] |
| 8 | mut-3 | e1eb1d2 | `... --mutants M10,M11,M12,M13` | 4/4 KILLED | 106 s | 0 | [Verified Fact] |
| 9 | mut-4 | e1eb1d2 | `... --mutants M14,M15` | 2/2 KILLED | 89 s | 0 | [Verified Fact] |
| 10 | neg-fx | e1eb1d2 | `--fixture-source ~/fde_sbx/fx-tampered` (1 byte changed) | refused E-FX-HASH rc 2 | 15 s | 0 | [Verified Fact] |
| 11 | final-A | ed43a0a | default | 134/134, shipped 15 OK as-found, PASS | 36 s | 0 | [Verified Fact] |
| 12 | final-B | ed43a0a | default | 134/134, PASS; digests == A | 37 s | 0 | [Verified Fact] |
[Verified Fact] Harness code is identical at e1eb1d2 and ed43a0a (ed43a0a only added README.md), so the mutation-gate results apply to the final harness.

Totals: CT checks 134 (127 Stage 7-golden-backed + 7 INC-01 supplement), 16 CT executable, 2 NOT-RUN (CT-17/18); mutation gate 15/15; determinism: 6 runs, identical canonical digests.

### INC-02 runs (device Python 3.10.12 / SQLite 3.37.2; hub runs from `~/fde_sbx/s15-inc02/<label>/c_pristine`, INC-01 runs from `~/fde_sbx/s15-inc01`)
| # | Label | HEAD | Command (from repo root) | Result | Wall | Checksum rc | Tag |
|---|---|---|---|---|---|---|---|
| 13 | smoke | 945c8f1+wip | `python -m hub selfcheck / golden-compare / no-ai-check` in `~/fde_sbx/s15-inc02/smoke` | selfcheck ok; 9 UNAPPROVED exit 6; repo data dir refused exit 7 (not created); no-ai clean | <5 s | 0 | [Verified Fact] |
| 14 | dev1 | 2859091+wip | `tests/hub/run_hub_tests.py --label dev1` | 11/11 ok (CO-01/02); runner's verbose-output parser counted 0 -> replaced by `_driver.py` JSON recorder | 45 s | 0/0 | [Verified Fact] |
| 15 | dev2 | 23e8e9a+wip | `--label dev2` | 27 run, 3 tests in error (CO-04: re-snapshot PermissionError, "authorization denied" unmapped, wrong table in test) -> fixed | 73 s | 0/0 | [Verified Fact] |
| 16 | dev3 | 23e8e9a+fix | `--label dev3 -k TST_CO_04` | 6/6 ok | 44 s | 0/0 | [Verified Fact] |
| 17 | dev4 | 90e4710+wip | `--label dev4` | 46 run, 2 FAIL (CO-11 b: `torchaudio` not deny-listed - real gap; CO-12 e inner suite failed on the same test) -> deny-list fixed | 111 s | 0/0 | [Verified Fact] |
| 18 | dev5 | 90e4710+fix | `--label dev5` | 45 ok, 1 skipped, 0 fail | 109 s | 0/0 | [Verified Fact] |
| 19 | inc02-regress | 23b3250 | `tests/characterization/run_characterization.py --label inc02-regress` | 134/134 PASS, shipped 15 OK as-found, digests == INC-01 final-A | 34 s | 0 | [Verified Fact] |
| 20 | final-A | 23b3250 | `tests/hub/run_hub_tests.py --label final-A` | 46 run: 45 ok, 0 FAIL, 0 ERROR, 1 skipped | 112 s | 0/0 | [Verified Fact] |
| 21 | inc02-mut-1 | 23b3250 | `run_characterization.py --mutation-gate --mutants M1,M2,M3 --no-legacy-suite` | 3/3 KILLED | 66 s | 0 | [Verified Fact] |
| 22 | inc02-mut-2 | 23b3250 | `... --mutants M4,M5,M6,M7,M8,M9` | 6/6 KILLED | 136 s | 0 | [Verified Fact] |
| 23 | inc02-mut-3 | 23b3250 | `... --mutants M10,M11,M12,M13,M14,M15` | 6/6 KILLED | 137 s | 0 | [Verified Fact] |
| 24 | final-B | 23b3250 | `tests/hub/run_hub_tests.py --label final-B` | 46 run: 45 ok, 0 FAIL, 0 ERROR, 1 skipped (same as final-A) | 129 s | 0/0 | [Verified Fact] |

### INC-02 planned tests (Stage 13 IDs, increment-test-map) - final-A and final-B
| Test ID | AC | Test methods (tests/hub/) | Result | Class / note |
|---|---|---|---|---|
| TST-CO-01 | AC-CO-01 | `test_tst_co_01_golden_compare.py` a-e (5) | PASS | A |
| TST-CO-02 | AC-CO-02 | `test_tst_co_02_unlisted_golden.py` a-f (6) | PASS | A |
| TST-CO-04 | AC-CO-04 | `test_tst_co_04_readonly_adapters.py` a-f (6) | PASS | A |
| TST-CO-05 | AC-CO-05 | `test_tst_co_05_legacy_paths_unchanged.py` a-c (3) | PASS | A |
| TST-CO-06 | AC-CO-06 | `test_tst_co_06_sandbox_guard.py` a-e (5) | PASS | A |
| TST-CO-07 | AC-CO-07 | `test_tst_co_07_backup_manifest.py` a-b (2) | PASS | A |
| TST-CO-11 | AC-CO-11 | `test_tst_co_11_no_ai_denylist.py` a-d (4) | PASS | A |
| TST-CO-12 | AC-CO-12 | `test_tst_co_12_egress_tripwire.py` a-e (5) | PASS | A; e = full suite under egress guard: 0 attempts, model_calls_total 0 |
| TST-CO-13 | AC-CO-13 | `test_tst_co_13_determinism.py` a-b (2) | PASS | A; en_IN locale not installed (DEV-13) |
| TST-CO-14 | AC-CO-14 | `test_tst_co_14_runtime_floor.py` a-e (5) | PASS (4) + 1 SKIP (e: no python3.9) | B (OD-S12-12): both modes 3.10 and 3.12 tested |
| TST-HUB-INC02-S01..S03 | (supplementary) | `test_inc02_supplementary.py` (3) | PASS | Untrusted, flags/kill switch, M000 |
Totals: 10/10 planned test IDs green - 43 test methods for the planned IDs (42 ok, 1 skipped) + 3 supplementary = 46 methods; 0 failures, 0 errors. TST-CO-12 e additionally re-runs the other 41 methods under the egress guard (all green).

## Evidence References
- `docs/15-modernization/evidence/inc01/*_report.json`, `summary.txt`, `checksum-log.txt`.
- INC-02: `docs/15-modernization/evidence/inc02/hub-final-{A,B}_report.json`, `hub-final-{A,B}_unittest-result.json`, `char-regression-inc02_report.json`, `mutation-gate-inc02.txt`, `checksum-log.txt`.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- None.

## Unresolved Issues
- RTD-09 (chunked mutation gate).
- INC-02: TST-CO-14 e skipped (no python3.9); hub suite + inner egress-guarded rerun takes 110-130 s, close to the 180 s device-call cap (RTD-19).

## Residual Risks
- RR-TE-1 Timings are from a 2-CPU device VM and will differ in CI.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
