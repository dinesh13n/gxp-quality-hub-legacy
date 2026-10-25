---
stage: "40 — Scale / 90-Day Transformation Roadmap"
artifact: "scale-governance.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 40 run)"
status: "DRAFT"
evidence_sources: ["docs/25-governance/governance-model.md", "docs/25-governance/risk-acceptance-register.md", "docs/23-human-control/", "docs/37-operating-model/{decision-rights,raci,change-governance,escalation-model}.md", "docs/29-incident-bcdr/incident-severity-matrix.md", "docs/17-implementation-prd/release-boundaries.md", "docs/40-scale/90-day-roadmap.md", "docs/40-scale/scale-risk-assessment.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-30..OD-36)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. PROPOSAL: these rules take effect only if Dinesh Naik adopts them (SB-37). They accept no risk, name no stakeholder other than Dinesh, imply no proven value (Stage 36: ROI NOT COMPUTABLE) and schedule no cutover.**

## Summary
Governance for scaled assets, preserved from the first use case and extended with rules for moving between scale steps. Principle: **nothing widens by default; every step up is a recorded human decision against pre-declared criteria; every consequential switch ships off; a breach stops scaling.** Twelve rules (SG-1..SG-12). The model has one real decider (Dinesh Naik), so most rules are gates he operates; roles that would share them are VACANT.

## Findings
### SG-1 Gate rule [Inference: extends PT-08]
A scale step needs (a) pre-declared criteria (`90-day-roadmap.md` RM-5), (b) evidence per criterion, (c) a recorded decision by the Engagement lead. Gate outcomes: PASS (all criteria met), CONDITIONAL (HARD criteria met; SOFT ones accepted-open with stated effect), HOLD (a HARD criterion unmet). Criteria are not edited after results are seen; changes are made as a new version with the reason (as TH-3 in Stage 26).

### SG-2 Decision rights [Verified Fact: inherited]
| Decision | Who decides | Source |
|---|---|---|
| Any gate outcome, any step up, any risk acceptance, any role-holder or Zone H holder naming, any cutover | Engagement lead (Dinesh Naik) only | OP-A, HAR-11, TP-14, OD-32 |
| Disposition, QA release, e-signature | An authorised human outside the engagement; no component simulates it | HAR-12, STOP-07, OP-B |
| Proposals, evidence, regression runs, documents | Agent roles; no approval right | OD-13, OD-23 |
Owners of record in this file are roles; all are VACANT except Dinesh (interim, not an accepted steady-state assignment, TOM-2).

### SG-3 Release rule for reused assets [Inference]
A component or accelerator moves to a new unit only if: it is tier A or B in `reusable-components.md`; its listed conditions are closed or accepted-open by Dinesh; it is not on the exclusion list (RC-4 X-01..X-11); and a post-reuse check passes (its own regression group plus the TEVV delta). A reuse that passes is recorded as E2 (sandbox) or E3 (real second unit); labels are never upgraded without that record.

### SG-4 Change control for scaled assets [Verified Fact: controls exist; Inference: apply to every unit]
Each of the following needs a recorded human decision with an `approval_ref` and ships OFF for every new unit (PT-03, PT-05):
rule-set activation (RC-04); Zone H holders and disposition mode (RC-08); source contract `enforce` (RC-05); scheduler on (RC-11); exposure beyond loopback (RC-09); making any capability authoritative (DW-17); retention purge (OD-S12-09); search / templates on (RC-16); changing a security value (DQ-09); introducing any model (OD-08, HAR-08/09/10). The CI file, Dockerfile and environment profiles need HAR-07 approval.

### SG-5 Claims and evidence rules [Verified Fact: Stage 40 and OD-30/OD-36]
- Every statement carries one of Verified Fact / Inference / Assumption / Unknown.
- No document may state ROI, NPV, payback, saving or benefit unless Stage 36 inputs are filled with measured production values under signed definitions and a finance-approved rate (RM-3 of `roi-model.md`). Until then the wording is "unproven / not computable".
- No "compliant" language; Part 11 stays at framing (GD-11).
- Parity is not improvement; a sandbox value is not a production value (Stage 35).
- Stage 42 and FINAL must carry "economic value: unproven" from Stage 36 unless a v0.2 changes it (BSF-3).

### SG-6 Stop and rollback conditions [Inference: proposed; thresholds are zero-tolerance invariants already in the repository]
Scaling halts and the previous step is restored when any of these occurs. Resumption is Dinesh's decision.
| Condition | Source | Immediate response |
|---|---|---|
| `model_calls_total` > 0 or `egress_attempts_total` > 0 | INV-01, INV-02, `hub/guards/` | SEV-A/B per incident matrix; switch off the unit's intake |
| A service actor passes the Zone H gate | INV-03, FR-GATE-03 | stop; investigate; holders unchanged |
| Audit chain fails `verify-audit` | RT-12, `E-DEC-CHAIN-BROKEN` | stop writes for the unit; forensics policy (Stage 29) |
| Legacy or `data/` checksum differs | TST-CO-05, OD-03a | stop; restore from backup; verify checksums |
| An authority switch used without an `approval_ref` | DW-17 | switch back OFF; record |
| A SEV-A/B incident without a named responder | Stage 29 matrix; SB-31 | stop until a responder exists |
Rollback of a capability is switching it off (each capability is independently revertible, `cutover-plan.md`); restoring data uses the checksum-gated backup pattern. Neither is rehearsed off-device yet (SB-19).

### SG-7 Re-issue triggers for this stage [Verified Fact: dependencies]
Re-issue Stage 40 (v0.2) when: Stage 39 (drift) is merged (an input listed by the stage prompt, absent at `ef72e4e`); Stage 30 or Stage 38 completes; a Stage 34/35/36 v0.2 appears; any HARD criterion changes class; Dinesh answers SB-02; or a second unit actually runs (first E3). Prior versions are preserved (no silent overwrite).

### SG-8 Roles for scale governance [Verified Fact: roles from TOM-4; holders VACANT except Dinesh]
| Role | Scale duty | Holder |
|---|---|---|
| RL-01 Engagement owner | all gates, risk acceptance, approvals | Dinesh Naik (interim) |
| RL-02 Service owner | go-live readiness of each unit, release, tier-3 support | VACANT |
| RL-03 Product/process owner | definitions, rule content, review practice per unit | VACANT |
| RL-04 Authorised dispositioner | Zone H actions | VACANT; outside the engagement |
| RL-05 / RL-06 Risk-security / compliance | exposure, data, retention, evidence before closure | VACANT |
| RL-07 / RL-08 Data / integration owners | per-unit data, per-source contract | VACANT |
| RL-09 Finance / cost | cost model, rate cards | VACANT |
| RL-11 Reviewers | pilot users | VACANT |
| RL-12 Toolchain owner | CI, workspaces, runner | Dinesh interim |
A scale step cannot rely on a VACANT role for a duty unless Dinesh records the gap as accepted-open.

### SG-9 Risk handling [Verified Fact]
RS-01..16, RP-01..12, VA-01..07, RTR-01..15, F-xx remain open, none accepted. SR-01..SR-16 are proposed additions. The agent proposes routing (accept / fix / defer); Dinesh decides (SB-02, SB-38).

### SG-10 Cadence [Assumption]
Proposed review points, in relative days: gate reviews at the end of each phase (D+14, D+45, end of pilot window, D+90); during the pilot window a daily automated check (tripwires, chain verify, checksum) reported to Dinesh and a weekly review. No other forum exists to hold them (OD-04).

### SG-11 Governance preserved from the first use case [Verified Fact]
No-AI product and tripwires (OD-08); human control zones and the authority switch (Stage 23); single approver (DQ-17 answered 'accept the single-approver risk' for the engagement, OD-30; RP-01 still open; to be re-decided for a scaled footprint); permission matrix TP-01..TP-15 confirmed for the engagement only and to be re-confirmed if reused (AGF-04); Part 11 framing only (GD-11); honest labelling of every metric (PNFR-20); sandbox-copy execution and checksum gating (OD-03a).

### SG-12 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| SGF-1 | [Verified Fact] Governance rests on one person; scaling multiplies decisions without adding deciders | OD-04, TOM-1 | Decision capacity caps pace | High | High | Second approver (PC-3) |
| SGF-2 | [Verified Fact] The stop invariants already exist as metrics, but observability is not wired | SLO doc INV-01..03; D-31 | Stop conditions detected by tests, not by running telemetry | Medium | High | SB-17 |
| SGF-3 | [Inference] TP-01..TP-15 and OD-31 approvals were given for the engagement, so scale to real users needs them re-confirmed | AGF-04 | Reconfirmation is a G1 task | Medium | Medium | SB-02 |

## Evidence References
See `evidence_sources`.

## Assumptions
- A-40-15 Cadence in SG-10. Confirm: Engagement lead (Dinesh Naik).
- A-40-16 Stop-condition set in SG-6 is complete enough; add conditions as units are added. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-40-17 Whether any of these rules conflict with a client governance framework (none exists in the repo).

## Unresolved Issues
- Adoption of these rules (SB-37) is itself a pending decision.

## Residual Risks
- SR-06, SR-07 (single decider, vacant ownership) apply to this governance as written.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue |
