---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "data-quality-rules.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["data/legacy.sqlite3 (read-only)", "data/enterprise_legacy.sqlite3 (read-only)", "data/documents/source_documents.jsonl", "docs/00-preflight/discovery/data-flow-overview.md DF-05", "docs/09-initial-prd/nfrs.md PNFR-10..13, PNFR-16, PNFR-20", "docs/09-initial-prd/functional-requirements.md FR-INT-*, FR-MET-*", "docs/10-architecture/adrs/ADR-008, ADR-011"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** 24 measurable quality rules (DQ-01..DQ-24) with an *as-found value on the baseline dataset* (125 cases, seed 4100; OD-09) wherever a read-only query could measure it. Principle: **source data is never "cleaned" in place** (DU-06). Rules either (a) reject/quarantine at intake with a reason code, (b) flag as a finding for a human, or (c) are monitored as a measure. Thresholds marked "[ASM] target" are proposals, not approvals; the baseline column is Verified Fact. Severity: B = blocks load to hub, Q = quarantine, F = finding/flag, M = monitor.

## Findings

| ID | Dimension | Rule | Sev | As-found on baseline (read-only) | Proposed target | Class |
|---|---|---|---|---|---|---|
| DQ-01 | Completeness | `business_key` present on every partner feed | Q | 8,357 / 8,567 present; 210 missing (2.45%) | 0 loaded without reason `NO_BUSINESS_KEY` | [VF] / [ASM] target |
| DQ-02 | Validity | `schema_rev` in {1.0, 1.1, 2.0} | Q | 224 `unsupported` (2.61%) | 100% routed to quarantine, none dropped | [VF] |
| DQ-03 | Validity | `raw_json` parses as JSON object | B | 0 parse errors / 8,567 | 0 | [VF] |
| DQ-04 | Conformance | Payload satisfies declared contract keys (`ref`,`status`,`schema_version`) | Q | 0 / 8,567 payloads (see `data-contracts.md`) | defined after U-11-04 | [VF]; target [UNK] |
| DQ-05 | Uniqueness/idempotency | Same content hash re-delivered = no-op; different content same key = quarantine | Q | 67 REPLAY rows all marked DUPLICATE without comparison (RC-6); 4,590 distinct `ref_id` / 8,567 rows | 0 duplicate effects over replay suite (PNFR-11) | [VF] |
| DQ-06 | Referential integrity | Feed `ref_id` resolves to exactly one case via crosswalk | F | 173 / 8,567 match `cases.id`; 8,394 orphans (97.98%) | orphans reported per source (FR-MET-07), never hidden or guessed | [VF] |
| DQ-07 | Referential integrity | Document `reference` resolves to a case | F | 30 / 1,200 match (2.5%) | reported, not linked by similarity (FR-ID-02) | [VF] |
| DQ-08 | Referential integrity | FK pragma enforced on every connection | B | on in `store.connect` only; other direct connections off (DM-02); FK errors 0 in inventory | on for all product connections | [VF] |
| DQ-09 | Consistency (units) | Unit vocabulary normalised only in a derived column, raw kept | F | `pct` vs `percent`: batch_records 68/57; lab_results 64/61 | 100% mapped via documented table | [VF] |
| DQ-10 | Validity (numeric) | Quantity/amount negative or unparsable flagged | F | vendor `amount_text`: 10 empty + 11 negative of 2,400; feed `quantity` negatives present (sample) | all flagged `UNPARSABLE_AMOUNT`/`NEGATIVE_VALUE`; money exact decimal (FR-MET-04) | [VF] |
| DQ-11 | Validity (identifier) | Identifier pattern checks (`GXP-########`) | F | all 2,400 vendor `external_id` use `GXP--` double hyphen | flagged; mapping rule documented, original kept | [VF] |
| DQ-12 | Validity (dates) | Calendar-valid dates; `effective_at` not after `valid_to` | F | lake events include invalid date `2023-02-29` (DF-05); reference windows overlap | 100% invalid dates flagged | [VF] |
| DQ-13 | Timeliness | `arrival_time - event_time` captured and late arrivals flagged | M | `evidence_events` carries both fields (12,500 rows); distribution not measured here | threshold [UNK] (PNFR-03/04 are Assumptions) | [VF] fields; [UNK] threshold |
| DQ-14 | Completeness (documents) | `ocr_confidence` present; low-confidence flagged | F | NULL 900 / 1,200 (75%); 38 below 0.70 | NULL treated as "unknown", never as high | [VF] |
| DQ-15 | Completeness (audit) | `access_reason` non-empty on every access | F | 220 / 4,167 empty (5.28%) | 0 empty for product-written audit | [VF] |
| DQ-16 | Integrity (history) | Every REOPENED case has a reopen event; creation event stores state at creation | B (hub) | 8 REOPENED cases, 0 reopen events; `events` types only CASE_CREATED 125, STATUS_REVIEWED 20; `cases.version`=1 for 125 | invariant count = 0 (FR-DEC-03) | [VF] |
| DQ-17 | Integrity (state) | Current state equals fold of events | B (hub) | not computable on legacy (snapshot only) | 100% replay match (FR-DEC-02) | [VF] gap |
| DQ-18 | Consistency (cross-object) | Contradictory combinations (e.g. case CLOSED with open linked CAPA) surfaced | F | not measured; no key links case to CAPA (ADR-009 context) | findings listed, no auto-fix (FR-ID-03) | [UNK] |
| DQ-19 | Untrusted content | Instruction-like strings never alter decision fields | B | 86 feed rows, 22/1,200 doc bodies (9+5+8), 9 enterprise evidence_events, archive >=4, lake 15 tiny / 150 bundled | 0 effects over planted-string fixture (PNFR-13) | [VF] |
| DQ-20 | Retention integrity | No deletion of case/evidence rows while policy unadopted | B | no deletion code exists in repo (DF-10); `retention_events`: 2,084 all class `standard`, 123 `legal_hold=1`; expiry dates 2027+ | 0 deletions (PNFR-10) | [VF] |
| DQ-21 | Metric reproducibility | Each KPI carries window, denominator, exclusions, definition tag, "synthetic, unvalidated" label | B (report) | `operating_costs.total_cases` random, not "cases created" (OD-07) | 100% labelled (PNFR-16/20) | [VF] |
| DQ-22 | Language/encoding | UTF-8 round-trip for es/de/ja/hi/pt text; NFC normalisation for indexing | F | 6 languages in `document_links` (~2,083 each); 5 locales in documents; 3 languages (EN/ES/JA) in case notes | 0 mojibake in test set | [VF] languages; [INF] rule |
| DQ-23 | Provenance completeness | Every hub row carries `source`, `source_hash`, `ingested_at`, `run_id` | B | legacy tables carry source for feeds only | 100% | [INF] |
| DQ-24 | Orphan accounting | Orphan counts are a reported measure, not a defect to fix in source | M | see DQ-06/07; baseline orphan rates are generator-shaped (R-05) | trend per source | [VF]/[INF] |

