---
stage: "3 — Frame Problem & Value"
artifact: "scope-exclusions.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "docs/00-preflight/operating-contract/scope-boundaries.md", "docs/domain-assurance.md", "docs/01-engagement/engagement-go-no-go.md", "docs/02-stakeholders/decision-rights-map.md", "docs/legacy-operations-history.md"]
supersedes: "none"
---
## Summary

Problem-scope boundary (what the problem framing covers), not solution scope. Exclusions protect against encoding unowned rules and against automated GxP decisions. Scope is provisional until Dinesh Naik confirms (no client sponsor).

## Findings

### In scope (problem space)

| ID | Item | Basis |
|---|---|---|
| IN-01 | Pharma batch-deviation / CAPA case handling from external message receipt to recorded decision and monthly review | `business-context.md` workflow steps 1-5 |
| IN-02 | Consistency of case information between external feeds and the core record | `business-context.md` "Operating concern"; 0A IO-01..05 |
| IN-03 | Definitions and measurement of closed / resolved / approved as a **decision to be made**, and measurement of each candidate meaning | SC-01..03 |
| IN-04 | Evidence availability and attribution for case decisions | `domain-assurance.md` |
| IN-05 | Cost and rework measurement per case, month-end comparability | `business-context.md` Finance partner; SC-04 |
| IN-06 | Preservation of existing human approval gates and legitimate workflows | `domain-assurance.md`; `business-context.md` "Transformation scope" |

### Out of scope

| ID | Exclusion | Reason |
|---|---|---|
| EX-01 | Choosing or imposing a definition of "closed"/"resolved", the 48 h rule, or approval thresholds | No owner (DR-20, DR-21, DR-23); CG-7 |
| EX-02 | Making, simulating or automating `batch_disposition` or any GxP release decision | HAR-12 / STOP-07; DR-22 |
| EX-03 | Any solution, technology, model or AI choice | Stage 8+ decision; stage guardrail |
| EX-04 | Retiring the parallel workflow kept for older customers | Owner unknown (SC-07) |
| EX-05 | Treating 21 CFR Part 11 as a binding obligation on this repo | Framing only (A-08, GD-11) |
| EX-06 | Archived enterprise estate and lake as separate data models (no join) unless Stage 5 shows need | DF-09, DF-10 |
| EX-07 | Real production systems, real people, real data | OD-04 |
| EX-08 | Security remediation of unauthenticated services (tracked as NFR gaps, solved in later stages) | 0A SO-01..03 |

### Ambiguities (not resolved)

- Whether the engagement's true objective is modernisation, AI or both (SCOPE-AMB-04, U-E02).
- Whether `legacy.sqlite3` (125 cases) or the regenerable 6,000-case dataset is the baseline (OD-02, provisional).

## Evidence References

As listed in `evidence_sources`.

## Assumptions

- A-03-07: The five-step workflow bounds the process. A-03-08: OD-02 baseline stays provisional.

## Unknowns

- U-03-08 Other sites/regions in scope ("multi-region", `business-context.md`).

## Unresolved Issues

- Exclusion EX-01 means the problem cannot be "solved" here; it can only be framed and measured.

## Residual Risks

- Scope creep into policy decisions by an engineering stage.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial scope. |
