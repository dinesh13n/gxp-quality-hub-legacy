---
stage: "35 — Before-vs-After Variance + Value Leakage"
artifact: "kpi-variance-table.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 35 run)"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/baseline-kpi-sheet.md", "docs/34-measure-after/after-intervention-kpi-sheet.md", "docs/34-measure-after/kpi-comparability-check.md", "docs/04-baseline-kpis/kpi-dictionary.md", ".fde/orchestrator-decisions.md (OD-04, OD-07, OD-32, OD-33, OD-34, OD-35)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 35 adds files under `docs/35-variance/` and changes nothing else). No production after-data exists: the hub is not in production, there is no production telemetry, Stage 30 has not run and Stage 31 is not merged. Every 'after' figure is a Stage 34 SANDBOX measurement on the 125-case synthetic baseline (seed 4100) or an earlier stage's test result. Where a like-for-like pair exists it is labelled 'synthetic, sandbox, parity - not an improvement'. No improvement, saving, benefit or ROI is claimed, no number is invented, no stakeholder is invented, and no risk is accepted on Dinesh's behalf (OD-04, OD-32, HAR-11).**

## Summary
Variance is computed **only** for the three Stage 34 class-C1 pairs (K-09-OPS count and site split, K-15, K-11). All three show zero or record-existence variance, i.e. **parity, not improvement**. For the other 19 KPI ids no variance is computed, each with its Stage 34 reason (unchanged by construction, hub-path only, not comparable, Unknown). **There is no production after-data.**

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### V-1 Variance on like-for-like pairs (the only computed variances)
Rule applied (Stage 34 CC rule, restated, not new): same definition, same population, same reference time. Definitions are the frozen Stage 4 ones (`kpi-dictionary.md` v0.1, FROZEN-PROVISIONAL, unsigned).

| KPI | Before (Stage 4, synthetic) | After (Stage 34, sandbox hub path) | Absolute variance | Relative variance | Reading | Tag | Confidence |
|---|---|---|---|---|---|---|---|
| K-09-OPS backlog count (D-OPS) | 89 of 125 | 89 of 125 | 0 | 0 % | **synthetic, sandbox, parity - not an improvement.** The hub backfills the legacy status, so equality is expected by construction | [Verified Fact] (values); [Inference] (by construction) | High on the values; Low on any meaning |
| K-09-OPS split by site (BR-SP / DE-BY / GB-ENG / IN-BLR / JP-KN / US-TX) | 22 / 18 / 14 / 10 / 11 / 14 | 22 / 18 / 14 / 10 / 11 / 14 | 0 in every site | 0 % | **synthetic, sandbox, parity - not an improvement** | [Verified Fact] | High on the values; Low on meaning |
| K-15 Rework (reopen) rate | 6.4 % (8 / 125) | 6.4 % (8 / 125; `case_state` REOPENED = 8, 8 `marked_legacy_reopen`) | 0 pp | 0 % | **synthetic, sandbox, parity - not an improvement.** A snapshot status imported from legacy; it is not a change in rework | [Verified Fact]; [Inference] | High on values; Low on meaning |
| K-11 Decision recorded | 0 of 2 | 2 of 2 have an "accepted open" record (OPD-01/02 for DR-20; OPD-03 for DR-21; OD-22) | +2 records | n/a | A record now exists that **nobody has decided**; not a resolution and not a benefit. Counted by K-11's own wording (D-34-08, assumption) | [Verified Fact]; Medium on meaning | Medium |

**Not a variance:** the legacy path re-measured with the frozen script is byte-identical to the baseline (output sha256 `31ffa1b2…1ba`). That is "unchanged by construction" (the hub is additive and read-only toward legacy data), **not** evidence of "no regression" or of improvement (Stage 34 RR-34-04).

### V-2 KPIs with no computable variance
| Class (Stage 34) | KPI ids | Why no variance | Tag |
|---|---|---|---|
| C2 legacy unchanged by construction; hub side C4 not comparable | K-02, K-03, K-06, K-08, K-09 age (median/p90), K-09U, K-10, K-12, K-13, K-14, K-16, K-17, K-18, K-19, K-20 | Legacy value is identical because nothing in the legacy path changed. The hub side uses a different definition, population or reference time (hub `as_of` is wall clock 2026-10-25, 310 days after the frozen AS_OF 2025-12-19T07:11Z; no median/p90 ageing; different exception population 8,335 queue items vs 224 policy exceptions; different classification). Subtracting them would compare unlike things | [Verified Fact] |
| C3 hub-path only, no before | K-01 (0 unsafe actions in the Stage 26 attack suite, a test result), K-07 (replay check: queues and totals unchanged), K-21 (0 of 125) | Before is Unknown or undefined. A single-sided value has no variance | [Verified Fact] (sandbox/test) |
| C5 Unknown both sides | K-04-OPS/EVID/FIN, K-05, K-09-EVID, K-09-FIN, K-22 | No closure, evidence or effort timestamps exist anywhere in the repo (OD-07). K-04/K-05 are unmeasurable | [Verified Fact] |

### V-3 Proxies and inherited caveats [Verified Fact]
- P-01..P-04, K-06, K-08, K-09U are generator-bounded proxies (OD-07). K-10 compares unrelated populations; K-12/K-13 divide by the ops-table total (108) not by cases (125) (A-04-01 refuted). These caveats apply to before and after alike and are why even a future C1 pair on those KPIs would need a Stage 4 v0.2 addendum first.

### V-4 Direction-of-variance statement
- [Verified Fact] No KPI has an improving variance. No KPI has a deteriorating variance. The correct statement is "no variance measured on any production basis"; FAIL-02 and FAIL-05 of Stage 3 (improve one definition by worsening another; synthetic value presented as client result) are not triggered because no improvement is claimed.

## Evidence References
`docs/34-measure-after/after-intervention-kpi-sheet.md` sections B, C, F; `kpi-comparability-check.md` CC-1..CC-6; `docs/34-measure-after/evidence/after_measure_baseline.json`, `hub-06-values.json`, `hub-01g-verify-projection.json`; `docs/04-baseline-kpis/baseline-kpi-sheet.md`; `docs/03-problem-value/success-criteria.md` FAIL-02, FAIL-05.

## Assumptions
- A-35-01 [Assumption] Artifact directory is `docs/35-variance/` as instructed by the orchestrator, not `docs/35-value-leakage/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-35-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (variance only on Stage 34 C1 rows; leakage traced to repository findings; corrective actions are proposals). It does not accept any risk. Confirm: Engagement lead (Dinesh Naik).
- A-35-03 [Assumption] Variance is expressed as after minus before, in the KPI's own unit; no tolerance band exists in Stage 3/4 (targets are relative, A-03-13), so no 'material' threshold is defined. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-35-01 Any production variance for any KPI (no after window). Resolution: D-34-02 (define window, exposure, owner; supply PP-1 / AD-2 measurements).
- U-35-02 Whether ageing variance (K-09 median/p90) would be zero or not at the frozen reference time. Resolution: D-34-03 (`as_of` parameter) then re-run.

## Unresolved Issues
- Stage 4 freeze unsigned; Stage 4 v0.2 addendum (OD-07, Stage 34 CC-5) not raised.
- 5-row gap between K-06 matched rows (173) and hub `linked` (168) not investigated (U-34-02).

## Residual Risks
- RR-35-01 Zero variance read as 'no regression' or 'improvement'. Mitigation: parity labels above.
- RR-35-02 Imported-state parity (K-09, K-15) used as a performance claim in Stage 36.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 35). |