### Measurement approach (Stage 14 owns tests, Stage 12 owns SQL)

- MQ-1 Each rule is a deterministic SQL/Python predicate with a count and an identifier list; results stored as run records (DC-15).
- MQ-2 Rules run (i) on the baseline fixture in the sandbox (regression), (ii) at every intake run.
- MQ-3 No rule consults a model; no randomness (PNFR-17).
- MQ-4 Baseline values above are frozen as the "as-found" quality profile for before/after comparison.

## Evidence References

Read-only queries (2026-10-18) on `data/legacy.sqlite3`: feed key-set, schema_rev, record_kind, `ref_id` vs `cases.id`; `vendor_file_rows` amount/ID profile; `lab_results`/`batch_records` units; `source_documents.jsonl` profile; `enterprise_legacy.sqlite3` `access_audit`, `retention_events`, `evidence_events`. Prior: DF-05, DF-08.

## Assumptions

- A-11-05: Proposed targets are engineering proposals; no quality SLA has been approved or exists. Confirm: Engagement lead (Dinesh Naik), Stage 12/14.
- A-11-06: Late-arrival, orphan and ocr thresholds remain unset until a data owner exists.

## Unknowns

- U-11-07 Business-acceptable orphan rate. U-11-08 Authoritative unit mapping. U-11-09 DQ-13 and DQ-18 not measured in this stage.

## Unresolved Issues

- DQ-18 and DQ-13 baselines can only be measured with a crosswalk/adapters (Stage 12/14).

## Residual Risks

- DR-05, DR-06, DR-07, DR-08.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial rules with as-found values. |
