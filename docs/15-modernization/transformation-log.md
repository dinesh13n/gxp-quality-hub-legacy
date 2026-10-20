---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "transformation-log.md"
version: "v0.4"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; INC-03 (hub DB migrations M001, C2 access & audit chain, backup/restore, first rollback rehearsal) added in v0.3. Stage 15 overall status: IN PROGRESS. INC-04 (policy & rule service: M002, as-found rule sets inactive, activation with a recorded human decision) added in v0.4."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "git log main..stage-15-inc01-harness", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)", "docs/15-modernization/evidence/inc03/", "docs/15-modernization/rollback-rehearsal-inc03.md", "hub/", "tests/hub/", ".fde/orchestrator-decisions.md (OD-15)"]
supersedes: "v0.3 (INC-01 .. INC-03)"
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
| INC-03 | `stage-15-inc03-hub-db-audit` | TB-09..TB-11 | DONE WITH CONDITIONS (see TL-6) | none | see TL-6 |
| INC-04 | `stage-15-inc04-rule-service` | TB-12 | DONE WITH CONDITIONS (see TL-8) | none | see TL-8 |
| INC-05..INC-09 | — | TB-13..TB-21 | NOT STARTED | — | — |

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

### TL-6 INC-03 register entry and steps (branch `stage-15-inc03-hub-db-audit`)
| Increment | Branch | Backlog | Status | Blocking | Exit evidence |
|---|---|---|---|---|---|
| INC-03 | `stage-15-inc03-hub-db-audit` | TB-09 forward-only runner + M001 + backup-before-migrate; TB-10 C2 users/roles (offline `hub.admin user`), audit hash chain, `verify-audit`, anchor via config; TB-11 backup/restore + first rollback rehearsal | DONE WITH CONDITIONS | none | 16/16 planned tests green (40 methods) + 5 supplementary; INC-02 46 methods unchanged (45 ok, 1 skip); harness 134/134, 0 diffs; mutation 15/15; rollback rehearsal 1 PASS (G2 clause not runnable) |

1. [Verified Fact] Read OD log (OD-03a, OD-08, OD-09, OD-11..OD-15), engagement context, Stage 0B write boundaries, Stage 15 prompt; Stage 14 backlog TB-09..TB-11, schema-migration plan (M001 users/roles "[addendum or config — Unknown]"), rollback strategy (INC-03 L1+L2, first rehearsal), gates (TG-3 INC-03 row), feature-flag plan (`audit.anchor_path`, `zone_h.holders`); Stage 12 F09 (BEH-SEC-01..11, AC-SEC-01..21), F10 (G1-G10, BEH-CO-06, AC-CO-10/15), DDL v0.1, audit-record / hub-config schemas, security-spec SEC-2/3, error-handling spec, OpenAPI x-roles; increment-test-map (16 INC-03 tests).
2. [Verified Fact] `c21526b` M001 (`hub/store/forward/`), `hub/store/migrate.py`, `hub/security/*` (canonical JSON, audit chain/anchor/verify, PBKDF2 authenticator + lockout, route authorisation + Zone H check, exposure guard, scan), `hub/ops/*` (backup/restore, release checklist, gate evaluators), `python -m hub.admin`. Sandbox smoke (`~/fde_sbx/s15-inc03/smoke*`): migrate, user create, verify-audit, scan, startup-check, release-checklist, backup/restore all as designed; the smoke exposed that M000 left `deviation_register` deletable -> hold-all trigger added in M001.
3. [Verified Fact] `69aa843` 16 planned tests + 5 supplementary. dev1: TST-SEC-13 b failed (empty tables never fire row triggers - test seeding gap) -> fixed; the run also showed that the INC-02 `_driver.py` recorder reports subTest failures as `ok` (RTD-28).
4. [Verified Fact] reg-B (INC-02 regression) failed TST-CO-04 d: new `sqlite3.connect` calls outside the allowed store/runtime/adapter files. Fixed in `68b93f3` by routing every hub-store connection through `hub.store.db.open_hub` and taking backups with `VACUUM INTO` (no INC-02 test changed). A first reg-B attempt hit ENOSPC on the device (old INC-02 sandbox copies); 5.5 GB of disposable INC-02 `c_pristine/`+`scratch/` copies were removed (WB-10), reports kept (RTD-31).
5. [Verified Fact] At `68b93f3`: final-A/B/C green (summary.txt); INC-01 harness `inc03-regress` 134/134, capture digests == INC-02 regression; mutation gate 4 chunks 15/15 KILLED; rollback rehearsal 1 PASS; backup manifest rc 0 after every session.
6. [Verified Fact] `e61e94c` evidence; then these Stage 15 docs (v0.3) and `rollback-rehearsal-inc03.md` (v0.1).

