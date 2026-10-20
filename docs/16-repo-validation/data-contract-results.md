---
stage: "16 — Validate the Good Repo"
artifact: "data-contract-results.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/16-repo-validation/evidence/contracts-cloud.json (s16_contracts.py, jsonschema draft-07)", "docs/16-repo-validation/evidence/obs-laptop.json, obs-cloud.json (intake runs, contract_check counts)", "docs/12-specs/contracts/schemas/*.schema.json (16 schemas)", "docs/12-specs/contracts/openapi.yaml (48 operations)", "integration/source-contract-v1.json", "hub/intake/contracts/source-contract-v1.json", "hub/intake/migrations/M004_intake.sql (addendum columns)", "hub/security/route_registry.json", "tests/hub/test_tst_sec_01_route_registry.py, test_inc06_supplementary.py S03, test_tst_int_09_16_validation.py (green)", "docs/15-modernization/evidence/inc06/shipped-source-profile.md"]
supersedes: "none"
---
**Label: synthetic data, unvalidated - method validation only.**

## Summary
Three kinds of data contract were checked: (1) the **declared source contract** `source-contract-v1` applied to every shipped source in shadow intake; (2) the **Stage 12 JSON schemas** against the objects the built hub actually wrote on FX-BASE125 (a new Stage 16 check: 22,427 stored objects + 3 service outputs validated); (3) the **API contract** (OpenAPI route registry). The hub conforms to 8 of 10 schemas exercised outright; the other 2 (intake-outcome, metric-value) fail only because of **documented additive fields** the schemas forbid (`additionalProperties: false`), and validate fully once those fields are set aside. The source contract fails for 3 of 4 shipped sources, which is a property of the synthetic legacy data recorded (not enforced) by design.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DC-1 Source contract `source-contract-v1` (binding `record_only`, the shipped default, OD-S12-11)
| Source | Items | Contract pass | Contract fail | Outcome effect (record_only) | Tag |
|---|---|---|---|---|---|
| partner_feed | 8,567 | 0 | 8,567 | recorded on the outcome (`contract_missing`), no quarantine; enforce mode would quarantine 8,500 + 67 NOOP (TST-INT-13) | [Verified Fact] |
| source_message | 15 | 15 | 0 | — | [Verified Fact] |
| gateway | 1 | 0 | 1 | VALIDATED (record_only); enforce -> quarantine (TST-INT-14) | [Verified Fact] |
| vendor_csv (tiny tier) | 2,400 | 0 | 2,400 | VALIDATED_WITH_FLAGS / QUARANTINED by value rules; IDENTIFIER_PATTERN on all 2,400 | [Verified Fact] |
[Verified Fact] Identical on 3.10.12 and 3.13 (per-source `outcomes_digest` equal: partner `4a50d715…`, message `1aa6d987…`, gateway `221e9a83…`, vendor `99be82fa…`); equal to the INC-06 shipped-source profile. The bundled contract is byte-identical to `integration/source-contract-v1.json` (INC06 S03 green).
[Inference] Switching any source to `enforce` would quarantine almost the whole shipped partner feed; that is a data-quality fact about the synthetic source, and the switch needs a Zone H holder (none configured, RTD-57).

