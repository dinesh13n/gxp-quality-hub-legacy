---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "sensitivity-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/36-roi/verified-benefits.md", "docs/36-roi/cost-model.md", "docs/35-variance/benefit-variance.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on behalf of Dinesh Naik (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
Sensitivity is stated as **structure and ranking by construction**, not as numbers: with no benefit values, a tornado of net-benefit swings cannot be computed. The only re-derivable sensitivity is on the cost side from the 0C ranges.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SE-1 Which inputs move the result (by construction of the formulas)
| Rank (Inference) | Input | Why it dominates | Evidence status |
|---|---|---|---|
| 1 | `A_t` adoption | multiplies every benefit term; currently 0 | EMPTY |
| 2 | `R_rev` rate and `m_recon` / `dH_close` / effort terms | linear in each benefit term | EMPTY |
| 3 | `dN` changes (rework, incidents) | each is a *difference* of two noisy counts; small samples make it unstable (K-15 is 8 of 125) | EMPTY |
| 4 | Build effort | largest cost term; 0C range S1 15 to S2 70 pd, a factor of 4.7 between S1 lo and S2 hi | Assumption |
| 5 | `Over_t` oversight | cost currently set to 0, an omission (ER-4) | EMPTY |
| 6 | Hosting, toolchain | small or unknown | Assumption / EMPTY |
| 7 | `r` | little effect on a 3-year horizon at this cost scale (Inference, not tested) | EMPTY |

The ranking is an Inference from the formulas in `roi-model.md`, not an output of a computation.

### SE-2 Re-derivable cost-side sensitivity (Assumption inputs)
- Build as share of gross cost: S1 mid 7,500 / 13,440 = 55.8 %; S2 hi 21,000 / 39,000 = 53.8 %. (7,500/13,440 = 0.5580; 21,000/39,000 = 0.5385.)
- Spread of the 0C gross range: S2 hi / S1 lo = 39,000 / 7,920 = 4.92. (Re-derived; includes the S1-to-S2 scenario choice, so it is not a pure uncertainty band.)
- Hosting share of gross: S1 lo 720 / 7,920 = 9.1 %; S1 mid 1,440 / 13,440 = 10.7 %; S1 hi 3,600 / 22,800 = 15.8 %; S2 hi 7,200 / 39,000 = 18.5 %. A minor driver relative to build.
No sensitivity on token price: it has no effect (zero).

### SE-3 Method to use once inputs exist (not executed)
1. One-at-a-time swing for each filled slot between its evidence-based low and high.
2. Two-way grid on adoption x time saved per case.
3. Break-even value of each input holding others at their evidence-based value.
4. Flag any input whose range comes from an Assumption; a result that flips sign only on an Assumption input is reported as 'unresolved', not as a conclusion.
No range is entered in this stage: 'illustrative placeholder, not evidence' ranges were considered and rejected because the 0C history (VD-numbers, K-12/K-13) shows placeholders get quoted (RR-35-05).

### SE-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| SEF-1 | [Verified Fact] No benefit-side sensitivity can be computed | `roi-model.md` RM-2 | none quotable | High | High | RM-2 |
| SEF-2 | [Inference] Adoption and the labour rate dominate by construction | SE-1 | Where evidence effort should go first | Low | Medium | none |
| SEF-3 | [Verified Fact] Build effort is >50 % of gross 0C cost in the two re-derived rows | SE-2 | Recording actual effort (OB-04) is the cheapest way to firm up the cost side | Low | High | OB-04 |


## Evidence References
`docs/36-roi/roi-model.md`; `docs/36-roi/cost-model.md` CM-2; `docs/00-preflight/ai-economics/preliminary-tco.md`.

## Assumptions
- A-36-11 [Assumption] Illustrative benefit ranges are omitted on purpose (SE-3). Confirm: Engagement lead (Dinesh Naik).
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-10 All benefit-side sensitivities.

## Unresolved Issues
- None beyond RM-2.

## Residual Risks
- RR-36-14 Ranking in SE-1 read as measured (Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
