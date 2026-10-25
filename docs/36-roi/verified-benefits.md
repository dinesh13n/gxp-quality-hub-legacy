---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "verified-benefits.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/35-variance/benefit-variance.md", "docs/35-variance/kpi-variance-table.md", "docs/35-variance/value-leakage-analysis.md", "docs/35-variance/corrective-action-backlog.md", "docs/34-measure-after/after-intervention-kpi-sheet.md", "docs/34-measure-after/adoption-metrics.md", ".fde/orchestrator-decisions.md (OD-04, OD-07)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on Dinesh Naik on his behalf (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
**Verified benefits valued in money: none. The verified-benefit list is empty (0 items).** The stage prompt allows only verified improvements into the financial model; nothing in the repository meets the bar. This file records, per candidate, exactly why it fails, so the list can be reopened row by row when evidence arrives.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### VB-1 Screening of every candidate against the Verified-Benefit test
Test (agent definition, Assumption A-36-04): a benefit is *verified* only if (a) it is a measured difference between two like-for-like values (same definition, population, reference time; Stage 34 rule), (b) the 'after' is from real operation, not a sandbox or test, (c) the difference is attributable to the intervention, and (d) a finance-approved rate and volume exist to convert it. All four are needed to enter the ROI/NPV model.

| Candidate | (a) like-for-like | (b) real operation | (c) attributable | (d) rate and volume | Verified? |
|---|---|---|---|---|---|
| K-09-OPS backlog 89 / 89 of 125 | Yes (parity) | No, sandbox | No (imported by construction) | No | **No** |
| K-15 rework 6.4 % / 6.4 % | Yes (parity) | No, sandbox | No | No | **No** |
| K-11 decision recorded 0 / 2 to 2 / 2 | By its own wording | No | Record exists, nobody decided | No | **No** |
| K-07 replay of 8,567 rows left queues unchanged | Hub only; legacy never measured | No, sandbox | n/a | No | **No** (fixture evidence of a mechanism) |
| K-01 0 unsafe actions | Hub only (test result) | No | Invariant, not a benefit | n/a | **No** |
| K-21 adoption 0 of 125 | Hub only | No | n/a | n/a | **No** (a leakage fact, VL-01) |
| K-04, K-05, K-22 (time, evidence, effort) | Unknown both sides | No | No | No | **No** |
| K-10 month-end | Unrelated populations (OD-07) | No | No | No | **No** |
| K-02, K-03, K-06, K-08, K-09 age, K-09U, K-12..K-20 | Not comparable or unchanged by construction (Stage 34 C2/C4) | No | No | No | **No** |

### VB-2 Result
- [Verified Fact] 0 of 22 KPI ids pass test (b). The 3 like-for-like pairs (4 rows) pass only (a), and show zero variance.
- [Verified Fact] Benefit valued in money: **0**. Benefit that can be stated in any unit as an improvement: **0**.
- [Inference] The honest 'verified benefits' number for this stage is therefore nil, and that is a statement about evidence, not about the product: a nil here does not show the product has no value (Stage 3: direction plausible, magnitude Unknown).

### VB-3 What would move a candidate to Verified (conditions, tied to the Stage 35 corrective backlog)
| Condition | Backlog item | Needed for test |
|---|---|---|
| Confirm no production use so far; define a real after-window | CA-01, CA-02 | (b) |
| Fix the yardstick: Stage 4 v0.2 addendum, `as_of` for ageing, closed/resolved decider | CA-05, CA-03, CA-07 | (a) |
| Pilot designed with comparison group or stable pre-trend, pre-registered KPIs | CA-04 | (c) |
| Time capture (closure, evidence-complete, reviewer effort) | CA-06 | (a) for time benefits |
| Finance-approved rate, volume, cost per case; cost owner | CA-13 | (d) |
| Re-run Stage 34 then Stage 35 on real data | CA-17 | all |

### VB-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| VBF-1 | [Verified Fact] Verified-benefit list is empty | VB-1; Stage 35 V-4 ('no KPI has an improving variance') | No monetisation possible | High | High | CA-01..CA-17 |
| VBF-2 | [Verified Fact] Stage 35 labels all computed variance 'parity, not improvement' | `kpi-variance-table.md` V-1 | Parity must not be carried into Stage 36 as a benefit (RR-35-02) | High | High | none |
| VBF-3 | [Inference] The first benefit likely to become verifiable is adoption-gated (K-21 > 0) followed by K-15 and K-09 on a real window; time benefits need capture design first. Reasoning: those KPIs have a comparable definition today, time KPIs do not | Stage 34 C1 vs C5 | Sequencing of the realisation plan | Low | Medium | CA-06 |


## Evidence References
`docs/35-variance/kpi-variance-table.md` V-1, V-2, V-4; `benefit-variance.md` BV-1; `docs/34-measure-after/after-intervention-kpi-sheet.md` sections B, C; `adoption-metrics.md` AD-1; `corrective-action-backlog.md` CB-1.

## Assumptions
- A-36-04 [Assumption] The four-part Verified-Benefit test in VB-1 is the agent's definition (the prompt says only 'verified improvements' and 'finance-approved rates'). Confirm: Engagement lead (Dinesh Naik).
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-03 Any production value for any KPI (U-35-01).

## Unresolved Issues
- No real after-window exists; no one has been named to supply production data (D-34-02).

## Residual Risks
- RR-36-03 Parity read as improvement (High). RR-36-04 Empty list read as 'product has no value' (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
