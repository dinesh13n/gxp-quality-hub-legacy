---
stage: "5 — Discover Current Process & Brownfield Landscape"
artifact: "integration-landscape.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/integration-overview.md", "docs/00-preflight/discovery/data-flow-overview.md", "services/source_gateway/server.py", "integration/source-gateway.json", "integration/source-contract-v1.json", "app/gateway_bridge.py", "app/partner_feeds.py", "app/historical_estate.py", "app/integration.py", "legacy_java/ReconcileLegacy.java", "sql/legacy_reports.sql", "docs/partner-feed-operations.md", "docs/interface-notes.md", "data/legacy.sqlite3 (read-only)", "data/lake/bundled (read-only)"]
supersedes: "none"
---
## Summary

Integration catalogue (interfaces IO-01..IO-15) is in Stage 0A `integration-overview.md` and is referenced, not copied. This file adds the **data-movement view**: every path data takes between systems, which of them are batch/ETL, what triggers them, what is lost or overwritten on the way, and where the process depends on a *manual* trigger. New Stage 5 evidence: gateway event timestamps are formula-generated; the gateway's `qa_disposition` event has no consumer; 26% of partner feeds carry `source_ts > ingest_ts`; recorded outage recoveries include "manual reconciliation" as a data value.

## Findings

### IL-A. Data-movement inventory

| ID | Flow | Trigger | Mode | Transformation / loss | Overwrites? | Evidence | Class |
|---|---|---|---|---|---|---|---|
| IL-01 | Gateway `/api/events` → `gateway_inbox` | Manual CLI `python -m app.gateway_bridge` (Compose runs it once, `restart: "no"`) | Pull, offset checkpoint per stream | Events with `business_key` not in `batch_records` counted `invalid`, **not stored**; checkpoint table is empty in shipped DB (0 rows) | Inbox append; checkpoint upsert | `app/gateway_bridge.py` L13-34; SQL | [Verified Fact] |
| IL-02 | Gateway event content | Request | Computed on the fly | `occurred_at` = `2025-03-{1+n%28}T{n%24}:00:00Z`, event type and source cycle by offset; `schema_version` `0.9` every 19th | n/a | `services/source_gateway/server.py` L21-27 | [Verified Fact] - not real timestamps |
| IL-03 | `qa_disposition` event type | Emitted by gateway (4 event types: batch_created, lab_test, deviation_review, qa_disposition) | — | Bridge stores it in `gateway_inbox` only; **the only reader of `gateway_inbox` is a `COUNT(*)` in `app/operational_report.py` L12** (grep) - no step turns an inbox row into a case change | — | `integration/source-gateway.json`; grep | [Verified Fact] |
| IL-04 | Partner feeds → status | Manual `python -m app.partner_feeds --reconcile` (limit 1000/run) | Batch, in-place | 4 rules (D-02); shipped DB: 8,000 NEW + 500 RETRY + 67 REPLAY, i.e. 9 runs needed to drain at limit 1000; `batch_runs` (60 rows) is generator output, **reconcile does not write `batch_runs`** (no INSERT in `reconcile()`) | **Yes** - original status lost, no history table | `app/partner_feeds.py` L60-71 | [Verified Fact] |
| IL-05 | Partner feed timing | — | — | 2,234 of 8,567 rows (26%) have `source_ts > ingest_ts` (source later than ingestion); schema_rev 1.0: 2,609 / 1.1: 2,659 / 2.0: 3,075 / unsupported: 224 | — | read-only SQL | [Verified Fact] |
| IL-06 | Vendor CSV → `vendor_file_rows` | Manual CLI with a path | Batch | Raw retention, amounts as text (`amount_text`), no validation; idempotent by SHA-256 prefix of file bytes (a re-exported file with 1 changed byte imports again as new) | Append | `app/historical_estate.py` L6-20 | [Verified Fact] / [Inference] on re-export |
| IL-07 | Same CSV → Java month-end total | Manual `java ReconcileLegacy <csv>` (reads file, not the DB table) | Batch | `double` sum; blank or non-numeric amounts silently skipped (2,390 of 2,400 on tiny export, per 0A); bundled CSV has 200 blank amounts of 50,000 | stdout only | `legacy_java/ReconcileLegacy.java`; csv count | [Verified Fact] |
| IL-08 | SQL month-end report | Manual (`sql/legacy_reports.sql` is referenced by no code) | Ad hoc | `LEFT JOIN events` then `sum(c.amount)` → [Inference] amounts multiplied for cases with 2 events (20 of 125 cases have 2) | stdout | file; event counts | [Verified Fact] / [Inference] |
| IL-09 | `source_messages` → adapter | Manual | Read | Ordered by `received_at`; contract `source-contract-v1.json` unenforced; 15 messages in baseline | none | `app/integration.py` | [Verified Fact] |
| IL-10 | Enterprise DB → night-shift job | Manual CLI | Read | Row multiplication via region LEFT JOIN (0A WF-07) | none | `legacy_batch/shift_reconciliation.py` | [Verified Fact] |
| IL-11 | Lake files (events JSONL, ledger, master data, documents) | `app.historical_fixture` generates | none consumed | 100,000 events, 20,000 ledger lines, 480 master rows, 600 docs have **no runtime consumer**; 92 event dates are invalid calendar dates (e.g. 2023-02-29) | — | grep `lake`; date parse of bundled events | [Verified Fact] |
| IL-12 | Archive .eml/.html, `source_documents.jsonl` | none | none | Orphaned | — | 0A IO-06 | [Verified Fact] |
| IL-13 | Outbound API | Pull by unknown consumers | HTTP GET | No auth/version; `/api/partners/*` triggers schema DDL (see `current-process-map.md` DO-01) | — | `app/server.py` | [Verified Fact] |

