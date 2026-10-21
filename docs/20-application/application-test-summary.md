---
stage: "20 — Application & Services Engineering"
artifact: "application-test-summary.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/20-application/evidence/regression-groups-laptop.json", "docs/20-application/evidence/mutation-gate.json", "docs/20-application/evidence/characterization-summary.json", "docs/20-application/evidence/no-ai-check.json", "tests/hub/regression_groups.json", "tests/hub/run_hub_groups.py", "../_data-backup-2026-10-17/SHA256SUMS.txt", ".fde/orchestrator-decisions.md OD-03a, OD-16, OD-21, OD-23"]
supersedes: "none"
---
**Label: synthetic data, unvalidated - method validation only. All runs on the reference laptop (Python 3.10.12, SQLite 3.37.2) in sandbox copies under ~/fde_sbx/s20-*, deleted after each run; backup checksum `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0 before and after every run. Per OD-23 the build agent ran its new / changed tests; the orchestrator runs the full hub regression once before merge.**

## Summary
New tests: 18 Stage 20 methods (selector `STG20`, group S20) + 1 egress-guard method (`E20EGRESS`, group E20) + TST-CO-01 f + TST-CO-12 e1/e2/e3 (replacing e). Static method count 397 -> **419**, every one selected by exactly one of the **15** manifest groups (STG20 S01). All Stage 20-run groups green; mutation gates KILLED; characterisation harness 134/134 with INC-01 digests.

## Findings
### TS-1 Group runs (`python3 -B tests/hub/run_hub_groups.py --sandbox-base ~/fde_sbx/s20-g --group <G>`)
| Group | Selectors | Expected = executed | Result | Wall s (laptop, incl. 45-90 s sandbox build) | Tag |
|---|---|---|---|---|---|
| B | TST_CO_01/02/04/05/06/07/11/13/14, INC02 | 42 | 41 ok + 1 skipped (no python3.9, DEV-12) | 102.8 | [Verified Fact] |
| C1 | TST_CO_12_a..d, e1 | 5 | 5 ok | 82.6 (109.3 earlier run) | [Verified Fact] |
| C2 | TST_CO_12_e2 | 1 | ok | 106.4 (153.8 earlier run) | [Verified Fact] |
| C3 | TST_CO_12_e3 | 1 | ok | 77.2 | [Verified Fact] |
| S20 | STG20 | 18 | 18 ok | 99.6 | [Verified Fact] |
| E20 | E20EGRESS | 1 | ok (inner: 0 egress, 0 model calls, 0 skipped) | 79.6 | [Verified Fact] |
Inner-run split of old group C measured per module shard: 13 s / 60 s / 23 s (shard 2 holds TST-CO-07, 40 s of `sha256sum -c` over the mounted backup). [Verified Fact]

### TS-2 Targeted runs of existing suites touching changed code (`run_hub_tests.py -k ...`)
| Selectors | Result | Tag |
|---|---|---|
| STG20, TST_CO_01, TST_CO_02, INC02_S03, INC03_S03 | 22/22 ok | [Verified Fact] |
| TST_POL, TST_DEC | 53/53 ok (before DW-06) | [Verified Fact] |
| TST_MET, TST_GATE | 38/38 ok (before DW-06) | [Verified Fact] |
| I9_, INC09_S, TST_REV | 46/46 ok (before DW-06) | [Verified Fact] |
| INC04, INC05_S, INC07_S, INC08_S, I8_ | 66/66 ok (before DW-06) | [Verified Fact] |
| TST_SEC, INC03, TST_POL | 68/68 ok (after DW-06) | [Verified Fact] |
| TST_GATE, TST_REV, INC05_S, INC08_S | 62 ok + 1 FAIL (INC08_S01: patched `wschema.migration` no longer seen by `require`) -> fixed (web.schema.require keeps its own body) | [Verified Fact] |
| INC08_S01, I8_, INC09_S | 25/25 ok (after fix) | [Verified Fact] |
| I9_, TST_RUN, TST_CO_11, TST_CO_13 | 40/40 ok (after DW-06) | [Verified Fact] |
Groups A, I45, I6, I7, I8a, I8b, E8, I9, E9 were not re-run as whole groups by the build agent (OD-23): the orchestrator's full regression (`run_hub_groups.py --all`) is required before merge. [Verified Fact]

### TS-3 Mutation gate (`docs/20-application/evidence/s20_mutation_gate.py`)
| Mutant | Change | Selectors | Result | Killed by | Tag |
|---|---|---|---|---|---|
| H1S20 | `zone_h.refusal` accepts non-holders (replaces S16 H1, whose anchor moved) | TST_GATE | KILLED (1 FAIL / 22) | TST-GATE-21 | [Verified Fact] |
| G1S20 | intake stops flagging negative quantities | TST_CO_01, STG20_S04 | KILLED (4 FAIL / 7) | TST-CO-01 b, c, d; STG20 S04 | [Verified Fact] |

### TS-4 Other gates
- Characterisation harness (`run_characterization.py --sandbox-root ~/fde_sbx/s20-h --no-legacy-suite`): OVERALL PASS 134/134; capture digests api c6db0a43…, batch 40237661…, lib c5797c3b…, supplement c3cbab2c… = INC-01 (CG-2). [Verified Fact]
- `python -m hub no-ai-check` rc 0, no findings (CG-7). [Verified Fact]
- Legacy paths unchanged since `baseline-as-found` (TST-CO-05 a/b green in group B, CG-4); every non-add edit listed (TST-CO-05 c). [Verified Fact]
- golden-compare with the observation record: D5 = 0 (CG-9); 11 UNAPPROVED = DV-01..DV-11 proposed (D4), each blocking its CUT step (CUT-2: DV-05, DV-06, DV-11; CUT-3: DV-02, DV-03, DV-07, DV-09, DV-10; CUT-4: DV-01, DV-04, DV-08). [Verified Fact]

## Evidence References
`evidence/regression-groups-laptop.json`, `mutation-gate.json`, `characterization-summary.json`, `no-ai-check.json`, `golden-compare-observed.json`.

## Assumptions
- A-20-TS-1 [Assumption] Targeted runs plus the orchestrator's full regression satisfy DoD-W item 4 (OD-23).

## Unknowns
- U-20-TS-1 Results on Python 3.12+ (OD-24 target) - not run here; Stage 27 CI (DW-26).

## Unresolved Issues
- DW-03 headroom target (< 120 s per group, A-18-DB-4) met in the latest runs of C1/C2/C3/B/S20/E20 but C2 measured 153.8 s once: wall time is dominated by the sandbox build from the mounted folder (variable 45-90 s), not by tests. Remedy: faster sandbox build / runner housekeeping (DW-31, Stage 27).
- Whole-group timings of A, I45, I6, I7, I8a, I8b, E8, I9, E9 on the laptop: not measured by the build agent.

## Residual Risks
- RR-TS-1 report.json counts can overstate passes for subTest failures (RTD-28 / RG-04); STG20 S10 uses subTests - its result relies on unittest_rc (Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
