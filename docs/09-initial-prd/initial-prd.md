---
stage: "9 — Initial PRD / Product Intent"
artifact: "initial-prd.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/success-criteria.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/08-ai-qualification/qualification-decision.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/03-problem-value/problem-statement.md", "docs/03-problem-value/personas.md", "docs/03-problem-value/user-journeys.md", "docs/03-problem-value/jobs-to-be-done.md", "docs/03-problem-value/scope-exclusions.md", "docs/02-stakeholders/decision-rights-map.md", "docs/07-repo-assessment/repo-transformation-readiness.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Approval of this PRD is Dinesh Naik's decision (HAR-11); nothing here is an approval.**

**Product intent.** Give the people who review, close, fund and audit pharma batch-deviation / CAPA cases (Gxp Group, fictional) a single, attributable record of each case and its decisions, safe handling of externally received case information, and figures that declare their own definitions, so that the organisation can see the same case and the same numbers - while the human approval for batch disposition stays exactly where it is, with a human. The product is **No-AI** (OD-08): rules, keyword/field search, templates and a deterministic core. Where the organisation has not decided something (what "closed" means, whether 48 h is right, who owns approval-rule conflicts, where disposition is recorded), the product carries a **configurable policy mechanism and an explicit open decision, not a guess**.

**Shape.** 10 capabilities, 52 functional requirements (43 MVP/R1, 9 R2) and 20 NFRs; 16 open product decisions (OPD-01..16) of which three (OPD-01..03) are recorded as accepted open and the rest are open; 15 non-goals; 7 release hypotheses. This is the **INITIAL PRD (v0.1, DRAFT)**. Stage 17 will finalise the implementation PRD; FINAL will disposition every requirement ID here (Delivered / Changed / Deferred / Rejected / Superseded).

## Findings
### PRD-1 Problem (frozen from Stage 3) [Inference; synthetic, unvalidated]
> Case-handling parties do not share an agreed meaning of "closed", "resolved" or "approved", nor an agreed answer to how much verifiable evidence is needed before closing and how fast; externally received case information is not reliably matched, de-duplicated and ordered before people act on it; as a result effort, cost and rework cannot be compared and decisions cannot be shown to be evidence-based. Size of effect: unknown (no baselines).

(`docs/03-problem-value/problem-statement.md`, preserved verbatim in meaning; not reframed here.)

| Problem | Element | Addressed by capability |
|---|---|---|
| P-1 | No agreed, owned definitions of closed/resolved/approved | CAP-03, CAP-07 (mechanism + transparency; decision itself = OPD-01..04) |
| P-2 | Speed-vs-evidence conflict, no decider | CAP-01, CAP-03, CAP-07 (make both measurable; OPD-02/03) |
| P-3 | External information not reliably matched, de-duplicated, ordered | CAP-04, CAP-05, CAP-06, CAP-08 |
| P-4 | Effort, cost, rework not comparable | CAP-07 |
| P-5 | Human authority for disposition has no named holder; must not be removed | CAP-02, CAP-09 |

### PRD-2 Root causes the product answers (Stage 6, repo-level) [Verified Fact]
RC-1 no decision step/record; RC-2 mutable snapshot state; RC-3 no owned definition (decision gap); RC-4 three unsynchronised approval rules (defect + decision); RC-5 manual, capped, unrecorded runs; RC-6 destructive, content-blind intake; RC-7 no shared identity; RC-8 month-end figures computed independently (19.3% inflation on shipped data). Confirmed at repo level on synthetic data only; none is confirmed as a cause of delay or cost (S1).

### PRD-3 Users (Stage 3 personas, documentary) [Inference]
| Persona | Role | What the product gives them |
|---|---|---|
| PER-01 | Case reviewer | Exception queue with reason codes; no duplicates/orphans silently attached; evidence pack |
| PER-02 | Quality operations lead | Backlog ageing per site; time-to-close under each candidate definition |
| PER-03 | Compliance / risk reviewer | Attributable, tamper-evident decisions; evidence reference on every closure or an authorised exception |
| PER-04 | Finance partner | One cut-off, declared definitions, corrected month-end totals |
| PER-05 | Integration lead | Replay-safe, lossless intake; quarantine for revised items; run records |
| PER-06 | Enterprise application owner | Reversible releases; as-found behaviour preserved |
| PER-07 | Authorised batch-disposition reviewer | Evidence pack; decision stays human; gate cannot be bypassed |
| PER-08 | Engagement lead (Dinesh Naik) | Decisions visible as policy objects; all open items explicit |

