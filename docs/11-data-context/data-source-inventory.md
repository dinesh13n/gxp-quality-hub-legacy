---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "data-source-inventory.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["data/legacy.sqlite3 (read-only, mode=ro&immutable=1)", "data/enterprise_legacy.sqlite3 (read-only)", "data/documents/source_documents.jsonl", "data/archive_documents/manifest.json", "data/lake/tiny/manifest.json", "integration/source-contract-v1.json", "integration/source-gateway.json", "contracts/decision-policies-archive.json", "docs/00-preflight/discovery/data-flow-overview.md DF-01..DF-10", "docs/00-preflight/operating-contract/data-use-constraints.md", "docs/data-dictionary.md", ".fde/orchestrator-decisions.md OD-04, OD-08, OD-09", "docs/10-architecture/adrs/ADR-004, ADR-008, ADR-009, ADR-012"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** Eleven legacy data sources (DS-01..DS-11) plus one planned target store (DS-T1 `hub.sqlite3`, ADR-004, PROPOSED) were inventoried. Counts were re-verified in this stage with read-only SQLite queries. **No source has a named human owner or an enforced contract**: the only owner-like values are generator-produced `owner_team`/`action_owner` columns inside the data, and the one declared contract (`integration/source-contract-v1.json`) is not enforced (RC-6). Per the Completion Gate this is a *documented gap*, not an invented owner: every source is assigned the interim steward **"Engagement lead (Dinesh Naik)"** (the only human on the engagement) as a placeholder, flagged as Assumption. Baseline = shipped 125-case DB, seed 4100 (OD-09).

## Findings

Tags: [VF] Verified Fact, [INF] Inference, [ASM] Assumption, [UNK] Unknown. Access = who can read today ([VF] no authentication anywhere, SO-01).

| ID | Source (path) | Content / volume | Producer -> consumer | Owner today | Contract today | Classification (ASM, would-be) | Class |
|---|---|---|---|---|---|---|---|
| DS-01 | `data/legacy.sqlite3` tables `cases` 125, `events` 145 (CASE_CREATED 125, STATUS_REVIEWED 20) | Case snapshot (status OPEN 42, UNDER_REVIEW 30, CLOSED 36, ESCALATED 9, REOPENED 8; created 2023-01-25..2025-12-19; regions AMER 46/APAC 39/EMEA 40); `version`=1 for all | `app.generate`, tests -> API, reports | None named [UNK]; interim steward Dinesh | DDL in `app/store.py`; FKs on events->cases | Internal/Confidential (account_id `ACCT-nnnnnn`) | [VF] counts; [ASM] class |
| DS-02 | `legacy.sqlite3` `materials` 30, `batch_records` 125, `deviations` 42, `lab_results` 125, `capa_actions` 21, `sop_versions` 45, `reference_versions` 180 | Pharma domain objects; units `pct` 68 / `percent` 57 in batch_records, 64/61 in lab_results; no NULL result_value in this DB (0/125) | `domain_data` -> API/reports | None [UNK]; `capa_actions.action_owner` is data | `docs/data-dictionary.md` L3-5 + DDL; FKs batch->material, deviation->batch, lab->batch, capa->deviation | GxP-record-like (ASM) | [VF] |
| DS-03 | `legacy.sqlite3` `partner_feeds` 8,567 (NEW 8,000 / RETRY 500 / REPLAY 67; schema_rev 1.0 2,609 / 1.1 2,659 / 2.0 3,075 / unsupported 224), `batch_runs` 60, `policy_exceptions` 224, `upstream_outages` 72 | Partner/staging feed; only 173 of 8,567 `ref_id` values match a `cases.id` (8,394 orphans) | `partner_feeds.py` -> reconcile (in-place status mutation) | None [UNK] | `integration/source-contract-v1.json` (required ref, status, schema_version) **not enforced**; no FK on `ref_id` | Confidential (ASM) | [VF] |
| DS-04 | `legacy.sqlite3` `gateway_inbox` 1, `gateway_checkpoints` 0, `source_messages` 15, `vendor_file_imports` 1, `vendor_file_rows` 2,400 | Gateway receipts and vendor CSV import | simulator/bridge/importer | None [UNK] | `integration/source-gateway.json` (config, not a schema) | Internal | [VF] |
| DS-05 | `legacy.sqlite3` `operating_costs` 36 | Monthly modelled cost (labor_hours, total_cases, infrastructure_usd); modelled, not measured (OD-07) | `generate.py` L40-42 | Finance? [UNK] | none | Internal/Financial (ASM) | [VF] model; [UNK] owner |
| DS-06 | `data/enterprise_legacy.sqlite3` (12 tables; `operational_objects`/`state_history`/`document_links`/`evidence_events` 12,500 each; `workflow_tasks` 6,250; `access_audit` 4,167; `cross_references` 4,166; `financial_adjustments` 3,125; `integration_attempts` 2,500; `retention_events` 2,084; `organizations` 96; `policy_register` 40) | 4 tenants, 6 statuses (~2,080 each), 6 languages; `retention_events`: all class `standard`, 123 `legal_hold=1`; `access_audit`: 220 empty `access_reason`; evidence_events schema_version 1.0/1.1/2.0/legacy 3,125 each | `enterprise_legacy.py` -> `shift_reconciliation` only | `owner_team` column is data; no human [UNK] | DDL + FKs (10 of 12 tables) | Confidential (actors, tenant, financial, legal hold) (ASM) | [VF] |
| DS-07 | `data/lake/tiny/` (master_data 480, ledger 960, `partner_export.csv` 2,400, 9,500 events, 360 docs; manifest seed 7421) | Historical lake, tiny tier | `historical_fixture` -> Java reconcile | None [UNK] | `manifest.json` (counts, sha256 of CSV); CSV read by position (DM-17) | Internal | [VF] |
| DS-08 | `data/lake/bundled/` (30 MB: ledger 20,000; CSV 50,000; 100,000 events; 600 docs) | Bundled tier | `historical_fixture --tier bundled` -> inventory script only | None [UNK] | `manifest.json` | Internal | [VF] |
| DS-09 | `data/documents/source_documents.jsonl` (git-tracked, 1,200 rows, 324 KB dir) | Fields: doc_id, domain, source (5), locale (5), version (4), effective_at (2023-01-01..2025-09-26), body, ocr_confidence (NULL for 900 = 75%; 38 < 0.70), reference, access_level (restricted 328, operations 295, engineering 305, quality 272) | `generate_documents.py` -> no consumer in code | None [UNK] | none (no schema file) | Restricted for 328 rows (ASM) | [VF] |
| DS-10 | `data/archive_documents/` (git-tracked, 210 `.eml` + 210 `.html` + `manifest.json`; 6 languages; `synthetic: true`) | Archive notes with `example.invalid` addresses | `archived_documents.py` (deletes dir on regenerate, DM-12) -> none | None [UNK] | `manifest.json` counts only | Internal | [VF] |
| DS-11 | `contracts/decision-policies-archive.json`, `domain.json`, `domain-profile.json`, `integration/*.json` | Policy and configuration data read at import (DM-14, DM-18) | hand-maintained -> JS/Python | None [UNK] | self | Controlled configuration | [VF] |
| DS-T1 | `hub.sqlite3` (target, does not exist) | Append-only event store, crosswalk, intake records, audit chain, FTS index (ADR-004/005/008/009/012, all PROPOSED) | product -> product | Dinesh (interim) [ASM] | `data-contracts.md` (this stage) | Confidential (ASM) | [INF] design only |