### DC-2 Stage 12 JSON schemas vs objects written by the built hub (new in Stage 16)
| Schema | Objects | Valid | Invalid | Cause of invalid | Tag |
|---|---|---|---|---|---|
| audit-record | 30 | 30 | 0 | — | [Verified Fact] |
| crosswalk-link | 168 | 168 | 0 | — | [Verified Fact] |
| decision-event | 250 | 250 | 0 | (SQLite 0/1 mapped to boolean) | [Verified Fact] |
| raw-intake | 10,983 | 10,983 | 0 | (`raw_bytes` mapped to `raw_bytes_b64`) | [Verified Fact] |
| metric-definition | 5 | 5 | 0 | — | [Verified Fact] |
| policy-object | 5 | 5 | 0 | — | [Verified Fact] |
| rule-set (+ rows) | 3 | 3 | 0 | — | [Verified Fact] |
| rule-result (`hub.policy evaluate`) | 2 | 2 | 0 | — | [Verified Fact] |
| intake-outcome | 10,983 | 0 | 10,983 | extra fields `contract_missing`, `conflicts_with`, `reason_detail` (M004 addendum columns, documented in `M004_intake.sql` header); with them set aside: **10,983 / 10,983 valid** | [Verified Fact] |
| metric-value (`hub.metrics month-end`) | 1 | 0 | 1 | extra field `detail` (currency minor unit, rounding note, source); without it: valid | [Verified Fact] |
| not exercised | — | — | — | evidence-record (0 rows: no evidence attached on the shipped data), run-record (no run executed in the observation), error-envelope (HTTP layer covered by I8 tests; CLI envelope differs, SS-07), hub-config, partner-feed-envelope/payload (legacy input side) | [Verified Fact] |

### DC-3 API contract
[Verified Fact] `hub/security/route_registry.json` holds 48 routes generated from `docs/12-specs/contracts/openapi.yaml` (48 `operationId`s); TST-SEC-01 (registry drift and deny-by-default) passes; I8 HTTP tests exercise the routes; five R2 operations answer in `R2WebApp` and 501 in the R1 `WebApp` (DEV-82, by design); OP-MET-05 answers `E-MET-NOT-AVAILABLE`.
[Inference] Several request/response details are hub additions not in the DRAFT OpenAPI (e.g. `reason` query parameter for C3 reads DEV-94, login body fields DEV-84, `view=freshness` DEV-98); they need the Stage 12 addenda already listed (RTD-66, RTD-78).

### DC-4 Findings register
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| DC-01 | Built objects conform to 8 Stage 12 schemas exactly | DC-2 | contracts usable as acceptance tests | Low | High | — |
| DC-02 | intake-outcome and metric-value schemas lag the code (additive fields forbidden by `additionalProperties: false`) | DC-2 | a consumer validating against the DRAFT schemas would reject every hub object of these two types | Medium | High | Stage 17 addendum: add the fields to the schemas (RTD-54/55/58 family) |
| DC-03 | 12 of the 16 Stage 12 JSON schemas are not referenced by any hub test (only audit-record, hub-config, rule-set and run-record are) | grep of schema names in `tests/hub` | schema drift (DC-02) went unnoticed through Stage 15 | Medium | High | adopt `s16_contracts.py` (or a stdlib equivalent) as a contract test (Stage 23) |
| DC-04 | Source contract fails for 3 of 4 shipped sources; enforce would quarantine ~99% of the partner feed | DC-1 | enforce mode is not usable on this data without a contract revision | Medium | High | OD-S12-11 per source; contract owner Unknown |
| DC-05 | evidence-record and run-record objects were not produced in the observation, so their schema conformance rests on the unit tests only | DC-2 | small gap | Low | High | include a run and an evidence attach in a later observation |

## Evidence References
- `python3 -B docs/16-repo-validation/evidence/s16_contracts.py --store <sbx>/work/data/hub.sqlite3 --obs <obs json> --out <json>` (needs `jsonschema`, evaluation tooling only; run in the cloud workspace on the observation store, read-only).

## Assumptions
- A-16-DC-1 [Assumption] Mapping SQLite storage forms to schema forms (0/1 -> boolean; JSON text -> object; BLOB -> base64) is the intended serialisation; the schemas describe the logical object. Confirm: Stage 17 addendum author.

## Unknowns
- U-16-DC-1 Owner of `source-contract-v1` and whether the shipped data or the contract is wrong (DC-04) - Engagement lead (Dinesh Naik).

## Unresolved Issues
- DC-02 schema addenda; DC-03 contract tests; DC-04 contract vs data.

## Residual Risks
- RR-DC-1 Schema drift continues while schemas are not executed as tests (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
