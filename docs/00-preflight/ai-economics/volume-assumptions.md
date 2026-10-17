---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "volume-assumptions.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/discovery-summary.md", "docs/00-preflight/discovery/data-flow-overview.md DF-01,DF-06", "docs/00-preflight/discovery/workflow-overview.md", "docs/00-preflight/discovery/assumptions-unknowns.md U-24", "docs/operations-service-levels.md", "data/legacy.sqlite3 (read-only row counts)", "data/lake/bundled/events/*.jsonl (line counts)", "data/lake/tiny, data/archive_documents (file sizes)", ".fde/orchestrator-decisions.md OD-02/OD-04"]
supersedes: "none"
---
## Summary

Volume drivers, tiers and growth for every cost calculation. Three tiers: Low (as-shipped 125-case DB), Base (documented 6,000-case dataset), High (10x Base, a stress assumption). All tiers are Assumed except where a measured source is shown.

## Findings

| Driver | Low | Base | High | Class / source |
|---|---|---|---|---|
| Cases / month | 4 | 167 | 1,670 | Assumed; derived from measured 125 and 6,000 over 36 months (W-01..W-03) |
| Partner-feed rows / month | 238 | 238 | 2,380 | Assumed; 8,567 shipped rows / 36 mo (period actually Unknown) |
| Rows needing exception handling (share of feeds) | 25% | 25% | 25% | Assumed; evidence: every 41st feed lacks business_key (~2.4%) and 86 'SYSTEM NOTE' rows (DF-05/08) suggest the true share is lower - kept conservative |
| Document Q&A queries / month | 400 | 440 | 4,400 | Assumed (users x ~20-29 queries) |
| Deviation/CAPA drafts / month | 2 | 5 | 50 | Assumed; shipped data has 42 deviations / 21 CAPA, period Unknown |
| Share of cases escalated to agentic investigation (S4 only) | 10% | 10% | 10% | Assumed; measured urgent share is 1.6-2.65% so 10% includes review/escalated cases |
| Lake events (reference only) | 1,667/mo | 1,667/mo | 16,670/mo | Measured (Low/Base) |
| Growth | 0%/yr | 10%/yr | 30%/yr | Assumed; no evidence. High tier already 10x |

**Growth sensitivity [Inference]**: token cost scales linearly with volume (tables in `cost-scenarios.md`); human-oversight cost scales linearly too; fixed infrastructure and build effort do not - hence AI unit economics improve only at volume tiers above Base, but Base token spend is already a few USD/month, so growth is not a cost-driver for tokens at any tier modelled.

**One-off backfill volumes (Measured sizes, Assumed token ratio 4 bytes/token)**: 100,020 lake events x ~245 bytes = ~25 MB = ~6.1 M tokens raw; 1,620 documents = ~0.1 M tokens raw. A naive "send every lake event through an LLM" pass is quantified in `cost-scenarios.md` as an anti-pattern.

## Evidence References

`workload-assumptions.md` W-01..W-12; `data/lake/bundled/events/` line counts; `data/archive_documents/` file sizes.

## Assumptions

- A-V01 4 bytes ~ 1 token for English/JSON text; multilingual text (DF-05) and base64/HTML may raise this. Confirm by tokenising a sample with the chosen model in Stage 8/10.
- A-V02 Growth rates are placeholders.

## Unknowns

- U-V01 True seasonality and growth. Owner: Engagement lead (Dinesh Naik); stage 4/31.
- U-V02 Real document size distribution (repo docs are tiny synthetic stubs; real GxP SOP/batch records are typically orders of magnitude larger) - **highest-impact unknown for context budget**.

## Unresolved Issues

- U-V02 unresolved; context budget (`provisional-context-budget.md`) must be revisited when real documents are seen.

## Residual Risks

- Real documents far larger than synthetic stubs would raise T3/T4 input tokens 10-100x [Inference]; envelope would then need re-baselining at Stage 8/10.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
