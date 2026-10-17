---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "technical-debt-register.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/*.py", "services/source_gateway/server.py", "legacy_batch/shift_reconciliation.py", "legacy_java/ReconcileLegacy.java", "legacy_js/legacy_policy.js", "sql/legacy_reports.sql", "tests/*.py", "scripts/*", "Dockerfile", "compose.yaml", ".github/workflows/verify.yml", "docs/07-repo-assessment/evidence/analysis/static_analysis.json", "docs/07-repo-assessment/baseline-test-results.md", "docs/07-repo-assessment/baseline-behaviour.md", "docs/06-root-cause/confirmed-root-causes.md"]
supersedes: "none"
---
## Summary

34 debt items (TD-01..TD-34). Effort is a relative engineering estimate in T-shirt sizes (S <= 1 day, M = 2-5 days, L = 1-3 weeks, XL > 3 weeks of one engineer) and is an **[Inference]** from code size (1,435 tracked non-doc lines; 818 Python lines), not a quote. "Type" distinguishes *defect-debt* (wrong or unsafe result), *design-debt*, *test-debt*, *doc-debt* and *ops-debt*. Disposition column proposes the stage that should decide; nothing is fixed in Stage 7. **Gating debt (must be handled before any refactor): TD-01, TD-02, TD-03, TD-04.**

## Findings