### PRD-4 Journeys improved (Stage 3) [Inference]
J1 case from external message to local decision -> CAP-04/05/01; J2 delayed or replayed feed -> CAP-04/06; J3 closing a deviation/CAPA -> CAP-01/02/03; J4 month-end reconciliation -> CAP-07. Journeys are reconstructed from documents, not observed.

### PRD-5 Goals and success metrics
Goals G-1..G-5 map to P-1..P-5. Success is measured by Stage 3 SUC-01..SUC-11 (see `release-hypothesis.md`): unsafe action count = 0 (SUC-01, invariant); source attribution 100% of sample (SUC-02); definition transparency 100% (SUC-03); replay change = 0 (SUC-07); month-end difference = 0 on agreed cut-off (SUC-10); decision recorded or accepted-open (SUC-11). Time/backlog measures (SUC-04, 05, 06, 08, 09) are "improve vs baseline" and **cannot be baselined today**; R1 makes them measurable. All thresholds are provisional Assumptions (A-03-12). **No monetary or time-saving benefit is asserted.**

### PRD-6 Capabilities and requirement counts
| Capability | Name | FRs | R1 | R2 |
|---|---|---|---|---|
| CAP-01 | Decision & Evidence Record | 6 | 6 | 0 |
| CAP-02 | Human Disposition Gate (Zone H) | 6 | 6 | 0 |
| CAP-03 | Policy, Definitions & Rule Service | 6 | 5 | 1 |
| CAP-04 | Safe Intake & Exception Handling | 8 | 7 | 1 |
| CAP-05 | Shared Identity & Crosswalk | 4 | 2 | 2 |
| CAP-06 | Scheduled Runs & Run Records | 3 | 3 | 0 |
| CAP-07 | Metrics & Reporting with Declared Definitions | 8 | 6 | 2 |
| CAP-08 | Reviewer Support (rules, search, templates) | 4 | 2 | 2 |
| CAP-09 | Access Control, Audit & Data Protection | 3 | 2 | 1 |
| CAP-10 | Coexistence & Change Safety | 4 | 4 | 0 |
| | **Total** | **52** | **43** | **9** |

NFRs: 20 (PNFR-01..20), of which 17 R1. Detail: `capability-map.md`, `functional-requirements.md`, `nfrs.md`.

### PRD-7 Requirements that express an unowned rule as configurable policy
| Unowned rule | Mechanism in PRD | Open decision | Default shipped |
|---|---|---|---|
| Meaning of closed / resolved / approved | FR-POL-01 versioned policy objects; FR-MET-01/02 tagging | OPD-01 | none adopted (candidates D-OPS, D-EVID, D-FIN) |
| The 48 h clock | FR-POL-02 parameterised clock; side-by-side elapsed time | OPD-02 | none |
| Speed vs evidence | FR-DEC-05 structural check only; FR-MET-02 no cross-definition combining | OPD-03, OPD-07 | structural presence only (A-09-03) |
| Approval/priority rule authority | FR-POL-04..06 three named rule sets, marker on defaulted outcomes | OPD-04 | as-found behaviour preserved and marked |
| Where batch disposition is recorded | FR-GATE-05 two recording modes | OPD-05 | blocked until configured |
| Who may disposition | FR-GATE-03/04 empty holder list | OPD-06 | no holder |

### PRD-8 Human gate (DR-22) [Verified Fact constraint]
Batch disposition, QA release and e-signature are never made, pre-filled as final, simulated or auto-triggered (FR-GATE-01; HAR-12; STOP-07). Zone H transitions accept only authenticated humans in a configured role (FR-GATE-03). The product provides an evidence pack and records the human's act (or a reference to it); it does not decide.

### PRD-9 AI stance [Verified Fact]
No-AI per OD-08 (Dinesh, 2026-10-18). No AI functional requirement exists (FR-CO-04, PNFR-18). Re-qualification triggers RQ-1..RQ-4 and the per-touchpoint treatment are in `non-goals.md`. Stage 19 = not-applicable (or deterministic rule/explanation module only = CAP-03 rule service and FR-REV-01); Stage 22 not triggered; Stage 32 tracks zero model calls.

