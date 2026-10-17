---
stage: "0A — Pre-Flight Repository & System Orientation"
artifact: "system-landscape.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/server.py", "services/source_gateway/server.py", "app/gateway_bridge.py", "app/partner_feeds.py", "app/historical_estate.py", "legacy_batch/shift_reconciliation.py", "legacy_java/ReconcileLegacy.java", "legacy_js/legacy_policy.js", "compose.yaml", "docs/service-boundaries.md", "docs/source-system-landscape.md", "docs/source-systems-and-constraints.md", "domain-profile.json", "integration/source-gateway.json"]
supersedes: "none"
---
## Summary

The estate simulates one core legacy application plus a ring of satellite processes and simulated upstream systems. All components run locally against SQLite files or flat files; **no component contacts any real external system**. There is no evidence that any component runs in a real production environment.

## Findings

### Component catalogue

| ID | Component | Type | Entry point | Primary store | Status signal | Class |
|---|---|---|---|---|---|---|
| SL-01 | **Legacy Quality API** | Long-running HTTP service (GET-only), port 8080 | `python -m app.server` (`app/server.py` L62-66); `run.sh`; Compose `legacy` | `data/legacy.sqlite3` via `LEGACY_DB` (`app/store.py` L4) | Started and passed smoke test in an isolated copy (`scripts/smoke.py` → `{"api":"pass","database":"pass"}`) | [Verified Fact] |
| SL-02 | **Source Gateway** (simulated MES / LIMS / QMS upstream) | Long-running HTTP service, port 8090, opens DB `mode=ro` | `python -m services.source_gateway.server`; Compose `source-gateway` | reads `batch_records` from `legacy.sqlite3` (`integration/source-gateway.json` `parent_table`) | Started in isolated copy; `/health` OK | [Verified Fact] |
| SL-03 | **Gateway Bridge** (ingestion job) | One-shot pull job with checkpoint | `python -m app.gateway_bridge` (L35-41); Compose `bridge` (`restart: "no"`) | writes `gateway_inbox`, `gateway_checkpoints` | Ran in isolated copy: 50 accepted per pull | [Verified Fact] |
| SL-04 | **Partner Feed staging & reconciliation** | CLI batch (generate / `--reconcile`) | `python -m app.partner_feeds` | `partner_feeds`, `reference_versions`, `policy_exceptions`, `upstream_outages`, `batch_runs` in `legacy.sqlite3` | Ran `--reconcile` in isolated copy: `{"accepted":912,"rejected":80,"duplicate":8}`; mutates status in place (L70) | [Verified Fact] |
| SL-05 | **Vendor file-drop import** | CLI batch (CSV → DB) | `python -m app.historical_estate <csv>` | `vendor_file_imports`, `vendor_file_rows` | Shipped DB already contains 1 import of `partner_export.csv` (2,400 rows) | [Verified Fact] |
| SL-06 | **Night-shift reconciliation** | CLI batch, reads a *separate* DB directly | `python -m legacy_batch.shift_reconciliation` | `data/enterprise_legacy.sqlite3` (12 tables) | Ran in isolated copy (500 processed / 210 flagged) | [Verified Fact] |
| SL-07 | **Java month-end reconciliation** | CLI batch (JVM) | `java ReconcileLegacy <csv>` | reads `data/lake/*/partner_export.csv` | Ran via single-file launch: count=2390 of 2,400 rows (blank amounts silently skipped) | [Verified Fact] |
| SL-08 | **JavaScript policy consumer** ("legacy front-end approval thresholds") | Node CLI / module | `node legacy_js/legacy_policy.js` | reads `contracts/decision-policies-archive.json` | Ran: `{"threshold":25000,"example":false}` | [Verified Fact] |
| SL-09 | **Reporting & baseline** | CLI | `app.baseline`, `app.operational_report`, `sql/legacy_reports.sql` | `legacy.sqlite3` | `app.baseline` runs; SQL file not wired into any code | [Verified Fact] |
| SL-10 | **Synthetic data generators / fixtures** | CLI | `app.generate`, `app.domain_data`, `app.enterprise_data`, `app.enterprise_legacy`, `app.generate_documents`, `app.archived_documents`, `app.historical_fixture`, `ops/legacy_log_sampler.py` | all stores | Support tooling of the simulator, not business runtime | [Verified Fact] |
| SL-11 | **Ops / verification scripts** | CLI | `scripts/verify.sh`, `smoke.py`, `offline_inventory.py`, `verify_preloaded.py`, `rehearse_local.py`, `app.workshop_check` | read (mostly) | All ran green in isolated copy | [Verified Fact] |

