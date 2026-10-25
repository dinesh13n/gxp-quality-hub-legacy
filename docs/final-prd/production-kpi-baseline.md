---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "production-kpi-baseline.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/baseline-kpi-sheet.md", "docs/04-baseline-kpis/kpi-baseline-signoff.md", "docs/34-measure-after/after-intervention-kpi-sheet.md", "docs/34-measure-after/kpi-comparability-check.md", "docs/35-variance/before-after-analysis.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
No production KPI baseline exists. The file records the frozen-provisional synthetic baseline, the only three like-for-like pairs (all parity or a record that nobody decided) and the work needed to create a real baseline.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### KP-1 Position [Verified Fact]
**There is no production KPI baseline.** The hub is not in production; there is no after-window, telemetry or adoption (K-21 = 0 of 125; 0 principals). Every number below is from a synthetic sandbox snapshot and is labelled 'synthetic, unvalidated'. No improvement is claimed. This file is the *as-built KPI position*, not a production baseline.

### KP-2 Baseline KPIs (Stage 4) [Verified Fact]
22 KPI ids: 16 with a synthetic measured value (several Low confidence), 6 Unknown. The sheet is **FROZEN-PROVISIONAL**; owner sign-off was not given. Stage 5 refuted A-04-01 (OD-07), so K-10 compares unrelated populations. P-01/P-03/P-04 are generator-bounded proxies. K-04 (time to close) and K-05 are unmeasurable (no real closure/evidence timestamps exist). A Stage 4 v0.2 addendum has not been raised (D-34-04, CA-05).

### KP-3 The like-for-like pairs (Stage 34/35) [Verified Fact]
| KPI | Before (legacy snapshot) | Hub (shadow, sandbox) | Reading | Class |
|---|---|---|---|---|
| K-09-OPS backlog (D-OPS) | 89 of 125; sites 22 / 18 / 14 / 10 / 11 / 14 | identical | parity of an imported snapshot | not an improvement |
| K-15 rework (reopen) rate | 6.4 % (8 / 125) | identical | parity of an imported status | not an improvement |
| K-11 decision recorded | 0 of 2 | 2 of 2 'accepted open' records | records that nobody decided | not a resolution |
| K-21 adoption | n/a | 0 of 125 cases via the hub in production | not in production | n/a |
Other hub values: month-end total 622,826.44 (hub) vs 742,956.61 (legacy report) = DV-01, unapproved difference; unresolved-exception rate not comparable (different formula and population); time to close `null`.

### KP-4 Legacy-path KPIs [Verified Fact / Inference]
16 KPI ids are 'unchanged by construction' on the legacy path because the hub is additive and read-only toward legacy data. [Inference] That is a property of construction, not evidence of no regression or of improvement.

### KP-5 Honest labelling rules that stand
No figure may be presented without its definition tag and label (FR-MET-01, PNFR-20). A 'time saved', 'cost avoided' or 'ROI' number does not exist and must not be quoted (`final-economics-baseline.md`).

### KP-6 What the production baseline requires (not done)
Define the after-window (start, exposure, minimum duration, data owner; D-34-02/CA-01), time and effort capture (CA-06), adopted definitions and 48 h clock (CA-07; OPD-01..03), Stage 4 v0.2 addendum and `as_of` parameter (CA-03/05). Then re-run Stages 34/35/36 as v0.2 (CA-17).

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-13 [Assumption] Stage 34 values are as recorded at its merge (as_of 2026-10-25 wall clock for ageing buckets).

## Unknowns
- U-43-15 All production values (every KPI).

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
