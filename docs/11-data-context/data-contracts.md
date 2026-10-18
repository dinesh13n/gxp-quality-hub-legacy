---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "data-contracts.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["integration/source-contract-v1.json", "integration/source-gateway.json", "data/legacy.sqlite3 partner_feeds, gateway_inbox, vendor_file_rows (read-only)", "data/documents/source_documents.jsonl", "docs/data-dictionary.md", "docs/09-initial-prd/functional-requirements.md FR-INT-01..08, FR-DEC-01..06, FR-ID-01..04, FR-REV-03", "docs/10-architecture/adrs/ADR-004, ADR-008, ADR-009, ADR-012", "docs/00-preflight/discovery/data-flow-overview.md DF-05"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** Defines logical data contracts at two boundaries: (A) *inbound* contracts the product's Intake service would enforce on legacy/partner/document sources, and (B) *internal* contracts of the target `hub.sqlite3` store. Physical DDL is Stage 12; schema-evolution/contract-test mechanics are Stage 21. Key evidence finding: the only declared contract (`integration/source-contract-v1.json`, required `ref`, `status`, `schema_version`) is **not satisfied by any of the 8,567 `partner_feeds.raw_json` payloads** (0 contain those keys; payloads carry `object_type, subtype, state, quantity, unit, currency, policy_version, quality_flag, notes, source_version`, plus `business_key` in 8,357). [Inference] the contract is meant for the envelope (columns `ref_id`, `processing_status`, `schema_rev`) rather than the payload, but nothing in the repo states which; resolution is a Stage 12/21 decision, with the existing behaviour preserved as the as-found baseline.

## Findings

### A. Inbound contracts (Intake, ADR-008). All text fields are typed **Untrusted** (ADR-002, FR-INT-07).

| ID | Source | Required (envelope) | Allowed values / types | Validation outcome | Notes / evidence | Class |
|---|---|---|---|---|---|---|
| DC-01 | Partner feed (DS-03) | `feed_id`, `partner`, `schema_rev`, `source_ts` (ISO-8601 UTC), `ref_id`, `record_kind`, `raw_json` (valid JSON object) | `schema_rev` in {1.0, 1.1, 2.0}; `record_kind` in {OOS_RESULT, DEVIATION, CAPA_UPDATE}; `unsupported` (224 rows) is explicit and routed to quarantine with reason `UNSUPPORTED_REVISION` | Pass -> stored raw + outcome record; fail -> quarantine with enumerated reason (FR-INT-04/06) | 0 of 8,567 payloads parse-fail; 8,567 `record_kind` values all in set (2,923/2,817/2,827) | [VF] values; [ASM] set is closed |
| DC-02 | Partner feed payload | `object_type`, `state`, `source_version`; `business_key` recommended | `quantity` numeric (negatives present); `unit` one of observed set (to be enumerated Stage 12); `currency` ISO-4217; `notes` free text = Untrusted | Missing `business_key` (210 of 8,567) -> reason `NO_BUSINESS_KEY`, kept, never auto-linked | 8,357 have `business_key` | [VF] |
| DC-03 | Re-delivery rule | content hash of canonical payload + `(partner, feed_id/business_key)` | same hash = no-op; different content same key = quarantine for human | FR-INT-02/03; replay rows (67 `REPLAY`) must not change totals | as-found: all REPLAY marked DUPLICATE without comparison (RC-6) | [VF] as-found; [INF] rule |
| DC-04 | Gateway message (DS-04) | `message_id`, `external_ref`, `source_system` in {mes, lims, qms}, `event_type` in {batch_created, lab_test, deviation_review, qa_disposition}, `event_time`, `raw_payload` | per `integration/source-gateway.json` | Invalid events stored (not merely counted) in quarantine | as-found invalid events counted not stored (ADR-008 context); 1 inbox row | [VF] |
| DC-05 | Vendor CSV (DS-04/DS-07/08) | named columns `tenant, external_id, kind, region, amount, currency, recorded_at, schema_version, status, language, reference_id` | `amount` kept as **text + parsed decimal** (21 of 2,400 `amount_text` are empty or negative; 10 empty); money = exact decimal (FR-MET-04) | Unparsable amount -> reason `UNPARSABLE_AMOUNT`, never silently skipped | Java reads by position `parts[4]` (DM-17); product must use header names; all 2,400 `external_id` carry the `GXP--` double-hyphen defect (DF-05) | [VF] |
| DC-06 | Document record (DS-09) | `doc_id` (unique), `source`, `locale`, `version`, `effective_at` (date), `body`, `reference`, `access_level` in {engineering, quality, operations, restricted} | `ocr_confidence` nullable float 0..1 (NULL 900/1,200; min observed 0.653) | Missing `access_level` -> treated as `restricted` (deny by default, ASM) | 1,200 unique doc_ids; dates 2023-01-01..2025-09-26; locales es-MX/de-DE/en-IN/ja-JP/en-US | [VF] |
| DC-07 | Archive item (DS-10) | file name, headers (`From`,`To`,`Subject`,`Date`), body, manifest entry | `.eml` quoted-printable decoded; `.html` text-extracted with active content stripped | Parse failure -> quarantine, file untouched | 420 files; addresses `example.invalid` | [VF] |
| DC-08 | Enterprise evidence (DS-06) | `event_id`, `object_id`, `source`, `kind`, `event_time`, `arrival_time`, `schema_version` in {1.0, 1.1, 2.0, legacy}, `payload` | `arrival_time >= event_time` check -> late-arrival flag | read-only adapter only | 12,500 rows; 9 payloads contain "ignore" | [VF] |

