---
stage: "30 — Release / Cutover / Rollback"
artifact: "release-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/14-transformation/cutover-plan.md", "docs/14-transformation/rollback-strategy.md", "docs/26-tevv/tevv-release-gate.md", "docs/27-hardening/production-readiness-checklist.md", "docs/29-incident-bcdr/incident-readiness.md", "docs/30-release/evidence/gate-results.json", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Stage 30 PREPARES and REHEARSES a release; it does not release, cut over, merge to production, tag, install CI, flip a shipped switch or approve anything. Every approval below is OPEN and belongs to Dinesh Naik (Engagement lead, the only human, OD-04). Defaults marked 'recommended' are agent proposals under OD-32 (scope choices only), not decisions. `zone_h.holders` ships EMPTY. The product is No-AI (OD-08).**

## Summary
**What is being released.** The Quality Hub (`hub/`) built in Stages 15-31, running in SHADOW next to the unchanged legacy system. No production environment, host, consumer or real data exists (OD-04), so "release" here means: a tagged, rollback-able hub baseline that could be installed on one named host in shadow mode, followed by five independent authority moves (CUT-1..CUT-5).

**State at Stage 30.** Preparation and rehearsal are done; the release and every cutover step are NOT executed. The go / no-go evaluator (`python -m hub.release evaluate`) returns **NO-GO**: 4 of 20 technical criteria fail or are not run (G1, T-05, T-09, T-10) and 0 of 40 human approvals exist. Recommended order when approvals exist: shadow release, then CUT-2, CUT-1, CUT-3, CUT-4, CUT-5 (cutover-plan CO-1).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| RP-1 | [Verified Fact] Upstream gates were confirmed: Stage 14 plan (DRAFT), Stage 26 CONDITIONAL PASS, Stage 27 CONDITIONAL PASS, Stage 29 CONDITIONAL PASS; none was an approval | stage docs above | Stage 30 may prepare, not release | - | High | - |
| RP-2 | [Verified Fact] The release record refuses `ready` unless G1..G10 are all `pass`; in the rehearsal six unevaluated gates blocked it (exit 20) | `s30-log-09-*`; `tests/hub/test_tst_hub_stg30_rehearsal.py` R03 | the product's own rule makes a release impossible today | - | High | - |
| RP-3 | [Verified Fact] G1 fails: `golden-compare` exit 6, 11 UNAPPROVED entries and 2 identical, because DV-01..DV-11 are proposed | `s30-log-06-golden-compare.txt` | no shadow release or cutover can be marked ready until Dinesh decides the DV rows | Blocking for release | High | OD-S12-13 |
| RP-4 | [Verified Fact] No consumer of legacy outputs is identifiable | cutover-plan CF-1 | CUT-2..CUT-4 step 4 (re-point) cannot be planned concretely | Medium | High | U-14-01 |
| RP-5 | [Inference] Releasing the hub in shadow changes nothing a user relies on; value only starts with CUT-1/CUT-2 | cutover-plan RR-CO-1 | a shadow-only release delivers no benefit by itself | Low | Medium | - |
| RP-6 | [Verified Fact] Release steps in order: confirm gates; plan promotion/flags; verify backup and rollback; obtain approvals; go/no-go; deploy; validate; record. Steps 1-3 and the evaluation of step 5 were done; steps 4, 6, 7 were not (no approvals exist) | this directory | stage is prepared, not complete | - | High | - |

## Evidence References
`release-approvals.md`, `go-no-go-criteria.md`, `cutover-checklist.md`, `rollback-plan.md`, `deployment-evidence.md`, `release-outcome.md`; `hub/release/`; `tests/hub/test_tst_hub_stg30_*.py`.

## Assumptions
- A-30-01 [Assumption] R1 release = shadow install on one host, loopback only, scheduler off (feature-flag-plan FF-1 defaults). Confirm: Engagement lead (Dinesh Naik).
- A-30-02 [Assumption] The recommended cutover order of Stage 14 still holds. Confirm: Dinesh.

## Unknowns
- U-30-01 which host, who operates it, and who the first consumer is.
- U-30-02 whether a release tag or a merge is the release act (the repository has a remote, OD-05, but no deployment target).

## Unresolved Issues
- Release not executed; see `release-outcome.md` for the gate (BLOCKED) and the clearing actions.

## Residual Risks
- RR-30-1 A release made while G1 is red would show unapproved behaviour changes as if accepted. Mitigated by the release record's own refusal.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 30). |
