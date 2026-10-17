---
stage: "3 — Frame Problem & Value"
artifact: "problem-framing-canvas.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md", "docs/legacy-operations-history.md", "docs/domain-assurance.md", "docs/01-engagement/use-case-hypothesis.md", "docs/01-engagement/engagement-canvas.md", "docs/02-stakeholders/stakeholder-needs-matrix.md", "docs/02-stakeholders/stakeholder-conflicts.md", "docs/02-stakeholders/decision-rights-map.md", "docs/00-preflight/discovery/data-flow-overview.md", "docs/00-preflight/discovery/integration-overview.md", "docs/00-preflight/discovery/workflow-overview.md", "operations/incidents/INC-2025-014.md"]
supersedes: "none"
---
## Summary

Separates **symptom**, **root problem (hypothesised)**, **proposed solution (as the repo frames it)** and **assumed AI need**. Every client-side statement is a claim in a synthetic document (OD-04); there are no stakeholders beyond Dinesh Naik (Stage 2). **All pain and value statements here are "synthetic, unvalidated".** The root problem is stated only as far as evidence allows and **does not encode any rule that has no owner** (DR-20, DR-21, DR-23 are GAPs): the unresolved conflict is itself framed as part of the problem, not settled.

## Findings

| Layer | Content | Class | Evidence | Confidence |
|---|---|---|---|---|
| **Symptoms** (observed/claimed) | S1 "Rising exception-handling effort" (claim, no trend data) | [Verified Fact] claim exists; [Unknown] truth | `docs/business-context.md` "Operating concern" | Low |
| | S2 Feed data inconsistent with core records: 8,394 of 8,567 partner-feed rows reference cases absent from the case table (synthetic, test-residue DB) | [Verified Fact] on synthetic data | Stage 0A IO-10, DF-03 | High (as data), Low (as business signal) |
| | S3 "Closed" means different things at different sites | [Verified Fact] (claim); 5+ status vocabularies in code | `business-context.md`; 0A WF-11 | Medium-High |
| | S4 A replayed partner delivery inflated the exception queue and caused a rollback (2025); a delayed feed forced manual spreadsheet reconciliation (INC-2025-014) | [Verified Fact] documented; no ticket/log | `historic-decisions.md` 2025; `operations/incidents/INC-2025-014.md` | Medium |
| | S5 Finance and operations monthly cut-offs disagree | [Verified Fact] documented | `legacy-operations-history.md` | Medium |
| **Root problem (hypothesis)** | RP1 Case state, approval thresholds and "resolved" are **not commonly defined or owned**, so the same case is counted, closed and costed differently by different parties. | [Inference] from S3, S5, 3 divergent approval rules (WF-06), DR-20/DR-23 GAP | `operations-vs-risk-2024.md`; 0A WF-06, WF-11 | Medium |
| | RP2 Externally received case information is **not reliably matched, de-duplicated and sequenced** against the core record before people act on it. | [Inference] from S2, S4, IO-01..03 (no retry, in-place status mutation, contract unenforced) | 0A IO-01..05, IO-10..13 | Medium (synthetic) |
| | RP3 The **evidence needed to justify closing a case is not uniformly available or defined**, and the speed-vs-evidence trade-off (48 h vs verifiable evidence; faster month-end vs more evidence) has no decider. | [Inference]; decision gap is [Verified Fact] | `operations-vs-risk-2024.md`; `historic-decisions.md` 2024; DR-20, DR-21 | Medium |
| **Proposed solution (as framed in repo)** | "Modernisation proposal awaiting baseline measurements and architecture review" (2026); "determine and justify any modernization or AI intervention". No solution is specified. | [Verified Fact] | `historic-decisions.md` 2026; `business-context.md` | High |
| **Assumed AI need** | The repo and use-case hypothesis H6 imply AI *might* help. No requirement, stakeholder or measurement demands it. Stage 0C found several gaps are addressable deterministically (H5). | [Assumption] (H6), explicitly unproven | `use-case-hypothesis.md` H5/H6; Stage 0C Key finding 5 | Low |
| **Not a problem statement element** | "We need AI" is **rejected as a requirement** (stage guardrail). AI applicability is decided no earlier than Stage 8. | Policy | Stage prompt; CG-4 | High |

### Separation test applied

| Question | Answer |
|---|---|
| Does any symptom prove a root cause? | No. RP1-RP3 are inferences; Stage 6 tests them. |
| Is the root problem phrased without a solution or technology? | Yes (see `problem-statement.md`). |
| Which part of the problem is a decision, not an engineering gap? | RP1 and RP3 (unowned policy). Engineering must not pick a side (CG-7). |

## Evidence References

See `evidence_sources`. Stage 2: SC-01..SC-05, DR-20..DR-24, SH-03..SH-15.

## Assumptions

- A-03-01..A-03-03 in `assumptions-register.md` (documents represent real client intent; synthetic data indicates direction not magnitude).

## Unknowns

- U-03-01 Whether any symptom is currently live or materially large (no telemetry, no tickets). U-03-02 Which of RP1-RP3 dominates.

## Unresolved Issues

- RP1/RP3 rest on policy with no decider (SC-01..03). Dinesh Naik must decide or accept as open (Stage 2 Q-02-05).

## Residual Risks

- Framing a synthetic corpus as client truth (ER-01). Anchoring on the AI row before Stage 8 (ER-05).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial canvas. |
