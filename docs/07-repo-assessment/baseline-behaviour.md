---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "baseline-behaviour.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/07-repo-assessment/evidence/golden/api_golden_run1.json", "docs/07-repo-assessment/evidence/golden/batch_golden_run1.json", "docs/07-repo-assessment/evidence/golden/lib_golden_run1.json", "docs/07-repo-assessment/evidence/scripts/capture_api.py", "docs/07-repo-assessment/evidence/scripts/capture_batch.py", "docs/07-repo-assessment/evidence/scripts/capture_lib.py", "docs/07-repo-assessment/evidence/analysis/golden_mutation_replay_*.json", "app/*.py", "services/source_gateway/server.py", "legacy_batch/shift_reconciliation.py", "legacy_java/ReconcileLegacy.java", "legacy_js/legacy_policy.js", "sql/legacy_reports.sql", "contracts/decision-policies-archive.json", "docs/05-current-state/*", "docs/06-root-cause/confirmed-root-causes.md"]
supersedes: "none"
---
## Summary

This is the **behaviour baseline** ("golden outputs") that Stages 15-16 must preserve or explicitly justify changing. It was captured by executing the as-found code against the shipped 125-case database (OD-02, provisional) inside a sandbox copy. Three capture scripts produced **three golden JSON files** (HTTP API + source gateway: 39 + 16 requests; batch/CLI/Java/JS/SQL/generators: 58 keys; library edge cases: 9 keys). Each capture was executed **twice and is byte-identical** (`cmp` equal), so the outputs are deterministic given: shipped DB `c254649f...d70aa`, `PYTHONHASHSEED=0`, Python 3.10.12, Java 11, Node 22. The read-only parts of the capture leave the DB hash unchanged (`c254649f...` after API/CLI baseline runs). The golden set detects 14 of 14 replayed regression mutants (M9 only after the library-level golden was added), versus 1 of 15 for the existing unit tests (`baseline-test-results.md` TQ-05).

**What "preserve" means.** The baseline records **current behaviour including defects** (e.g. three divergent approval rules, row multiplication, silent drops). Defects are marked **[DEFECT]** so Stage 15 can distinguish "preserve exactly" from "preserve until a decision is taken" (RC-3/RC-4 are decision gaps; do not merge rules by assumption).

## Findings

Legend: values quoted are from the golden files; "G:" gives the key. All items [Verified Fact] unless stated.

### BB-01 Case triage and prioritisation (CW-01) - `app/legacy_logic.py`

| Aspect | Observed behaviour (G: `priority_truth_table` 120 rows) |
|---|---|
| Rule order | `CLOSED` -> `archive` (any severity/amount); else `CRITICAL` or `amount > 50000` -> `urgent`; else `HIGH` or `ESCALATED` -> `review`; else `queue`. |
| Boundaries | amount `50000` -> not urgent; `50000.01` -> urgent; `-1`, `0` -> no effect; CLOSED beats everything. Amount is strict `>` on a float. |
| Unvalidated inputs | Unknown status/severity strings fall through to `queue`; no exception. |
| Over the shipped 125 cases (G: `api_priority_distribution`) | `archive` 36, `queue` 70, `review` 17, `urgent` 2. **No shipped case has amount > 50000** (verified: 0 rows), so the amount branch of the rule is not exercised by the shipped data; only the truth table pins it. |
| `manual_review_required(status, severity)` (G: `manual_review_truth_table` 20 rows) | True iff severity in {HIGH, CRITICAL} or status in {ESCALATED, REOPENED}; note CLOSED+HIGH is still True. |

### BB-02 HTTP API on port `PORT` (default 8080, host `127.0.0.1`) - `app/server.py` (CW-01/02/03/10/13)

Captured with a server started from the pristine copy; DB hash unchanged after capture.