### TL-7 INC-03 deviations from the Stage 14 plan / specs
| ID | Plan / spec | Actual | Tag | Reason / follow-up |
|---|---|---|---|---|
| DEV-17 | branch `stage-15-inc03-store-audit` (TG-3) | `stage-15-inc03-hub-db-audit` (created by the orchestrator) | [Verified Fact] | matches OD-11 E-6 pattern |
| DEV-18 | `hub user create`, `hub verify-audit` (BEH-SEC-02/06) | `python -m hub.admin user create` / `verify-audit` | [Verified Fact] | `hub/cli.py` frozen by the add-only rule (TST-CO-05 c); fold in later (RTD-25) |
| DEV-19 | schema-migration-plan M001 "users/roles [addendum or config — Unknown]" | DB addendum (principal, principal_role, session, login_attempt) + release tables; permission matrix as data file; holders in config | [Verified Fact] | RD-24; Stage 12 DDL not edited (A-14-08) -> RTD-23 |
| DEV-20 | AC-SEC-01 "every registered route called" | no HTTP server in INC-03; tested on the single authorisation decision point + route registry generated from the OpenAPI x-roles (planned level: static/introspection) | [Verified Fact] | re-test against real handlers in INC-04+ |
| DEV-21 | AC-SEC-09 decision event + policy change | producers do not exist; exercised through the C2 API they must use (`audit.change`) | [Verified Fact] | re-run when INC-04/05 producers exist |
| DEV-22 | AC-SEC-16 "the server starts" | `hub.admin startup-check` runs the start-up guard (no listener yet) | [Verified Fact] | server must call `exposure.check_startup` first (INC-04+) |
| DEV-23 | E-SEC-EXPOSURE-NOT-APPROVED exit 9 (spec) | kept 9 as specified; collides with INC-02 E-CO-DENYLIST-IMPORT = 9 | [Verified Fact] | RTD-24 |
| DEV-24 | BEH-SEC-03 service bearer tokens (rotatable) | service principals can be created and are refused interactive login and Zone H; bearer tokens not built | [Verified Fact] | RTD-27 |
| DEV-25 | AC-CO-15 "recorded pass/fail" | third value `not_run` for gates without an evaluator; it blocks like `fail` | [Verified Fact] | never assumes pass; RTD-32 |
| DEV-26 | AC-CO-09 / BEH-CO-06 "replay-safety suite passes" in the rehearsal | not runnable (G2 suite arrives INC-06) | [Verified Fact] | re-rehearse then |
| DEV-27 | All execution in the sandbox (OD-03a) | once, `python3` imported `hub/security/openapi_routes.py` from the working tree to generate `route_registry.json` (reads only `docs/12-specs/contracts/openapi.yaml`; no legacy code, no `data/` access); stray `__pycache__` removed; checksum rc 0 | [Verified Fact] | process slip, no data impact; later regeneration must run in the sandbox |

### TL-8 INC-04 register entry and steps (branch `stage-15-inc04-rule-service`)
| Increment | Branch | Backlog | Status | Blocking | Exit evidence |
|---|---|---|---|---|---|
| INC-04 | `stage-15-inc04-rule-service` | TB-12 C4 policy & rule service: policy objects (candidate / adopted / accepted-open), table-driven rule sets as data, pure engine, `defaulted` marker (DV-06), AD-06 as-found importer (3 sets, inactive, read-only), activation with a recorded human decision, M002 | DONE WITH CONDITIONS | none | 25/25 planned test IDs green (29 methods: TST-CO-03 + TST-POL-01..23 + TST-POL-25) + 8 supplementary (TST-HUB-INC04-S01..S08) = 37 ok; INC-02/03 suites unchanged (A 45 ok, B 40 ok + 1 skipped, C 5 ok with inner 123 run / 0 egress / 0 model calls); harness 134/134; mutation 8/8 KILLED; backup checksum rc 0 before and after |

