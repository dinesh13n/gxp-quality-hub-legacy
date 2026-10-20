---
stage: "16 — Validate the Good Repo"
artifact: "test-results.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/16-repo-validation/regression-results.md (run details)", "docs/16-repo-validation/evidence/cloud-regression.log", "docs/16-repo-validation/evidence/char-*.json", "docs/16-repo-validation/evidence/hub-mutation.json", "docs/16-repo-validation/evidence/contracts-cloud.json", "docs/16-repo-validation/evidence/boundary-cloud.json", "docs/16-repo-validation/evidence/obs-laptop.json", "docs/16-repo-validation/evidence/ruff-hub.txt", "docs/14-transformation/evidence/increment-test-map.csv (241 planned tests; classes A/B/C)", "docs/15-modernization/test-execution-log.md", "tests/hub/, tests/characterization/, tests/test_*.py"]
supersedes: "none"
---
**Label: synthetic data, unvalidated - method validation only. Sandbox / shadow evidence only; no production, no human user, no real partner.**

## Summary
Every required suite was executed at `main` 2c63b07 and passes, or its non-execution is dispositioned:

| Suite (Stage 16 scope) | Where | Result | Disposition |
|---|---|---|---|
| Unit + integration + API (hub, 397 methods incl. the 241 planned Stage 13 tests) | cloud (OD-23) | 396 ok, 1 skipped, 0 fail | skip = no python3.9 interpreter (DEV-12), accepted since INC-02 |
| Characterisation (CT-01..CT-16, 134 checks) | laptop 3.10.12 | 134/134 x 6 runs; CT-17/18 NOT-RUN | CT-17 no golden (U-07-05), CT-18 no Docker (HAR-05) - by design, Stage 26/31 |
| Legacy mutation gate M1..M15 | laptop | 15/15 KILLED | — |
| Hub mutation gate INC-08/09 H1..H10 (new) | cloud, throw-away copies | 8/10 KILLED | 2 survivors = test gaps SS-04, SS-08 (debt, not regressions) |
| Shipped legacy tests `tests/test_*.py` | laptop sandbox | ran 15, OK, post-DB sha = Stage 7 R1 | as-found destructive behaviour pinned (RTD-11) |
| Security tests (TST-SEC-*, I8 SEC, TST-CO-11/12, E05..E09 egress) | cloud | all green | — |
| Contract tests (route registry, source contract, schema checks) | cloud + observation | green; schema check 8/10 exact, 2 additive-field lags | DC-02 debt |
| Behaviour comparison (TG-4) | both | D5 = 0 | behavior-difference-report.md |
| Static checks (bandit, ruff F/E9/C901) | cloud | no HIGH in hub; 12 unused-import / unused-variable; 11 functions > complexity 15 | debt S16-D08 |
| Human walkthroughs behind TST-REV-03/04/08 | — | **NOT RUN** | needs a human reviewer (Dinesh or delegate); automated stand-ins green |

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### T-1 Planned Stage 13 tests (241) by increment
[Verified Fact] All 241 planned tests (INC-02 10, INC-03 16, INC-04 25, INC-05 39, INC-06 28, INC-07 39, INC-08 64, INC-09 20) are inside the groups run in R-1 of regression-results.md (TST-CO-03 run separately) and pass. Class-B tests (35, decision-dependent) are green against the **specified defaults** only (e.g. TST-POL-23 "invalid input refused", no preserve mode); they will need re-running after the human decisions (OD-S12-xx). Class-C tests (9) produce sandbox proxies only (NFR figures, RTD-72).

### T-2 Test types required by the Stage 16 scope
| Type | Representative tests | Status | Tag |
|---|---|---|---|
| Unit | TST-POL-*, TST-DEC-*, TST-MET-*, INC supplementary | green | [Verified Fact] |
| Integration | TST-INT-* (shadow intake of the shipped sources), TST-CO-09 rollback rehearsal, INC06 S02 CLI chain | green | [Verified Fact] |
| Contract | TST-SEC-01 route registry vs OpenAPI, INC06 S03 source contract copy, TST-RUN schema checks; Stage 16 schema check (data-contract-results DC-2) | green / 2 schema lags | [Verified Fact] |
| Characterisation | CT-01..CT-16 + TST-CO-03 parity | green | [Verified Fact] |
| Security | TST-SEC-01..21, I8-SEC, TST-CO-11/12, E0xEGRESS, mutation H1-H10 | green; 2 mutants survive | [Verified Fact] |
| Data-contract | source-contract-v1 outcomes per source | as expected (record_only) | [Verified Fact] |
| Static / dependency / architecture | bandit, import scan, ruff, package dependency graph | see respective reports | [Verified Fact] |

