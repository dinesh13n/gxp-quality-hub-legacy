---
stage: "16 — Validate the Good Repo"
artifact: "dependency-scan-summary.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["pyproject.toml (no dependencies)", "docs/16-repo-validation/evidence/import-scan.txt (AST scan of every .py file)", "Dockerfile, compose.yaml", "legacy_js/legacy_policy.js, legacy_java/ReconcileLegacy.java (no package / build manifests)", "laptop runtime probe 2026-10-20 (python 3.10.12, SQLite 3.37.2 with FTS5 trigram, node v22.23.2, OpenJDK 11, no docker)", "docs/15-modernization/dependency-changes.md", "tests/hub/test_tst_co_11_no_ai_denylist.py (green)", "https://discuss.python.org/t/python-3-10-eol-is-there-an-official-end-of-support-date-within-october-2026/108064", "https://www.linuxcompatible.org/story/python-31022-31117-31215-31316-and-3148-ship-as-310-hits-end-of-life/"]
supersedes: "none"
---
**Label: synthetic repository. No vulnerability database was queried offline; runtime CVE status is reported as Unknown with a reasoned risk.**

## Summary
The modernised code adds **zero third-party dependencies**: every import in `hub/` (163 files, 13,994 lines) and in the legacy estate resolves to the Python standard library or to the repository's own packages; `pyproject.toml` declares none; there is no `requirements*.txt`, `package.json`, `pom.xml` or lock file. `pip-audit` therefore has nothing to audit (not run against an empty set). The dependency risk sits entirely in the **runtimes**: the reference runtime is **Python 3.10.12**, a 3.10 point release that is behind the final 3.10 security releases, and the 3.10 line reached end of life in October 2026 (public sources, see Evidence). The runtime floor decision (OD-S12-12: 3.10 floor vs ADR-018's 3.12) is therefore no longer only a compatibility question.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| DS-01 | `hub/` imports only stdlib + `hub.*`; legacy imports only stdlib; tests import stdlib + local helpers | `evidence/import-scan.txt` (AST, `sys.stdlib_module_names` of 3.13) | no supply-chain exposure from packages; No-AI deny-list trivially satisfied | Low | High | — |
| DS-02 | No dependency manifest changed since `baseline-as-found` (`pyproject.toml` unchanged; no lock file) | `git diff --name-status baseline-as-found main` (additions only) | matches OD-14 "no pyproject change" | Low | High | — |
| DS-03 | Reference runtime Python 3.10.12: the 3.10 line is end-of-life as of October 2026 and 3.10.12 lacks the later 3.10 security point releases | laptop probe; public EOL sources | security fixes for the interpreter no longer arrive; any production use on 3.10 inherits unpatched CPython issues | **High** for production, Low for the sandbox shadow | Medium (EOL date from public sources, not from python.org directly in this run) | OD-S12-12: decide target runtime (3.12+) at Stage 17/27 |
| DS-04 | SQLite 3.37.2 on the device (FTS5 + trigram available); cloud has 3.45.1. SQLite >= 3.43 changes floating-point `sum()` results (behavior-difference-report ENV-4) | probes; char-cloud-py313_report.json CT-12 | an upgrade changes legacy report outputs at the last digit; hub uses Decimal and is unaffected | Medium | Medium | include SQLite version in the runtime decision |
| DS-05 | Node v22.23.2 and OpenJDK 11 are used only to run the as-found JS / Java comparators in sandboxes; they are not product dependencies | `tests/characterization/capture/batch.py`; ADR-018 | none for the product | Low | High | — |
| DS-06 | Legacy container base `python:3.12-slim` is an unpinned tag (no digest); compose binds `0.0.0.0` | `Dockerfile`, `compose.yaml` | non-reproducible legacy image; pre-existing (Stage 7), unchanged | Medium (legacy only) | High | retire / pin at Stage 30 |
| DS-07 | Evaluation-only tools used in Stage 16 (bandit 1.9.4, pip-audit 2.10.1 installed but not needed, jsonschema for contract checks, ruff 0.16.8) live in the cloud workspace only; nothing was added to the repository's dependencies | this stage's evidence | none for the product | Low | High | — |

## Evidence References
- Import scan: `python3 - <<EOF` AST walk over `hub/`, `tests/hub`, `tests/characterization`, `app`, `legacy_batch`, `services`, `scripts`, `ops`, `integration` -> non-stdlib top-level imports: `hub` only (plus test helper modules) (`evidence/import-scan.txt`).
- Python 3.10 EOL: discuss.python.org thread on the October 2026 end-of-support date; linuxcompatible.org release note "3.10 hits end of life".

## Assumptions
- A-16-DS-1 [Assumption] The October 2026 EOL of Python 3.10 (PEP 619 schedule, as reported by the public sources above) applies; confirm against python.org before the runtime decision. Owner: Engagement lead (Dinesh Naik).

## Unknowns
- U-16-DS-1 CVE exposure of CPython 3.10.12, SQLite 3.37.2, Node 22 and JDK 11 builds on the device (no offline vulnerability database) - resolve at Stage 24/27 with a networked scanner or vendor advisories.
- U-16-DS-2 Target deployment runtime (OD-S12-12, RTD-79) - Stage 27.

## Unresolved Issues
- DS-03 runtime floor; DS-06 legacy image pinning.

## Residual Risks
- RR-DS-1 Running the hub on an EOL interpreter in any real deployment (High) - mitigated only by deciding OD-S12-12 before Stage 30.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
