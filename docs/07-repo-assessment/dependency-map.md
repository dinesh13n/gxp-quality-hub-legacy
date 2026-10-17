---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "dependency-map.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["pyproject.toml", "Dockerfile", "compose.yaml", ".github/workflows/verify.yml", "app/*.py", "services/source_gateway/server.py", "legacy_batch/shift_reconciliation.py", "legacy_java/ReconcileLegacy.java", "legacy_js/legacy_policy.js", "scripts/*.py", "docs/07-repo-assessment/evidence/analysis/static_analysis.json", "docs/05-current-state/dependency-hotspots.md", "docs/00-preflight/discovery/technology-inventory.md"]
supersedes: "none"
---
## Summary

**External dependencies: none beyond language runtimes.** All 35 Python files import only the standard library (`sqlite3`, `http.server`, `urllib`, `json`, `csv`, `random`, `hashlib`, `email`, `unittest`, ...); Java uses `java.nio`/`java.util`; JavaScript uses Node built-in `fs`. There is no `requirements.txt`, lock file, `package.json` or `pom.xml`. Dependency risk is therefore concentrated in **runtime versions** (Python 3.10 vs 3.12; JDK 11+; Node 18+), **implicit internal coupling** (shared SQLite files, repo-relative paths, cwd-relative paths) and **data-file contracts** (JSON/CSV). Internal module coupling is low in count (hub: `app.store`, imported by 11 of 17 app modules) but high in implicitness.

## Findings

### External / platform dependencies

| ID | Dependency | Version evidence | Used by | Status | Class | Confidence |
|---|---|---|---|---|---|---|
| DM-01 | Python | `pyproject.toml` `>=3.10`; CI/Dockerfile 3.12; sandbox 3.10.12 | all `.py` | 3.10 reaches end-of-life Oct 2026 (public CPython schedule; [Inference] from release calendar, not repository evidence); 3.12 supported | [Verified Fact] (versions) / [Inference] (EOL) | Medium |
| DM-02 | SQLite (via `sqlite3`) | bundled with CPython; version not pinned | all data access | Single-file DB, `PRAGMA foreign_keys=ON` set per connection in `store.connect`, but not in `enterprise_legacy`/`historical_fixture`/`historical_estate` direct connections | [Verified Fact] | High |
| DM-03 | JDK | source-launcher `java File.java` works on OpenJDK 11.0.32; no `javac` on PATH; no build file | `legacy_java/ReconcileLegacy.java` | Requires JDK >= 11 (single-file source launch); not in CI or Docker | [Verified Fact] | High |
| DM-04 | Node.js | v22.23.2; no `package.json`; `require('fs')` only | `legacy_js/legacy_policy.js` | not in CI or Docker | [Verified Fact] | High |
| DM-05 | Docker / Compose | `Dockerfile` (python:3.12-slim), `compose.yaml` | optional | not installed on device, never executed (U-09) | [Verified Fact] / [Unknown] | High |
| DM-06 | GitHub Actions | `actions/checkout@v4`, `actions/setup-python@v5` | CI | never run (U-20); actions pinned by major tag, not SHA | [Verified Fact] | High |
| DM-07 | SQL Server / Oracle | mentioned in `docs/interface-notes.md` as historical | none in code | not a dependency | [Verified Fact] (absence) | High |
| DM-08 | Third-party Python/JS/Java libraries | none | - | **No supply-chain surface**; no SBOM entries beyond runtimes; vulnerability scanning of libraries n/a | [Verified Fact] | High |

### Internal module dependency graph (static, from AST)

| Module | Imports (internal) | Fan-in |
|---|---|---|
| `app.store` | - | 11 app modules (baseline, domain_data, enterprise_data, gateway_bridge, generate, historical_estate, integration, operational_report, partner_feeds, server, workshop_check) + 5 test modules |
| `app.legacy_logic` | - | 2 (baseline, server) + test_workflow |
| `app.enterprise_data` | store | 3 (generate, generate_documents, server) |
| `app.partner_feeds` | store | 2 (server, workshop_check) |
| `app.generate` | domain_data, enterprise_data, store | 0 in app (tests only) |
| `app.server` | enterprise_data, legacy_logic, partner_feeds, store | 0 |
| standalone (no internal imports): `enterprise_legacy`, `historical_fixture`, `archived_documents`, `shift_reconciliation`, `services.source_gateway.server`, `scripts/*` | - | tests only |

No import cycles. `app.generate` imports submodules lazily inside the function (circularity avoidance via function-local imports, `app/generate.py` L16, L43-45).

### Implicit (non-import) dependencies - the real coupling

| ID | Dependency | Mechanism | Evidence | Impact | Class |
|---|---|---|---|---|---|
| DM-10 | `data/legacy.sqlite3` shared by API, bridge, reconcile, importer, baseline, report, gateway (ro), smoke test | file path via `LEGACY_DB` (import-time) or `parents[1]/data` | `app/store.py` L4; `services/source_gateway/server.py` L7; `scripts/smoke.py` L7 (hard-coded path, **ignores `LEGACY_DB`**) | Integration bus; `LEGACY_DB` override incomplete (`smoke.py` verifies the default DB while the server it spawns may use another) | [Verified Fact] |
| DM-11 | `data/enterprise_legacy.sqlite3` | hard-coded `ROOT/data/...` in `enterprise_legacy.py` L4 and `shift_reconciliation.py` L5 | | no env override; test-only `db=` parameter | [Verified Fact] |
| DM-12 | Repo-relative `data/` writers: `archived_documents.py` L6-7 (deletes all files in `data/archive_documents`), `generate_documents.py` L6, `historical_fixture.py` L13, `enterprise_legacy.py`, `shift_reconciliation.py` | `Path(__file__).resolve().parents[1]` | WB-F1 | destructive when run in the working tree | [Verified Fact] |
| DM-13 | cwd-relative: `legacy_js/legacy_policy.js` reads `contracts/decision-policies-archive.json` relative to the process cwd; Java and Node commands need repo-root cwd for the documented data paths | | golden `node_cwd_other` rc 1 | breaks when launched from another directory | [Verified Fact] |
| DM-14 | JSON configuration read at import: `domain.json` (server), `domain-profile.json` (partner_feeds), `integration/source-gateway.json` (bridge, report, gateway) | module-level `json.loads(read_text())` | | import fails if file missing; config changes need restart | [Verified Fact] |
| DM-15 | Network: bridge -> gateway HTTP (`SOURCE_URL`, default `http://127.0.0.1:8090`, `urlopen` timeout 5 s, no retry) | | `app/gateway_bridge.py` L29, L36 | only runtime network dependency; `urlopen` accepts `file:`/`ftp:` schemes if the URL is user-supplied | [Verified Fact] |
| DM-16 | Table-name coupling through config: `parent_table=batch_records`, `parent_key=batch_id`, `child_table=deviations` interpolated into SQL (`gateway_bridge`, `operational_report`, `gateway server`) | string concatenation | `integration/source-gateway.json` | swapping domain requires editing JSON plus keeping schema aligned; allow-list absent (config is trusted) | [Verified Fact] |
| DM-17 | Cross-language data contracts: partner CSV columns (`tenant,external_id,kind,region,amount,currency,recorded_at,schema_version,status,language,reference_id`) consumed by Java by **positional index** (`parts[4]` amount, `parts[2]` kind); `vendor_file_rows` by named columns | | `ReconcileLegacy.java`; `historical_estate.py` | column reorder silently breaks Java totals | [Verified Fact] |
| DM-18 | Policy archive JSON consumed by JS only; Python rules do not read it | | RC-4 | duplicates policy by hand | [Verified Fact] |

### Test/CI dependencies

CI runs `unittest` before data generation and imports tests that depend on the default DB (TQ-01). No lint/type/security steps. `verify.sh` depends on `sh` and `python` (not `python3`) being on PATH.

## Evidence References

`evidence/analysis/static_analysis.json` (`internal_imports`); `grep` of imports; files cited per row; `baseline-behaviour.md` BB-08/09.

## Assumptions

- A-07-10: Runtime versions required = those named in README/Dockerfile/CI; no minimum for Java/Node is documented, so the observed working versions are recorded only.

## Unknowns

- Minimum supported JDK/Node; whether Python 3.12 behaviour differs (TR-12).

## Unresolved Issues

- Hard-coded paths (DM-10..DM-13) require a decision on a configuration strategy in Stage 14 (not changed here).

## Residual Risks

- R-07-08: Python 3.10 end-of-life [Inference] makes the 3.10 baseline short-lived; Stage 15 should baseline on 3.12.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial dependency map. |
