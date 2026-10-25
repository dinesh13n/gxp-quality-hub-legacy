---
stage: "40 — Scale / 90-Day Transformation Roadmap"
artifact: "scale-out-backlog.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 40 run)"
status: "DRAFT"
evidence_sources: ["docs/40-scale/reuse-readiness-assessment.md", "docs/40-scale/scale-risk-assessment.md", "docs/27-hardening/production-readiness-checklist.md", "docs/28-reliability/resilience-readiness.md", "docs/29-incident-bcdr/incident-readiness.md", "docs/31-observability/slo-sla-definitions.md", "docs/32-finops/optimization-backlog.md", "docs/34-measure-after/after-intervention-kpi-sheet.md", "docs/35-variance/corrective-action-backlog.md", "docs/36-roi/payback-analysis.md", "docs/37-operating-model/operating-contract-closure.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. PROPOSAL. Every item is PROPOSED: none is started, approved or accepted. No effort, cost, date or headcount is estimated (none exists: OB-04, Stage 32). No value claim, no cutover scheduled, no risk accepted for Dinesh Naik.**

## Summary
Forty backlog items in eight workstreams. Priority P1 = unlocks a gate; P2 = produces evidence needed for the value case (slots I-01..I-14) or for reuse; P3 = prepares later steps. Ordering is by gate and dependency (`90-day-roadmap.md`), then by evidence value, then by readiness. **Owner is a role**: Dinesh Naik is the only named person (Engagement lead); every other role is Unknown/TBD/VACANT. "Orchestrator (agent)" is the automated runner under OD-23 and holds no approval right. Sizes are intentionally absent.

## Findings
Gate key: G0 decisions closed; G1 fit to pilot; G2 pilot exit / limited entry; G3 limited exit / broader entry (defined in `90-day-roadmap.md`).

### W0 Decide
| ID | Item | Type | Source (open item) | Gate | Pri | Owner role | Depends on | Exit evidence |
|---|---|---|---|---|---|---|---|---|
| SB-01 | Record whether this roadmap is adopted as a proposal, and what D+0 means (relative anchor, not a date) | Decision | this stage | G0 | P1 | Engagement lead (Dinesh Naik) | none | OD entry |
| SB-02 | Disposition (fix / accept-open / defer / route) for every open list: D-27-01..09, D-28-01..10, D-31-01..10, D-34-01..08, Q-29-01..09 and C-1..C-7, Stage 32 items, CA-01..17, I-01..19 / PC-1..10, VA-01..07, GD-06/07/10/15; 'accepted open' is a legitimate answer | Decision | OD-33..OD-36 | G0 | P1 | Engagement lead (Dinesh Naik) | SB-01 | Disposition table; unresolved ones become gate constraints |
| SB-03 | Confirm, edit or strike adjacent candidates AU-01..AU-07; say whether any real sponsor exists | Decision | `adjacent-use-case-inventory.md` U-40-07 | G0 | P2 | Engagement lead (Dinesh Naik) | SB-01 | Edited inventory v0.2 |
| SB-04 | Name real Zone H holders, or declare Zone H unused (holders stay EMPTY otherwise) | Decision | PC-2, OD-17, OD-31 | G1 | P1 | Engagement lead (Dinesh Naik); holders are outside the engagement (SH-15) | SB-02 | Recorded decision |
| SB-05 | Steady-state owners: who, if anyone, accepts RL-02 service, RL-05 risk/security, RL-06 compliance, RL-07 data, RL-08 integration, RL-10 legacy, RL-11 reviewers; or record single-approver explicitly (acceptance is Dinesh's alone) | Decision | PC-3, DQ-17, OD-34 | G1 | P1 | Engagement lead (Dinesh Naik) | SB-02 | Ownership state per asset moves off VACANT or is accepted-open |
| SB-06 | Process owner for closed / resolved / approved / 48 h definitions (OPD-01..03) and rule-set owner | Decision | PC-4, OD-16 | G1 | P1 | Engagement lead (Dinesh Naik) / RL-03 VACANT | SB-02 | Definitions adopted, or 'accepted open' recorded with its effect on KPIs |
| SB-07 | Cost owner and finance partner (RL-09); finance-approved rate and discount rate (only if value is to be quantified) | Decision | PC-9, I-10, RL-09 | G2 | P2 | Engagement lead (Dinesh Naik) / Finance partner VACANT | SB-02 | Owner named, or economics remain 'not computable' |
| SB-08 | Python floor: decide 3.12+ production floor and keep 3.10 test floor, or other | Decision | D-27-02, OD-24 | G1 | P1 | Engagement lead (Dinesh Naik) | none | Recorded decision |
| SB-09 | Merge and read Stage 39 (drift); re-issue this roadmap as v0.2 if it changes findings | Evidence | U-40-09 | G0 | P1 | Orchestrator (agent); Dinesh reviews | Stage 39 merged | Roadmap v0.2 or 'no change' note |
| SB-10 | Record Stage 30 outcome and Dinesh's cutover decision (this roadmap schedules neither) | Decision | PRE-17 | G1 | P1 | Engagement lead (Dinesh Naik) | Stage 30 | Recorded, whichever way |

### W1 Verification
| ID | Item | Type | Source | Gate | Pri | Owner role | Depends on | Exit evidence |
|---|---|---|---|---|---|---|---|---|
| SB-11 | Perform and sign walkthroughs TST-REV-03/04/08, or record them as left open | Verification | RTR-07, OD-24 | G1 | P1 | Engagement lead (Dinesh Naik); a reviewer role VACANT | none | Signed `walkthrough-records.md` or open decision |
| SB-12 | Full hub regression on Python 3.12+/3.13 at the then-current HEAD, record RT-14 | Verification | RTR-08, U-27-01 | G1 | P1 | Orchestrator (agent) | SB-08 | Run record with checksum gate |
| SB-13 | Install CI gate from `ci/hub-hardening.yml` under `.github` with SHA pins (needs HAR-07 approval) | Change | PR-30, PR-31, D-27-03 | G1 | P1 | Engagement lead (Dinesh Naik) approves; toolchain owner RL-12 interim | SB-02 | Workflow running; or decision to leave uninstalled |
| SB-14 | TEVV delta run after any wiring/behaviour change; re-score thresholds RT-01..RT-15 | Verification | `tevv-release-gate.md` GT-3 | G1 | P1 | Orchestrator (agent) | SB-16..SB-18 | TEVV v0.2 results |
| SB-15 | Decide on a human adversary / external penetration test and real-browser testing, or accept limitation (acceptance is Dinesh's) | Decision | RTR-14, D-24 | G1 | P2 | Engagement lead (Dinesh Naik) | SB-02 | Decision |

### W2 Hardening and wiring
| ID | Item | Type | Source | Gate | Pri | Owner role | Depends on | Exit evidence |
|---|---|---|---|---|---|---|---|---|
| SB-16 | Wire `GuardedGateway` and `BoundedLoopbackServer`, or record 'not used' (D-28-01, D-28-02); persist breaker state; add metrics | Build | PC-8, S28-DEV-01 | G1 | P1 | Build agent under Engagement lead (Dinesh Naik) decision | SB-02 | Wired path re-injected (FI-xx re-run) |
| SB-17 | Wire observability; decide SLO candidates SLO-01..05; close SLI gaps for SLO-04, SLO-05 | Build / Decision | D-31-01..10, F-31-01..07 | G1 | P2 | Engagement lead (Dinesh Naik) | SB-16 | Wired metrics; SLOs adopted or left as candidates |
| SB-18 | Fix F-29-01 (`verify-audit` KeyError); route F-29-02..16, F-31-01..07, F-11 and the 9 complex functions | Build | OD-35, OD-34 | G1 | P1 | Build agent under Engagement lead (Dinesh Naik) | SB-02 | Fix + test; remaining items dispositioned |
| SB-19 | Off-device backup (HAR-09) and a restore drill with timing; live tabletop with a human participant | Verification | PR-25, Q-29-01..09, C-1..C-7 | G1 | P1 | Engagement lead (Dinesh Naik); host owner Unknown | SB-02 | Drill record; RTO/RPO targets confirmed or left as agent targets |
| SB-20 | Exposure posture: stay loopback-only for the pilot, or approve TLS / second factor / token expiry before any wider bind | Decision | D-27-09, RS-01, RS-02, RS-08 | G1 | P1 | Engagement lead (Dinesh Naik) | SB-02 | Decision; if wider, PR-06/07/14 MET |
| SB-21 | Data decisions before real data: field classes, tenant, regime, retention rule | Decision | DQ-S24, OD-S12-09, GD-07 | G1 | P1 | Engagement lead (Dinesh Naik); RL-05/06/07 VACANT | SB-02 | Recorded decisions |

### W3 Operating model
| ID | Item | Type | Source | Gate | Pri | Owner role | Depends on | Exit evidence |
|---|---|---|---|---|---|---|---|---|
| SB-31 | Who answers the pilot: support tier, escalation, incident severity routing in practice (Stage 37 support model, Stage 29 playbook); if nobody exists, the pilot cannot start | Decision | `support-model.md`, `escalation-model.md` | G1 | P1 | Engagement lead (Dinesh Naik); service owner RL-02 VACANT | SB-05 | Named responder or recorded gap |
| SB-32 | Who runs orchestrator duties after Stage 38 (regression, merge gate) | Decision | OD-34 | G1 | P1 | Engagement lead (Dinesh Naik) | none | Recorded |

### W4 Measurement and value
| ID | Item | Type | Source | Gate | Pri | Owner role | Depends on | Exit evidence |
|---|---|---|---|---|---|---|---|---|
| SB-26 | Raise Stage 4 v0.2 addendum; decide `as_of` parameter for metrics | Decision | D-34-03, D-34-04, PC-6 | G1 | P2 | Engagement lead (Dinesh Naik) | SB-02 | Addendum signed or amended |
| SB-27 | Define the after-window: start (relative to pilot), exposure (which units), minimum duration, data owner | Decision | D-34-02, PC-1 | G1 | P1 | Engagement lead (Dinesh Naik) | SB-05, SB-06 | Recorded definition |
| SB-28 | Time and effort capture design (CA-06, K-22, OB-04/05) | Design | CA-06 | G1 | P2 | Engagement lead (Dinesh Naik) | SB-27 | Capture method in place |
| SB-29 | Cost inputs: toolchain charges, hosting, effort, cost owner; request finance-approved rate | Evidence | OB-02..OB-04, OB-07, I-14, I-10 | G2 | P2 | Engagement lead (Dinesh Naik) / Finance partner VACANT | SB-07 | Filled `cost-model.md` terms |
| SB-30 | Re-run Stages 34, 35 and 36 as v0.2 when an after-window completes | Evidence | OD-36 | G2 | P1 | Orchestrator (agent); Dinesh reviews | SB-27, pilot window | v0.2 documents |

### W5 Reuse packaging
| ID | Item | Type | Source | Gate | Pri | Owner role | Depends on | Exit evidence |
|---|---|---|---|---|---|---|---|---|
| SB-22 | Write the per-source contract template and source-onboarding checklist (AP-04); write contracts for pilot sources | Design | OD-28, AP-04 | G1 | P2 | Integration owner RL-08 VACANT; Dinesh interim | SB-02 | Template + contracts |
| SB-23 | Generalise AP-01..AP-03 (guards, store/audit, runner) once SB-18 closes | Build | RC-01..03 | G2 | P2 | Build agent under Dinesh | SB-18, SB-12 | Pack manifest items 'PACKAGED' |
| SB-24 | Generalise the TEVV kit and readiness scorecard (AP-05, AP-06) | Design | RC-19, RC-20 | G2 | P3 | Build agent under Dinesh | SB-14 | Kit v0.2 |
| SB-25 | First reuse trial: apply one tier-A accelerator to a second unit in a sandbox; record as E2, never as E3 until a real second unit runs | Verification | RRF-1 | G2 | P2 | Engagement lead (Dinesh Naik) | SB-23 | Trial record |

### W6 Adjacent preparation (no build before G2)
| ID | Item | Type | Source | Gate | Pri | Owner role | Depends on | Exit evidence |
|---|---|---|---|---|---|---|---|---|
| SB-33 | AU-01 readiness pack: site inventory, local rule owner, regime, local reviewers | Design | AU-01 | G3 | P2 | Site owner Unknown; Dinesh interim | G2 | Pack |
| SB-34 | AU-02 per-feed contract, source owner, late-delivery handling (D-28-04) | Design | AU-02 | G3 | P2 | RL-08 VACANT | SB-22, G2 | Contract per feed |
| SB-35 | AU-03 finance field classes and owner decision (no build) | Decision | AU-03 | G3 | P3 | RL-09 VACANT | SB-07, SB-21 | Decision |
| SB-36 | AU-04 scoping decision (reverse EX-06 or keep it excluded) | Decision | EX-06 | G3 | P3 | Engagement lead (Dinesh Naik) | SB-03 | Decision |

### W7 Governance
| ID | Item | Type | Source | Gate | Pri | Owner role | Depends on | Exit evidence |
|---|---|---|---|---|---|---|---|---|
| SB-37 | Adopt (or amend) the scale gate rules in `scale-governance.md` as recorded decisions | Decision | SG-1 | G0 | P1 | Engagement lead (Dinesh Naik) | SB-01 | OD entry |
| SB-38 | Decide whether to add SR-01..SR-16 to the risk register; route each (accept / fix / defer) | Decision | `scale-risk-assessment.md` | G0 | P1 | Engagement lead (Dinesh Naik) | SB-37 | Register entries |
| SB-39 | Re-issue triggers handled: Stage 39, Stage 30, Stage 38, each completed after-window | Governance | SG-7 | all | P2 | Orchestrator (agent) | events | Version log |
| SB-40 | Non-carry checklist (RC-4 X-01..X-11) run for every new unit as an entry criterion | Governance | SR-04 | G1 (pilot unit), G3 (each later unit) | P1 | Engagement lead (Dinesh Naik) | SB-37 | Checklist per unit |

**Count [Verified Fact: rows above]:** 40 items (SB-01..SB-40; rows are grouped by workstream, not numerically). P1 = 24; P2 = 13; P3 = 3.

## Evidence References
Per-row source column.

## Assumptions
- A-40-10 [Assumption] Gate assignment per item is the agent's sequencing. Confirm: Engagement lead (Dinesh Naik).
- A-40-11 [Assumption] Build items continue under the existing OD-01/OD-13 mechanism (branch, PR, squash-merge by the orchestrator).

## Unknowns
- U-40-05 Effort per item (no data).
- U-40-13 Whether any non-Dinesh human can take any W0/W3 item.

## Unresolved Issues
- Items depending on Stage 30, Stage 38, Stage 39 outputs cannot be finalised until those land.

## Residual Risks
- A backlog with 24 P1 items and one decider (SR-06): sequencing, not parallel execution, is the mitigation.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue |
