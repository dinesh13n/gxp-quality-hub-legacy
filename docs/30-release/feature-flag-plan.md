---
stage: "30 — Release / Cutover / Rollback"
artifact: "feature-flag-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/14-transformation/feature-flag-plan.md", "hub/control/flags.py", "hub/config.py", "hub/release/gonogo.py", "docs/30-release/evidence/s30-log-11-flags-before.txt"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Stage 30 PREPARES and REHEARSES a release; it does not release, cut over, merge to production, tag, install CI, flip a shipped switch or approve anything. Every approval below is OPEN and belongs to Dinesh Naik (Engagement lead, the only human, OD-04). Defaults marked 'recommended' are agent proposals under OD-32 (scope choices only), not decisions. `zone_h.holders` ships EMPTY. The product is No-AI (OD-08).**

## Summary
Flags are configuration keys, not a flag service (ADR-015). Every decision flag ships at its safe default; every capability ships `shadow`. A non-default value needs `approval_refs[<flag>]` (a pointer to a recorded human decision; the hub cannot verify it), and every change is an audited `CONFIG_CHANGED`. Stage 30 added a read-only **posture check** (`python -m hub.release posture`) that fails on any non-default flag, non-empty `zone_h.holders`, non-loopback bind, enabled schedule, kill switch or approval_refs in the shipped config. Shipped posture: clean (violations = []).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| Flag | Shipped | Changed by Stage 30? | To change needs | Tag |
|---|---|---|---|---|
| `capability_authority.<cap>` (CUT-1..5 map to capabilities) | none set = shadow | NO | AP-CUT-n + its AP-DV rows + `--approval-ref` | [Verified Fact] |
| `zone_h.holders` | `[]` | NO (stays EMPTY) | real names (AP-OPS-13, OD-S12-06, HAR-11/12) | [Verified Fact] |
| `disposition.mode` | `none` | NO | OD-S12-05 + HAR-12 | [Verified Fact] |
| `closure.unconfigured_behaviour`, `workflow.transition_table`, `facts.derivation` | defaults | NO | OD-S12-03 / -16 / -15 | [Verified Fact] |
| `case_creation.enabled`, `search.enabled`, `search.fts`, `templates.enabled` | off | NO | OD-S12-19 / -14 / -12, PCH-22 | [Verified Fact] |
| `schedule.enabled` | false | NO | OD-S12-10 + HAR-10 (refused in config) | [Verified Fact] |
| `network.bind` / `exposure_approved` | 127.0.0.1 / false | NO | HAR-05, Stages 23-25 | [Verified Fact] |
| `hub.kill` | false | NO | none needed to stop | [Verified Fact] |
| `data_origin` | synthetic | NO | HAR-15 | [Verified Fact] |

Rehearsal [Verified Fact]: on a sandbox config, `set-flag capability_authority.CUT-2 "authoritative"` without a reference was refused (exit 2, E-CFG-INVALID); with the marker `REHEARSAL-SANDBOX-NOT-AN-APPROVAL` it held and the posture check reported it; `flip-to-shadow` returned the posture to clean. The marker is not an approval and was never written to any shipped file (`s30-config-while-authoritative.json` is the sandbox copy).

Flag lifecycle at release [Inference]: no flag is removed at Stage 30; removal criteria stay as in Stage 14 FF-1. Rule gap [Verified Fact]: the approval reference is free text; "no reference, no switch" prevents an accidental flip but not a made-up reference. Hence `release-approvals.md` keeps the real approval in a separate register with named human, date and pointer.

## Evidence References
`rollback-plan.md` (L3), `cutover-checklist.md`; tests R02 and D04.

## Assumptions
- A-30-05 [Assumption] Capability names for CUT-1..5 are chosen at cutover; the rehearsal used `CUT-2`.

## Unknowns
- U-30-05 whether a GxP change-control record is required for a flag change (Stage 14 U-14-09).

## Unresolved Issues
- The approval-reference rule cannot verify the approver.

## Residual Risks
- RR-30-4 A hand-edited config can set a flag; the next start-up audits it (S23) but does not block it if a reference string exists.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 30). |
