---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "scenario-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/36-roi/verified-benefits.md", "docs/36-roi/cost-model.md", "docs/35-variance/benefit-variance.md", "docs/00-preflight/ai-economics/cost-scenarios.md", "docs/35-variance/confounder-analysis.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on behalf of Dinesh Naik (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
The prompt asks for optimistic, expected and downside scenarios. **They can be defined only on the cost side, where the 0C lo/mid/hi Assumption ranges exist. The benefit side has no range, so every scenario's net outcome is NOT COMPUTABLE.** The scenarios are therefore defined as input sets with empty benefit slots, to be filled from evidence later.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SA-1 Scenario definitions (structure)
| Scenario | Cost inputs (0C Assumption) | Benefit inputs | Adoption path | Net result |
|---|---|---|---|---|
| Optimistic | lo column (S1 lo USD 7,920 gross 3y) | slots I-01..I-09 EMPTY | EMPTY | NOT COMPUTABLE |
| Expected | mid column (S1 mid 13,440 or S2 mid 22,080) | EMPTY | EMPTY | NOT COMPUTABLE |
| Downside | hi column (S2 hi 39,000) plus the four unpriced terms at higher-than-hi (not quantifiable) | EMPTY; adoption stays 0 until preconditions clear | EMPTY | NOT COMPUTABLE |

Which of S1 or S2 applies is an open choice (Stage 8 kept both; ER-2 says actual effort may be at or above S2). The cost columns are Assumptions, synthetic and unvalidated (A-36-05).

### SA-2 A fourth case the evidence does support: 'no adoption'
[Verified Fact] Today A = 0 of 125 (K-21). In that case every benefit term is zero and cost is positive. This is a description of the current state, not a forecast. It is the only scenario with an evidence basis and is labelled **status quo of the repository, not a downside forecast**.

### SA-3 Scenario guardrails
- Benefit side of a scenario may be filled only under the RM-3 fill rule; an 'optimistic benefit' picked without evidence is an invented benefit and is excluded.
- Scenarios must not be shown on a single chart that visually ranks them before the benefit slots hold evidence.
- Confounders (Stage 35 CNF-01..13) are not scenario inputs; they are reasons a measured difference might not be attributable.

### SA-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| SCF-1 | [Verified Fact] Cost ranges exist (0C); benefit ranges do not | `cost-model.md` CM-2; `value-hypothesis.md` | Scenarios are half-defined | High | High | Benefit evidence |
| SCF-2 | [Verified Fact] The only evidenced adoption state is 0 | `adoption-metrics.md` AD-1 | Anchors the base case at zero benefit | High | High | CA-01 |
| SCF-3 | [Inference] The 0C S1/S2 split is a labour-effort question; whether the build to date fits either is Unknown (TCO-F4), so the Expected cost column is itself uncertain | `tco-model.md` | Expected case is not a central estimate | Medium | Medium | OB-04 |


## Evidence References
`docs/36-roi/cost-model.md`; `docs/00-preflight/ai-economics/cost-scenarios.md`; `docs/35-variance/confounder-analysis.md`; `adoption-metrics.md` AD-1.

## Assumptions
- A-36-10 [Assumption] Scenario names follow the stage prompt; mapping lo/mid/hi to optimistic/expected/downside is the agent's choice for the cost side only. Confirm: Engagement lead (Dinesh Naik).
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-09 Any benefit range; adoption path.

## Unresolved Issues
- None specific beyond RM-2 slots.

## Residual Risks
- RR-36-13 Optimistic and downside read as probability-weighted (no probabilities exist) (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