| Request | Status / behaviour (G: `api`) |
|---|---|
| `GET /health` | 200 `{"service":"gxp-quality-hub-legacy","status":"ok"}` |
| `GET /` | 200 routes list of only 5 routes (`/health`, `/api/cases?limit=20`, `/api/cases/C00000001`, `/api/metrics`, `/api/incidents`) - **[DEFECT]** `/api/partners/*` and `/api/domain/*` exist but are not advertised |
| `GET /api/incidents` | 200 hard-coded single incident `INC-2019-0082`, summary from `domain.json` `legacy_incident`, state `investigating` (static; WF-10) |
| `GET /api/metrics` | 200 `total_cases` 125; `by_status` CLOSED 36, ESCALATED 9, OPEN 42, REOPENED 8, UNDER_REVIEW 30; `monthly_operating_costs` 36 rows (`operating_costs`, ordered by period) |
| `GET /api/cases` | 200; default `limit` 20 offset 0; items ordered by `id`; each item has all `cases` columns plus computed `priority` |
| Pagination clamps | `limit` clamped to 1..100 (`limit=1000` -> 100 items; `0` and `-5` -> 1); `offset` clamped to >= 0; non-integer -> 400 `{"error":"invalid pagination"}`; offset past end -> 200 empty `items` |
| `GET /api/cases/<id>` | 200 case + `events` (ordered by `recorded_at`) + `manual_review_required`; unknown id or trailing slash -> 404 `{"error":"not found"}`; SQL-metacharacter id -> 404 (parameterised) |
| `GET /api/partners/{partner_feeds,reference_versions,policy_exceptions,upstream_outages,batch_runs}` | 200 `{resource,total,items}`; `total` for partner_feeds 8567; unknown -> 404 `unknown partner resource`; calls `partner_feeds.init()` (DDL) on every request |
| `GET /api/domain/{deviations,lab_results,capa_actions,sop_versions}` | 200 `{resource,total,items}`; unknown -> 404 `unknown domain resource` |
| Unknown route | 404 `{"error":"route not found"}` |
| `POST/PUT/DELETE /api/cases` | **501** HTML error page from `http.server` (no write path; G: `METHOD *`); `HEAD` 501 empty body |
| Content type | `application/json; charset=utf-8`; no auth, no CORS, no security headers |
| Full case list with priority | G: `api_all_cases_priority` (125 rows: id, status, severity, amount, priority) |

Response bodies (<20 kB) are stored verbatim; larger ones by SHA-256 (e.g. `/api/cases?limit=1000` 31,916 bytes).

### BB-03 Source gateway (port `SOURCE_PORT`, default 8090) - `services/source_gateway/server.py` (CW-04)

| Request | Observed (G: `gateway`) |
|---|---|
| `/health` | 200 `{status:ok, service:source-gateway, domain:"Life Sciences"}` |
| `/api/catalog` | 200 contents of `integration/source-gateway.json` |
| `/api/events?limit=N&offset=M[&source=mes|lims|qms]` | 200 `{items,count,next_offset}`; one event per `batch_records` row ordered by `batch_id`; `limit` 1..200; `message_id` = first 24 hex chars of `sha256(system+business_key+event_type)`; `event_type` and `system` cycle by position (4 types, 3 systems); `schema_version` is `"0.9"` for every 19th position else `"1.0"`; `occurred_at`/`published_at` are formulas (`2025-03-DD...`); `payload.source_status` `HOLD` for every 5th else `OPEN`. Offset past end -> 200 empty with `next_offset` = offset. Unknown `source` -> 400; non-integer -> 400 `bad pagination`. |
| `/api/record/<batch_id>` | 200 full `batch_records` row + `system:"mes"`; unknown -> 404 |
| `/api/failure[?mode=timeout|schema|rate_limit]` | 503 `upstream unavailable`/200 `{"unexpected_schema":"v3","records":null}`/429; any other mode -> 200 `{"mode":"normal"}` |
| Logging | `log_message` suppressed -> no access log |

