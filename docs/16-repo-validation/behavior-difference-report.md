---
stage: "16 — Validate the Good Repo"
artifact: "behavior-difference-report.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/07-repo-assessment/evidence/golden/{api,batch,lib}_golden_run1.json (Stage 7 frozen baseline)", "docs/14-transformation/transformation-gates.md TG-4 (classes D0-D5)", "hub/coexistence/seed_inc02.json (DV-01..DV-09, all proposed)", "hub/golden/probes_inc02.json", "docs/16-repo-validation/evidence/obs-laptop.json, obs-cloud.json (s16_observe.py)", "docs/16-repo-validation/evidence/char-run2_report.json, char-mut{1..4}_report.json (laptop, Python 3.10.12)", "docs/16-repo-validation/evidence/char-cloud-py313_report.json (environment A/B)", "docs/16-repo-validation/evidence/boundary-cloud.json (s16_boundary.py)", "docs/15-modernization/transformation-log.md (DEV-01..DEV-107)", "docs/14-transformation/cutover-plan.md (CUT-1..CUT-5)", "app/partner_feeds.py (reconcile precedence)", ".fde/orchestrator-decisions.md (OD-09, OD-22, OD-23)"]
supersedes: "none"
---
**Label: synthetic repository; every number below comes from synthetic data (FX-BASE125, 125 cases, seed 4100, OD-09) and is unvalidated - method validation only. No deviation is approved; nothing here is an approval.**

## Summary
Stage 16 ran the TG-4 behaviour-comparison protocol at `main` 2c63b07 and went one step further than the built `golden-compare`: it **observed the built hub modules** (INC-04..INC-09) on the FX-BASE125 sandbox copy for every DV golden reference, instead of relying on the INC-02 *declared* target values (DEV-08 / RTD-15, still open in the code).

Result: **D5 (unexplained) = 0.** Every difference found is listed below with cause, class and the cutover step it blocks.

| Class (TG-4) | Count | Items |
|---|---|---|
| D0 IDENTICAL | 132 legacy CT checks + 2 golden-compare identity probes + 105 boundary cases + rule-set parity (TST-CO-03) | BD-00, BD-12, BD-13 |
| D1 NORMALISED | 2 legacy CT checks (CT-H3 path / tail rules, unchanged since INC-01) | BD-00 |
| D2 KNOWN-NON-REPRODUCIBLE | 0 beyond the Stage 7 list (CT-14 regeneration handled by normalisation) | — |
| D3 APPROVED-DEVIATION | **0** (no DV row is approved; OD-S12-13 open) | — |
| D4 PROPOSED-DEVIATION (hub shadow only) | **9 registered** (DV-01..DV-09) **+ 2 unregistered but explained** (DEV-29 partial-year match, intake outcome classification under DV-07) | BD-01..BD-11 |
| D5 UNEXPLAINED | **0** | — |
| Environment (not a product difference) | Python 3.13 / SQLite 3.45 cloud run: 10 of 16 CTs differ; reproduced A/B against the 3.10.12 reference run | ENV-1..ENV-6 |
| Net-new behaviour (no legacy counterpart) | hub HTTP surface, decision record, audit, R2 search / reports | BD-14 |

Legacy behaviour is unchanged: 134/134 CT checks on the reference runtime in 6 runs, capture digests byte-identical to INC-01 (`api c6db0a43…`, `batch 40237661…`, `lib c5797c3b…`, `supplement c3cbab2c…`), mutation gate 15/15, all 688 changes since `baseline-as-found` are additions.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### Behaviour-difference register
Columns follow TG-4 "explained": scenario + golden path; legacy value; new value (declared in the register, and **observed** from the built module in Stage 16); class; cause; DV / test; approval_ref; CUT step blocked; reproduce. Evidence file hashes are in `evidence/SHA256SUMS.txt`.

