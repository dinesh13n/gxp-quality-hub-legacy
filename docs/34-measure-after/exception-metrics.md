---
stage: "34 — Measure After-Intervention KPIs"
artifact: "exception-metrics.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 34 run)"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/baseline-kpi-sheet.md (K-06, K-09U, K-19, K-20)", "docs/34-measure-after/evidence/after_measure_baseline.json", "docs/34-measure-after/evidence/hub-10-ingest-legacy.json", "docs/34-measure-after/evidence/hub-12-verify-replay.json", "docs/34-measure-after/evidence/hub-15-values-after-intake.json", "docs/26-tevv/red-team-findings.md", "docs/28-reliability/failure-injection-results.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Every number below is either (a) a SANDBOX measurement on a copy under `~/fde_sbx` of the 125-case synthetic baseline (seed 4100, sha256 `c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa`), or (b) a result already recorded by an earlier stage's tests, or (c) Unknown. NOTHING here is production performance: the hub is not in production, no production telemetry exists, Stage 30 has not been run and Stage 31 is not merged (in progress on branch stage-31-observability by another agent). Documentation only. No KPI definition is changed, no benefit is claimed, no risk is accepted (OD-04, OD-32).**

## Summary
Exceptions are measured on two separate paths and **not combined**. (1) Legacy path, frozen definitions: unchanged by construction (K-06, K-09U, K-19, K-20). (2) Hub path, sandbox shadow intake of the same legacy feeds: **8,516 queue items, of which 8,109 EXCEPTION (unmatched), 223 QUARANTINED, 3 flagged, 181 validated**; 8,335 of 8,335 exception-queue items open (rate 1.0000) because no reviewer exists. The two paths use different classifications, so there is no exception-rate "improvement" or "deterioration" to report.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### EX-1 Legacy path (frozen definitions, sandbox re-run, identical to Stage 4) [Verified Fact]
| KPI | Value | Note |
|---|---|---|
| K-06 unmatched reference rate | 97.98 % (8,394 / 8,567); 99.11 % (222 / 224) | generator residue; not a business baseline (Stage 4) |
| K-09U unresolved exception rate | UE-1 75.0 % (168 / 224); UE-2 52.2 % (117 / 224); outcomes BLOCKED 51, OPEN 57, REVIEW 60, WAIVED 56 | meaning of WAIVED/BLOCKED unowned (U-04-03) |
| K-19 batch runs | rejected 3.25 % (454 / 13,979); FAILED 31.7 % (19 / 60); all 19 FAILED runs have accepted_count > 0 | semantic inconsistency, unchanged |
| K-20 outages | median 2.30 h, p90 3.74 h (n = 64); 8 of 72 unresolved | history ends 2024-04-22 |

### EX-2 Hub path, sandbox shadow intake [Verified Fact; synthetic, sandbox]
Source: `evidence/hub-10-ingest-legacy.json`, `hub-11`, `hub-13`.
| Partner-feed outcome (8,567 rows) | Count | Reason counts (queue reasons) |
|---|---|---|
| EXCEPTION (queue `unmatched`) | 8,109 | UNMATCHED_REF 7,903; NO_BUSINESS_KEY 208 (the sum exceeds 8,109 by 2: overlap not analysed) |
| QUARANTINED (queue `quarantine_invalid`) | 223 | UNSUPPORTED_REVISION 223 |
| VALIDATED_WITH_FLAGS (queue `flagged_value`) | 3 | NEGATIVE_VALUE (161 reason entries reported by the CLI across all outcomes) |
| VALIDATED | 165 (181 incl. 15 source messages and 1 gateway row) | contract check on source messages: 15 pass; gateway 1 fail; partner_feed 8,567 fail (record_only mode: recorded, not enforced, OD-28) |
| NOOP_DUPLICATE | 67 (the REPLAY rows) | - |
- [Verified Fact] Queue totals before and after the replay check are identical (8,516 items; EXCEPTION 8,109 / QUARANTINED 223 / VALIDATED 181 / VALIDATED_WITH_FLAGS 3).
- [Verified Fact] MET-UNRESOLVED-EXC-RATE-D-OPS after intake: open 8,335 / all 8,335 = 1.0000 (IN-BLR 2/2, JP-KN 1/1, "unknown" site 8,332/8,332). Before intake: null, n = 0, `no_exception_queue_items`.
- [Inference] The 100 % is the mechanical result of "nobody has worked the queue" in a store with 0 principals. It is neither an exception-resolution KPI value nor comparable to K-09U.
- [Verified Fact] Exception handling by the code is deterministic and bounded: no row was dropped (8,567 in, 8,567 outcomes), duplicates were counted out not removed, negative quantities were flagged not corrected (consistent with Stage 4: no row removed).

### EX-3 Software exceptions and failures (test-time, not production) [Verified Fact from earlier stages]
- Stage 28: FI-01..FI-09 PASS; FI-13/FI-14 not run; resilience mechanisms built but not wired into `gateway-pull` / `web serve` (OD-35).
- Stage 26: 11 findings F-01..F-11 registered, F-01..F-07 fixed and F-08..F-10 closed in Stage 27, F-11 open; behaviour changes recorded in Stage 27 (e.g. 401 anonymous unknown action, 400 lone surrogate, 408 read timeout, 503 store fault, 429 after 100 refusals per 60 s) are agent assumptions, not approved (OD-34).
- Stage 29: F-29-01 (verify-audit KeyError after tamper) open, routed to Stage 30.
- No production error rate, incident count or MTTR for the hub exists: **Unknown**; K-20 is about upstream legacy outages and is not applicable to hub faults.

### EX-4 Comparability of exceptions [Inference, reasoning in kpi-comparability-check.md CC-4]
Hub classes (UNMATCHED_REF, NO_BUSINESS_KEY, QUARANTINED, NOOP_DUPLICATE) are not the Stage 4 K-06 test. Stage 4 matched 173 feed rows to cases, the hub linked 168: unexplained 5-row gap [Unknown, U-34-02].

## Evidence References
`evidence/hub-10-ingest-legacy.json`, `hub-11-report-before-replay.json`, `hub-12-verify-replay.json`, `hub-13-report-after-replay.json`, `hub-15-values-after-intake.json`; `evidence/after_measure_baseline.json` keys `K-06_*`, `policy_exception_outcomes`, `batch_runs`, `outages`; `docs/26-tevv/red-team-findings.md`; `docs/28-reliability/failure-injection-results.md`.

## Assumptions
- A-34-09 [Assumption] Contract mode stays `record_only` everywhere (OD-28), so contract failures are recorded and do not change outcomes. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-34-09 Production exception volumes, ageing and resolution rates (no production queue). Supply: exception counts and resolution timestamps per queue per week from a running instance, with the business meaning of WAIVED/BLOCKED (U-04-03).
- U-34-02 5-row gap (K-06 173 vs hub linked 168).

## Unresolved Issues
- The 5-row K-06 gap (U-34-02) and the 2-row reason overlap in EX-2 are open. Totals reconcile: partner-feed outcomes 8,109 + 223 + 3 + 165 + 67 = 8,567; queue items 8,500 (non-duplicate feed rows) + 15 + 1 = 8,516 [Verified Fact: arithmetic].

## Residual Risks
- RR-34-07 A reader sets a target on the 1.0000 or on 97.98 %; both are artefacts (no reviewer; generator residue).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 34). |