### T-3 Additional Stage 16 executions
| ID | What | Result | Tag |
|---|---|---|---|
| T-3a | `s16_observe.py`: built-module observations for DV-01..09, policy evaluate, shadow intake, month-end, divergence, golden-compare, verify-audit | all CLI steps rc as expected (golden-compare 6 by design; invalid inputs 23 by design); verify-audit rc 0; fixture hashes unchanged; identical results on 3.10.12 and 3.13 | [Verified Fact] |
| T-3b | `s16_boundary.py`: x1.05 tolerance boundary, 105 cases | 105/105 identical legacy JS vs hub Decimal | [Verified Fact] |
| T-3c | `s16_contracts.py`: 22,430 objects vs 10 schemas | see DC-2 | [Verified Fact] |

### T-4 Hub mutation gate (INC-08 / INC-09)
| Mutant | Inc | Behaviour weakened | Result | Killed by |
|---|---|---|---|---|
| H1 | 08 | Zone H non-holder accepted | KILLED | TST-GATE-21 |
| H2 | 08 | CSRF disabled | KILLED | I8-SEC-17 |
| H3 | 08 | X-Frame-Options weakened | SURVIVED | — |
| H4 | 08 | non-loopback peer accepted | KILLED | INC08-S07 |
| H5 | 08 | non-loopback bind accepted | SURVIVED | — |
| H6 | 09 | search enabled by default | KILLED | INC09-S03, S10 |
| H7 | 09 | C3 reason not required (search) | KILLED | I9-SEC-20 |
| H8 | 09 | C3 reason not required (protection) | KILLED | I9-SEC-20 |
| H9 | 09 | divergence counts nulls | KILLED | I9-POL-24 |
| H10 | 09 | drafts enabled by default | KILLED | I9-REV-18, INC09-S10 |
[Inference] INC-09's kill rate (5/5) is good; INC-08's (3/5) shows assertion gaps in HTTP hardening. Ten hand-chosen mutants are a sample, not a full mutation analysis (no mutation tool installed; RTD-04 coverage still Unknown).

### T-5 Findings register
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| TR-01 | All required suites pass or are dispositioned | Summary table | gate condition met | Low | High | — |
| TR-02 | Human walkthroughs TST-REV-03/04/08 not run (no human tester in this engagement) | Stage 15 hand-over | reviewer UX unproven | Medium | High | Dinesh: run or accept-open (Stage 26 TEVV) |
| TR-03 | Two hub mutants survive (SS-04, SS-08) | T-4 | security hardening regressions could pass | Medium | High | add tests (Stage 23) |
| TR-04 | Class-B tests encode spec defaults; decisions may flip them | T-1 | rework after OD-S12-xx | Medium | High | U-13-13 |
| TR-05 | Branch / line coverage unknown (no coverage tool, RTD-04) | — | blind spots unknown | Medium | Medium | Stage 23 when installs are allowed |
| TR-06 | Static quality: 12 pyflakes findings (unused imports / variables) and 11 functions above McCabe 15 (`hub/decision/service.py transition` 25, `hub/web/app.py _dispatch` 22, `hub/policy/engine.py evaluate` 21, …) | `evidence/ruff-hub.txt` | maintainability | Low | High | clean-up when non-add edits are allowed |

## Evidence References
- Commands: regression-results.md; `s16_observe.py`, `s16_boundary.py`, `s16_contracts.py`, `s16_hub_mutation_gate.py` headers.

## Assumptions
- A-16-TR-1 [Assumption] Automated stand-ins for TST-REV-03/04/08 are acceptable evidence until a human walkthrough is run. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-16-TR-1 Coverage (RTD-04); U-16-TR-2 behaviour under concurrency (CT-17) and in containers (CT-18).

## Unresolved Issues
- TR-02, TR-03, TR-05.

## Residual Risks
- RR-TR-1 Tests are run manually only (no CI) - High until Stage 27.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
