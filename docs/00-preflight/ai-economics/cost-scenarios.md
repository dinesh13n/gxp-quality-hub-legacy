---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "cost-scenarios.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["token-flow-scenarios.md", "volume-assumptions.md", "data/legacy.sqlite3 baseline (app.baseline hours_per_case 0.603, synthetic)", "docs/00-preflight/discovery/data-flow-overview.md DF-06"]
supersedes: "none"
---
## Summary

Cost per request, per case and per month for S0-S4 with ranges. **Token price is a dated ASSUMPTION** (see below); every other input is Assumed unless noted. Headline [Inference]: at every modelled volume tier, monthly token spend is under USD 137 (worst case) and is dwarfed by assumed infrastructure, human oversight and build effort - **cost does not differentiate AI from non-AI here; risk and effort do.** This is not a conclusion that AI is justified (Stage 8 decides).

## Findings

**Price assumption (A-P01)**: indicative public list-price bands per 1M tokens (input/output), USD, as of 2026-10-17: Tier S (0.25, 1.25), Tier M (3.0, 15.0), Tier L (15.0, 75.0). **Source: agent's general knowledge of vendor list-price bands; NOT verified against a dated vendor price page in this stage (no web lookup; no platform chosen).** Must be replaced by a cited vendor page (e.g., Azure OpenAI / Foundry pricing, the user's usual platform [Inference from engagement profile]) in Stage 8/10. Ranges: Low = 0.7x tokens, 2% retry, 0.5x price (cache/batch discount); Mid = 1.0x, 5%; High = 1.6x, 15%, list price.

**Cost per request, USD (Tier M unless T2 = Tier S)**

| Touchpoint | Low | Mid | High |
|---|---|---|---|
| T1 Case triage explanation / review summary | 0.0026 | 0.0077 | 0.0135 |
| T2 Partner-feed exception classification | 0.0001 | 0.0002 | 0.0004 |
| T3 Document Q&A (RAG over source+archive docs) | 0.0038 | 0.0112 | 0.0196 |
| T4 Deviation/CAPA narrative draft | 0.0064 | 0.0189 | 0.0331 |
| T5 Agentic investigation (6 steps) | 0.0305 | 0.0898 | 0.1573 |

**Cost per case, token only, USD** (T1, plus 10% x T5 for S4)

| Scenario | Low | Mid | High |
|---|---|---|---|
| S0 | 0.0000 | 0.0000 | 0.0000 |
| S1 | 0.0000 | 0.0000 | 0.0000 |
| S2 | 0.0000 | 0.0000 | 0.0000 |
| S3 | 0.0026 | 0.0077 | 0.0135 |
| S4 | 0.0057 | 0.0167 | 0.0293 |

Human-handling reference (S0): 0.601 h/case [Measured from synthetic generator, W-07] x USD 25/h [Assumed loaded rate] = **USD 15.02/case** (indicative only; real value Unknown, U-24).

**Monthly run cost** (token + assumed infrastructure + assumed oversight; oversight = reviewer minutes per output (T1 2, T2 1, T3 0.5, T4 10, T5 5 minutes) x USD 25/h, scaled 0.6/1/1.5 across range). S0 increments are zero because its human effort is the baseline, not an increment (shown per case above).

| Scenario | Volume tier | Token cost/mo (lo / mid / hi) | Infra/mo (lo/mid/hi) | Human oversight/mo (mid rate) | Total run/mo (lo / mid / hi) |
|---|---|---|---|---|---|
| S0 | Low | 0 / 0 / 0 | 0 / 0 / 0 | 0 (baseline manual effort not an increment) | 0 / 0 / 0 |
| S0 | Base | 0 / 0 / 0 | 0 / 0 / 0 | 0 (baseline manual effort not an increment) | 0 / 0 / 0 |
| S0 | High | 0 / 0 / 0 | 0 / 0 / 0 | 0 (baseline manual effort not an increment) | 0 / 0 / 0 |
| S1 | Low | 0.00 / 0.00 / 0.00 | 20 / 40 / 100 | 0 | 20 / 40 / 100 |
| S1 | Base | 0.00 / 0.00 / 0.00 | 20 / 40 / 100 | 0 | 20 / 40 / 100 |
| S1 | High | 0.00 / 0.00 / 0.00 | 20 / 40 / 100 | 0 | 20 / 40 / 100 |
| S2 | Low | 0.00 / 0.00 / 0.00 | 40 / 80 / 200 | 0 | 40 / 80 / 200 |
| S2 | Base | 0.00 / 0.00 / 0.00 | 40 / 80 / 200 | 0 | 40 / 80 / 200 |
| S2 | High | 0.00 / 0.00 / 0.00 | 40 / 80 / 200 | 0 | 40 / 80 / 200 |
| S3 | Low | 1.55 / 4.56 / 7.98 | 120 / 250 / 600 | 120 | 193 / 374 / 788 |
| S3 | Base | 2.15 / 6.32 / 11.07 | 120 / 250 / 600 | 276 | 288 / 533 / 1026 |
| S3 | High | 21.48 / 63.18 / 110.71 | 120 / 250 / 600 | 2765 | 1800 / 3078 / 4858 |
| S4 | Low | 1.56 / 4.59 / 8.05 | 200 / 400 / 1000 | 121 | 274 / 525 / 1189 |
| S4 | Base | 2.66 / 7.82 / 13.70 | 200 / 400 / 1000 | 311 | 389 / 719 / 1481 |
| S4 | High | 26.58 / 78.17 / 136.98 | 200 / 400 / 1000 | 3112 | 2094 / 3591 / 5806 |

**Anti-pattern quantified (naive full-lake pass)**: sending all 100,020 lake events through an LLM once at 500 in / 80 out tokens costs USD 23 (Tier S), USD 270 (Tier M), USD 1350 (Tier L) - plus quality risk; deterministic normalisation (S2) costs ~0 tokens. [Inference] Do not design batch LLM over the whole lake.

**Sensitivity [Inference]**: token cost is linear in volume, tokens and price; moving Base to High (10x) adds < USD 130/month at list price. The largest levers are (1) reviewer minutes per output (each +1 min/case = +USD 70/month at Base), (2) agent steps (quadratic), (3) real document size (10-100x on T3/T4 inputs, U-V02).

## Evidence References

`token-flow-scenarios.md`; `volume-assumptions.md`; assumptions recorded in `preliminary-finops-baseline.md`.

## Assumptions

- A-P01 prices (above). A-P02 infrastructure per month by scenario: S1 20/40/100, S2 40/80/200, S3 120/250/600, S4 200/400/1000 (lo/mid/hi, USD; Azure-class managed services, not quoted). A-P03 loaded reviewer rate USD 25/h. A-P04 reviewer minutes per output as shown. All owners: Engagement lead (Dinesh Naik); confirm with Finance partner at Stage 4/8.

## Unknowns

- U-P01 Actual platform, region, contract discounts, PTU/reserved capacity. U-P02 Real labour cost. U-P03 Real infrastructure quote.

## Unresolved Issues

- Price verification (A-P01) is required before any figure is quoted outside this envelope.

## Residual Risks

- Currency/price volatility; token pricing changes frequently. Human-oversight cost may dominate and is the least certain input.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
