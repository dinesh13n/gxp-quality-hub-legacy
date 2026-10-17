---
stage: "4 — Capture Before-AI / Before-Intervention KPIs"
artifact: "baseline-kpi-sheet.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/evidence/measure_baseline.py", "docs/04-baseline-kpis/evidence/measure_baseline.output.json", "docs/04-baseline-kpis/evidence/app_baseline_sandbox_output.txt", "data/legacy.sqlite3 (sha256 c254649f…d70aa)", "docs/02-stakeholders/decision-rights-map.md"]
supersedes: "none"
---
## Summary

**LABEL ON EVERY VALUE BELOW: measured on synthetic baseline data (method validation only). Not real-world performance. Not a target.** Population: the 125-case shipped `data/legacy.sqlite3` (OD-02, PROVISIONAL). Reference time AS_OF 2025-12-19T07:11Z (dataset max timestamp). Of 22 KPIs, **16 have a measured synthetic value (several Low confidence) and 6 are Unknown** (no data exists in repo; collection method recorded; K-04/K-05 have proxies only). No definition of closed/resolved is selected; D-OPS/D-EVID/D-FIN are reported separately.

## Findings

Value classes: [Verified Fact] = computed by the cited reproducible query; [Unknown] = cannot be computed from repo data.

| KPI | Current value (synthetic) | Period | Population (n) | Class | Confidence | Note |
|---|---|---|---|---|---|---|
| K-01 Unsafe action count | **Unknown** | n/a | n/a | [Unknown] | n/a | No action/audit log in DB; cannot show 0 or >0. Collection: Stage 7 characterisation + audit-log design (Stage 12/23). |
| K-02 Source attribution rate | **0 % (0 of 20)** STATUS_REVIEWED events carry an evidence/source key (payload keys: reviewer, severity only) | 2023-01-25..2025-12-19 | 20 events | [Verified Fact] (structural presence only) | Medium | Says nothing about whether evidence exists elsewhere (e.g. signed PDFs mentioned in case notes). |
| K-03 Definition transparency | **0 % (0 of 6)** figures output by `app/baseline.py` declare a definition | current code | 6 keys | [Verified Fact] | High (for this module) | Other reports/endpoints not enumerated (U-04-05, Stage 7). |
| K-04-OPS Time to close | **Unknown** | — | 36 CLOSED cases, no closure timestamp | [Unknown] | n/a | See proxy P-01. |
| K-04-EVID Time to close | **Unknown** | — | 0 of 36 verifiable | [Unknown] | n/a | No evidence/approver data. |
| K-04-FIN Time to resolved | **Unknown (definition itself unowned)** | — | — | [Unknown] | n/a | DR-20 gap. |
| K-05 Time to evidence | **Unknown** | — | — | [Unknown] | n/a | Proxies P-01 (created→first review: median 12.06 h, p90 25.62 h, n=20), P-02 (created→external-feed message: median 2.90 h, p90 4.14 h, n=15). Not evidence-complete times. |
| K-06 Unmatched reference rate | **97.98 %** partner_feeds (8,394 of 8,567); **99.11 %** policy_exceptions (222 of 224) | feeds 2021-01..2024-12 | 8,567 / 224 | [Verified Fact] | High (arithmetic) / Low (meaning) | Test residue (IO-10): feeds/exceptions reference IDs outside the 125 cases (4,590 distinct ref_ids). Not a business baseline. By status: NEW 7,837/8,000; RETRY 490/500; REPLAY 67/67. |
| K-07 Replay safety | **Unknown** (behavioural) | — | — | [Unknown] | n/a | Presence only: 67 REPLAY rows, all 67 have a matching original feed row (same ref_id, source_ts, kind). Safety not tested; requires sandbox replay test (Stage 7/16). |
| K-08 Reconciliation delay | Median **0.02 h**, p90 **168 h**, **75.24 %** within 4 h; 2,234 of 8,567 rows (26.1 %) have **negative** delay (ingest before source) | feeds 2021-01..2024-12 | 8,567 | [Verified Fact] | Low | Negative delays are a data-quality defect; headline stats not decision-grade. NEW median 0.02/p90 168; RETRY 0.02/168; REPLAY 1.02/25. |
| K-09-OPS Backlog (D-OPS) | **89 of 125** not CLOSED; age median **565.1 d**, p90 **974.2 d**; buckets ≤90 d: 11, 91-365 d: 21, 366-730 d: 26, >730 d: 31 | snapshot 2025-12-19 | 125 | [Verified Fact] | Medium | By site (not closed / total; median age d): BR-SP 22/25; 656.1 · DE-BY 18/30; 561.6 · GB-ENG 14/25; 301.5 · IN-BLR 10/13; 578.9 · JP-KN 11/16; 477.8 · US-TX 14/16; 667.9. Site n is 13-30: indicative only. |
| K-09-EVID Backlog (D-EVID) | **Unknown; upper bound 125 of 125** (no case can be shown evidence-complete) | snapshot | 125 | [Unknown] with bound | n/a | Bound follows from `cases` columns (no evidence/approver). 36 CLOSED cases are unverifiable, not "bad". |
| K-09-FIN Backlog (D-FIN) | **Unknown (definition unowned)** | — | — | [Unknown] | n/a | |
| K-09U Unresolved exception rate | UE-1 (outcome<>WAIVED): **75.0 %** (168 of 224); UE-2 (OPEN+REVIEW): **52.2 %** (117 of 224). Outcomes: BLOCKED 51, OPEN 57, REVIEW 60, WAIVED 56 | 2021-01..2024-12 | 224 | [Verified Fact] | Low | 222 of 224 exceptions point at non-existent cases; meaning of WAIVED/BLOCKED unowned (U-04-03). |
| K-10 Month-end comparability | **8 of 36** months equal; totals **125** (cases) vs **108** (operating_costs.total_cases); Σ|monthly diff| = **51** | 2023-01..2025-12 | 36 months | [Verified Fact] | Medium | Depends on A-04-01. Consistent with Stage 3 claim SC-04 that ops and finance totals differ. |
| K-11 Decision recorded | **0 of 2** (DR-20, DR-21 have no decider/decision) | to 2026-10-17 | 2 | [Verified Fact] | High | `docs/02-stakeholders/decision-rights-map.md` L40-41. |
| K-12 Effort per case | **0.603 h/case** (65.14 h / 108 cases) | 2023-01..2025-12 | 108 per ops table | [Verified Fact] | Low | Reproduced independently by `python3 -m app.baseline` in sandbox (0.603). Estimates, not time records; denominator differs from 125 (K-10). On 125 cases: 0.521 h/case (derived). |
| K-13 Infra cost per case | **USD 23.40** (2,527.56 / 108) | same | 108 | [Verified Fact] | Low | Monthly infra figure is near-constant (e.g. 70.14 in 2023-01..03), so per-case value is an artefact of volume. |
| K-14 Throughput | **3.47 cases/month**; 40 (2023), 40 (2024), 45 (2025) | 2023-01..2025-12 | 125 | [Verified Fact] | Medium | Too small for seasonality. |
| K-15 Rework (reopen) rate | **6.4 %** (8 of 125) | snapshot | 125 | [Verified Fact] | Low | Snapshot status only; no reopen history events. |
| K-16 Manual-review share | **23.2 %** (29 of 125) by `manual_review_required` rule | snapshot | 125 | [Verified Fact] | Medium | Rule output, not observed review effort. |
| K-17 Deviations closed w/o root cause | **66.7 %** (8 of 12 CLOSED) | 2023-01+ | 42 deviations | [Verified Fact] | Low | Synthetic nulls (all statuses: 21 of 42 null). |
| K-18 CAPA overdue share | **46.2 %** (6 of 13 not verified) | snapshot | 21 CAPA | [Verified Fact] | Low | Also 4 of 8 VERIFIED CAPA link to deviations that are not CLOSED (integrity oddity). |
| K-19 Batch-run rejection / failure | Rejected **3.25 %** (454 of 13,979 input); FAILED runs **31.7 %** (19 of 60) | 2021-01..2024 | 60 runs | [Verified Fact] | Low | All 19 FAILED runs have accepted_count>0 (semantic inconsistency); input=accepted+rejected holds in all 60. |
| K-20 Outage MTTR / open | Median **2.30 h**, p90 **3.74 h** (n=64 resolved); **8 of 72** unresolved | 2021-01-01..2024-04-22 | 72 | [Verified Fact] | Low | Period ends 2024-04, before case data ends. |
| K-21 Adoption | **Not applicable pre-intervention (no value)** | — | — | [Unknown] | n/a | Defined for Stage 34. |
| K-22 Rework effort | **Unknown** | — | — | [Unknown] | n/a | No rework time capture; labour rate also Unknown (U-03-17). |

