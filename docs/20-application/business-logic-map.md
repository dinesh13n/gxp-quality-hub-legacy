---
stage: "20 — Application & Services Engineering"
artifact: "business-logic-map.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/golden/observe.py", "hub/golden/probes_s20.json", "hub/coexistence/seed_s20.json", "hub/policy/withdrawal.py", "hub/review/producer.py", "hub/security/zone_h.py", "docs/16-repo-validation/behavior-difference-report.md BD-01..BD-14", "docs/16-repo-validation/evidence/obs-laptop.json", "docs/17-implementation-prd/implementation-prd.md IP-6"]
supersedes: "none"
---
**Label: synthetic data (FX-BASE125, 125 cases, seed 4100, OD-09), unvalidated. No deviation is approved; DV-01..DV-11 are `proposed` (OD-S12-13 accepted open until Stage 30). All business logic is deterministic (OD-08 No-AI).**

## Summary
Stage 20 business logic: (1) golden-compare's new side now comes from the built modules for 9 probes (DW-04); (2) the register states the 11 known behaviour differences (DW-05); (3) policy withdrawal (DW-07); (4) rule traces produced from the rule service (DW-08); (5) one Zone H holder rule (DW-06). Observed values equal the Stage 16 independent observation of the same build.

## Findings
### BL-1 Golden-compare probes (13) and the register (11 proposed rows)
| Golden ref | DV | New-side provider | Observed new value (FX-BASE125) | Legacy value | Class | Tag |
|---|---|---|---|---|---|---|
| CT-07 lib.missing_field | DV-09 | observed intake.missing_envelope_field | quarantined 1, reason MISSING_ENVELOPE_FIELD, received 1 | invalid 1, not stored | D4 | [Verified Fact] |
| CT-08 partner_error_reasons[replayed] | DV-02 | observed intake.partner_replay | NOOP_DUPLICATE 67, REVISED_CONFLICT 0 | 64 | D4 | [Verified Fact] |
| CT-08 partner_error_reasons[quantity] | DV-03 | observed intake.partner_negative_quantity | NEGATIVE_VALUE items 161, flagged_value queue 3 | 154 rejected | D4 | [Verified Fact] |
| CT-08 partner_status_after_all | DV-07 (+07a text) | observed intake.partner_outcomes | legacy table untouched; append-only; EXCEPTION 8,109, NOOP_DUPLICATE 67, QUARANTINED 223, VALIDATED 165, VALIDATED_WITH_FLAGS 3 | ACCEPTED 7917 / DUPLICATE 64 / REJECTED 586 | D4 | [Verified Fact] |
| CT-08 partner_status_after_all[ref_id match] | DV-10 (new) | observed intake.partner_ref_match | linked 168, UNMATCHED_REF 7,903, NO_BUSINESS_KEY 206 | as above | D4 | [Verified Fact] |
| CT-10 shift_active_policies_per_region | — | baseline_ro | identical | — | D0 | [Verified Fact] |
| CT-10 shift_distinct_objects_in_first_500 | DV-08 | baseline_ro (reference query; not a built job) | 500 | 118 | D4 (weak, BD-08) | [Verified Fact] |
| CT-11 java_tiny.stdout#count | DV-04 | observed intake.vendor_tiny | UNPARSABLE_AMOUNT 10, kept rows 2,390 | "2390" | D4 | [Verified Fact] |
| CT-12 sql_report_1_total_gross | DV-01 | baseline_ro | 622,826.44 | 742,956.61 | D4 | [Verified Fact] |
| CT-12 true_total_amount | — | baseline_ro | identical | — | D0 | [Verified Fact] |
| CT-13 js_policy_table.allows[7:9] | DV-05 | observed policy.js_invalid_amount | both E-POL-INPUT-INVALID | false / true | D4 | [Verified Fact] |
| CT-13 js_policy_table.table[0] | DV-06 | observed policy.js_unknown_year | 999999, defaulted true | 999999 | D4 (additive) | [Verified Fact] |
| DEV-29 js.threshold(APAC, partial year) | DV-11 (new) | observed policy.js_partial_year; legacy from register (no golden) | '202','2','' -> 999999 defaulted | 15000 each (INC-04 S05 live node run) | D4 | [Verified Fact] |
Golden-compare with the record: 13 probes, 2 identical, 11 UNAPPROVED, 0 NOT-RUN, exit 6 (G1 red by design while OD-S12-13 is open). D5 = 0. [Verified Fact] `evidence/golden-compare-observed.json`.

- [Verified Fact] Equality with Stage 16 `s16_observe.py` (obs-laptop.json) is asserted field by field by STG20 S04 (DW-04 acceptance).
- [Verified Fact] FAC-05 power: mutant G1S20 (intake stops flagging negative quantities) is KILLED by TST-CO-01 b/c/d and STG20 S04 (`evidence/mutation-gate.json`) - a built-module regression is now visible to the gate tests.
- [Inference] DV-01 and DV-08 still use baseline reference queries, not the built metric / batch modules; DV-01's value equals the INC-07 metric service (BD-01) but is not read from it - residual S20-D02.

### BL-2 Withdrawal rules (DW-07)
Zone H ZH-10; authority_ref and reason required; only adopted versions; once per version; withdrawn_from >= effective_from; stops: clock verdicts, closure-set use, consistency rules in runs, overlap window; metric values carry `detail.policy_withdrawal`. [Verified Fact] STG20 S11-S13.

### BL-3 Trace producer (DW-08)
Active set (authoritative) or named set (what-if); inputs = declared fields of the function from the read-only case snapshot; refusal (E-POL-INPUT-INVALID) is counted, not stored; idempotent. Over the 125 shipped cases with PRIORITY / as-found-python@1: 125 stored, 0 refused; second run 0 stored / 125 unchanged. [Verified Fact] STG20 S14.

### BL-4 Zone H holder rule (DW-06)
human (+ dispositioner where required, integration rejected at the gate service) -> holders non-empty -> principal listed -> re-auth within window; first failing condition named; error classes per caller unchanged. Mutant H1S20 KILLED by TST-GATE-21. [Verified Fact]

## Evidence References
`evidence/golden-observation.json`, `golden-compare-observed.json`, `golden-compare-no-observation.json`, `register-dump.json`, `mutation-gate.json`; tests STG20 S04-S08, S11-S15, S20-S21.

## Assumptions
- A-20-BL-1 [Assumption] The register `new_value` for DV-02/03/04/07 may be restated in the observed shape (registration text, not behaviour); confirm with DQ-13 at Stage 30: Engagement lead (Dinesh Naik).

## Unknowns
- U-20-BL-1 DV-02 "changed-content replay -> REVISED_CONFLICT" is not exercised by FX-BASE125 (0 such rows); covered only by synthetic TST-INT-01..08.

## Unresolved Issues
- DV-01..DV-11 preserve-or-fix (DQ-13, Stage 30). DV-08 / DV-01 observed via reference queries (S20-D02).

## Residual Risks
- RR-BL-1 A custom `--probes` file can still declare values (provider kept for synthetic tests TST-CO-02); the shipped catalogue has none and S03 guards it (Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
