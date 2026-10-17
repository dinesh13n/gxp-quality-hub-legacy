---
stage: "0A — Pre-Flight Repository & System Orientation"
artifact: "repository-overview.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["git log (a6eb4e8, b126c56)", "git ls-files", ".gitignore", "README.md", "pyproject.toml", "Dockerfile", "compose.yaml", ".github/workflows/verify.yml", "PRELOADED_DATA.md", "DATA_READINESS.md"]
supersedes: "none"
---
## Summary

`gxp-quality-hub-legacy` is a single-repository (monorepo-style) **synthetic, self-described "legacy training simulator"** for a Life Sciences / Pharma quality workflow (batch quality review, deviation and CAPA processing). It is predominantly Python (standard library only, no third-party dependencies), with one legacy Java class, one legacy Node.js script and one SQL report file. The repository has **no meaningful version-control history**: two commits, both made on 2026-10-17 by the engagement lead (baseline import + FDE prompt pack). Activity, ownership and deployment signals therefore cannot be derived from git and must come from documents or stakeholders.

## Findings

| ID | Finding | Class | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|---|
| RO-01 | Repo has exactly 2 commits: `a6eb4e8` "baseline: import legacy gxp-quality-hub repository (unmodified)" (2026-10-17 14:39:00Z, 500 files, +5,156 lines) and `b126c56` "chore(fde): add FDE stage system prompts and engagement context". No git remote is configured. | [Verified Fact] | `git log`, `git show --stat a6eb4e8`, `git remote -v` (empty) | No commit-history signals (churn, authorship, hot spots) are available for Stage 7. | Ownership and change-frequency analysis impossible from VCS. | High | Does an upstream origin repo with history exist? |
| RO-02 | 548 tracked files; 421 of them are `data/archive_documents/*` (210 `.eml`, 210 `.html`, 1 `manifest.json`). ~45 source/config/doc files carry the logic; total non-archive text ≈2,824 lines incl. 1,200-line JSONL. | [Verified Fact] | `git ls-files \| wc -l`; `wc -l` over tracked files | Codebase is small; orientation can be exhaustive. | Low | High | — |
| RO-03 | Top-level layout: `app/` (18 py modules: API, generators, ingestion, reports), `services/source_gateway/` (second HTTP service), `legacy_batch/` (night-shift reconciliation), `legacy_java/`, `legacy_js/`, `sql/`, `ops/`, `scripts/` (verify/smoke/inventory), `tests/` (7 unittest modules), `integration/` (contract + gateway config JSON), `contracts/` (policy archive JSON), `environments/` (3 `.env.example`), `operations/` (runbook, incident, baseline notes), `docs/` (18 pre-existing md incl. `correspondence/`, `decisions/`), `data/`, `.github/workflows/`, `.fde/` (engagement prompt pack). | [Verified Fact] | `find . -type d` | Defines the module map used in all other 0A artifacts. | — | High | — |
| RO-04 | Build system: none beyond `pyproject.toml` (5 lines: name, version 0.1.0, `requires-python >=3.10`, no dependencies, no build-backend). No lock file, no `requirements*.txt`, no `package.json`, no Maven/Gradle file. | [Verified Fact] | `pyproject.toml` L1-5; file tree | Zero third-party supply chain in Python path. | Java/JS components have no build descriptor; how they are built/run in "production" is undocumented. | High | — |
| RO-05 | Runtime databases are **git-ignored and local-only**: `data/*.sqlite3` and `data/lake/` (`.gitignore` L1, L6/9/12). Present on disk: `data/legacy.sqlite3` (8.3 MB), `data/enterprise_legacy.sqlite3` (9.2 MB), `data/lake/{tiny,bundled}` (~33 MB). | [Verified Fact] | `.gitignore`; `git check-ignore -v`; `ls -la data` | The baseline data cannot be reproduced from git alone; a fresh clone lacks the preloaded DBs that `PRELOADED_DATA.md` says must not be regenerated. | Baseline-preservation risk (see R-01, R-02). | High | Where is the authoritative copy of the original ZIP/data (PRELOADED_DATA.md L34 says "keep an untouched copy of the original ZIP")? |
| RO-06 | Packaging/run entry points: `run.sh` (generates data only if DB missing, then `python -m app.server`), `Dockerfile` (python:3.12-slim, copies whole tree incl. data), `compose.yaml` (3 services: `legacy`, `source-gateway`, `bridge`), CI `verify.yml` (push/PR: unittest → generate --reset → baseline). | [Verified Fact] | `run.sh`, `Dockerfile` L1-7, `compose.yaml`, `.github/workflows/verify.yml` | Multiple run modes with different data semantics. | Divergent DB state between modes (see architecture & data-flow artifacts). | High | — |
| RO-07 | Documentation hygiene signals: README.md repeats the section "Additional legacy subsystems and large synthetic fixtures" three times (L78-L104); `.gitignore` repeats `data/lake/` and `*.class` three times; `app.generate` default `--seed 4100` (L49) while README/CI/`domain.json` use seed 4326. | [Verified Fact] | `README.md`, `.gitignore` L5-13, `app/generate.py` L49, `domain.json` L15 | Indicates accreted, append-only maintenance. | Running the documented "regenerate" command without `--seed` yields a different dataset than the documented baseline. | High | Which seed is the authoritative baseline seed? |
| RO-08 | File modification times of all baseline files are 2026-10-16 23:17 (packaging time); no other activity signal (no CHANGELOG, no release tags). | [Verified Fact] | `stat` on `data/*.sqlite3`, `app/server.py`, manifests | No evidence of live operation or recent maintenance cadence. | Operational status must be treated as Unknown. | Medium | — |
| RO-09 | Ownership hints exist only in prose: `docs/business-context.md` lists five stakeholder roles (Quality ops lead, Enterprise app owner, Finance partner, Risk & security partner, Integration lead); `domain.json` `"owner": "Quality"`. No CODEOWNERS file. | [Verified Fact] | `docs/business-context.md` L9-15; `domain.json` L10 | Roles known, named individuals unknown. | Approval authority unclear for later stages. | High | Who are the named people in each role? |
| RO-10 | The repository is explicitly an educational simulation ("not certified for handling real ... pharmaceutical ... production operations"; "not a validated production system"). | [Verified Fact] | `README.md` "Boundary", "Explicit baseline scope"; `PRELOADED_DATA.md` L34 | Bounds all claims about production status, GxP validation and real data. | Mis-framing the simulator as a validated GxP system. | High | — |

## Evidence References

- `git log --format='%h %ad %an %s' --date=iso` → `b126c56`, `a6eb4e8` only.
- `git ls-files | wc -l` → 548; `ls data/archive_documents | wc -l` → 421.
- `.gitignore` lines 1–13; `git check-ignore -v data/legacy.sqlite3 data/lake/x`.
- `pyproject.toml` L1–5; `run.sh` L1–6; `Dockerfile` L1–7; `compose.yaml` L1–45; `.github/workflows/verify.yml` L1–13.

## Assumptions

- A-01 (see `assumptions-unknowns.md`): commit `a6eb4e8` faithfully reproduces the supplied legacy ZIP ("unmodified"). Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-01 Upstream VCS history / origin repository. U-02 Named owners per component. U-03 Authoritative baseline seed (4100 vs 4326). Details in `assumptions-unknowns.md`.

## Unresolved Issues

- No change-history evidence exists; Stage 7 must rely on static analysis and behaviour characterisation only.
- The preloaded data files are outside version control; preservation of the "before" baseline depends on an out-of-git copy.

## Residual Risks

- R-02 (git-ignored baseline data can be lost or silently altered). R-10 (documentation drift). See `initial-risk-register.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 0A discovery draft (read-only inspection of commit `b126c56`). |
