---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "remaining-technical-debt.md"
version: "v0.4"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; INC-03 (hub DB migrations M001, C2 access & audit chain, backup/restore, first rollback rehearsal) added in v0.3. Stage 15 overall status: IN PROGRESS. INC-04 (policy & rule service: M002, as-found rule sets inactive, activation with a recorded human decision) added in v0.4."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "docs/07-repo-assessment/technical-debt-register.md", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)", "docs/15-modernization/evidence/inc03/", "docs/15-modernization/rollback-rehearsal-inc03.md", "hub/", "tests/hub/", ".fde/orchestrator-decisions.md (OD-15)"]
supersedes: "v0.3 (INC-01 .. INC-03)"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
Debt that remains after INC-01 (legacy debt itself is untouched by design and stays in the Stage 7 register). Items below are about the change-safety net and the open INC-01 conditions.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Debt / open item | Impact | Owner | Due | Tag |
|---|---|---|---|---|---|
| RTD-01 | Harness cannot run in GitHub CI as-is: FX-BASE125 data (`data/*.sqlite3`, `data/lake/`) is git-ignored and absent on the runner; partner tables are not regenerable | CT gate not enforced on PRs | Engagement lead (Dinesh Naik) | before INC-02 merge (fixture provisioning decision, e.g. private artifact) | [Verified Fact] |
| RTD-02 | Harness and mutation gate not wired into `.github/workflows/verify.yml` (existing file, out of INC-01 scope) | manual gate only | orchestrator | later increment / Stage 23 | [Verified Fact] |
| RTD-03 | CT-H5: no Python 3.12 parity run (CI uses 3.12, device has 3.10.12 only). INC-02: floor 3.10/3.37 adopted as default (OD-14) and enforced; 3.12 mode tested only by refusal on 3.10 | runtime-dependent diffs unknown | Engagement lead (Dinesh Naik) | before CUT / Stage 27 | [Verified Fact] |
| RTD-04 | CT-H7 coverage.py unavailable (no installs); kill rate used instead | branch coverage unknown | — | when HAR-08 allows | [Verified Fact] |
| RTD-05 | CT-17 (concurrency) and CT-18 (docker) NOT-RUN | no lock-timeout / container evidence | — | Stage 26/31 | [Verified Fact] |
| RTD-06 | AC-CO-L04..L16 proposed in test metadata only; Stage 12 acceptance criteria not updated (GAP-13-06 partially closed) | traceability partial | Engagement lead (Dinesh Naik) | Stage 16/17 addendum | [Inference] |
| RTD-07 | TB-22 (correct unsafe legacy quick-start docs) not done — would edit an existing file | users may still run destructive tests in the working tree | orchestrator | separate approved docs increment | [Verified Fact] |
| RTD-08 | Supplement golden v1 reviewed only by its authoring agent | weak four-eyes on 7 checks | orchestrator / Dinesh (PR review) | INC-01 PR | [Verified Fact] |
| RTD-09 | Full mutation gate (~5-6 min) had to be run in 4 chunks because device calls are capped at 180 s; a single uninterrupted run was not observed | none functionally (same code path) | — | CI wiring | [Verified Fact] |
| RTD-10 | Negative test of the INC-01 runner golden-manifest check (E-GOLDEN-HASH) not executed. INC-02: the equivalent hub AD-08 check is negatively tested on a synthetic golden dir (TST-CO-02 f, E-FX-HASH); the INC-01 runner path itself is still untested | check partly untested | — | later increment | [Verified Fact] |
| RTD-11 | Shipped tests still overwrite the DB copy they run on (TQ-01): post-run sha 750336f3… — pinned as-found, not fixed | unchanged legacy hazard (sandbox-contained) | — | Stage 30 decision | [Verified Fact] |
| RTD-12 | N4 tail compare tolerates a change only in the clipped start of one stderr tail (`node_cwd_other`) | small blind spot | — | review with CT-H3 list | [Inference] |

