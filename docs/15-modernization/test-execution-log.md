---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "test-execution-log.md"
version: "v0.4"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; INC-03 (hub DB migrations M001, C2 access & audit chain, backup/restore, first rollback rehearsal) added in v0.3. Stage 15 overall status: IN PROGRESS. INC-04 (policy & rule service: M002, as-found rule sets inactive, activation with a recorded human decision) added in v0.4."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)", "docs/15-modernization/evidence/inc03/", "docs/15-modernization/rollback-rehearsal-inc03.md", "hub/", "tests/hub/", ".fde/orchestrator-decisions.md (OD-15)"]
supersedes: "v0.3 (INC-01 .. INC-03)"
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

### INC-03 runs (device Python 3.10.12 / SQLite 3.37.2; hub runs from `~/fde_sbx/s15-inc03/<label>/c_pristine`; harness runs under `~/fde_sbx/s15-inc03/char`)
| # | Label | HEAD | Command (from repo root unless stated) | Result | Wall | Checksum rc | Tag |
|---|---|---|---|---|---|---|---|
| 25 | smoke, smoke2 | c21526b-wip | `python -m hub.admin ...` in `~/fde_sbx/s15-inc03/smoke*` (copy of hub/) | all commands as designed; deviation_register delete guard missing -> fixed in M001 | <10 s | 0 | [Verified Fact] |
| 26 | dev1 | c21526b+tests | `tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s15-inc03 --label dev1 -k TST_SEC -k TST_CO_10 -k TST_CO_15 -k INC03` | 45 run, unittest rc 1: TST-SEC-13 b subTests failed (empty tables) -> fixed; recorder showed them as ok (RTD-28) | 67 s | 0/0 | [Verified Fact] |
| 27 | dev2 | +fix | `... --label dev2 -k TST_SEC_13` | 2/2 ok | 47 s | 0/0 | [Verified Fact] |
| 28 | reg-B (1st) | 69aa843 | INC-02 split | aborted: ENOSPC on the device (sandbox only) | 78 s | 0 | [Verified Fact] |
| 29 | reg-B | 69aa843 | `... --label reg-B -k TST_CO_01 -k TST_CO_02 -k TST_CO_04 -k TST_CO_05 -k TST_CO_06 -k TST_CO_07 -k TST_CO_11 -k TST_CO_13 -k TST_CO_14 -k INC02` | 41 run: 39 ok, 1 FAIL (TST-CO-04 d: new sqlite3.connect sites), 1 skipped -> fixed (RD-33) | 79 s | 0/0 | [Verified Fact] |
| 30 | dev3 | 68b93f3 (pre-commit tree) | `... -k TST_SEC -k TST_CO_10 -k TST_CO_15 -k INC03 -k TST_CO_04` | 51/51 ok | 68 s | 0/0 | [Verified Fact] |
| 31 | reg-C | 68b93f3 | `... --label reg-C -k TST_CO_12` | 5/5 ok; inner full suite 86 run, 85 ok, 2 skipped, 0 egress, 0 model calls | 119 s | 0/0 | [Verified Fact] |
| 32 | rehearsal-1 | main 8a01da7 / 68b93f3 | `~/fde_sbx/s15-inc03/rehearsal-1/rehearse.sh` | PASS (rollback-rehearsal-inc03.md) | ~3 s | 0 | [Verified Fact] |
| 33 | inc03-regress | 68b93f3 | `tests/characterization/run_characterization.py --sandbox-root ~/fde_sbx/s15-inc03/char --label inc03-regress` | 134/134 PASS, shipped 15 OK as-found, digests == INC-02 | 39 s | 0 | [Verified Fact] |
| 34-37 | inc03-mut-1..4 | 68b93f3 | `... --mutation-gate --mutants M1-M5 / M6-M9 / M10-M13 / M14,M15 --no-legacy-suite` | 5+4+4+2 = 15/15 KILLED | 169/105/88/104 s | 0 | [Verified Fact] |
| 38 | final-A | 68b93f3 | `run_hub_tests.py --sandbox-root ~/fde_sbx/s15-inc03 --label final-A -k TST_SEC -k TST_CO_10 -k TST_CO_15 -k INC03` | 45/45 ok | 68 s | 0/0 | [Verified Fact] |
| 39 | final-B | 68b93f3 | `... --label final-B` + INC-02 split of #29 | 41 run: 40 ok, 1 skipped (CO-14 e) | 95 s | 0/0 | [Verified Fact] |
| 40 | final-C | 68b93f3 | `... --label final-C -k TST_CO_12` | 5/5 ok; inner 86 run, 85 ok, 2 skipped, egress [], model_calls_total 0 | 108 s | 0/0 | [Verified Fact] |

