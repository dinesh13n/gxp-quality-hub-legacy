---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "human-control-test-results.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["tests/hub/test_tst_hub_stg23_controls.py", "tests/hub/test_tst_hub_stg23_registry.py", "tests/hub/test_tst_hub_stg23_schemas.py", "tests/hub/test_tst_hub_stg23_catalogue.py", "tests/hub/test_tst_hub_stg23_egress_guard.py", "tests/hub/regression_groups.json", "docs/23-human-control/evidence/hub-mutation-s23.json", "docs/23-human-control/evidence/*.json", "tests/characterization/run_characterization.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
The Stage 23 controls are tested by 27 new test methods in two new groups (S23 = 26 methods, E23 = 1 egress-guard method), and the 19 regression groups (the 17 required plus C2 and I45) ran green with executed = expected. Mutants of the new controls (H1, H3, H5, A1, A2) are all KILLED, including Stage 16's H3 and H5, which had survived. The characterization harness passes; `data/` checksums were rc 0 before and after. All results are synthetic, unvalidated, and were produced in sandbox copies on the laptop (Python 3.10.12).

## Findings
### New tests (group S23, selector `STG23`; E23 runs the same modules under the egress guard)
| Test | Work item | Proves |
|---|---|---|
| S01, S02 | DW-14 | security headers have exact values in process and over the wire |
| S03, S04, S05 | DW-15 | an approved non-loopback bind is refused by the guard, the server factory and the `serve` command (exit 9) |
| S10 | DW-17 | ships OFF: no non-default flag, no authoritative capability, holders empty |
| S11 | DW-17 | non-default flag refused without `approval_ref` (nothing written) |
| S12 | DW-17 | accepted with a reference and audited CONFIG_CHANGED |
| S13 | DW-17 | L3 flip back to shadow, audited, idempotent |
| S14 | DW-17 | a config-file edit is audited or refused at the next start |
| S15 | DW-17 | class-B pattern: default and decided modes leave every other control unchanged |
| S16 | DW-17 | shipped configuration is OFF and holders empty |
| S20..S24 | DW-13 | codes in code = registry (109, diff 0); exit-code uniqueness; clash check works; CLI `--check` |
| S30..S34 | DW-16 | validator support; v0.2 additive; 16 of 16 schemas exercised; table coverage; drift detected |
| S40, S43 | DW-18 | catalogue matches the code (ZH 10 of 10, HAR 16 of 16); shipped gate closed |
| S41, S42 | DW-18 | Zone H refusal matrix (ZH-01..10, 30 requests) and success matrix (ZH-01, 02, 03, 07, 08, 09) |
| E23 S90 | all | the 26 methods under the egress guard: 0 attempts, 0 model calls, none skipped |

### Regression groups (one group per device call, sandbox deleted after; `evidence` = run logs on the laptop)
| Group | Executed / expected | Result |
|---|---|---|
| A | 45 / 45 | ok 45 (after the TST-SEC-21 fixture edit, S23-DEV-02; the first run had 1 error from a hand-written holder config) |
| B | 42 / 42 | ok 41, skipped 1 (TST-CO-14 b: `python3.9` not installed on the laptop; unchanged from earlier stages) |
| C1 | 5 / 5 | ok |
| C2 | 1 / 1 | ok |
| C3 | 1 / 1 | ok |
| I45 | 91 / 91 | ok |
| I6 | 43 / 43 | ok |
| I7 | 59 / 59 | ok |
| I8a | 35 / 35 | ok (TST-GATE-09/11/12 included) |
| I8b | 43 / 43 | ok |
| E8 | 1 / 1 | ok |
| I9 | 33 / 33 | ok |
| E9 | 1 / 1 | ok |
| S20 | 18 / 18 | ok |
| E20 | 1 / 1 | ok |
| S21 | 7 / 7 | ok |
| E21 | 1 / 1 | ok |
| S23 | 26 / 26 | ok |
| E23 | 1 / 1 | ok |

Group B (No-AI, sandbox, legacy-paths tests) and the egress groups were run by the build agent, as required. [Verified Fact]

### Mutants (`evidence/hub-mutation-s23.json`; each in a throw-away copy, selector `STG23`)
| Mutant | Change | Result | Killed by |
|---|---|---|---|
| H3 (DW-14) | `X-Frame-Options` DENY -> SAMEORIGIN | **KILLED** | S01, S02 |
| H5 (DW-15) | loopback test in the server factory removed | **KILLED** | S03, S04, S05 |
| A1 (DW-17) | approval reference check removed | **KILLED** | S11, S14 |
| A2 (DW-17) | config-file authority change not audited | **KILLED** | S14 |
| H1 (DW-18) | holder membership test removed | **KILLED** | S41 |

### Other checks
- Data checksums (`sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt`): rc 0 before the stage, after the test runs and at hand-off. [Verified Fact]
- Characterization harness: OVERALL PASS (CT-01..CT-16 pass; CT-17 and CT-18 NOT-RUN as before: no golden for CT-17 (U-07-05), Docker unavailable (HAR-05)); shipped `tests/test_*.py` 15 run OK; post-run DB equals Stage 7. [Verified Fact]
- Legacy code and `data/` byte-identical: TST-CO-05 a / b green in group B.

### Findings
- [Verified Fact] The first run of group A failed once (TST-SEC-21 hand-writes a holder config and now needs an `approval_refs` entry); fixed by a one-line test edit, listed in `non_add_edits.json`; no hub behaviour was weakened.
- [Verified Fact] In the H5 run the pass / fail counts add to 25 of 26 although three tests are named as failing; one test did not report in that run (inconclusive for that method, the mutant is still killed by three).
- [Inference] The suite kills the mutants because the assertions compare exact values (headers, exit code 9, `approval_ref` presence) rather than only the absence of an error.
- [Unknown] Behaviour on Python 3.12 (OD-24 production target): not run here (3.10 laptop). The 3.12 cloud run is the orchestrator's.
- [Unknown] Python 3.9 floor refusal (skipped test).

## Evidence References
Run logs `~/fde_sbx/s23-logs/*.json` (laptop, sandbox runs; copied counts above); `evidence/hub-mutation-s23.json`; the evidence JSON files named in the tests.

## Assumptions
- A-23-13 Passing on Python 3.10.12 is a fair proxy until the orchestrator's 3.12 run.

## Unknowns
- U-23-16 Python 3.12 result. U-23-17 Python 3.9 refusal path on this device.

## Unresolved Issues
- None blocking.

## Residual Risks
- Tests prove the mechanism with synthetic holders and references, not that a real approval exists (RR-HC-1).
- The sandbox run logs are on the laptop, not in the repository.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
