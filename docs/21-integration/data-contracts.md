---
stage: "21 — Enterprise Integration"
artifact: "data-contracts.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/21-integration/evidence/contract-pack.json (STG21 S01)", "docs/21-integration/evidence/gateway-stub-conformance.json (STG21 S02)", "integration/source-contract-v1.json", "hub/intake/contracts/source-contract-v1.json", "hub/intake/contracts.py, validate.py, profiles.py, service.py", "docs/12-specs/contracts/schemas/partner-feed-payload.schema.json", "docs/16-repo-validation/data-contract-results.md (DC-1, DC-04)", "docs/16-repo-validation/evidence/obs-laptop.json", "docs/11-data-context/data-contracts.md", "docs/12-specs/spec-readiness.md OD-S12-11 / RF-2", "tests/hub/test_tst_int_09_16_validation.py (TST-INT-12/13/14 re-run green)"]
supersedes: "none"
---
**Label: synthetic data, unvalidated - decision support only. No binding was changed: every source stays `record_only` (OD-10d / OD-S12-11 default); `zone_h.holders` stays empty, so nobody can switch a source to `enforce`.**

## Summary
**DW-10 source-contract evidence pack.** `source-contract-v1` (required `ref`, `status`, `schema_version`, all strings; bundled copy byte-identical to `integration/`) was evaluated over the four shipped sources through the hub's own parse and check, and through a record_only ingest of each source into a sandbox store. Results reproduce Stage 16 exactly (per-source outcome digests equal `obs-laptop.json`): **partner_feed 0 / 8,567 pass, source_message 15 / 15, gateway inbox 0 / 1, vendor_csv 0 / 2,400**; the repo's live gateway stub events are **0 / 125**. The failing-field analysis shows the contract is the **shape of `source_messages` bodies** (`{"ref","status","schema_version"}`) and nothing else: no partner-feed row has any of the three keys (it carries `state`, `source_version`, `business_key`), the vendor CSV lacks only `ref` (it has `reference_id`, `status`, `schema_version`), gateway events lack `ref` and `status`. Every one of the 8,567 partner rows conforms to the Stage 12 `partner-feed-payload` schema. [Inference] The DC-04 gap is a **contract-scope mismatch, not bad data**: applying a message contract to other source shapes fails by construction.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DC-S21-1 Per-source result (record_only, FX-BASE125, legacy.sqlite3 c254649f…; vendor CSV tiny)
| Source | Items | Pass | Fail | Failing fields (absent / wrong type) | Payload keys present (count) | Tag |
|---|---|---|---|---|---|---|
| partner_feed | 8,567 | 0 | 8,567 | `ref` 8,567 / 0; `status` 8,567 / 0; `schema_version` 8,567 / 0 | `state`, `source_version`, `object_type`, `currency`, `notes`, `policy_version`, `quality_flag`, `quantity`, `subtype`, `unit` 8,567; `business_key` 8,357 | [Verified Fact] |
| source_message | 15 | 15 | 0 | — | `ref`, `status`, `schema_version` 15 | [Verified Fact] |
| gateway (legacy inbox) | 1 | 0 | 1 | `ref`, `status`, `schema_version` absent | `business_key`, `event_type`, `message_id`, `occurred_at`, `system` | [Verified Fact] |
| vendor_csv (tiny) | 2,400 | 0 | 2,400 | `ref` 2,400 / 0 only | 11 header columns incl. `reference_id`, `status`, `schema_version` (2,400 each) | [Verified Fact] |
| gateway (live stub events, S02) | 125 | 0 | 125 | `ref`, `status` (signature `ref,status` 125) | 8 event keys incl. `schema_version`; status only nested as `payload.source_status` | [Verified Fact] |

### DC-S21-2 What `enforce` would do (computed from the record_only store; no binding changed)
| Source | Contract-fail items by current outcome | Newly quarantined under enforce | Already quarantined | NOOP_DUPLICATE (unchanged) | Tag |
|---|---|---|---|---|---|
| partner_feed | EXCEPTION 8,109; QUARANTINED 223; VALIDATED 165; VALIDATED_WITH_FLAGS 3; NOOP_DUPLICATE 67 | 8,277 | 223 | 67 | [Verified Fact] (= TST-INT-13: 8,500 + 67 NOOP) |
| source_message | none fail | 0 | 0 | 0 | [Verified Fact] (= TST-INT-14) |
| gateway inbox | VALIDATED 1 | 1 | 0 | 0 | [Verified Fact] |
| vendor_csv | VALIDATED_WITH_FLAGS 2,390; QUARANTINED 10 | 2,390 | 10 | 0 | [Verified Fact] |
| gateway stub events | VALIDATED 125 (first pull) | 125 | 0 | 0 | [Verified Fact] S02 |

