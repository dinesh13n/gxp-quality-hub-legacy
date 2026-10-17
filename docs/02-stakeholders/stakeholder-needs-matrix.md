---
stage: "2 — Stakeholder Discovery & Authority Confirmation"
artifact: "stakeholder-needs-matrix.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md", "docs/legacy-operations-history.md", "docs/domain-assurance.md", "docs/operations-service-levels.md", "docs/service-boundaries.md", "operations/incidents/INC-2025-014.md", "docs/02-stakeholders/stakeholder-map.md"]
supersedes: "none"
---
## Summary

Needs, incentives, concerns and responsibilities per stakeholder. **Needs stated in a repo document are [Verified Fact] that the statement exists, not that the stakeholder holds it** (synthetic documents, no interviews). Incentives and concerns are [Inference] unless the source states them. "Resistance" is predicted, not observed. Feeds Stage 3 (problem framing), Stage 4 (KPI owners).

## Findings

| ID | Stakeholder | Stated need / responsibility (source) | Incentive [Inference] | Concern / likely resistance [Inference unless cited] | Link to KPI (Stage 4) | Confidence |
|---|---|---|---|---|---|---|
| SH-01 | Dinesh Naik | Determine and justify any modernisation or AI intervention through evidence, preserving legitimate workflows (`business-context.md` "Transformation scope") | Complete a defensible capstone with honest evidence | Single-approver load across 46 stages (ER-11); unvalidated claims inflating the case (ER-01) | All (owner by default) | High (he is the only human) |
| SH-03 | Quality operations lead | Throughput, handling time, case quality (`business-context.md`); close deviation/CAPA within 48 h (`operations-vs-risk-2024.md`) | Faster closure, less exception effort | Change that slows closure or removes local workflows ("parallel workflow retained for older customers", `legacy-operations-history.md` 2024) | Handling time, throughput, case quality | Medium |
| SH-04 | Enterprise application owner | Uptime, interfaces, release process (`business-context.md`) | Stability; avoid repeat of rolled-back release (`historic-decisions.md` 2025) | Release risk; 2025 migration paused over compatibility (`legacy-operations-history.md`) | Availability (archived 99.5 % target, unmeasured), interface health | Medium |
| SH-05 | Finance partner | Case cost and avoidable rework (`business-context.md`); faster month-end reconciliation (`historic-decisions.md` 2024); "successfully resolved" not agreed (`operations-vs-risk-2024.md`) | Predictable cost, quicker close | Extra evidence steps raise cost; monthly cut-offs differ from operations reports (`legacy-operations-history.md`) | Case cost, rework rate | Medium |
| SH-06 | Risk and security partner | Authorisation, retention, audit evidence (`business-context.md`); more supporting evidence (`historic-decisions.md` 2024) | Defensible audit trail | Automation without verifiable evidence; unauthenticated services (SO-01..03 in 0A); Part 11 framing (A-08) | Time to evidence, unsafe action count (`domain-assurance.md`) | Medium |
| SH-07 | Integration lead | Delivery semantics and reconciliation (`business-context.md`) | Fewer replay/duplicate incidents | Replay inflating queues (2025 rollback); schema revisions 1.0/1.1/2.0 and unsupported variants (`source-systems-and-constraints.md`) | Reconciliation delay, orphan references | Medium |
| SH-08 | Technical owner of legacy code | Not stated; ADR-007 keeps nightly file exchange, owner transferred 2024 (`ADR-archived-007.md`) | Unknown | Unknown; diagram still shows obsolete endpoint | n/a | Low |
| SH-09 | Compliance team | No automatic closures without verifiable evidence (`operations-vs-risk-2024.md`) | Audit defensibility | Any 48 h auto-close rule; AI-driven closure (links to HAR-12) | Unsafe action count, time to evidence | Medium |
| SH-10 | Operations leadership | Reports rising exception-handling effort and inconsistent feed/core data (`business-context.md`) | Lower effort, one consistent view | Compliance veto on closure speed; undefined "closed" | Exception rate, backlog aging | Medium |
| SH-11 | Legal/compliance, IT, domain quality teams | Canonical state definitions not agreed (`service-boundaries.md`) | Unknown | Definitions imposed without agreement | Definition of "closed" (OQ-05) | Low |
| SH-12 | Application and integration teams | Root cause of INC-2025-014 disputed; follow-up owner unknown (`INC-2025-014.md`) | Avoid blame | Ownership of reconciliation defects | Reconciliation delay | Low-Medium |
| SH-13 | Operations case reviewers | Review, prioritise, record decisions locally (`business-context.md` workflow 3-4) | Less manual reconciliation (manual spreadsheet used, INC-2025-014) | Loss of local practice; local 'closed' interpretations differ (`business-context.md`) | Handling time | Low |
| SH-14 | Source/partner owners | Systems publish OOS_RESULT, DEVIATION, CAPA_UPDATE (`source-systems-and-constraints.md`) | Unknown | Replays and schema revisions are theirs to fix; internal feeds not trusted as approvals (`partner-feed-operations.md`) | Feed acceptance (archived 4 h, unmeasured) | Low |
| SH-15 | Authorised batch-disposition reviewer | `batch_disposition` requires authorised human review; preserve existing human approval gates (`domain-assurance.md`) | Patient/product safety, regulatory defence | Any automation or simulation of disposition | Unsafe action count (must stay 0) | Medium (requirement), Low (holder) |

### Cross-cutting needs (Verified Fact: stated; Inference: weighting)

1. Common definitions of "closed" and "resolved" (all of SH-03, SH-05, SH-09, SH-11).
2. Evidence-backed, source-attributed decisions (SH-06, SH-09, SH-15; `domain-assurance.md`).
3. Reconciliation correctness and replay safety (SH-04, SH-07, SH-12).
4. Preserve legitimate workflows and human approval gates (`business-context.md`, `domain-assurance.md`).

## Evidence References

As cited per row. No interview notes, survey or ticket data exist ("Interview notes are incomplete", `business-context.md`).

## Assumptions

- A-02-03: Incentives and likely resistance are inferred from role descriptions and documented disputes. Confirm: Engagement lead (Dinesh Naik) or, if ever staffed, the role holder.

## Unknowns

- U-02-04 Actual priorities and weighting of each role. U-02-05 Needs of SH-08 and SH-14 (not stated anywhere).

## Unresolved Issues

- No needs have been validated with a human other than SH-01. Stage 3 must label stakeholder pain as "claimed in synthetic repo documents".

## Residual Risks

- Needs matrix is a documentary model; it may drive a problem statement nobody holds (ER-01).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial needs matrix. |
