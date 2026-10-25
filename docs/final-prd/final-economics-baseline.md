---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "final-economics-baseline.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/36-roi/", "docs/32-finops/tco-model.md", "docs/35-variance/", "docs/03-problem-value/value-hypothesis.md", "docs/42-executive-defence/economic-value-summary.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
No economic value is realised or computable. Only the model spend (USD 0) is measured; the 3-year cost ranges are arithmetic on unvalidated assumptions.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### EC-1 Position [Verified Fact]
**Value realised: NONE claimed. ROI, NPV and payback are NOT COMPUTABLE** (Stage 36): verified benefits 0 items; 1 of 10 cost terms measured (model spend USD 0 by design); no discount rate exists; no labour rate, volume or cost of the real process exists; benefits sign-off BS-2 is UNSIGNED. The five value drivers VD-01..VD-05 are unquantified Assumptions. No variance in Stage 35 is attributable to the intervention.

### EC-2 Cost figures that exist [Verified Fact, with caveat]
| Figure | Value | Caveat |
|---|---|---|
| Model/token spend | USD 0 by design (No-AI) | the only measured cost term (Stage 32) |
| Gross 3-year cost, Scenario S1 (low / base / high) | USD 7,920 / 13,440 / 22,800 | re-derived arithmetic on unvalidated Stage 0C Assumptions; excludes four unpriced terms |
| Gross 3-year cost, Scenario S2 (low / base / high) | USD 13,440 / 22,080 / 39,000 | same caveat |
| Toolchain charges, hosting, build effort actuals, support, training | Unknown | RL-09 cost owner VACANT; D-32 items |
These are not benefits and not a budget. Stage 0C S3/S4 cost files cover only the AI options and should be labelled so (CA-15, an edit outside docs-only stages).

### EC-3 Value-leakage [Verified Fact]
17 value-leakage items (VL-01..VL-17), sized by counts only; no money or time leakage can be quantified. The build also incurred rework from late-caught defects (S21-DEV-02, S24-DEV-05, S28-DEV-08, S31-DEV-08).

### EC-4 Inputs needed to compute anything (Stage 36) 
I-01..I-19 (adoption share, persistence, minutes saved per case, rework and incident effort, month-end hours, loaded labour rate, haircut, overlap, horizon, cost terms, discount rate, timing, inflation, exit treatment, tax and currency) and preconditions PC-1..PC-10. All OPEN, owner Engagement lead (Dinesh Naik). Honest statement at any near-term review: **'ROI not computable.'**

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-14 [Assumption] The Stage 0C cost ranges are carried unchanged from Stage 32/36; I did not recompute them.

## Unknowns
- U-43-16 Every benefit and cost term except model spend.

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
