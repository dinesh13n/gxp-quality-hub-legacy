---
stage: "2 — Stakeholder Discovery & Authority Confirmation"
artifact: "stakeholder-map.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "docs/service-boundaries.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md", "docs/legacy-operations-history.md", "docs/decisions/ADR-archived-007.md", "docs/domain-assurance.md", "docs/operations-service-levels.md", "operations/incidents/INC-2025-014.md", "docs/01-engagement/team-charter.md", "docs/00-preflight/operating-contract/provisional-operating-contract.md", ".fde/orchestrator-decisions.md OD-04"]
supersedes: "none"
---
## Summary

No real stakeholder is available (OD-04). The client "Gxp Group" is fictional and "all people and company records are synthetic" (`docs/business-context.md` L3). The only human is **Dinesh Naik, engagement lead**. Every client-side stakeholder below is a **role or team named in a repo document, unconfirmed**: no person, name, contact, org chart, RACI or interview record exists anywhere in the repo. Influence/interest ratings are the agent's [Inference] from the role descriptions and are not validated. No owner is invented; unfilled roles are governance gaps (see `decision-rights-map.md`).

Presence key: **P** = person exists (confirmed); **R** = role named in repo document, unconfirmed; **T** = team named in repo doc, unconfirmed; **A** = non-human agent; **X** = group absent from evidence.

## Findings

### Stakeholder register

| ID | Stakeholder | Group(s) | Presence | Influence | Interest | Source | Class |
|---|---|---|---|---|---|---|---|
| SH-01 | Dinesh Naik, engagement lead (sponsor proxy, sole approver, technical owner proxy) | Leadership, product, architecture | **P** (the only human) | High | High | `.fde/orchestrator-decisions.md` OD-01, OD-04; `team-charter.md` | [Verified Fact] that he approved OD-01/OD-04; his wider authority is [Assumption] A-0B-06 |
| SH-02 | claude-fde-agent (orchestrator and stage agents) | Engineering | **A** (no decision rights; TP-14, AG-5) | Medium (executes, cannot approve) | High | `provisional-tool-agent-permissions.md` | [Verified Fact] |
| SH-03 | Quality operations lead | Business, operations, users | **R** | High [Inference] | High [Inference] | `business-context.md` "Operating stakeholders": throughput, handling time, case quality | [Verified Fact] title; holder [Unknown] |
| SH-04 | Enterprise application owner | Product, engineering, operations | **R** | High [Inference] | High [Inference] | `business-context.md`: uptime, interfaces, release process | [Verified Fact] title; holder [Unknown] |
| SH-05 | Finance partner | Business (finance) | **R** | Medium-High [Inference] | High [Inference] | `business-context.md`: case cost, avoidable rework; `historic-decisions.md` 2024 | [Verified Fact] title; holder [Unknown] |
| SH-06 | Risk and security partner | Security, privacy, compliance, risk | **R** | High [Inference] (veto-like on evidence per 2024 correspondence) | High [Inference] | `business-context.md`: authorization, retention, audit evidence | [Verified Fact] title; holder [Unknown] |
| SH-07 | Integration lead | Architecture, data, engineering | **R** | Medium [Inference] | High [Inference] | `business-context.md`: delivery semantics, reconciliation | [Verified Fact] title; holder [Unknown] |
| SH-08 | Technical owner of legacy code / nightly file exchange | Engineering, architecture | **R** (unnamed) | Medium [Inference] | Unknown | `ADR-archived-007.md`: "owner transferred 2024" (to whom: not stated) | [Verified Fact] statement; owner [Unknown] |
| SH-09 | Compliance team | Compliance, risk | **T** | High [Inference] | High | `operations-vs-risk-2024.md`: "refuses automatic closures without verifiable evidence" | [Verified Fact] (as documented) |
| SH-10 | Operations leadership / operations team | Business, operations, leadership | **T** | High [Inference] | High | `business-context.md` ("Operations leadership reports rising exception-handling effort"); `operations-vs-risk-2024.md` (48 h closure); `legacy-operations-history.md` 2024 | [Verified Fact] (as documented) |
| SH-11 | Legal/compliance, IT and domain quality teams (no agreed canonical state definitions) | Compliance, engineering, business | **T** | Medium [Inference] | Medium | `service-boundaries.md` | [Verified Fact] |
| SH-12 | Application team and integration team (disputed root cause of INC-2025-014) | Engineering, architecture, operations | **T** | Medium | High | `operations/incidents/INC-2025-014.md`: "Root cause disputed ... Follow-up owner unknown" | [Verified Fact] |
| SH-13 | Operations case reviewers (end users who review/prioritise work, record decisions locally) | Users, operations | **T** (implied by workflow steps 3-4) | Low individually, High collectively [Inference] | High | `business-context.md` "Existing workflow" | [Inference] |
| SH-14 | Upstream source-system and partner owners (ElectronicBatchRecord, LIMS-QMS, partner file senders) | Data, architecture, external | **T** (systems named, no owners) | Medium [Inference] | Low-Medium | `source-systems-and-constraints.md`; `partner-feed-operations.md` | [Verified Fact] systems; owners [Unknown] |
| SH-15 | Authorised human reviewer for `batch_disposition` (QA release authority) | Compliance, risk, operations | **R** (decision named, role not named) | Very high on that decision [Inference] | Unknown | `domain-assurance.md`: "Decision requiring authorized human review: batch_disposition" | [Verified Fact] requirement; role holder [Unknown] |

