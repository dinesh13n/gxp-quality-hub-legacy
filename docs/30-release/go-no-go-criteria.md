---
stage: "30 — Release / Cutover / Rollback"
artifact: "go-no-go-criteria.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/30-release/evidence/gate-results.json", "docs/30-release/evidence/approvals-register.json", "hub/release/register.py", "hub/release/gonogo.py", "hub/ops/release.py", "docs/12-specs/features/f10-coexistence-change-safety.md"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Stage 30 PREPARES and REHEARSES a release; it does not release, cut over, merge to production, tag, install CI, flip a shipped switch or approve anything. Every approval below is OPEN and belongs to Dinesh Naik (Engagement lead, the only human, OD-04). Defaults marked 'recommended' are agent proposals under OD-32 (scope choices only), not decisions. `zone_h.holders` ships EMPTY. The product is No-AI (OD-08).**

## Summary
Decision rule, computed by `python -m hub.release evaluate` over `gate-results.json` and `approvals-register.json`: **GO only if all 20 technical criteria are `pass` AND all 22 release approvals are valid APPROVED records by a named human; a cutover step also needs its own approvals.** Today: **NO-GO** (technical: 16 pass, G1 fail, T-09 fail, T-10 fail, T-05 not_run; approvals: 0 of 40). A `pass` below is evidence, not an approval.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### GN-1 Technical criteria (evidence only)
| ID | Criterion | Result | Evidence | Note |
|---|---|---|---|---|
| G1 | golden diff: unapproved differences = 0 | **fail** | `docs/30-release/evidence/s30-log-06-golden-compare.txt` | golden-compare exit 6: every entry UNAPPROVED because DV-01..DV-11 are proposed (OD-S12-13 open); cannot pass before Dinesh decides |
| G2 | replay-safety suite (AC-INT-04/05) passes | **pass** | `docs/30-release/evidence/s30-regression-groups.txt` | group I6 43/43 (TST_INT, replay safety) |
| G3 | verify-audit ok | **pass** | `docs/30-release/evidence/s30-log-04-verify-audit.txt` | verify-audit ok on the sandbox store; also ok after refusal, authority flip, L3, restore (logs 10, 16, 19, 22, 25) |
| G4 | verify-projection 0 mismatches | **pass** | `docs/30-release/evidence/s30-regression-groups.txt` | group I45 91/91 (projection tests); no stand-alone verify-projection on a production store (none exists) |
| G5 | No-AI tripwire: deny-list clean, no egress, model_calls_total = 0 | **pass** | `docs/30-release/evidence/s30-regression-groups.txt` | tripwires zero in the groups run; hub.admin release-checklist evaluates G5 (log 09b) |
| G6 | secret scan 0; deletion-path grep 0 | **pass** | `docs/30-release/evidence/s30-log-09b-release-checklist-no-mark.txt` | scan evaluated by hub.admin release-checklist |
| G7 | backup/restore rehearsal checksum match | **pass** | `docs/30-release/evidence/s30-log-09b-release-checklist-no-mark.txt` | backup/restore rehearsal evaluated by hub.admin; also logs 07, 08, 21, 22 |
| G8 | Zone H negative tests (AC-GATE-09/11/12) pass | **pass** | `docs/30-release/evidence/s30-regression-groups.txt` | group I8a 35/35 (TST_GATE, TST_REV) |
| G9 | planted-string fixture suite (86/22/44) 0 effects | **pass** | `docs/30-release/evidence/s30-regression-groups.txt` | group I6 (planted-string and untrusted-source tests) |
| G10 | determinism: bit-identical across PYTHONHASHSEED/TZ/locale | **pass** | `docs/30-release/evidence/s30-regression-groups.txt` | TST_CO_13 inside group B (41 of 42 executed ok-or-skipped; the 1 failure is TST_CO_05_c, S30-DEV-03) |
| T-01 | backup manifest of the legacy baseline verifies (rc 0) before and after every rehearsal | **pass** | `docs/30-release/evidence/s30-rehearsal-summary.txt` | manifest rc 0 before and after the rehearsal; rc 0 before and after every group |
| T-02 | L1 code revert rehearsed on a sandbox clone | **pass** | `docs/30-release/evidence/s30-log-31-l1-tree-restored.txt` | revert of the Stage 31 squash commit in a clone gives exactly the pre-Stage-31 hub/ and tests/hub (log 28); revert-of-revert restores main (log 31) |
| T-03 | L2 hub-state backup / restore rehearsed on a sandbox copy | **pass** | `docs/30-release/evidence/s30-log-22-verify-audit-after-restore.txt` | backup, restore, corrupt-backup refusal exit 21 (log 24) |
| T-04 | L3 authority flip and flip back rehearsed on a sandbox copy, audit chain verifies | **pass** | `docs/30-release/evidence/s30-audit-config-changed.txt` | flip refused without reference (exit 2); held with a sandbox marker; flip-to-shadow; two CONFIG_CHANGED records; chain ok |
| T-05 | full hub regression: every group green and executed = expected | **not_run** | `docs/30-release/evidence/s30-regression-groups.txt` | 11 of 31 groups run here; the full regression at the final HEAD is the orchestrator's (OD-23) |
| T-06 | characterization harness: no failure except the registered CT-13 Node drift | **pass** | `docs/30-release/evidence/s30-characterization.txt` | only CT-13 fails (Node patch drift, S24-DEV-04, registered) |
| T-07 | shipped configuration posture: shadow, empty Zone H holders, loopback, schedule off, synthetic data | **pass** | `docs/30-release/evidence/s30-log-23-posture-after-restore.txt` | hub.release posture clean on shipped defaults; hub-hardening workflow not installed (only the legacy verify.yml exists); no config sets an authority switch |
| T-08 | F-29-01 fixed with a test (verify-audit exits 17 on a malformed anchor line) | **pass** | `tests/hub/test_tst_hub_stg30_f2901.py` | F01..F03 green; exit 17 and no traceback |
| T-09 | monitoring coverage for the release window: persisted metrics, alert delivery and an owner | **fail** | `docs/31-observability/alert-catalog.md` | no persisted metrics, no alert delivery, no on-call (F-29-03, D-31-01, D-31-08) |
| T-10 | every High vulnerability and every open High finding has a recorded decision by the Engagement lead | **fail** | `docs/27-hardening/vulnerability-disposition.md` | VR-02, VR-03, VR-04 High items have no accepted disposition; F-11 and risk registers open |