### INC-02 additions
| ID | Debt / open item | Impact | Owner | Due | Tag |
|---|---|---|---|---|---|
| RTD-13 | Stage 12 addenda needed: DDL (M000 tables), hub-config schema (4 INC-02 keys), error-handling spec (new codes + exit codes 2-15, RD-19) | specs lag the code | Engagement lead (Dinesh Naik) | Stage 16/17 addendum (HAR-13) | [Verified Fact] |
| RTD-14 | `no-ai-check` and hub tests not wired into CI; BEH-CO-07 says "CI blocks" | No-AI gate is manual | orchestrator | Stage 27/30 (OD-14) | [Verified Fact] |
| RTD-15 | 7 of 9 DV probes use declared target values (DEV-08) | golden-compare proves machinery, not modules | owning increments | INC-04..INC-08 | [Verified Fact] |
| RTD-16 | Untrusted: runtime guard only; AC-INT-23 static check not built | a typed misuse is caught only at run time | — | INC-06 | [Verified Fact] |
| RTD-17 | Deny-list is heuristic and scoped to hub/ + tests/hub + manifests; legacy estate excluded (`app/gateway_bridge.py` uses `urllib.request`) | transitive or renamed packages could slip | — | Stage 24 review | [Inference] |
| RTD-18 | No python3.9 and no `en_IN` locale on the device: AC-CO-14 old runtime simulated; AC-CO-13 locale relies on libc fallback | partial environment coverage | Engagement lead (Dinesh Naik) | CI matrix (Stage 27) | [Verified Fact] |
| RTD-19 | Hub suite takes 110-130 s (TST-CO-12 e re-runs the suite); device calls are capped at 180 s | suite will need chunking (`-k`) as it grows | — | INC-03+ | [Verified Fact] |
| RTD-20 | Gate G1 red by design until DV-01..DV-09 are decided (OD-S12-13 / HAR-06) | merge criterion must accept "UNAPPROVED = DV-01..09 only" | Engagement lead (Dinesh Naik) | before INC-04 | [Verified Fact] |
| RTD-21 | Exit code 2 shared by usage error, E-FX-HASH and E-CFG-INVALID | ambiguous in scripts | — | with RTD-13 | [Verified Fact] |
| RTD-22 | `coexistence_inventory` triggers block all updates, including a future legitimate owner assignment for CO-WF-01 (OPD-15) | needs a migration when the owner is known | — | when OPD-15 answered | [Inference] |

### INC-03 additions
| ID | Debt | Impact | Owner | Due | Tag |
|---|---|---|---|---|---|
| RTD-23 | Stage 12 addenda: DDL (M001 tables + deviation_register delete trigger), hub-config schema (`auth.*`, `network.tls`), error-handling spec (E-SEC-SECRET-IN-AUDIT, E-SEC-SCAN-FINDINGS, E-CO-RELEASE-BLOCKED, E-STORE-BACKUP-INVALID, E-AUTH-PASSWORD-POLICY, E-STORE-NOT-MIGRATED, trigger message E-SEC-RETAINED; exit codes 16-22) | specs lag the code | Engagement lead (Dinesh Naik) | Stage 16/17 (HAR-13) | [Verified Fact] |
| RTD-24 | Exit code 9 means both E-CO-DENYLIST-IMPORT (INC-02) and E-SEC-EXPOSURE-NOT-APPROVED (spec) | ambiguous in scripts | — | with RTD-23 | [Verified Fact] |
| RTD-25 | `python -m hub.admin` separate from `python -m hub`; two migration directories | operator UX, two runners | — | when hub/cli.py may change (INC-04+) | [Verified Fact] |
| RTD-26 | Security values are Stage 12 proposals (A-12-F09-1): PBKDF2 600k, lockout 5/15/15, session 30 min/8 h, re-auth 300 s, password >= 12 | not policy-backed | Engagement lead (Dinesh Naik) | Stage 24 | [Assumption] |
| RTD-27 | Not built: service bearer tokens + rotation (BEH-SEC-03), user disable / role revoke / password change commands, CSRF/cookie flags (no web layer), C3 read reasons (R2) | C2 incomplete beyond INC-03 scope | — | INC-04+ / OD-S12-06 | [Verified Fact] |
| RTD-28 | INC-02 `tests/hub/_driver.py` recorder does not record subTest failures (per-test status `ok` while unittest rc=1) | report.json counts can overstate passes; `unittest_rc` is authoritative | — | next change to the runner | [Verified Fact] |
| RTD-29 | Audit anchor is an unsigned local file on the same host; tail truncation after the last anchor undetectable (R-SEC-1, TST-SEC-12) | tamper evidence limited | Engagement lead (Dinesh Naik) | OD-S12-18 for real deployment / Stage 24 | [Verified Fact] |
| RTD-30 | Hold-all means unbounded growth of audit_log, login_attempt, session | storage growth | Engagement lead (Dinesh Naik) | retention policy OD-S12-09 | [Inference] |
| RTD-31 | Hub runner leaves ~470 MB per run in `<label>/scratch` + 61 MB `c_pristine`; device disk filled (ENOSPC) in INC-03; INC-02 copies removed (reports kept) | runs can fail on disk space | — | runner cleanup option | [Verified Fact] |
| RTD-32 | G1, G2, G4, G8, G9, G10 have no evaluator in INC-03 -> every release checklist is blocked (correct, but not yet useful) | release gate incomplete | owning increments | INC-04..INC-08 | [Verified Fact] |
| RTD-33 | L2 restore loses records written after the backup from the live store (kept only in `pre-restore/`); after rollback to the pre-migration backup a roll-forward starts a new chain | RPO window; chain continuity across rollback | — | Stage 28/30 | [Verified Fact] |
| RTD-34 | Lockout is per principal only; unknown-principal attempts and source rate limiting not controlled (no server) | brute force across names | — | INC-04+ / Stage 24 | [Inference] |
| RTD-35 | Route registry generated from the DRAFT OpenAPI; regeneration manual (TST-SEC-01 a detects drift) | must be regenerated (in the sandbox) when OpenAPI changes | — | Stage 16/17 | [Verified Fact] |
| RTD-36 | No process lock during restore ("stop process" is procedural) | concurrent writer could race a restore | — | when a daemon exists | [Inference] |