### Coverage of required groups

| Required group | Covered by | Status |
|---|---|---|
| Business | SH-03, SH-05, SH-10 | Roles only, unfilled |
| Users | SH-13 | Team implied; no user research or interviews exist ("Interview notes are incomplete", `business-context.md`) |
| Product | SH-01 (proxy), SH-04 | **Gap**: no product owner role is named in any repo document |
| Architecture | SH-01 (proxy), SH-07, SH-08 | Unfilled; ADR-007 owner unnamed |
| Engineering | SH-02, SH-08, SH-12 | No human engineering owner other than SH-01 proxy |
| Data | SH-07, SH-14 | **Gap**: no data owner/steward role named for `data/legacy.sqlite3`, lake or archive documents |
| Security | SH-06 | Unfilled |
| Privacy | SH-06 (retention) | **Gap**: no privacy/DPO role named; data is synthetic (OD-04), so low current exposure |
| Compliance | SH-09, SH-11, SH-15 | Unfilled; Part 11/GxP treatment unconfirmed (A-08, GD-11) |
| Risk | SH-06, SH-09 | Unfilled |
| Operations | SH-03, SH-04, SH-10, SH-13 | Unfilled |
| Leadership | SH-01 (proxy), SH-10 | **Gap**: no executive sponsor, budget holder or steering group evidenced |

Groups marked Gap are **explicitly absent from the evidence** and recorded as governance gaps, not filled.

### Influence / interest grid (agent [Inference], unvalidated)

| | Interest High | Interest Medium/Low |
|---|---|---|
| **Influence High** (manage closely) | SH-01, SH-03, SH-04, SH-06, SH-09, SH-10, SH-15 | none |
| **Influence Medium** (keep informed / consult) | SH-05, SH-07, SH-08, SH-12 | SH-11, SH-14 |
| **Influence Low** (keep informed) | SH-13 | none |

## Evidence References

See `evidence_sources`. Stage 1: `docs/01-engagement/team-charter.md` (role table), `engagement-canvas.md` (role-based stakeholders row), `open-qualification-questions.md` OQ-01, OQ-02.

## Assumptions

- A-02-01: Roles in `business-context.md` are the intended stand-ins for client stakeholders in this synthetic capstone (extends A-ENG-01). Confirm: Engagement lead (Dinesh Naik).
- A-02-02: Influence/interest ratings are judgement, not measurement. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-02-01 Whether any role holder exists (even as a role-played persona). U-02-02 Who received ADR-007 ownership in 2024. U-02-03 Whether an executive sponsor, product owner, data owner or privacy role is intended.

## Unresolved Issues

- Product, data, privacy and leadership groups have no named role. Owner: Engagement lead (Dinesh Naik) to waive or define (Decision D-02-01 in `operating-contract-confirmations.md`).

## Residual Risks

- Treating role titles as if real people were consulted would overstate validation (ER-01, ER-02).
- Influence ratings may mis-prioritise engagement if a role is later staffed differently.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial stakeholder map. |