### IL-B. Recorded recovery behaviour (from data, not code)

`upstream_outages` (72 rows, 2021-01-01..2024-04-22): recovery actions - rerun import 20 (3 unresolved), restart bridge 19 (3), leave queued 17 (1), **manual reconciliation 16 (1)**. [Verified Fact] on rows; the rows are generator output (`app/partner_feeds.py`), so they evidence the *intended pattern* of manual recovery, not real frequency [Inference]. `batch_runs` results: SUCCESS 23, PARTIAL 18, FAILED 19 (also generated).

### IL-C. No event bus, no scheduler

No queue, broker, webhook, SFTP, cron or workflow engine exists (grep); every "batch" is human-started. The word "event" in the estate means a row (`events`, `gateway_inbox`, `evidence_events`, lake JSONL), not a stream [Verified Fact]. Delivery guarantees: at-most-once for invalid gateway events (dropped), at-least-once with PK dedupe for valid ones.

### IL-D. Documented vs observed

| ID | Documented | Observed | Class |
|---|---|---|---|
| IN-01 | `docs/partner-feed-operations.md`: replays and delayed delivery are normal | Code classifies every REPLAY as DUPLICATE regardless of content - a legitimate corrected replay would be discarded | [Verified Fact] code / [Inference] consequence |
| IN-02 | `integration/source-contract-v1.json` required fields | Not validated by `app/integration.py` | [Verified Fact] |
| IN-03 | INC-2025-014 "queue retried twice" | Bridge has no retry logic (0A IO-02); the "queue" it mentions does not exist in the repo | [Verified Fact] absence - so the documented incident concerns a runtime that is not this repo [Inference] |

## Evidence References

`services/source_gateway/server.py` L8-30; `integration/source-gateway.json`; `app/gateway_bridge.py`; `app/partner_feeds.py` L11-71; `app/historical_estate.py`; `legacy_java/ReconcileLegacy.java`; `sql/legacy_reports.sql`; SQL on `data/legacy.sqlite3` (`gateway_checkpoints`=0 rows, `partner_feeds` timings and revs, `upstream_outages` actions); Python date parse of `data/lake/bundled/events/*.jsonl` (92 invalid dates); CSV blank-amount count (200).

## Assumptions

- A-05-06: Real integrations at the client would also be manually triggered or scheduled outside this repo. Confirm: Engagement lead (Dinesh Naik) - Stage 7/14.

## Unknowns

- U-05-10 Real cadence of partner feeds and of reconcile runs. U-05-11 Whether `gateway_inbox` is intended to feed `cases` (no such code). U-05-12 Intended meaning of `qa_disposition` events.

## Unresolved Issues

- The documented incident (INC-2025-014) cannot be reproduced from the repo's mechanisms.

## Residual Risks

- Silent drops (invalid gateway events), silent skips (Java), in-place status overwrite and dropped legitimate replays all lose evidence needed for GxP data integrity (ALCOA+); not yet assessed against regulation (Stage 7/compliance stages).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 5 discovery draft (read-only; no application code executed; SQLite opened `mode=ro&immutable=1`). |
