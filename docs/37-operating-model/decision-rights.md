---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "decision-rights.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/02-stakeholders/{decision-rights-map,approval-authority-map}.md", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md HAR-01..HAR-16", "docs/25-governance/governance-model.md GM-2, GM-3", "docs/23-human-control/{approval-gates,human-override-policy,autonomy-matrix}.md", ".fde/orchestrator-decisions.md OD-01..OD-33"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
Steady-state decision rights, built on the Stage 2 map (DR-01..DR-31) and the Stage 25 tiers (T0..T4). Two things are kept apart: (1) **decision rights exercised during the engagement**, which are evidenced and "ACCEPTED-IN-EFFECT" because Dinesh Naik answered or approved them in the OD log; and (2) **steady-state decision rights**, which are *proposed* here and are PROPOSED until Dinesh records them. **Default-answer authority (OD-32) covers scope and sequencing only; it does not cover accepting risks, naming real Zone H holders or stakeholders, approving cutover, or any irreversible step.** No new right is granted to any agent.

## Findings
### DRT-1 Engagement-phase rights (evidenced, closed at Stage 38)
| ID | Decision | Decider | State | Evidence |
|---|---|---|---|---|
| DRT-01 | Run order, stop-only-on-BLOCKED, merge after review | Dinesh | ACCEPTED-IN-EFFECT | OD-01, OD-13 |
| DRT-02 | No fabrication; no real stakeholders exist | Dinesh | ACCEPTED-IN-EFFECT | OD-04 |
| DRT-03 | AI vs No-AI | Dinesh | ACCEPTED-IN-EFFECT | OD-08 |
| DRT-04 | PRD baseline, implementation baseline, delivery plan | Dinesh | ACCEPTED-IN-EFFECT | OD-22, OD-25, OD-26 |
| DRT-05 | Authority switch by CLI + `approval_ref`; Zone H holders stay empty | Dinesh | ACCEPTED-IN-EFFECT | OD-31 |
| DRT-06 | Scope/sequencing choices at recommended defaults (assumptions, not risk acceptance) | Orchestrator under Dinesh's standing instruction | ACCEPTED-IN-EFFECT (limited) | OD-32 |
| DRT-07 | Test-once, cloud regression, parallel doc stages | Orchestrator under Dinesh's approval | ACCEPTED-IN-EFFECT | OD-23 |
| DRT-08 | Single-approver risk (DQ-17) | Dinesh, as a general risk | ACCEPTED in OD-30 as general risk; **not** a Stage 37 acceptance | OD-30 |

### DRT-2 Proposed steady-state decision rights
Decider = role. "Holder" shows who could decide today. Reversibility is Inference.