### INC-03 planned tests (Stage 13 IDs, increment-test-map) - final-A
| Test ID | AC | Test methods (tests/hub/) | Result | Class / note |
|---|---|---|---|---|
| TST-CO-10 | AC-CO-10 | `test_tst_co_10_release_blocked.py` a-b (2) | PASS | A |
| TST-CO-15 | AC-CO-15 | `test_tst_co_15_release_checklist.py` a (1) | PASS | A; G1 from golden-compare (exit 6), G2/4/8/9/10 not_run |
| TST-SEC-01 | AC-SEC-01 | `test_tst_sec_01_route_registry.py` a-d (4) | PASS | A; decision-point level (DEV-20) |
| TST-SEC-04 | AC-SEC-04 | `test_tst_sec_04_fresh_install.py` a-c (3) | PASS | A |
| TST-SEC-05 | AC-SEC-05 | `test_tst_sec_05_lockout.py` a-c (3) | PASS | A; values = Stage 12 proposals |
| TST-SEC-06 | AC-SEC-06 | `test_tst_sec_06_credential_store.py` a-c (3) | PASS | A |
| TST-SEC-09 | AC-SEC-09 | `test_tst_sec_09_audit_events.py` a (1) | PASS | A; decision/policy via C2 API (DEV-21) |
| TST-SEC-10 | AC-SEC-10 | `test_tst_sec_10_verify_audit_ok.py` a-b (2) | PASS | A |
| TST-SEC-11 | AC-SEC-11 | `test_tst_sec_11_tamper_detection.py` a-e (5) | PASS | A |
| TST-SEC-12 | AC-SEC-12 | `test_tst_sec_12_truncation_limit.py` a-b (2) | PASS | A; documents R-SEC-1 |
| TST-SEC-13 | AC-SEC-13 | `test_tst_sec_13_insert_only_triggers.py` a-b (2) | PASS | A |
| TST-SEC-14 | AC-SEC-14 | `test_tst_sec_14_audit_write_failure.py` a (1) | PASS | A |
| TST-SEC-15 | AC-SEC-15 | `test_tst_sec_15_no_secrets_in_audit_logs.py` a-c (3) | PASS | A |
| TST-SEC-16 | AC-SEC-16 | `test_tst_sec_16_exposure_guard.py` a-c (3) | PASS | A; startup-check (DEV-22) |
| TST-SEC-18 | AC-SEC-18 | `test_tst_sec_18_secret_scan_deletion_grep.py` a-c (3) | PASS | B (OD-S12-09 hold-all, OD-15) |
| TST-SEC-21 | AC-SEC-21 | `test_tst_sec_21_config_loaded.py` a-b (2) | PASS | A |
| TST-HUB-INC03-S01..S05 | (supplementary) | `test_inc03_supplementary.py` (5) | PASS | migrations, backup/restore, INC-02 compat, anchor config, Zone H |
Totals: 16/16 planned INC-03 test IDs green - 40 methods + 5 supplementary = 45; INC-02: 46 methods, 45 ok + 1 skipped; 0 failures, 0 errors.

### INC-04 runs (device Python 3.10.12 / SQLite 3.37.2 / Node v22.23.2; hub runs from `~/fde_sbx/s15-inc04/<label>/c_pristine`; harness under `~/fde_sbx/s15-inc04/`)
| # | Label | Code HEAD | Command (from repo root) | Result | Wall | Checksum rc | Tag |
|---|---|---|---|---|---|---|---|
| 41 | first | 7439198 | `tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s15-inc04 --label D -k TST_POL -k TST_CO_03 -k INC04` | 36 run, 36 ok (25 planned IDs + S01..S07) | 66 s | 0/0 | [Verified Fact] |
| 42 | A | 7439198 | `--label A -k TST_SEC -k TST_CO_10 -k TST_CO_15 -k INC03` | 45/45 ok | 77 s | 0/0 | [Verified Fact] |
| 43 | B | 7439198 | `--label B -k TST_CO_01 -k TST_CO_02 -k TST_CO_04 -k TST_CO_05 -k TST_CO_06 -k TST_CO_07 -k TST_CO_11 -k TST_CO_13 -k TST_CO_14 -k INC02` | 41 run: 40 ok, 1 skipped | 84 s | 0/0 | [Verified Fact] |
| 44 | C | 7439198 | `--label C -k TST_CO_12` | 5/5 ok | 115 s | 0/0 | [Verified Fact] |
| 45 | char-regression-inc04 | 7439198 | `tests/characterization/run_characterization.py --sandbox-root ~/fde_sbx/s15-inc04 --label char-regression-inc04` | 134/134 PASS | 88 s | 0 | [Verified Fact] |
| 46-53 | mutants M1..M8 | working tree + mutant | `~/fde_sbx/s15-inc04/mut.sh` (apply, run INC-04 group, `git checkout`, delete copies) | 8/8 KILLED (`evidence/inc04/mutation-gate-inc04.txt`) | ~66 s each | 0 | [Verified Fact] |
| 54 | final-INC04 | 86f1a9a | `--label final-INC04 -k TST_POL -k TST_CO_03 -k INC04` | 37 run, 37 ok (adds S08) | 64 s | 0/0 | [Verified Fact] |
| 55 | final-A | 86f1a9a | as #42 | 45/45 ok | 63 s | 0/0 | [Verified Fact] |
| 56 | final-B | 86f1a9a | as #43 | 41 run: 40 ok, 1 skipped (CO-14 e) | 80 s | 0/0 | [Verified Fact] |
| 57 | final-C | 86f1a9a | as #44 | 5/5 ok; inner full suite 123 run, 122 ok, 2 skipped, egress [], model_calls_total 0 | 103 s | 0/0 | [Verified Fact] |
| 58 | char-final | 86f1a9a | as #45 `--label char-final` | 134/134 PASS, shipped 15 OK as-found | 71 s | 0 | [Verified Fact] |