### INC-04 additions
| ID | Debt | Impact | Owner | Due | Tag |
|---|---|---|---|---|---|
| RTD-37 | M002 is applied by `hub.policy.schema` with its own version table; `hub.admin status` / `migrate` do not know it; two runners, three migration locations | operator must remember `hub.policy migrate`; a restore to a pre-M002 backup drops the policy tables (S08) | — | Stage 16/17: move M002 into `hub/store/forward/` and update INC-03 S01 + `migrate.py` | [Verified Fact] |
| RTD-38 | Stage 12 addenda: DDL (immutability / pointer triggers, `policy_schema_migrations`, `rule_row.outcome` JSON shape, `$input` values), error registry (E-POL-DECISION-REQUIRED, E-POL-ASFOUND-DRIFT, E-POL-INVALID; exit codes 23 / 24 / 19), `POLICY_DECISION_RECORDED` + `POLICY_SEEDED` / `RULESET_LOADED` / `POLICY_SCHEMA_APPLIED` audit actions, function domain lists | specs and code diverge | Engagement lead (Dinesh Naik) | Stage 16/17 | [Verified Fact] |
| RTD-39 | Not built: divergence report (BEH-POL-10, AC-POL-24, R2), policy withdrawal (BEH-POL-05), HTTP routes OP-POL-01..07, reviewer-pack / report surfaces of the `defaulted` marker, listing filters beyond kind / status | R2 and API parts of F03 missing | — | INC-05+ / R2 | [Verified Fact] |
| RTD-40 | `hub/policy/gate.py` duplicates the F02 holder check | two places to change | — | INC-05 | [Verified Fact] |
| RTD-41 | DEV-29 / DEV-30: preserve-or-fix of the JS partial-year match and of non-numeric amounts; no "preserve" mode exists | behaviour differs from legacy on degenerate inputs | Engagement lead (Dinesh Naik) | OD-S12-13 / Stage 30 | [Verified Fact] |
| RTD-42 | Exact Decimal vs IEEE doubles: 870 grid cases identical, untested last-bit boundaries unknown | possible 1-ulp differences at x1.05 boundaries | — | Stage 16 | [Unknown] |
| RTD-43 | Decision mechanism (DEV-35): a recorded decision has no expiry, is not re-verified against the holder's re-auth, and `activate` re-verifies the whole audit chain (O(n)) | design choice by the build agent; cost grows with hold-all audit | Engagement lead (Dinesh Naik) | Stage 24 / confirmation of A-15-04-1 | [Assumption] |
| RTD-44 | Group C (`-k TST_CO_12`) re-runs the whole suite under the egress guard: 123 tests, 103-115 s of the 180 s device cap | next increments will hit the cap | — | before INC-05: split the inner run or raise the cap | [Verified Fact] |
| RTD-45 | `active_ruleset` is a pointer table without a delete guard (history is `policy_events` + audit); custom rule sets can be created and edited but have no review / approval flow beyond activation | pointer history relies on events | — | Stage 24 | [Inference] |

