---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "how-to-run-characterization-harness.md"
version: "v0.3"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; INC-03 (hub DB migrations M001, C2 access & audit chain, backup/restore, first rollback rehearsal) added in v0.3. Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "tests/characterization/README.md", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)", "docs/15-modernization/evidence/inc03/", "docs/15-modernization/rollback-rehearsal-inc03.md", "hub/", "tests/hub/", ".fde/orchestrator-decisions.md (OD-15)"]
supersedes: "v0.2 (INC-01 + INC-02)"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
Operator instructions for the INC-01 harness (also in `tests/characterization/README.md`). It never runs legacy code in the working tree and refuses to start if asked to.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Prerequisites [Verified Fact]
Python ≥ 3.10 (evidence on 3.10.12), `java` (JDK 11+) and `node` (≥ 18) on PATH for CT-11/CT-13, and the baseline fixture directory containing `data/` that matches `tests/characterization/fixtures/FX-BASE125.sha256` (default `../_data-backup-2026-10-17`). No package installs.

### Commands
| Purpose | Command (repo root) | Expected |
|---|---|---|
| CT-01..CT-16 + shipped suite | `python3 -B tests/characterization/run_characterization.py` | `CT checks: 134/134 passed`, `OVERALL PASS`, exit 0 (~40 s) |
| + mutation gate | `python3 -B tests/characterization/run_characterization.py --mutation-gate` | `mutation gate: 15/15 KILLED`, exit 0 (~5-6 min) |
| subset of mutants | `... --mutation-gate --mutants M1,M11 --no-legacy-suite` | listed mutants KILLED |
| other sandbox / fixture | `... --sandbox-root /path/outside/repo --fixture-source /path/with/data` | refuses (exit 2) if unsafe or hash mismatch |
| new golden (reviewed) | `... --update-golden supplement --reviewed-by "<name>"` | writes `golden/inc01/supplement_golden_vN.json`; activate via INDEX.json + MANIFEST.sha256 in a PR |
| data integrity afterwards | `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` | exit 0 |

### Outputs
`<sandbox-root>/<label>/report.json` (per-check results with first difference, unittest output, capture digests, tool versions, mutation results) and `<label>/out/*.json` (raw captures). Sandbox copies are deleted unless `--keep`.

### Reading a failure
A failing check prints `CT-xx FAIL ... first: <check> :: <path> golden=... actual=...`. On unmodified legacy code any failure is D5 UNEXPLAINED → STOP-12; do not edit goldens or normalisation to make it pass.

### INC-02 hub tests [Verified Fact]
```sh
python3 -B tests/hub/run_hub_tests.py [--label NAME] [--sandbox-root DIR] [-k PATTERN]
```
The runner refuses (exit 2) if the backup manifest check fails before the run or the sandbox root is unsafe; it builds `<sandbox-root>/<label>/c_pristine` with the INC-01 hash-gated fixture, runs `tests/hub/_driver.py` inside it (HUB_WORKTREE_ROOT, HUB_SANDBOX_ROOT, HUB_LEGACY_ROOT set), re-checks the manifest and writes `<label>/report.json` and `<label>/unittest-result.json`. Exit 0 = all green and checksums rc 0; 1 = a test failed; 2 = refused / checksum failure. Test files must never be run directly from the working tree (`require_sandbox()` refuses).
Hub CLI (from a sandbox copy): `python -m hub selfcheck | init --data-dir D | deviations --data-dir D | golden-compare --data-dir D --legacy-root <sandbox copy> [--json] | no-ai-check [paths]`.

### HR-INC03 Running the INC-03 hub tests and operator commands
Device calls are capped at 180 s and the full hub suite takes > 200 s with the sandbox build, so run it in three splits (each builds its own sandbox copy; `--sandbox-root` must be outside the working tree):
```
python3 -B tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s15-inc03 --label A -k TST_SEC -k TST_CO_10 -k TST_CO_15 -k INC03
python3 -B tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s15-inc03 --label B -k TST_CO_01 -k TST_CO_02 -k TST_CO_04 -k TST_CO_05 -k TST_CO_06 -k TST_CO_07 -k TST_CO_11 -k TST_CO_13 -k TST_CO_14 -k INC02
python3 -B tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s15-inc03 --label C -k TST_CO_12   # re-runs everything under the egress guard
rm -rf ~/fde_sbx/s15-inc03/{A,B,C}/{c_pristine,scratch}   # ~0.5 GB per run (RTD-31)
```
Use `unittest_rc` / the runner exit code as the verdict (RTD-28). Operator commands (sandbox data dir; config must set `audit.anchor_path` outside the data dir):
```
python -m hub.admin --config cfg.json migrate --data-dir D --backup-root B
HUB_NEW_USER_PASSWORD=... python -m hub.admin --config cfg.json user create --data-dir D --principal alice --role reviewer
python -m hub.admin --config cfg.json verify-audit --data-dir D          # exit 17 on tamper
python -m hub.admin --config cfg.json backup --data-dir D --dest-root B --label L
python -m hub.admin --config cfg.json restore --data-dir D --backup B/L
python -m hub.admin --config cfg.json release-checklist --data-dir D --release R --evidence-dir E --scratch-root S [--mark-ready]
python -m hub.admin --config cfg.json scan --data-dir D ; python -m hub.admin --config cfg.json startup-check
```

## Evidence References
- INC-03 evidence: `docs/15-modernization/evidence/inc03/` (summary.txt, hub-final-{A,B,C} reports, char-regression-inc03_report.json, mutation-gate-inc03.txt, checksum-log.txt, rollback-rehearsal-1/); `docs/15-modernization/rollback-rehearsal-inc03.md`; commits `git log --oneline main..stage-15-inc03-hub-db-audit`.
- `tests/characterization/run_characterization.py` docstring.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- None.

## Unresolved Issues
- RTD-01 (CI).

## Residual Risks
- RR-HR-1 Running with a custom `--fixture-source` that is not the OD-09 baseline is refused by the hash gate by design.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
| v0.3 | 2026-10-18 | claude-fde-agent | INC-03 (branch `stage-15-inc03-hub-db-audit`): sections added; earlier content unchanged. |