| diff_id | Scenario / golden ref | Legacy value (golden) | New value observed at 2c63b07 | Class | Cause | DV / tests | approval_ref | Blocks |
|---|---|---|---|---|---|---|---|---|
| BD-00 | CT-01..CT-16 legacy capture (api/batch/lib/supplement) | Stage 7 goldens | 134/134 equal (132 D0, 2 D1), digests = INC-01 | D0/D1 | legacy code byte-identical since `baseline-as-found` | CT-01..16, M1..M15 | n/a | — |
| BD-01 | CT-12 `batch.sql_report_1_total_gross` | 742956.61 | 622826.44 (MET-MONTH-END-TOTAL, n=125, `hub.metrics month-end`; same in golden-compare `baseline_ro`) | D4 | BB-08: `sql/legacy_reports.sql` LEFT JOIN events fans out; hub sums `cases.amount` once (INC-07) | DV-01; TST-MET-09, TST-CO-01 | none | CUT-4 |
| BD-02 | CT-08 `partner_error_reasons[replayed source message]` | 64 DUPLICATE | 67 NOOP_DUPLICATE, 0 REVISED_CONFLICT | D4 | BB-05 fix (INC-06). 64 vs 67 reconciled: the feed has 67 REPLAY rows; legacy `reconcile()` checks key/schema first, so 3 REPLAY rows without key or with `schema_rev='unsupported'` become REJECTED (`app/partner_feeds.py:66-68`) | DV-02; TST-INT-01..08 | none | CUT-3 |
| BD-03 | CT-08 `partner_error_reasons[quantity out of range]` | 154 REJECTED | 161 partner items carry NEGATIVE_VALUE, kept (3 VALIDATED_WITH_FLAGS in queue `flagged_value`; 158 also carry a higher-precedence reason: UNMATCHED_REF 151, NO_BUSINESS_KEY 4, UNSUPPORTED_REVISION 3) | D4 | change of class (reject -> flag). Reconciliation: 163 rows have quantity < 0; legacy rejects only the 154 non-REPLAY rows with a valid key and revision; hub flags all except the 2 REPLAY rows, which are NOOP_DUPLICATE before validation (DEV-54): 163 - 2 = 161 | DV-03; DEV-58; TST-INT-09..16 | none | CUT-3 |
| BD-04 | CT-11 `batch.java_tiny.stdout#count` | "2390" (10 blank amounts skipped silently) | vendor tiny CSV: 2,390 VALIDATED_WITH_FLAGS + 10 QUARANTINED `UNPARSABLE_AMOUNT` | D4 | BB fix: silent drop -> quarantine (INC-06) | DV-04; TST-INT-27 | none | CUT-4 |
| BD-05 | CT-13 `js_policy_table.allows[7:9]` | 'abc' -> false; null -> true (JS coercion) | both refused `E-POL-INPUT-INVALID` (exit 23), no outcome | D4 | BEH-POL-11 specified default (INC-04); no "preserve" mode built (DEV-30) | DV-05; TST-POL-23 | none | CUT-2 |
| BD-06 | CT-13 `js_policy_table.table[0]` | ["APAC",2019,999999] | threshold 999999, `defaulted: true`, `NO_MATCH_REGION_YEAR`, allowed true | D4 (additive) | DV-06 marker (INC-04) | DV-06; TST-POL-11..21 | none | CUT-2 |
| BD-07 | CT-08 `partner_status_after_all` | ACCEPTED 7917 / DUPLICATE 64 / REJECTED 586 (legacy table overwritten) | legacy table untouched (sha256 `c254649f…` before = after; status NEW 8000 / REPLAY 67 / RETRY 500); append-only outcomes: EXCEPTION 8,109 (UNMATCHED_REF 7,903, NO_BUSINESS_KEY 206), QUARANTINED 223 (UNSUPPORTED_REVISION), VALIDATED 165, VALIDATED_WITH_FLAGS 3, NOOP_DUPLICATE 67 | D4 + **register under-specified** | DV-07 covers "untouched / append-only" and is met. The outcome **classification** also differs: the hub links `ref_id` to the 125 baseline cases by exact key (BEH-INT-08, AC-INT-18), legacy never checks `ref_id`, so most legacy ACCEPTED rows are hub EXCEPTION/UNMATCHED_REF. This is specified behaviour (PRD baseline OD-22) but no DV row states it | DV-07 (+ proposed DV-10); TST-INT-17..29; DEV-54 | none | CUT-3 |
| BD-08 | CT-10 `shift_distinct_objects_in_first_500_joined_rows` | 118 | 500 | D4 (weak evidence) | DV-08 target. The new value is a reference query over the RO snapshot (`hub/golden/baseline_probes.py`), not a built batch job; the built SHIFT_FLAG function evaluates one entity per call, so fan-out cannot occur by construction | DV-08; TST-CO-03 b | none | CUT-4 |
| BD-09 | CT-07 `lib.missing_field` | {accepted 0, duplicates 0, invalid 1, received 1}; event not stored | built intake: QUARANTINED, reason `MISSING_ENVELOPE_FIELD`, stored (`test_inc06_supplementary.py` S-tests, AC-INT-10) | D4 + **register text drift** | DV-09 fix. The seed's new value says reason `envelope_invalid`; the built module uses the Stage 12 code `MISSING_ENVELOPE_FIELD` (schema-specifications.md, SBR-INT-03). Same behaviour, stale label | DV-09; TST-INT-09..16 | none | CUT-3 |
| BD-10 | JS threshold for partial years (no golden; INC-04 S05 live node run) | `threshold('APAC', 202)` / `2` / `''` -> 15000 (`startsWith` prefix match) | 999999, `defaulted: true` (observed `APAC_202_partial`) | D4-equivalent, **unregistered** | 4-digit year required (INC-04) | DEV-29; RTD-41 | none | CUT-2 |
| BD-11 | Amount-limit boundary x1.05, 15 limits x 7 offsets (0, ±0.01, ±1e-6, ±1e-10) | node `legacyAllows` (IEEE double) | 105/105 identical (exact Decimal engine) | D0 | — (partially closes RTD-42) | s16_boundary.py | n/a | — |
| BD-12 | Rule divergence over the 125 cases (INC-09 report) | legacy python vs JS rules disagree | 3 of 125 cases (C00000059, C00000077, C00000080: JS true, Python false; batch set null for all 125, no policy_code) | D0 (hub reproduces a legacy inconsistency; it does not create one) | three as-found rule sets loaded inactive (OD-16); divergence reported, not resolved (RC-3/RC-4) | TST-CO-03 a-c (3/3 green), DEV-97 | n/a | CUT-2 decision |
| BD-13 | golden-compare identity probes CT-10 `shift_active_policies_per_region`, CT-12 `true_total_amount` | as golden | identical | D0 | — | TST-CO-01 | n/a | — |
| BD-14 | Hub surfaces without a legacy counterpart: `/api/v2` loopback HTTP + pages, decision record, audit chain, R2 search / reports / drafts | none (legacy API CT-04/CT-16 unchanged) | new, shadow, flags off by default | net-new | ADR-003 (no dual write), PRD baseline OD-22 | TST-* (241 planned) | OD-22 (scope only) | CUT-1, CUT-5 |