1. [Verified Fact] Read the OD log (OD-03/03a, OD-08, OD-12, OD-14..OD-16), Stage 15 prompt, Stage 14 backlog TB-12 / adapter AD-06 / schema plan M002 / gates TG-3 / rollback (INC-04 = L1 + L2 rebuild), `increment-test-map.csv` (25 INC-04 rows), Stage 12 F03 (BEH-POL-01..11, AC-POL-01..25), ADR-007, error catalogue, OpenAPI OP-POL-*, DDL v0.1 (SCH-POLICY / SCH-RULE-SET), the Stage 7 goldens and the INC-02/03 hub code and tests.
2. [Verified Fact] `787c290` design notes (`inc04-design-notes.md`, decisions D-01..D-12) written first so a dead session leaves the reasoning on the branch.
3. [Verified Fact] `a3f529f` skeleton: error codes, M002 SQL + applier (`hub/policy/schema.py`), strict Decimal parsing, pure engine. `55fd4ed` as-found importer (AST/regex cross-checks, sha256 pins), rule-set documents, `PolicyService` (policy objects, adoption through Zone H, clocks, rule-set load / fork / edit, activation with a recorded decision), local Zone H check, `python -m hub.policy`.
4. [Verified Fact] `3013cfd`, `623a975`, `355ef65`: test helpers, 25 planned IDs, supplementary S01..S07. `7439198`: CLI `status` now refuses on M002 drift (found while writing S01). `86f1a9a`: S08 (rollback L2 restore then rebuild).
5. [Verified Fact] First sandbox run of the INC-04 group: 36/36 ok at the first attempt (`evidence/inc04/hub-inc04-first_report.json`). Because that is unusual, an 8-mutant gate was run (below): 8/8 killed, so the tests do detect broken engine, gate, decision, overlap, authority, default-marker, tolerance and immutability code.
6. [Verified Fact] Final runs at code HEAD `86f1a9a`: INC-04 group 37 ok; A 45 ok; B 40 ok + 1 skipped (CO-14 e, no python3.9); C 5 ok (inner full suite 123 run, 122 ok, 2 skipped, 0 egress attempts, `model_calls_total` 0); characterisation harness 134/134 PASS (shipped 15 tests OK as-found). Backup manifest `sha256sum -c` rc 0 before and after (`evidence/inc04/checksum-log.txt`).
7. [Verified Fact] Sandbox copies (`c_pristine`, `scratch`) deleted after every run; device disk 6.0 GB free at start.

### TL-9 INC-04 deviations from the Stage 14 plan / specs
| ID | Plan / spec | Actual | Tag | Reason / follow-up |
|---|---|---|---|---|
| DEV-28 | schema-migration-plan M002 applied by the forward runner (`hub/store/forward/`) | M002 lives in `hub/policy/migrations/` and is applied by `python -m hub.policy migrate` (backup first), recorded with its sha256 in its own insert-only table `policy_schema_migrations`; `schema_migrations` still lists M000, M001 only | [Verified Fact] | a file in `hub/store/forward/` joins `migrate.known_versions()` and breaks the INC-03 test S01 (`applied == ["M001"]`); `migrate.py` and that test are frozen by the add-only rule (TST-CO-05 c). Fold into the main runner at Stage 16/17 with a one-line test update (RTD-37) |
| DEV-29 | "reproduce legacy outputs exactly" (AD-06) | legacy JS matches PARTIAL years: `threshold('APAC', 202)`, `(…, 2)` and `(…, '')` all return 15000 (the 2022 row) via `startsWith(String(year))`; the service needs the 4-digit year text and falls back to 999999 with `defaulted = true` | [Verified Fact] node run in the sandbox (S05) | a prefix match is a defect, not a rule; every golden / grid value (630 JS cases) is identical. Needs Dinesh's preserve-or-fix call under OD-S12-13 (RTD-41) |
| DEV-30 | BEH-POL-11 / AC-POL-23 / TST-POL-23 class B "test both modes" | only the specified default is built: amount 'abc', null, NaN, infinity, boolean, blank -> `E-POL-INPUT-INVALID`; no "preserve" mode. Legacy (golden CT-13): 'abc' -> not allowed, null -> allowed (JS coercion) | [Verified Fact] | OD-S12-13 stays open; the legacy results are pinned in TST-POL-23 so a future preserve mode can be compared |
| DEV-31 | branch `stage-15-inc04-policy-rules` (TG-3) | `stage-15-inc04-rule-service` (created by the orchestrator) | [Verified Fact] | matches OD-11 E-6 pattern |
| DEV-32 | "25 tests: TST-POL-* + TST-CO-03" | TST-POL-24 does not exist in the test map (AC-POL-24 divergence report is R2); 25 IDs = TST-CO-03 + TST-POL-01..23 + TST-POL-25. Divergence report (BEH-POL-10, `GET /rules/divergence`) not built | [Verified Fact] | scope = test map (RTD-39) |
| DEV-33 | OP-POL-01..07 HTTP routes; "same marker in the API response, pack and trace text" (AC-POL-19) | no HTTP server exists; the service API (`PolicyService`) and `python -m hub.policy` (status / migrate / seed / load-as-found / rulesets / policies / evaluate) are the surface; the marker is tested in the result object (= API body), in the trace text; "pack" does not exist yet (INC-08) | [Verified Fact] | Zone H actions are service calls that need an authenticated human session; no CLI path activates anything. Re-test when the HTTP layer / reviewer pack exist (RTD-39) |
| DEV-34 | F02 gate service performs Zone H eligibility | `hub/policy/gate.py` implements the same rules locally (human + role dispositioner + in `zone_h.holders` + re-auth window; E-GATE-NO-HOLDERS / E-GATE-NOT-AUTHORISED; every attempt audited ZONE_H_ATTEMPT) | [Verified Fact] | gate service arrives with INC-05; replace then (RTD-40) |
| DEV-35 | F03 BEH-POL-08: setting the active pointer is ZH-06 | OD-16 adds "activation requires a recorded human decision": implemented as audit record `POLICY_DECISION_RECORDED` (human holder, `decision = activate`, function, ruleset_ref, authority_ref, reason) whose `audit_seq` must be passed to `activate`; checked for kind, actor, holder status, exact function / ruleset, single use and an intact audit chain | [Inference] | mechanism chosen by the build agent (A-15-04-1); Stage 12 addendum + Dinesh's confirmation (RTD-38, RTD-43) |
| DEV-36 | BEH-POL-05 withdrawal / `POLICY_WITHDRAWN` | not built (DDL status enum has no withdrawn value); an adopted window can therefore not be superseded by a new adoption of the same tag in the same window | [Verified Fact] | RTD-39 |
| DEV-37 | error registry (82 codes) | addenda E-POL-DECISION-REQUIRED, E-POL-ASFOUND-DRIFT, E-POL-INVALID; exit codes chosen: E-POL-* 23 (as-found drift 24), E-GATE-* 19; hub.policy reuses 15 (migration drift) and 22 (store not migrated) | [Verified Fact] | RTD-38 |
| DEV-38 | DDL v0.1 verbatim | five DDL tables verbatim + addenda: immutability triggers on `rule_set` / `rule_row`, pointer-integrity trigger on `active_ruleset`, `policy_schema_migrations`; `rule_row.outcome` is JSON `{function, kind(rule/domain/param/register), …}` and a condition value may be `{"$input": name}` | [Verified Fact] | rule-set.schema.json allows any `value`; Stage 12 files not edited in place (HAR-13) -> RTD-38 |
| DEV-39 | All execution in the sandbox (OD-03a) | twice a `python3 -B` snippet imported `hub.policy.engine` from the working tree (pure arithmetic, no legacy code, no `data/` access) and once `py_compile` ran there (pycache removed); checksum rc 0 | [Verified Fact] | process slip like DEV-27; no data impact |
| DEV-40 | INC-03: TST-CO-12 inner suite 86 tests | 123 tests (122 ok, 2 skipped); group C 103-115 s, inside the 180 s device cap but with less headroom | [Verified Fact] | RTD-44 |

