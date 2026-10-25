---
stage: "30 — Release / Cutover / Rollback"
artifact: "deployment-evidence.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/30-release/evidence/s30-rehearsal-summary.txt", "docs/30-release/evidence/s30-regression-groups.txt", "docs/30-release/evidence/s30-characterization.txt", "docs/30-release/evidence/gate-results.json", "docs/30-release/evidence/SHA256SUMS.txt", "tests/hub/test_tst_hub_stg30_*.py"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Stage 30 PREPARES and REHEARSES a release; it does not release, cut over, merge to production, tag, install CI, flip a shipped switch or approve anything. Every approval below is OPEN and belongs to Dinesh Naik (Engagement lead, the only human, OD-04). Defaults marked 'recommended' are agent proposals under OD-32 (scope choices only), not decisions. `zone_h.holders` ships EMPTY. The product is No-AI (OD-08).**

## Summary
What was actually run, where, and with what result. **Nothing was deployed.** All executions are on sandbox copies under `~/fde_sbx`; the working-tree `data/` was never an execution target and its checksum manifest verified rc 0 before and after the rehearsal and every test group.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DE-1 Rehearsal (script `evidence/s30-rehearse.sh`, HEAD 3024200 + docs, Python 3.10.12) [Verified Fact]
| Phase | Result |
|---|---|
| R1 rollout, fresh store | migrate, status, startup-check, verify-audit, posture all rc 0 |
| golden-compare in shadow | rc 6 (11 UNAPPROVED, 2 identical) |
| R2 backup + manifest | rc 0 / rc 0 |
| R3 release-checklist `--mark-ready` | rc 20 E-CO-RELEASE-BLOCKED (G1, G2, G4, G8, G9, G10); checklist without mark: only G1 blocking after real results supplied (log 09b, checklist json) |
| R4 cutover dry-run + L3 | flip refused w/o reference rc 2; held with sandbox marker; posture flags it; flip-to-shadow; verify-audit ok at each step |
| R5 L2 restore | checksum match, chain ok, later records set aside |
| R6 corrupt backup | refused rc 21 |
| R7 L1 revert in a clone | clean; tree equals pre-Stage-31; revert-of-revert restores main |
| R8 regeneration | different hash from shipped baseline (F-29-12 answered) |

### DE-2 Tests [Verified Fact]
- New Stage 30 tests: F01-F03, G01-G07, R01-R04, D01-D05 (19 methods, group S30) and the egress run (group E30, 1 method).
- Groups run: see `s30-regression-groups.txt` (B, I6, I45, I8a, S20, S24, S27, S28, S31 as listed, plus S30 and E30 in the final section). Characterization: `s30-characterization.txt`, only CT-13 fails (Node patch drift S24-DEV-04).
- Not run here: 20 other groups, the orchestrator's full regression, any Python 3.12+ run.

### DE-3 Deviations from the stage prompt and from earlier stages [Verified Fact]
| ID | Deviation |
|---|---|
| S30-DEV-01 | F-29-01 fixed (behaviour change, recorded): `verify-audit` with an unreadable anchor now exits 17 instead of 1; the anchor file is not appended to; other commands unchanged. Also catches TypeError/AttributeError in `audit.verify` (a JSON line that is not an object). Files: `hub/admin/cli.py`, `hub/security/audit.py` |
| S30-DEV-02 | `non_add_edits.json` reset; groups S30 and E30 appended to `regression_groups.json` |
| S30-DEV-03 | Group B reports 1 failure (TST_CO_05_c) only because the local `main` ref moved to 549512a while the branch is based on ef72e4e; against ef72e4e the only non-add entries are the listed ones. Expected to pass after the coordinator rebases |
| S30-DEV-04 | `test_tst_hub_stg31_static_docs.py` D01 relaxed to accept the stage-30 list (listed non-add edit) |
| S30-DEV-05 | The prompt says "prepare and execute"; per the coordinator's scope rule only preparation and sandbox rehearsal were done. No release, tag, merge, CI install, authority flip or approval |
| S30-DEV-06 | New stand-alone package `hub/release/` (evaluator, posture, CLI), not wired into the product |
| S30-DEV-07 | Sandbox marker `REHEARSAL-SANDBOX-NOT-AN-APPROVAL` used as `--approval-ref` on throwaway configs only |
| S30-DEV-08 | Only 11 of 31 groups run by this stage (T-05 not_run) |
| S30-DEV-09 | Stage 28/31 wiring decisions (D-28-01/02/09, D-31-01/02/07) not implemented: each is a behaviour change needing approval |

### DE-4 Behaviour change and assumptions [Verified Fact / Assumption]
One behaviour change (S30-DEV-01), safest option chosen (verify-audit only, fail closed). Assumption A-30-11: exit 17 on a damaged anchor is the intended contract (spec error-handling: tamper = 17).

## Evidence References
`evidence/` (checksummed by `SHA256SUMS.txt`).

## Assumptions
- A-30-11 above.

## Unknowns
- U-30-11 the orchestrator's full regression result at the merge HEAD.

## Unresolved Issues
- Evidence logs were produced at HEAD 3024200; `hub/` has not changed since except nothing (docs/tests only).

## Residual Risks
- RR-30-10 Rehearsal on a tiny synthetic store says little about timing at scale.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 30). |
