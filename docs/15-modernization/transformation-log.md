---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "transformation-log.md"
version: "v0.2"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "git log main..stage-15-inc01-harness", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)"]
supersedes: "v0.1 (INC-01 only)"
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
| INC-02 | `stage-15-inc02-hub-skeleton` | TB-06 `hub/` skeleton + runtime self-check + sandbox guard; TB-07 No-AI deny-list + egress guard (+ Untrusted type, zero-model-call tripwire); TB-08 RO adapters AD-01/02/08, deviation register DV-01..09 `proposed`, `hub golden-compare`, M000 | DONE WITH CONDITIONS | none | exit criteria met: 10/10 planned tests green; golden-compare lists DV-01..09 UNAPPROVED, exit 6 (AC-CO-01); INC-01 harness 134/134, 15/15 killed |
| INC-03..INC-09 | — | TB-09..TB-21 | NOT STARTED | — | — |

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

### TL-4 INC-02 steps (in order)
1. [Verified Fact] Read OD log (OD-03a, OD-08, OD-09, OD-11..OD-14), Stage 0B write boundaries / stop conditions, Stage 14 backlog TB-06..TB-08, gates (TG-3 INC-02 row), adapter strategy AS-1/AS-2, feature-flag plan FF-1, schema-migration plan M000, F10 spec (BEH-CO-01..09, AC-CO-01..15), ADR-002, error-handling spec, increment-test-map (10 INC-02 tests).
2. [Verified Fact] `945c8f1` hub package skeleton: error codes, runtime floor (3.10/3.37 default, 3.12 option), config flags (`data_origin`, `hub.kill`, `capability_authority`, `runtime.floor`), sandbox guard, No-AI deny-list scanner, egress guard, `Untrusted` type, tripwire metrics.
3. [Verified Fact] `2859091` AD-01/AD-02 read-only snapshot adapters (pinned sha256 + schema, `mode=ro&immutable=1`, SQLite authorizer), AD-08 capture reader (golden MANIFEST check), M000 (`schema_migrations`, `deviation_register`, `coexistence_inventory`), DV-01..DV-09 seed (`proposed`), `golden-compare` engine + 11 probes, `python -m hub` CLI. Smoke run in `~/fde_sbx/s15-inc02/smoke`: 9 UNAPPROVED, exit 6; data dir inside the repo refused exit 7 (nothing created).
4. [Verified Fact] `23e8e9a` sandboxed runner `tests/hub/run_hub_tests.py` (+ `_driver.py`) and TST-CO-01/02.
5. [Verified Fact] `90e4710` TST-CO-04/05/06/07. Development run dev2 exposed two hub defects, fixed before commit: re-snapshot onto the read-only snapshot file (PermissionError) and the SQLite message "authorization denied" not mapped to E-CO-LEGACY-WRITE-REFUSED.
6. [Verified Fact] `23b3250` TST-CO-11/12/13/14 + supplementary S01..S03. Development run dev4 exposed a deny-list gap (`torchaudio` not matched by the `torch` family rule); fixed (prefix families now match any top-level name starting with the family).
7. [Verified Fact] At `23b3250` (final code): INC-01 regression `inc02-regress` 134/134 PASS, capture digests identical to INC-01 `final-A`; hub `final-A` and `final-B` 45 ok / 0 fail / 1 skipped; mutation gate in 3 chunks 15/15 KILLED; backup manifest rc 0 before/after every execution.
8. [Verified Fact] `2d2f40d` evidence under `evidence/inc02/`; then these Stage 15 docs (v0.2).