### Simulated external / upstream systems (named in docs and config only)

| ID | System | Where named | Real integration? | Class |
|---|---|---|---|---|
| SL-12 | ElectronicBatchRecord (EBR/MES) | `domain-profile.json` `system`; `docs/partner-feed-operations.md` | No — simulated by SL-02 / generated data | [Verified Fact] |
| SL-13 | LIMS-QMS | `domain-profile.json` `other`; `docs/historic-decisions.md` (2023 migration) | No — simulated | [Verified Fact] |
| SL-14 | External partner gateway (5 partners: north/south/europe/asia/americas) | `app/partner_feeds.py` L10; `upstream_outages.system_name='PartnerGateway'` | No — generated rows | [Verified Fact] |
| SL-15 | SQL Server / Oracle "historical deployment" | `docs/interface-notes.md` L7 | Not present in code | [Verified Fact] (mention) / [Unknown] (whether it ever existed) |
| SL-16 | SharePoint / FILE_DROP / EMAIL / ECM document sources; ERP / CRM / SUPPLIER / REGULATOR providers | `app/enterprise_legacy.py` L41, L49 (values in generated data only) | No | [Verified Fact] |

### Relationships

- SL-01, SL-02, SL-03, SL-04, SL-05, SL-09 all share **one SQLite file** (`legacy.sqlite3`) as an integration database. [Verified Fact — `app/store.py` L4; `services/source_gateway/server.py` L7]
- SL-06 uses a **separate** database (`enterprise_legacy.sqlite3`) that no HTTP service exposes. [Verified Fact — `legacy_batch/shift_reconciliation.py` L5]
- SL-07 and SL-08 operate purely on files and share no runtime with the Python estate. [Verified Fact]
- The same business decision (approval / priority threshold) is implemented independently in SL-01 (`app/legacy_logic.py`), SL-06 and SL-08 with different values — see `workflow-overview.md` WF-06. [Verified Fact]
- [Inference] The source gateway (SL-02) publishes events *derived from the same DB the bridge writes back into*, so the "upstream" is circular in the simulator; in Compose the gateway reads the image copy `/opt/legacy/data/legacy.sqlite3` while the API and bridge use the volume copy `/var/lib/legacy/legacy.sqlite3` (`compose.yaml` L20-22 vs L6, L32-34).

## Evidence References

`app/server.py`, `app/store.py`, `services/source_gateway/server.py`, `app/gateway_bridge.py`, `app/partner_feeds.py`, `app/historical_estate.py`, `legacy_batch/shift_reconciliation.py`, `legacy_java/ReconcileLegacy.java`, `legacy_js/legacy_policy.js`, `compose.yaml`, `docs/service-boundaries.md`, `docs/source-system-landscape.md`. Execution evidence: isolated copy at `$HOME/fde_sbx/repo` on the device (outside the repo; DB regenerated there with `--count 6000 --seed 4326`).

## Assumptions

- A-03: The named upstream systems (EBR, LIMS-QMS, partner gateway) stand in for real systems the client would integrate with; their real contracts are not in scope of the repo. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-04: Which components (if any) are considered "operational" by the fictional client vs dormant (e.g. Java/JS consumers, `sql/legacy_reports.sql`). U-05: real deployment topology (single host? container host per `docs/interface-notes.md` 2023 entry?).

## Unresolved Issues

- No deployment evidence for any component beyond local/Compose descriptors; Compose itself is stated as "not executed in the release-building environment" (`PRELOADED_DATA.md` L30) and Docker is not installed on the inspection device.

## Residual Risks

- R-05 (shared integration DB couples all components), R-06 (divergent duplicated business rules). See `initial-risk-register.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 0A discovery draft (read-only inspection of commit `b126c56`). |
