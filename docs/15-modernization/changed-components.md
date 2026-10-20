---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "changed-components.md"
version: "v0.4"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; INC-03 (hub DB migrations M001, C2 access & audit chain, backup/restore, first rollback rehearsal) added in v0.3. Stage 15 overall status: IN PROGRESS. INC-04 (policy & rule service: M002, as-found rule sets inactive, activation with a recorded human decision) added in v0.4."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "git diff --name-status main..stage-15-inc01-harness", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)", "docs/15-modernization/evidence/inc03/", "docs/15-modernization/rollback-rehearsal-inc03.md", "hub/", "tests/hub/", ".fde/orchestrator-decisions.md (OD-15)"]
supersedes: "v0.3 (INC-01 .. INC-03)"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
INC-01 adds one new component — the characterisation harness (C11 change-safety tooling) under `tests/characterization/` — plus Stage 15 documentation. **No existing component changed.**

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CC-1 Added (all new files, status `A` in git)
| Path | Component | Backlog | Tag |
|---|---|---|---|
| `tests/characterization/run_characterization.py` | harness CLI (captures, unittest comparison, shipped-suite check, mutation gate, `--update-golden`) | TB-02/03/04 | [Verified Fact] |
| `tests/characterization/harness.py` | sandbox guard E-CO-NOT-SANDBOX, FX-BASE125 hash gate, CT-H3 normalisation N1-N4, comparison | TB-01/02/03 | [Verified Fact] |
| `tests/characterization/capture/{_common,api,batch,lib,supplement}.py` | ported Stage 7 captures + INC-01 supplement | TB-03/04 | [Verified Fact] |
| `tests/characterization/catalogue.json` | CT-01..CT-18 definitions + `ac_links` (C3) | TB-04/05 | [Verified Fact] |
| `tests/characterization/mutants.json` | M1..M15 | TB-04 | [Verified Fact] |
| `tests/characterization/fixtures/FX-BASE125.sha256` | 1,512 pinned data hashes (byte copy of backup manifest) | TB-01 | [Verified Fact] |
| `tests/characterization/golden/stage7/*` | byte copies of Stage 7 goldens + R1/R7 logs | TB-03 | [Verified Fact] |
| `tests/characterization/golden/inc01/supplement_golden_v1.json` | INC-01 supplement golden | TB-04 | [Verified Fact] |
| `tests/characterization/golden/{INDEX.json,MANIFEST.sha256}` | active-golden index + integrity manifest (CT-H4) | TB-03 | [Verified Fact] |
| `tests/characterization/README.md` | how to run | TB-03 | [Verified Fact] |
| `docs/15-modernization/*.md`, `docs/15-modernization/evidence/inc01/*` | Stage 15 artifacts + run evidence | — | [Verified Fact] |

### CC-2 Unchanged (verified)
[Verified Fact] `app/`, `legacy_batch/`, `legacy_java/`, `legacy_js/`, `services/`, `scripts/`, `sql/`, `integration/`, `contracts/`, `ops/`, `operations/`, `environments/`, `data/` (git-ignored, checksum rc 0), existing `tests/test_*.py`, `.github/workflows/verify.yml`, `Dockerfile`, `compose.yaml`, `pyproject.toml`, `run.sh`, `domain.json`, all earlier `docs/` stage folders. Evidence: `git diff --name-status main..HEAD | grep -v '^A'` → empty.

### CC-3 Interaction with existing components
- [Verified Fact] No `__init__.py` in `tests/characterization/`: `python -m unittest discover -s tests` (CI and `scripts/verify.sh`) still discovers exactly the 15 shipped tests.
- [Verified Fact] The harness imports no legacy module in its own process; legacy code runs only in child processes whose cwd is a sandbox copy.

