---
stage: "14 — Transformation / Migration Plan"
artifact: "rollback-strategy.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/12-specs/features/f10-coexistence-change-safety.md (BEH-CO-06, G2, G7, AC-CO-05/07)", "docs/10-architecture/adrs/ADR-003, ADR-004, ADR-005, ADR-015", "docs/00-preflight/operating-contract/ (HAR-03, HAR-04, STOP-01, STOP-12, WB-08)", ".fde/orchestrator-decisions.md (OD-01, OD-03, OD-03a, OD-06 tag baseline-as-found)", "../_data-backup-2026-10-17/SHA256SUMS.txt (1,512 entries, verified by Stages 7 and 13)", "docs/14-transformation/schema-migration-plan.md, feature-flag-plan.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository; DRAFT plan, not an approval.**
Every Stage 15 increment is reversible by **code revert alone**, because (a) no increment changes legacy code or `data/`, (b) the hub is non-authoritative (shadow) in R1, and (c) `hub.sqlite3` is disposable until cutover (SM-4). There are three rollback levels: **L1 code** (revert the merge commit on `main`), **L2 hub state** (restore `hub.sqlite3` + audit anchor from the pre-increment checksummed backup, or rebuild from legacy snapshot), **L3 consumer authority** (flip `capability.<cap>.authority` back to `shadow` — only relevant after a Stage 30 cutover step). The legacy data backup (OD-03) is the last line and is never needed by a correct increment; it is verified after every executable step (STOP-01). The immutable reference point is tag `baseline-as-found` (a6eb4e8, OD-06).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### RB-1 Rollback per increment
| Inc | What can go wrong | Rollback (level) | Trigger | Data loss on rollback | Rehearsed by | Feasibility | Tag |
|---|---|---|---|---|---|---|---|
| INC-01 | harness flaky / wrong normalisation | L1: revert PR (only `tests/characterization/` added) | non-determinism across 2 runs; any CT red on untouched code | none | n/a (no state) | High | [Inference] |
| INC-02 | guard false-positive blocks runs; adapter writes | L1 revert; delete sandbox hub file | TST-CO-04/05/06 red | none (hub empty) | TST-CO-07 | High | [Inference] |
| INC-03 | migration runner / audit chain defect | L1 + L2 (delete or restore hub file; anchor file restored together) | `verify-audit` fails (G3), migration hash mismatch | hub-only test data | G7 backup/restore rehearsal (TST-CO-10/15) | High | [Inference] |
| INC-04 | rule transcription differs from legacy | L1 + L2 rebuild | TST-CO-03 ≠ 0 diffs | none (rebuild) | rebuild script | High | [Inference] |
| INC-05 | wrong backfill/projection | L1 + L2 rebuild from legacy snapshot (SM-4) | G4 `verify-projection` ≠ 0; count ≠ 125 | none pre-cutover | rebuild | High pre-cutover | [Inference] |
| INC-06 | mis-classification / identity key wrong | L1 + L2 rebuild; checkpoints are hub-owned, legacy gateway offsets untouched | replay-safety G2 red; outcome sum ≠ input | none pre-cutover | G2 | High | [Inference] |
| INC-07 | runs/metrics wrong; schedule accidentally on | L1; `schedule.enabled=false`; L2 | TST-RUN/MET red; any run without operator trigger | none | — | High | [Inference] |
| INC-08 | exposure beyond loopback; Zone H bypass | `hub.kill=true` immediately, then L1 | any bind ≠ 127.0.0.1; G8 red | none | G8 negative tests | High | [Inference] |
| INC-09 | FTS5 missing / wrong ranking | `search.fts=off`; drop derived index | — | none (derived) | — | High | [Inference] |
| CUT-n (Stage 30) | hub authoritative output wrong | L3 flip authority back to `shadow`; consumers re-pointed to legacy (still running, unchanged) | Stage 30 verification fails | events recorded while authoritative are kept (append-only) and reviewed | Stage 30 rehearsal | Medium (needs consumers known, U-14-01) | [Inference] |

### RB-2 Rollback mechanics
- **Branch/PR**: each increment is one squash-merged PR from `stage-15-incNN-<slug>` into `main`; L1 = `git revert -m 1 <merge>` (or revert the squash commit) on a new branch + PR — performed by the orchestrator (HAR-04), never force-push (WB-08). [Inference]
- **Pre-increment backup**: before any hub migration in a sandbox/runtime, copy `hub.sqlite3` + anchor to `backups/<inc>/` with SHA256 manifest; restore = stop, copy back, `sha256sum -c`, `verify-audit`, restart (BEH-CO-06). [Verified Fact] BEH-CO-06 text.
- **Legacy safety net**: after every executable step `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` from repo root must return 0; mismatch = STOP-01 and restore from backup only with HAR-01 approval. [Verified Fact] OD-03/03a.
- **Golden safety net**: after a rollback the INC-01 harness must again be green on `main` (proves the revert restored behaviour). [Inference]

### RB-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| RF-RB-1 | No increment needs a data rollback of legacy data | CR-1..CR-3 | rollback is cheap | Low | High | — |
| RF-RB-2 | Append-only design forbids row-level undo after cutover | ADR-004 triggers | post-cutover rollback is compensating, not restorative | Medium | High | Stage 30 must rehearse |
| RF-RB-3 | Deletion needs HAR-03; `git revert` is additive, so no deletion permission needed | HAR-03 | revert path safe within contract | Low | High | — |
| RF-RB-4 | On the device, git deletes lock files; until delete permission is granted git operations may leave `.lock` files (tool note) | device tool behaviour | orchestrator, not stage agents, runs git | Low | Medium | — |

## Evidence References
BEH-CO-06; ADR-004/005; OD-01/03/03a/06; HAR-01/03/04; STOP-01/12; `../_data-backup-2026-10-17/SHA256SUMS.txt`.

## Assumptions
- A-14-10 [Assumption] Squash-merge per increment is acceptable to the orchestrator (OD-01 says merge after review; method unspecified). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-14-01 (consumers) limits L3 feasibility evidence.

## Unresolved Issues
- No rollback rehearsal has been executed (documentation-only stage); first rehearsal is INC-03 (G7).

## Residual Risks
- RR-RB-1 A revert of INC-0n after INC-0n+1 merged requires reverting in reverse order (linear dependency) — mitigated by merging in order and keeping each increment self-contained.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial rollback strategy (Stage 14). |
