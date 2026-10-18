---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "test-execution-log.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 only (characterisation harness + hermetic fixtures + mutation gate). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)"]
supersedes: "none"
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

## Evidence References
- `docs/15-modernization/evidence/inc01/*_report.json`, `summary.txt`, `checksum-log.txt`.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- None.

## Unresolved Issues
- RTD-09 (chunked mutation gate).

## Residual Risks
- RR-TE-1 Timings are from a 2-CPU device VM and will differ in CI.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
