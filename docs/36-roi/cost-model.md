---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "cost-model.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/32-finops/tco-model.md", "docs/32-finops/finops-model.md", "docs/00-preflight/ai-economics/preliminary-tco.md", "docs/35-variance/cost-leakage.md", "docs/37-operating-model/finops-ownership.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on Dinesh Naik on his behalf (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
Full-cost structure for the ROI model, built on the Stage 32 TCO. **Only one cost term is measured (model spend, USD 0 by design). The Stage 0C Assumption ranges are re-derived below, arithmetic only, and exclude four terms that have no price anywhere.** Nothing here is a budget or a forecast.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CM-1 Cost terms and their status
`C_t` for year t, with `C_0` = build year. Terms follow `tco-model.md` TC-1; the two terms the stage prompt names in addition (adoption cost, human oversight) are mapped to TC-1 terms.

| Term | Symbol | 0C figure (Assumption) | Measured? | Input owner / source needed |
|---|---|---|---|---|
| Build effort | `Build = PD_build x R_day` | S1 15 / 25 / 40 pd; S2 25 / 40 / 70 pd; R_day USD 300 | No; actual effort never recorded (BA-F3, TCO-F4) | Engagement lead (Dinesh Naik); Finance partner for R_day (SH-05 unfilled) |
| Operations | `Ops_t = PD_ops_yr x R_day` | S1 3 / 5 / 8; S2 5 / 8 / 12 pd per year | No | Support model, staffing (FC-09); Dinesh |
| Hosting | `Host_t = H_month x 12` | S1 20 / 40 / 100; S2 40 / 80 / 200 USD per month | No (nothing deployed; ADR-015) | Hosting decision, Dinesh |
| Toolchain | `Tool_t` | not in 0C | No | Plans and charges for code host, AI assistant, cloud workspace, CI (U-33-01/02); Dinesh |
| Human oversight | `Over_t = N_t x m_rev/60 x R_rev` | S1/S2 = 0 (ER-4 calls this an omission) | No | Reviewer minutes (U-24), volume, rate; Dinesh |
| Validation and compliance | `Val` | not priced in 0C | No | Compliance owner estimate (RL-06 VACANT) |
| Exit | `Exit` | not in 0C | No | Per `exit-plan.md` once priced |
| Model / token | `Tok_t` | 0 | **Yes, by design (No-AI, OD-08; tripwire)** | none |
| Parallel-run double work | `Dbl_t` | not in 0C | No; no parallel-run definition exists (VL-14) | CA-12 |
| Adoption / training / change | `Adopt_t` | not in 0C | No | Not scoped; Dinesh |

### CM-2 Re-derivation of the retained 0C gross 3-year ranges [Verified Fact: arithmetic only; inputs are Assumptions]
Recomputed here from the stated components (not copied):

| Scenario | Case | Build (pd x 300) | Ops 3y (pd x 3 x 300) | Hosting 3y (USD/month x 36) | Gross 3y USD |
|---|---|---|---|---|---|
| S1 | lo | 15 x 300 = 4,500 | 3 x 3 x 300 = 2,700 | 20 x 36 = 720 | 7,920 |
| S1 | mid | 25 x 300 = 7,500 | 5 x 3 x 300 = 4,500 | 40 x 36 = 1,440 | 13,440 |
| S1 | hi | 40 x 300 = 12,000 | 8 x 3 x 300 = 7,200 | 100 x 36 = 3,600 | 22,800 |
| S2 | lo | 25 x 300 = 7,500 | 5 x 3 x 300 = 4,500 | 40 x 36 = 1,440 | 13,440 |
| S2 | mid | 40 x 300 = 12,000 | 8 x 3 x 300 = 7,200 | 80 x 36 = 2,880 | 22,080 |
| S2 | hi | 70 x 300 = 21,000 | 12 x 3 x 300 = 10,800 | 200 x 36 = 7,200 | 39,000 |

These match `tco-model.md` TC-2 and the 0C preliminary TCO. Reading rule (Stage 32, restated): the planning range for the No-AI product is S1 lo to S2 hi, **USD 7,920 to 39,000 gross over 3 years, unvalidated, understated by the four unpriced terms** (toolchain, oversight, validation, exit) and also by `Dbl_t` and `Adopt_t`. The 3-year horizon and 0 % growth are inherited Assumptions (A-TC01).

### CM-3 Cost-side hurdle (arithmetic on Assumption figures; not a benefit claim)
For a project to merely cover its cost, undiscounted, over 3 years: required average benefit per year = gross cost / 3. On the 0C figures this is S1 2,640 / 4,480 / 7,600 and S2 4,480 / 7,360 / 13,000 USD per year (lo / mid / hi). These are **lower bounds** because four or more cost terms are missing, no discount rate is applied (none exists), and the figures are Assumptions. They say what a benefit would have to be, they do not say it will be.

### CM-4 What the repository measures that bears on cost [Verified Fact]
Third-party libraries in the hub 0; product vendors with fees 0 identified; model spend 0; full regression 2,403 s per pass on the laptop; hosting vendor none chosen (`tco-model.md` TC-3). Hold-all retention (OD-30) means storage grows with no policy (CLK-6).

### CM-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CMF-1 | [Verified Fact] Cost is Unknown except model spend USD 0 | Stage 32; `cost-leakage.md` CL-2 | Full cost cannot be stated | High | High | Inputs in CM-1 |
| CMF-2 | [Verified Fact] 0C ranges are internally consistent, wholly assumed, never finance-reviewed | CM-2; TCO-F1 | May frame a conversation, not a budget | Medium | High | Finance partner review |
| CMF-3 | [Verified Fact] No cost owner (RL-09 VACANT); 0 of 28 assets have an accepted steady-state owner | OD-34, OD-35 | Nobody to hold or report cost | Medium | High | Named holder |
| CMF-4 | [Inference] If hosting stays loopback-only on a laptop, cost is mainly labour and toolchain. Reasoning: TCO-F3 | `tco-model.md` | Which inputs matter | Low | Low | Hosting decision |
| CMF-5 | [Verified Fact] Reducing test coverage to save time is barred as a 'saving' (CG-7, RR-32-12) | Stage 32 | Prevents a false cost saving | Medium | High | none |


## Evidence References
`docs/32-finops/tco-model.md` TC-1..TC-5; `docs/00-preflight/ai-economics/preliminary-tco.md`; `docs/35-variance/cost-leakage.md` CLK-1..CLK-10; `docs/37-operating-model/finops-ownership.md`.

## Assumptions
- A-36-05 [Assumption] USD 300 per person-day, the 0C effort and hosting ranges and the 3-year horizon stay Assumptions (inherits A-32-18/19). Confirm: Dinesh and a Finance partner (SH-05, unfilled).
- A-36-06 [Assumption] Currency USD as in 0C; no confirmation exists (U-32-25).
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-04 Every input in the CM-1 right-hand column. U-36-05 Currency and budget.

## Unresolved Issues
- Finance review of the 0C ranges has never happened.

## Residual Risks
- RR-36-05 0C range quoted as a budget (Medium). RR-36-06 Understated range because terms are unpriced (Medium). RR-36-07 CM-3 hurdle quoted as a target benefit (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
