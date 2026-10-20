---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "refactoring-decisions.md"
version: "v0.4"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; INC-03 (hub DB migrations M001, C2 access & audit chain, backup/restore, first rollback rehearsal) added in v0.3. Stage 15 overall status: IN PROGRESS. INC-04 (policy & rule service: M002, as-found rule sets inactive, activation with a recorded human decision) added in v0.4."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)", "docs/15-modernization/evidence/inc03/", "docs/15-modernization/rollback-rehearsal-inc03.md", "hub/", "tests/hub/", ".fde/orchestrator-decisions.md (OD-15)"]
supersedes: "v0.3 (INC-01 .. INC-03)"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
Design decisions taken while building INC-01. None changes legacy code; all are reversible by deleting `tests/characterization/` (rollback L1).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Decision | Alternatives | Rationale / evidence | Approval | Tag |
|---|---|---|---|---|---|
| RD-01 | Subprocess-per-capture in full sandbox copies; no refactor of `app.store` | refactor for injection; `importlib.reload` | HD-1 option B; import-time DB binding (WB-F2) and ≥5 repo-relative writers (WB-F1) | OD-11 E-1 (Dinesh) | [Verified Fact] |
| RD-02 | Fixture `data/` copied from the Stage 0A backup (`../_data-backup-2026-10-17/data`), not from the working tree; code copied read-only from the working tree without `.git`/`data/` | copy working-tree `data/`; regenerate | "never touch working-tree data/"; backup manifest == working tree (rc 0); partner tables are not regenerable (CT-14) so seeding alone cannot rebuild FX-BASE125 | within OD-03a | [Inference] |
| RD-03 | Hash gate on all 1,512 data files (`FX-BASE125.sha256` = byte copy of backup manifest) plus explicit check of `legacy.sqlite3` = c254649f… | gate only the two DBs | lake files feed CT-07/09/11/14; Stage 0B noted un-checksummed lake files as a gap, now covered | — | [Verified Fact] |
| RD-04 | Supplementary captures (SQL file itself, readiness scripts, write methods on all routes, static scan) get their own versioned golden `inc01/supplement_golden_v1.json` captured once on unmodified code; Stage 7 goldens never edited | extend Stage 7 golden; skip | CT plan CT-12/15/16 ask for more than Stage 7 captured; CT-H4 forbids in-place edits | reviewed in PR (OD-13) | [Inference] |
| RD-05 | Normalisation limited to N1 sandbox paths, N2 interpreter path, N3 JVM banner line, N4 tail-window suffix compare; everything data-derived compared exactly | broader regex / ignore stderr | CT-H3; only 2 of 134 checks need N1/N4 on this device | list changes only via reviewed PR | [Verified Fact] |
| RD-06 | Determinism measured on a canonical digest (normalised, tail fields trimmed to 400 chars) of each capture | raw byte compare | raw batch bytes embed the sandbox label; observed digest drift with label length before RD-06 (commit e1eb1d2) | — | [Verified Fact] |
| RD-07 | No `__init__.py` in `tests/characterization/` | package it | keeps CI/verify.sh discovery identical (15 tests) | — | [Verified Fact] |
| RD-08 | Each CT is a `unittest.TestCase`, each golden element a `subTest`; harness exits 0/1/2 | pytest | stdlib only (HAR-07/08) | — | [Verified Fact] |
| RD-09 | Mutant counts as KILLED if any CT check differs or any capture exits non-zero; result records which | CT diff only | a crash is an observable behaviour change; in practice all 15 were killed by CT diffs | — | [Verified Fact] |
| RD-10 | C3 delivered as `ac_links` metadata with proposed AC-CO-L04..L16 | edit Stage 12 acceptance criteria | Stage 12 docs not edited in place (OD-10 pattern); TB-05 specifies test metadata | addendum pending | [Inference] |
| RD-11 | Four captures run concurrently per run; mutants sequential | all sequential | separate sandbox copies and ephemeral ports make them independent; determinism verified (6 runs) | — | [Verified Fact] |

