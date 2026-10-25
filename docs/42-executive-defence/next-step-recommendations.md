---
stage: "42 — Executive Defence & Final Value Story"
artifact: "next-step-recommendations.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/40-scale/90-day-roadmap.md", "docs/30-release/release-approvals.md", "docs/36-roi/roi-model.md", "docs/39-drift/improvement-backlog.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation. These are recommendations by the agent. None is a decision, none is approved, none is costed.** The order is by what unblocks the story, not by engineering interest. The shortest honest path: **decide, name, define the window, then pilot**. Engineering is no longer the constraint; Dinesh Naik's decisions and a second human are.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### NS-1 Decisions only Dinesh can make (blocking order)
| # | Decision | Why now | Unblocks | Source |
|---|---|---|---|---|
| 1 | Is this engagement continuing toward a pilot, or stopping at a documented sandbox build? Record the go-ahead (roadmap D+0) or a stop | Everything depends on it; the roadmap takes no position | all | `90-day-roadmap.md` SB-01 |
| 2 | Release decision: go / no-go across the 40 approval records (22 release approvals plus step-specific ones, per the evaluator rule); at minimum DV-01..DV-11 preserve-or-fix, CUT-1..CUT-5, G1..G10 acknowledgement | Gate BLOCKED at 0 of 40 | G1 criterion, any cutover | `release-approvals.md`; OD-37 |
| 3 | Name Zone H holders, or declare Zone H unused for the pilot | Human gate cannot be exercised without them | RP-09, pilot | OD-31 |
| 4 | Name owners/responder, or state explicitly that Dinesh alone is the pilot owner; appoint a second reviewer or record that none exists (DQ-17) | 0/28 owners; single approver | RP-01, TOM | OD-34 |
| 5 | Define the after-window: start, unit, minimum duration, data owner, capture method for time and effort | Without it ROI is never computable | Stage 34/35/36 v0.2 | G1-10; D-34-02 |
| 6 | Sign or amend the KPI baseline freeze; raise Stage 4 v0.2 addendum for A-04-01; provide an `as_of` parameter for the hub | Baseline contestable | like-for-like variance | D-34-03/04 |
| 7 | Decide the Python floor and run a 3.12+ regression | Production target untested | RT-14, VR-02 | D-27-02; SB-08, SB-12 |
| 8 | Decide data posture: field classes, tenant, regime, retention, exposure (loopback vs wider with TLS/second factor/token expiry) | Required before any real data | RS-06, RP-04, RP-07, RS-01/02 | SB-20, SB-21 |
| 9 | Accept, reject or reroute residual registers (RP, RS, RTR, VA, SR, F-11) with a review trigger for each | Nothing is accepted today | honest risk position | OD-30..OD-37 |
| 10 | Sign the three reviewer walkthroughs (TST-REV-03/04/08) or leave them open explicitly | RT-13 | TEVV PASS | `walkthrough-records.md` |
| 11 | Accept or reject S30-DEV-01 (verify-audit exit 17), the Stage 27 behaviour defaults (A-27-02/04/05), and the Stage 28/31 numeric defaults | Agent assumptions awaiting a human | traceability of "approved" | OD-34..OD-37 |
| 12 | Install the hardening CI under `.github` with SHA pins (HAR-07) or record "manual" | CI absent | RP-05 | OD-34 |
| 13 | Supply cost inputs for Stage 36 (rate, volumes, reviewer minutes, effort actuals, hosting, toolchain charges, discount rate) | ROI inputs | Stage 36 v0.2 | `roi-model.md`; OD-36 |
| 14 | Instruct Stages 38 (handover) and 41 (retirement), then FINAL | Not produced | closure of the engagement | C-32 |

### NS-2 Engineering work after decisions (proposed, agent Inference)
| Priority | Work | Rationale | Source |
|---|---|---|---|
| P1 | Wire or declare "not used" the Stage 28 controls; run TEVV delta | Controls on paper | SB-16, SB-14 |
| P1 | Persisted metrics export and alert delivery or accept manual monitoring for the window | T-09 fails | D-31-01/08 |
| P1 | Off-device backup and a timed restore drill with a person present; a live tabletop | Recovery unproven | Q-29-xx |
| P1 | Time and effort capture design | K-04, K-05, K-22 are Unknown and block time-saving evidence | VL-11 |
| P2 | Re-issue Stage 25 matrix as v0.2; Stage 34/35/36 as v0.2 on any window | Stale registers | RP-10; OD-36 |
| P2 | Legacy Dockerfile/compose hardening at cutover; nine complex functions; F-11 | Open debt | VR-04, D-27-06/07 |
| P3 | Drift: run IB-01 first evaluation session manually | Drift framework unexercised | `improvement-backlog.md` |

### NS-3 Proposed pilot shape (from the roadmap, not a commitment)
Four phases in relative days: P0 Decide D+0..14; P1 Make fit D+15..45; P2 Pilot (conditional) D+46..75 with S1 for one unit; P3 Evaluate D+76..90 re-running Stages 34/35/36 as v0.2 and deciding limited entry. [Verified Fact] All 12 hard G1 conditions must be met before the pilot starts. [Inference] 90 days reaches at most a limited-entry decision. A 30-day window may be too short to see a month-end. Unless the window completes and slots are filled, the correct D+90 statement is "ROI not computable".

### NS-4 What not to do
Do not present a ROI. Do not run on real data or expose beyond loopback before decisions 8 and 3. Do not flip any authority switch without a recorded human approval reference. Do not let an agent choose Zone H holders, accept risks, or approve cutover (OD-32 limits).

### NS-5 Success definitions for the next review (candidate, to be set by Dinesh)
A signed baseline; a defined and started window; at least one named holder or a declared "unused"; a second reviewer or a recorded "none"; and Stage 34/35/36 v0.2 with at least one like-for-like KPI showing a measured, labelled change either way. A neutral or negative result is a valid result and would be reported as such.

## Evidence References
`docs/40-scale/90-day-roadmap.md`, `scale-out-backlog.md`; `docs/30-release/release-approvals.md`; `docs/36-roi/roi-model.md`; `docs/39-drift/improvement-backlog.md`; OD-24, OD-30..OD-37; claims C-19, C-25, C-27, C-29.

## Assumptions
Priorities are agent Inference. The roadmap's step ordering is a proposal.

## Unknowns
Whether any receiving team or sponsor exists; Dinesh's intent for the capstone after FINAL.

## Unresolved Issues
All of NS-1.

## Residual Risks
Recommendations unadopted; decision fatigue (single decider).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