## Evidence References
- INC-04 evidence: `docs/15-modernization/evidence/inc04/` (hub-final-{A,B,C,INC04} reports + unittest results, hub-final-C_inner-egress-run.json, char-regression-inc04_report.json, mutation-gate-inc04.txt, checksum-log.txt); design notes `docs/15-modernization/inc04-design-notes.md`; commits `git log --oneline main..stage-15-inc04-rule-service`.
- INC-03 evidence: `docs/15-modernization/evidence/inc03/` (summary.txt, hub-final-{A,B,C} reports, char-regression-inc03_report.json, mutation-gate-inc03.txt, checksum-log.txt, rollback-rehearsal-1/); `docs/15-modernization/rollback-rehearsal-inc03.md`; commits `git log --oneline main..stage-15-inc03-hub-db-audit`.
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
- INC-03: DEV-17..DEV-27 carried as open items (RTD-23..RTD-36).
- INC-04: DEV-28..DEV-40 carried as open items (RTD-37..RTD-45); DEV-29 / DEV-30 need Dinesh's OD-S12-13 decision, DEV-35 his confirmation of the decision mechanism.

## INC-05 (branch `stage-15-inc05-decision-record`)
Decision record service (hash-chained, append-only `decision_events`, rebuildable `case_state`), crosswalk, backfill of the 125 baseline cases (seed 4100, OD-09), shared Zone H gate. All new files under `hub/`, `tests/hub/`, `docs/15-modernization/`; legacy code and `data/` byte-identical (Verified Fact: `git diff --name-status main` shows only A outside docs).