### GN-2 Rules
- [Verified Fact] A criterion with no result counts as `not_run` and blocks. A result file cannot contain an approval (`hub.release` validates the schema).
- [Verified Fact] An APPROVED approval record counts only with a named human approver (agent, system, orchestrator, hub, AI names are refused), a reference, an ISO date and a pointer to where the decision is recorded (tests G03).
- [Inference] Rollback triggers (any of): `verify-audit` exit 17; golden-compare shows an UNEXPLAINED difference in the verification window; a bind other than 127.0.0.1; a model call or egress attempt (tripwire non-zero); outcome-sum mismatch (DM-3); `hub.kill` needed. Action: L3 flip to shadow first, then L1/L2 as `rollback-plan.md` says.
- [Assumption] The numeric thresholds in `docs/31-observability` (SLO candidates) are NOT go/no-go criteria; no SLA exists.

### GN-3 Monitoring coverage (T-09) [Verified Fact]
Persisted metrics, alert delivery and an on-call do not exist (F-29-03). Alerts are evaluated by hand (RB-00) from an offline sample file. Six metrics are not exported (audit_chain_verify_ok etc., F-31-04). T-09 therefore FAILS; it can be cleared by AP-OPS-05 plus the wiring decisions D-31-01/D-31-08, or by Dinesh explicitly accepting manual monitoring for the release window.

## Evidence References
`gate-results.json`; `release-approvals.md`; `deployment-evidence.md`.

## Assumptions
- A-30-06 [Assumption] The 20-criterion list is the minimum for a shadow release; Dinesh may add or remove criteria.

## Unknowns
- U-30-06 whether the orchestrator's full regression at merge HEAD will be green (T-05).

## Unresolved Issues
- G1 cannot pass until DV-01..DV-11 are decided; T-09/T-10 need decisions.

## Residual Risks
- RR-30-5 Criteria are agent-chosen; passing them is necessary, not sufficient.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 30). |
