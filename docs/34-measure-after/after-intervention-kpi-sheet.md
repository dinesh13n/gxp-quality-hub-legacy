---
stage: "34 — Measure After-Intervention KPIs"
artifact: "after-intervention-kpi-sheet.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 34 run)"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/kpi-dictionary.md (sha256 516e2dd8…defe5)", "docs/04-baseline-kpis/baseline-kpi-sheet.md", "docs/04-baseline-kpis/evidence/measure_baseline.py (sha256 cb062e1b…60a6)", "docs/34-measure-after/evidence/after_measure_baseline.json", "docs/34-measure-after/evidence/after_app_baseline.txt", "docs/34-measure-after/evidence/hub-*.json", "docs/26-tevv/tevv-results.md", "docs/28-reliability/failure-injection-results.md", ".fde/orchestrator-decisions.md (OD-04, OD-07, OD-09, OD-22, OD-32)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Every number below is either (a) a SANDBOX measurement on a copy under `~/fde_sbx` of the 125-case synthetic baseline (seed 4100, sha256 `c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa`), or (b) a result already recorded by an earlier stage's tests, or (c) Unknown. NOTHING here is production performance: the hub is not in production, no production telemetry exists, Stage 30 has not been run and Stage 31 is not merged (in progress on branch stage-31-observability by another agent). Documentation only. No KPI definition is changed, no benefit is claimed, no risk is accepted (OD-04, OD-32).**

## Summary
After-intervention sheet for the 22 Stage 4 KPIs (K-01..K-22, with the `-OPS/-EVID/-FIN` variants), using the Stage 4 definitions **unchanged** (`kpi-dictionary.md` sha256 `516e2dd83e05…55b0e4`, byte-identical to `main`; this stage adds files only under `docs/34-measure-after/`).

**Result in one paragraph.** There is no production "after" value for any KPI. In the sandbox the intervention can be measured in two ways: (1) the **legacy path**, re-measured with the frozen Stage 4 script on a sandbox copy: output is **byte-identical** to the baseline (sha256 `31ffa1b2…1ba`), because the hub is additive and read-only toward the legacy data (this is "unchanged by construction", NOT evidence that anything improved or failed to improve); (2) the **hub path** (`python -m hub.metrics`, `hub.intake`) run on a sandbox copy of the same 125 cases. Only **three** KPIs can be shown before-vs-after on a like-for-like basis (K-09-OPS count and site split, K-15, K-11), and two of those are parity or record-existence, not improvement. Everything else is "unchanged by construction", "hub-path only (no before)", "not comparable" (reason given) or Unknown. **No improvement, saving or benefit is claimed for any KPI.**

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### A. Conventions
- Columns: **Before** = Stage 4 v0.1 value (synthetic, AS_OF 2025-12-19T07:11Z). **After, legacy path** = frozen `measure_baseline.py` / `python3 -m app.baseline` on a sandbox copy, run 2026-10-25. **After, hub path** = sandbox run of the hub CLIs on a fresh sandbox store (scratch `~/fde_sbx/s34-scratch`; 125-case backfill + shadow intake of the legacy partner feeds; scripts `evidence/run_hub_metrics.sh`, `evidence/run_hub_intake.sh`). **Comparable?** = like-for-like (same definition, same population, same reference time) YES / NO with the reason.
- Every value is **synthetic, sandbox, not production**. Confidence follows Stage 4 (the unit is not made more reliable by a re-run).
- Comparability classes: **C1** like-for-like both measured; **C2** legacy path re-measured, unchanged by construction; **C3** hub-path measured, no before; **C4** not comparable (different definition, population or reference time); **C5** Unknown on both sides.

