---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "preliminary-finops-baseline.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["cost-scenarios.md", "token-flow-scenarios.md", "docs/operations-service-levels.md", "docs/00-preflight/discovery/workflow-overview.md WF-05,WF-11", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md"]
supersedes: "none"
---
## Summary

Baseline for Stage 32 comparison. Records, per metric, the baseline value, class (Measured/Assumed/Unknown), source and the measure to be captured in production. Unit-cost tags and dimension names are proposed so actuals can be joined to these baselines.

## Findings

| ID | Metric | Baseline value | Class | Source | Stage 32 actual to capture |
|---|---|---|---|---|---|
| FB-01 | Model calls / month today | 0 | Measured (grep, 0A) | repo scan | calls by touchpoint |
| FB-02 | Token spend today | USD 0 | Measured | same | tokens in/out/cached by touchpoint |
| FB-03 | Cases (shipped DB) | 125 | Measured | `data/legacy.sqlite3` | cases/month |
| FB-04 | Cases (documented dataset) | 6,000 | Measured (documented/regenerable) | OD-02 | - |
| FB-05 | hours_per_case | 0.601-0.603 | Measured from synthetic formula | `app/baseline` | real handling time (U-24) |
| FB-06 | Human cost per case | USD 15.02 | Assumed (rate USD 25/h) | cost-scenarios | finance actuals |
| FB-07 | Expected token cost per case S3 / S4 (mid) | USD 0.0077 / 0.0167 | Assumed | cost-scenarios | actual USD/case |
| FB-08 | Expected total monthly run S3 / S4 at Base (mid) | USD 533 / 719 | Assumed | cost-scenarios | actual invoice |
| FB-09 | Expected monthly calls Base S3 / S4 | ~672 / ~772 | Assumed | call inventory | actual calls |
| FB-10 | Expected retry rate | 5% (2-15%) | Assumed | token-flow | actual retries/failures |
| FB-11 | Avg agent steps / investigation | 6 (cap 8) | Assumed | loop budget | actual step histogram |
| FB-12 | Infra cost today | Unknown (no deployment evidence, U-05) | Unknown | - | - |

**Proposed cost-allocation tags**: `engagement=gxp-quality-hub`, `scenario=S0..S4`, `touchpoint=T1..T5`, `stage=0C-baseline`, `env=E1|prod`; budget owner = Engagement lead (Dinesh Naik) until Stage 2 names others.
**Preservation rule**: this file is not edited after approval; changes are new versions (`supersedes`).

## Evidence References

`cost-scenarios.md`; `workload-assumptions.md`.

## Assumptions

- A-F01 Baseline numbers remain Assumed until replaced; no number here may be reported as an achieved result.

## Unknowns

- U-F01 Real infrastructure spend and real labour cost.

## Unresolved Issues

- Baseline dataset decision (U-13) changes FB-03/FB-04.

## Residual Risks

- Stage 32 comparison is only as valid as these assumptions; unlogged assumption drift is the main risk.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
