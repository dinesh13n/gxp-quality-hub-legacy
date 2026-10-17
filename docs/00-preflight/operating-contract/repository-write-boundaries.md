---
stage: "0B — Provisional Operating Contract & Engineering Boundaries"
artifact: "repository-write-boundaries.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md OD-01, OD-03", ".gitignore", "app/store.py L4", "app/enterprise_legacy.py L4", "legacy_batch/shift_reconciliation.py L4-5", "app/archived_documents.py L6-7", "app/generate_documents.py L6", "app/generate.py L15-20", "../_data-backup-2026-10-17/SHA256SUMS.txt", "git status --porcelain --ignored"]
supersedes: "none"
---
## Summary

Least-privilege write rules for every path in `gxp-quality-hub-legacy/`. Default is **deny**. A stage agent may write only its own stage `docs/` folder (DESIGN/DISCOVERY stages) or, for BUILD stages, code on a `stage-NN-*` branch prepared by the orchestrator. The working-tree `data/` directory is **write-prohibited for everyone except an explicit engagement-lead-approved restore**. Git commits/branches/merges/pushes are performed only by the orchestrator (OD-01). All rules are PROVISIONAL (confirm Stage 25, close Stage 37).

Key new finding: OD-03's mitigation "copy data to a temp dir and point env vars there" is **insufficient** — only `LEGACY_DB` is env-configurable; four writers resolve `data/` relative to the code location, so the only safe execution pattern is a **full repository copy outside the working tree**.

## Findings

### Path write matrix (PROVISIONAL)

| ID | Path | Stage agent (DISCOVERY/DESIGN) | Stage agent (BUILD, on branch) | Orchestrator | Engagement lead | Notes |
|---|---|---|---|---|---|---|
| WB-01 | `docs/<own-stage-folder>/` | Write (create new; version bump to change) | Write | Commit | Approve | Only path writable in DESIGN mode |
| WB-02 | `docs/<other-stage-folders>/` (incl. `docs/00-preflight/discovery/`) | **Deny** | **Deny** | Deny except errata commit approved by lead | Approve | Prior evidence immutable; corrections via later-version artifacts |
| WB-03 | `docs/*.md` (original legacy docs) | Deny | Deny unless stage scope names it | Commit | Approve | Legacy docs are evidence of as-found state |
| WB-04 | `app/`, `services/`, `legacy_batch/`, `legacy_java/`, `legacy_js/`, `sql/`, `scripts/`, `ops/`, `integration/`, `contracts/`, `tests/` | Deny | Write on `stage-NN-*` branch only | Merge after review | Approve merge (PROVISIONAL, Stage 25) | |
| WB-05 | `Dockerfile`, `compose.yaml`, `.dockerignore`, `environments/`, `.github/workflows/`, `pyproject.toml`, `run.sh`, `domain.json` | Deny | Write on branch only **with HAR approval** (config/CI) | Merge after review | Approve | Config/CI change = human-approval trigger HAR-07 |
| WB-06 | `data/` (all 1,512 files) | **Deny** | **Deny** | **Deny** | Restore-from-backup only, then verify checksums | OD-03; R-01/R-02 |
| WB-07 | `.fde/` (stage prompts, engagement context, orchestrator decisions) | Deny | Deny | Write (decision log) | Approve decisions | Control plane |
| WB-08 | `.git/` internals; history of `main` | Deny (read-only git allowed) | Deny | Commit/merge only; **no rewrite / force-push** | Approve any exception | OD-01 |
| WB-09 | `../_data-backup-2026-10-17/` | Read only (for checksum verification) | Read only | Read only | Owner | Backup must stay immutable |
| WB-10 | Sandbox outside repo (e.g. `$HOME/fde_sbx/…` on device) | Write (disposable) | Write | — | — | All execution happens here |
| WB-11 | Any other folder on the user's device | Deny | Deny | Deny | — | Least privilege |

### Supporting findings

| ID | Finding | Class | Evidence | Impact | Confidence |
|---|---|---|---|---|---|
| WB-F1 | Only `LEGACY_DB` is configurable via env; `app/enterprise_legacy.py` L4, `legacy_batch/shift_reconciliation.py` L5, `app/archived_documents.py` L4-7 (`for f in root.glob('*'): f.unlink()`), `app/generate_documents.py` L6, `app/historical_fixture.py` (lake target) write to repo-relative `data/` | [Verified Fact] | grep of `parents[1]` / `sqlite3'` | Running these from the working tree mutates or deletes tracked/ignored data even with `LEGACY_DB` redirected | High |
| WB-F2 | `app/store.py` L4 resolves `LEGACY_DB` at import time; tests overwrite the default DB (reproduced in 0A) | [Verified Fact] | `test-overview.md` TO-03; DF-02 | Env redirection after import is ineffective | High |
| WB-F3 | `data/*.sqlite3` and `data/lake/` are git-ignored; git cannot restore them | [Verified Fact] | `.gitignore`; `git status --ignored` shows `!! data/legacy.sqlite3`, `!! data/enterprise_legacy.sqlite3`, `!! data/lake/` | Backup is the only recovery path | High |
| WB-F4 | Backup `../_data-backup-2026-10-17/` contains 1,513 files (1,512 data + `SHA256SUMS.txt`) but SHA256SUMS lists only the 6 SQLite files; the 1,084 lake JSON/JSONL/CSV files are backed up but **not checksummed** | [Verified Fact] | `wc -l SHA256SUMS.txt` = 6; `find … -type f | wc -l` = 1,513 | Integrity of lake files cannot be verified after an incident | High |
| WB-F5 | Working-tree SQLite DBs match backup at this stage | [Verified Fact] | `sha256sum -c` on 6 entries → all `OK` (2026-10-17, Stage 0B start) | Baseline intact | High |
| WB-F6 | `git status --porcelain` clean at Stage 0B start (prior to writing this folder) | [Verified Fact] | command output empty | Clean starting point | High |
| WB-F7 | Repo `.gitignore` duplicates `data/lake/` and `*.class` three times | [Verified Fact] | `.gitignore` | Cosmetic; no write impact | High |

### Mandatory execution pattern (binding on all stages)

1. Copy the **entire repository** (not only `data/`) to a sandbox directory outside the working tree.
2. Run commands only inside the sandbox; set `LEGACY_DB` to the sandbox path before any Python import.
3. Before and after any stage that executes code, run `sha256sum -c` against `../_data-backup-2026-10-17/SHA256SUMS.txt` from the repo root and `git status --porcelain`; record both outputs in the stage artifacts.
4. Never run `python -m unittest`, `scripts/verify.sh`, `app.workshop_check`, `app.generate --reset`, `app.archived_documents`, `app.generate_documents`, `app.enterprise_legacy`, `app.historical_fixture`, `app.partner_feeds` (generate) or `app.domain_data`/`app.enterprise_data` in the working tree.

## Evidence References

As cited in the tables; commands: `git status --porcelain` (empty), `git status --porcelain --ignored`, `sha256sum -c` (6 × OK), `git ls-files data | wc -l` (422), `find data -type f | wc -l` (1,512).

## Assumptions

- A-0B-02: The device connector blocks `rm` in connected folders by default (tool-level behaviour as described by the agent platform; not tested to avoid a destructive attempt). It is a defence-in-depth control, not a substitute for WB-06. Confirm: Engagement lead (Dinesh Naik), Stage 25.
- Orchestrator review before merge is treated as the human review step (OD-01 approved by Dinesh). PROVISIONAL — Stage 25.

## Unknowns

- Who besides the engagement lead may approve merges (Stage 2 / 25).

## Unresolved Issues

- WB-F4: extend SHA256SUMS to all 1,512 backed-up files (orchestrator action; GD-03).

## Residual Risks

- A BUILD-stage agent running a generator from inside the working tree would destroy data even with `LEGACY_DB` set (WB-F1) — mitigated by STOP-02/STOP-03 and backup.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional write boundaries. |
