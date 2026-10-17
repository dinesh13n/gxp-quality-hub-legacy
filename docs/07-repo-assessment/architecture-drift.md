---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "architecture-drift.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["README.md", "PRELOADED_DATA.md", "DATA_READINESS.md", "docs/service-boundaries.md", "docs/interface-notes.md", "docs/source-gateway.md", "docs/domain-contracts.md", "docs/partner-feed-operations.md", "docs/business-context.md", "operations/runbook.md", "domain.json", "domain-profile.json", "compose.yaml", "Dockerfile", "app/server.py", "app/workshop_check.py", "app/partner_feeds.py", "services/source_gateway/server.py", "docs/00-preflight/discovery/high-level-architecture.md", "docs/05-current-state/dependency-hotspots.md", "docs/07-repo-assessment/baseline-behaviour.md"]
supersedes: "none"
---
## Summary

There is **no formal architecture document or ADR set** in the repository (the "intended design" is spread across README, `docs/service-boundaries.md`, `interface-notes.md`, `source-gateway.md`, `partner-feed-operations.md`, the runbook and `domain*.json`). Drift is therefore measured as **documented intent vs observed behaviour**. 17 drift items were found (AD-01..AD-17); five are material to GxP-relevant behaviour (AD-01 decision recording, AD-02 "CRUD" API, AD-03 shared-state vs service boundaries, AD-05 test claims, AD-09 doc-led destructive commands). The system is a modular monolith-in-name: more than ten independently runnable entry points that integrate through shared SQLite files and hard-coded relative paths, not through the documented "service interfaces".

## Findings

| ID | Intended (source) | Observed | Class | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|---|
| AD-01 | Journey step 4 "case decisions are recorded in local systems"; `domain-assurance.md`: batch disposition requires authorised human review (`docs/business-context.md`; `docs/domain-assurance.md` L4) | No code records a decision; only generators write `cases`; API is GET-only (POST/PUT/DELETE -> 501, golden) | [Verified Fact] | Core GxP decision outside the system; nothing to preserve or audit | High | High | Where is it recorded? (A-07, U-17) |
| AD-02 | `docs/service-boundaries.md`: "Legacy API: synchronous CRUD and reporting" | Read-only reporting; no Create/Update/Delete | [Verified Fact] | Doc overstates capability | Medium | High | - |
| AD-03 | `docs/service-boundaries.md`: separate "services" (API, gateway, bridge, night-shift, Java, JS) | They are separate processes but integrate by sharing `data/legacy.sqlite3` (API, bridge, reconcile, importer, baseline, gateway read-only) and by reading each other's data files directly; night-shift reads `enterprise_legacy.sqlite3` bypassing any API; no contracts enforced between them | [Verified Fact] | Shared database is the integration bus (DH-01); schema changes ripple everywhere | High | High | - |
| AD-04 | `integration/source-contract-v1.json` declares `ref,status,schema_version` required | No code loads or validates it (`grep`: only the file itself); gateway events use a different shape (`message_id,business_key,system,...`); `0.9` and `unsupported` versions are accepted/handled ad hoc | [Verified Fact] | Contract is decorative | Medium | High | Which contract is current? |
| AD-05 | README: "`tests/` - existing characterization coverage"; PRELOADED_DATA: "unit tests" as readiness check | 47.9 % line coverage, 14/15 injected regressions undetected (`baseline-test-results.md`) | [Verified Fact] | Overstated assurance | High | High | - |
| AD-06 | `docs/interface-notes.md` and `GET /` list 5 routes | 9 further routes exist and are not advertised (`/api/partners/*` x5, `/api/domain/*` x4); `docs/source-gateway.md` documents gateway routes correctly | [Verified Fact] | Discoverability gap | Low | High | - |
| AD-07 | `operations/runbook.md`: "API process does not mutate core records" | True for `cases`; but every `/api/partners/*` request runs `partner_feeds.init()` DDL (CREATE TABLE/INDEX IF NOT EXISTS) and `setup()` DDL at start - schema mutation on a GET path. Also runbook says logs go to stderr; the gateway suppresses all logs | [Verified Fact] | Read path has side effects | Low | High | - |
| AD-08 | README quick start "`python -m app.generate --count 6000 --seed 4326 --reset`" + "All required default synthetic data is already included. No generation is needed" | The shipped DB is `generate --count 125 --seed 4100` (all 10 base tables identical), not 6,000/4326; the quick start would destroy the shipped DB; partner-feed tables in the shipped DB cannot be regenerated from the shipped 125 cases (BB-12) | [Verified Fact] | Two incompatible dataset definitions (OD-02) | High | High | Which is canonical? OD-02 provisional |
| AD-09 | PRELOADED_DATA.md: "Do not run any generator or reset command" yet its quick start runs `python -m unittest discover` | The test suite regenerates and overwrites the shipped DB when run from the working tree (TQ-01) | [Verified Fact] | Documentation-induced data loss | High | High | - |
| AD-10 | `docs/partner-feed-operations.md`: "partner upload -> batch staging -> reconciliation -> operational case and quality decision" | Reconcile only changes `partner_feeds.processing_status`; it never creates or updates a case; `policy_exceptions` never consulted; feed `ref_id` has no FK and 173 of 8,567 shipped feeds point to an existing case (98 % orphan, RC-7) | [Verified Fact] | The chain ends at staging | High | High | - |
| AD-11 | Compose topology: legacy + gateway + bridge | Gateway reads the **image-baked** DB (`LEGACY_DB=/opt/legacy/data/legacy.sqlite3`) while legacy/bridge use the **volume** DB (`/var/lib/legacy/...`) - two physical databases; Compose never executed (Docker absent) | [Verified Fact] (file) / [Unknown] (runtime) | Divergent data after first write | Medium | Medium | U-09 |
| AD-12 | `domain.json` `okstatus: "released"`, `business_measure: "batch quality cases reviewed"` | Neither value exists in any data or code path (status vocabulary has no `released`; no code computes the measure) | [Verified Fact] | Dead configuration | Low | High | - |
| AD-13 | One domain: names appear as "Pharma Quality", "Life Sciences - Pharma Quality Intelligence", "Life Sciences", "Pharma batch deviation and CAPA", "GMP quality deviation and batch review", "Pharma" | Six naming variants across `domain.json`, `domain-profile.json`, `integration/source-gateway.json`, generators, JS, Java | [Verified Fact] | Domain config copy-pasted per generator ("domain templating") | Low | High | - |
| AD-14 | Environment profiles dev/staging/production-like (`environments/*.env.example`) | Only `HOST`, `PORT`, `SOURCE_PORT` are read; `LOG_LEVEL` unused; no logging configuration; profile "production-like" binds 0.0.0.0 with no auth | [Verified Fact] | Profiles differ only in bind address | Medium | High | - |
| AD-15 | `pyproject.toml` (name/version/requires-python only) | No package layout, no entry points, no dependency lock, no build-system; code is run as `python -m app.x` from repo root, imports rely on cwd/`parents[1]` | [Verified Fact] | Not installable; path-coupled | Medium | High | - |
| AD-16 | README: Python 3.10+; CI and Docker use 3.12 | Only 3.10.12 exercised here; no matrix | [Verified Fact] | Runtime parity unknown | Low | High | - |
| AD-17 | Domain data model: batch -> deviation -> CAPA -> SOP (`enterprise_data.py`) vs workflow entity `cases` | The `cases` aggregate (API, priority, metrics) has no key to `batch_records`/`deviations`; two parallel data models of the same business (case vs batch quality) | [Verified Fact] | The domain model is split; the GxP entities have only read endpoints and no state logic | High | High | Which is the system of record? |

