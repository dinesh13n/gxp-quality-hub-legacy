---
stage: "5 — Discover Current Process & Brownfield Landscape"
artifact: "brownfield-inventory.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/*.py", "services/source_gateway/server.py", "legacy_batch/shift_reconciliation.py", "legacy_java/ReconcileLegacy.java", "legacy_js/legacy_policy.js", "sql/legacy_reports.sql", "scripts/*", "ops/legacy_log_sampler.py", "tests/*.py", "docs/00-preflight/discovery/technology-inventory.md", "docs/00-preflight/discovery/repository-overview.md", "git log (read-only)"]
supersedes: "none"
---
## Summary

Inventory of legacy components as found (baseline commit `a6eb4e8`, tag `baseline-as-found`; HEAD at Stage 5 start `429bd26`). The estate is small: **~850 lines** across Python (app/services/batch/scripts/tests), one Java file (16 lines), one JavaScript file (7), one SQL file (6). Age is not evidenced by version control (git history starts 2026-10-17 with the import); age statements come only from `docs/legacy-operations-history.md` (2018, 2020, 2022...) and are [Verified Fact] only as claims. Business logic is spread over five languages/runtimes with no shared library.

## Findings

### BI-A. Component inventory

| ID | Component | Path | Lines | Runtime | Role in process | Tests | Coupling / fragility | Class |
|---|---|---|---|---|---|---|---|---|
| BC-01 | HTTP API | `app/server.py` | 66 | Python stdlib `http.server` | Step 3 read access | `scripts/smoke.py` (health + 1 call) only; no route-level tests | `ThreadingHTTPServer`, no auth; f-string-free but table names concatenated from an allow-list (safe); DDL on read path (`init()`) | [Verified Fact] |
| BC-02 | Decision logic | `app/legacy_logic.py` | 8 | Python | D-03/D-04 | `tests/test_workflow.py` tests `priority` for 2 inputs; `manual_review_required` untested | Constants hard-coded (50,000) | [Verified Fact] |
| BC-03 | Store | `app/store.py` | 19 | Python + SQLite | Shared DB, DDL for 4 core tables | indirect | `LEGACY_DB` env; module-level path; `PRAGMA foreign_keys=ON` | [Verified Fact] |
| BC-04 | Generators | `app/generate.py`, `domain_data.py`, `enterprise_data.py`, `enterprise_legacy.py`, `generate_documents.py`, `archived_documents.py`, `historical_fixture.py`, `historical_estate` (importer), `ops/legacy_log_sampler.py` | ~300 | Python | Produce *all* data (no real source exists) | `test_workflow`, `test_domain`, `test_enterprise*`, `test_historical_fixture` | **Process evidence is generator output**; `generate.py --reset` drops tables | [Verified Fact] |
| BC-05 | Gateway bridge | `app/gateway_bridge.py` | 42 | Python | IO-01 | `tests/test_source_gateway.py` | No retry/backoff; drops invalid | [Verified Fact] |
| BC-06 | Source gateway | `services/source_gateway/server.py` | 44 | Python | Upstream simulator | `tests/test_source_gateway.py` | Access log disabled; failure modes via query param | [Verified Fact] |
| BC-07 | Partner feeds | `app/partner_feeds.py` | 75 | Python | IO-03 reconcile | `tests/test_partner_feeds.py` (no test names `reconcile`; grep) | In-place status mutation; `json.loads(raw_json)` without try - one malformed row aborts the whole run [Inference] | [Verified Fact] / [Inference] |
| BC-08 | Vendor file drop | `app/historical_estate.py` | 23 | Python | IO-04 | none (grep) | No validation | [Verified Fact] |
| BC-09 | Source adapter | `app/integration.py` | 8 | Python | IO-05 | `test_workflow.test_feed_parser` (type check only) | Contract unenforced | [Verified Fact] |
| BC-10 | Night-shift reconciliation | `legacy_batch/shift_reconciliation.py` | 18 | Python | D-06 | `tests/test_enterprise_legacy_v6.py` references it | Row multiplication by LEFT JOIN; reads second DB by repo-relative path (`ROOT/'data'`) | [Verified Fact] |
| BC-11 | Month-end reconciliation | `legacy_java/ReconcileLegacy.java` | 16 | Java (single-file launch) | Step 5 totals | none | `double`, silent skip, naive CSV split (`split(",")` breaks on quoted commas) [Inference]; no build file (no pom/gradle) | [Verified Fact] |
| BC-12 | Policy consumer | `legacy_js/legacy_policy.js` | 7 | Node | D-05 | none | Reads archive JSON via cwd-relative path; default limit 999,999 | [Verified Fact] |
| BC-13 | SQL reports | `sql/legacy_reports.sql` | 6 | SQL | Month-end | none | Not referenced by any code; join inflates sums [Inference] | [Verified Fact] |
| BC-14 | Baseline/report CLIs | `app/baseline.py`, `app/operational_report.py` | 13 / 15 | Python | Step 5 | `test_baseline`, `test_source_gateway` | `baseline()` count-based, no time dimension | [Verified Fact] |
| BC-15 | Verification scripts | `scripts/*`, `app/workshop_check.py`, `.github/workflows/verify.yml` | ~100 | sh/Python | Release gate (local+CI) | self | CI generates 6,000-case DB (a different dataset than shipped 125) | [Verified Fact] |
| BC-16 | Config/contracts | `domain.json`, `domain-profile.json`, `integration/*.json`, `contracts/decision-policies-archive.json`, `environments/*.example`, `compose.yaml`, `Dockerfile` | - | JSON/YAML | Config | none | Policy archive consumed only by JS | [Verified Fact] |
| BC-17 | Data assets | `data/legacy.sqlite3`, `data/enterprise_legacy.sqlite3`, `data/lake/`, `data/archive_documents`, `data/documents` | - | files | Stores | see `system-landscape.md` SY-B | git-ignored (local-only) per engagement context | [Verified Fact] |
| BC-18 | Operational docs | `operations/runbook.md` (3 lines), `operations/baseline-evidence.md`, `operations/incidents/INC-2025-014.md`, `docs/*.md` (16 historical/context files) | - | markdown | Only process documentation | n/a | Runbook has no step-by-step procedures, no roles, no escalation | [Verified Fact] |

