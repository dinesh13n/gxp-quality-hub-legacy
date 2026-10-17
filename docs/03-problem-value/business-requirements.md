---
stage: "3 — Frame Problem & Value"
artifact: "business-requirements.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/problem-statement.md", "docs/03-problem-value/jobs-to-be-done.md", "docs/02-stakeholders/stakeholder-needs-matrix.md", "docs/02-stakeholders/stakeholder-conflicts.md", "docs/domain-assurance.md", "docs/business-context.md", "docs/correspondence/operations-vs-risk-2024.md"]
supersedes: "none"
---
## Summary

Outcome-based business requirements, each traced to a stakeholder need (SH/SC/DR), a JTBD and a problem element. **No requirement names a technology or AI.** Requirements are **candidate, unvalidated, synthetic**: no stakeholder has accepted them. Where a requirement would encode an unowned rule, it is written as "state which definition applies" rather than choosing one. Priority is MoSCoW proposed by agent, owner Dinesh Naik.

## Findings

| ID | Requirement (outcome) | Priority | Problem | JTBD | Trace (need / evidence) | Verification | Class |
|---|---|---|---|---|---|---|---|
| BR-01 | Every reported case figure (closed, resolved, cost, handling time) shall declare which definition of the state it uses, and figures built on different definitions shall not be combined or compared. | Must | P-1, P-4 | 05, 09 | SC-01, SC-02, SH-05; `business-context.md` | Inspect reports: 100 % carry a definition tag | [Inference] |
| BR-02 | The organisation shall record who decides the definition of closed/resolved and the closure-time expectation. The engagement shall not choose it. | Must | P-1, P-2 | 09 | DR-20, DR-21; `operations-vs-risk-2024.md` | A decision record exists with owner/date, or an "accepted open" record exists | [Verified Fact] (gap) |
| BR-03 | Time-to-close shall be measurable under each candidate definition (elapsed from receipt to ops-closed, and to evidence-complete) without prejudging which is correct. | Must | P-2, P-4 | 03 | SC-01; SH-03, SH-09 | Two separate measures computed on same population | [Inference] |
| BR-04 | Externally received case information shall be matched to exactly one core case, or flagged unmatched, before it reaches a reviewer's queue. | Must | P-3 | 01 | SH-07, SH-13; IO-10; `business-context.md` | Unmatched-reference rate measured; no silent attach | [Inference] |
| BR-05 | A re-delivered or replayed item shall not increase the exception queue or alter totals. | Must | P-3 | 06 | 2025 rollback; INC-2025-014; SH-04, SH-07 | Replay test: queue and totals unchanged | [Verified Fact] (incident), [Inference] |
| BR-06 | Delayed, missing or revised items shall be detectable and attributable to a source and time without manual spreadsheet reconciliation. | Should | P-3 | 06 | INC-2025-014; SH-12 | Reconciliation delay measured; manual step count | [Inference] |
| BR-07 | Each case decision shall carry the evidence relied on and its source, retrievable on request. | Must | P-2, P-5 | 02, 04 | SH-06, SH-09, SH-15; `domain-assurance.md` ("source attribution for each decision") | Sample audit: evidence and source present | [Verified Fact] (need) |
| BR-08 | Batch disposition and any other decision requiring an authorised person shall remain a human decision; no process shall make, pre-fill as final, or simulate it. | Must | P-5 | 08 | SH-15; DR-22; `domain-assurance.md`; HAR-12 | Unsafe action count = 0 | [Verified Fact] |
| BR-09 | No case shall be closed without verifiable evidence unless an owner has explicitly authorised an exception rule. | Must | P-2 | 04 | SH-09; `operations-vs-risk-2024.md` | Count of closures lacking evidence = 0, or each has recorded authorisation | [Verified Fact] (stated need); the exception rule is a GAP |
| BR-10 | Case cost and avoidable rework shall be attributable per case and per period using one agreed cut-off and denominator. | Should | P-4 | 05 | SH-05; SC-04; `baseline-measurement-notes.md` | Finance and ops totals reconcile on shared cut-off | [Inference] |
| BR-11 | Existing legitimate workflows (including the parallel path for older customers) shall not be disrupted without an identified owner's agreement. | Must | P-1 | 07 | SC-07; `business-context.md` "preserving legitimate workflows" | Workflow inventory with owner sign-off [Unknown owner] | [Verified Fact] (stated) |
| BR-12 | Backlog ageing and unresolved exception rate shall be visible per site and comparable across sites. | Should | P-4 | 03 | SH-03, SH-10; `domain-assurance.md` | Metric produced per site on one definition | [Inference] |
| BR-13 | Change to the handling process shall be releasable without causing a rollback of the kind documented in 2025. | Should | P-3 | 07 | SH-04; `historic-decisions.md` 2025 | Rollback count over a release window | [Inference] |

### Traceability check

Every row cites an SH/SC/DR id or evidence path. No requirement derives from "we need AI". BR-02 and BR-09 expose DR-20/21 as owner gaps; they remain **unmet by design** until an owner exists.

## Evidence References

As per rows.

## Assumptions

- A-03-09: MoSCoW priorities are agent proposals. A-03-10: BR-09 "unless authorised" is wording that preserves the unowned decision.

## Unknowns

- U-03-09 Real priority; U-03-10 whether BR-05/BR-04 failures occur at material rates outside synthetic data.

## Unresolved Issues

- BR-02, BR-09, BR-11 depend on owners that do not exist. They cannot reach "met" in this engagement without Dinesh's recorded decision.

## Residual Risks

- Requirements may be read as agreed policy; they are candidates.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial requirements. |