### B. After sheet
| KPI | Before (Stage 4) | After, legacy path (frozen script) | After, hub path (sandbox) | Class | Comparable? / reason | Evidence class |
|---|---|---|---|---|---|---|
| K-01 Unsafe action count | Unknown (no action log) | Unknown (still no action/audit log) | **0 unsafe actions observed in the Stage 26 attack suite** (0 Zone H bypass in A02/A03/A04; mutants M1, M2 killed; 0 model calls, 0 egress). Operationally: 0 human principals, 0 sessions, 0 dispositions in a fresh sandbox store, so there was no opportunity for an unsafe action | C3 | NO - before is Unknown; a test result is not an operational count. Caveats: mutants M5/M9/M10 survive, F-08/F-09 are test gaps | [Verified Fact] (test result); operational count [Unknown] |
| K-02 Source attribution rate | 0 % (0 of 20) | 0 % (0 of 20), identical | n = 0 human decisions through the hub. The 250 backfilled events (125 CASE_IMPORTED + 125 FACT_RECEIVED, actor_kind system) carry no `evidence_refs`; they are imports, not reviews | C2 / C4 | Legacy: same by construction. Hub: NO - different population (no STATUS_REVIEWED equivalent exists); the mechanism (decision needs evidence refs) is "supported at mechanism level" (RH-1, tevv-results TR-7), not a rate | [Verified Fact] / [Inference] |
| K-03 Definition transparency | 0 % (0 of 6) | 0 % (0 of 6): `app.baseline` still returns the same 6 untagged keys | **4 of 4** definition-involving metric values carry definition tag + policy version + status + label (MET-TTC-C-OPS, MET-TTC-C-EVID, MET-BACKLOG-D-OPS, MET-UNRESOLVED-EXC-RATE-D-OPS); the 5th figure (month-end total) involves no closed/resolved concept and carries no tag by design. All tags are policy status `candidate` | C2 / C4 | Legacy: unchanged. Hub: NO - a different report population (hub metrics, not `app/baseline.py`); shown side by side, no "improved" headline | [Verified Fact] (sandbox) |
| K-04-OPS Time to close | Unknown | Unknown | MET-TTC-C-OPS: value null, n = 0, open_count 125, `no_completed_cycles` (verdict `not_available_no_adopted_policy`) | C5 | NO - still unmeasurable (no closure timestamp exists). RH-4 "measurable, not improved" is not even reached on baseline data | [Verified Fact] |
| K-04-EVID | Unknown | Unknown | MET-TTC-C-EVID: null, n = 0, open_count 125 | C5 | as above | [Verified Fact] |
| K-04-FIN | Unknown (definition unowned) | Unknown | no hub metric (D-FIN undefined) | C5 | D-FIN still undefined (OPD-01 accepted open) | [Unknown] |
| K-05 Time to evidence | Unknown; proxies P-01 median 12.06 h / p90 25.62 h (n=20), P-02 2.90 h / 4.14 h (n=15) | Unknown; proxies identical | = MET-TTC-C-EVID null | C2 / C5 | Proxies unchanged by construction; K-05 itself Unknown | [Verified Fact] (proxies) / [Unknown] |
| K-06 Unmatched reference rate | 97.98 % (8,394 / 8,567 feeds); 99.11 % (222 / 224 exceptions) | identical | No K-06 metric exists in the hub (BEH-MET-10 is R2, not seeded). Shadow intake of the 8,567 feed rows: EXCEPTION 8,109 (UNMATCHED_REF 7,903 + NO_BUSINESS_KEY 208, less overlap), QUARANTINED 223 (UNSUPPORTED_REVISION), NOOP_DUPLICATE 67, VALIDATED 165, VALIDATED_WITH_FLAGS 3; `linked` 168 | C2 / C4 | Legacy: unchanged. Hub: NO - a different classification (quarantine and duplicate precedence, NO_BUSINESS_KEY separate). Frozen K-06 counts 173 matched rows, the hub links 168: 5-row gap not investigated [Unknown] | [Verified Fact] / [Unknown] (gap) |
| K-07 Replay safety | Unknown (67 REPLAY rows present; safety untested) | Unknown (legacy replay not run here) | `hub.intake verify-replay`: re-delivered 8,567 rows, all NOOP_DUPLICATE, **queue sizes and totals unchanged** (8,516 items before and after; EXCEPTION 8,109 / QUARANTINED 223 / VALIDATED 181 / VALIDATED_WITH_FLAGS 3), 0 conflicts, `ok: true`. Note: `raw_intake` grows by the re-delivered rows (8,583 to 17,150); safety holds at outcome level, not storage level | C3 | NO - before is Unknown. Hub-path invariant held in this sandbox run; legacy path never measured | [Verified Fact] (sandbox) |
| K-08 Reconciliation delay | median 0.02 h, p90 168 h, 75.24 % <= 4 h; 26.1 % negative delays | identical | not measured (no hub delay metric; hub clocks in a sandbox would measure sandbox ingest time) | C2 | NO for the hub; legacy unchanged | [Verified Fact] / [Unknown] |
| K-09-OPS Backlog (D-OPS) | 89 of 125; age median 565.1 d, p90 974.2 d; buckets 11 / 21 / 26 / 31; sites BR-SP 22, DE-BY 18, GB-ENG 14, IN-BLR 10, JP-KN 11, US-TX 14 | identical | MET-BACKLOG-D-OPS (candidate D-OPS@1): **89 of 125**; per-site backlog **22 / 18 / 14 / 10 / 11 / 14** (identical to Stage 4); buckets at the hub's as_of 2026-10-25 (wall clock): <=90 d 0, 91-365 d 6, 366-730 d 29, >730 d 54; no median/p90 age | C1 (count, sites) / C4 (age) | Count and site split: YES, parity (hub reproduces the legacy count from its 125-case backfill; not an improvement). Age buckets and median/p90: NO - the hub uses wall-clock as_of (310 days after the frozen AS_OF 2025-12-19) and emits no median/p90 | [Verified Fact] |
| K-09-EVID | Unknown; upper bound 125 of 125 | same | no evidence records (`evidence_record` 0 rows) | C5 | Bound unchanged | [Unknown] |
| K-09-FIN | Unknown | Unknown | none | C5 | D-FIN undefined | [Unknown] |
| K-09U Unresolved exception rate | UE-1 75.0 % (168 / 224); UE-2 52.2 % (117 / 224) | identical | MET-UNRESOLVED-EXC-RATE-D-OPS: null (n = 0) before intake; **1.0000 (8,335 of 8,335 open)** after the shadow intake (IN-BLR 2/2, JP-KN 1/1, unknown 8,332/8,332) | C2 / C4 | Hub: NO - different formula (open queue items / all queue items, A-12-F07-2) and population (feed-derived queue items, not `policy_exceptions`). The 100 % reflects that no reviewer has acted (0 principals), not a performance level | [Verified Fact] |
| K-10 Month-end comparability | 8 of 36 months equal; 125 vs 108; sum abs diff 51 | identical | not computed by design (`operating_costs.total_cases` refused as "cases created", E-MET-SOURCE-REFUSED, OD-07). Related, NOT K-10: month-end total of `cases.amount` = **622,826.44, n = 125** (legacy SQL report gives 742,956.61, BB-08) | C2 / C4 | Hub: NO - a different quantity. Also see kpi-comparability-check.md: A-04-01 was refuted (OD-07), so K-10 compares unrelated populations | [Verified Fact] |
| K-11 Decision recorded | 0 of 2 | 0 of 2 in `decision-rights-map.md` (DR-20, DR-21 still marked GAP) | **2 of 2 have an "accepted open" record**: OPD-01/02 (DR-20) and OPD-03 (DR-21) in `docs/09-initial-prd/open-product-decisions.md`, confirmed in OD-22 (Dinesh, 2026-10-20) | C1 | YES by the K-11 text ("owner+date or accepted-open record"). It records that nobody decided; no decider exists. Not a resolution | [Verified Fact]; Medium confidence on meaning |
| K-12 Effort per case | 0.603 h/case | 0.603 (`python3 -m app.baseline`, sandbox) | none (no time records; cost metrics are `modelled`) | C2 | NO for hub; legacy unchanged by construction | [Verified Fact] |
| K-13 Infra cost per case | USD 23.40 | identical (derived from the same JSON) | none | C2 | as K-12. Hub cost is a separate Stage 32 matter (model spend USD 0 by design, other costs Unknown) | [Verified Fact] |
| K-14 Throughput | 3.47 cases/month | identical | n/a (the hub creates no cases) | C2 | unchanged by construction | [Verified Fact] |
| K-15 Rework (reopen) rate | 6.4 % (8 / 125) | identical | `case_state` REOPENED = 8 of 125 (6.4 %); 8 `marked_legacy_reopen` in the backfill | C1 | YES, parity of a snapshot status; the hub imports the legacy status. Not a rework change | [Verified Fact] |
| K-16 Manual-review share | 23.2 % (29 / 125) | identical (legacy rule unchanged) | Unknown: the hub ships NO active rule set (OD-16); the as-found rule sets are loaded inactive | C2 / C5 | NO for hub | [Verified Fact] / [Unknown] |
| K-17 Deviations closed w/o root cause | 66.7 % (8 / 12) | identical | n/a. (`deviation_register` in the hub store holds 11 behaviour-preservation rows DV-xx, a different concept; not K-17) | C2 | unchanged by construction | [Verified Fact] |
| K-18 CAPA overdue share | 46.2 % (6 / 13) | identical | n/a | C2 | as above | [Verified Fact] |
| K-19 Batch-run rejection / failure | 3.25 %; FAILED 31.7 % (19 / 60) | identical | Unknown: `run_event` has 0 rows (no hub run in the store; scheduler OFF) | C2 / C5 | unchanged | [Verified Fact] / [Unknown] |
| K-20 Outage MTTR / open | median 2.30 h, p90 3.74 h (n = 64); 8 of 72 open | identical (history ends 2024-04-22) | n/a. Stage 28 failure injections FI-01..09 are tests, not outages | C2 / C4 | NO - injected faults are not upstream outages | [Verified Fact] |
| K-21 Adoption | not measurable pre-intervention | n/a | **0 of 125 cases handled via the hub in production** - the hub is not in production (engagement-lead instruction for this stage); the working tree has no hub store (`data/` holds no `hub.sqlite3`); `zone_h.holders` EMPTY, 0 principals; scheduler, authority switch ship OFF. A sandbox shadow run is not adoption | C3 | n/a (no before by definition) | [Verified Fact] (repo state) / production value [Unknown] |
| K-22 Rework effort | Unknown | Unknown | Unknown (no time capture) | C5 | - | [Unknown] |

