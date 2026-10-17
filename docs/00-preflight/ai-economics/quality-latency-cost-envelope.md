---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "quality-latency-cost-envelope.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["cost-scenarios.md", "token-flow-scenarios.md", "docs/operations-service-levels.md", "docs/00-preflight/discovery/workflow-overview.md WF-05,WF-11", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md"]
supersedes: "none"
---
## Summary

Acceptable bounds for quality, latency and cost, expressed as PROVISIONAL design constraints. No user tolerance, SLO or quality measurement exists (R-14, U-23); bounds are derived from documented historic targets, the structure of the workflows and the cost model. Stage 8 decides whether any AI portion survives.

## Findings

| Dimension | Provisional bound | Class | Basis |
|---|---|---|---|
| Cost per request | <= USD 0.05 single-pass; <= USD 0.25 investigation (T5) | Assumed | `provisional-token-budget.md` TB-07 |
| Cost per case (token) | <= USD 0.30 | Assumed | ~2% of USD 15.02 indicative human cost per case (0.601 h synthetic x USD 25/h assumed); 20x headroom over worst modelled 0.029 |
| Total run cost per case (incl. infra + oversight) must be <= human baseline per case | USD 15.02 | Assumed | Base S3 mid: USD 533/167 = USD 3.2/case; S4 mid USD 719/167 = USD 4.3/case - but gross, **benefits (time saved) are Unknown** |
| Interactive latency (T3 Q&A) | p95 <= 8 s end-to-end, first token <= 2 s | Assumed | no user evidence; typical interactive tolerance |
| Case-level synchronous (T1) | p95 <= 10 s | Assumed | same |
| Batch (T2, nightly) | complete before 06:00 local; documented historic target | Verified Fact (doc) / Assumed (still valid, U-23) | `docs/operations-service-levels.md` |
| Agentic investigation | <= 120 s wall-clock, async with notification | Assumed | LB-04 |
| Availability | no AI-specific SLO; AI path must degrade to the deterministic path (S1/S2) without loss of function | Assumed | 99.5% historic is unmeasured |
| Quality - factual grounding | every generated statement traceable to a cited record id; unsupported statements = defect | Assumed target, no baseline | GxP evidence expectations |
| Quality - decision safety | AI output is advisory only; **zero** AI-originated `batch_disposition`/approval/status writes | Verified constraint (WF-05 gap + 0B approval rules) | `provisional-human-approval-rules.md` |
| Quality - injection robustness | 0 of the seeded instruction-like strings (>=286, DF-08) obeyed in a red-team eval | Assumed target | DF-08; threshold to be set in Stage 19/22 |
| Quality metrics thresholds (accuracy, recall, hallucination rate) | Unknown - no labelled data or baseline | Unknown | resolve Stage 4/8 |

**Trade-off envelope [Inference]**: moving from Tier M to Tier S models cuts token cost ~12x but token cost is already <1% of total run cost at Base, so the cost axis offers little leverage; quality and oversight minutes are the binding axes. Moving a touchpoint from sync to async batch relaxes latency with no cost change; agentic loops trade 1.6x tokens (6 to 8 steps) for unknown quality gain.

**Pareto reading**: S1/S2 dominate on cost and latency (no inference latency, near-zero marginal cost); S3/S4 can only win on coverage of unstructured text (T3/T4) - the claim must be proven in Stage 8, not assumed here.

## Evidence References

`cost-scenarios.md`; `provisional-token-budget.md`; `docs/operations-service-levels.md`; 0B approval rules.

## Assumptions

- A-Q01 Latency tolerances. Confirm: Quality operations lead; stage 5. A-Q02 AI advisory-only posture.

## Unknowns

- U-Q01 Quality baselines and acceptance thresholds. U-Q02 Human time saved per touchpoint.

## Unresolved Issues

- Benefit side of the economics is absent by design (OD-04); Stage 4 (KPI baseline) and Stage 8 must supply it.

## Residual Risks

- Cost caps could be met while quality is unacceptable; caps are necessary, not sufficient.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
