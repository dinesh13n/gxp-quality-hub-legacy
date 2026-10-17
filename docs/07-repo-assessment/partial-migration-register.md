---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "partial-migration-register.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/legacy-operations-history.md", "docs/historic-decisions.md", "docs/interface-notes.md", "docs/source-systems-and-constraints.md", "contracts/decision-policies-archive.json", "app/integration.py", "app/gateway_bridge.py", "app/partner_feeds.py", "app/historical_estate.py", "app/server.py", "app/enterprise_data.py", "app/enterprise_legacy.py", "legacy_batch/shift_reconciliation.py", "Dockerfile", "compose.yaml", "domain.json", "docs/07-repo-assessment/baseline-behaviour.md"]
supersedes: "none"
---
## Summary

Eleven partial or paused migrations (PM-01..PM-11) are evidenced either by the repository's own history documents or by parallel implementations of the same concern in code. **The history documents are narrative, unsigned and synthetic; they are used as evidence of what the repository claims, not of what the organisation did** (OD-04). Where code shows two co-existing implementations, the finding is [Verified Fact] on the code; the migration *story* is [Inference]. The most consequential partial migrations are PM-01 (policy roles changed in 2025 but code unchanged), PM-02 (two data models: generic `cases` vs GxP batch entities) and PM-03 (two intake mechanisms).

## Findings

