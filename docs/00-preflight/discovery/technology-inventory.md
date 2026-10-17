---
stage: "0A — Pre-Flight Repository & System Orientation"
artifact: "technology-inventory.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["pyproject.toml", "Dockerfile", ".github/workflows/verify.yml", "compose.yaml", "legacy_java/ReconcileLegacy.java", "legacy_js/legacy_policy.js", "sql/legacy_reports.sql", "docs/historical-fixtures.md", "README.md", "device tool versions (python3 --version, node --version, java)"]
supersedes: "none"
---
## Summary

Python 3 standard library is the only runtime for the core estate (HTTP via `http.server`, persistence via `sqlite3`, no ORM, no web framework, no third-party packages). Java and Node.js appear as optional legacy consumers. There is no AI/LLM, cloud SDK, message broker or external database client anywhere in the code.

## Findings

| ID | Technology | Version evidence | Where used | EOL / currency signal | Class | Confidence |
|---|---|---|---|---|---|---|
| TI-01 | Python | `requires-python = ">=3.10"` (`pyproject.toml` L3); Docker `python:3.12-slim` (`Dockerfile` L1); CI `python-version: "3.12"` (`verify.yml` L9-10); device interpreter 3.10.12 | All `app/`, `services/`, `legacy_batch/`, `scripts/`, `tests/` | [Inference] Python 3.10 reaches upstream end-of-life in Oct 2026 (python.org release schedule — external, to be confirmed); minimum supported version is at/after EOL as of RUN_DATE. 3.12 is supported. Docker tag `3.12-slim` is unpinned (floating patch/OS layer). | Verified (versions) / Inference (EOL) | High / Medium |
| TI-02 | Python stdlib modules | `http.server.ThreadingHTTPServer`, `sqlite3`, `urllib.request`, `json`, `csv`, `email`, `argparse`, `unittest`, `hashlib` | `app/server.py` L2; `app/store.py` L1; `app/gateway_bridge.py` L2 | `http.server` is documented by Python as "not recommended for production" (it only implements basic security checks) — [Inference] from stdlib docs, not repo | Verified (usage) | High |
| TI-03 | SQLite | via Python `sqlite3`; `PRAGMA foreign_keys=ON`, `busy_timeout=15000` (`app/store.py` L10-11) | 6 database files (see `data-flow-overview.md`) | Single-writer file DB used as shared integration store | Verified | High |
| TI-04 | Java | Docs require "Java 17+" (`docs/historical-fixtures.md` L4); code uses `Path.of` (Java 11+) | `legacy_java/ReconcileLegacy.java` (16 lines) | No build file; `.class` git-ignored; device has `java` but no `javac` (ran via single-file source launch) | Verified | High |
| TI-05 | Node.js | Docs require "Node 18+" (`docs/historical-fixtures.md` L4); device Node v22.23.2 | `legacy_js/legacy_policy.js` (CommonJS `require`) | No `package.json`; no dependencies | Verified | High |
| TI-06 | SQL | ANSI-ish SQLite SQL | `sql/legacy_reports.sql` (2 queries) | Not referenced by any code (grep) — [Inference] dormant / manually run | Verified (unreferenced) / Inference (dormant) | Medium |
| TI-07 | Container | `Dockerfile` (single image used for all 3 Compose services); `compose.yaml` (no `version:` key, Compose v2 syntax, healthchecks) | Packaging | Docker not installed on inspection device; Compose "not executed in the release-building environment" (`PRELOADED_DATA.md` L30) | Verified (descriptors) / Unknown (works) | High / Low |
| TI-08 | CI | GitHub Actions `actions/checkout@v4`, `actions/setup-python@v5`, `ubuntu-latest` | `.github/workflows/verify.yml` | No git remote configured → no evidence CI has ever run (no run logs) | Verified (file) / Unknown (execution) | High |
| TI-09 | Shell | POSIX `sh` with `set -eu` | `run.sh`, `scripts/verify.sh` | — | Verified | High |
| TI-10 | Data formats | JSON, JSONL (events/documents), CSV (partner export), RFC-822 `.eml`, HTML, JSON Schema-like contract (`integration/source-contract-v1.json`, draft not declared) | `data/`, `integration/`, `contracts/` | `source-contract-v1.json` is not enforced by any code (grep) | Verified | High |
| TI-11 | AI / ML / LLM / cloud SDKs | none — grep for `openai|anthropic|llm|langchain|azure|embedding|gpt` returns no matches outside `.fde/` | — | Relevant to Stage 0C: current model-call volume = 0 | Verified | High |
| TI-12 | Observability tooling | none (no logging framework config, metrics library, tracing SDK) | — | See `security-observability-overview.md` | Verified | High |

## Evidence References

`pyproject.toml` L1-5; `Dockerfile` L1; `.github/workflows/verify.yml` L5-10; `app/server.py` L1-2; `app/store.py` L1-11; `legacy_java/ReconcileLegacy.java`; `legacy_js/legacy_policy.js`; `sql/legacy_reports.sql`; `docs/historical-fixtures.md` L4; device commands `python3 --version` (3.10.12), `node --version` (v22.23.2), `which javac` (absent).

## Assumptions

- A-04: Python 3.10 EOL date (Oct 2026) is taken from the public CPython release schedule, not from the repo. Confirm in Stage 7 / 10. Owner: Engagement lead (Dinesh Naik).

## Unknowns

- U-06: Which Python version the fictional client actually runs in its "container host" (docs/interface-notes.md 2023 entry). U-07: Whether Java/Node consumers run on a schedule anywhere.

## Unresolved Issues

- Version pinning is absent for the base image and CI runner; reproducible builds are not guaranteed.

## Residual Risks

- R-11 (runtime currency / unpinned base image). See `initial-risk-register.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 0A discovery draft (read-only inspection of commit `b126c56`). |
