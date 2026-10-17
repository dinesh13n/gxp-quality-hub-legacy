---
stage: "0B — Provisional Operating Contract & Engineering Boundaries"
artifact: "change-control-rules.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md OD-01, OD-05", "git log --oneline (4 commits: a6eb4e8, b126c56, 5c086e3, e3ed6f1)", ".github/workflows/verify.yml", "scripts/verify.sh", "docs/00-preflight/discovery/test-overview.md TO-03"]
supersedes: "none"
---
## Summary

How changes are proposed, reviewed and merged. Git history: `a6eb4e8` baseline import (unmodified legacy), `b126c56` FDE prompts, `5c086e3` Stage 0A, `e3ed6f1` OD log. The existing CI/preflight (`verify.yml`, `scripts/verify.sh`) is itself destructive to the default DB (TO-03) and **cannot be used as a merge gate in the working tree** until test isolation is fixed (Stage 7 design → later BUILD). PROVISIONAL — confirm Stage 25, close Stage 37.

## Findings

| ID | Rule | Class / basis |
|---|---|---|
| CC-01 | `a6eb4e8` is the immutable as-found code baseline; never amend, rebase or force-push `main`. | [Verified Fact] commit message "baseline: import legacy … (unmodified)"; A-01 unconfirmed |
| CC-02 | DISCOVERY/DESIGN stages: agent writes only its `docs/` folder; orchestrator commits to `main` as `stage-<ID>: <title> v<ver> (<GATE>)`. | OD-01; existing commit `5c086e3` follows this |
| CC-03 | BUILD stages: orchestrator creates `stage-NN-*` branch; agent changes only paths named in its stage prompt; orchestrator reviews diff, evidence and gate; merges to `main` (HAR-04). | OD-01 |
| CC-04 | Every merge request includes: diff stat, stage artifacts, test evidence from E1 sandbox (EV-08), before/after checksums (EO-2), gate status. | Evidence contract |
| CC-05 | Behaviour-changing code (decision thresholds, status models, ingestion semantics) requires a characterisation baseline (Stage 7) first and HAR-06. | R-06, R-13 |
| CC-06 | Artifacts are versioned: change = new version (v0.2 …) with Change History entry and `supersedes`; prior versions remain in git history; never silently overwrite. | Stage prompt Global Execution Contract |
| CC-07 | Prior-stage evidence is immutable; corrections are made by an erratum in a later artifact referencing the original finding ID. | WB-02 |
| CC-08 | Gate statuses: BLOCKED halts the sequence (OD-01); CONDITIONAL PASS proceeds with conditions logged (owner, due stage). | OD-01; stage prompt |
| CC-09 | Orchestrator decisions are appended (never edited) to `.fde/orchestrator-decisions.md` with ID, date, status. | Existing OD log format |
| CC-10 | Pushes go only to the private remote `dinesh13n/gxp-quality-hub-legacy` once created (OD-05); CI on push is accepted because it runs on a fresh runner copy, not the working tree. | [Verified Fact] OD-05 pending; ENV-F4 |
| CC-11 | Emergency rollback = `git revert` (new commit) for code/docs; data restore = copy from `../_data-backup-2026-10-17/` + `sha256sum -c` (HAR-01). | WB-06 |
| CC-12 | Recommended (not done here): orchestrator tags `a6eb4e8` as `baseline-as-found` for before/after diffing. | GD-08 |

## Evidence References

`git log --oneline`; OD log; `verify.yml`; `scripts/verify.sh` L4 (`python -m unittest discover -s tests -v`).

## Assumptions

- A-0B-07: Orchestrator review constitutes adequate code review for a single-human engagement. Confirm: Engagement lead (Dinesh Naik), Stage 25.

## Unknowns

- Client-mandated change-management (CAB, GxP change control/validation) — none evidenced; Stage 25.

## Unresolved Issues

- No non-destructive automated test gate exists yet (Stage 7).

## Residual Risks

- Without a safe test gate, early BUILD merges rely on sandbox evidence only.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial change-control rules. |
