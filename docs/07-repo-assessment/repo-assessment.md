---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "repo-assessment.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["README.md", "app/", "services/", "legacy_batch/", "legacy_java/", "legacy_js/", "sql/", "scripts/", "tests/", "compose.yaml", "Dockerfile", ".github/workflows/verify.yml", "docs/00-preflight/*", "docs/04-baseline-kpis/*", "docs/05-current-state/*", "docs/06-root-cause/*", ".fde/orchestrator-decisions.md (OD-02, OD-03a, OD-07)", "docs/07-repo-assessment/*.md", "docs/07-repo-assessment/evidence/*"]
supersedes: "none"
---
## Summary

**Stage 7 gate outcome: CONDITIONAL PASS** (evaluation in "Completion Gate" below). The assessment covered the full repository at commit `3b9876a` (source unchanged since tag `baseline-as-found`, `a6eb4e8`): 35 Python files (818 lines), 1 Java, 1 JS, 1 SQL file, 7 test modules (15 tests), 10+ manually started entry points, SQLite-only persistence, and 1,512 git-ignored data files (55 MB, synthetic). All executable behaviour was run **only in sandbox copies** outside the working tree.

**Headline conclusions**

1. The estate is small, dependency-free and fully runnable offline; it is also a *characterisation-hostile* codebase: the shipped tests **overwrite the baseline database**, cover 47.9 % of lines and detect **1 of 15** injected regressions.
2. A **behaviour baseline now exists** (three deterministic golden captures: 55 HTTP requests, 58 batch/CLI/Java/JS/SQL/generator observations, 9 library edge cases) that detects 14 of 14 replayed regressions; it is data, not yet an executable suite (see `characterization-test-plan.md`).
3. The code contains **material defects that the baseline records but must not silently preserve or fix**: three divergent approval rules (RC-4), SQL `SUM` inflation of 19.3 % (RC-8), night-shift row multiplication (118 objects in 500 rows), JS default-allow threshold 999,999 (17 of 32 probed region/year pairs), silent drops in Java and the bridge.
4. The **core GxP function - recording a decision/batch disposition with an approver - does not exist in code** (API is GET-only; write verbs return 501). It must be preserved as an *absence* and not simulated (STOP-07/HAR-12).
5. **Data provisioning is partly irreproducible**: the shipped `legacy.sqlite3` base tables equal `generate --count 125 --seed 4100` (not the README's 6,000/4326), and the five partner-feed tables cannot be regenerated from the shipped case table.

## Findings

### Scope and method (what was done)

| Step | Action | Evidence |
|---|---|---|
| 1 | Read stage prompt, OD-03a/OD-07, engagement context, Stage 0B boundaries; consumed 0A, 5, 6 artefacts | this file; `.fde/` |
| 2 | Full read of all source (app, services, batch, Java, JS, SQL, scripts, tests, CI, Docker) | cited per artifact |
| 3 | Static analysis with stdlib AST (no analysers installed) and import graph | `evidence/analysis/static_analysis.json` |
| 4 | Sandbox copy `cp -a` -> executed 7 test/verify scenarios on fresh copies | `evidence/test-logs/R1..R7`, `baseline-test-results.md` |
| 5 | Line coverage via stdlib `trace`; 15-mutant probe on the suite | `evidence/analysis/coverage_trace_unittest.json`, `mutation_probe.log` |
| 6 | Golden captures (API + gateway, batch/CLI/Java/JS/SQL/generators, library edge cases), each run twice and compared (`cmp`) | `evidence/golden/*.json`, `baseline-behaviour.md` |
| 7 | Golden mutation replay (14 mutants) | `evidence/analysis/golden_mutation_replay_*.json` |
| 8 | Dynamic security probe on localhost sandbox | `evidence/analysis/security_probe_output.txt` |
| 9 | Authored 13 artifacts; verified real-repo integrity | this section |

### Repository inventory (Verified Facts)

| Area | Files | Lines | Notes |
|---|---|---|---|
| `app/` | 18 (17 modules + `__init__`) | 552 | procedural scripts + HTTP server + generators |
| `services/source_gateway/` | 3 | 44 | second HTTP server |
| `legacy_batch/` | 2 | 18 | night-shift job |
| `legacy_java/`, `legacy_js/`, `sql/` | 3 | 16 / 7 / 6 | ad hoc, no build |
| `scripts/`, `ops/` | 5 | 83 | verification and sampler |
| `tests/` | 7 | 121 | 15 tests |
| Config | `domain.json`, `domain-profile.json`, `integration/*.json`, `contracts/decision-policies-archive.json`, env examples, Dockerfile, compose, CI | - | |
| Documentation (legacy) | README, PRELOADED_DATA, DATA_READINESS, 16 `docs/*.md`, runbook, incident | - | partly inaccurate |
| Data (git-ignored/tracked mix) | 1,512 files, 55 MB | - | `legacy.sqlite3` (19 tables), `enterprise_legacy.sqlite3` (12 tables, 12,500 objects), lake tiny/bundled, documents, archive_documents (421) |

### Assessment by required dimension

| # | Dimension | Verdict | Where detailed |
|---|---|---|---|
| 1 | Architecture drift | 17 drift items; documented "services/CRUD" vs shared-DB read-only reality; no ADRs | `architecture-drift.md` |
| 2 | Module boundaries and coupling | No layering; shared SQLite bus; import-time global config; 5 hard-coded-path writers | `architecture-drift.md`, `dependency-map.md` |
| 3 | Dependency health | No third-party libraries; runtime-version risk only (Python 3.10, JDK 11, Node) | `dependency-map.md` |
| 4 | Duplication and complexity | Rules in 4 languages; 7 functions CC >= 15; code-density issues | `technical-debt-register.md`, `maintainability-assessment.md` |
| 5 | Legacy patterns and partial migrations | 22 patterns; 11 partial migrations | `legacy-pattern-register.md`, `partial-migration-register.md` |
| 6 | Security and code quality | No injectable/secret/exec findings; architectural gaps (no authN/Z, no audit trail, root container, destructive commands) | `security-code-quality-findings.md` |
| 7 | Testability and test results | 15/15 pass; destructive; 47.9 % line; 1/15 mutants killed | `baseline-test-results.md` |
| 8 | Observability and maintainability | No logging/run records; maintainability Low-Moderate | `maintainability-assessment.md` |

### Key findings (ranked)

| ID | Finding | Class | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|---|
| RA-01 | Running the existing tests from the working tree silently rewrites `data/legacy.sqlite3`; the outcome depends on module order (125 vs 180 cases); the shipped DB itself carries test residue (`gateway_inbox` row `CHECK-batch_quality`) | [Verified Fact] | TR-01..05, TQ-01/02 | Baseline destruction; unreliable regression evidence | High | High | Fix approach (Stage 14/15) |
| RA-02 | The suite is not a safety net: 47.9 % line coverage, 14/15 injected regressions survive; 0 tests for HTTP, reconcile, bridge pagination, file import, Java, JS, SQL | [Verified Fact] | TQ-04/05 | Modernisation cannot rely on it | High | High | - |
| RA-03 | Golden baseline captured and validated: deterministic (2 identical runs), kills 14/14 replayed mutants | [Verified Fact] | `baseline-behaviour.md` | Stage 15/16 can compare behaviour | Positive | High | Executable harness (CT plan) |
| RA-04 | No decision/disposition write path or audit trail; API GET-only | [Verified Fact] (absence) | CW-14, RC-1/2 | Central GxP step outside the system | High | High | Where recorded (A-07) |
| RA-05 | Three divergent approval rules + fail-open default 999,999 + unused policy roles | [Verified Fact] | BB-01/07/09, PM-01 | Inconsistent / bypassable approvals | High | High | Authority decision RC-3 |
| RA-06 | Month-end figures differ by method; SQL inflated +19.3 % (742,956.61 vs 622,826.44); Java skips 200 unparsable rows; floats latent | [Verified Fact] | BB-08 | Wrong/unreconciled finance numbers | High | High | Consumers unknown |
| RA-07 | Dataset definitions conflict: shipped = `125/4100`; README/CI/run.sh = `6000/4326`; shipped partner feeds not regenerable (98 % orphan refs); 5 of 7 data artefacts reproduce byte/table-exact | [Verified Fact] | BB-12, AD-08 | Baseline identity ambiguous (OD-02) | Medium | High | Confirm OD-02 |
| RA-08 | Docs instruct destructive commands while promising preservation (README, PRELOADED_DATA, verify.sh) | [Verified Fact] | AD-08/09, TD-04 | Operator data loss | High | High | - |
| RA-09 | No third-party dependencies; no injectable SQL; no secrets; no logging; unauthenticated; root container | [Verified Fact] | `security-code-quality-findings.md` | Small attack surface, no controls | Medium | High | - |
| RA-10 | Only Python 3.10.12 / JDK 11 / Node 22 exercised; CI/Docker (3.12) unverified; no coverage/lint tools offline | [Verified Fact] | TR-12 | Environment parity unknown | Medium | High | - |

### Integrity attestation (executed after all sandbox work, in the real repository)

| Check | Command (cwd = real repo root) | Result |
|---|---|---|
| Data integrity | `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` | no output, **exit 0** (all 1,512 entries match) [Verified Fact] |
| Working tree | `git status --porcelain` | `?? docs/07-repo-assessment/` only [Verified Fact] |
| Tracked-file changes | `git diff --quiet HEAD -- . ':!docs/07-repo-assessment'` | exit 0 - no tracked file modified [Verified Fact] |
| Ignored files | `git status --porcelain --ignored` | only `data/enterprise_legacy.sqlite3`, `data/lake/`, `data/legacy.sqlite3` (as at Stage 0B); no `__pycache__` in the tree [Verified Fact] |
| HEAD | `git rev-parse HEAD` | `3b9876a8d7c4ec7563ef7ecfeb16057195cf1d7d` [Verified Fact] |
| Sandbox location | `$HOME/fde_sbx/stage7` (not under `$HOME/mnt/Case-Execution`) | [Verified Fact] |
| Evidence manifest | `docs/07-repo-assessment/evidence/SHA256SUMS-evidence.txt` | lists every evidence file |

### Completion Gate evaluation

| Gate condition | Status | Evidence |
|---|---|---|
| Critical workflows and baseline behaviour documented | **Met** | `critical-workflow-inventory.md` (14), `baseline-behaviour.md` |
| Baseline test results recorded | **Met** | `baseline-test-results.md` (15/15, plus 7 scenarios) |
| Characterisation plan for every critical workflow lacking coverage | **Met** | `characterization-test-plan.md` CT-01..CT-18 map to CW-01..CW-14 |
| No source modified | **Met** | integrity attestation above |
| All 13 required artifacts exist at the paths | **Met** | `ls docs/07-repo-assessment/` |
| Critical gaps resolved or explicitly documented | **Met (documented)** | conditions C-1..C-6 below |
| Evidence supports the stage conclusion | **Met**, with the limits listed in Unknowns | - |

**Outcome: CONDITIONAL PASS.** No blocking gap. Non-blocking conditions (owner "Engagement lead (Dinesh Naik)" unless stated; due = the named stage, no calendar dates exist):

| ID | Condition | Risk if left | Due |
|---|---|---|---|
| C-1 | Goldens are captured data, not an executable suite; build harness per CT-H1..H7 on a BUILD branch | Stage 15 lacks automated parity | Stage 14 (plan) / Stage 15 (build) |
| C-2 | Dataset identity OD-02 provisional (125/4100 vs 6000/4326); confirm or capture second golden set | Wrong baseline | Stage 8 |
| C-3 | Only Python 3.10.12, JDK 11, Node 22 on a device without Docker; re-run on 3.12 and E2 tier | Runtime drift | Stage 14 |
| C-4 | No coverage.py / SAST / SCA tooling available offline; line coverage via `trace`; no CVE check (no third-party libs) | Understated quality/security view | Stage 14 tooling |
| C-5 | RC-3 authority decision pending: "fix vs preserve" for defects BB-07, BB-08, BB-09, BB-01 cannot be made | Blocks remediation choices, not baselining | Stage 8 |
| C-6 | Concurrency and Compose behaviour not characterised (CT-17/18) | Unknown multi-process behaviour | Stage 14/E2 |

## Evidence References

All artifacts in `docs/07-repo-assessment/`; scripts, logs and goldens in `docs/07-repo-assessment/evidence/` (manifest `SHA256SUMS-evidence.txt`); prior stage artifacts `docs/00-preflight/discovery/test-overview.md`, `workflow-overview.md`, `docs/05-current-state/*`, `docs/06-root-cause/confirmed-root-causes.md`; decisions `.fde/orchestrator-decisions.md` OD-02, OD-03a, OD-07.

**Reproduction recipe** (all inside a disposable copy): `cp -a <repo> $HOME/fde_sbx/stage7/repo`; `PYTHONHASHSEED=0 ./evidence/scripts/run_tests.sh`; `python3 evidence/scripts/capture_api.py <copy> out.json`; `FDE_SRC=<copy> python3 evidence/scripts/capture_batch.py out.json`; `python3 evidence/scripts/capture_lib.py out.json`; compare with `cmp` against `evidence/golden/*.json` (the scripts expect the sandbox layout `~/fde_sbx/stage7/{repo,golden,evidence}`).

## Assumptions

- A-07-01..A-07-17 as listed in the sibling artifacts; key ones: A-07-03 (dataset = shipped DB, OD-02 provisional), A-07-06 (criticality is engineering inference), A-07-02 (3.10 ~ 3.12 equivalence).

## Unknowns

- U-07-01 CI ever run; U-07-02 Python 3.12/Docker behaviour; U-07-03 authoritative approval rule; U-07-05 concurrency; U-17 location of the disposition decision; real consumers of SQL/Java/JS outputs (U-19).

## Unresolved Issues

- C-1..C-6 above; plus TD-01..TD-04 (P0 debt) must be scheduled before any refactor.

## Residual Risks

- R-01 baseline destruction (mitigated by sandbox + backup checksum gate); R-07-01 green suite mistaken for preserved behaviour; R-07-02 defects frozen into parity expectations; R-04 unauthenticated services; R-07-07 destructive documentation.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 7 assessment; gate CONDITIONAL PASS. |
