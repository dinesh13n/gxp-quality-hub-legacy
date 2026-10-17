---
stage: "0C — Provisional Token Efficiency & AI Economics Envelope"
artifact: "economics-readiness.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["all 0C artifacts in docs/00-preflight/ai-economics/", "docs/00-preflight/discovery/assumptions-unknowns.md", "docs/00-preflight/operating-contract/open-governance-decisions.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

**Stage 0C gate: CONDITIONAL PASS.** All 13 artifacts exist; non-AI scenarios (S0-S2) are modelled alongside AI scenarios (S3-S4); measured data and assumptions are separated; provisional cost, latency, context and loop limits are stated; and it is explicitly recorded that **Stage 8 determines whether AI portions remain applicable** and may retire S3/S4 assumptions. The condition: every price, effort, rate and usage input is an Assumption (no telemetry, stakeholders or verified vendor pricing exist), so the envelope is a planning constraint, not a business case.

## Findings

| Gate condition | Met? | Evidence |
|---|---|---|
| At least one non-AI scenario modelled alongside AI | Yes | S0, S1, S2 in `solution-scenarios.md`, `cost-scenarios.md`, `preliminary-tco.md` |
| Measured data and assumptions clearly separated | Yes | Class column in `workload-assumptions.md`, `cost-scenarios.md`; measured = repo counts/sizes only |
| Provisional cost, latency, context, loop limits stated | Yes | `provisional-token-budget.md`, `provisional-context-budget.md`, `provisional-loop-budget.md`, `quality-latency-cost-envelope.md` |
| Stage 8 determines AI applicability recorded | Yes | `solution-scenarios.md` Summary; this file; Lifecycle |
| All required artifacts exist | Yes | 13/13 |
| Critical gaps resolved or documented | Documented | C-1..C-5 below |
| Evidence supports the conclusion | Partly | Conclusion limited to "envelope is provisional" - appropriate |

**Key findings**
1. [Verified Fact] Current AI workload and spend = 0; no AI dependency in repo.
2. [Inference] At every modelled tier, token spend is < 1% of total run cost; worst-case High-volume S4 token cost ~USD 137/month at list price (assumed). Economics are driven by oversight labour, ops effort and managed services.
3. [Inference] Agent loops are the only token-risk: cost grows quadratically with steps (n=8 is ~1.6x n=6); hard caps mandated.
4. [Inference] Gross 3-year TCO at Base (mid): S1 USD 13.4k, S2 22.1k, S3 49.8k, S4 72.7k - benefits not modelled so no ranking of value is claimed.
5. [Verified Fact] The deterministic gaps (WF-05 missing disposition gate, WF-06 three divergent rules, IO-01..03 ingestion drops) are independent of any AI decision and cost nothing in tokens to fix.
6. [Verified Fact] >=286 embedded instruction-like strings make injection controls (CB-05, LB-08) a cost-of-adoption item under S3/S4.

**Non-blocking conditions (owner: Engagement lead (Dinesh Naik))**

| ID | Condition | Resolving stage | Risk if unmet |
|---|---|---|---|
| C-1 | Replace Assumed model prices with a cited, dated vendor/platform price page | 8 (before 10) | Mis-sized budgets |
| C-2 | Obtain real volumes, users, seasonality (U-C01/U-24) | 4/5 | Order-of-magnitude error |
| C-3 | Dataset baseline decision (U-13/OD-02) | 1 -> 4 | Wrong volume tier |
| C-4 | Obtain real document sizes/formats (U-V02) | 5/10 | Context/token budgets 10-100x off |
| C-5 | Quantify benefits and labour cost (U-24, U-P02) | 4/8 | TCO not decision-grade |

**Open economics questions**: Which platform/region and contract terms? Is a sync Q&A touchpoint wanted at all? What is acceptable human-review time per output? What validation (GxP CSV/CSA) cost applies to AI features? Who owns the AI budget?

## Evidence References

All sibling 0C artifacts; Stage 0A `assumptions-unknowns.md` and `discovery-summary.md`; Stage 0B contract.

## Assumptions

Price/effort/rate/volume assumptions listed in `cost-scenarios.md`, `preliminary-tco.md`, `workload-assumptions.md`; none verified by a stakeholder.

## Unknowns

See C-1..C-5 and the open economics questions; plus U-V02, U-Q01, U-TC1.

## Unresolved Issues

Open items C-1..C-5 (owner: Engagement lead (Dinesh Naik)); no due dates can be committed without stakeholders - each is due before its resolving stage starts.

## Residual Risks

Envelope may be mistaken for a business case; mitigated by repeated "gross, benefits unmodelled" statements. Anchoring on synthetic volumes (R-03, R-15). Prompt injection (R-09).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional economics draft. |
