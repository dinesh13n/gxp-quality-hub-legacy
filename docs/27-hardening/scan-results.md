---
stage: "27 — Production Hardening"
artifact: "scan-results.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/27-hardening/evidence/no-ai-check.json", "docs/27-hardening/evidence/secret-and-deletion-scan.json", "docs/27-hardening/evidence/static-checks.json", "docs/27-hardening/evidence/sbom.cdx.json", "docs/27-hardening/evidence/mutation-s27.json", "docs/27-hardening/evidence/runtime-selfcheck.json", "docs/27-hardening/evidence/regression/"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW: nothing here is an approval and no risk is accepted. Every acceptance, every decision and every sign-off named below is Dinesh Naik's (Engagement lead) and is not recorded by this stage. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
Twelve scans and checks were run; ten completed with a clean or expected result and two could not be run with the tools available (a vulnerability-database scan and an infrastructure scanner, neither installed and no feed reachable). Nothing is hidden: a scan that did not run is listed as NOT RUN with the reason. The scans found no secret, no AI or network-client import, no deletion of a retained table, no third-party package, no import cycle, and a mutation gate in which 13 of 13 mutants are killed. The only non-green item in the regression is the known characterization check CT-13 (Node patch drift, S24-DEV-04).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SR-1 Scan table [Verified Fact]
| ID | Scan | Tool / command | Scope | Result | Evidence file |
|---|---|---|---|---|---|
| SCN-01 | dependency and import deny-list | `python -m hub no-ai-check` | `hub`, `tests/hub`, `pyproject.toml` | rc 0, 0 findings | `evidence/no-ai-check.json` |
| SCN-02 | secret scan (regex heuristic) | `hub.security.scan.secret_scan` | product scan (`hub`, `tests/hub`) and a wide scan of 26 paths (all source dirs, `docs`, `ci`, container files, config) | 0 findings / 0 findings | `evidence/secret-and-deletion-scan.json` |
| SCN-03 | deletion-path grep (retained tables) | `hub.security.scan.deletion_grep` | `hub/*.py`, `hub/*.sql` | 0 findings | same file |
| SCN-04 | source structure (cycles, complexity, layering, unused hints) | `docs/20-application/evidence/s20_static_checks.py` | whole tree | two-cycles 0, three-cycles 0, domain-to-web 0, functions over 15: 9, unused-name hints 11, holder-rule copies 1 (Stage 20: 4 two-cycles, 6 three-cycles, 10 functions over complexity 15, 10 unused-name hints). The one new unused hint, `timeout` in `make_handler`, is a class attribute the heuristic misreads (same kind as the existing `protocol_version` hint) | `evidence/static-checks.json` |
| SCN-05 | dependency review / SBOM | `python -m hub.security.sbom` | `hub/`, `app/`, Dockerfile | 61 components, 0 third-party | `evidence/sbom.cdx.json` |
| SCN-06 | source test strength (mutation gate) | `s27_mutation_gate.py`, 13 mutants in throwaway clones | M5, M9, M10 and one mutant per fix | 13 KILLED, 0 survived | `evidence/mutation-s27.json` |
| SCN-07 | runtime self-check | `python -m hub selfcheck` | host | Python 3.10.12, SQLite 3.37.2, FTS5 yes, floor 3.10 met; `--floor 3.12` refused (E-CO-RUNTIME-UNSUPPORTED) as expected on this host | `evidence/runtime-selfcheck.json` |
| SCN-08 | exposure / secrets review of the code | grep for debug, `eval`, `exec`, `shell=True`, `pickle`, bind addresses, `chmod` | `hub/` | no debug mode, no unsafe call, no `0.0.0.0` in `hub/`; 5 `chmod` sites: 4 in the read-only legacy snapshot / golden helpers, 1 the new store-file tightening (S27-DEV-14) | this document, SH-3 |
| SCN-09 | regression | 25 groups, one per call | see `production-readiness-checklist.md` | all green; counts below | `evidence/regression/` |
| SCN-10 | characterization harness | `tests/characterization/run_characterization.py` | CT-01 .. CT-18 | 133 of 134 checks pass; CT-13 FAIL (Node v22.23.2 golden vs v22.23.4 laptop, S24-DEV-04); CT-17 / CT-18 NOT-RUN as before (no golden / Docker) | `evidence/characterization-summary.txt` |
| SCN-11 | infrastructure / container scan | none | `Dockerfile`, `compose.yaml`, `environments/` | **NOT RUN**: no scanner (hadolint, trivy, grype) is installed and none can be fetched; the files were read by hand (RH-4) | `runtime-hardening.md` |
| SCN-12 | known-vulnerability scan of dependencies and runtime | none | Python, SQLite, Node, Java | **NOT RUN**: no vulnerability database is reachable offline; the dependency set is empty, the runtime status is Unknown (U-27-03) | `dependency-hardening.md` |