| ID | Deviation / choice | Label |
|---|---|---|
| DEV-41 | DEV-34 closed by subclass `GatedPolicyService` (overrides `_zone_h`); frozen `hub/policy/gate.py` and its import stay because non-add edits are barred outside docs. Physical removal is RTD-46. | Verified Fact |
| DEV-42 | M003 applied by `hub.decision.schema` with its own table `decision_schema_migrations` (INC-04 D-02 precedent); needs M001+M002; `schema_migrations` untouched. | Verified Fact |
| DEV-43 | Plan text says LEGACY_IMPORTED; DDL/spec use CASE_IMPORTED; DDL followed. | Inference |
| DEV-44 | FACT_RECEIVED written only when `received_at` is given at create (AC-DEC-01 seq 1..6). | Assumption |
| DEV-45 | OD-S12-15 `rule` derivation mode not built; only `human_only`. Case creation disabled by default (OD-S12-19). | Verified Fact |
| DEV-46 | CLOSE_EXCEPTION event is itself the closing transition (ZH-04). | Assumption |
| DEV-47 | Evidence access matrix: `restricted` readable by quality_lead, compliance, dispositioner; others by all four read roles (A-15-05-1). | Assumption |
| DEV-48 | Imported events use `occurred_at = cases.created_at` as a proxy; as_of for imported cases is therefore a proxy. Legacy `events` rows are not imported. | Verified Fact |
| DEV-49 | Exit codes E-DEC-* 25, E-ID-* 26, E-DEC-BACKFILL-MISMATCH 27 and extra error codes / settings keys are INC-05 choices needing a Stage 12 addendum. | Verified Fact |
| DEV-50 | Stale re-auth now raises E-GATE-REAUTH-REQUIRED (401) via the shared gate; the INC-04 local copy raised E-GATE-NOT-AUTHORISED. | Verified Fact |
| DEV-51 | `hub/security/authz.py` remains a third copy of Zone H logic (frozen). | Verified Fact |
| DEV-52 | INC-05 test modules skip in TST-CO-12's inner run; separate E05EGRESS test covers the guard. | Verified Fact |
| DEV-53 | One import check ran in the working tree (like DEV-27/39); no data or pycache written. | Verified Fact |

Backfill result (Verified Fact, sandbox): 125 cases, 250 events, states CLOSED 36 / ESCALATED 9 / OPEN 42 / REOPENED 8 / UNDER_REVIEW 30; 8 REOPENED cases marked `LEGACY_UNEVIDENCED_REOPEN`; projection mismatches 0; CT-02 priority distribution archive 36 / queue 70 / review 17 / urgent 2 through the inactive as-found rule set. Crosswalk rule run: LT-01 42, LT-02 21, LT-03 125, LT-04 173, LT-05 30 links; 8,394 feed and 1,170 document orphans reported, none guessed.
`zone_h.holders` stays empty in shipped config; tests use synthetic holders (synthetic, unvalidated).

## INC-06 (branch `stage-15-inc06-intake`)
Data intake: source-contract validation (record_only default, enforce per source), idempotent intake by the OD-18 natural key, re-delivery handling, quarantine, untrusted text, hash-chained audit. Only added files under `hub/`, `tests/hub/`, `docs/15-modernization/`; legacy code and `data/` byte-identical (Verified Fact).

| ID | Deviation / choice | Label |
|---|---|---|
| DEV-54 | NOOP_DUPLICATE precedes validation (SBR-INT-04), so replays of quarantined originals are NOOP: unsupported outcomes (223) plus NOOP (67) account for the spec's 224-row figure region, and enforce gives 8,500 QUARANTINED + 67 NOOP, not the spec text counts. | Verified Fact |
| DEV-55 | Contract bindings are `policy_events` rows (ZH-10 gate), not config keys; default record_only (OD-S12-11). | Verified Fact |
| DEV-56 | `intake_run_event` is a subset of the DDL `run_event`; INC-07 owns the full table (RTD-53). | Verified Fact |
| DEV-57 | Unknown gateway partner maps to MISSING_ENVELOPE_FIELD. | Inference |
| DEV-58 | Legacy REJECTED negative quantity vs hub FLAG (NEGATIVE_VALUE) is a recorded difference, pending OD-S12-13. | Verified Fact |
| DEV-59 | M004 applied outside `schema_migrations` (own table, D-02); new tables are not in the frozen RETAINED_TABLES list except raw_intake / intake_outcome (RTD-52 style gap, RTD-54). | Verified Fact |
| DEV-60 | Exit code 28 and E-INT-* codes, `gateway.retries` setting: INC-06 choices needing a Stage 12 addendum (RTD-55). | Verified Fact |
| DEV-61 | Gateway client sleeps via `threading.Event().wait` because adapters may not import `time` (TST-CO-13 b); found by the regression run, fixed. | Verified Fact |
| DEV-62 | INC-06 modules skip in TST-CO-12's inner run; E06EGRESS covers the guard (as DEV-52). | Verified Fact |
| DEV-63 | `source_message` is the hub name for legacy `external-feed`; the 22 document bodies are out of scope (INC-07). | Verified Fact |

## INC-07 (branch `stage-15-inc07-runs-metrics`)
Scheduled-run orchestration WITHOUT a scheduler (OD-19), run records, deterministic metrics with definition tags, structured logs and observability reports. Only added files under `hub/`, `tests/hub/`, `docs/15-modernization/`; legacy code and `data/` byte-identical (Verified Fact, `git diff --name-status main` shows only `A`).

