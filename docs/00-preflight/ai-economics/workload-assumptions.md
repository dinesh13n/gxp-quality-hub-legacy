---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "workload-assumptions.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/discovery-summary.md", "docs/00-preflight/discovery/data-flow-overview.md DF-01,DF-06", "docs/00-preflight/discovery/workflow-overview.md", "docs/00-preflight/discovery/assumptions-unknowns.md U-24", "docs/operations-service-levels.md", "data/legacy.sqlite3 (read-only row counts)", "data/lake/bundled/events/*.jsonl (line counts)", "data/lake/tiny, data/archive_documents (file sizes)", ".fde/orchestrator-decisions.md OD-02/OD-04"]
supersedes: "none"
---
## Summary

Workload and volume basis for the 0C envelope. **Current model-call workload is 0 [Verified Fact]** (Stage 0A: no AI/LLM calls; re-grep of `*.py/*.toml/*.yaml` outside docs/data for openai|anthropic|langchain|llm returned no hits). All AI volumes below are therefore *hypothetical derivations* from measured data volumes of a synthetic training simulator and from assumed usage rates. No production volume, user count or seasonality evidence exists (OD-04).

## Findings

| ID | Finding | Class | Value | Source | Confidence |
|---|---|---|---|---|---|
| W-01 | Shipped primary DB holds 125 cases / 125 batch_records / 8,567 partner_feeds rows / 2,400 vendor_file_rows / 145 events / 42 deviations / 21 CAPA / 45 SOP versions / 125 lab_results | Measured (read-only SQLite counts, 2026-10-17) | see left | `data/legacy.sqlite3` | High (but test-residue; DF-01/R-03) |
| W-02 | Documented alternative dataset = 6,000 cases (seed 4326); regenerable, not shipped | Measured (documented in README; reproduced in 0A isolated copy) | 6,000 cases | `discovery-summary.md`, OD-02 | High |
| W-03 | `operating_costs` covers 36 months (2023-01..2025-12) | Measured | 36 months | DF-06 | High (synthetic, modelled) |
| W-04 | Bundled lake: 60 monthly files x 1,667 lines = ~100,020 events; 5-year span | Measured (line counts, `wc`) | 1,667 events/month | `data/lake/bundled/events/` | High |
| W-05 | Document corpus: 1,200 source documents (jsonl, mean ~274 bytes), 420 archive docs (mean 338 bytes, max 478), 210 eml + 210 html fixtures | Measured (file sizes) | ~1,620 docs, tiny | `data/archive_documents`, `data/documents` | High |
| W-06 | Case mix: urgent 2/125 (shipped) and 159/6,000 (regenerated) | Measured (`app.baseline`, 0A) | 1.6% / 2.65% | `discovery-summary.md` | High |
| W-07 | Human effort baseline `hours_per_case` 0.603 (125) / 0.601 (6,000) | Measured **from a synthetic generator formula** (not real effort) | ~0.6 h | DF-06, `app/generate.py` L40-42 | Low for business use |
| W-08 | Historical working targets: 99.5% scheduled-hour availability; overnight reconciliation before 06:00 local; unmeasured | Verified Fact (doc says historic, unmeasured) | - | `docs/operations-service-levels.md`, U-23 | Medium |
| W-09 | Real users, request rates, seasonality, growth, case arrival rates | [Unknown] | - | none in repo (U-24) | - |
| W-10 | Monthly case rate Low/Base/High = 4 / 167 / 1,670 | Assumed (125/36; 6,000/36; 10x) | derived | W-01..W-03 | Low |
| W-11 | Seasonality: month-end reconciliation spike and quarter-end KPI review are *documented concepts* (`docs/business-context.md` journey step 5) but magnitude Unknown; modelled as a peak factor 3x on the last 2 working days of month (Assumed) for latency/capacity sizing only | Assumed | 3x peak | workflow-overview WF-08/WF-09 | Low |
| W-12 | Interactive users: assumed 5 (Low), 15 (Base), 60 (High) reviewers; 20 Q&A queries/user/month x users gives query volume | Assumed | see volume-assumptions.md | - | Low |

## Evidence References

`docs/00-preflight/discovery/discovery-summary.md`; `data-flow-overview.md`; `workflow-overview.md`; `assumptions-unknowns.md`; `.fde/orchestrator-decisions.md`; read-only counts from `data/legacy.sqlite3` (opened `mode=ro`); file-size statistics from `data/` via stat only. No application code was run in this stage.

## Assumptions

- A-C01 Monthly volumes W-10 / W-12 are planning placeholders. Confirm: Engagement lead (Dinesh Naik) with Quality operations lead; resolving stage 4/5.
- A-C02 The 36-month window applies to both 125- and 6,000-case tiers. Confirm: Engagement lead (Dinesh Naik); stage 4.
- A-C03 Peak factor 3x (W-11). Confirm: Enterprise application owner; stage 5/31.

## Unknowns

- U-C01 Real case arrival rates, users, concurrency, growth (extends U-24). Owner: Engagement lead (Dinesh Naik); stage 4/5.
- U-C02 Which dataset (125 vs 6,000) is the baseline (U-13) - changes cost by ~40x at case level.

## Unresolved Issues

- Baseline dataset decision (OD-02 provisional default; U-13) remains open; this document shows both tiers.
- Shipped DB internal incoherence (8,394 orphan partner_feeds refs) limits any volume inference.

## Residual Risks

- Anchoring on synthetic volumes could under- or over-size real production by an order of magnitude (R-03, R-15).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