| ID | Migration (claimed or inferred) | Old side | New side | State evidenced | Evidence | Risk | Class | Confidence |
|---|---|---|---|---|---|---|---|---|
| PM-01 | Approval policy tightening (2024 "stricter approvals ... parallel workflow retained"; 2025 roles change) | Python `priority()` single threshold 50,000; night-shift thresholds 2,500-8,500 | `contracts/decision-policies-archive.json`: 15 `batch_disposition` versions 2022-2026, approver `operations_lead` (2022-2024) -> `business_owner` + `risk_control` (2025-2026), regional limits 15,000-27,200 | New policy exists as data and is read **only** by JS; no runtime enforcement of approver roles anywhere | `legacy_js/legacy_policy.js`; `docs/legacy-operations-history.md` 2024; RC-4 | High | [Verified Fact] (code/data) / [Inference] (story) | High |
| PM-02 | Domain re-targeting: generic customer-case template -> GxP batch quality | `cases` (account_id, segment `enterprise/priority/legacy-v1`, amount, notes such as "Customer service notes partial recovery") used by API, priority, baseline | `materials`, `batch_records`, `deviations`, `lab_results`, `capa_actions`, `sop_versions` (read-only endpoints; no state logic) | Both exist side by side with no keys between them; the API's core aggregate is still the generic `cases` | `app/generate.py` L12-13, L30; `app/enterprise_data.py`; AD-17 | High | [Verified Fact] | High |
| PM-03 | Intake: simple adapter -> persistent bridge with offsets/idempotency | `app/integration.py` `consume_source_messages` (reads `source_messages`, no writer outside generator, no CLI use except print) | `app/gateway_bridge.py` + `services/source_gateway/server.py` + `gateway_inbox`/`gateway_checkpoints` | Both present; the old adapter has no caller except tests (`test_feed_parser`); events from the new path are never consumed by any downstream step (inbox is write-only; `qa_disposition` event type has no consumer) | grep; BB-04 | Medium | [Verified Fact] | High |
| PM-04 | Partner ingestion (2020): replays "operationally common" -> staged feeds with reconcile | CSV file-drop (`historical_estate`) and Java/SQL month-end | `partner_feeds` staging + `--reconcile` | Three overlapping partner/vendor ingestion paths (`partner_feeds`, `vendor_file_*`, `gateway_inbox`) with different keys and no link | code; AD-10 | High | [Verified Fact] | High |
| PM-05 | Schema versions: 1.0 -> 1.1 -> 2.0 (+ `unsupported`, gateway `0.9`, `legacy-v1`, `legacy` source version) | v1.0 | v2.0 | Reconcile only rejects `unsupported`; 0.9/1.0/1.1/2.0 processed identically; no version-specific mapping | `partner_feeds.py` L34, L66; `gateway server.py` L28; `integration/source-contract-v1.json` unused | Medium | [Verified Fact] | High |
| PM-06 | Status vocabulary / region mapping changes (2021 status mappings; 2022 revised region mapping) | case statuses `OPEN/UNDER_REVIEW/CLOSED/ESCALATED/REOPENED`; regions APAC/AMER/EMEA | enterprise `OPEN/REVIEW/HOLD/CLOSED/REOPENED/ESCALATED`; regions IN/DE/US/JP/BR/GB/ZA/AU; batch `REVIEW/QA_HOLD/CLOSED`; lake `ACTIVE/PENDING/FAILED/REVERSED/ESCALATED/REOPENED`; docs human queues `OPEN/INVESTIGATING/QA_REVIEW/DISPOSITIONED/REOPENED` | Five coexisting vocabularies and two region taxonomies; JS thresholds keyed only on APAC/EMEA/AMER, so enterprise regions fall to 999,999 | BB-09; `interface-notes.md` 2021; `legacy-operations-history.md` 2022 | High | [Verified Fact] | High |
| PM-07 | Host migration (2023: shared host -> container host); (2025: "migration initiative paused after compatibility concerns") | bare-process `run.sh` | `Dockerfile`/`compose.yaml` | Container artefacts exist but were never executed here; Compose splits data into an image-baked DB and a volume DB | `interface-notes.md`; `legacy-operations-history.md` 2025; TD-26 | Medium | [Verified Fact] (files) / [Unknown] (runtime) | Medium |
| PM-08 | Spreadsheet approvals (2018) -> service | spreadsheet adjustments ("Manual spreadsheet adjustment applied during month-end close" appears in case notes) | `app/` service | Manual spreadsheet step persists in the monthly close narrative; not in code | `generate.py` notes; `legacy-operations-history.md` 2018 | Medium | [Inference] | Low |
| PM-09 | LIMS-QMS migration (2023) retained older identifiers; mapping documentation "not fully refreshed" | old batch identifiers | LIMS-QMS ids | Gateway keys on `batch_id`; cases on `C########`; support refers to either (history doc); no cross-reference table | `historic-decisions.md` 2023; BB-03 | Medium | [Verified Fact] (absence of mapping) | Medium |
| PM-10 | Monthly operating metrics (2025 "reporting team implemented new monthly operating metrics") vs legacy month-end paths | Java/SQL totals | `operating_costs` + `/api/metrics` + `app.baseline` | Three independent month-end computations, none sharing definitions (RC-8); `operating_costs.total_cases` unrelated to `cases` (OD-07) | `interface-notes.md` 2025; BB-08, BB-11 | High | [Verified Fact] | High |
| PM-11 | Database platform: SQL Server/Oracle (historic) -> SQLite (local) | n/a | SQLite | Historic engines not present; SQL file uses ANSI subset; types are SQLite-flexible (e.g. `REAL` for money, TEXT dates) | `interface-notes.md` | Low | [Verified Fact] (absence) | High |

## Evidence References

As cited per row; `docs/legacy-operations-history.md`, `docs/historic-decisions.md` (narrative), `contracts/decision-policies-archive.json` (15 versions, rule `batch_disposition`, roles by year), grep results for callers of `consume_source_messages` (tests only).

## Assumptions

- A-07-14: The history documents are accepted as a faithful (synthetic) description of the estate's past; no corroborating artefacts (tickets, change logs) exist. Confirm: Engagement lead (Dinesh Naik), Stage 8.

## Unknowns

- U-07-08: Whether the "paused 2025 migration" corresponds to any code branch or artefact (the repository history has 12 commits; the first is the as-found import tagged `baseline-as-found`, so no earlier history exists).
- U-07-09: The extent to which the parallel (older-customer) workflow still exists.

## Unresolved Issues

- No migration has a recorded completion criterion; Stage 14 must define what "done" means for PM-01..PM-06 before sequencing.

## Residual Risks

- R-07-11: Completing a partial migration without knowing the abandoned one's rationale (PM-07, "compatibility concerns") may repeat the 2025 rollback.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial register (11 items). |
