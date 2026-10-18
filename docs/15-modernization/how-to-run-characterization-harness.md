---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "how-to-run-characterization-harness.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 only (characterisation harness + hermetic fixtures + mutation gate). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "tests/characterization/README.md"]
supersedes: "none"
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

## Evidence References
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