### Cross-cutting findings

| ID | Finding | Evidence | Impact | Risk | Confidence | Class |
|---|---|---|---|---|---|---|
| DI-01 | No source has an accountable human owner, steward or custodian; ownership of data, retention, and definitions of closed/resolved is open (OPD-01, OPD-09, OPD-15). | repo-wide; open-product-decisions | Completion Gate "owner or documented gap" met only as a documented gap | High | High | [VF] absence in repo; [UNK] real owners |
| DI-02 | Three disjoint identifier spaces and no cross-store key: cases `C########` (DS-01), objects `GXP-########`/`TENANT-*` (DS-06), lake `REF-######`/`T-NORTH…` (DS-07/08). | DF-09; schemas | Joins impossible without ADR-009 crosswalk | Medium | High | [VF] |
| DI-03 | Document `reference` values look like case IDs but only 30 of 1,200 match an existing `cases.id`; 1,081 distinct values for 1,200 docs. | query this stage | Evidence-to-case linking will be mostly unmatched; must be reported, not hidden (ADR-009 consequence) | Medium | High | [VF]; cause [INF] generator-shaped |
| DI-04 | Document corpus has only 3 distinct base sentences (387 / 394 / 397 rows) plus 22 rows with an appended injection line (9+5+8). Search quality results on it will be unrepresentative. | query this stage | FTS recall/precision cannot be validated on this corpus (see `synthetic-data-strategy.md`) | Medium | High | [VF] |
| DI-05 | `legacy.sqlite3` shipped content is test-fixture residue (DF-03); `data/*.sqlite3` and `data/lake/` are git-ignored, so only 6 -> now all 1,512 files are covered by backup manifest. | DF-03; OD-03a | Provenance of the baseline is "as shipped, generator/test-derived" | Medium | High | [VF] |
| DI-06 | Dataset baseline fixed: 125 cases, seed 4100 (OD-09). The `partner_feeds` and `policy_exceptions` volumes (8,567 / 224) were generated against a larger case set, so orphan rates reflect that, not a real defect (R-05). | OD-09; DF-03 | Fixtures for later stages must use this baseline and label orphans as such | Low | High | [VF] decision; [INF] cause |

## Evidence References

Read-only queries this stage (`file:...?mode=ro&immutable=1`): table counts and PRAGMA table_info for both DBs; status/region/unit distributions; `source_documents.jsonl` field profile; archive and lake manifests. Prior: DF-01..DF-10 (Stage 0A), DU-01..DU-06 (0B).

## Assumptions

- A-11-01: Interim steward for every source is "Engagement lead (Dinesh Naik)" until real owners exist. Confirm: Engagement lead (Dinesh Naik), Stage 25.
- A-11-02: Classification labels (Internal/Confidential/Restricted/Financial) are would-be labels for a regulated setting; GxP / 21 CFR Part 11 framing is unconfirmed (OPD-16). Confirm: Engagement lead (Dinesh Naik), Stage 24.

## Unknowns

- U-11-01 Real data owners/stewards (OPD-04, OPD-15). U-11-02 Real data availability (none exists; all synthetic). U-11-03 Who owns `operating_costs` definition (OPD-08).

## Unresolved Issues

- Ownership and contract gaps above are documented, not resolved; they are non-blocking for a No-AI synthetic engagement but must be closed before any non-synthetic use.

## Residual Risks

- DR-01, DR-02, DR-03 in `data-context-risks.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial inventory, re-verified by read-only queries. |
