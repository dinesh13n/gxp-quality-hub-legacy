---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "context-engineering-strategy.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md OD-08", "docs/08-ai-qualification/qualification-decision.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/09-initial-prd/functional-requirements.md FR-CO-04, FR-REV-01, FR-GATE-02", "docs/09-initial-prd/nfrs.md PNFR-18", "docs/00-preflight/ai-economics/provisional-context-budget.md", "docs/00-preflight/ai-economics/provisional-token-budget.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** **Status: NOT APPLICABLE to the product (minimal, by decision).** OD-08 (Dinesh, 2026-10-18) fixed the product as No-AI: zero model calls, no prompts, no context window, no token budget, no grounding step, no agent memory. Context engineering for a model therefore has nothing to design, and inventing a model-context architecture would contradict ADR-002 and FR-CO-04. What remains is a *deterministic equivalent*: **how the product assembles read-only information for a human reviewer** ("display context"), and a **guard** that keeps untrusted text out of any future prompt-like channel. The Stage 0C provisional context/token budgets are superseded for the product as "0 tokens" (they remain valid only as a re-qualification reference).

## Findings

| ID | Finding | Evidence | Impact | Risk | Conf. | Class |
|---|---|---|---|---|---|---|
| CE-01 | The product contains no LLM/ML call and no model-inference egress; this is both a decision and a CI-testable property. | OD-08; FR-CO-04; PNFR-18; ADR-002 B | No context window, prompt template, tool schema, memory or compaction to design | Low | High | [VF] decision |
| CE-02 | The 0C context and token budgets assumed AI scenarios; with OD-08 they apply as 0 for the product. | `provisional-context-budget.md`, `provisional-token-budget.md` | Cost model for Stage 31 should use zero model cost; infrastructure only | Low | High | [VF]/[INF] |
| CE-03 | Planted instruction strings (86 feed rows, 22 doc bodies, 9 evidence payloads, archive, lake) are the principal reason a future AI would be unsafe without a boundary. | DF-08; metadata-model MU-2 | Boundary rules below are kept as insurance, not as an AI design | High (if AI later) | High | [VF] |

### Deterministic "display context" assembly (the in-scope remainder)

| Rule | Description |
|---|---|
| CX-1 Inputs are enumerated | A reviewer view (case pack, exception queue row, search hit, rule trace, metric) is built from named tables/fields only; no free-form concatenation. |
| CX-2 Provenance travels | Each displayed item carries source, version, effective date and hash prefix (`provenance-policy.md`). |
| CX-3 Untrusted text is leaf content | Untrusted fields are rendered only as escaped leaf text in a labelled region; they are never used as labels, links, field names, SQL, paths, template fragments, or rule inputs (FR-INT-07). |
| CX-4 Missing is shown | Unmatched links, NULL OCR confidence, defaulted rule outputs and orphans are displayed explicitly ("none found", "unknown", "defaulted"). |
| CX-5 Size is bounded | Display length limits per field; a truncated field shows "truncated, full text at source link" with the hash; nothing is summarised. |
| CX-6 Access is applied first | Role/tenant/access-level filtering precedes assembly (MA-3). |
| CX-7 Rule trace, not rationale | Explanations are generated from rule-table row, inputs and version (FR-REV-01); no narrative generation. |

### Re-qualification guard (applies only if Dinesh later reverses OD-08; RQ-1..RQ-3)

- RG-1 A new Stage 8 qualification and a new decision are prerequisites; ADR-002 would be superseded.
- RG-2 Any model prompt must treat all Untrusted fields as quoted data in a separate, delimited, non-instruction channel, with outputs limited to citing source ids already in the pack; no tool access; Zone H actions unreachable (FR-GATE-01).
- RG-3 The planted-string fixture set (86/22/44) becomes a release gate for that change.
- These notes are constraints, not a design; no component is reserved for them (ADR-002 option C not selected).

## Evidence References

OD-08 text in `.fde/orchestrator-decisions.md`; ADR-002 decision; FR-CO-04; PNFR-18.

## Assumptions

- A-11-13: "AI coding assistants used to build the system are dev tooling, not product AI" (OD-08 / BR-AI-7) so no context strategy is needed for them. Confirm: Engagement lead (Dinesh Naik), already approved in OD-08.

## Unknowns

- U-11-20 Whether Dinesh will ever request T3 Q&A (OPD-12). Resolution: RQ triggers, Stage 34 re-baseline.

## Unresolved Issues

- None; N/A is justified by an approved decision.

## Residual Risks

- DR-14 (untrusted text), DR-16 (silent AI creep, mitigated by ADR-002 deny-list/tripwire).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Recorded as N/A with deterministic display-context rules. |
