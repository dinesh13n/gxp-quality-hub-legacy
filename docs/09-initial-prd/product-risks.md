---
stage: "9 — Initial PRD / Product Intent"
artifact: "product-risks.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/success-criteria.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/08-ai-qualification/qualification-decision.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/01-engagement/engagement-risks.md", "docs/07-repo-assessment/repo-transformation-readiness.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Approval of this PRD is Dinesh Naik's decision (HAR-11); nothing here is an approval.**

14 product risks. Likelihood and impact are agent judgement (Inference) because no real incident, volume or cost data exists; none is a measurement. Owner for all: **Engagement lead (Dinesh Naik)**.

## Findings
### PR-1 Product risk register
| ID | Area | Risk | Likelihood | Impact | Mitigation in PRD | Trace | Owner |
|---|---|---|---|---|---|---|---|
| PR-01 | Governance | Engineers silently encode one party's rule (closed/48 h/approval limit) because no owner exists | High | High | Policy objects with no adopted default (FR-POL-01/02/04); Zone H adoption; OPD-01..04 | RC-3, RC-4; CG-7 | Engagement lead (Dinesh Naik) |
| PR-02 | Safety | Decision write path creates a gate that is bypassed or simulated (batch disposition) | Low | Critical | FR-GATE-01..06; FAIL-01; HAR-12; CT-16 guard; empty role-holder list | RC-1; STOP-07 | Engagement lead (Dinesh Naik) |
| PR-03 | Evidence | Root causes are confirmed only at repo level on synthetic data; the real organisation may record decisions and history elsewhere (FH-1), shrinking R1 | Medium | High | Label everything synthetic; FR-GATE-05 supports external-reference mode; revisit at Stage 34 | U-05-02; IH-3 FH-1; Stage 6 scope statement | Engagement lead (Dinesh Naik) |
| PR-04 | Value | No baseline exists (K-04/K-05 unmeasurable); R1 produces the first baseline, not an improvement; benefit cannot be claimed | High | Medium | Release hypothesis framed as 'establish measurability'; no monetary claim; FAIL-03/FAIL-05 | OD-07; IH-2 | Engagement lead (Dinesh Naik) |
| PR-05 | Delivery | Code change not yet safe: executable golden harness missing (R-1 partial), hermetic fixture needed (R-2), working-tree execution forbidden (OD-03a) | High | High | All R1 acceptance runs in sandbox copies; characterisation harness is first BUILD task; FR-CO-01 | docs/07-repo-assessment/repo-transformation-readiness.md R-1, R-2 | Engagement lead (Dinesh Naik) |
| PR-06 | Regression | Fixing RC-8 (fan-out) or RC-6 changes figures that unknown consumers rely on ('wrong-but-pinned') | Medium | Medium | FR-CO-01: deviations listed and approved (HAR-06); old and new totals shown side by side | RC-8; heat map 'High (numbers)' | Engagement lead (Dinesh Naik) |
| PR-07 | Security | R1 exposed beyond loopback while auth/TLS/audit are unmet | Medium | High | PNFR-07/08/09 are R1; HAR-05 gate; R-11 Not met | 0A SO-01..03, SO-09 | Engagement lead (Dinesh Naik) |
| PR-08 | Scope | Scope creep into AI (T3 Q&A, narrative drafting) or into policy decisions | Medium | Medium | Non-goals NG-01..NG-04; RQ-1..RQ-3 triggers; FR-CO-04 tripwire | OD-08; BR-AI-1..7 | Engagement lead (Dinesh Naik) |
| PR-09 | Adoption | Personas are documentary; no user validates the reviewer experience (queue, evidence pack) | High | Medium | Treat UX requirements as hypotheses; Dinesh walk-through acceptance only | A-03-02; U-03-04 | Engagement lead (Dinesh Naik) |
| PR-10 | Review | Single author/approver pair (ER-11): no independent challenge of PRD, root causes or No-AI conclusion | High | Medium | Declared; adversarial self-check at Stage 34; record explicitly | CD-7 | Engagement lead (Dinesh Naik) |
| PR-11 | False negative on AI | Real documents may be large/multilingual/noisy so keyword search disappoints | Low-Medium | Medium | Deterministic baseline first; RQ-1..RQ-3; baseline recall measured before any AI | A-08-14; U-08-04 | Engagement lead (Dinesh Naik) |
| PR-12 | Data | Synthetic content stats (98% orphans, 19.3% inflation) read as business facts | Medium | Medium | FR-MET-06 labelling; PNFR-20; OD-07 proxy rule | R-04, R-05 | Engagement lead (Dinesh Naik) |
| PR-13 | Integrity | Append-only decision store grows or conflicts with in-place legacy writers (generator, reconcile) during coexistence | Medium | Medium | FR-CO-01 coexistence; migration plan at Stage 14; legacy writers not widened | RC-2, RC-6 | Engagement lead (Dinesh Naik) |
| PR-14 | Compliance | Part 11/GxP framing mistaken for certification; retention unknown | Medium | Medium | PNFR-09/10 are framing; hold-all retention; OPD-09 | DR-24, DR-29; A-08 | Engagement lead (Dinesh Naik) |

### PR-2 Reading the register
- [Inference] The two highest-consequence risks (PR-01, PR-02) both concern *unowned authority*. They are structural to the engagement, so the PRD answers with mechanism (no default, empty holder list), not with a chosen rule.
- [Verified Fact] PR-05 is a gate on delivery, not on documentation: Stage 7 verdict was "READY FOR TRANSFORMATION PLANNING; NOT READY FOR CODE CHANGE until R-1..R-5".
- [Unknown] Probability of PR-03 (decisions already recorded elsewhere) cannot be estimated without Dinesh or a stakeholder answer (U-05-02).

## Evidence References
`docs/01-engagement/engagement-risks.md`; `docs/06-root-cause/confirmed-root-causes.md`; `docs/07-repo-assessment/repo-transformation-readiness.md`; `docs/08-ai-qualification/qualification-decision.md` CD-1..CD-7.

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
- PR-03, PR-09, PR-10 cannot be reduced without an external human; accepted as residual.

## Residual Risks
- Ratings are subjective and single-reviewer.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Initial PRD v0.1). |