### INC-02 decisions
| ID | Decision | Alternatives | Rationale / evidence | Approval | Tag |
|---|---|---|---|---|---|
| RD-12 | New top-level `hub/` package beside the legacy estate, run as `python -m hub`; no `pyproject.toml` change | `src/` layout + entry point | E-2b and OD-S12-12 defaults (OD-14); avoids HAR-07 | OD-14 (accepted on Dinesh's instruction, OD-12) | [Verified Fact] |
| RD-13 | Legacy stores read only via per-run snapshot copies opened `mode=ro&immutable=1` plus an SQLite authorizer (deny all but SELECT/READ/FUNCTION/RECURSIVE and read pragmas) plus pinned sha256 and table/column lists | `mode=ro` on the source file | AS-2 rules 3-4; immutable snapshot avoids lock contention with legacy writers (TR-09); authorizer is defence in depth | E-5 at risk | [Verified Fact] |
| RD-14 | golden-compare new-side providers: `baseline_ro` (computed over RO snapshots) and `declared` (F10-2 target) until modules exist | wait for modules; compare legacy-vs-legacy | lets AC-CO-01/02 be proven now; declared probes are replaced per increment (DEV-08) | — | [Inference] |
| RD-15 | A difference counts as approved only if the DV row is `approved`, has a non-empty `approval_ref` AND its legacy/new values equal the observation (canonical JSON) | match on golden_ref only | prevents a stale approval from covering a changed behaviour (TST-CO-01 d) | — | [Verified Fact] |
| RD-16 | No product command approves or edits deviations; approval_ref only references Dinesh's decision outside the product | `hub deviations approve` | BEH-CO-02; STOP-07 spirit (no automated approvals) | — | [Verified Fact] |
| RD-17 | Sandbox guard refuses any path inside a directory holding `.git`, plus HUB_WORKTREE_ROOT, the backup, ancestors, `/` and `$HOME` | env var only | protects the original repo even if the env var is missing | — | [Verified Fact] |
| RD-18 | Egress guard patches connect/connect_ex/sendto/getaddrinfo; loopback/AF_UNIX allowed; hostnames never resolved; installed at every CLI start | patch connect only | DNS resolution itself is egress; children spawned by tests are also guarded | — | [Verified Fact] |
| RD-19 | Exit codes for codes without a specified exit: 9 deny-list, 10 legacy write, 11 egress, 12 untrusted use, 13 schema drift, 14 tripwire, 15 migration drift, 3 kill switch, 2 fixture/config | reuse 1 | distinguishable in CI; needs Stage 12 addendum (RTD-13) | — | [Verified Fact] |
| RD-20 | `tests/hub/` without `__init__.py`; runner reuses INC-01 `harness.build_pristine` (hash-gated FX-BASE125 copy) and runs tests inside the copy with HUB_* env vars | own copy logic | one proven sandbox path; shipped CI discovery unchanged | — | [Verified Fact] |
| RD-21 | AC-CO-12 "full acceptance suite" = TST-CO-12 e re-runs all other INC-02 tests in a child with the egress guard installed (recursion guard HUB_EGRESS_INNER) | patch only inside one test | literal reading of AC-CO-12 | — | [Verified Fact] |
| RD-22 | Hidden CLI test seams `--assume-python`, `--assume-sqlite`, `--observations` | monkeypatch in-process | exercises the real start-up / CLI path; documented as test-only | — | [Verified Fact] |
| RD-23 | Untrusted runtime guard delivered in INC-02 (ADR-002 B(3)) | defer to INC-06 | requested in INC-02 scope; static type check deferred (RTD-16) | — | [Verified Fact] |

### INC-03 decisions
| ID | Decision | Alternatives | Rationale | Approval | Tag |
|---|---|---|---|---|---|
| RD-24 | **Users/roles in the DB** (M001 addendum: principal, principal_role, session, login_attempt); permission matrix as versioned DATA (`hub/security/route_registry.json` generated from the OpenAPI x-roles = SEC-3); Zone H holders in CONFIG (`zone_h.holders`, default []) | users in a config file; matrix in DB | lockout counters and sessions need durable transactional state audited in the same transaction (BEH-SEC-02/05); credentials in config files spread secrets; SEC-2 says "holder list is configuration"; matrix "is data" (BEH-SEC-04) | resolves the Stage 14 M001 Unknown; DDL addendum (A-14-08) | [Inference] |
| RD-25 | Forward migrations in `hub/store/forward/`, applied only by `hub.admin migrate` after an automatic pre-migration backup; M000 stays with `db.open_hub` | put M001 in `migrations/` | INC-02 `init` contract (S03: M000 only) preserved; add-only rule; backup-before-migrate needs an explicit operator step | — | [Verified Fact] |
| RD-26 | Operator commands under `python -m hub.admin` | edit `hub/cli.py` | add-only rule (TST-CO-05 c) | — | [Verified Fact] |
| RD-27 | Hash = sha256(prev_hash_hex ‖ canonical(record)); record = all SCH-AUDIT fields except prev_hash/hash (incl. audit_seq, details as object); genesis 64×"0"; canonical JSON sorted keys, `(",",":")`, ensure_ascii; UTC `…ffffffZ` | hash raw row | BEH-SEC-05 literal; seq inside the hash makes moves detectable | — | [Verified Fact] |
| RD-28 | `verify` classifies the first break: gap -> missing_record; link/content mismatch -> reordered if the row verifies at another position, else altered_record; anchored head absent/different -> head_mismatch | report "broken" only | AC-SEC-11 asks for the kind | — | [Verified Fact] |
| RD-29 | Anchor = JSON-lines file, append + fsync, every `audit.anchor_every` records and at the end of every `hub.admin` run; `audit.anchor_path` REQUIRED (no default), absolute, outside the DB dir, sandbox-safe | derived default path | OD-S12-18 default "set in config" (OD-15); an implicit path could land beside the DB | OD-15 | [Verified Fact] |
| RD-30 | Session tokens / salts from `os.urandom` (not `secrets`) | `secrets` | TST-CO-13 b forbids importing `secrets` in hub/; both use the OS CSPRNG | — | [Verified Fact] |
| RD-31 | Lockout state = insert-only `login_attempt` rows with a `lockout_started` marker; failures counted since the last success/lockout inside the window; locked attempts do not extend the lock; dummy PBKDF2 for unknown/locked principals; generic errors | counter column on principal | hold-all, auditability, timing equalisation | values = A-12-F09-1 | [Verified Fact] |
| RD-32 | `audit.change()` = BEGIN IMMEDIATE, change, audit insert, COMMIT; audit failure -> ROLLBACK + E-SEC-AUDIT-WRITE-FAILED; credential-like keys refused in `details` | audit after commit | AC-SEC-14, BEH-SEC-07 | — | [Verified Fact] |
| RD-33 | All hub-store connections via `db.open_hub`; backups with `VACUUM INTO` from that connection (facts read before/after, mismatch -> refuse) | sqlite3 backup API on a 2nd connection | TST-CO-04 d single connection point (found by reg-B); SQLite floor 3.37 supports VACUUM INTO | — | [Verified Fact] |
| RD-34 | Restore verifies first, sets the current store + anchor aside under `pre-restore/<ts>/`, never deletes | overwrite | hold-all (OD-S12-09/OD-15); forensic copy of a tampered store | OD-15 | [Verified Fact] |
| RD-35 | Release checklist rows insert-only, results pass/fail/not_run, a DB trigger refuses `ready` unless 10 passes; a new release id per attempt | mutable rows | AC-CO-10 defence in depth; evidence immutability | — | [Verified Fact] |
| RD-36 | Exit codes: 16 scan findings, 17 audit tamper, 18 audit write failed / secret in audit, 19 auth errors, 20 release blocked, 21 backup invalid, 22 store not migrated; 9 exposure (as specified) | reuse 1 | distinguishable; needs Stage 12 addendum | — | [Verified Fact] |
| RD-37 | CONFIG_LOADED (config sha256 + holders + anchor_every) appended at the start of every store-opening `hub.admin` run (after migration for `migrate`, after verification for `restore`) | only on config change | AC-SEC-21 "process restarted" | — | [Verified Fact] |
| RD-38 | Full-increment rollback rehearsed with `git archive main hub` into the sandbox | `git checkout` | no checkout/switch allowed; working tree untouched | — | [Verified Fact] |

### INC-04 decisions
| ID | Decision | Alternatives | Rationale | Approval | Tag |
|---|---|---|---|---|---|
| RD-39 | New package `hub/policy/` with its own CLI `python -m hub.policy`; no existing file touched | extend `hub/cli.py`, `hub/store/migrate.py` | add-only rule (TST-CO-05 c) | — | [Verified Fact] |
| RD-40 | M002 in `hub/policy/migrations/`, applied by `hub.policy.schema` after a backup, recorded in `policy_schema_migrations` | `hub/store/forward/M002_*.sql` | the forward directory is scanned by `migrate.known_versions()`; INC-03 S01 (frozen) pins `applied == ["M001"]` | — | [Verified Fact] (DEV-28) |
| RD-41 | Rule sets are data: rows `{row_id, ordinal, conditions[], outcome{function, kind, …}, is_default}`; kinds rule / domain / param / register; first match wins by ordinal; conditions ANDed; value may be `{"$input": field}` | code per rule set; columns for domains / params | DDL v0.1 unchanged; one engine for three very different legacy rules | A-14-07 | [Inference] |
| RD-42 | Engine is a pure function (imports decimal / re only); numbers are exact `Decimal` parsed strictly (bool, NaN, infinity, None, odd strings rejected) | float arithmetic as legacy; permissive `Decimal(str)` | AC-POL-22 purity, AC-POL-23, no silent coercion | — | [Verified Fact] |
| RD-43 | `defaulted` precedence NULL_INPUT > UNKNOWN_INPUT_VALUE > matched default row; the as-found value is always kept; the PRIORITY catch-all row is not a "default row" | mark every fall-through | AC-POL-19/20/21 | OD-S12-04 | [Verified Fact] |
| RD-44 | `as-found-batch` = the row-level predicate; threshold is an input or looked up by (region, policy_code) among `active = 1` register rows; one result per input; `valid_from` / `valid_to` ignored as in legacy | reproduce the JOIN; honour validity windows | AC-POL-15, BB-07 fan-out is an adapter defect | OD-S12-13 | [Verified Fact] |
| RD-45 | Importer reads legacy sources as text / data, sha256-pins them, cross-checks constants (AST for Python, regex for JS), reads the register through the INC-02 read-only snapshot adapter; reload is a no-op, divergence is E-POL-ASFOUND-DRIFT | import the legacy modules; call node | AD-06 "never imported as code"; fail closed | A-14-07 | [Verified Fact] |
| RD-46 | Activation = `record_activation_decision` (audit record) + `activate(decision_seq)`; decision is single-use, tied to function + ruleset, by a human holder, in an intact chain; refusals are audited | single Zone H call; free-text approval reference | OD-16 "recorded human decision", F03 BEH-POL-08 | A-15-04-1 | [Inference] |
| RD-47 | Zone H check implemented locally in `hub/policy/gate.py` (same rules as F02) | wait for INC-05 | the policy actions are needed now; one place to replace | — | [Verified Fact] |
| RD-48 | Editing a rule row = new version of a CUSTOM set (copy of any set); as-found sets can only be forked; `rule_set` / `rule_row` are immutable by trigger | in-place edit | BEH-POL-07, AC-POL-11/25, versioned history | — | [Verified Fact] |
| RD-49 | Every policy change = one transaction of data + `policy_events` + audit record (`audit.change`); a denied attempt writes its own audit record before the error | audit after commit | AC-SEC-14 pattern, F03 BEH-POL-05 | — | [Verified Fact] |

### INC-07 decisions
| ID | Decision | Alternatives | Rationale | Approval | Tag |
|---|---|---|---|---|---|
| RD-50 | New packages `hub/runs`, `hub/metrics`, `hub/obs` (log, collect) with CLIs `python -m hub.runs` and `python -m hub.metrics`; no existing file touched | extend `hub/cli.py` | add-only rule (TST-CO-05 c) | - | [Verified Fact] |
| RD-51 | M005 in `hub/runs/migrations/`, own applier and table `runs_schema_migrations` | `hub/store/forward/` | same reason as RD-40 | - | [Verified Fact] |
| RD-52 | Flag = latest `SCHEDULE_CHANGED` policy event via ZH-09; only `schedule.py` imports the gate | config key; jobs call the gate | OD-S12-10, AC-RUN-12 | OD-19 | [Verified Fact] |
| RD-53 | Run record = folded append-only events; single-flight lock with heartbeat; checkpoint = order keys; resume via idempotent backfill | mutable status row | auditability, kill/resume equality (AC-RUN-07) | - | [Verified Fact] |
| RD-54 | Exact `Decimal` metrics; stored values keep params / inputs; `reproduce` bounded by `recorded_until` | floats; recompute from live data | AC-MET-13/14 | - | [Verified Fact] |
| RD-55 | Log fields are a closed whitelist | free-form log messages | AC-OBS-04 by construction | - | [Verified Fact] |

### INC-09 decisions
| ID | Decision | Alternative rejected | Reason | Reversal | Label |
|---|---|---|---|---|---|
| RD-56 | Extend frozen INC-08 classes by subclass (R2SearchService, R2WebApp) and delegate the API module | edit hub/review/search.py and hub/web/api.py | frozen earlier modules; additive rule | delete the new packages | [Verified Fact] |
| RD-57 | FTS5 tables are derived objects outside M007 | virtual tables in the migration | M007 must apply on an FTS-less runtime; drop = rollback | `drop-index` | [Verified Fact] |
| RD-58 | Same bm25 formula and excerpt on both engines | engine-specific order / snippet() | AC-REV-16 'same result order' holds generally; responses engine-independent | switch ranking per engine | [Verified Fact] |
| RD-59 | Runtime probe with TEMP virtual tables on the store connection | `hub.runtime.fts5_available` (opens :memory:, no trigram) | trigram needed; TST-CO-04 d allows no new connect | - | [Verified Fact] |
| RD-60 | C3 reads need a reason only when the permitted result holds restricted rows | reason on every search | callers who cannot read C3 are never asked; least friction consistent with MA-2 | config `search.require_c3_reason` | [Inference] |
| RD-61 | Consistency findings with INSERT OR IGNORE on a unique key | read-then-insert | idempotent by construction (AC-ID-15) | - | [Verified Fact] |
| RD-62 | Reports computed as of a data instant and not stored (OP-MET-06, delays) | store a metric_value per GET | INC-08 D-10 pattern; reproducible GETs | store via a job later | [Verified Fact] |

## Evidence References
- INC-03 evidence: `docs/15-modernization/evidence/inc03/` (summary.txt, hub-final-{A,B,C} reports, char-regression-inc03_report.json, mutation-gate-inc03.txt, checksum-log.txt, rollback-rehearsal-1/); `docs/15-modernization/rollback-rehearsal-inc03.md`; commits `git log --oneline main..stage-15-inc03-hub-db-audit`.
- `tests/characterization/harness.py` (`NORMALISATION_RULES`, guard), `run_characterization.py`; commits 2633062, 0283660, e1eb1d2, ed43a0a.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- None.

## Unresolved Issues
- RD-10 needs a Stage 12/13 addendum owner: Engagement lead (Dinesh Naik).

## Residual Risks
- RR-RD-1 RD-02 depends on the backup staying intact and adjacent to the repo; `--fixture-source` allows another location.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
| v0.3 | 2026-10-18 | claude-fde-agent | INC-03 (branch `stage-15-inc03-hub-db-audit`): sections added; earlier content unchanged. |
| v0.4 | 2026-10-18 | claude-fde-agent | INC-04 (branch `stage-15-inc04-rule-service`): sections added; earlier content unchanged. |
| v0.5 | 2026-10-19 | claude-fde-agent | INC-07 (branch `stage-15-inc07-runs-metrics`): sections added; earlier content unchanged. |
| v0.9 | 2026-10-20 | claude-fde-agent | INC-09 (branch `stage-15-inc09-search-corpus`): sections added; earlier content unchanged. |
