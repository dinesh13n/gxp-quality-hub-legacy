---
stage: "8 — AI-vs-No-AI Qualification"
artifact: "economics-baseline-reconciliation.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/economics-readiness.md", "docs/00-preflight/ai-economics/cost-scenarios.md", "docs/00-preflight/ai-economics/preliminary-tco.md", "docs/00-preflight/ai-economics/preliminary-finops-baseline.md", "docs/00-preflight/ai-economics/provisional-model-call-inventory.md", "docs/00-preflight/ai-economics/solution-scenarios.md", "docs/00-preflight/ai-economics/volume-assumptions.md", "docs/08-ai-qualification/ai-vs-no-ai-matrix.md"]
supersedes: "none"
---
## Summary

Reconciles each Stage 0C economics item with the Stage 8 recommendation (P-NOAI, no AI). **If Dinesh approves the recommendation: scenarios S3 and S4 and their token, context, loop and call budgets are RETIRED as active assumptions (kept dormant for re-qualification); S1 plus the non-ML part of S2 become the cost basis for Stage 32.** All figures remain **unverified assumptions**; no model price was verified in this stage, deliberately: the decision does not depend on price (shown in section ER-3). Reconciliation is conditional on approval; until then S3/S4 remain "recommended for retirement" and no 0C artifact is edited (HAR-13).

## Findings

### ER-1 Item-by-item reconciliation

| 0C item | 0C value (all Assumption unless noted) | Stage 8 treatment | Status |
|---|---|---|---|
| S0 as-is | baseline | **Retain** as before/after reference | Active |
| S1 deterministic | 3-yr gross 7,920 / 13,440 / 22,800 USD (build 15/25/40 person-days; infra 20/40/100 USD/mo) | **Retain** as the primary basis | Active, unverified |
| S2 conventional automation | 13,440 / 22,080 / 39,000 USD; includes classical ML for feed exceptions | **Retain without the classical-ML component** (O6 rejected); the non-ML part (ETL, normalisation, scheduling) is O3/O5 | Active, unverified; component list to be re-cut at Stage 10 |
| S3 GenAI RAG | 29,569 / 49,780 / 88,527 USD | **Retire** (O7 not selected) | Dormant |
| S4 Agentic | 42,819 / 72,686 / 134,301 USD | **Retire** (O8 rejected) | Dormant |
| A-P01 token price bands | Tier S/M/L USD per 1M tokens; source: agent's general knowledge, not verified | Retire as decision input. Not verified because no model is selected; verify only if an RQ trigger fires, from a dated vendor page | Retired (dormant) |
| A-P02 infra for S3/S4 (120-1000 USD/mo) | Retire | Dormant |
| A-P03 reviewer rate USD 25/h | **Retain** (used for the human-handling baseline USD 15.02/case and any future oversight of rule-flag review); still unverified (U-P02, U-24) | Active, unverified |
| A-P04 reviewer minutes per AI output (T1 2, T2 1, T3 0.5, T4 10, T5 5) | **Retire** as AI-output review times; replace at Stage 32 with measured review time for rule-flagged items | Retired |
| `provisional-token-budget.md`, `provisional-context-budget.md`, `provisional-loop-budget.md`, `provisional-model-call-inventory.md` (MC-01..MC-06) | **Retire** from active budgets; keep on file as the starting point if re-qualified. Stage 32 should not track token metrics | Dormant |
| `token-flow-scenarios.md` | Same | Dormant |
| Anti-pattern "send all 100,020 lake events through an LLM" (USD 23/270/1350) | Keep as a documented anti-pattern; deterministic normalisation is the approach | Retained as guardrail |
| Volume tiers Low 4 / Base 167 / High 1,670 cases/mo | **Retain** as unverified tiers; still relevant to infra and review capacity | Active, unverified |
| Volume driver "Document Q&A 440 queries/mo", "drafts 5/mo", "agentic share 10%" | Retire as AI drivers; T3 queries remain a possible usage metric for search | Retired / reused |
| 0C open condition C-1 (replace price with cited dated page before Stage 10) | **Downgraded** from required to conditional: required only if RQ triggers fire | Closed by retirement, pending approval |
| C-2 real volumes, C-3 dataset (OD-02), C-4 real doc sizes (U-V02), C-5 benefits and labour | **Carried forward unchanged**; C-4 now doubles as input to RQ-1 | Open (owner Engagement lead (Dinesh Naik)) |

