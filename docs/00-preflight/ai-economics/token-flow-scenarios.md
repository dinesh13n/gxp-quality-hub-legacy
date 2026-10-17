---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "token-flow-scenarios.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["workload-assumptions.md", "volume-assumptions.md", "data/archive_documents/* sizes", "data/lake/bundled/events/*.jsonl sizes", "app/legacy_logic.py"]
supersedes: "none"
---
## Summary

Token flow per scenario and step. Token counts for single-pass calls are built from **measured byte sizes of repository records / 4 bytes per token (Assumed)** plus **assumed** prompt overhead. Agent-loop tokens follow a stated formula, not a measurement.

## Findings

S0/S1/S2: 0 tokens [Verified Fact: no model calls].

**Single-pass touchpoints (S3, S4)**

| ID | Touchpoint | Tier | Input tok (Assumed) | Output tok (Assumed) | Total |
|---|---|---|---|---|---|
| Case triage explanation / review summary | T1 | M | 1,200 | 250 | 1,450 |
| Partner-feed exception classification | T2 | S | 500 | 80 | 580 |
| Document Q&A (RAG over source+archive docs) | T3 | M | 2,050 | 300 | 2,350 |
| Deviation/CAPA narrative draft | T4 | M | 2,500 | 700 | 3,200 |

Input composition (Assumed unless noted): system+guardrail prompt ~600; task instruction ~100; record payload (T1 ~300: case row + ~1.2 events, record sizes are small in the synthetic data; T2 ~250; T4 ~1,800 incl. deviation+CAPA+SOP excerpts); retrieval T3 = top-5 x ~270 tokens (+ 50 question). Synthetic stubs are ~70-100 tokens per document [Measured sizes/4]; retrieval chunk size is set to a realistic 270 because real SOPs will be larger (Assumption, U-V02).

**Agentic loop (S4, T5)** - formula (Assumed parameters): base context B=2,000 (system+case), each tool result adds R=800, output per step 150. Input tokens over n steps = n*B + R*n(n-1)/2 (the whole context is re-sent each step, no caching); output = 150n.

| Steps n | Input tokens | Output tokens | Cost per investigation USD (Tier M, list) |
|---|---|---|---|
| 1 | 2,000 | 150 | 0.0083 |
| 2 | 4,800 | 300 | 0.0189 |
| 3 | 8,400 | 450 | 0.0319 |
| 4 | 12,800 | 600 | 0.0474 |
| 5 | 18,000 | 750 | 0.0653 |
| 6 | 24,000 | 900 | 0.0855 |
| 7 | 30,800 | 1,050 | 0.1081 |
| 8 | 38,400 | 1,200 | 0.1332 |

Avg planned n=6: 24,000 in / 900 out. [Inference] Tokens grow quadratically in steps: going from 6 to 8 steps raises input by 60%. This is the reason for the hard loop cap in `provisional-loop-budget.md`.

**Retry/failure overhead (Assumed)**: +2% / +5% / +15% (low/mid/high) of tokens for schema-validation failures and transient errors; no measured failure rate exists (no telemetry, R-14).

**Prompt-caching sensitivity (Assumed)**: a cached static prefix (~600-2,000 tokens) could cut input cost materially; not assumed in the base, captured in the low-case price multiplier 0.5.

## Evidence References

Formulae above; byte sizes from `data/` (stat); `workload-assumptions.md` W-05.

## Assumptions

- A-T01 4 bytes/token. A-T02 prompt overhead 600 tokens. A-T03 loop parameters B, R, output/step. Confirm by prototype measurement in Stage 10/19; owner Engagement lead (Dinesh Naik).

## Unknowns

- U-T01 Real tokenisation of multilingual text (DF-05 multilingual fields). U-T02 Real tool-result sizes.

## Unresolved Issues

- None blocking.

## Residual Risks

- Quadratic growth means a single mis-tuned agent could exceed budgets by 5-10x without caps.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
