---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "payback-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/36-roi/verified-benefits.md", "docs/36-roi/cost-model.md", "docs/35-variance/benefit-variance.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on behalf of Dinesh Naik (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
**Payback = NOT COMPUTABLE.** There is no benefit stream to accumulate against cost. This file gives the formulas, the cost-side hurdle that is re-derivable, and the conditions that must hold before a payback can be stated.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### PB-1 Skeleton
- Simple payback: smallest t such that `sum_{s<=t} (B_s - C_s) >= 0`; interpolate within the year if needed.
- Discounted payback: the same with `(B_s - C_s)/(1+r)^s` (needs I-15).
- Steady-state break-even benefit: `B_break-even = (sum C_t) / T` undiscounted.
- Adoption-gated payback: no benefit accrues until A_t > 0 (K-21 = 0 of 125 today), and not until the Stage 35 leakage blockers VL-01, VL-02, VL-06, VL-10, VL-11 are cleared. Time to first benefit therefore cannot be earlier than the time to clear them; that time is Unknown (no plan, owner or date exists).

### PB-2 Cost-side hurdle (re-derivable; Assumption inputs)
From `cost-model.md` CM-3: average benefit per year needed merely to repay the 0C gross 3-year cost, undiscounted:
| Scenario | lo | mid | hi |
|---|---|---|---|
| S1 (gross 7,920 / 13,440 / 22,800) | 2,640 | 4,480 | 7,600 |
| S2 (gross 13,440 / 22,080 / 39,000) | 4,480 | 7,360 | 13,000 |
USD per year, = gross / 3. Check: 7,920/3 = 2,640; 13,440/3 = 4,480; 22,800/3 = 7,600; 22,080/3 = 7,360; 39,000/3 = 13,000. Because four or more cost terms are unpriced and the benefit is front-loaded by neither evidence nor plan, **no payback period in months or years can be stated.** A payback figure needs benefit per period, which is empty.

### PB-3 Conditions before payback can be stated (from the Stage 35 leakage items)
| # | Condition | Leakage item | Backlog | Status |
|---|---|---|---|---|
| PC-1 | Real after-window defined; hub used by people on real cases | VL-01 | CA-01, CA-02 | Open |
| PC-2 | Zone H holders named or Zone H declared unused; a rule set activated by a recorded human decision | VL-02 | CA-09 | Open |
| PC-3 | Owners named for assets and vacant roles; second reviewer or recorded single-approver acceptance (acceptance is Dinesh only) | VL-06, VL-07 | CA-08 | Open |
| PC-4 | Closed/resolved decided; definitions adopted | VL-10 | CA-07 | Open |
| PC-5 | Time capture exists | VL-11 | CA-06 | Open |
| PC-6 | Stage 4 v0.2 addendum and `as_of` parameter | VL-12, VL-13 | CA-05, CA-03 | Open |
| PC-7 | Parallel-run plan so work is not done twice | VL-14 | CA-12 | Open |
| PC-8 | Stage 28 mechanisms wired; CI installed (decisions) | VL-04, VL-05 | CA-10 | Open |
| PC-9 | Cost inputs and cost owner | VL-17, CLK-9 | CA-13 | Open |
| PC-10 | Open risk registers routed (accept / fix / defer) | VL-09 | CA-14 | Open |

### PB-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| PBF-1 | [Verified Fact] No payback can be computed | `roi-model.md` ROF-1 | none quotable | High | High | PB-3 |
| PBF-2 | [Verified Fact] All 10 preconditions are open and none is started | `corrective-action-backlog.md` RR-35-15 (all PROPOSED) | Time to first benefit Unknown | High | High | Dates and owners |
| PBF-3 | [Inference] Cost is incurred before any benefit can start because adoption is 0 and the preconditions are open, so cumulative net position is non-positive until at least PC-1 to PC-5 clear. Reasoning: A_t = 0 makes every V_d = 0 | `adoption-metrics.md` AD-1 | Cash-flow shape | Medium | Medium | none |


## Evidence References
`docs/36-roi/cost-model.md` CM-2, CM-3; `docs/35-variance/value-leakage-analysis.md` VL-01..VL-17; `corrective-action-backlog.md` CA-01..CA-17.

## Assumptions
- A-36-09 [Assumption] No calendar dates exist; preconditions are due 'before any pilot or production use' (Stage 34/35 convention). Confirm: Engagement lead (Dinesh Naik).
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-08 Time to clear PC-1..PC-10; benefit per period.

## Unresolved Issues
- No owner or date for any precondition.

## Residual Risks
- RR-36-12 The hurdle table is read as an expected benefit or a target (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
