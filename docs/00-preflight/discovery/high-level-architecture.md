---
stage: "0A — Pre-Flight Repository & System Orientation"
artifact: "high-level-architecture.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/server.py", "app/store.py", "services/source_gateway/server.py", "app/gateway_bridge.py", "compose.yaml", "Dockerfile", "run.sh", "environments/*.env.example", "docs/service-boundaries.md", "docs/interface-notes.md"]
supersedes: "none"
---
## Summary

Shape: a **shared-database integration** architecture. One SQLite file (`legacy.sqlite3`) is the hub for the API, the simulated upstream gateway, the ingestion bridge, partner-feed staging and reporting. A second, isolated SQLite estate (`enterprise_legacy.sqlite3`) is consumed only by a batch job. File-based consumers (Java, Node) sit outside both. All runtime boundaries are process boundaries on one host (or containers in Compose); there is no network boundary to any real external system.

## Findings

### Component view (as implemented)

```
                 (simulated upstream: MES / LIMS / QMS)
                 +--------------------------------------+
                 | Source Gateway  :8090  (read-only DB) |  services/source_gateway/server.py
                 +-------------------+------------------+
                                     | HTTP GET /api/events?offset&limit
                                     v
 +-------------------+     +--------------------+
 | Gateway Bridge    |---->| gateway_inbox /    |
 | (one-shot job)    |     | gateway_checkpoints|
 +-------------------+     +---------+----------+
                                     |
   Partner feed CLI ----------> +----v------------------------------------+      HTTP GET (no auth)
   (app.partner_feeds)          |  data/legacy.sqlite3  (shared hub DB)    |<------ Legacy Quality API :8080
   File-drop CLI -------------> |  cases, events, source_messages,         |        app/server.py
   (app.historical_estate)      |  operating_costs, materials, batch_*,    |
   Reporting CLIs <-------------|  deviations, lab_results, capa, sop, ... |
   (baseline, operational_rpt)  +------------------------------------------+

   legacy_batch.shift_reconciliation ---> data/enterprise_legacy.sqlite3 (12 tables, isolated)
   Java ReconcileLegacy ----------------> data/lake/*/partner_export.csv
   Node legacy_policy.js ---------------> contracts/decision-policies-archive.json
```

