---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "changed-components.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 only (characterisation harness + hermetic fixtures + mutation gate). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "git diff --name-status main..stage-15-inc01-harness"]
supersedes: "none"
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

## Evidence References
- `git diff --stat main..stage-15-inc01-harness`; `evidence/inc01/final-A_report.json` (`legacy_suite`).

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
