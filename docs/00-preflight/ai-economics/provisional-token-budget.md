---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "provisional-token-budget.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["workload-assumptions.md", "volume-assumptions.md", "data/archive_documents/* sizes", "data/lake/bundled/events/*.jsonl sizes", "app/legacy_logic.py"]
supersedes: "none"
---
## Summary

PROVISIONAL per-request token ceilings (design constraints for Stages 10/19/22 until Stage 8 decides whether AI remains applicable). Ceilings are set at ~2x the Assumed expected usage to absorb the 1.6x high multiplier plus headroom.

## Findings

| Limit | Value | Rationale / basis |
|---|---|---|
| TB-01 T1 triage: input max / output max | 3,000 / 500 | 2.5x/2x of expected 1,200/250 |
| TB-02 T2 feed classification: input / output | 1,200 / 150 | expected 500/80 |
| TB-03 T3 Q&A: input / output | 5,000 / 600 | expected 2,050/300 |
| TB-04 T4 narrative draft: input / output | 6,000 / 1,500 | expected 2,500/700 |
| TB-05 T5 investigation: cumulative tokens per investigation | 40,000 in / 2,000 out | expected 24,000/900 at n=6; n=8 would be 38,400/1,200 |
| TB-06 Per-case aggregate (all calls incl. retries) | 50,000 total tokens | hard stop, then route to human |
| TB-07 Max cost per request | USD 0.05 (single-pass), USD 0.25 (T5 investigation) | ~2x worst-case modelled (0.033 and 0.157) |
| TB-08 Max cost per case | USD 0.30 | see cost-per-case rationale in `quality-latency-cost-envelope.md`; ~2% of assumed human handling cost USD 15/case |
| TB-09 Monthly token spend alert / hard cap (Base tier) | USD 50 / USD 150 | ~6x / ~19x Base expected; Low-volume tiers well inside |
| TB-10 Output must be schema-bound (JSON) with max_tokens enforced | mandatory | prevents runaway output |

Enforcement is by design constraint only: **no code exists and none may be written in this stage**.

## Evidence References

`token-flow-scenarios.md`; `cost-scenarios.md`.

## Assumptions

- A-B01 Budgets scale with the Assumed token flows; re-derive after first prototype measurement.

## Unknowns

- U-B01 Approved cost authority / budget owner - none exists.

## Unresolved Issues

- Budget owner and funding source (Engagement lead (Dinesh Naik); stage 1).

## Residual Risks

- Caps set too tight may force quality degradation; too loose provides no protection. Calibrate in Stage 19/22.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
