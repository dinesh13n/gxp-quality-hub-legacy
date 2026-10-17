---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "provisional-context-budget.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["token-flow-scenarios.md", "docs/00-preflight/operating-contract/data-use-constraints.md DU-03,X-4", "docs/00-preflight/discovery/data-flow-overview.md DF-08,DF-09", "docs/00-preflight/discovery/integration-overview.md IO-01..IO-03"]
supersedes: "none"
---
## Summary

PROVISIONAL context-window limits and assembly rules. Model context windows are not the constraint at this scale; **injection exposure and cost amplification** are.

## Findings

| ID | Constraint | Value | Class / basis |
|---|---|---|---|
| CB-01 | Max assembled prompt, single-pass touchpoints | 8,000 tokens | Assumed; ~1.3x largest TB input ceiling (6,000) |
| CB-02 | Max context in agent loop (any single step) | 16,000 tokens, with compaction of older tool results beyond 12,000 | Assumed; expected at step 6 = 2,000 + 800x5 = 6,000 |
| CB-03 | Retrieval: top-k <= 5, chunk <= 400 tokens, de-duplicated, with source id | 5 x 400 | Assumed |
| CB-04 | Context assembly order: fixed system/guardrail prefix (cacheable) > task schema > policy excerpts > retrieved evidence > case record | - | Design assumption |
| CB-05 | All retrieved/record text is wrapped as **untrusted data** and never placed in the instruction channel | mandatory | Verified Fact basis: >=286 embedded instruction-like strings (DF-08); 0B X-4 |
| CB-06 | Per-tenant filtering before retrieval (tenant/`access_level` fields exist but are unenforced today) | mandatory for any retrieval | Verified Fact (SO-02); retrieval must not widen access |
| CB-07 | Cross-store context (legacy.sqlite3 vs enterprise vs lake) cannot be joined by key today (DF-09), so T5 must fetch per-store through tools rather than pre-assembled context | design consequence | Inference |
| CB-08 | Long-context fallback (>32k) not permitted without Stage 8/10 approval | - | Assumed |

Window needed vs available: required windows (<=16k) fit comfortably in any current mainstream model class [Inference; no model chosen]. Risk is therefore **not window size**, but real documents being larger than the synthetic stubs (U-V02).

## Evidence References

`token-flow-scenarios.md`; DF-08, DF-09; 0B data-use-constraints.

## Assumptions

- A-C-01 Chunk size 400 tokens suits SOP-like text. Confirm with real documents (Stage 10/19).

## Unknowns

- U-CB1 Real document length/format (PDF, tables) and OCR needs.

## Unresolved Issues

- Retrieval design (index, tenancy filtering) not specified here; Stage 10.

## Residual Risks

- Prompt-injection through retrieved text (DF-08) is High likelihood x High impact if any LLM is introduced (R-09).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