### ER-2 Recommended cost basis for Stage 32

| Item | Basis | Class |
|---|---|---|
| Scenario to track | P-NOAI ≈ S1 plus non-ML parts of S2; planning range USD 7.9k to 39.0k gross 3-yr (lo of S1 to hi of S2), mid-point reading 13.4k to 22.1k | Assumption (0C), unverified |
| Build effort | 0C S1 15/25/40 and S2 25/40/70 person-days. [Inference] S1 description lists rule consolidation, search, templates and the disposition gate but not shared-identity/crosswalk, non-destructive intake, run records or shared metric definitions (RC-6, RC-7, RC-5, RC-8), so the true range may lie at or above S2. **Re-estimate at Stage 9/13** | Unknown |
| Token / model line | USD 0 and calls 0; Stage 32 should assert zero as a check (any non-zero value signals an unapproved AI element, HAR-10) | Verified Fact today (FB-01, FB-02) |
| Human oversight line | Measure actual review time on rule-flagged items; no AI-output oversight | Unknown |
| Benefits | Not modelled; no monetary benefit asserted (U-24, FAIL-05) | Unknown |

### ER-3 Decision sensitivity to price (why price verification is not needed now)

[Inference] 0C shows token spend under USD 137/month in its worst modelled case (High volume, S4, list price, Assumption) and under 1% of total run cost at every tier. Setting token price to zero leaves S3/S4 behind S1/S2 on the gates in `ai-vs-no-ai-matrix.md` (G2/G3) and on root-cause coverage (0 of 8). Conversely a price ten times higher would change annual spend by hundreds of dollars, not the ranking. The AI options are rejected on fit and risk, not cost. Therefore the unverified token prices remain labelled "unverified assumption, dormant", and a web check was not made. If an RQ trigger fires, the check becomes mandatory first step.

### ER-4 TCO side-by-side (0C figures, USD, 3-year gross, mid, Assumption)

| Scenario | Total 3y mid | Token | Human oversight | Decision |
|---|---|---|---|---|
| S1 | 13,440 | 0 | 0 | Active |
| S2 | 22,080 | 0 | 0 | Active (minus ML) |
| S3 | 49,780 | 227 | 9,952 | Retired |
| S4 | 72,686 | 281 | 11,205 | Retired |

Note: S1/S2 show 0 oversight only because 0C did not model reviewer time for deterministic outputs; this is an omission in the comparison that favours S1/S2 and should be remedied at Stage 32 (Unknown).

## Evidence References

`preliminary-tco.md` table; `cost-scenarios.md`; `economics-readiness.md` C-1..C-5; `preliminary-finops-baseline.md` FB-01..FB-12; `provisional-model-call-inventory.md` MC-01..MC-06.

## Assumptions

- A-08-12 All 0C numbers remain Assumptions (price, rate, effort, infra, volume); none verified by a stakeholder or vendor source. Owner: Engagement lead (Dinesh Naik).
- A-08-13 Retirement of S3/S4 takes effect only on Dinesh's approval of `qualification-decision.md`.

## Unknowns

- U-08-10 Real platform/region/contract terms (U-P01); only relevant if AI is re-qualified.
- U-08-11 Reviewer-time cost of rule-flagged items (omitted from S1/S2).

## Unresolved Issues

- 0C artifacts are not modified (HAR-13); the reconciliation lives here and Stage 32 must read both. A 0C addendum can be added when Dinesh approves.

## Residual Risks

- S1/S2 may be understated versus S3/S4 comparisons because oversight and effort for P-NOAI scope extensions are not modelled; this does not alter the decision but does matter for budgeting.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial reconciliation. |