### INC-04 planned tests (Stage 13 IDs, increment-test-map) - final-INC04
| Test ID | AC | Test methods (tests/hub/) | Result | Class / note |
|---|---|---|---|---|
| TST-CO-03 | AC-CO-03 | `test_tst_co_03_golden_parity.py` a-c (3) | PASS | A; goldens CT-01 / CT-03 / CT-13, night-shift golden, legacy code in the sandbox (python + node) |
| TST-POL-01 | AC-POL-01 | `test_tst_pol_01_10_policy_objects.py` (1) | PASS | A |
| TST-POL-02 | AC-POL-02 | same file (1) | PASS | A |
| TST-POL-03 | AC-POL-03 | same file (1) | PASS | A |
| TST-POL-04 | AC-POL-04 | same file (1) | PASS | A (planned kind nfr-measurement; functional here) |
| TST-POL-05 .. 08 | AC-POL-05 .. 08 | same file (4) | PASS | A |
| TST-POL-09, -10 | AC-POL-09, -10 | same file (2) | PASS | A |
| TST-POL-11 .. 18 | AC-POL-11 .. 18 | `test_tst_pol_11_21_rule_sets.py` (8) | PASS | A; 12-14 are golden parity; 18 includes the recorded-decision flow |
| TST-POL-19, -20, -21 | AC-POL-19, -20, -21 | same file (3) | PASS | B (OD-S12-04): as-found value preserved and marked |
| TST-POL-22 | AC-POL-22 | `test_tst_pol_22_25_purity_inputs_immutability.py` a-c (3) | PASS | A; 1000 evaluations x 3 processes; I/O patched to raise; static import check |
| TST-POL-23 | AC-POL-23 | same file (1) | PASS | B (OD-S12-13): reject mode only (DEV-30) |
| TST-POL-25 | AC-POL-25 | same file (1) | PASS | A |
| TST-HUB-INC04-S01..S08 | (supplementary) | `test_inc04_supplementary.py` (8) | PASS | M002 applier + CLI, activation refusal matrix, no-holders, loader drift / purity, engine edges + legacy deltas, audit rollback, M002 required, L2 rollback + rebuild |
Totals: 25/25 planned INC-04 test IDs green - 29 methods + 8 supplementary = 37 ok, 0 failures, 0 errors, 0 skipped. TST-POL-24 is not in the test map (DEV-32). Prior suites unchanged: INC-03 A 45 ok; INC-02 B 40 ok + 1 skipped; C 5 ok.
[Verified Fact] The first INC-04 run passed at once; the 8-mutant gate was run for that reason and killed every mutant. [Inference] TST-POL-09 and S02 contain subTest loops: the `_driver.py` recorder does not record subTest failures (RTD-28), so `unittest_rc` (0) is the authoritative result alongside `report.json`.

## Evidence References
- INC-03 evidence: `docs/15-modernization/evidence/inc03/` (summary.txt, hub-final-{A,B,C} reports, char-regression-inc03_report.json, mutation-gate-inc03.txt, checksum-log.txt, rollback-rehearsal-1/); `docs/15-modernization/rollback-rehearsal-inc03.md`; commits `git log --oneline main..stage-15-inc03-hub-db-audit`.
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
| v0.3 | 2026-10-18 | claude-fde-agent | INC-03 (branch `stage-15-inc03-hub-db-audit`): sections added; earlier content unchanged. |
| v0.4 | 2026-10-18 | claude-fde-agent | INC-04 (branch `stage-15-inc04-rule-service`): sections added; earlier content unchanged. |
