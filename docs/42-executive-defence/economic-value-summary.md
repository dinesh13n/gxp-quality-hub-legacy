---
stage: "42 — Executive Defence & Final Value Story"
artifact: "economic-value-summary.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/36-roi/", "docs/32-finops/tco-model.md", "docs/32-finops/finops-model.md", "docs/35-variance/cost-leakage.md", "docs/00-preflight/ai-economics/"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.**
- **ROI: NOT COMPUTABLE.**
- **NPV: NOT COMPUTABLE** (no finance-approved discount rate exists anywhere in the repository).
- **Payback: NOT COMPUTABLE.**
- **Verified benefits: 0 items. Benefit sign-off: UNSIGNED.**
- Cost: **1 of 10 cost terms measured** (model spend USD 0 by design). Everything else is an assumption range or unpriced.

No saving, avoided cost, productivity gain or break-even is stated anywhere in this engagement's final story, and none may be stated from this document (C-25, C-26).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### EV-1 Why each metric cannot be computed
| Metric | Needs | Have | Verdict |
|---|---|---|---|
| ROI | verified benefit stream and full cost | 0 benefits; 1 of 10 cost terms | NOT COMPUTABLE |
| NPV | the above plus discount rate and timing | no discount rate; none chosen by the agent | NOT COMPUTABLE |
| Payback | benefit stream to accumulate against cost | none | NOT COMPUTABLE |
| Benefit realisation | after-window with measured effect | no window; K-21 = 0 of 125 | Not started |
| Scenario outcome | benefit ranges | cost ranges only (0C lo/mid/hi); no benefit ranges | Every net outcome NOT COMPUTABLE |

### EV-2 Cost side: what is and is not known
| Term | Status | Figure | Class |
|---|---|---|---|
| Model / token spend | Measured by design | USD 0 (No-AI; tripwire `model_calls_total = 0`) | [Verified Fact] |
| Build effort | Never recorded | S1 15/25/40 person-days; S2 25/40/70 at USD 300/day | [Assumption] (0C) |
| Operations | Not measured | S1 3/5/8 pd/yr; S2 5/8/12 pd/yr | [Assumption] |
| Hosting | Nothing deployed | S1 USD 20/40/100 per month; S2 40/80/200 | [Assumption] |
| Toolchain charges (code host, AI assistant, cloud workspace, CI) | Unknown | none | [Unknown] |
| Human oversight (reviewer minutes x volume x rate) | Not priced; 0C omitted it | none | [Unknown] |
| Validation and compliance | Not priced; compliance owner VACANT | none | [Unknown] |
| Exit | Not priced | none | [Unknown] |
| Parallel-run double work | No parallel-run definition | none | [Unknown] |
| Adoption, training, change | Not scoped | none | [Unknown] |

Re-derived Stage 0C gross 3-year ranges (arithmetic check only, inputs are Assumptions, four terms excluded): **S1 (deterministic) USD 7,920 / 13,440 / 22,800; S2 (deterministic plus non-ML part) USD 13,440 / 22,080 / 39,000** (lo/mid/hi). They are **not** a forecast, quote or budget and understate cost by the unpriced terms. The cost owner role RL-09 (finance partner) is VACANT.

### EV-3 Benefit side: five drivers, all Assumptions
VD-01 reconciliation time, VD-02 rework, VD-03 queue-inflation incidents (one documented in 2025, one INC-2025-014; frequency Unknown), VD-04 month-end, VD-05 audit defensibility (qualitative). [Verified Fact] None has a volume, a time-per-unit or a rate. The only hour figures (0.603 h/case; 65.14 h over 108 cases) are generator "modelled estimates" and are deliberately not used as value claims.

### EV-4 What leaks before value starts
17 documented leakage items (VL-01..VL-17), counted not priced: adoption 0/125; Zone H holders empty; authority switch and scheduler off; Stage 28 controls unwired; CI not installed; 0/28 owners; single approver; walkthroughs unsigned; four open risk registers; unowned definitions; no time capture (K-22 Unknown); wall-clock `as_of`; baseline freeze unsigned; parallel-running double work (VL-14, [Inference]); late-caught build defects with unrecorded rework hours; 2,403 s full-regression wall time; four unpriced TCO terms. (C-24)

### EV-5 What can be said at the executive level
1. "We built an inexpensive-to-run deterministic system; its measurable run cost in model spend is zero. Total cost of ownership is unknown."
2. "Whether it pays back is unknown, and cannot be estimated responsibly until three things exist: a real after-window, time and cost capture, and a finance-approved rate."
3. "The cheapest honest next step is to define the after-window and capture method (roadmap G1-10) before spending on anything else."

### EV-6 Inputs that unblock a re-run (Stage 36 slots; owner Dinesh unless stated)
Labour rate and loaded rate (finance partner role vacant); volumes (cases, feed rows, exceptions per period); reviewer minutes per item; effort actuals for build; hosting decision; toolchain plan charges; discount rate; benefit evidence from a window; an approver for benefits sign-off other than the builder if one can be found.

### EV-7 Hard questions
| Question | Defensible answer |
|---|---|
| Can you give me a rough payback? | No. Any figure would be invented; there is no benefit stream. |
| But costs are small, right? | The gross ranges are small relative to many projects, but they rest on a day-rate assumption, omit four terms and exclude the human time to run the thing. Unknown. |
| What would convince you value exists? | A defined window with real users, time and effort capture, a signed baseline, a named finance rate, and a before/after on like-for-like KPIs reviewed by someone other than the builder. |
| Is zero model spend a benefit? | No. It is a design property of No-AI. It is a cost-avoided only relative to an AI alternative that was never priced or built. |

## Evidence References
`docs/36-roi/` (11 files), `docs/32-finops/tco-model.md`, `finops-model.md`, `token-leakage-analysis.md`, `docs/35-variance/cost-leakage.md`, `docs/35-variance/value-leakage-analysis.md`, `docs/03-problem-value/value-hypothesis.md`; C-25, C-26, C-24.

## Assumptions
0C ranges and the USD 300/day rate are unvalidated Assumptions (owner: Dinesh).

## Unknowns
All of EV-6.

## Unresolved Issues
Stage 36 inputs I-01..I-19 and preconditions PC-1..PC-10; BS-2 signatures; Stage 36 re-issue as v0.2 once an after-window exists.

## Residual Risks
An unsupported ROI figure entering a deck. Mitigation: EI-2 of the evidence index forbids it.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
