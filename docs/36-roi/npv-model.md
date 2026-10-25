---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "npv-model.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/36-roi/verified-benefits.md", "docs/36-roi/cost-model.md", "docs/35-variance/benefit-variance.md", "docs/00-preflight/ai-economics/preliminary-tco.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on behalf of Dinesh Naik (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
**NPV = NOT COMPUTABLE.** It needs the benefit and cost streams (see `roi-model.md`) and a finance-approved discount rate; **no discount rate exists anywhere in the repository** and none is chosen here. This file gives the formula, the timing convention to be confirmed, and the slots.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### NM-1 Skeleton
`NPV = sum_{t=0..T} (B_t - C_t) / (1 + r)^t`
- `t = 0` is the build year (cost-only unless a pilot yields benefit); the timing convention (year-end vs mid-year) is an open choice (I-16).
- `B_t` and `C_t` as in `roi-model.md` RM-1 and `cost-model.md` CM-1.
- `r` is the discount rate (slot I-15).
- Discounted benefit-cost ratio: `DBCR = sum B_t/(1+r)^t / sum C_t/(1+r)^t`.
- Internal rate of return: the r at which NPV = 0; defined only if the stream changes sign, which cannot be tested without values.

### NM-2 Extra slots
| Slot | Input | Evidence required | Owner | Status |
|---|---|---|---|---|
| I-15 | Discount rate `r` | **finance-approved** hurdle/discount rate | Finance partner (unfilled); Dinesh to name one | EMPTY. No rate in repo; none invented |
| I-16 | Timing convention | decision | Dinesh | EMPTY |
| I-17 | Inflation / rate escalation on `R_rev` and costs | finance guidance | Finance partner | EMPTY (0C assumes 0 % growth, A-TC01) |
| I-18 | Terminal/exit treatment (`Exit` cost, residual value) | `exit-plan.md` priced | Dinesh | EMPTY |
| I-19 | Tax and currency | finance guidance | Finance partner | EMPTY |

### NM-3 Cost-only present value: deliberately not computed
A present value of the 0C cost range would need r; applying a guessed r to Assumption costs yields a number with two unsourced inputs. It is not shown. The undiscounted cost range (USD 7,920 to 39,000, `cost-model.md` CM-2) is the only cost figure that can be stated, and it is an Assumption.

### NM-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| NPF-1 | [Verified Fact] No discount rate, hurdle rate or finance guidance exists in the repository | case-insensitive search of all `docs/**/*.md` (excluding `docs/36-roi/`) for 'discount rate', 'hurdle', 'WACC', 'cost of capital' and 'NPV' returned no file on 2026-10-25; Stage 32 TCO uses 0 % growth and no discounting | NPV cannot be computed | High | High | I-15 |
| NPF-2 | [Verified Fact] NPV needs `B_t`, which is empty | `verified-benefits.md` | same | High | High | RM-2 |
| NPF-3 | [Inference] With a 3-year horizon and a small cost scale (USD 10^4), discounting is unlikely to change a go/no-go on its own; the dominant uncertainty is the benefit stream. Reasoning: discount factors near 1 at low r. Not tested | cost scale from CM-2 | Prioritise benefit evidence over rate debate | Low | Low | none |


## Evidence References
`docs/36-roi/roi-model.md` RM-1; `docs/36-roi/cost-model.md` CM-2; `docs/32-finops/tco-model.md` A-32-19.

## Assumptions
- A-36-08 [Assumption] Horizon of 3 years is carried over from 0C unchanged (A-TC01). Confirm: Dinesh and a Finance partner.
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-07 Discount rate, timing convention, escalation, tax, currency.

## Unresolved Issues
- No Finance partner exists (SH-05).

## Residual Risks
- RR-36-10 A rate is picked to make NPV look positive (High). RR-36-11 NPF-3 read as evidence (Low, flagged Low confidence).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