### CC-4 INC-02 added (all new files, status `A` in git)
| Path | Component (Stage 10/14) | Backlog | Purpose |
|---|---|---|---|
| `hub/__init__.py`, `hub/__main__.py`, `hub/cli.py` | C11 / hub entry point | TB-06 | `python -m hub` (selfcheck, init, deviations, golden-compare, no-ai-check); installs egress guard, checks runtime, honours kill switch, exports tripwires |
| `hub/runtime.py` | runtime self-check | TB-06 | floor 3.10/3.37 (default) or 3.12 (ADR-018 option); prints Python/SQLite/FTS5 (BEH-CO-09) |
| `hub/config.py` | config + INC-02 flags | TB-06 | `data_origin`, `hub.kill`, `capability_authority`, `runtime.floor` (FF-1) |
| `hub/core/errors.py`, `hub/core/untrusted.py` | core | TB-06/07 | error codes + exit codes; `Untrusted` text type and decision-parameter guard (ADR-002 B(3)) |
| `hub/guards/sandbox.py` | sandbox guard | TB-06 | E-CO-NOT-SANDBOX (BEH-CO-04); backup-manifest verifier |
| `hub/guards/no_ai.py`, `hub/guards/egress.py` | No-AI guard | TB-07 | AST/manifest deny-list (E-CO-DENYLIST-IMPORT); socket egress guard (E-CO-EGRESS-ATTEMPT) |
| `hub/obs/metrics.py` | observability | TB-07 | `model_calls_total`, `egress_attempts_total` zero-tripwires (BEH-OBS-06) |
| `hub/adapters/legacy_sqlite.py`, `baseline_pins.json` | AD-01, AD-02 | TB-08 | snapshot + `mode=ro&immutable=1` + authorizer + sha256/schema pins |
| `hub/adapters/legacy_captures.py` | AD-08 | TB-08 | reads active INC-01 goldens after MANIFEST check |
| `hub/store/db.py`, `hub/store/migrations/M000_coexistence.sql` | store, M000 | TB-08 | `schema_migrations`, `deviation_register`, `coexistence_inventory` (DDL addendum) |
| `hub/coexistence/register.py`, `seed_inc02.json` | deviation register | TB-08 | DV-01..DV-09 `proposed`; CO-WF-01 owner Unknown |
| `hub/golden/compare.py`, `run.py`, `baseline_probes.py`, `probes_inc02.json` | golden-compare | TB-08 | BEH-CO-01 engine, 11 probes, reference queries |
| `tests/hub/run_hub_tests.py`, `_driver.py`, `_support.py` | test infrastructure | TB-06..08 | sandboxed runner (reuses INC-01 `harness.build_pristine`), JSON result recorder, helpers |
| `tests/hub/test_tst_co_{01,02,04,05,06,07,11,12,13,14}_*.py`, `test_inc02_supplementary.py` | tests | TB-06..08 | the 10 planned INC-02 tests + S01..S03 |
| `docs/15-modernization/evidence/inc02/*` | evidence | — | run reports, golden-compare output, checksums |