| ID | Debt item | Type | Evidence | Impact | Risk | Effort | Pri | Confidence | Route |
|---|---|---|---|---|---|---|---|---|---|
| TD-01 | Test suite mutates the real DB; order-dependent (180 vs 125 cases) | test/defect | `tests/test_enterprise.py` L2, `tests/test_source_gateway.py` L4, `app/store.py` L4; TR-01..05 | Baseline destruction; unreliable CI | High | S-M (harness) | P0 | High | Stage 14 plan, Stage 15 |
| TD-02 | Suite cannot detect regressions (47.9 % line, 14/15 mutants survive; no HTTP/Java/JS/SQL tests) | test | TQ-04, TQ-05 | No safety net for modernisation | High | M-L (CT plan) | P0 | High | Stage 15 (CT-01..16) |
| TD-03 | `LEGACY_DB` resolved at import; 5 writers use hard-coded repo-relative `data/` paths (incl. one deleting all files in `data/archive_documents`) | design | WB-F1; `app/store.py` L4; `archived_documents.py` L6-7 | Unsafe execution; no multi-env config | High | M | P0 | High | Stage 14 |
| TD-04 | Documentation instructs destructive commands while claiming data preservation (README quick start, PRELOADED_DATA quick start, `verify.sh`) | doc | AD-08, AD-09 | Operator data loss | High | S | P0 | High | Stage 15 (docs on branch) |
| TD-05 | Three divergent approval/priority rules (Python 50,000; JS regional x1.05 / 999,999; night-shift 2,500-8,500); archive roles unused | defect/design | RC-4; BB-01/07/09 | Inconsistent decisions for the same input | High | M (consolidation) but **blocked by decision RC-3** | P1 | High | Stage 8 decision, Stage 15 |
| TD-06 | No write path for case decisions/dispositions; no audit trail (`version` constant 1, snapshot status) | design (missing) | RC-1, RC-2; BB-02 (501) | GxP data-integrity gap (not part of code) | High | XL | P1 | High | Stage 8-12 (requirements); STOP-07/HAR-12 |
| TD-07 | SQL report inflates `SUM(amount)` by 19.3 % (`LEFT JOIN events`) | defect | BB-08; `sql/legacy_reports.sql` | Wrong financial figure if consumed | High | S | P1 | High | Stage 15 with approval; consumer unknown |
| TD-08 | Night-shift join multiplies rows 4-5x per object (118 objects in 500 rows) | defect | BB-07; `shift_reconciliation.py` L9 | Over-counted tenant totals / flagged counts | High | S | P1 | High | Stage 15 |
| TD-09 | Java month-end: silent `NumberFormatException` swallow (200 rows in bundled CSV), `double` accumulation, positional CSV columns, no date cut-off | defect | BB-08; `ReconcileLegacy.java` | Silent under-count; precision risk (latent) | Medium | S-M | P1 | High | Stage 15 |
| TD-10 | JS threshold: default 999,999 when region/year absent (17/32 probed pairs), cwd-relative file read, `Number(null)` -> allowed | defect | BB-09 | Approval limit effectively disabled for unmapped regions/years | High | S | P1 | High | Stage 15 (after RC-3) |
| TD-11 | Reconcile is destructive (in-place status overwrite), content-blind replay detection, 1,000-row cap, no run record, unguarded `json.loads` | defect/design | BB-05; `partner_feeds.py` L60-71 | Evidence loss; one bad row aborts the run (exception) | High | M | P1 | High | Stage 15 |
| TD-12 | Bridge stores nothing for invalid events (counted only); accepts schema 0.9; no retry/backoff; a failure after `apply` but before checkpoint write re-delivers (idempotent by message_id) | design | BB-04; `gateway_bridge.py` L13-34 | Silent data loss for invalid events | Medium | M | P2 | High | Stage 15 |
| TD-13 | `source-contract-v1.json` and `contracts/decision-policies-archive.json` are not enforced / read by Python | design | AD-04, DM-18 | Contracts decorative | Medium | M | P2 | High | Stage 14 |
| TD-14 | HTTP server: single 50-line `do_GET` (CC 28) mixing routing, SQL, validation; pagination clamp block copied 3x (`server.py` L28, L39, L46); `ThreadingHTTPServer` with new SQLite connection per request; no structured errors/logging | design | static analysis; `app/server.py` | Hard to change safely | Medium | M | P2 | High | Stage 15 |
| TD-15 | `app/enterprise_legacy.py generate` (CC 25, 49 lines), `historical_fixture.generate` (CC 23, 52 lines), `partner_feeds.generate` (CC 17), `enterprise_data.expand` (CC 15), `generate.generate` (CC 15): monolithic generators with inline domain constants | design | `static_analysis.json` | Maintenance cost; but generators are test-data tooling, not production | Low | M | P3 | High | defer |
| TD-16 | Code style: 11 of 35 Python files use 1-space indent, 24 use 4-space; semicolon-joined statements (`;`) in 20 files; lines up to 922 chars (`app/store.py` L19 DDL), 753 (`enterprise_data.py` L3), 566; no formatter/linter config | maintainability | static analysis | Poor readability and review quality | Low | S (formatter) but large diff | P3 | High | Engineering standards (see memory: coding-standards initiative) / Stage 15 |
| TD-17 | 0 of 58 functions have docstrings or type annotations; no module docstring in 22 of 35 files (4 are empty `__init__.py`) | maintainability | static analysis | Onboarding cost | Low | M | P3 | High | Stage 15 |
| TD-18 | No logging/observability: no logger, `LOG_LEVEL` unused, gateway suppresses access log, no correlation ids, no metrics, no health depth (`/health` is static) | ops | SO-12; `server.py`; `source_gateway/server.py` L38 | Incidents not diagnosable (INC-2025-014) | Medium | M | P2 | High | Stage 15/20 |
| TD-19 | No authentication/authorisation; staging/production-like profiles bind 0.0.0.0; container runs as root | ops/security | `compose.yaml`, `Dockerfile`, env examples | Exposure if run beyond localhost | High (contextual) | M | P1 | High | Stage 23/25 |
| TD-20 | Dataset definitions conflict (125/4100 shipped vs 6000/4326 README/CI/run.sh vs partner feeds 8500/20261017 generated against a different case table); shipped partner feeds not regenerable; test residue row in shipped `gateway_inbox` | data | BB-12; TQ-02 | Baseline ambiguity | Medium | S (decision) | P1 | High | Stage 8 (OD-02 confirm) |
| TD-21 | No schema migration mechanism: DDL inline in 6 modules (`CREATE TABLE IF NOT EXISTS`), one DDL on each partners GET; schema drift undetectable | design | `store.py`, `partner_feeds.py`, `gateway_bridge.py`, `enterprise_data.py`, `domain_data.py`, `historical_estate.py` | Hard to evolve schema | Medium | M | P2 | High | Stage 14 |
| TD-22 | Weak data integrity: `cases` has no FK to batch/deviation/CAPA; `partner_feeds.ref_id` has no FK (98 % orphan in shipped data); five status vocabularies; only 2 secondary indexes (`status`, `case_id`, feed ref/source) | data/design | RC-7; AD-17 | Cross-record inconsistency | Medium | L | P2 | High | Stage 8-14 |
| TD-23 | Generators use `random.Random(seed)` but with undocumented derived seeds (`seed+9211`, `+77019`, `+8800`) and shipped partner feeds were created against another state | data | `domain_data.py` L5; `enterprise_data.py` L8; BB-12 | Reproducibility depends on call order | Low | S | P3 | High | defer |
| TD-24 | `scripts/smoke.py` and `rehearse_local.py` / `offline_inventory.py` hard-code `data/` paths, ignore `LEGACY_DB`; smoke asserts only `total_cases>0` | test | `smoke.py` L7, L16-21 | False "pass" for a different DB | Low | S | P3 | High | Stage 15 |
| TD-25 | CI: unittest before generation; no matrix, no cache, actions unpinned by SHA; never run | ops | `verify.yml` | Unverified pipeline | Low | S | P2 | High | Stage 15/24 |
| TD-26 | Docker/Compose: image copies whole context incl. `data/` (55 MB) and runs as root; gateway uses an image-baked DB while legacy uses a volume (two DBs); no multi-stage, no HEALTHCHECK in Dockerfile; never executed | ops | `Dockerfile`, `compose.yaml` | Runtime divergence | Medium | M | P2 | High | Stage 14/E2 |
| TD-27 | `ops/legacy_log_sampler.py` and `sql/legacy_reports.sql` are orphan artefacts run by no entry point; README repeats the "Additional legacy subsystems" section 3x | doc/cleanup | grep; README | Noise | Low | S | P3 | High | Stage 15 |
| TD-28 | `domain.json` `okstatus: released` and `business_measure` unused; domain name variants (6) | design | AD-12, AD-13 | Dead config | Low | S | P3 | High | Stage 15 |
| TD-29 | `app.workshop_check` runs DDL and exits 0/1 with JSON; used as "self-check" but cannot detect wrong data (TQ-08) | test | `workshop_check.py` | False readiness | Low | S | P3 | High | Stage 15 |
| TD-30 | `/api/incidents` is a hard-coded literal, INC-2025-014 "retried twice" has no code counterpart | design/doc | BB-02; RC-6 | Misleading operational view | Low | S | P3 | High | Stage 8 |
| TD-31 | Timezone/time handling: naive/`utc` mix; `received_at` uses wall-clock; hard-coded dates (2023-01-01 base) and future-dated generated data (up to 2026-01-05 vs run date 2026-10-17); `2023-02-29` invalid dates injected in lake events | data | generators; Stage 5 CS-B | Time-based KPIs unreliable | Medium | M | P2 | Medium | Stage 8/14 |
| TD-32 | Concurrency: SQLite file shared by multiple processes with `busy_timeout` 15 s; `ThreadingHTTPServer`; no WAL mode; no locking strategy documented | design | `store.py` L8-11 | Possible lock errors under parallel runs (not characterised) | Medium | M | P2 | Medium | Stage 14 (CT-17) |
| TD-33 | `gateway_bridge.pull` uses `urlopen` on any scheme and builds the URL by concatenation; error path prints traceback | security/quality | `gateway_bridge.py` L29 | Low in CLI context | Low | S | P3 | High | Stage 15 |
| TD-34 | No dependency/runtime pinning for Java/Node; Java built ad hoc by source launcher | ops | DM-03/04 | Reproducibility | Low | S | P3 | High | Stage 14 |

