---
stage: "3 — Frame Problem & Value"
artifact: "user-journeys.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/business-context.md", "docs/legacy-operations-history.md", "docs/partner-feed-operations.md", "docs/00-preflight/discovery/workflow-overview.md", "docs/00-preflight/discovery/integration-overview.md", "operations/incidents/INC-2025-014.md", "docs/historic-decisions.md"]
supersedes: "none"
---
## Summary

Current-state journeys reconstructed from the five-step workflow in `docs/business-context.md` and Stage 0A workflow/integration findings. **Not observed**: no shadowing, no interviews. Pain points are marked claimed (documents) or inferred (structure). Label: synthetic, unvalidated.

## Findings

### J1 — Case from external message to local decision (persona PER-01, PER-05)

| Step | What happens (source) | Pain point | Class |
|---|---|---|---|
| 1 External source produces case message | MES/LIMS/QMS/partner messages; schema rev 1.0/1.1/2.0/unsupported (`source-systems-and-constraints.md`; 0A IO-01, IO-03) | Variants and an "unsupported" revision exist | [Verified Fact] |
| 2 Integration reconciles or imports | Gateway pull with no retry/backoff; partner rows processed by status with in-place mutation; contract unenforced (0A IO-02, IO-03, IO-05) | Drops, replays, status overwritten (no history) | [Verified Fact] (code), [Inference] (business effect) |
| 3 Operations review and prioritise | Reviewer sees imported items (`business-context.md` step 3) | Orphan references (8,394 of 8,567 on the synthetic DB, IO-10); duplicates after replay (2025 rollback) | [Verified Fact] on synthetic data |
| 4 Decision recorded locally | "Local systems"; 'closed' differs by site | Same case classed differently; parallel workflow retained for older customers (`legacy-operations-history.md` 2024) | [Verified Fact] (claim) |
| 5 Monthly review | Operating measures reviewed; finance and operations cut-offs differ | Numbers not comparable (SC-04) | [Verified Fact] (claim) |

### J2 — Delayed or replayed feed incident (PER-05, PER-01, PER-02)

| Step | Source | Pain point |
|---|---|---|
| Feed delayed 03:15 UTC, queue retried twice, totals diverge | `INC-2025-014.md` | Divergence detected by totals, not by a control |
| Manual spreadsheet reconciliation 04:00 UTC | `INC-2025-014.md` | Manual, undocumented effort; time unmeasured |
| Root cause disputed; follow-up owner unknown | `INC-2025-014.md`; SC-06 | No learning loop or owner |
| Earlier: 2025 rollout rolled back after replay inflated queue; "resolved operationally" | `historic-decisions.md` | Resolution not evidenced |

### J3 — Closing a deviation/CAPA case (PER-02, PER-03, PER-04, PER-07)

| Step | Source | Pain point |
|---|---|---|
| Ops aims to close within 48 h | `operations-vs-risk-2024.md` | Clock start/stop undefined [Unknown] |
| Compliance requires verifiable evidence before closure | same | Where evidence lives, who verifies: [Unknown]; audit trail not in code (0A SO-09) |
| Finance asks "resolved?" for cost | same | No agreed definition (SC-02) |
| Batch disposition by authorised human | `domain-assurance.md` | Holder unnamed (DR-22) |

### J4 — Month-end reconciliation (PER-04, PER-02)

Finance wants faster month-end; risk wants more evidence ("both remain active", `historic-decisions.md` 2024). Cut-offs differ (`legacy-operations-history.md`). Effort is **[Unknown]** (U-24 carried).

## Evidence References

As cited. 0A IDs in `docs/00-preflight/discovery/`.

## Assumptions

- A-03-06: The documented five-step workflow is complete enough for framing; step durations and volumes are not available.

## Unknowns

- U-03-06 Step-level time, volume and error rates for every journey. U-03-07 Where "evidence" is stored today.

## Unresolved Issues

- Journeys cannot be validated by users; baseline measurement is Stage 4.

## Residual Risks

- A tidy journey may hide shadow practices (spreadsheets) that matter.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial journeys. |