| ID | Finding | Class | Evidence | Impact | Risk | Confidence |
|---|---|---|---|---|---|---|
| HA-01 | API is a single-file `BaseHTTPRequestHandler` with an if-chain router; **GET only** (no `do_POST/PUT/DELETE`). Routes: `/health`, `/`, `/api/incidents`, `/api/metrics`, `/api/partners/<5 tables>`, `/api/domain/<4 tables>`, `/api/cases`, `/api/cases/<id>`. | [Verified Fact] | `app/server.py` L11-60 | Read-only API surface; all writes happen through CLIs/jobs. | Business decisions are not recorded through the API (see WF). | High |
| HA-02 | DB location is resolved **once at import time** from `LEGACY_DB` (`app/store.py` L4: module-level `DB = Path(os.environ.get(...))`). | [Verified Fact] | `app/store.py` L4 | Changing `LEGACY_DB` after `app.store` is imported has no effect — the root cause of the test-suite data overwrite (see `test-overview.md` TO-03). | High (data integrity of baseline) | High |
| HA-03 | GET handlers perform DDL: `/api/partners/*` calls `partner_feeds.init()` (CREATE TABLE IF NOT EXISTS) on every request; `main()` calls `setup()`. | [Verified Fact] | `app/server.py` L26-27, L63 | "API does not mutate core records" (`operations/runbook.md` L3) holds for rows but not for schema. | Low-Medium | High |
| HA-04 | Dynamic SQL table names concatenated into queries, guarded by allow-lists in the API (`app/server.py` L24-25, L37-38) and by config-file values elsewhere (`operational_report.py` L9-11, `gateway_bridge.py` L19, gateway L22). | [Verified Fact] | cited lines | Injection exposure is bounded by allow-list/config, not parameterisation. | Deeper review is Stage 7. | Medium |
| HA-05 | Runtime boundaries in Compose: `legacy` (8080, volume `legacy_data:/var/lib/legacy`), `source-gateway` (8090, `LEGACY_DB=/opt/legacy/data/legacy.sqlite3` — the **image copy**, no volume), `bridge` (writes to the volume copy, depends on both healthchecks, `restart: "no"`). | [Verified Fact] | `compose.yaml` L2-41 | [Inference] In Compose the gateway and the API read **different copies** of the DB; gateway output reflects image-build-time data while bridge writes go to the volume. | Medium | Medium |
| HA-06 | Image bootstrap copies `data/legacy.sqlite3` into the volume only if absent (`Dockerfile` L7). Because `data/*.sqlite3` is git-ignored, an image built from a fresh git clone would not contain it. | [Verified Fact] (descriptor + ignore rule) / [Inference] (behaviour) | `Dockerfile` L3, L7; `.gitignore` L1 | [Inference] `cp` would fail, the `sh -c` has no `set -e`, and `setup()` would create an empty DB → API serves 0 cases. Not executed (Docker unavailable). | Medium | Medium |
| HA-07 | Bind addresses: default `127.0.0.1` (`app/server.py` L63; gateway L43); `0.0.0.0` in Docker and staging/production-like env examples. | [Verified Fact] | `Dockerfile` L4; `environments/*.env.example` | Exposed without auth when containerised. | See security artifact. | High |
| HA-08 | `LOG_LEVEL` is defined in all three `environments/*.env.example` files but is **read by no code** (grep for `LOG_LEVEL`, `getenv`, `environ`). Environment variables actually read: `HOST`, `PORT`, `SOURCE_PORT`, `LEGACY_DB`, `SOURCE_URL`. | [Verified Fact] | grep output; `app/server.py` L63; `app/gateway_bridge.py` L36; gateway L7, L43 | Config descriptors overstate configurability. | Low | High |
| HA-09 | Environments named dev / staging / production-like exist only as `.env.example` files with ports/hosts; no IaC, no Kubernetes/Helm/Terraform, no deployment pipeline beyond CI tests. | [Verified Fact] | `environments/`; tree | No evidence of any deployed environment. | Production status unknown. | High |
| HA-10 | Historical architecture claims (2023 move "from a shared host to a container host"; SQL Server/Oracle in "historical deployment descriptions"; ADR-007 "architecture diagram still shows an obsolete service endpoint") are not backed by any artifact in the repo (no diagram, no DB driver). | [Verified Fact] (claims exist) / [Unknown] (truth) | `docs/interface-notes.md` L7, L12; `docs/decisions/ADR-archived-007.md` | Architecture documentation is incomplete and partly obsolete. | Medium | High |

## Evidence References

`app/server.py` L1-66; `app/store.py` L1-19; `services/source_gateway/server.py` L1-44; `app/gateway_bridge.py` L1-42; `compose.yaml`; `Dockerfile`; `environments/dev.env.example`, `staging.env.example`, `production-like.env.example`; `docs/decisions/ADR-archived-007.md`.

## Assumptions

- A-05: The Compose topology is the closest available proxy for the "production-like" runtime. Confirm: Engagement lead (Dinesh Naik), Stage 0B/5.

## Unknowns

- U-05 real deployment topology; U-08 the "obsolete service endpoint" referenced by ADR-007; U-09 whether Compose actually starts end-to-end (needs a Docker-enabled host).

## Unresolved Issues

- HA-05/HA-06 behaviours are inferred from descriptors and not executed.

## Residual Risks

- R-05 shared-DB coupling; R-07 Compose data divergence / empty-DB start. See `initial-risk-register.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 0A discovery draft (read-only inspection of commit `b126c56`). |