### Debt totals

By priority (counted from the table): P0 = 4 (TD-01..04); P1 = 9 (TD-05, 06, 07, 08, 09, 10, 11, 19, 20); P2 = 10 (TD-12, 13, 14, 18, 21, 22, 25, 26, 31, 32); P3 = 11 (TD-15, 16, 17, 23, 24, 27, 28, 29, 30, 33, 34). Total 34. [Verified Fact]

Aggregate effort (indicative, [Inference]): P0 ~ 2-3 weeks including the characterisation suite; P1 ~ 4-6 weeks excluding TD-06 (XL, requirements-led); P2 ~ 4-5 weeks; P3 ~ 2 weeks. No staffing or calendar commitment is implied.

## Evidence References

As listed per row; metrics from `evidence/analysis/static_analysis.json`; behaviour from `baseline-behaviour.md`.

## Assumptions

- A-07-11: Effort sizes assume a single engineer familiar with Python/SQLite and the stage-14 plan; excludes stakeholder decisions. Confirm: Engagement lead (Dinesh Naik), Stage 14.
- A-07-12: Defect-debt items (TD-07..TD-10) have unknown real-world consumers; severity is therefore contingent (OD-04).

## Unknowns

- Who consumes the SQL report, the Java totals and the JS thresholds (U-19); whether any real data exists with amounts > 50,000.

## Unresolved Issues

- TD-05/TD-10 cannot be resolved until RC-3 (definition/authority) is decided.

## Residual Risks

- R-07-09: Debt register is derived from a synthetic training estate; transfer of priorities to a real estate requires revalidation.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial register (34 items). |