| ID | Deviation / choice | Label |
|---|---|---|
| DEV-64 | The schedule flag is the latest `SCHEDULE_CHANGED` policy event written through Zone H ZH-09, not a config key; config `schedule.enabled: true` is refused. | Verified Fact |
| DEV-65 | Scheduler OFF (OD-19): `trigger = scheduled` is a caller-supplied label accepted only with the flag on; AC-RUN-01 is exercised by an explicit call at a controlled test-clock time. Scheduler vs HAR-10 stays open. | Verified Fact |
| DEV-66 | Full `run_event` table created by M005; `intake_run_event` (INC-06) stays as the intake's own per-ingest record (RTD-53 closed for run records). | Verified Fact |
| DEV-67 | run-record.schema.json requires an integer `batch_size` >= 1: non-batching jobs report `max(1, inputs_seen)`. | Verified Fact |
| DEV-68 | Exit codes 29 (E-RUN-*) and 30 (E-MET-*); E-RUN-UNKNOWN-JOB is also used for an unknown run id (RTD-58). | Verified Fact |
| DEV-69 | Backlog by site implements the state-based D-OPS definition only; D-EVID returns E-MET-NOT-AVAILABLE (needs the evidence check). A date-only `as_of` means end of day. | Verified Fact |
| DEV-70 | CLI results on stdout, JSON log lines on stderr. | Verified Fact |
| DEV-71 | Built-in KPI definitions are registered on first use (insert-only catalogue rows), so even an unstored computation may add definition rows. | Verified Fact |
| DEV-72 | TST-RUN-04, TST-MET-02/12/21 belong to INC-08, TST-MET-19/20 to INC-09; not run here (service-level equivalents S02, S06, S07). | Verified Fact |
| DEV-73 | INC-07 modules skip in TST-CO-12's inner run; E07EGRESS covers the guard (as DEV-52, DEV-62). | Verified Fact |
| DEV-74 | Process slip (as DEV-53): one pure-import check of hub modules ran in the working tree early in the increment (python -B, no data touched, no files written); all later syntax checks used `ast.parse`. | Verified Fact |

Steps (in order): M005 schema + applier; run service, jobs, sources, schedule flag; observability log and collectors; metrics package and detector; CLIs and reports; test helpers; 39 planned tests; first full run had 13 failing tests (3 FAIL, 10 ERROR) from problems in new code or tests (session expiry after test-clock moves, unseeded KPI registry, one-batch-per-run semantics, a too-broad regex), all fixed; supplementary tests S01..S19; regression groups.

## INC-08 (branch `stage-15-inc08-http-reviewer`)
Loopback HTTP surface, reviewer queue and the disposition gate (mode `none` by default, human-only dispositions through Zone H). Only added files under `hub/`, `tests/hub/`, `docs/15-modernization/`; legacy code and `data/` byte-identical; `zone_h.holders` empty in the shipped configuration.

| ID | Deviation / choice | Label |
|---|---|---|
| DEV-75 | Loopback only: a non-loopback bind is refused even with an approval in the config; non-loopback peers are dropped; no TLS claim. Exposure and TLS are Stage 24 decisions. | Verified Fact |
| DEV-76 | M006 has its own table `web_schema_migrations` and four insert-only tables (`service_token`, `service_token_revocation`, `rule_trace`, `flag_action`); forward-only; rollback by backup restore. | Verified Fact |
| DEV-77 | The 11 INC-08 tests filed under TST-DEC/INT/MET/RUN/SEC are named `test_I8_<FAMILY>_<NN>_...` so the frozen selectors keep their sizes; the runner `ids=` line omits them. | Verified Fact |
| DEV-78 | INC-08 modules skip in TST-CO-12's inner run; `E08EGRESS` covers the guard; real loopback sockets are the documented exception (confined to 127.0.0.1, the guard already allows it). | Verified Fact |
| DEV-79 | Metric GET values are computed with `store=False` on a clock pinned to the data horizon, so identical GETs are identical (AC-MET-21) and `computed_at` is a data instant. | Verified Fact |
| DEV-80 | OP-MET-01 returns `{"items": [...]}` (one series per clock); OP-MET-03 takes `kind=exception_rate` and requires `as_of` (E-MET-DEFINITION-REQUIRED otherwise); OP-MET-08 supports sum/min/max/compare (ratio and difference are E-MET-NOT-AVAILABLE); OP-MET-02 takes `source` as a name looked up in the app's registered sources. | Verified Fact |
| DEV-81 | Search (OP-REV-03) is the fallback engine only, disabled by default, with an injected document provider; FTS5 and the corpus loader are INC-09 (partial coverage of R2, RTD-68). | Verified Fact |
| DEV-82 | OP-POL-07, OP-INT-04, OP-ID-04, OP-ID-05, OP-MET-06 answer 501 E-REQ-NOT-IMPLEMENTED; OP-REV-04 is E-REV-DRAFTS-DISABLED; OP-MET-05 is E-MET-NOT-AVAILABLE. They write nothing. | Verified Fact |
| DEV-83 | OP-INT-01 envelope uses the hub's canonical delivery names (`source_key`, `partner`, `schema_rev`, `source_ts`, `ref_id`, `record_kind`, `payload_text`); source alias `source_messages` maps to `source_message`; an `idempotency_key` gives a deterministic run id (`HTTP-<hex>`), so a replay is not ingested twice. | Verified Fact |
| DEV-84 | Login returns `token` and `csrf_token` in the body besides the HttpOnly SameSite=Strict cookie; no `Secure` flag over loopback HTTP; the login POST has no CSRF token (A-INC08-3/4/5). | Assumption |
| DEV-85 | An anonymous Zone H call with an unknown action name is 422 from the choke point (no effect); with a well-formed action it is 401; an anonymous UI disposition post is a 401 page, not a redirect. | Verified Fact |
| DEV-86 | The web app opens the store through `hub.store.db.open_hub`, not `sqlite3.connect` (TST-CO-04 d). | Verified Fact |
| DEV-87 | `WebApp.last_exception` is a diagnostic hook for tests (never serialised); an unexpected 500 in a test fails with its traceback. | Verified Fact |
| DEV-88 | Process notes (as DEV-53, DEV-74): `data/documents/source_documents.jsonl` and the legacy schema were inspected read-only (immutable mode) from the sandbox copy to build the search fixture; the pure `hub/intake/untrusted_lint.py` source was executed once from the working tree to list its findings (no data touched, no file written). All other syntax checks used `ast.parse`; all tests ran in sandbox copies. | Verified Fact |
| DEV-89 | AC-NFR-13 names "44 regex-hit strings", for which no standalone fixture exists; the 86 shipped feed rows, the 22 injection documents and 10 injection variants are used (TST-NFR-13). | Verified Fact |

