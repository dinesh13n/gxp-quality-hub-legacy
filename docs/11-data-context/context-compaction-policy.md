---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "context-compaction-policy.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md OD-08", "docs/11-data-context/context-engineering-strategy.md", "docs/09-initial-prd/functional-requirements.md FR-DEC-01, FR-DEC-02, FR-CO-04", "docs/09-initial-prd/nfrs.md PNFR-10, PNFR-17", "docs/10-architecture/adrs/ADR-004-data-store-and-event-model.md", "docs/00-preflight/ai-economics/provisional-context-budget.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** **Model-context compaction: NOT APPLICABLE** (no context window exists, OD-08). The product must also **not** perform lossy summarisation of records, because decision history is append-only and must reconstruct state (FR-DEC-01/02) and no deletion is allowed while retention is unset (PNFR-10, OPD-09). This policy therefore records a **"no lossy compaction" rule** and defines the only permitted *lossless* space/volume measures.

## Findings

| ID | Finding / rule | Basis | Class |
|---|---|---|---|
| CP-01 | No context window, history or scratchpad exists; no compaction of conversational context is designed. | OD-08; CE-01 | [VF] decision |
| CP-02 | **Prohibited:** summarising, truncating-and-discarding, deduplicating-by-similarity, or overwriting decision events, raw intake, audit records, or documents. | FR-DEC-01; ADR-004; PNFR-10 | [INF] |
| CP-03 | **Permitted (lossless, reversible):** (a) projections/materialised views rebuilt from events (verification test = rebuild equals stored); (b) FTS index rebuild from sources; (c) SQLite `VACUUM`/WAL checkpoint (no logical change); (d) compressed *copies* for backup with checksum manifest, original retained. | ADR-004; PNFR-05 | [INF] |
| CP-04 | **Permitted display-only truncation:** field-length limits in UI with hash and link to full text (CX-5); the stored value is untouched. | context-engineering CX-5 | [INF] |
| CP-05 | **Deferred:** archival/tiering of old data, event-snapshot checkpoints (snapshot every N events with hash) and deletion are blocked until a retention policy is adopted (OPD-09, owner open). Snapshots, if later added, must be derivable and verifiable from events. | OPD-09 | [UNK] policy |
| CP-06 | Volume reality: 125 cases, 145 events, 8,567 feeds, 12,500 enterprise objects; whole estate about 17.5 MB of SQLite plus about 33 MB lake; there is no measured storage pressure. | `ls -la data` this stage (legacy 8.3 MB, enterprise 9.2 MB; lake bundled 30 MB, tiny 2.8 MB) | [VF] |
| CP-07 | Quarantine/backlog items are never "compacted away"; unresolved work is reported as outstanding (FR-RUN-03). | PRD | [INF] |

### If OD-08 were ever reversed

Any model-context compaction would need its own design under a new Stage 8 qualification; it must keep citations to original source ids intact and be tested for loss of those ids. Not designed here.

## Evidence References

`ls -la data` (file sizes); `du -sh data/lake/*`; ADR-004; FR-DEC-01/02.

## Assumptions

- A-11-14: At the stated volumes no space-saving measure is needed for R1/R2. Confirm: Engagement lead (Dinesh Naik), Stage 31/33 after load measurement.

## Unknowns

- U-11-21 Real production volumes (volume-assumptions are Assumptions). U-11-22 Retention/archival rules (OPD-09).

## Unresolved Issues

- Archival and snapshot policy deferred to the retention decision (Stage 25).

## Residual Risks

- DR-13 (retention unset), DR-17 (unbounded growth if volumes are far higher than assumed).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Recorded N/A; lossless-only compaction rules. |