### BB-04 Gateway bridge (CW-04) - `app/gateway_bridge.py` (G: `gateway_bridge_sequence`, `gateway_inbox_*`, lib golden)

Sequence on shipped DB (inbox starts with 1 residue row): `--limit 50` -> accepted 50; again `--limit 50` (checkpoint offset 50) -> accepted 50; `--offset 0 --limit 50` -> accepted 0, duplicates 50; `--offset 0 --limit 200` -> accepted 25, duplicates 100 (received 125); next `--limit 50` from checkpoint -> received 0. Final: `gateway_inbox` 126 rows (125 distinct `external_ref` + the residue row), all `RECEIVED`; `gateway_checkpoints` `primary` -> 125; 7 stored events carry `schema_version 0.9` (accepted, not rejected - **[DEFECT]** contract unenforced). Library cases (lib golden): unknown `business_key` -> `invalid` (silently counted, event not stored); missing fields or non-dict -> `invalid`; duplicate `message_id` -> `duplicates` even if the key differs; `business_key` with SQL metacharacters -> `invalid` (parameterised). Unreachable source URL -> traceback, rc 1, checkpoint unchanged.

### BB-05 Partner feed reconcile (CW-05) - `app/partner_feeds.py --reconcile` (G: `partner_reconcile_sequence`, `partner_status_after_all`)

Shipped table: 8567 rows (statuses before: NEW / RETRY / REPLAY). Each run processes at most 1000 rows ordered by `ingest_ts, feed_id`. Ten consecutive runs on a copy gave: `{accepted,rejected,duplicate}` = (912,80,8), (921,71,8), (924,68,8), (925,65,10), (937,57,6), (924,70,6), (925,66,9), (931,64,5), (518,45,4), then all-zero (backlog exhausted after 9 productive runs). Final distribution: ACCEPTED 7917; REJECTED 586 (432 "schema/key validation", 154 "quantity out of range"); DUPLICATE 64 ("replayed source message"). Rule order: missing key or `schema_rev=='unsupported'` -> REJECTED; `REPLAY` -> DUPLICATE (no content comparison); `quantity < 0` -> REJECTED; else ACCEPTED. `status` is overwritten in place; **no row in `batch_runs` is written** (still 60). `policy_exceptions` are never read. `json.loads(raw_json)` is unguarded. **[DEFECT]** all as per RC-5/RC-6.

### BB-06 Vendor file-drop import (CW-06) - `app/historical_estate.py`

Idempotency key = first 24 hex of `sha256(file bytes)`. Shipped DB already holds import `d5f841003e666012a16a78b7` (`partner_export.csv`, 2400 rows, ACCEPTED), so re-importing `data/lake/tiny/partner_export.csv` returns `{"status":"already_imported","rows":0}`. After deleting both tables in a copy: first run `accepted` 2400 rows, second `already_imported`. Raw representation kept: 10 rows with blank amount are stored as `''`; 4 distinct tenants; no validation (G: `vendor_rows_after` [2400,10,4]).

### BB-07 Night-shift reconciliation (CW-07) - `legacy_batch/shift_reconciliation.py`

Reads `data/enterprise_legacy.sqlite3` directly (path hard-coded; no env override). `--limit 500`: `processed` 500, `flagged_count` 210, `by_tenant` AMER 131, APAC 120, EMEA 133, SOUTH 116; `--limit 100` -> flagged 53; `--limit 50` -> 3; `--limit 12500` -> flagged 5454. **[DEFECT]** the `LEFT JOIN policy_register ON region AND active=1` multiplies each object by 4-5 active policies per region (AU4, BR4, DE5, GB4, IN4, JP4, US5, ZA4), so the first 500 joined rows cover only **118 distinct objects** and per-tenant counts are row counts, not object counts. A row is flagged if status in {HOLD, REVIEW} or `value > threshold`. Output includes a `flagged_preview` of the first 12 rows (repeated object ids).

### BB-08 Month-end reconciliation (CW-08) - Java and SQL

