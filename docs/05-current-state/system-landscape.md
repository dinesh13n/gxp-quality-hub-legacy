---
stage: "5 — Discover Current Process & Brownfield Landscape"
artifact: "system-landscape.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/system-landscape.md", "docs/00-preflight/discovery/technology-inventory.md", "compose.yaml", "Dockerfile", "run.sh", "pyproject.toml", "environments/production-like.env.example", ".github/workflows/verify.yml", "app/store.py", "app/server.py", "services/source_gateway/server.py", "scripts/offline_inventory.py", "data/lake/bundled/manifest.json", "data/legacy.sqlite3 (read-only)", "data/enterprise_legacy.sqlite3 (read-only)"]
supersedes: "none"
---
## Summary

Process-centred view of the systems the business process touches. Stage 0A (`docs/00-preflight/discovery/system-landscape.md`, SL-01..SL-16) is the component catalogue and is **not repeated**; this file re-projects it onto the process steps (P-A in `current-process-map.md`) and adds what 0A did not cover: data stores by role, deployment descriptors, which components are on the process path vs support tooling, and documented-vs-observed differences. Everything is local, synthetic, SQLite/file based; no component reaches a real external system [Verified Fact, 0A + grep for credentials/endpoints].

## Findings

### SY-A. Systems on the process path

| Process step | System | Role | Store | Evidence | Class |
|---|---|---|---|---|---|
| 1 Source production | Source Gateway (`services/source_gateway/server.py`, :8090, SL-02) | Simulated MES/LIMS/QMS publisher; derives events from `batch_records` | `legacy.sqlite3` read-only (opened `mode=ro`; path from env `LEGACY_DB`) | file; `integration/source-gateway.json` | [Verified Fact] |
| 1 | Partner feeds generator (`app.partner_feeds` generate) | Creates 8,000 NEW / 500 RETRY / 67 REPLAY rows in shipped DB (5 partners) | `partner_feeds` | read-only SQL | [Verified Fact] |
| 2 Integration | Gateway Bridge (SL-03), Partner reconcile (SL-04), Vendor file drop (SL-05), source-message adapter (`app/integration.py`) | Import and reconcile | same DB | files | [Verified Fact] |
| 3 Review/prioritise | Legacy Quality API (SL-01, :8080) | Read-only JSON; computes `priority` and `manual_review_required` on the fly | `legacy.sqlite3` | `app/server.py` | [Verified Fact] |
| 4 Decision | "Local systems" | — | — | `docs/business-context.md` | [Unknown] |
| 5 Monthly measures | `app.baseline`, `sql/legacy_reports.sql`, `ReconcileLegacy.java`, `shift_reconciliation.py`, JS policy consumer | Reporting and side-rule implementations | `legacy.sqlite3`, `enterprise_legacy.sqlite3`, `data/lake/*/partner_export.csv` | files | [Verified Fact] |

### SY-B. Data stores by role (all local files)

| Store | Content | Written by | Read by | Notes | Class |
|---|---|---|---|---|---|
| `data/legacy.sqlite3` (19 tables) | 125 cases, 145 events (125 CASE_CREATED + 20 STATUS_REVIEWED), 15 source_messages, 36 operating_costs; 125 batch_records, 42 deviations, 21 CAPA, 125 lab_results, 45 SOP versions; 8,567 partner_feeds; 60 batch_runs; 72 outages | generators; reconcile/bridge/historical_estate mutate it | API, bridge, gateway (ro), baseline | Single shared integration DB (R-05) | [Verified Fact] |
| `data/enterprise_legacy.sqlite3` (12,500 objects, 12 tables) | operational objects, state_history, evidence_events, workflow_tasks, access_audit, policy_register ... | `app.enterprise_legacy` | `shift_reconciliation` only; **no HTTP service exposes it** | Not part of OD-02 baseline | [Verified Fact] |
| `data/lake/{tiny,bundled}` | per-month event JSONL (100,000 events bundled), `finance.sqlite3` ledger (20,000), `reference.sqlite3` master data (480), 600 documents, `partner_export.csv` (50,000 rows) | `app.historical_fixture` | only `scripts/offline_inventory.py` and Java (tiny CSV) | No application consumes ledger/reference/events (grep: `lake` referenced only in generator and inventory script) | [Verified Fact] |
| `data/archive_documents`, `data/documents` | .eml/.html archive notes, `source_documents.jsonl` | generators | nothing | Orphaned content | [Verified Fact] |

