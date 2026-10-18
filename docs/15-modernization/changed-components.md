---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "changed-components.md"
version: "v0.2"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "git diff --name-status main..stage-15-inc01-harness", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)"]
supersedes: "v0.1 (INC-01 only)"
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

## Evidence References
- `git diff --stat main..stage-15-inc01-harness`; `evidence/inc01/final-A_report.json` (`legacy_suite`).
- INC-02: `git diff --name-status main..stage-15-inc02-hub-skeleton`; `hub/`; `tests/hub/`.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- None for INC-01.

## Unresolved Issues
- None.

## Residual Risks
- RR-CC-1 `tests/characterization/` is a new WB-04-class path approved via OD-11 E-2; future increments must keep it free of `__init__.py` or CI discovery changes.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