### CC-5 INC-02 unchanged (verified)
[Verified Fact] `git diff --name-status main..HEAD` lists only `A` entries plus `M` on `docs/15-modernization/*.md` (Stage 15's own artifacts). No change to `app/`, `services/`, `legacy_*`, `sql/`, `scripts/`, `integration/`, `contracts/`, `data/`, existing `tests/*.py`, `tests/characterization/`, `.github/`, `Dockerfile`, `pyproject.toml` (TST-CO-05).
[Verified Fact] `tests/hub/` has no `__init__.py`: the shipped `python -m unittest discover -s tests` still collects 15 tests (regression run: shipped suite ran=15 OK).

### CC-6 INC-03 additions (all new files, status `A`; no existing file modified)
| Path | Component | Backlog | Tag |
|---|---|---|---|
| `hub/store/forward/M001_access_audit.sql` | audit_log (DDL v0.1 verbatim) + DDL addendum: principal, principal_role, session, login_attempt, release_record, release_gate_result; hold-all triggers incl. deviation_register delete guard | TB-09/10 | [Verified Fact] |
| `hub/store/migrate.py` | forward-only runner, backup-before-migrate, drift / unknown-version refusal | TB-09 | [Verified Fact] |
| `hub/security/{canonical,audit,auth,authz,exposure,scan,settings,errors,openapi_routes}.py`, `hub/security/route_registry.json` | C2: canonical JSON + clock, hash chain + anchor + verify, PBKDF2 authenticator + lockout + sessions, deny-by-default authorisation + Zone H check, exposure guard, secret/deletion scan, security settings, INC-03 error codes, route registry | TB-10 | [Verified Fact] |
| `hub/ops/{backup,release,gates}.py` | backup/restore with manifest; release checklist G1-G10; G3/G5/G6/G7 evaluators | TB-11 | [Verified Fact] |
| `hub/admin/{__init__,__main__,cli}.py` | `python -m hub.admin` operator CLI | TB-09..11 | [Verified Fact] |
| `tests/hub/_inc03.py`, `tests/hub/test_tst_sec_{01,04,05,06,09,10,11,12,13,14,15,16,18,21}_*.py`, `tests/hub/test_tst_co_{10,15}_*.py`, `tests/hub/test_inc03_supplementary.py` | 16 planned INC-03 tests + 5 supplementary | — | [Verified Fact] |
| `docs/15-modernization/rollback-rehearsal-inc03.md`, `docs/15-modernization/evidence/inc03/*` | rollback procedure + rehearsal 1, run evidence | — | [Verified Fact] |

[Verified Fact] `git diff --name-status main..HEAD` lists only `A` entries plus `M` for `docs/15-modernization/*.md` (TST-CO-05 c green). Existing hub files (`hub/cli.py`, `hub/config.py`, `hub/store/db.py`, `hub/core/errors.py`, M000) and INC-02 tests are unchanged; INC-03 reuses `db.open_hub`, `config.load`, `sandbox`, `egress`, `no_ai`, `metrics`.

### CC-7 INC-04 additions (all new files, status `A`; no existing file modified)
| Path | Component | Backlog | Tag |
|---|---|---|---|
| `hub/policy/migrations/M002_policy_rules.sql` | `policy_object`, `policy_events`, `rule_set`, `rule_row`, `active_ruleset` (DDL v0.1 verbatim) + immutability / pointer triggers | TB-12 | [Verified Fact] |
| `hub/policy/schema.py` | M002 applier: backup-before-migrate, `policy_schema_migrations`, drift / not-migrated refusal | TB-12 | [Verified Fact] |
| `hub/policy/engine.py`, `hub/policy/inputs.py` | pure table-driven evaluation (imports only decimal / re) and strict Decimal parsing | TB-12 | [Verified Fact] |
| `hub/policy/rulesets.py`, `hub/policy/asfound.py`, `hub/policy/as_found_pins.json` | rule-set documents (validate, content hash) and the AD-06 importer for `as-found-python` / `-js` / `-batch` (text / data read, sha256 pins, never executes legacy code) | TB-12 / AD-06 | [Verified Fact] |
| `hub/policy/service.py`, `hub/policy/clocks.py`, `hub/policy/gate.py`, `hub/policy/errors.py` | `PolicyService` (policy objects, rule sets, evaluation, activation with a recorded decision), clock verdicts, local Zone H check, E-POL-* / E-GATE-* codes | TB-12 | [Verified Fact] |
| `hub/policy/{__init__,__main__,cli}.py` | `python -m hub.policy` operator CLI (never activates) | TB-12 | [Verified Fact] |
| `tests/hub/_inc04.py`, `tests/hub/test_tst_co_03_golden_parity.py`, `tests/hub/test_tst_pol_{01_10_policy_objects,11_21_rule_sets,22_25_purity_inputs_immutability}.py`, `tests/hub/test_inc04_supplementary.py` | 25 planned INC-04 test IDs (29 methods) + 8 supplementary | — | [Verified Fact] |
| `docs/15-modernization/inc04-design-notes.md`, `docs/15-modernization/evidence/inc04/*` | design decisions D-01..D-12, run evidence | — | [Verified Fact] |

[Verified Fact] `git diff --name-status main..HEAD` lists only `A` entries plus `M` for `docs/15-modernization/*.md` (TST-CO-05 c green). `hub/core/errors.py`, `hub/store/*`, `hub/security/*`, `hub/cli.py`, `hub/admin/*`, M000 / M001 and all INC-02 / INC-03 tests are unchanged; INC-04 reuses `db.open_hub`, `audit.change`/`append`/`verify`, `legacy_sqlite.open_snapshot`, `legacy_captures`, `backup.backup`, `migrate.check`, `Authenticator` sessions and `settings`.

## Evidence References
- INC-03 evidence: `docs/15-modernization/evidence/inc03/` (summary.txt, hub-final-{A,B,C} reports, char-regression-inc03_report.json, mutation-gate-inc03.txt, checksum-log.txt, rollback-rehearsal-1/); `docs/15-modernization/rollback-rehearsal-inc03.md`; commits `git log --oneline main..stage-15-inc03-hub-db-audit`.
- `git diff --stat main..stage-15-inc01-harness`; `evidence/inc01/final-A_report.json` (`legacy_suite`).
- INC-02: `git diff --name-status main..stage-15-inc02-hub-skeleton`; `hub/`; `tests/hub/`.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- None for INC-01.

## Unresolved Issues
- None.

## INC-05 additions
All new (no legacy file changed): `hub/gate/*` (shared Zone H gate, `GatedPolicyService`); `hub/decision/*` (M003 migration, schema applier, settings, access, service, backfill, CLI); `hub/crosswalk/*` (registry.json, service, sources); `tests/hub/_inc05.py` and four test modules (39 planned + 14 supplementary + 1 egress); `docs/15-modernization/inc05-design-notes.md`. Verified Fact (`git diff --stat main`).

## INC-06 additions
All new (no legacy file changed): `hub/intake/*` (M004, schema applier, canon, reasons, contracts, profiles, validate, service, untrusted lint, replay, CLI), `hub/adapters/intake_sources.py`, `hub/adapters/gateway_client.py`; `tests/hub/_inc06.py` and test modules (27 TST-INT, TST-CO-09, 14 supplementary, 1 egress); `docs/15-modernization/inc06-design-notes.md`, `rollback-rehearsal-inc06.md`, `evidence/inc06/`. Verified Fact (`git diff --stat main`).

## INC-07 additions
All new (no legacy or earlier-increment file changed): `hub/runs/*` (M005, schema applier, errors, settings, catalogue, flag, ZH-09 schedule service, sources, jobs, run service, detector, reports, CLI), `hub/metrics/*` (errors, values, registry, sources, service, CLI), `hub/obs/log.py`, `hub/obs/collect.py`; `tests/hub/_inc07.py` and test modules (39 planned, 19 supplementary, 1 egress); `docs/15-modernization/inc07-design-notes.md`, `rollback-rehearsal-inc07.md`, `evidence/inc07/`. Verified Fact (`git diff --name-status main`: only `A` outside the doc edits in `docs/15-modernization/`).

## INC-08 additions
All new (no legacy or earlier-increment file changed): `hub/web/*` (M006, schema applier, errors, wire, routes, authz, csrf, tokens, obs_http, app, api, ui, server, cli, nfr, `ui_routes.json`), `hub/gate/{actions,dispositions,disposition_errors,flags,modes,pack,reauth}.py`, `hub/review/*`; `tests/hub/_inc08.py`, `_http8.py`, `_probe8.py` and seven test modules (64 planned, 14 supplementary, 1 egress); `docs/15-modernization/inc08-design-notes.md`, `rollback-rehearsal-inc08.md`, `evidence/inc08/`. Existing docs/15-modernization files are extended. No change under `app/`, `data/`, `.github/`, `pyproject.toml`; `git diff --name-status main` shows only `A` outside docs/15-modernization.

## INC-09 additions
All new (no legacy or earlier-increment file changed): `hub/search/*` (settings, fts, text, corpus, engine, schema, cli, `migrations/M007_search_r2.sql`), `hub/r2/*` (api, web, cli, consistency, divergence, drafts + `templates.json`, errors, facts, intake_reports, joined, protection, source_quality); `tests/hub/_inc09.py` and four test modules (20 planned, 13 supplementary, 1 egress). Extended earlier classes by subclassing only: `hub.review.search.SearchService` -> `hub.search.engine.R2SearchService`, `hub.web.app.WebApp` -> `hub.r2.web.R2WebApp`; `hub.web.api` is reused by delegation (`hub.r2.api.__getattr__`). Docs: `inc09-design-notes.md`, `rollback-rehearsal-inc09.md`, `evidence/inc09/`; non-add edits only to the docs/15-modernization logs and summaries.

## Residual Risks
- RR-CC-1 `tests/characterization/` is a new WB-04-class path approved via OD-11 E-2; future increments must keep it free of `__init__.py` or CI discovery changes.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
| v0.3 | 2026-10-18 | claude-fde-agent | INC-03 (branch `stage-15-inc03-hub-db-audit`): sections added; earlier content unchanged. |
| v0.4 | 2026-10-18 | claude-fde-agent | INC-04 (branch `stage-15-inc04-rule-service`): sections added; earlier content unchanged. |
| v0.5 | 2026-10-19 | claude-fde-agent | INC-05 (branch `stage-15-inc05-decision-record`): sections added; earlier content unchanged. |
| v0.6 | 2026-10-19 | claude-fde-agent | INC-06 (branch `stage-15-inc06-intake`): sections added; earlier content unchanged. |
| v0.7 | 2026-10-19 | claude-fde-agent | INC-07 (branch `stage-15-inc07-runs-metrics`): sections added; earlier content unchanged. |
| v0.8 | 2026-10-19 | claude-fde-agent | INC-08 (branch `stage-15-inc08-http-reviewer`): sections added; earlier content unchanged. |
| v0.9 | 2026-10-20 | claude-fde-agent | INC-09 (branch `stage-15-inc09-search-corpus`): sections added; earlier content unchanged. |