### B. Internal (hub) contracts

| ID | Entity | Contract | Source requirement | Class |
|---|---|---|---|---|
| DC-10 | `decision_events` | insert-only; fields: `event_id`, `case_id`, `seq`, `event_type`, `from_state`, `to_state`, `actor`, `actor_kind` (human/rule/system), `occurred_at` (UTC), `recorded_at`, `basis`, `evidence_refs[]`, `policy_version`, `prev_hash`, `hash`. UPDATE/DELETE rejected by trigger. Current state = fold. | FR-DEC-01..06, ADR-004/005 | [INF] design |
| DC-11 | `raw_intake` + `intake_outcome` | raw record immutable (source, schema rev, receipt time, content hash, raw bytes); outcome is a separate append-only table with reason code and queue | FR-INT-01/06, ADR-008 | [INF] |
| DC-12 | `crosswalk_link` | `from_type/id`, `to_type/id`, `key_used`, `creator` (rule/human), `created_at`; unique match by exact configured key only; no similarity | FR-ID-01/02, ADR-009 | [INF] |
| DC-13 | `policy_object` | versioned definition (closed/resolved/approved candidates D-OPS, D-EVID, D-FIN), owner, effective date, status; changes are events (Zone H) | FR-POL-01/03, FR-MET-01 | [INF]; values [UNK] (OPD-01) |
| DC-14 | `doc_index` (FTS5) | one row per document version: text, `doc_id`, `reference`, `locale`, `version`, `effective_at`, `access_level`, `source_hash` | FR-REV-03, ADR-012 | [INF] |
| DC-15 | `run_record` | start/end, trigger, inputs seen, outcomes by type, errors, backlog remaining, checkpoint | FR-RUN-02/03 | [INF] |
| DC-16 | `metric_value` | value + definition tag + policy version + window + denominator + exclusions + label "synthetic, unvalidated" | FR-MET-01/06, PNFR-20 | [INF] |

### C. Contract governance rules

- CG-1 Contracts are versioned files in-repo; change = new version with Change History (CC-06). Ownership of each contract: Engagement lead (Dinesh Naik) interim [ASM].
- CG-2 A producer-side change that violates a contract fails a contract test (Stage 21), not a runtime guess.
- CG-3 The legacy `legacy.sqlite3`/`enterprise_legacy.sqlite3` are read-only to the product through adapters (ADR-003); the product never alters their schemas.
- CG-4 Defaults must be explicit: when a rule has no match the output carries a "defaulted" marker (FR-POL-06), never a hidden value.

## Evidence References

`integration/source-contract-v1.json` (3 required keys); query: key-set frequency over `partner_feeds.raw_json` (0 JSON errors, 0 with all three contract keys, 8,357 with `business_key`); `vendor_file_rows` `amount_text` and `external_id` profile; `source_documents.jsonl` field profile; `integration/source-gateway.json`.

## Assumptions

- A-11-03: Value sets above (record_kind, source_system, access_level) are closed per the observed data; new values are quarantined. Confirm: Engagement lead (Dinesh Naik), Stage 12.
- A-11-04: Missing/unknown `access_level` defaults to `restricted`. Confirm: Stage 24.

## Unknowns

- U-11-04 Which object the declared contract validates (envelope vs payload). U-11-05 Authoritative unit vocabulary. U-11-06 Whether partners would accept a contract change (no real partners exist).

## Unresolved Issues

- Contract/payload mismatch is not fixed here (documentation-only); legacy behaviour stays the characterised baseline (FR-CO-01).

## Residual Risks

- DR-02 (contract not enforced), DR-05 (units), DR-06 (money parsing). See `data-context-risks.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial logical contracts. |