### Golden-compare as built
- [Verified Fact] `python -m hub golden-compare` at 2c63b07 (laptop 3.10.12 and cloud 3.13 give the same report hash): probes 11, identical 2, approved 0, UNAPPROVED 9, NOT-RUN 0, **exit 6** - the specified AC-CO-01 behaviour while no DV is approved (gate G1 red by design).
- [Verified Fact] 7 of 11 probes still use the INC-02 **declared** value (`new_source: "declared:F10-2 DV-0x (target; owning module not built yet)"`) although the owning modules are now built. Stage 16 closed the evidence gap by observation (table above), not by changing code.
- [Inference] Because the comparison tool still compares declared values, a future regression in an intake / policy module would not turn golden-compare red; only the module tests would catch it. Recommend replacing declared probes with module observations (debt S16-D01).

### Environment A/B (legacy capture on a different runtime)
The same commit run on the cloud workspace (Python 3.13.16, SQLite 3.45.1, OD-23 says it is not authoritative) gives OVERALL FAIL, 124/134 checks; on the reference laptop (3.10.12, SQLite 3.37.2) 134/134. Legacy code is identical in both, so every difference is environmental:
| ID | CT | Difference | Cause | Tag |
|---|---|---|---|---|
| ENV-1 | CT-03, CT-15 | `$.python` "3.10.12" vs "3.13.16" | interpreter version echoed in output | [Verified Fact] |
| ENV-2 | CT-07 | traceback file/line in stderr tail | stdlib `urllib/request.py` differs per version | [Verified Fact] |
| ENV-3 | CT-11 | extra JVM stderr line | cloud JAVA_TOOL_OPTIONS proxy agent | [Verified Fact] |
| ENV-4 | CT-12 | SQLite `sum()` 64067.70999999998 vs 64067.71 | SQLite 3.43+ changed floating-point summation (compensated sum) | [Inference] (SQLite release history; not re-verified here) |
| ENV-5 | CT-13, CT-14 | absolute sandbox paths not normalised | CT-H3 rule N1 expects `~/fde_sbx/...` paths; cloud sandbox is `/home/claude/sbx/...` | [Verified Fact] |
| ENV-6 | CT-16 | http.server error page HTML | Python 3.13 changed the default error page | [Verified Fact] |
[Inference] ENV-4 and ENV-6 are real legacy output changes that a runtime upgrade (3.10 -> 3.12, SQLite upgrade) would cause; they matter for OD-S12-12 and for any cutover comparison on a new runtime. Per TG-4 they are not "explained by assertion": the A/B run is recorded here, but a reviewed CT-H3 normalisation change or a re-baselined golden (reviewed `--update-golden`) is still needed before any non-3.10 environment can be the comparison baseline.