Tally by KPI id (22): **16 have a measured synthetic value** (K-02, K-03, K-06, K-08, K-09 [D-OPS and exception rate only; D-EVID and D-FIN Unknown], K-10, K-11, K-12..K-20); **6 are Unknown** (K-01, K-04 all variants, K-05, K-07, K-21, K-22). K-02 is a structural-presence value, and K-04/K-05 have proxies only (`proxy-metrics.md`). Rely on the Class and Confidence columns.

## Evidence References

`evidence/measure_baseline.output.json` (sha256 31ffa1b2…61ba, reproducible: re-run produced byte-identical output); `evidence/app_baseline_sandbox_output.txt`; query-per-KPI in `data-source-map.md`.

## Assumptions

A-04-01 (total_cases = cases created in month), A-04-02 (4 h is a reporting cut only), A-04-03: AS_OF = dataset max timestamp is an acceptable snapshot time (confirm: Engagement lead (Dinesh Naik), Stage 5).

## Unknowns

K-01, K-04 (all), K-05, K-07, K-09-EVID, K-09-FIN, K-21, K-22 — no data; resolution paths in `measurement-methodology.md`.

## Unresolved Issues

- No KPI value is real-world evidence. Magnitudes for Stage 3 relative targets (A-03-13) still cannot be set: the exception-effort magnitude U-03-01 is not measurable from this DB (hours/case 0.603 is a generated estimate).
- FAIL-06 test (is the problem negligible?): cannot be answered from synthetic data; deferred to Stage 6 (root cause) and a real-data decision by Dinesh.

## Residual Risks

- Reader may quote synthetic numbers as client performance (FAIL-05). Mitigation: label above; Stage 34/35 must compare like with like (same DB hash, same script).
- K-06/K-08/K-09U figures are dominated by generator residue and negative timestamps.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial synthetic baseline. |
