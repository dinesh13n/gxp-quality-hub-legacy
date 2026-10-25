---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "roi-model.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/36-roi/verified-benefits.md", "docs/36-roi/cost-model.md", "docs/35-variance/benefit-variance.md", "docs/32-finops/tco-model.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on behalf of Dinesh Naik (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
**ROI = NOT COMPUTABLE.** The numerator needs a verified benefit stream (0 items, `verified-benefits.md`) and the denominator needs full cost (one term of ten measured, `cost-model.md`). This file gives the calculation skeleton, the full input-slot table with an owner for each input, and the rule for when the skeleton may be filled. Slots are empty on purpose.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RM-1 Skeleton
Benefit stream per driver d in year t (d in VD-01..VD-04; VD-05 is not monetised):
- `V_01,t = A_t x P_t x N_recon,t x (m_recon / 60) x R_rev`  (reconciliation minutes saved)
- `V_02,t = A_t x P_t x N_rework,t x e_rework x R_rev`  (rework avoided; N_rework is the *change* in reworked cases, not the rate)
- `V_03,t = A_t x P_t x dN_inc,t x e_inc x R_rev`  (incidents avoided)
- `V_04,t = A_t x P_t x dH_close,t x R_rev`  (month-end hours saved)

Net benefit after the double-counting deduction (`double-counting-check.md`):
`B_t = sum_d V_d,t - Overlap_t - Realisation_haircut_t`

ROI (undiscounted, over horizon T): `ROI = (sum_t B_t - sum_t C_t) / sum_t C_t`, with `C_t` from `cost-model.md` CM-1 (all ten terms).
Benefit-cost ratio: `BCR = sum_t B_t / sum_t C_t`. Discounted forms are in `npv-model.md`.

Where A_t = adoption share in year t (K-21 once measured; 0 of 125 today), P_t = persistence (benefit decay), dN and dH are **measured differences between like-for-like before and after values**, never modelled hours.

### RM-2 Input-slot table (every slot is empty)
Status key: EMPTY = no value in repository. Owner column names who must supply it; where no such role exists the slot says VACANT. All owners default to Engagement lead (Dinesh Naik) under OD-04 because no other human exists.

| Slot | Input | Unit | Evidence required before filling | Owner | Status |
|---|---|---|---|---|---|
| I-01 | `A_t` adoption share | share of cases/reviewers using hub | production K-21 and principal count (AD-2) | Dinesh (hub owner VACANT) | EMPTY (0 of 125 sandbox, not production) |
| I-02 | `P_t` persistence/decay | share | observed over >= 1 full after-window | Dinesh | EMPTY |
| I-03 | `N_recon,t` cases needing manual reconciliation | count/period | production count under a signed definition (CA-05, CA-07) | Dinesh | EMPTY |
| I-04 | `m_recon` minutes saved per case | minutes | time capture (CA-06), before and after, same population | Dinesh | EMPTY |
| I-05 | `dN_rework,t` change in reworked cases | count/period | K-15 on a real window with comparison (CA-04) | Dinesh | EMPTY |
| I-06 | `e_rework` effort per rework | hours | effort capture (K-22) | Dinesh | EMPTY |
| I-07 | `dN_inc,t` incident change | count/year | incident log over a real period | Dinesh | EMPTY (two historic incidents only) |
| I-08 | `e_inc` effort per incident | hours | incident records with effort | Dinesh | EMPTY |
| I-09 | `dH_close,t` month-end hours change | hours/month | close-time capture; K-10 redefined (OD-07) | Dinesh; Finance partner SH-05 unfilled | EMPTY |
| I-10 | `R_rev` loaded labour rate | currency/hour | **finance-approved** rate card (prompt rule) | Finance partner (unfilled) | EMPTY. USD 300/day in 0C is an unvalidated Assumption and is not accepted as finance-approved |
| I-11 | `Realisation_haircut_t` | share | policy decision; not evidence | Dinesh | EMPTY |
| I-12 | `Overlap_t` | currency | method in `double-counting-check.md` | Dinesh | EMPTY |
| I-13 | Horizon T | years | decision; 3 years inherited from 0C | Dinesh | Assumption (A-TC01) |
| I-14 | All cost terms | currency | `cost-model.md` CM-1 | Dinesh; cost owner RL-09 VACANT | EMPTY except Tok = 0 |

### RM-3 Fill rule
A slot may be filled only with (i) a measured production value under a signed definition, or (ii) a finance-approved rate. Anything else stays EMPTY or is shown only as an Assumption in a separate scenario that is labelled as such and is excluded from any go/no-go figure.

### RM-4 Result
- [Verified Fact] 0 of 14 slots hold evidence; 1 (horizon) holds an inherited Assumption.
- [Verified Fact] Stage 35 found no KPI with an improving variance, so even a partly filled skeleton would return a zero or negative ROI numerator for any value derived from today's data. This is stated as a data fact, not as a finding that ROI is negative: **the correct statement is 'not computable'.**

### RM-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| ROF-1 | [Verified Fact] ROI cannot be computed; both numerator and denominator lack evidence | `verified-benefits.md` VBF-1; `cost-model.md` CMF-1 | No ROI may be quoted | High | High | RM-2 slots |
| ROF-2 | [Inference] Any ROI figure produced from the 0C costs plus a guessed benefit would be a fabricated number. Reasoning: both are Assumptions with no source | Stage 3, 0C | Guard against invention | High | High | none |
| ROF-3 | [Verified Fact] Rate I-10 has no finance approval | `tco-model.md` A-32-18 | Blocks all time-based benefit values | High | High | Finance partner |


## Evidence References
`docs/36-roi/verified-benefits.md`; `docs/36-roi/cost-model.md`; `docs/03-problem-value/value-hypothesis.md` formulas VD-01..VD-04 (extended here with adoption, persistence and haircut terms).

## Assumptions
- A-36-07 [Assumption] The adoption/persistence/haircut factors in RM-1 are the agent's structural additions to the Stage 3 formulas; they hold no values. Confirm: Engagement lead (Dinesh Naik).
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-06 All RM-2 slots.

## Unresolved Issues
- No finance partner or cost owner exists to approve rates (SH-05, RL-09).

## Residual Risks
- RR-36-08 Skeleton filled with plausible-looking values (High). RR-36-09 Stage 42 or the final PRD quoting an ROI from this file (High; this file states none).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
