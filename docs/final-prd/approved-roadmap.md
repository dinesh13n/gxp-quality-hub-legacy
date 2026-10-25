---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "approved-roadmap.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/40-scale/90-day-roadmap.md", "docs/40-scale/scale-out-backlog.md", "docs/40-scale/reuse-readiness-assessment.md", "docs/42-executive-defence/next-step-recommendations.md", "docs/30-release/release-plan.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
No roadmap is approved. This file presents the proposed gated roadmap, corrected for the current state, and the decisions that would approve it. File name follows the stage prompt; the content is NOT approved.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RM-1 Status of this file
The prompt calls this artifact the *approved* roadmap. **No roadmap is approved.** The content below is the Stage 40 *proposed* gated 90-day roadmap (`docs/40-scale/90-day-roadmap.md`), reconciled to the OD-37/OD-38 state. Approval is Dinesh's decision and is OPEN (SB-01). The roadmap takes no position on cutover.

### RM-2 Reconciliation of the Stage 40 roadmap with the current state (main 08add05)
| Stage 40 statement (baseline ef72e4e) | Current state | Effect |
|---|---|---|
| Stage 39 not merged (PRE-16, SB-09) | Stage 39 merged (PR #25); drift framework exists as design only | SB-09 can be closed by reading Stage 39 |
| F-29-01 `verify-audit` KeyError to be fixed (SB-18, G1-8) | Fixed at Stage 30 with tests (exit 17); acceptance of the exit-17 behaviour change OPEN (HO-12); F-29-02..16 remain | G1-8 partly satisfied |
| Stage 30 outcome not recorded (PRE-17, G1-11) | Stage 30 BLOCKED, 0 of 40 approvals recorded (OD-37); cutover decision still Dinesh's | G1-11 'outcome recorded' = BLOCKED; decision OPEN |
| Stage 38 not produced | Stage 38 BLOCKED (OD-38); Stage 41 BLOCKED; Stage 42 CONDITIONAL PASS | Receiver and operator exercises become pilot pre-conditions |
| 17 scale pre-conditions all unmet | Still unmet except PRE-16 (consumed), PRE-09 (F-29-01 fixed, rest open) | No gate has moved |

### RM-3 Phases (relative days; proposed, not scheduled) [Verified Fact: Stage 40]
| Phase | Window | Purpose | Gate |
|---|---|---|---|
| P0 Decide | D+0..D+14 | Close the decisions everything waits on (SB-01, 02, 03, 08, 09, 37, 38) | G0 |
| P1 Make fit to pilot | D+15..D+45 | Owners and holders, data and exposure decisions, 3.12+ evidence, wiring or 'not used', backup drill, walkthroughs, after-window definition | G1 (12 HARD conditions) |
| P2 Pilot (conditional) | D+46..D+75 | Operate S1 for one unit; daily tripwire and chain checks; capture K-21, time, cost inputs | end of window |
| P3 Evaluate and decide | D+76..D+90 | Re-run Stages 34/35/36 as v0.2; decide limited entry; re-issue roadmap v0.2 | G2 |
Scale steps: Pilot S1, Limited S2, Broader S3 (S2/S3 defined, not scheduled, after D+90).

### RM-4 What must be true before any pilot (G1 HARD conditions) [Verified Fact]
G1-1 walkthroughs signed; G1-2 full regression green on Python 3.12+/3.13 at then-current HEAD; G1-3 Zone H holders named or Zone H declared unused, no capability authoritative; G1-4 pilot responder and asset ownership recorded or single-approver stated; G1-5 data decisions (field classes, tenant, regime, retention); G1-6 exposure posture (loopback or TLS + second factor + token expiry); G1-7 off-device backup and timed restore drill; G1-8 F-29-01 fixed and remaining F-xx dispositioned; G1-9 Stage 28 controls wired or 'not used', TEVV delta green; G1-10 after-window defined with time/effort capture; G1-11 Stage 30 outcome and cutover decision recorded; G1-12 non-carry checklist. Soft: G1-13 CI installed, G1-14 observability wired.

### RM-5 Honest outlook [Inference]
90 days reaches at most a limited-entry decision. A 30-day pilot window may be too short to see a month-end. Unless the window completes and the Stage 36 slots are filled with measured values and a finance-approved rate, the correct statement at D+90 is 'ROI not computable'. A neutral or negative result is a valid result.

### RM-6 Release path in the order Stage 30 recommends [Verified Fact]
CUT-2 (rule evaluation), CUT-1 (decision record and audit), CUT-3 (intake outcomes), CUT-4 (metrics, month-end), CUT-5 (automation and exposure, last). Prerequisites per step in `docs/30-release/release-plan.md`; each step needs its own approvals (AP-CUT-n, AP-DV-nn). Retirement follows only after cutover (Stage 41 ladder RL-0..RL-3; deletion not proposed).

### RM-7 Proposed decisions for the next review (Stage 42 NS-1; none decided)
1 continue to pilot or stop at a documented sandbox build; 2 release decision across the 40 records; 3 Zone H holders or 'unused'; 4 owners or 'Dinesh alone'; 5 define the after-window; 6 sign/amend the KPI baseline; 7 Python floor and 3.12+ run; 8 data posture; 9 route residual registers; 10 sign walkthroughs; 11 accept/reject agent-assumed defaults; 12 CI install; 13 cost inputs; 14 rule on Stage 39/40-before-38 sequencing.

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-17 [Assumption] Day numbers are relative to a D+0 that Dinesh has not set (SB-01).

## Unknowns
- U-43-19 Whether a pilot sponsor, unit or receiving team exists.

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