### Module boundary / layering view (observed)

```
 run.sh / python -m <module>  (10+ entry points, manual start)
   app.server (HTTP) -> app.store (SQLite, LEGACY_DB at import) ; app.legacy_logic ; app.partner_feeds.init ; app.enterprise_data.TABLES
   app.generate -> domain_data, enterprise_data -> store           (data origin)
   app.gateway_bridge -> store, integration/source-gateway.json    <- HTTP -> services/source_gateway/server.py -> sqlite (ro)
   app.partner_feeds -> store, domain-profile.json
   app.historical_estate -> store      app.integration -> store
   app.enterprise_legacy | app.historical_fixture | app.archived_documents | app.generate_documents   (no store; repo-relative data/)
   legacy_batch.shift_reconciliation -> enterprise_legacy.sqlite3 (hard-coded)
   legacy_java / legacy_js / sql -> files (CSV, JSON, DB) by cwd-relative path
```

There is no layering: HTTP handlers contain SQL, routing and rule invocation in one 50-line `do_GET` (cyclomatic complexity 28).

## Evidence References

Files cited per row; import graph from `evidence/analysis/static_analysis.json` (`internal_imports`); `baseline-behaviour.md` BB-02, BB-12; `grep -rn source-contract-v1` (only the JSON); feed/case orphan count by read-only SQL (`partner_feeds.ref_id IN (SELECT id FROM cases)` = 173 of 8,567).

## Assumptions

- A-07-09: "Intended architecture" = what README/docs state; no other design intent exists (confirm: Engagement lead (Dinesh Naik), Stage 14).

## Unknowns

- U-09 Compose runtime; U-17 decision recording location; real deployment topology (U-05).

## Unresolved Issues

- Which dataset is canonical (AD-08) - OD-02 provisional.

## Residual Risks

- R-07-07: Documentation still instructs destructive commands (AD-08, AD-09) until the docs or tests are corrected in a BUILD stage.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial drift analysis. |
