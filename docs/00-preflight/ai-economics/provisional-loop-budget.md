---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "provisional-loop-budget.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["token-flow-scenarios.md", "docs/00-preflight/operating-contract/data-use-constraints.md DU-03,X-4", "docs/00-preflight/discovery/data-flow-overview.md DF-08,DF-09", "docs/00-preflight/discovery/integration-overview.md IO-01..IO-03"]
supersedes: "none"
---
## Summary

PROVISIONAL limits for agent loops, steps and retries (S4 only; S3 has no loops). Derived from the quadratic token model in `token-flow-scenarios.md`.

## Findings

| ID | Limit | Value | Basis |
|---|---|---|---|
| LB-01 | Max steps per investigation | 8 (expected 6) | n=8 costs ~1.6x n=6 in input tokens (38,400 vs 24,000) |
| LB-02 | Max tool calls per step | 3, read-only tools only | 0B tool/agent permissions: no writes, no disposition |
| LB-03 | Max retries per model call | 2 with exponential backoff; none on schema-failure beyond 1 repair attempt | Assumed |
| LB-04 | Max wall-clock per investigation | 120 s (async) | Assumed; no user tolerance evidence |
| LB-05 | Per-investigation token ceiling | 40,000 in / 2,000 out (TB-05) | - |
| LB-06 | Circuit breaker | 5 consecutive failures or >3x expected monthly spend in 24 h halts the touchpoint and routes to human | Assumed |
| LB-07 | Repeated-action detector | identical tool call twice in one investigation aborts the loop | Assumed |
| LB-08 | No agent may take a decision action (`batch_disposition`, status change, approval) | absolute | 0B stop-conditions/HAR; WF-05 |
| LB-09 | Termination outcome on any limit | hand off to a human with partial trace | - |

Retry overhead worked example: with 15% high retry rate and 8-step cap, worst-case investigation = 38,400 x 1.15 = ~44,200 input tokens, which would breach TB-05 and trigger LB-09 [Inference] - the caps are deliberately binding.

Ingestion retry note (non-AI): the existing bridge has no retry/backoff and drops unknown-key events (IO-01..IO-03, R-08); AI retries must not be conflated with this - a deterministic fix is independent of any AI decision.

## Evidence References

`token-flow-scenarios.md`; `docs/00-preflight/operating-contract/` (tool/agent permissions, stop-conditions); IO-01..IO-03.

## Assumptions

- A-L01 Loop parameters (steps 6/8, 120 s). Confirm via prototype, stage 19/22.

## Unknowns

- U-L01 Observed failure rates - none (no telemetry).

## Unresolved Issues

- Whether any agent is permitted at all is a Stage 8 / Stage 2 governance decision.

## Residual Risks

- Runaway loops: mitigated only if caps are implemented as platform-level limits, not prompt instructions.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
