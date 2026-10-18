---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "transformation-log.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 only (characterisation harness + hermetic fixtures + mutation gate). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "git log main..stage-15-inc01-harness"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
Chronological log of every Stage 15 increment. **INC-01 (P0 "make change observable") is complete on branch `stage-15-inc01-harness` with conditions** (see `remaining-technical-debt.md`). It delivered backlog items TB-01..TB-05 as new files only; no legacy source, test, data, CI, Dockerfile or pyproject file was modified. CT-01..CT-16 are executable (134 checks, all green on the unmodified code), two consecutive runs are identical, the mutation gate kills 15/15 mutants, the 7 shipped test modules still give the as-found result (15 tests OK, same post-run DB hash as Stage 7 R1), and the backup checksum check was rc 0 after every execution session.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TL-1 Increment register
| Inc | Branch | Backlog items | Status | Behaviour change to legacy | Gate (TG-3) |
|---|---|---|---|---|---|
| INC-01 | `stage-15-inc01-harness` | TB-01 FX-BASE125 fixture + hash gate; TB-02 subprocess runner; TB-03 ported captures + CT-H3 normaliser + reviewed `--update-golden`; TB-04 CT-01..CT-16 + M1..M15 gate; TB-05 `ac_links` for CT-04..CT-16 (C3) | DONE WITH CONDITIONS | none | exit criteria met: CT-01..CT-16 green, 15/15 killed, 2 identical runs, shipped tests as-found |
| INC-02..INC-09 | — | TB-06..TB-21 | NOT STARTED | — | — |

### TL-2 INC-01 steps (in order)
1. [Verified Fact] Read OD log (OD-03a, OD-08, OD-09, OD-11..OD-13), Stage 0B write boundaries / stop conditions, Stage 7 plan + scripts + goldens, Stage 13 C3, Stage 14 backlog/gates/roadmap.
2. [Verified Fact] Built `tests/characterization/` (commit 2633062): sandbox guard, FX-BASE125 gate (1,512 pinned sha256), ported Stage 7 capture scripts, byte-identical golden copies (sha256 equal to `docs/07-repo-assessment/evidence/SHA256SUMS-evidence.txt`), catalogue CT-01..CT-18 with `ac_links`, M1..M15. Guard self-test: 6 unsafe sandbox roots refused with rc 2 before any execution.
3. [Verified Fact] First sandbox run (`run-1`): 127/134 checks green — every check backed by a Stage 7 golden; the 7 failing checks were the INC-01 supplement checks, which had no golden yet.
4. [Verified Fact] Supplement golden v1 captured once on unmodified code via `--update-golden supplement` and activated through `golden/INDEX.json` + `MANIFEST.sha256` (commit 0283660).
5. [Verified Fact] Determinism digest made independent of the sandbox path length (commit e1eb1d2) after observing that tail-truncated stderr windows shift with the label length (N4).
6. [Verified Fact] Mutation gate run in four chunks (M1-M5, M6-M9, M10-M13, M14-M15) at e1eb1d2: 15/15 KILLED. Negative fixture test: tampered `legacy.sqlite3` refused with E-FX-HASH (rc 2).
7. [Verified Fact] README (commit ed43a0a); final runs `final-A`/`final-B` at ed43a0a: 134/134, identical digests.
8. [Verified Fact] Stage 15 artifacts and evidence written under `docs/15-modernization/`.

### TL-3 Deviations from the Stage 14 plan
| ID | Plan | Actual | Tag | Reason |
|---|---|---|---|---|
| DEV-01 | branch `stage-15-inc01-characterization-harness` (TG-3) | `stage-15-inc01-harness` (created by the orchestrator) | [Verified Fact] | still matches OD-11 E-6 pattern `stage-15-incNN-<slug>` |
| DEV-02 | TB-22 optional docs fix of unsafe legacy quick start (AD-09) | not done | [Verified Fact] | would modify an existing file (README); out of INC-01 write scope given by the orchestrator |
| DEV-03 | CT-H5 run on 3.10 **and** 3.12 | 3.10.12 only | [Verified Fact] | no 3.12 on device; E-4 accepts this as a gap |
| DEV-04 | CT-H6 "in CI nightly" | runnable gate exists; not wired into `.github/workflows/verify.yml` | [Verified Fact] | CI file may not be modified in INC-01; CI also lacks the git-ignored fixture |
| DEV-05 | C3 = "add AC-CO-xx" | proposed AC-CO-L04..L16 stored as test metadata (`catalogue.json` `ac_links`) | [Inference] | Stage 12 acceptance-criteria.md is not edited in place (OD-10 pattern); adoption needs a Stage 12/13 addendum |
| DEV-06 | Stage 7 plan: CT-11 "requires JDK, absent" | JDK 11.0.32 present on device; CT-11 executes | [Verified Fact] | device fact differs from Stage 13 GAP note |

## Evidence References
- Commits: `git log --oneline main..stage-15-inc01-harness`.
- Run reports: `docs/15-modernization/evidence/inc01/{final-A,final-B,mut-1..mut-4}_report.json`, `summary.txt`, `checksum-log.txt`.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-15-01 Whether the harness can run in GitHub CI (fixture is git-ignored) — decided in a later increment / Stage 23.

## Unresolved Issues
- DEV-02, DEV-04, DEV-05 carried as open items (see `remaining-technical-debt.md`).

## Residual Risks
- RR-TL-1 INC-01 proves the harness on this device only; another runtime (3.12, other JDK/Node) is unverified.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
