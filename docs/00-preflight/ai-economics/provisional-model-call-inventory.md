---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "provisional-model-call-inventory.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/workflow-overview.md WF-01..WF-11", "docs/00-preflight/discovery/integration-overview.md", "docs/00-preflight/operating-contract/data-use-constraints.md DU-03,X-3", "app/legacy_logic.py", "legacy_batch/shift_reconciliation.py", "workload-assumptions.md"]
supersedes: "none"
---
## Summary

Expected model calls per workflow per scenario (HYPOTHETICAL). S0-S2 = 0 model calls. Counts use Base-tier volumes from `volume-assumptions.md`; calls/month = unit volume x calls per unit.

## Findings

| Call ID | Touchpoint | Scenarios | Model tier (Assumed) | Calls per unit | Base units/month | Base calls/month | Notes |
|---|---|---|---|---|---|---|---|
| MC-01 | T1 triage summary | S3,S4 | M | 1 | 167 cases | 167 | Retry overhead modelled separately (5% base) |
| MC-02 | T2 feed exception classification | S3,S4 | S | 1 | 238 x 25% = 60 rows | 60 | Rules pre-filter in all scenarios |
| MC-03 | T3 document Q&A | S3,S4 | M (+embedding) | 1 generation + 1 embed | 440 queries | 440 gen + 440 embed | Embedding Assumed $0.10/1M tokens, negligible |
| MC-04 | T4 CAPA/deviation draft | S3,S4 | M | 1 | 5 drafts | 5 | Human-edited |
| MC-05 | T5 investigation loop | S4 | M | avg 6 steps (cap 8) | 17 cases (10%) | ~100 | Quadratic context growth, see token-flow |
| MC-06 | One-off corpus embedding | S3,S4 | embedding | batch | 1,620 docs | 1,620 | One-off; ~0.1 M tokens |
| **Total Base** | | S3 | | | | **~672 gen + embeds** | |
| **Total Base** | | S4 | | | | **~772 gen + embeds** | |
| S0/S1/S2 | all | - | none | 0 | - | **0** | Verified: no model calls in repo today |

Latency exposure: only MC-03 is interactive; MC-01/02/04 can be asynchronous batch (overnight window before 06:00, documented historical target `docs/operations-service-levels.md`) [Inference].

## Evidence References

`workload-assumptions.md`; `volume-assumptions.md`; `docs/operations-service-levels.md`.

## Assumptions

- A-M01 Model tiers S/M are generic capability classes, not named products (no platform decision exists).
- A-M02 One model call per unit for single-pass touchpoints.

## Unknowns

- U-M01 Whether T3 would be interactive (needs p95 target from real users).

## Unresolved Issues

- Call counts can only be validated against real usage in Stage 32.

## Residual Risks

- Hidden extra calls (guardrail/classifier checks, re-ranking, LLM-as-judge evals) are *not* counted; could add 30-100% calls [Inference] - covered by the high token multiplier.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