## Evidence References
- INC-03 evidence: `docs/15-modernization/evidence/inc03/` (summary.txt, hub-final-{A,B,C} reports, char-regression-inc03_report.json, mutation-gate-inc03.txt, checksum-log.txt, rollback-rehearsal-1/); `docs/15-modernization/rollback-rehearsal-inc03.md`; commits `git log --oneline main..stage-15-inc03-hub-db-audit`.
- `transformation-log.md` TL-3; `behavior-preservation-evidence.md` residual risks.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-15-01 CI fixture provisioning approach.

## Unresolved Issues
- INC-03: RTD-23 (Stage 12 addenda) and RTD-26 (security values, Stage 24) need decisions by Dinesh (owner).
- INC-04: RTD-41 (preserve-or-fix, OD-S12-13), RTD-43 (decision mechanism) and RTD-38 (addenda) need decisions by Dinesh (owner).
- RTD-01, RTD-03, RTD-06 need decisions by Dinesh (owner) before or during INC-02.

## INC-05 additions
| ID | Item | Label |
|---|---|---|
| RTD-46 | Remove `hub/policy/gate.py` and its import in `hub/policy/service.py` once a non-add edit is permitted; `GatedPolicyService` then folds into `PolicyService`. | Verified Fact |
| RTD-47 | Stage 12 addendum for exit codes 25/26/27, new error codes, settings keys and the `decision_idempotency` table. | Verified Fact |
| RTD-48 | OD-S12-15 `rule` derivation mode and case creation (OD-S12-19) not built; human decision pending. | Unknown |
| RTD-49 | Evidence access matrix and CLOSE_EXCEPTION-as-closing-transition need owner confirmation (A-15-05-1, DEV-46). | Assumption |
| RTD-50 | Imported `occurred_at` is the case creation time proxy; legacy `events` history not imported. | Verified Fact |
| RTD-51 | Third Zone H copy in `hub/security/authz.py`. | Verified Fact |
| RTD-52 | Mutation gate for INC-05 not run. | Verified Fact |
| RTD-44 | Resolved by DEV-52 (E05EGRESS). | Verified Fact |

## INC-06 additions
| ID | Item | Label |
|---|---|---|
| RTD-53 | Full `run_event` table (DDL) is owned by INC-07; `intake_run_event` is an interim subset. | Verified Fact |
| RTD-54 | Frozen `hub/security/scan.py` RETAINED_TABLES lists only raw_intake and intake_outcome; `intake_item_attr` and `intake_run_event` need adding when edits are permitted. | Verified Fact |
| RTD-55 | Stage 12 addendum for exit code 28, E-INT-* codes and `gateway.retries`. | Verified Fact |
| RTD-56 | Untrusted-text lint (U1/U2/U3) is heuristic; it cannot prove absence of misuse (A-15-06-1). | Assumption |
| RTD-57 | Enforce mode cannot be switched on until Dinesh names Zone H holders; DV for negative quantity (OD-S12-13) and the vendor CSV identifier pattern findings (all 2,400 rows) need a human decision. | Unknown |

## Residual Risks
- RR-RTD-1 Until RTD-01/02 are closed, behaviour preservation depends on someone running the harness manually before each merge (OD-13 orchestrator check).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
| v0.3 | 2026-10-18 | claude-fde-agent | INC-03 (branch `stage-15-inc03-hub-db-audit`): sections added; earlier content unchanged. |
| v0.4 | 2026-10-18 | claude-fde-agent | INC-04 (branch `stage-15-inc04-rule-service`): sections added; earlier content unchanged. |
| v0.5 | 2026-10-19 | claude-fde-agent | INC-05 (branch `stage-15-inc05-decision-record`): sections added; earlier content unchanged. |
| v0.6 | 2026-10-19 | claude-fde-agent | INC-06 (branch `stage-15-inc06-intake`): sections added; earlier content unchanged. |