### SR-2 Before / after of the structure checks [Verified Fact]
| Metric | Stage 20 end | Stage 27 |
|---|---|---|
| two-cycles | 4 | 0 |
| three-cycles | 6 | 0 |
| functions over complexity 15 | 10 | 9 (`WebApp._dispatch` 22 -> under 15) |
| domain-to-web imports | 0 | 0 |

Remaining over-complex functions: `hub/decision/service.py transition` 25, `hub/admin/cli.py _cmd` 21, `hub/policy/engine.py evaluate` 21, `hub/runs/cli.py _cmd` 20, `hub/intake/validate.py validate` 20, `hub/intake/service.py ingest` 19, `hub/obs/collect.py samples` 18, `untrusted_lint check_source` 16, `hub/policy/rulesets.py validate` 16 (exact list in `evidence/static-checks.json`). The ratchet test keeps the number from growing.

### SR-3 Regression counts [Verified Fact: logs under `evidence/regression/`]
| Group | Executed / expected | ok | FAIL | ERROR | skipped | Wall (s, laptop) | Checksum rc pre / post |
|---|---|---|---|---|---|---|---|
| A | 45 / 45 | 45 | 0 | 0 | 0 | 82 | 0 / 0 |
| B | 42 / 42 | 41 | 0 | 0 | 1 | 95 | 0 / 0 |
| C1 | 5 / 5 | 5 | 0 | 0 | 0 | 67 | 0 / 0 |
| C2 | 1 / 1 | 1 | 0 | 0 | 0 | 92 | 0 / 0 |
| C3 | 1 / 1 | 1 | 0 | 0 | 0 | 68 | 0 / 0 |
| I45 | 91 / 91 | 91 | 0 | 0 | 0 | 102 | 0 / 0 |
| I6 | 43 / 43 | 43 | 0 | 0 | 0 | 100 | 0 / 0 |
| I7 | 59 / 59 | 59 | 0 | 0 | 0 | 85 | 0 / 0 |
| I8a | 35 / 35 | 35 | 0 | 0 | 0 | 79 | 0 / 0 |
| I8b | 43 / 43 | 43 | 0 | 0 | 0 | 74 | 0 / 0 |
| E8 | 1 / 1 | 1 | 0 | 0 | 0 | 90 | 0 / 0 |
| I9 | 33 / 33 | 33 | 0 | 0 | 0 | 67 | 0 / 0 |
| E9 | 1 / 1 | 1 | 0 | 0 | 0 | 66 | 0 / 0 |
| S20 | 18 / 18 | 18 | 0 | 0 | 0 | 104 | 0 / 0 |
| E20 | 1 / 1 | 1 | 0 | 0 | 0 | 110 | 0 / 0 |
| S21 | 7 / 7 | 7 | 0 | 0 | 0 | 97 | 0 / 0 |
| E21 | 1 / 1 | 1 | 0 | 0 | 0 | 100 | 0 / 0 |
| S23 | 26 / 26 | 26 | 0 | 0 | 0 | 113 | 0 / 0 |
| E23 | 1 / 1 | 1 | 0 | 0 | 0 | 111 | 0 / 0 |
| S24 | 21 / 21 | 21 | 0 | 0 | 0 | 102 | 0 / 0 |
| E24 | 1 / 1 | 1 | 0 | 0 | 0 | 105 | 0 / 0 |
| S26 | 23 / 23 | 23 | 0 | 0 | 0 | 142 | 0 / 0 |
| E26 | 1 / 1 | 1 | 0 | 0 | 0 | 144 | 0 / 0 |
| S27 | 25 / 25 | 25 | 0 | 0 | 0 | 110 | 0 / 0 |
| E27 | 1 / 1 | 1 | 0 | 0 | 0 | 98 | 0 / 0 |
| **total** | **526 / 526** | **525** | **0** | **0** | **1** | | |

### SR-4 Limits of the scans [Inference]
- Regex secret scanning finds known shapes only; the scan skips `data/` by design and does not read git history.
- The static checks are the Stage 20 tool's own heuristics (cyclomatic complexity by AST, import graph at module and function level).
- A clean SBOM says what the code imports, not whether the interpreter underneath is patched.

## Evidence References
- `docs/27-hardening/evidence/` (all files above)
- `tests/hub/run_hub_groups.py` logs: `docs/27-hardening/evidence/regression/final-*.json`

## Assumptions
- The regex patterns of `hub.security.scan` (Stage 24) are an adequate heuristic for a synthetic repository.

## Unknowns
- U-27-03; SCN-11 and SCN-12 results are Unknown by construction.

## Unresolved Issues
- Install a container scanner and a vulnerability database in the orchestrator's cloud run or CI (D-27-03).

## Residual Risks
- A clean scan can be a blind scan; the two NOT RUN rows are the largest blind spots.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 27 BUILD). |