### SY-C. Deployment and runtime descriptors

| Item | Observed | Class |
|---|---|---|
| Compose: `legacy`, `source-gateway`, `bridge` (one-shot, `restart: "no"`) | `legacy` and `bridge` share volume DB `/var/lib/legacy/legacy.sqlite3`; `source-gateway` reads `/opt/legacy/data/legacy.sqlite3` (image copy) - two copies of the "same" DB, so gateway never sees bridge writes | [Verified Fact] |
| Dockerfile | copies shipped DB into the volume only if absent; `python:3.12-slim`; no non-root user, no pinned dependencies (no requirements file; stdlib only) | [Verified Fact] |
| `run.sh` | generates 6,000 cases seed 4326 if DB missing (so the repo has two baselines: shipped 125 vs regenerated 6,000, OD-02) | [Verified Fact] |
| Environments | `dev/staging/production-like.env.example` contain only HOST/PORT/SOURCE_PORT/LOG_LEVEL; no secrets, no endpoints | [Verified Fact] |
| CI | `.github/workflows/verify.yml`: unit tests, generate 6,000 seed 4326, baseline; no deploy job | [Verified Fact] |
| Scheduling | **No scheduler** (cron, Airflow, systemd) anywhere; every batch job is a manually started CLI | [Verified Fact] (grep) |
| Auth / TLS | None on either HTTP service; `HOST` default 127.0.0.1 locally, 0.0.0.0 in container | [Verified Fact] |
| Observability | stderr access log on API; gateway log disabled; `ops/legacy_log_sampler.py` prints 300 *synthetic* log lines (not real logs) | [Verified Fact] |

### SY-D. Documented vs observed (landscape)

| ID | Documented | Observed | Class |
|---|---|---|---|
| SD-01 | `docs/interface-notes.md` mentions SQL Server/Oracle historical deployment | No driver, DSN or schema for either | [Verified Fact] (absence) |
| SD-02 | `docs/legacy-operations-history.md`: "migrated from spreadsheet approvals to the current service" (2018) | The current service has no approval function | [Verified Fact] |
| SD-03 | `docs/service-boundaries.md` describes service boundaries | Physically one process family sharing one SQLite file; boundaries are logical only | [Inference] |
| SD-04 | Compose implies a deployable topology | Not executed in release environment (`PRELOADED_DATA.md`), Docker not installed on inspection device | [Verified Fact] |

## Evidence References

`compose.yaml` L1-42; `Dockerfile`; `run.sh`; `environments/*.env.example`; `.github/workflows/verify.yml`; `scripts/offline_inventory.py` L5-20; table list and counts via read-only SQL on both SQLite DBs; `data/lake/bundled/manifest.json`; `grep -rn lake` over `app scripts services tests`.

## Assumptions

- A-05-05: Which components are "operational" at the fictional client is unknown; for Stage 6/7 all code under `app/`, `legacy_batch/`, `legacy_java/`, `legacy_js/` is treated as in scope (carries 0A U-04). Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-05-08 Real hosting, scheduling and operator of batch jobs. U-05-09 Whether lake finance/reference data is meant to feed any process step.

## Unresolved Issues

- Compose topology never executed; two-DB-copy behaviour is from reading the YAML [Verified Fact for the file, behaviour is an Inference].

## Residual Risks

- Shared SQLite integration DB with no concurrency design beyond `busy_timeout=15000` (`app/store.py`); unscheduled batch jobs imply operator-dependent timing.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 5 discovery draft (read-only; no application code executed; SQLite opened `mode=ro&immutable=1`). |