### DC-S21-3 Contract-vs-data analysis (U-17-IP-2 / U-16-DC-1: "contract or data wrong?")
| Source | Semantic analogue of `ref` | of `status` | of `schema_version` | Reading | Tag |
|---|---|---|---|---|---|
| partner_feed | envelope `ref_id`; payload `business_key` (8,357 of 8,567) | payload `state` (legacy-truth risk: stored only as `source_state`, BEH-INT-01) | envelope `schema_rev`; payload `source_version` | different shape, governed by the Stage 12 envelope + payload schemas and the L1/L2 rules (DC-01/02) | [Inference] |
| source_message | `ref` | `status` | `schema_version` | exact match - the contract was written for this source (app/integration.py reads it, IL-09) | [Inference] from IN-02 / IL-09 |
| gateway | `business_key` | `payload.source_status` (nested) | `schema_version` (stub) / absent (inbox row) | different shape | [Inference] |
| vendor_csv | `reference_id` | `status` | `schema_version` | one rename away from the contract | [Inference] |
- [Verified Fact] 8,567 / 8,567 partner payloads pass the Stage 12 `partner-feed-payload` schema (required `object_type`, `state`, `source_version`; types and enums) - stdlib subset check in `tests/hub/_stg21.py` (evaluation tooling, not a hub binding).
- [Inference] Neither the contract nor the data is "wrong": the declared contract has **no per-source scope**, and the hub profile binds the same file to all four sources (`hub/intake/profiles.py` `contract: "source-contract-v1"`). Which party owns that scope is the open question (contract owner Unknown).

### DC-S21-4 Options for OD-S12-11 (decision support; owner Engagement lead (Dinesh Naik))
| Option | What changes | Effect on shipped data | Needs | Risk | Recommendation |
|---|---|---|---|---|---|
| O1 Keep `record_only` everywhere (status quo) | nothing | 0 items affected; contract result stays visible on every outcome (`contract_check`, `contract_missing`) | nothing | contract never protects anything | acceptable default ("accepted open" is legitimate) |
| O2 `enforce` for source_message only | one Zone H ZH-10 binding change | 0 / 15 quarantined | a named Zone H holder (none today, RTD-57) + authority_ref | Low | **recommended first step** once a holder exists |
| O3 Per-source contracts v2: partner_feed -> Stage 12 envelope + payload schemas; vendor_csv -> v1 with `reference_id`; gateway -> event schema | new contract files + profile entries (a Stage 23 build item, DW-13 family) | partner 8,567 / 8,567 would pass the payload schema; vendor would pass after the rename | spec owner sign-off; new tests | Medium (spec work) | recommended before any enforce on non-message sources |
| O4 `enforce` source-contract-v1 on partner / vendor / gateway | Zone H binding change | quarantines 8,277 + 2,390 + 1 more items (DC-S21-2) | holder | High: blocks ~99% of the feed for a scope error | **not recommended** |

### DC-S21-5 Read-only database contracts (AD-01 / AD-02)
[Verified Fact] Legacy SQLite sources are opened only as hash-pinned snapshots (`baseline_pins.json`: sha256 + schema), `mode=ro&immutable=1`, with an authorizer refusing every write; drift or a hash mismatch fails closed (TST-CO-04 a-f, green in Stage 21); the FX-BASE125 copy is byte-identical after the full Stage 21 run (STG21 S06).

## Evidence References
- `docs/21-integration/evidence/contract-pack.json` - reproduce: `python3 -B tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s21-pack --label pack -k TST_HUB_STG21_S01` (writes `<sandbox>/pack/scratch/s21-evidence/contract-pack.json`; the test fails if it differs from the committed file).
- TST-INT-09..16 re-run green on the laptop (`evidence/test-runs-laptop.json`).

## Assumptions
- A-21-DC-1 [Assumption] `source-contract-v1` was meant for `source_messages` only (inferred from the exact key match and from `app/integration.py`); confirm: Engagement lead (Dinesh Naik) as contract owner proxy.
- A-21-DC-2 [Assumption] The Stage 12 partner-feed schemas (DRAFT) are the intended partner contract; confirm at Stage 23 (DW-13, Stage 12 v0.2).

## Unknowns
- U-21-DC-1 Owner of `source-contract-v1` (U-17-IP-2 / U-16-DC-1) - Engagement lead (Dinesh Naik).
- U-21-DC-2 Contract for real partner feeds (none exist).

## Unresolved Issues
- OD-S12-11 per-source binding (DQ-S21-01); Stage 12 schema lag for intake-outcome / metric-value (Stage 16 DC-02, Stage 23).

## Residual Risks
- RR-21-DC-1 While every source is record_only, a malformed upstream contract change is visible on outcomes but blocks nothing (Medium, accepted by the default).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue (DW-10 pack). |