* Java `ReconcileLegacy` (JDK 11 source launcher): `tiny` CSV -> `count=2390 total=10497082.12 eventTypes={batch_exception=597, capa_action=598, oos_lab=598, sop_change=597}`; `bundled` CSV -> `count=49800 total=218191169.74` (12,450 per type). 10 (tiny) / 200 (bundled) rows with blank amount are **silently skipped** (NumberFormatException swallowed); negative amounts (11 / 236) are summed as-is; no args -> usage on stderr, rc 2. An independent Python/`decimal` computation gives identical totals (10497082.12; 218191169.74), i.e. the float-accumulation risk is **latent, not manifested** on these files.
* SQL `legacy_reports.sql` query 1 (executed read-only on the shipped DB): 15 (region,status) rows ordered by `gross_amount`; sum of `gross_amount` = **742,956.61** vs true `SUM(cases.amount)` = **622,826.44** (+19.3 % inflation from `LEFT JOIN events`, RC-8 re-confirmed). `COUNT(DISTINCT c.id)` is correct, `SUM(c.amount)` is not. Query 2 (`vendor_file_rows` by kind/tenant) returns 16 rows of 132-173.

### BB-09 JavaScript policy consumer (CW-09) - `legacy_js/legacy_policy.js` (G: `js_policy_table`, `node_*`)

`threshold(region, year)` returns the archive `limit` for a matching (region, `effective_from` year-prefix) row, else **999999**. Archive covers only APAC/EMEA/AMER for 2022-2026 (APAC 15000, 17500, 20000, 22500, 25000 ... EMEA 16100 ... AMER 17200 ...). 17 of 32 probed (region,year) pairs fall to 999999, including **every probed year for `IN`** (an enterprise-estate region absent from the archive), and 2019/2021/2027. `legacyAllows(amount,...)` = `Number(amount) <= threshold*1.05`: `legacyAllows(27000,'APAC',2026)` false; 26250 true; 26250.01 false; negative and `null` -> true; `"abc"` -> false (NaN). Running with a different cwd fails (`ENOENT contracts/decision-policies-archive.json`). **[DEFECT]** (RC-4/DH-08).

### BB-10 Operational correlation report (CW-11)

`python -m app.operational_report` on the shipped DB: `parent_records` 125, `detail_records` 42, `parents_with_detail` 42, `parents_without_detail` 83, `ingested_source_messages` 1 (the residue row). On the 6,000/4326 regeneration: 6000 / 2000 / 2000 / 4000 / 1.

### BB-11 Operating baseline (CW-03) - `python -m app.baseline`

Shipped 125-case DB: `{"records":125,"open_cases":89,"urgent_cases":2,"mean_amount":4982.61,"sites":6,"hours_per_case":0.603}`. Alternative dataset (OD-02) regenerated as `generate --count 6000 --seed 4326 --reset`: `{"records":6000,"open_cases":4251,"urgent_cases":159,"mean_amount":4403.0,"sites":6,"hours_per_case":0.601}`. `open_cases` counts any status other than CLOSED (includes ESCALATED/REOPENED). `hours_per_case` is a ratio of independent random totals (A-04-01 refuted, OD-07) - cite only as a generator-bounded proxy.

### BB-12 Data provisioning and reproducibility (CW-12)