### TL-5 INC-02 deviations from the Stage 14 plan / specs
| ID | Plan / spec | Actual | Tag | Reason / follow-up |
|---|---|---|---|---|
| DEV-07 | branch `stage-15-inc02-hub-skeleton-guards` (TG-3) | `stage-15-inc02-hub-skeleton` (created by the orchestrator) | [Verified Fact] | matches OD-11 E-6 pattern |
| DEV-08 | BEH-CO-01 compares legacy with "the new modules' preserved functions" | new modules do not exist yet: 7 of 9 DV probes use the **declared** F10-2 target value; DV-01, DV-08 and 2 identity probes are computed live over RO snapshots of FX-BASE125 | [Verified Fact] | each declared probe is replaced by the owning module's live output in INC-04..INC-08 (RTD-15) |
| DEV-09 | BEH-CO-07 "CI blocks" deny-listed imports | check exists (`python -m hub no-ai-check`, TST-CO-11) but is not wired into `.github/workflows/` | [Verified Fact] | OD-14: CI unchanged; Stage 27/30 (RTD-14) |
| DEV-10 | error-handling spec lists 6 E-CO codes with exit codes for 3 | INC-02 adds exit codes 9-15 and codes E-CO-LEGACY-SCHEMA-DRIFT, E-OBS-TRIPWIRE, E-CFG-INVALID, E-HUB-KILLED, E-STORE-MIGRATION-DRIFT, E-CO-PROTECTED-WORKFLOW (and reuses E-FX-HASH) | [Verified Fact] | Stage 12 addendum needed (RTD-13); Stage 12 files not edited in place (HAR-13) |
| DEV-11 | DDL v0.1 / hub-config.schema v0.1 | M000 tables and 4 config keys are addenda, held in `hub/store/migrations/M000_coexistence.sql` and `hub/config.py` | [Verified Fact] | schema-migration-plan DR-3, FF-1 note; Stage 16/17 back-reference (RTD-13) |
| DEV-12 | AC-CO-14 "a runtime older than the floor (Python 3.9)" | no 3.9 interpreter on the device; simulated with the hidden `--assume-python` seam; real-interpreter subtest skipped | [Verified Fact] | RTD-18 |
| DEV-13 | AC-CO-13 locale `en_IN` | `en_IN` not installed (`locale -a`: C, C.utf8, POSIX, en_US.utf8); LC_ALL=en_IN.UTF-8 still set (libc fallback) | [Verified Fact] | RTD-18 |
| DEV-14 | Untrusted type belongs to F04 (INC-06), AC-INT-23 "static check fails the build" | runtime guard (`require_trusted`, `@decision_params`) delivered now as ADR-002 B(3); static check not implemented; tested only by supplementary S01 | [Verified Fact] | RTD-16 |
| DEV-15 | deny-list "project" scope | scans `hub/`, `tests/hub/`, root `pyproject.toml` / `requirements*.txt`; the legacy estate is out of scope (`app/gateway_bridge.py` uses `urllib.request`) | [Verified Fact] | RTD-17 |
| DEV-16 | `coexistence_inventory` (BEH-CO-05) not in INC-02 test map | created in M000 (plan row M000) with update/delete-blocking triggers; covered only by supplementary S03 | [Verified Fact] | TST-CO-08 planned later |

## Evidence References
- Commits: `git log --oneline main..stage-15-inc01-harness`.
- Run reports: `docs/15-modernization/evidence/inc01/{final-A,final-B,mut-1..mut-4}_report.json`, `summary.txt`, `checksum-log.txt`.
- INC-02 commits: `git log --oneline main..stage-15-inc02-hub-skeleton`; evidence `docs/15-modernization/evidence/inc02/` (summary.txt, hub-final-A/B reports, golden-compare-baseline.*, char-regression-inc02_report.json, mutation-gate-inc02.txt, checksum-log.txt).

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).
- A-15-02 [Assumption] Building on PROPOSED ADR-002/003/018 and DRAFT F10 at risk is acceptable (E-5, accepted on Dinesh's instruction OD-12/OD-14); not an approval of those ADRs (HAR-11). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-15-01 Whether the harness can run in GitHub CI (fixture is git-ignored) — decided in a later increment / Stage 23.
- U-15-02 Whether the declared DV target values match what INC-04..INC-08 modules will actually produce (resolved when each module replaces its declared probe).

## Unresolved Issues
- DEV-02, DEV-04, DEV-05 carried as open items (see `remaining-technical-debt.md`).
- INC-02: DEV-08..DEV-16 carried as open items (RTD-13..RTD-22).

## Residual Risks
- RR-TL-1 INC-01 proves the harness on this device only; another runtime (3.12, other JDK/Node) is unverified.
- RR-TL-2 golden-compare gate G1 stays red (exit 6) by design until Dinesh decides DV-01..DV-09 (OD-S12-13 / HAR-06); a red gate could be normalised by habit.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