Steps (in order): M006 + applier; web helpers and dispatcher; 48 API handlers and reviewer pages; loopback server and CLI; gate and review services; test helpers; TST-GATE, TST-REV, I8_ HTTP tests; NFR helpers and tests; supplementary and egress modules; documents.

## INC-09 (branch `stage-15-inc09-search-corpus`)
R2 scope (TB-21 and the R2 parts of C2/C3/C4/C6/C7/C9): FTS5 search behind `search.fts` (default off) with a runtime-detected fallback, derived corpus index (drop = rollback), deterministic template drafts (default off), and the five operations that answered 501 in INC-08. Entry: OD-22. Only added files under `hub/`, `tests/hub/`, `docs/15-modernization/` (non-add edits only in docs/15-modernization); legacy code and `data/` byte-identical; `zone_h.holders` empty in the shipped configuration. Design: `inc09-design-notes.md`.

| ID | Deviation / choice | Label |
|---|---|---|
| DEV-90 | The plan's optional "M006 FTS5 virtual table" is M007 (M006 is INC-08's) with its own table `search_schema_migrations`; M007 holds regular tables only; the FTS5 virtual tables are derived objects built by the corpus loader when the runtime offers FTS5 + trigram. | Verified Fact |
| DEV-91 | AC-SEC-19 "read through the API": the finance_read masking of `account_id` is verified at the protection layer, because no registered route serves case fields to finance_read (frozen registry; OP-ID-04 roles exclude finance_read). Restricted / missing-level handling is verified through the API (search, joined view). | Verified Fact |
| DEV-92 | AC-ID-13 counts 3 entities (batch, deviation, CAPA). The shipped data also links LAB00000000 to BT00000000 (LT-03): with LT-01/LT-02 the set is 3 from every member, with LT-03 it is 4 from every member; both are tested. | Verified Fact |
| DEV-93 | Both engines rank with the bm25 formula (FTS5 bm25() and a Python reproduction, rounded to 1e-9) and use the same escaped excerpt instead of FTS5 snippet(); so the fallback order equals the FTS5 order in general, not only for the AC-REV-16 tie fixtures. | Verified Fact |
| DEV-94 | C3 rule (BEH-SEC-10, MA-2) implemented for OP-REV-03 and OP-ID-04: a permitted result containing restricted rows needs a non-empty `reason` query parameter (E-SEC-REASON-REQUIRED) and is audited as C3_READ. The parameter is not in the OpenAPI (Stage 12 addendum). The INC-08 SearchService is unchanged; the rule applies in R2WebApp only. | Verified Fact |
| DEV-95 | The 420 archive items carry no access level: indexed as `restricted` (MA-1), `doc_id` ARC-<stem>, effective date from the "Source date" text, locale / reference null. | Verified Fact |
| DEV-96 | `latest_only` collapses versions per doc_id (INC-08 behaviour), not per `reference` (BEH-REV-04 wording); the shipped 1,200 doc ids are distinct, so there is no observable difference on the shipped corpus. | Verified Fact |
| DEV-97 | Divergence: the batch set's `amount_over_limit` needs a threshold from region + policy_code; the cases carry no policy_code, so it is null (not comparable) for all 125; divergence is computed over non-null outputs: 3 of 125 cases (python vs js). Count recorded in the audit record RULE_DIVERGENCE_REPORTED. | Verified Fact |
| DEV-98 | Freshness (PNFR-04) is served on the OP-INT-04 path with `?view=freshness&as_of=` (no separate registry operation); thresholds are config `intake_reports.*` with Assumption values 4 h / 24 h. | Verified Fact |
| DEV-99 | The consistency check is an operator command / service call (the registry has only the GET OP-ID-05); OP-ID-05 lists findings plus the 'no consistency policy adopted' statement. | Verified Fact |
| DEV-100 | OP-MET-06 returns one metric-value-shaped document (overall unmatched rate as `value`, per-source figures in `detail.per_source`), computed as of the data horizon and not stored (INC-08 D-10 pattern). | Verified Fact |
| DEV-101 | R2WebApp is an additive subclass served by `python -m hub.r2 serve`; `python -m hub.web serve` still serves the R1 WebApp (frozen). One entry point must be chosen before any exposure (RTD-81). | Verified Fact |
| DEV-102 | Template drafts: two deterministic templates in `hub/r2/templates.json` (field sets are an Assumption, A-INC09-4); `templates.enabled` default false. | Assumption |
| DEV-103 | New codes / keys / audit actions (inc09-design-notes D-16): E-REV-INDEX-ABSENT 409, E-R2-INPUT-INVALID 422 (exit code 32, INC-09 family), E-SEC-REASON-REQUIRED (exit 19). | Verified Fact |
| DEV-104 | TST-REV-15's labelled set (61 queries) is generated from corpus metadata, not by a human (OPD-12 proposal); recall@5 0.3776 on both engines is a baseline only, no threshold. | Verified Fact |
| DEV-105 | The 20 planned tests are named `test_I9_<FAMILY>_<NN>_...` so the frozen selectors keep their sizes; INC-09 modules skip in TST-CO-12's inner run and run under the egress guard in E09EGRESS (no socket is opened). | Verified Fact |
| DEV-106 | Joined view: a denied document is `{type, access}` without id; links touching it are hidden; `depth_capped` flags a branch cut by the depth cap (an addition to `truncated`). | Verified Fact |
| DEV-107 | Process notes: corpus and legacy facts were inspected read-only from the Stage 0A BACKUP copy (`../_data-backup-2026-10-17/data`, sqlite `mode=ro` URI and plain file reads) to design fixtures - never the working-tree `data/`; checksum rc 0 afterwards. No hub code was imported from the working tree (syntax checks with `ast.parse`); every test ran in a sandbox copy that was deleted after the run. | Verified Fact |