## Evidence References
- Reproduce (from the repository root, sandbox only):
  - `python3 -B tests/characterization/run_characterization.py --sandbox-root ~/fde_sbx/<x>` (then delete the sandbox)
  - `python3 -B docs/16-repo-validation/evidence/s16_observe.py --sandbox-root ~/fde_sbx/<x> --out <file>`
  - `python3 -B docs/16-repo-validation/evidence/s16_boundary.py --store <sbx>/work/data/hub.sqlite3 --out <file>` (cwd = `<sbx>/c_pristine`; s16_observe.py leaves `<sbx>` in place, delete it after this step)
- Legacy precedence: `app/partner_feeds.py` lines 66-68. Counts from the FX-BASE125 sandbox copy: REPLAY 67 (3 with no key / unsupported revision), quantity < 0: 163 (154 non-REPLAY with valid key and revision; 2 REPLAY).
- Observations: `evidence/obs-laptop.json` (3.10.12) and `evidence/obs-cloud.json` (3.13.16) - identical section hashes for golden_compare, policy_evaluate, intake outcomes, divergence, month_end; per-source `outcomes_digest` identical (only run ids differ).

## Assumptions
- A-16-BD-1 [Assumption] The INC-06 supplementary tests that feed a gateway event with missing envelope fields are an adequate stand-in for the CT-07 `lib.missing_field` scenario on the new side (no hub path replays the exact legacy library call). Confirm: Engagement lead (Dinesh Naik) at the DV-09 decision.

## Unknowns
- U-16-BD-1 Whether DV-08's "per entity, no fan-out" holds for a future batch night-shift job: no such job is built; resolve when CUT-4 scope is fixed (Stage 17/30).
- U-16-BD-2 Behaviour of the legacy estate on the eventual target runtime (3.12 / newer SQLite): ENV-4 and ENV-6 show it changes; resolve with OD-S12-12 and a reviewed re-baseline (Stage 27).

## Unresolved Issues
- DV-01..DV-09 preserve-or-fix (OD-S12-13) - owner Dinesh Naik, due before the related CUT step (Stage 30).
- Register maintenance: DV-07 new value under-specified (BD-07), DV-09 label stale (BD-09), DEV-29 has no DV row (BD-10) - proposed as a Stage 17 addendum (S16-D02).

## Residual Risks
- RR-BD-1 Golden-compare stays green-by-declaration for 7 probes until debt S16-D01 is done (Medium).
- RR-BD-2 Runtime upgrade changes legacy outputs (ENV-4/6); comparisons on another runtime will need a reviewed baseline (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue (Stage 16 at main 2c63b07). |
