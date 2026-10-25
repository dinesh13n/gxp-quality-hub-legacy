---
stage: "35 — Before-vs-After Variance + Value Leakage"
artifact: "corrective-action-backlog.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 35 run)"
status: "DRAFT"
evidence_sources: ["docs/35-variance/value-leakage-analysis.md", "docs/35-variance/confounder-analysis.md", "docs/34-measure-after/after-intervention-kpi-sheet.md section E", "docs/37-operating-model/raci.md", ".fde/orchestrator-decisions.md (OD-04, OD-32, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 35 adds files under `docs/35-variance/` and changes nothing else). No production after-data exists: the hub is not in production, there is no production telemetry, Stage 30 has not run and Stage 31 is not merged. Every 'after' figure is a Stage 34 SANDBOX measurement on the 125-case synthetic baseline (seed 4100) or an earlier stage's test result. Where a like-for-like pair exists it is labelled 'synthetic, sandbox, parity - not an improvement'. No improvement, saving, benefit or ROI is claimed, no number is invented, no stakeholder is invented, and no risk is accepted on Dinesh's behalf (OD-04, OD-32, HAR-11).**

## Summary
Corrective actions that would reduce leakage or make a future before-vs-after valid. **Every action is a PROPOSAL.** Anything that changes a control, definition, rule set, owner, cost commitment or production state needs Dinesh's recorded decision through the controlled change process (OD-32: default-answer authority does not cover accepting risks, naming holders, approving cutover or irreversible steps). Owner of every item: Engagement lead (Dinesh Naik). Due: 'before any pilot or production use' (no calendar date exists; same convention as Stage 34).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CB-1 Backlog
Priority (agent Inference): P1 prerequisite to any valid after-measurement; P2 reduces leakage; P3 housekeeping.

| ID | Action | Closes | Type | Needs Dinesh decision? | Priority | Link |
|---|---|---|---|---|---|---|
| CA-01 | Define the real after-window: start date, exposure (cases/sites), minimum duration, data owner; supply production measurements listed in Stage 34 PP-1/AD-2 | VL-01, CNF-01, U-35-01 | Decision + data | Yes | P1 | D-34-02 |
| CA-02 | Confirm the hub is not in production and no pilot has happened | A-34-02, BA-F1 | Confirmation | Yes | P1 | D-34-01 |
| CA-03 | Add an `as_of` parameter to hub metrics so ageing can be compared at 2025-12-19T07:11Z (code change, Stage 30/hardening scope) | VL-12, CNF-06 | Code change (change process) | Yes | P1 | D-34-03 |
| CA-04 | Design the pilot with a comparison: unexposed cases/sites or stable pre-trend, pre-registered KPIs, no concurrent behaviour changes during the window | CNF-09, CNF-13 | Plan | Yes | P1 | new |
| CA-05 | Raise the Stage 4 v0.2 addendum (A-04-01 refutation; reference-time rule; separate KPI ids for hub K-09U/K-06) and sign or amend the freeze | VL-13, CNF-05, CNF-12 | Change record | Yes | P1 | D-34-04 |
| CA-06 | Add time capture (closure, evidence-complete, reviewer effort) so K-04, K-05, K-22 become measurable | VL-11 | Design/build (Stage 30/31) | Yes | P1 | new |
| CA-07 | Decide who decides closed/resolved (DR-20/21) and adopt or reject candidate policy `D-OPS@1`; define D-FIN or declare it out of scope | VL-10, CNF-08 | Decision | Yes | P1 | OPD-01..03 |
| CA-08 | Name accepted owners for the 28 assets and the vacant roles, or record a waiver; appoint a second reviewer or record the single-approver design as accepted by Dinesh | VL-06, VL-07, ADL-4 | Decision | Yes | P2 | OD-34, DQ-17 |
| CA-09 | Name real Zone H holders, or record that Zone H stays unused | VL-02 | Decision | Yes | P2 | OD-31 |
| CA-10 | Decide on wiring Stage 28 mechanisms into the serve path and installing `ci/hub-hardening.yml` (HAR-07) | VL-04, VL-05, ADL-6 | Decision + change | Yes | P2 | D-28-xx, HAR-07 |
| CA-11 | Obtain human sign-off of TST-REV-03/04/08 | VL-08 | Human test | Yes (a human must do it) | P2 | OD-33 |
| CA-12 | Define a parallel-run/coexistence plan so reviewers do not do the work twice; define an override/acceptance KPI as a new id if wanted | VL-14, ADL-2 | Plan | Yes | P2 | D-34-06 |
| CA-13 | Supply 0C inputs C-1..C-5 (volumes, rate, cost per case), actual or estimated build effort, toolchain plans, hosting decision; appoint cost owner RL-09 | CLK-5..CLK-9, BNV-1 | Inputs | Yes | P2 | Stage 32 |
| CA-14 | Route open registers (RS-01..16, RP-01..12, VA-01..07, RTR-01..15, F-11, 9 complex functions) to accept / fix / defer decisions | VL-09 | Risk decisions | Yes (acceptance is Dinesh only) | P2 | OD-33..35 |
| CA-15 | Label 0C S3/S4 cost files as AI-option-only (edit outside this docs-only stage) | CLK-2 | Doc edit | Yes | P3 | OB-09 |
| CA-16 | Investigate the 5-row K-06 gap (173 vs 168) and legacy replay safety (K-07 before) in a sandbox | U-34-02, U-34-03 | Investigation | No (read-only sandbox) | P3 | Stage 34 |
| CA-17 | Re-run Stage 34, then Stage 35, after Stage 30/31 and a real window exist | all | Re-measure | Yes (trigger) | P1 | D-34-07 |

### CB-2 Sequencing [Inference]
CA-02 and CA-01 first (they decide whether any production variance can ever exist); CA-05, CA-07 and CA-03 fix the yardstick; CA-06 and CA-04 make attribution possible; CA-08..CA-14 reduce leakage; CA-17 closes the loop.

### CB-3 What this backlog does not do
It does not accept any risk, change any control or definition, choose any owner, or claim any saving from completing an action.

## Evidence References
`docs/35-variance/*`; `docs/34-measure-after/after-intervention-kpi-sheet.md` section E (D-34-01..08); OD-30..OD-35.

## Assumptions
- A-35-01 [Assumption] Artifact directory is `docs/35-variance/` as instructed by the orchestrator, not `docs/35-value-leakage/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-35-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (variance only on Stage 34 C1 rows; leakage traced to repository findings; corrective actions are proposals). It does not accept any risk. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-35-14 Effort and cost of each action (not estimated; no rate exists).

## Unresolved Issues
- All actions are open; none started.

## Residual Risks
- RR-35-15 Backlog read as approved work. Status of every item is PROPOSED.
- RR-35-16 Doing P2 items before P1 yields leakage fixes with no way to measure them.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 35). |