Steps (in order): M007 + applier, settings, FTS probe, text rules, corpus loader, R2 search service; R2 services (protection, divergence, intake reports, joined view, consistency, source quality, drafts, facts), R2 API handlers, R2WebApp, CLIs; test helpers; 20 planned tests; 13 supplementary tests and the E09EGRESS module; documents; final runs.

## Residual Risks
- RR-TL-1 INC-01 proves the harness on this device only; another runtime (3.12, other JDK/Node) is unverified.
- RR-TL-3 INC-03 audit tamper evidence is limited by an unsigned same-host anchor file and undetectable tail truncation after the last anchor (R-SEC-1).
- RR-TL-2 golden-compare gate G1 stays red (exit 6) by design until Dinesh decides DV-01..DV-09 (OD-S12-13 / HAR-06); a red gate could be normalised by habit.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
| v0.3 | 2026-10-18 | claude-fde-agent | INC-03 (branch `stage-15-inc03-hub-db-audit`): sections added; earlier content unchanged. |
| v0.4 | 2026-10-18 | claude-fde-agent | INC-04 (branch `stage-15-inc04-rule-service`): sections added; earlier content unchanged. |
| v0.5 | 2026-10-19 | claude-fde-agent | INC-05 (branch `stage-15-inc05-decision-record`): sections added; earlier content unchanged. |
| v0.6 | 2026-10-19 | claude-fde-agent | INC-06 (branch `stage-15-inc06-intake`): sections added; earlier content unchanged. |
| v0.7 | 2026-10-19 | claude-fde-agent | INC-07 (branch `stage-15-inc07-runs-metrics`): sections added; earlier content unchanged. |
| v0.8 | 2026-10-19 | claude-fde-agent | INC-08 (branch `stage-15-inc08-http-reviewer`): sections added; earlier content unchanged. |
| v0.9 | 2026-10-20 | claude-fde-agent | INC-09 (branch `stage-15-inc09-search-corpus`): sections added; earlier content unchanged. |