| Dataset | Reproduction command | Equals shipped? (table-level SHA-256 of sorted rows) |
|---|---|---|
| `legacy.sqlite3` base tables (cases, events, source_messages, operating_costs, materials, batch_records, deviations, lab_results, capa_actions, sop_versions) | `python -m app.generate --count 125 --seed 4100 --reset` | **Yes, all 10 tables identical** |
| same, `--count 125 --seed 4326` and `--count 6000 --seed 4326` (README/CI/run.sh) | | No (only `sop_versions` identical) - the README 6,000-case dataset is a different dataset (OD-02 alternative) |
| `partner_feeds`, `reference_versions`, `policy_exceptions`, `upstream_outages`, `batch_runs` | `python -m app.partner_feeds` (defaults count 8500, seed 20261017) on the 125-case DB | **No** (all five differ): shipped feeds reference case ids from a larger (6,000) case table, i.e. were generated against another DB state; **not reproducible from the shipped 125-case DB** (RC-7 orphan finding explained) |
| `enterprise_legacy.sqlite3` | `python -m app.enterprise_legacy` (12,500 rows, seed 20261017) | **Yes, all 12 tables identical** |
| `lake/tiny` (CSV, events, reference, finance, manifest) | `python -m app.historical_fixture --tier tiny --destination <dir>` | **Yes** (manifest, CSV bytes, all event partitions, both DBs) |
| `data/archive_documents` (421 files) | `python -m app.archived_documents` | **Yes** (byte-identical, 421 files) |
| `data/documents/source_documents.jsonl` | `python -m app.generate_documents` | **Yes** (byte-identical) |
| `vendor_file_*`, `gateway_inbox` (1 row), `lake/bundled` | no generator path evidenced for the shipped state of vendor/inbox; `bundled` tier generator exists (`historical_fixture --tier bundled`) but was not run (50k rows) | [Unknown] - not verified |

`app.workshop_check` on the shipped DB: `ok: true` with counts cases 125, events 145, source_messages 15, partner_feeds 8567, reference_versions 180, policy_exceptions 224, upstream_outages 72, batch_runs 60; on an empty DB: `ok: false`, rc 1.

## Evidence References

Golden files: `evidence/golden/api_golden_run1.json` (sha256 `c6db0a43...cd13`), `batch_golden_run1.json` (`1460b050...f591`), `lib_golden_run1.json` (`52b0bf6c...7b80`; full hashes in `evidence/SHA256SUMS-evidence.txt`). Capture scripts in `evidence/scripts/`. Determinism: second run files compared with `cmp` (identical). Mutation replay: `evidence/analysis/golden_mutation_replay_summary.txt`.

## Assumptions

- A-07-03: The shipped 125-case DB is the as-found baseline (OD-02, provisional - Dinesh may override). All golden values depend on it. If the 6,000-case dataset is chosen, re-run the three capture scripts after `generate --count 6000 --seed 4326 --reset` in a sandbox and store as a second golden set (baseline numbers for `app.baseline` already recorded above).
- A-07-04: Dates/timestamps in goldens are data (fixed in the DB), not wall-clock; `gateway_bridge` writes `received_at`/`last_sync` with wall-clock, which are **not** compared by the goldens (only counts).
- A-07-05: Normalisation required by a future comparison harness: ephemeral ports, sandbox absolute path inside `generate_documents` stdout, wall-clock fields.

## Unknowns

- U-07-03: Which of the three approval rules is authoritative (RC-3/RC-4, U-16); the baseline preserves all three.
- U-07-04: Behaviour of the workshop/stress tiers and Docker/Compose runtime (not run).
- U-07-05: Behaviour under concurrent writers (API + bridge + reconcile on the same SQLite file); not characterised (single-process captures only).

## Unresolved Issues

- Golden files are **data**, not yet an executable regression suite; converting them into a runnable harness is the first deliverable of Stage 15 prep (CT plan, `characterization-test-plan.md`).
- The `gateway_inbox` residue row (TQ-02) is part of the baseline counts (126 after full ingest); a decision is needed whether the clean baseline excludes it.

## Residual Risks

- R-07-02: Golden outputs encode defects (RC-4, RC-8, BB-07 row multiplication). Blindly "preserving" them in a modernised system would carry known-wrong numbers forward; every [DEFECT] needs an explicit Stage 14/15 disposition (preserve-for-parity vs fix-with-approval).
- R-07-03: Behaviour that depends on external human decisions (batch disposition) cannot be baselined - it does not exist in the code (CW-14).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial behaviour baseline from sandbox execution. |
