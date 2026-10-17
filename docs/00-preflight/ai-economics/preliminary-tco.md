---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "preliminary-tco.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["cost-scenarios.md", "token-flow-scenarios.md", "docs/operations-service-levels.md", "docs/00-preflight/discovery/workflow-overview.md WF-05,WF-11", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md"]
supersedes: "none"
---
## Summary

Preliminary 3-year TCO at Base volume, USD, all components Assumed. Build effort at USD 300/person-day (Assumed blended). **Gross cost only: benefits (time saved, error avoidance) are not modelled because no evidence exists (OD-04); this TCO therefore cannot show AI or non-AI to be worthwhile - Stage 8 must do so.** S0 has no incremental TCO.

## Findings

| Scenario | Build (one-off) | Ops/maintain 3y | Infra 3y | Tokens 3y | Human oversight 3y | **Total 3y (lo / mid / hi)** |
|---|---|---|---|---|---|---|
| S1 | 7,500 | 4,500 | 1,440 | 0 | 0 | **7,920 / 13,440 / 22,800** |
| S2 | 12,000 | 7,200 | 2,880 | 0 | 0 | **13,440 / 22,080 / 39,000** |
| S3 | 18,000 | 12,600 | 9,000 | 227 | 9,952 | **29,569 / 49,780 / 88,527** |
| S4 | 27,000 | 19,800 | 14,400 | 281 | 11,205 | **42,819 / 72,686 / 134,301** |

Components assumed (lo/mid/hi): build person-days S1 15/25/40, S2 25/40/70, S3 40/60/100, S4 60/90/150; ops person-days/yr S1 3/5/8, S2 5/8/12, S3 8/14/24, S4 12/22/40; infra USD/month S1 20/40/100, S2 40/80/200, S3 120/250/600, S4 200/400/1000; reviewer minutes per output as in `cost-scenarios.md`.

**Stress: High volume (10x)**

| Scenario | Total 3y mid, High volume (10x) |
|---|---|
| S1 | 13,440 (infra assumed unchanged at 10x - Assumption) |
| S2 | 22,080 (same) |
| S3 | 141,399 |
| S4 | 176,064 |

[Inference] (1) At Base, S1/S2 are roughly 2x-5x cheaper than S3/S4 (S1 mid 13.4k vs S3 mid 49.8k vs S4 mid 72.7k) in 3-year gross TCO, driven by oversight labour, evaluation/ops effort and managed AI services - not by tokens (token share of S3 mid TCO = 0.5%). (2) Because S1/S2 incur no oversight cost in this model, the comparison is biased in their favour: S1/S2 deliver *less coverage* (no unstructured-text capability, T3/T4 only templated); the coverage gap is unpriced. (3) Cost of *not* fixing deterministic defects (WF-05 disposition gate, WF-06 rule divergence) is excluded from all scenarios and is a prerequisite under any scenario.

**Hidden TCO items not priced (Unknown)**: red-team/eval harness build, GxP validation (CSV/CSA) of AI features, security review, model-version change control, training, incident handling.

## Evidence References

`cost-scenarios.md`; `volume-assumptions.md`; `workload-assumptions.md`.

## Assumptions

- A-TC01 3-year horizon, constant volume (growth 0% to keep comparisons simple; Base growth 10% would raise token/oversight lines ~10%/yr). A-TC02 Person-day rate USD 300 and effort figures. Confirm: Engagement lead (Dinesh Naik); Finance partner; stage 8.

## Unknowns

- U-TC1 Validation/compliance effort for AI in a GxP context. U-TC2 Benefit side.

## Unresolved Issues

- Needs Finance partner review; none available.

## Residual Risks

- Effort estimates carry +/-50% or worse uncertainty; ranking is more robust than absolute values.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