### C. Tally (22 KPI ids, 27 rows counting variants)
- C1 like-for-like both measured: **3** (K-09-OPS count and site split, K-11, K-15). None is an improvement; two are parity with imported legacy state, one is a record that nobody has decided.
- C2 legacy re-measured, unchanged by construction: **16** KPI ids (K-02, K-03, K-05 proxies, K-06, K-08, K-09-OPS age, K-09U, K-10, K-12, K-13, K-14, K-16..K-20; some also appear in C4).
- C3 hub path measured, no before: **K-01, K-07, K-21** (and the hub side of K-03).
- C4 not comparable: hub side of K-02, K-03, K-06, K-09 age, K-09U, K-10, K-20.
- C5 Unknown both sides: **K-04 (all variants), K-05, K-09-EVID, K-09-FIN, K-22** (and K-16/K-19 on the hub side).

### D. Methods and integrity [Verified Fact]
- `python3 -I docs/04-baseline-kpis/evidence/measure_baseline.py data/legacy.sqlite3` on the sandbox copy: rc 0, output `cmp`-identical to `measure_baseline.output.json`; script sha256 `cb062e1b…f60a6` and DB sha256 `c254649f…d70aa` unchanged.
- `python3 -m app.baseline` (sandbox): same six values as `app_baseline_sandbox_output.txt` (records 125, open_cases 89, urgent_cases 2, mean_amount 4982.61, sites 6, hours_per_case 0.603; only comment lines differ).
- Hub runs: `hub.admin migrate`, `hub.policy migrate/seed` (candidates only; nothing adopted), `hub.decision migrate/backfill/verify-projection/verify-chain` (125 cases, 250 events, 0 mismatches), `hub.intake migrate/ingest-legacy/verify-replay/report`, `hub.runs migrate`, `hub.metrics registry/snapshot/values/kpi-coverage/month-end`, `hub.admin verify-audit` (29 records, 22 anchors, status ok). Python 3.10.12, SQLite 3.37.2.
- Working-tree `data/`: `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0 before and after (see measurement-data-quality.md).

### E. Decisions and inputs requested from Dinesh (none is a risk acceptance)
| ID | Request | Default taken meanwhile (OD-32 assumption) |
|---|---|---|
| D-34-01 | Confirm the hub is not in production and no pilot or parallel run with real people has happened (A-34-02, U-34-08) | Not in production; K-21 = 0 |
| D-34-02 | Define the real after-window: start date, exposure (which cases/sites), minimum duration, data owner; supply the production measurements listed in production-performance-report.md PP-1 and adoption-metrics.md AD-2 | None; all production values stay Unknown |
| D-34-03 | Decide whether hub metrics should accept an `as_of` parameter (code change, Stage 30/hardening scope) so ageing can be compared at the frozen 2025-12-19T07:11Z | Ageing declared not comparable |
| D-34-04 | Raise the Stage 4 v0.2 addendum proposed in kpi-comparability-check.md CC-5 (OD-07 follow-up) and sign or amend the Stage 4 freeze | Stage 4 stays FROZEN-PROVISIONAL, untouched |
| D-34-05 | Confirm the artifact path `docs/34-measure-after/` (stage prompt says `docs/34-after-kpis/`) | `docs/34-measure-after/` |
| D-34-06 | Decide whether an override/acceptance KPI should be added (would be a new KPI id in Stage 4 v0.2, not a redefinition) | No override KPI; counts only |
| D-34-07 | Re-run Stage 34 after Stage 30 (cutover/release) and Stage 31 (telemetry) land and a real window exists | This v0.1 is the sandbox edition |
| D-34-08 | Confirm K-11 may be counted by its own "accepted open" wording (2 of 2) | Counted, with the caveat that it records no decision |

### F. Hand-off to Stages 35 and 36 [Verified Fact: scope limit]
- **Stage 35 (variance):** only the three C1 rows have a before and an after; two are parity and one is a record count. Variance and value-leakage analysis has nothing production-based to analyse. It may record "no after-data" and the C4/C5 reasons; it must not compute an improvement.
- **Stage 36 (benefits):** no benefit, saving or ROI can be derived from this stage (OD-04, NG-10). Stage 32 already shows model spend USD 0 by design and all other costs Unknown.

### G. Completion gate: CONDITIONAL PASS [Inference from the checks below]
| Gate condition | Status | Basis |
|---|---|---|
| Definitions identical to Stage 4 | MET | kpi-comparability-check.md CC-1 (dictionary, script, DB, output hashes match; no file outside `docs/34-measure-after/` changed) |
| Comparability check complete | MET | CC-2..CC-6 |
| All required artifacts exist | MET | 7 files in `docs/34-measure-after/` (path differs from the prompt by instruction, A-34-01) |
| Critical gaps resolved or documented | MET (documented) | production after-values, Stage 30/31 inputs, Stage 4 sign-off: each has an owner (Engagement lead (Dinesh Naik)) in section E; due date = before any pilot or production use, no calendar date exists |
| Evidence supports the conclusion | MET for the narrow conclusion "no production after-measurement exists; sandbox parity and unchanged-by-construction shown"; NOT available for any improvement conclusion | sections B-D |
Not PASS because the stage depends on Stage 30/31 production telemetry and none exists; not BLOCKED because the orchestrator scoped this run to sandbox evidence or Unknown, and nothing prevents Stages 35/36 from recording "no after-data". Residual gaps are non-blocking only under that scope.

## Evidence References
`docs/34-measure-after/evidence/` (29 files + SHA256SUMS.txt): `after_measure_baseline.json`, `after_app_baseline.txt`, `hub-01*..hub-16*.json`, `hub-07-month-end-nocutoff.err`, `run_hub_metrics.sh`, `run_hub_intake.sh`. Baseline: `docs/04-baseline-kpis/*`. Test evidence: `docs/26-tevv/tevv-results.md` TR-4, TR-7; `docs/28-reliability/failure-injection-results.md`.

## Assumptions
- A-34-01 [Assumption] Artifact directory is `docs/34-measure-after/` as instructed by the orchestrator, not `docs/34-after-kpis/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-34-02 [Assumption] The hub is not in production (instruction for this stage); "adoption 0" is therefore a repo-state fact plus that instruction, not production telemetry. Confirm: Engagement lead (Dinesh Naik).
- A-34-03 [Assumption] A "sandbox shadow run" over the legacy partner feeds is an acceptable stand-in for a post-intervention window; it measures the hub's behaviour on fixtures, not users. Confirm: Engagement lead (Dinesh Naik).
- A-34-04 [Assumption] Default-answer authority (OD-32) covers the scope choices made here (sandbox measurement only; K-11 counted by its own "accepted open" wording). It does not accept any risk.

## Unknowns
- U-34-01 Every production after-value (no production, no Stage 31 telemetry). Resolution: Dinesh supplies production data, or a pilot window is defined and approved (see human-override-metrics.md and adoption-metrics.md for exact measurements).
- U-34-02 The 5-row difference between K-06 matched rows (173) and hub `linked` (168). Resolution: query the sandbox store for the matched rows with outcome QUARANTINED (not run).
- U-34-03 Legacy replay safety (K-07 before). Resolution: run the legacy partner replay path in a sandbox (Stage 7 characterisation scope).

## Unresolved Issues
- Stage 4 freeze is still FROZEN-PROVISIONAL and unsigned (no sign-off record found in `.fde/orchestrator-decisions.md`); Q-02-04 was answered (OD-09), Q-02-05 is accepted open.
- No Stage 4 v0.2 addendum exists for the OD-07 refutation of A-04-01 (K-10, K-12, K-13 interpretation). Proposed text is in kpi-comparability-check.md; not applied (Stage 4 is frozen).
- Stage 30 and Stage 31 outputs do not exist on `main` (`docs/30*`, `docs/31*` absent on `main`): no cutover, no telemetry, no SLO data.

## Residual Risks
- RR-34-01 A reader quotes "89 = 89" or "unchanged" as a result. Mitigation: classes C1/C2 above; parity is not improvement.
- RR-34-02 Hub-path sandbox figures (K-07, K-09U, K-01) are read as operational. Mitigation: label on every row; K-09U 1.0000 is explained as "no reviewer has acted".
- RR-34-03 Stages 35/36 compute variance or benefit from this sheet. Mitigation: only the three C1 rows have both sides; none supports a benefit.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 34). |
