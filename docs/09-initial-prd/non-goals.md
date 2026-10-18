---
stage: "9 — Initial PRD / Product Intent"
artifact: "non-goals.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/success-criteria.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/08-ai-qualification/qualification-decision.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Approval of this PRD is Dinesh Naik's decision (HAR-11); nothing here is an approval.**

15 explicit non-goals. They protect against (a) AI capability that Stage 8 rejected, (b) encoding rules nobody owns, (c) automating the human disposition gate, and (d) claims the evidence cannot support. Stage 3 exclusions EX-01..EX-08 are carried forward and extended.

## Findings
### NG-A Non-goals
| ID | Non-goal | Basis | Revisit when |
|---|---|---|---|
| NG-01 | Any AI/LLM/ML/agentic capability: GenAI document Q&A, narrative drafting, ML classification of feed exceptions, agentic cross-store investigation | OD-08; qualification-decision.md QD-1; BR-AI-1..7; HAR-10 | Re-qualification only via RQ-1..RQ-3 (RQ-4 for agency) and a new Dinesh decision |
| NG-02 | Making, pre-filling as final, simulating or automating batch disposition, QA release, e-signature | BR-08; DR-22; HAR-12; STOP-07 | Never (Zone H) |
| NG-03 | Choosing or imposing a definition of closed/resolved/approved, the 48 h rule, evidence-sufficiency criteria or approval thresholds | EX-01; RC-3; DR-20/21/23 | Only when an owner (or Dinesh) decides (OPD-01..04, 07) |
| NG-04 | Auto-closing any case; auto-linking orphans by guessing or similarity | BR-09; RC-7; Stage 6 guardrail | Never in this scope |
| NG-05 | Retiring or altering the parallel workflow kept for older customers | EX-04; SC-07; FR-CO-02 | Owner decision (OPD-15) |
| NG-06 | Treating 21 CFR Part 11 / GxP as a binding certification target | EX-05; DR-29; A-08 | If Dinesh declares it |
| NG-07 | Replacing the system with a commercial QMS (O9) | OPD-10; not evaluated | Stage 10 if in scope |
| NG-08 | Merging archived enterprise estate / lake into the product data model | EX-06; DF-09, DF-10 | Stage 5 shows need |
| NG-09 | Real production data, real people, real external systems, production telemetry | EX-07; OD-04; STOP-04 | Never in this engagement |
| NG-10 | Quantified benefit, ROI or labour-saving claims | value-hypothesis.md; OD-07; economics | After real baselines (Stage 34/36) |
| NG-11 | Implementation detail: technology, framework, schema, deployment topology | Stage 9 prompt Exclude | Stages 10-13 |
| NG-12 | Cost attribution per case and per period in R1 | FR-MET-08; U-24; no cost source | R2 once a cost input and owner exist |
| NG-13 | Exposure beyond loopback / multi-tenant hosting before PNFR-07/08/09 are met | PR-07; HAR-05; R-11 | Stage 23-25 |
| NG-14 | Running or testing code in the working tree; regenerating or modifying data/ | OD-03a; HAR-01, HAR-16 | Never (sandbox copy only) |
| NG-15 | Security remediation of the legacy services as a goal in itself | EX-08; NFR gaps | Only to the extent PNFR-07..09 require for the new product |

### NG-B AI non-goals and re-qualification triggers (required by QD-4)
| Touchpoint | Product treatment | AI status |
|---|---|---|
| T1 triage explanation | Rule-trace text (FR-REV-01) | Not AI |
| T2 feed exception classification | Rule-based reason codes and quarantine (FR-INT-06) | Not AI, no ML |
| T3 document Q&A | Keyword/field search only (FR-REV-03, R2) | AI-assisted NOT selected; conditional via RQ-1..RQ-3 |
| T4 deviation/CAPA narrative | Optional template (FR-REV-04, R2) | Narrative generation not selected |
| T5 cross-store investigation | Crosswalk + read-only view (FR-ID-01/04) | Agentic rejected |

| Trigger | Condition (proposal, not measurement) |
|---|---|
| RQ-1 | Real/realistic corpus available; labelled set of at least 50 questions; keyword/FTS top-5 recall below a threshold Dinesh sets (proposal 80%) |
| RQ-2 | Real content multilingual or OCR-noisy in a way the baseline demonstrably fails |
| RQ-3 | Named stakeholder requests a language-based touchpoint and accepts a reviewer-time budget |
| RQ-4 | Only after RQ-1..RQ-3 yield an approved AI element and RC-7 crosswalk exists: residual cross-store cases that deterministic queries cannot resolve |
Each re-qualification must also satisfy BR-AI-1..BR-AI-7 (approval, no model output into decision tables, synthetic-only inputs, injection tests, deterministic fallback). AI coding assistants used to *build* the system are development tooling, not product AI (BR-AI-7).

## Evidence References
`docs/03-problem-value/scope-exclusions.md`; `docs/08-ai-qualification/qualification-decision.md` QD-3, QD-4; `docs/08-ai-qualification/deterministic-vs-ai-boundaries.md`; `docs/00-preflight/operating-contract/scope-boundaries.md`.

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
- RQ thresholds are proposals until Dinesh sets them (OPD-12).

## Residual Risks
- A non-goal may later prove wrong if the real corpus defeats keyword search (PR-11); mitigated by RQ triggers.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Initial PRD v0.1). |
