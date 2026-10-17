---
stage: "3 — Frame Problem & Value"
artifact: "problem-statement.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/problem-framing-canvas.md", "docs/business-context.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md", "docs/domain-assurance.md", "docs/02-stakeholders/stakeholder-conflicts.md", "docs/02-stakeholders/decision-rights-map.md"]
supersedes: "none"
---
## Summary

Technology-neutral problem statement. It names no product, model, platform or AI, and it does **not** prescribe a closure rule, threshold or definition, because none has an owner. **Label: synthetic, unvalidated.** Nobody other than the engagement lead (Dinesh Naik) has confirmed it.

## Findings

### Problem statement [Inference; synthetic, unvalidated]

> In pharma batch-deviation and CAPA case handling at Gxp Group (a fictional organisation), the people who review, close, fund and audit cases do not share an agreed meaning of when a case is "closed", "resolved" or "approved", nor an agreed answer to how much verifiable evidence is needed before closing and how fast closure must happen. Case information that arrives from external sources is also not reliably matched, de-duplicated and ordered against the core case record before people act on it. As a result, reviewers spend effort on manual reconciliation and rework, the same case is counted and costed differently by operations, finance and compliance, and the time needed to show that a decision was evidence-based cannot be measured consistently. The size of this effect is unknown because no agreed definitions or measured baselines exist.

### Decomposition (each traceable)

| ID | Problem element | Traces to | Class |
|---|---|---|---|
| P-1 | No agreed, owned definitions of closed / resolved / approved | SC-02, SC-05, DR-20, DR-23; `business-context.md` | [Inference] |
| P-2 | Speed-of-closure and evidence-sufficiency expectations conflict, with no decider | SC-01, SC-03, DR-20, DR-21; `operations-vs-risk-2024.md` | [Verified Fact] (documented) |
| P-3 | Externally received case information is not reliably matched, de-duplicated and ordered before use | S2/S4 in canvas; 0A IO-01..05, IO-10..13 | [Inference] |
| P-4 | Effort, cost and rework cannot be compared across parties or periods (definitions, cut-offs, denominators differ) | SC-02, SC-04; `baseline-measurement-notes.md` | [Inference] |
| P-5 | Human authority for batch disposition has no named holder; the problem must be solved without removing human approval | DR-22; `domain-assurance.md` | [Verified Fact] constraint |

### What this statement deliberately does not do

- It does not say what "closed" means, or whether 48 hours is right (SC-01 unresolved; DR-20 GAP).
- It does not say the cause (Stage 6) or the remedy (Stages 8-10).
- It does not assert that effort is "rising": that is a claim without trend data (U-03-01).

## Evidence References

`docs/business-context.md` "Operating concern"; `docs/correspondence/operations-vs-risk-2024.md`; `docs/domain-assurance.md`; Stage 2 `stakeholder-conflicts.md`, `decision-rights-map.md`.

## Assumptions

- A-03-01, A-03-04 (`assumptions-register.md`).

## Unknowns

- U-03-01 magnitude; U-03-03 whether the conflict still exists outside the 2024 document.

## Unresolved Issues

- P-1 and P-2 cannot be closed by analysis; they need a decision by an owner who does not exist (DR-20/21). Recorded, not resolved.

## Residual Risks

- Readers may treat this as a validated client problem. Mitigation: label on every downstream use.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial problem statement. |