### PRD-10 Constraints, dependencies and exposure [Verified Fact unless noted]
| ID | Constraint / dependency | Source |
|---|---|---|
| CON-01 | Synthetic data only; no production telemetry; Dinesh Naik is the only human | OD-04 |
| CON-02 | Baseline dataset = shipped 125 cases, seed 4100 | OD-09 |
| CON-03 | All code execution in a full-repo sandbox copy; working-tree data/ never touched; checksum gate | OD-03a |
| CON-04 | Code change not ready until R-1 (executable goldens), R-2, R-4 (now answered), R-5 | repo-transformation-readiness.md |
| CON-05 | Stdlib-only today; new dependencies / egress need HAR-08/09 | HAR-08 |
| CON-06 | Changes to decision/approval logic need HAR-06; PRD/KPI/decision approvals need HAR-11 | provisional-human-approval-rules.md |
| CON-07 | Loopback only until PNFR-07/08/09 met | HAR-05 |
| CON-08 | Stage 4 KPI sheet frozen-provisional; proxies P-01/P-03/P-04 are generator-bounded, K-10/12/13 compare unrelated populations | OD-07 |
| DEP-01 | Stage 10 architecture (answer or design-both for OPD-05) | qualification-decision.md QD-4 |
| DEP-02 | Characterisation harness CT-H1..H7 before any behavioural change | Stage 7 |
| DEP-03 | Owner decisions OPD-01..04 before KPI targets or rule adoption | Stage 3/6 |

### PRD-11 Release plan
- **R1 (MVP)**: 43 FRs + 17 NFRs, see `mvp-scope.md`. Must prove RH-1..RH-7.
- **R2**: 9 FRs: reconciliation-delay views, rule divergence report, cross-object consistency findings, joined view, keyword/field search (FTS), optional templates, cost attribution, field-level data protection.
- **Beyond**: AI-assisted element only through RQ triggers; any pilot with real data only after STOP-04 / HAR-15 and a real owner.

### PRD-12 Stage consumption
Feeds Stage 10 (architecture: Zones H/D, OPD-05), Stage 12 (specs), Stage 17 (Implementation PRD) and FINAL (As-Built reconciliation by requirement ID).

## Companion artifacts
`capability-map.md`, `functional-requirements.md`, `nfrs.md`, `mvp-scope.md`, `non-goals.md`, `release-hypothesis.md`, `product-risks.md`, `open-product-decisions.md`, `initial-prd-traceability.md` (all `docs/09-initial-prd/`).

## Evidence References
Companion artifacts; `docs/03-problem-value/*`; `docs/06-root-cause/confirmed-root-causes.md`; `docs/08-ai-qualification/*`; `docs/02-stakeholders/decision-rights-map.md`; `docs/00-preflight/operating-contract/*`; `.fde/orchestrator-decisions.md`.

## Assumptions
- A-09-01 Stage 3 BR/NFR/SUC items stand as *candidate* requirements; no stakeholder has accepted them (synthetic, unvalidated). Confirm: Engagement lead (Dinesh Naik).
- A-09-02 The R1 (MVP) / R2 (later) split is an agent proposal. Confirm: Engagement lead (Dinesh Naik).
- A-09-03 For FR-DEC-05 the structural presence of an evidence reference (not its sufficiency) is an acceptable default closure check; sufficiency is policy (OPD-07). Confirm: Engagement lead (Dinesh Naik).
- A-09-04 NFR numeric targets are archived working targets, not measured guarantees (`docs/operations-service-levels.md`). Confirm: Engagement lead (Dinesh Naik).
- A-09-05 Content statistics from the synthetic data (fixed-key feeds, short stubs) represent real content structure well enough for a No-AI product (A-08-14).
- A-09-06 The user roles in FR-SEC-01 are derived from documentary personas PER-01..PER-08, not observed users.

## Unknowns
- U-09-01 Definitions of closed/resolved/approved and the 48 h clock (OPD-01, OPD-02) - accepted open (Q-02-05 unanswered).
- U-09-02 Owner of approval-rule conflicts (OPD-04) and where batch disposition is recorded (OPD-05).
- U-09-03 Real volumes, timings, labour and cost (no production telemetry; OD-04). No benefit is quantified in this PRD.
- U-09-04 Whether any user wants natural-language document Q&A (U-S01); whether the real corpus would defeat keyword search (RQ-1..RQ-3).
- U-09-05 Retention policy (OPD-09); performance targets (OPD-14); owner of the parallel legacy-customer workflow (OPD-15).

## Unresolved Issues
- OPD-13: Dinesh has not approved this PRD, the R1/R2 split or the NFR targets (HAR-11). Status stays DRAFT.
- OPD-01..05 accepted open; the PRD is parameterised, not complete, on those points.

## Residual Risks
- See `product-risks.md` (PR-01..PR-14). Chief residual risk: a PRD traced only to synthetic, unvalidated discovery written and approved by one person.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Initial PRD v0.1). |
