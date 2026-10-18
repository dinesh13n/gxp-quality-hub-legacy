---
stage: "9 — Initial PRD / Product Intent"
artifact: "capability-map.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/success-criteria.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/08-ai-qualification/qualification-decision.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Approval of this PRD is Dinesh Naik's decision (HAR-11); nothing here is an approval.**

Ten capabilities, all No-AI, grouped into four layers: a **trust layer** (CAP-09, CAP-02), a **record layer** (CAP-01, CAP-05), a **flow layer** (CAP-04, CAP-06) and a **meaning layer** (CAP-03, CAP-07, CAP-08), with CAP-10 as a cross-cutting constraint. Capabilities are grouped by the Stage 6 root cause they address; RC-3 and RC-4 are addressed only by *mechanism* because they are decisions (CR-D).

## Findings
### CM-1 Capabilities
| ID | Capability | Purpose | Stage 6 root causes | Stage 3 problems | Functional requirements |
|---|---|---|---|---|---|
| CAP-01 | Decision & Evidence Record | Append-only, attributable record of every case decision/state change with evidence references; reconstructable history. | RC-1, RC-2 | P-2, P-5 | 6 (6 R1 / 0 R2) |
| CAP-02 | Human Disposition Gate (Zone H) | Guarantees batch disposition / QA release / e-signature stay human; supplies read-only evidence pack; configurable recording mode. | RC-1 | P-5 | 6 (6 R1 / 0 R2) |
| CAP-03 | Policy, Definitions & Rule Service | Versioned, owner-tagged policy objects (definitions, clock, rule tables) with no adopted default for unowned decisions; one table-driven rule service. | RC-3, RC-4 | P-1, P-2, P-4 | 6 (5 R1 / 1 R2) |
| CAP-04 | Safe Intake & Exception Handling | Non-destructive, idempotent, content-aware intake with validation, reason codes and quarantine; inbound content treated as data. | RC-6 | P-3 | 8 (7 R1 / 1 R2) |
| CAP-05 | Shared Identity & Crosswalk | Explicit keys linking case/batch/deviation/CAPA/feed; orphans stay orphans; cross-object consistency findings. | RC-7 | P-3 | 4 (2 R1 / 2 R2) |
| CAP-06 | Scheduled Runs & Run Records | Scheduled reconcile/import with run records, checkpoints and no hidden capacity cap. | RC-5 | P-3 | 3 (3 R1 / 0 R2) |
| CAP-07 | Metrics & Reporting with Declared Definitions | One declared definition/cut-off/denominator per figure; definition tags; reproducible KPIs; fan-out defect removed. | RC-8, RC-3 | P-1, P-4 | 8 (6 R1 / 2 R2) |
| CAP-08 | Reviewer Support (rules, search, templates) | Rule-trace explanations, exception queue with reason codes, keyword/field retrieval, optional templates. No AI. | RC-1, RC-6 (enabling) | P-2, P-3 | 4 (2 R1 / 2 R2) |
| CAP-09 | Access Control, Audit & Data Protection | Authentication, role-based authorisation, tamper-evident audit of writes and policy changes, protected fields. | RC-1 (enabling) | P-2, P-5 | 3 (2 R1 / 1 R2) |
| CAP-10 | Coexistence & Change Safety | As-found behaviour preserved until approved change; legitimate parallel workflow untouched; reversible releases; zero-AI tripwire. | RC-4 (guard) | P-1, P-3 | 4 (4 R1 / 0 R2) |

### CM-2 Relationships
| From | To | Relationship | Type |
|---|---|---|---|
| CAP-09 | CAP-01 | guards all writes; audits events | depends-on |
| CAP-01 | CAP-02 | gate transitions are events in the record (or external references) | feeds |
| CAP-03 | CAP-01 | closure policy decides which transitions need evidence (FR-DEC-05) | configures |
| CAP-03 | CAP-07 | definition tags and clocks come from policy objects | configures |
| CAP-03 | CAP-08 | rule trace explains rule-table output | feeds |
| CAP-04 | CAP-05 | matching uses the crosswalk; unmatched stays unmatched | depends-on |
| CAP-04 | CAP-06 | runs execute intake and write run records | executed-by |
| CAP-04 | CAP-08 | exception queue shows reason codes | feeds |
| CAP-01 | CAP-07 | event timestamps (receipt, ops-closed, evidence-complete) feed time-to-close | feeds |
| CAP-06 | CAP-07 | run records feed reconciliation-delay and backlog metrics | feeds |
| CAP-05 | CAP-02 | evidence pack shows linked objects | feeds |
| CAP-10 | all | coexistence, goldens and zero-AI tripwire constrain every capability | constrains |

### CM-3 Layer view (text)
```
 [CAP-10 Coexistence & change safety  -- constrains everything]
 Trust:    CAP-09 Access/Audit  ->  CAP-02 Human Disposition Gate (Zone H)
 Record:   CAP-01 Decision & Evidence Record  <-  CAP-05 Identity & Crosswalk
 Flow:     CAP-04 Safe Intake  ->  CAP-06 Scheduled Runs & Run Records
 Meaning:  CAP-03 Policy/Rules (no adopted default)  ->  CAP-07 Metrics (tagged)  ->  CAP-08 Reviewer support
```

### CM-4 Zone alignment (Stage 8 B-1) [Verified Fact]
| Zone | Capabilities |
|---|---|
| H (human-only) | CAP-02; adoption/changes in CAP-03 (FR-POL-01, FR-POL-03, FR-POL-04 active-set choice); closure failing evidence rule (FR-DEC-05) |
| D (deterministic only) | CAP-01, CAP-03 rule service, CAP-04, CAP-05, CAP-06, CAP-07, CAP-09 |
| A (AI-eligible, empty) | none admitted |

### CM-5 Root-cause coverage [Inference]
RC-1 -> CAP-01, CAP-02; RC-2 -> CAP-01; RC-3 -> CAP-03 (mechanism only), CAP-07; RC-4 -> CAP-03 (candidates), CAP-10; RC-5 -> CAP-06; RC-6 -> CAP-04; RC-7 -> CAP-05; RC-8 -> CAP-07. All eight root causes map to at least one capability; the two decision-gap causes are not "solved", only made visible and parameterised.

## Evidence References
`docs/06-root-cause/confirmed-root-causes.md`; `docs/08-ai-qualification/deterministic-vs-ai-boundaries.md`; `docs/09-initial-prd/functional-requirements.md`.

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
- CAP-02 shape depends on OPD-05; CAP-03 content depends on OPD-01..04.

## Residual Risks
- Capability boundaries are a product view, not an architecture; Stage 10 may regroup them.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Initial PRD v0.1). |
