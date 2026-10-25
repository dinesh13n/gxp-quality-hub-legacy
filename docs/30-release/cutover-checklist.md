---
stage: "30 — Release / Cutover / Rollback"
artifact: "cutover-checklist.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/14-transformation/cutover-plan.md CO-2", "docs/30-release/evidence/s30-rehearsal-summary.txt", "hub/release/register.py"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Stage 30 PREPARES and REHEARSES a release; it does not release, cut over, merge to production, tag, install CI, flip a shipped switch or approve anything. Every approval below is OPEN and belongs to Dinesh Naik (Engagement lead, the only human, OD-04). Defaults marked 'recommended' are agent proposals under OD-32 (scope choices only), not decisions. `zone_h.holders` ships EMPTY. The product is No-AI (OD-08).**

## Summary
A per-step checklist. Column R = rehearsed on a sandbox copy in Stage 30 (done); column X = executed for real (NOT done: no approval exists). Nothing below may be executed until the go/no-go evaluator returns GO for the step.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| # | Step | R | X | Gate / evidence |
|---|---|---|---|---|
| 1 | Entry: AP-REL-01, AP-GATE-*, AP-OPS-01..11 and the step's AP-CUT-n / AP-DV rows are valid APPROVED records; `python -m hub.release evaluate` shows GO | rehearsed as NO-GO (tests G02..G04) | no | HAR-11 |
| 2 | Verify legacy backup: `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0 | yes (rc 0 before and after) | - | STOP-01 |
| 3 | `hub.admin migrate` on the target data dir; `status`; `startup-check`; `verify-audit` | yes (logs 01-04) | no | G3 |
| 4 | `hub golden-compare`: 0 UNAPPROVED (needs approved DV rows) | yes: exit 6, 11 UNAPPROVED | no | G1 |
| 5 | `hub.admin backup --label pre-<step>`; `sha256sum -c SHA256SUMS` in the backup; record audit head | yes (logs 07-08) | no | G7 |
| 6 | Copy the backup off the device (AP-OPS-04) | no | no | HAR-09 |
| 7 | `hub.admin release-checklist --release R-n` with real gate results; `--mark-ready` only when all ten are `pass` | yes: refused (exit 20) and recorded without mark-ready (logs 09, 09b) | no | G1..G10 |
| 8 | Flip: `hub.control set-flag --flag capability_authority.<cap> --value '"authoritative"' --approval-ref <real OD/approval id> --data-dir D` | yes with a sandbox marker; refused without reference | no | FF-2 rule 3 |
| 9 | Re-point the named consumer (AP-OPS-12) | no (no consumer) | no | U-14-01 |
| 10 | Verification window: legacy and hub in parallel, daily `golden-compare`, `verify-audit`; any UNEXPLAINED difference = L3 | partly (one compare in shadow) | no | cutover-plan CO-2 step 5 |
| 11 | Exit: Dinesh records acceptance; legacy keeps running as comparator | no | no | - |
| 12 | Rollback at any step: `flip-to-shadow` (L3); restore (L2); revert (L1); re-run `sha256sum -c` | yes (all three) | no | rollback-plan.md |

## Evidence References
`s30-rehearsal-summary.txt`; tests R01..R04.

## Assumptions
- A-30-09 [Assumption] Steps 6, 9 and 11 are performed by Dinesh personally.

## Unknowns
- U-30-09 duration of a realistic verification window (no real data).

## Unresolved Issues
- Steps 6, 9, 11 cannot be rehearsed (no off-device target, no consumer).

## Residual Risks
- RR-30-8 A checklist run by one person has no independent check.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 30). |