### BI-B. Test coverage of process-relevant behaviour

7 test files, ~21 test methods (counted `def test`); behaviour **without any automated test**: `reconcile()` rules, `historical_estate.import_csv`, `manual_review_required`, `ReconcileLegacy`, `legacy_policy.js`, `legacy_reports.sql`, all API routes except through `smoke.py` [Verified Fact, grep by name]. Characterisation tests do not exist for any of the three duplicated approval rules.

### BI-C. Brownfield characteristics that matter for later stages

- [Verified Fact] **No dependency manifest** for Python beyond `pyproject.toml` (name/version/requires-python only); Java and Node have none; stdlib-only code.
- [Verified Fact] Several modules write repo-relative `data/` paths (OD-03a) - running anything in the working tree mutates evidence.
- [Verified Fact] Planted instruction-like strings sit in data (86 feed rows, 1-in-1399 enterprise evidence notes, lake events `source_claim`, quoted in `docs/00-preflight/discovery/integration-overview.md` IO-15); treated as data.
- [Inference] The estate is a *simulator of* a legacy estate: component sizes (7-75 lines) are far below what the described business scope (GxP batch disposition) would need; the real legacy logic the client runs is likely not in this repo (A-05-01).

## Evidence References

`wc -l` over all source files (852 lines total incl. tests); `grep -ln` of test files for component names; `git log --format` (6 commits before Stage 5, first = import `a6eb4e8`); `docs/00-preflight/discovery/technology-inventory.md`; file reads cited per row.

## Assumptions

- A-05-07: Line counts and test grep are a sufficient proxy for size/coverage at discovery depth; Stage 7 will measure coverage by execution. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-05-13 Actual age and change history of each component (no VCS history before 2026-10-17). U-05-14 Which components, if any, have owners.

## Unresolved Issues

- Ownership is unrecorded for every component (no CODEOWNERS, no owner fields) [Verified Fact: `ls -a` shows none].

## Residual Risks

- Behaviour duplicated in Python/Java/JS/SQL with no characterisation tests - any change in Stages 14+ risks silent divergence.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 5 discovery draft (read-only; no application code executed; SQLite opened `mode=ro&immutable=1`). |
