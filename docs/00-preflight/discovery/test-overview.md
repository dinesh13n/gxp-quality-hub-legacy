---
stage: "0A — Pre-Flight Repository & System Orientation"
artifact: "test-overview.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["tests/*.py", "scripts/verify.sh", "scripts/smoke.py", "scripts/offline_inventory.py", "scripts/rehearse_local.py", "app/workshop_check.py", ".github/workflows/verify.yml", "app/store.py", "isolated-copy test runs"]
supersedes: "none"
---
## Summary

There are 15 `unittest` tests in 7 modules plus 5 verification scripts. In an isolated copy all 15 tests pass (0.78 s), smoke passes, and inventory reports ready. Tests are **characterisation / fixture-integrity** checks (counts, FK integrity, idempotent insert) — there are no HTTP API tests, no tests of reconciliation outcomes, JS, Java or SQL. Critically, **running the suite mutates and shrinks the default database** (see TO-03). Coverage measurement tooling is absent.

## Findings

| ID | Finding | Class | Evidence | Impact | Risk | Confidence |
|---|---|---|---|---|---|---|
| TO-01 | Test inventory: `test_domain.py` (1 test: material/batch counts + FK), `test_enterprise.py` (2: domain tables populated, FK), `test_enterprise_legacy_v6.py` (2: enterprise generator reproducibility + shift_reconciliation counts), `test_historical_fixture.py` (1: tiny tier counts), `test_partner_feeds.py` (2: profile contract, tables exist), `test_source_gateway.py` (3: report relations, idempotent ingest, invalid rejected), `test_workflow.py` (4: counts, baseline, 2 priority asserts, feed parser returns list). | [Verified Fact] | `tests/*.py` | Thin behavioural coverage; `priority` has 2 asserts, `manual_review_required` none; partner reconcile rules untested; API routes untested by unit tests. | Medium | High |
| TO-02 | Result in isolated copy: `Ran 15 tests ... OK`; `scripts/smoke.py` → `{"api":"pass","database":"pass"}`; `scripts/offline_inventory.py` → `ready: true`; `app.workshop_check` → `ok: true`. | [Verified Fact] | device run in `$HOME/fde_sbx/repo` (copy, `.git` removed) | Suite is green. | Green ≠ correct (DATA_READINESS.md L27 says so). | High |
| TO-03 | **Test isolation defect**: `tests/test_enterprise.py` L2 imports `app.store` at discovery time, fixing `DB` to `data/legacy.sqlite3` (`app/store.py` L4). `test_domain`/`test_workflow` later set `LEGACY_DB` to a temp file, which is ignored, then call `generate(n, 4100, reset=True)` on the real DB. Reproduced: 6,000 cases → 125 after one suite run. `test_source_gateway` also inserts `CHECK-batch_quality` into the real `gateway_inbox`; `test_enterprise`/`test_source_gateway` depend on whatever data the earlier tests left. | [Verified Fact] (reproduced) | isolated-copy run; `tests/test_workflow.py` L5-7; `tests/test_domain.py` L5-7; `tests/test_source_gateway.py` L13-15 | Tests are order-dependent and destructive; documented preflights (`PRELOADED_DATA.md`, `DATA_READINESS.md`, `scripts/verify.sh`) instruct running them against the preloaded data. | **Critical** for baseline preservation | High |
| TO-04 | Test temp-dir cleanup: because the temp DB is never used, `tmp.cleanup()` removes an empty dir; the real DB keeps test residue. | [Inference] from TO-03 | same | — | Low | High |
| TO-05 | CI (`verify.yml`) runs `unittest` **before** `generate --reset` and `baseline`; on a fresh clone (no DB) the tests themselves create the DB. No coverage, lint, type-check, security scan, Java/Node steps. No evidence CI has ever executed (no remote, no run logs). | [Verified Fact] (file) / [Unknown] (execution) | `.github/workflows/verify.yml` L11-13 | CI gate is weak. | Medium | High |
| TO-06 | Verification scripts: `scripts/verify.sh` (workshop_check → unittest → smoke), `offline_inventory.py` (read-only, URI `mode=ro`, checks integrity/FK/manifest counts/SHA-256), `verify_preloaded.py` (wraps inventory), `rehearse_local.py` (integrity/FK on 2 DBs), `app.workshop_check` (asserts required tables non-empty; also runs DDL via `init()`). | [Verified Fact] | cited files | Inventory checks presence/integrity, **not** expected row counts for `legacy.sqlite3`, so a 125-case DB passes as "ready". | Medium | High |
| TO-07 | No API contract tests, no tests for `/api/partners/*` and `/api/domain/*` pagination, no tests for gateway failure modes (`/api/failure`), no performance tests despite `workshop`/`stress` tiers. | [Verified Fact] (absence) | tree; grep | Behaviour baseline for Stage 7 must be built by characterisation. | Medium | High |
| TO-08 | No test or doc asserts the injection-like strings are handled as data. | [Verified Fact] (absence) | grep tests | — | Medium (future AI) | High |

## Evidence References

`tests/` (7 files, 15 tests); `scripts/verify.sh`; `scripts/smoke.py` L1-25; `scripts/offline_inventory.py` L1-35; `.github/workflows/verify.yml`; isolated-copy command outputs (`Ran 15 tests in 0.784s OK`; post-suite counts `cases 125 batch 125`).

## Assumptions

- None beyond A-02 (baseline dataset identity).

## Unknowns

- U-20 whether CI has ever run; U-21 intended test data isolation design.

## Unresolved Issues

- TO-03: Until resolved, **nobody should run `unittest`, `scripts/verify.sh`, `PRELOADED_DATA.md` or `DATA_READINESS.md` quick-starts in the engagement working tree** without first copying `data/`. Remediation is out of scope for 0A (no code changes); flag to Stage 0B (operating boundaries) and Stage 7.

## Residual Risks

- R-01 baseline destruction by test runs; R-13 low behavioural coverage. See `initial-risk-register.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 0A discovery draft (read-only inspection of commit `b126c56`). |
