---
stage: "1 — Engage & Qualify"
artifact: "use-case-hypothesis.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md", "docs/00-preflight/discovery/workflow-overview.md", "docs/00-preflight/discovery/integration-overview.md", "docs/00-preflight/discovery/data-flow-overview.md", "docs/00-preflight/ai-economics/economics-readiness.md"]
supersedes: "none"
---
## Summary

**THIS IS A HYPOTHESIS, NOT A FINDING OR A SOLUTION.** It restates the problem area the repo points to, as testable hypotheses, for Stage 3 to reframe in technology-neutral terms. No technology, architecture or AI approach is proposed or chosen; AI applicability is decided no earlier than Stage 8.

## Findings

### Hypothesis statement (to be tested)

> H0. Pharma batch-deviation / CAPA case handling at Gxp Group loses time and quality because case state, approval thresholds, and external-feed data are not consistently defined and reconciled across systems, and because the evidence needed to close a case is not uniformly available. Reducing that inconsistency, while preserving human GxP approval, may reduce handling effort and rework.

### Sub-hypotheses and how each would be falsified

| ID | Sub-hypothesis | Basis | Class | Falsifier / test (stage) |
|---|---|---|---|---|
| H1 | Inconsistent definitions (what is "closed"/"resolved"/"approved") drive avoidable rework and disputed metrics | Correspondence 2024; 5+ status vocabularies (WF-11); 3 divergent threshold rules (WF-06) | [Inference] | Stakeholders agree one definition with no measurable rework impact (2, 4, 6) |
| H2 | Feed ingestion/reconciliation defects (drops, replays, in-place overwrites, orphan references) inflate exception queues | 2025 rollback note; IO-01..03; DF-03 | [Inference] | Characterisation shows defects do not affect queue size (5, 7) |
| H3 | The compliance requirement for verifiable evidence conflicts with the 48 h closure goal, and the conflict is unresolved policy, not a tooling gap | Correspondence 2024 | [Inference] | Policy owner shows an agreed, documented rule exists (2, 3) |
| H4 | Month-end reconciliation is slow/manual because definitions and data windows differ | Finance request 2024; baseline notes ("business definitions not guaranteed to agree") | [Assumption] | Measured month-end effort (4) |
| H5 | Some of the above is addressable without AI (deterministic rule/definition/reconciliation fixes) | 0C Key finding 5: gaps are independent of AI and cost no tokens | [Inference] | Stage 8 AI-vs-no-AI qualification |
| H6 | A narrow, human-in-the-loop AI assist (e.g. over evidence/documents) *might* add value beyond H5 | Document corpora with mixed confidence/locale exist (DF-*); repo is framed for "AI intervention" | [Assumption] — **explicitly unproven; no commitment** | Stage 8 may reject; requires measured baseline (4) and economics beyond 0C envelope |

### Out of scope for this artifact

Solution design, technology selection, AI architecture (Stage prompt Scope: Exclude).

### Preconditions for the hypothesis to be testable

1. Baseline dataset chosen (OD-02 provisional; U-13).
2. Metric definitions agreed (OQ-05).
3. Stakeholder or documented-waiver validation of the problem (OQ-01, OQ-02).

## Evidence References

Claims: `docs/business-context.md`, `docs/correspondence/operations-vs-risk-2024.md`, `docs/historic-decisions.md`. Verified structural facts: Stage 0A findings WF-06, WF-11, IO-01..03, DF-03.

## Assumptions

- H4 and H6 are assumptions; H1–H3, H5 are inferences from synthetic data only.
- The shipped DB (125 cases, test residue) is not a reliable basis for quantifying any hypothesis.

## Unknowns

- Real magnitude (hours, cost, backlog ageing) of any effect (U-24). Whether any hypothesis holds outside the synthetic simulator.

## Unresolved Issues

- Stage 3 must reframe H0 technology-neutrally and attach measures; Stage 8 must decide AI.

## Residual Risks

- Anchoring downstream stages on H6 (AI) before evidence (ER-05).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial hypothesis. |
