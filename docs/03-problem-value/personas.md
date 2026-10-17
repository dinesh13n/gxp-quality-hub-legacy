---
stage: "3 — Frame Problem & Value"
artifact: "personas.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "docs/02-stakeholders/stakeholder-map.md", "docs/02-stakeholders/stakeholder-needs-matrix.md", "docs/legacy-operations-history.md", "docs/domain-assurance.md", "operations/incidents/INC-2025-014.md"]
supersedes: "none"
---
## Summary

Seven role-based personas derived **only from role titles and documented statements** (no interviews, no named people, no usage data). They are documentary models, not observed users. Label: synthetic, unvalidated. Each persona's "holder" is unfilled except where noted; Dinesh Naik is the only human in the engagement.

## Findings

| ID | Persona (role) | Maps to | Context and goals (source) | Pain (claimed) | Evidence | Class | Conf. |
|---|---|---|---|---|---|---|---|
| PER-01 | Case reviewer (operations) | SH-13 | Reviews and prioritises work, records decisions locally (`business-context.md` workflow 3-4) | Manual reconciliation (spreadsheet in INC-2025-014); differing "closed" meaning | `business-context.md`; `INC-2025-014.md` | [Inference] | Low |
| PER-02 | Quality operations lead | SH-03, SH-10 | Throughput, handling time, case quality; close deviation/CAPA within 48 h | Exception effort; compliance limits on closure | `business-context.md`; `operations-vs-risk-2024.md` | [Verified Fact] (stated) | Medium |
| PER-03 | Compliance / risk-and-security reviewer | SH-06, SH-09 | Authorisation, retention, audit evidence; no automatic closure without verifiable evidence | Cannot show evidence-complete decisions; unauthenticated services (0A SO-01..03) | same; `domain-assurance.md` | [Verified Fact] (stated) | Medium |
| PER-04 | Finance partner | SH-05 | Case cost and avoidable rework; faster month-end reconciliation | No agreed "successfully resolved"; cut-off mismatch | `business-context.md`; `historic-decisions.md` 2024; `legacy-operations-history.md` | [Verified Fact] (stated) | Medium |
| PER-05 | Integration lead / owner | SH-07, SH-12, SH-14 | Delivery semantics and reconciliation | Replays, delays, schema revisions 1.0/1.1/2.0/unsupported; disputed root cause | `business-context.md`; `INC-2025-014.md`; 0A IO-03 | [Verified Fact] (stated) | Medium |
| PER-06 | Enterprise application owner | SH-04, SH-08 | Uptime, interfaces, release process | Fear of repeat rollback; owner of nightly exchange unnamed (ADR-007) | `business-context.md`; `ADR-archived-007.md` | [Verified Fact] (stated) | Medium-Low |
| PER-07 | Authorised batch-disposition reviewer | SH-15 | Makes the disposition decision; existing human gates must be preserved | Any automation or simulation of the decision | `domain-assurance.md` | [Verified Fact] (requirement), holder [Unknown] | Medium |
| PER-08 | Engagement lead (Dinesh Naik) | SH-01 | Determine and justify any intervention through evidence | Single-approver load; unvalidated claims inflating the case | `.fde/orchestrator-decisions.md`; ER-01, ER-11 | [Verified Fact] | High |

### Persona gaps

- Source/partner owners (SH-14), legacy-customer workflow owners (SC-07) and the person who made the 2022 manual-reconciliation agreement are unspecified: [Unknown].
- No persona count, volume or seniority is evidenced (U-03-04).

## Evidence References

As per rows. Stage 2 `stakeholder-map.md` SH-IDs.

## Assumptions

- A-03-02: Role descriptions in the synthetic docs approximate real needs. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-03-04 Headcount per role, shift patterns (night-shift batch exists, 0A WF), seniority.

## Unresolved Issues

- Personas cannot be validated; the only available validation is Dinesh's judgement.

## Residual Risks

- Designing for personas nobody holds (ER-01).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial personas. |