| ID | Decision | Tier | Decider role | Must consult | Holder today | Reversible? | Evidence of need |
|---|---|---|---|---|---|---|---|
| SDR-01 | Merge/release a code change | T1 | RL-02 Service owner | RL-05, RL-13 | Dinesh (INTERIM) | Yes (revert) | OD-13 |
| SDR-02 | Move a decision flag off its safe default | T2 | RL-03 Process owner, with `approval_ref` | RL-02, RL-05, RL-06 | VACANT; Dinesh decides OD-S12-xx | Yes | DW-17; `feature-flag-plan.md` |
| SDR-03 | Activate a rule set / adopt or withdraw a policy / change mode / enable schedule | T3 | RL-04 Zone H holder | RL-03, RL-06 | **VACANT**; refused by default | Partly (withdrawal is audited, ZH-10) | AP-4; ZH-01..ZH-10 |
| SDR-04 | Batch disposition, QA release, e-signature | T3 | Authorised dispositioner (RL-04 / SH-15), never an agent or the engagement | RL-06 | **VACANT** | No (regulatory effect) | HAR-12; STOP-07; DR-22 |
| SDR-05 | Accept a risk | T0 | RL-01 only | RL-05, RL-06 | Dinesh | n/a | AP-7 |
| SDR-06 | Preserve-or-fix a deviation DV-xx | T2 | RL-01 (HAR-06) on advice of RL-03, RL-08 | RL-06 | Dinesh | Yes until cutover | AP-3 |
| SDR-07 | Expose beyond loopback; enable TLS; issue service tokens | T0 | RL-01 with RL-05 (HAR-05) | RL-02 | Dinesh | Yes | AP-6; RS-01, RS-08 |
| SDR-08 | Cutover step CUT-1..CUT-5 go/no-go | T0 | RL-01 (HAR-11) | RL-03, RL-09 (CUT-4), RL-06, RL-04 | Dinesh | Per step (see `rollback-strategy.md`) | AP-5; RB-4 |
| SDR-09 | Retention/disposal rule | T2 | RL-05 with RL-06 | RL-07 | **VACANT**; hold-all | No (deletion) | OD-30; DR-24 |
| SDR-10 | Real data enters the system; privacy regime; field classes; tenant | T0 | RL-01 with RL-05 | RL-06, RL-07 | Dinesh; STOP-04 on real data | No | OD-32 (decided before real data); RS-06 |
| SDR-11 | Closed/resolved/48 h definitions | T2 | RL-03 | RL-06, RL-09 | **VACANT** (SH-03/09/05 disagree: DR-20) | Yes | OPD-01..03 |
| SDR-12 | Source-contract enforce vs record_only; schema_version list | T2 | RL-08 | RL-03, RL-07 | **VACANT**; record_only | Yes | OD-28 |
| SDR-13 | Add a vendor / third-party dependency | T0 | RL-01 with RL-05 (ADR + decision) | RL-09, RL-06 | Dinesh | Yes | VA-07; DM-08 |
| SDR-14 | Introduce AI / re-qualify | T0 | RL-01 (new decision) + HAR-08/09/10 | RL-05, RL-06, RL-09 | Dinesh | Yes | OD-08; RQ-1..RQ-3 |
| SDR-15 | Gate status of an engagement stage | T4 | Stage agent proposes; orchestrator accepts; RL-01 overrides | - | as today | Yes | TP-13; DR-12 |
| SDR-16 | Close the engagement contract | T0 | RL-01 | all | Dinesh | Yes (reopen by new record) | `operating-contract-closure.md` |

### DRT-3 Rules for exercising a right
1. A right is exercised only by the named role. An agent may *prepare* a decision; it may never record itself as the decider (TP-14, AG-5, HAR-11).
2. Where the role is VACANT the decision is **not made**; it is "accepted open" with the safe default shipping (OD-12, OD-22). Dinesh's interim presence does not convert a VACANT-role decision into a made one unless he records it.
3. Irreversible or regulatory acts (SDR-04, SDR-09, SDR-10) have no delegation path.
4. Every exercised right leaves a record: OD entry, `approval_ref`, or audited Zone H event.

### DRT-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| DF-01 | [Verified Fact] Of 16 proposed steady-state rights, 6 have a VACANT decider role (SDR-02..04, 09, 11, 12) | DRT-2 | Decisions stay open by design | High (real use) | High | Fill or keep "accepted open" |
| DF-02 | [Verified Fact] Rights T0 (SDR-05, 07, 08, 10, 13, 14, 16) all rest on Dinesh | DRT-2 | Single point of decision | Medium-High | High | Alternate/second reviewer (ES-09, DQ-17) |
| DF-03 | [Inference] SDR-02 (flag moves) is the practical gate for every product behaviour; it works only because Dinesh is the decider | DW-17 | A real owner must take it before activation | Medium | Medium | Who is the process owner? |

## Evidence References
See `evidence_sources`; `decision-rights-map.md` DR-01..DR-31 are preserved unchanged and referenced, not superseded.

## Assumptions
- A-37-DR-1 [Assumption] The SDR table is a proposal; none of SDR-01..SDR-16 is approved. Confirm: Engagement lead (Dinesh Naik).
- A-37-DR-2 [Assumption] Reversibility ratings are agent Inference. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-37-DR-1 Whether a client change board or quality unit would hold SDR-01, 02, 06.
- U-37-DR-2 Statutory or contractual decision rights in a real GxP context (no legal review; LR-1..LR-4 flagged).

## Unresolved Issues
- Holders for RL-03, RL-04, RL-05, RL-08; second reviewer (DQ-17).

## Residual Risks
- RR-37-DR-1 A decision recorded by Dinesh in a VACANT role is mistaken for a role-holder decision (Low; rule 2 above).
- RR-37-DR-2 Decision latency at single decider (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
