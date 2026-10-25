---
stage: "41 — Retirement / Decommissioning"
artifact: "dependency-clearance.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/07-repo-assessment/{dependency-map,critical-workflow-inventory}.md", "docs/14-transformation/{cutover-plan,coexistence-strategy,rollback-strategy}.md", "docs/37-operating-model/service-ownership-map.md", "docs/33-vendor-risk/vendor-inventory.md", "docs/30-release/{rollback-plan,release-outcome}.md", "hub/policy/asfound.py", "hub/adapters/{legacy_sqlite.py,baseline_pins.json}", "hub/golden/run.py", "hub/intake/cli.py", "hub/crosswalk/sources.py", "hub/search/corpus.py", "tests/hub/test_tst_co_05_legacy_paths_unchanged.py", "tests/characterization/harness.py", ".github/workflows/verify.yml", "run.sh", "git grep / ls (read-only)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. DOCUMENTATION ONLY. Nothing is retired or deleted. Every asset below is NOT CLEARED; clearance is a state that can only be reached by re-running the checks named here at retirement time and recording an APPROVED owner decision. Legacy stays authoritative (OD-37).**

## Summary
Inventory of **25 retirement candidates (RA-01..RA-25)** and **15 live dependencies (DF-01..DF-15)**. Result: **0 of 25 assets are CLEARED.** 19 are NOT CLEARED because a live dependency exists, 3 are PROTECTED (never retired by this plan), 2 are N/A (nothing exists to retire) and 1 is NOT APPLICABLE until a hosting decision. The most important finding is that the **hub itself depends on the legacy tree**: its as-found rule sets are built from legacy source files at pinned hashes, its golden comparison and the characterization harness execute unmodified legacy code, and a test (TST-CO-05) fails if a legacy path changes. A legacy file therefore cannot simply be removed from `main` even after cutover; it must first be replaced as a reference by an archived, hash-pinned copy under an approved change (DF-01..DF-05).

Dependency method used (all read-only, repo-relative): file listing, `grep` for imports and path strings, the Stage 7 static import graph, and the Stage 14/30 documents. No code was executed and no test was run in this docs-only stage; items that need execution are marked Unknown and listed as re-checks.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DC-1 Retirement candidates and clearance state
Legend: NOT CLEARED = live dependency or missing precondition; PROTECTED = see `retirement-criteria.md` RC-3; N/A = nothing exists. "Wave" refers to `retirement-criteria.md` RC-4.

| ID | Asset (paths / identity) | Capability / CUT | Wave | Blocking dependencies | State | Tag |
|---|---|---|---|---|---|---|
| RA-01 | Legacy read API `app/server.py` (CW-01/02/10/13; `GET` only, write verbs 501) | none (hub exposes its own API) | W5 | DF-07, DF-09, DF-12 | NOT CLEARED | [Verified Fact] |
| RA-02 | Rule evaluation: `app/legacy_logic.py`, `legacy_js/legacy_policy.js`, `contracts/decision-policies-archive.json` | CUT-2 | W2 | DF-01, DF-03, DF-04, DF-07, DF-09 | NOT CLEARED | [Verified Fact] |
| RA-03 | Intake and reconcile: `app/gateway_bridge.py`, `app/partner_feeds.py`, `app/integration.py`, `app/historical_estate.py` | CUT-3 | W3 | DF-02, DF-06, DF-08, DF-09, DF-10 | NOT CLEARED | [Verified Fact] |
| RA-04 | Upstream simulator `services/source_gateway/` | comparator for CUT-3 | W3 | DF-02, DF-06, DF-08 | NOT CLEARED | [Verified Fact] |
| RA-05 | Reporting: `app/baseline.py`, `app/operational_report.py`, `app/workshop_check.py`, `legacy_java/ReconcileLegacy.java`, `sql/legacy_reports.sql` | CUT-4 | W4 | DF-02, DF-04, DF-07, DF-09 | NOT CLEARED | [Verified Fact] |
| RA-06 | Night shift `legacy_batch/shift_reconciliation.py` | CUT-4 | W4 | DF-01, DF-02, DF-04, DF-09 | NOT CLEARED | [Verified Fact] |
| RA-07 | Provisioning and readiness: `app/generate*.py`, `app/enterprise_*.py`, `app/domain_data.py`, `app/historical_*.py`, `app/archived_documents.py`, `run.sh`, `scripts/*` | CW-12 | W5 | DF-04, DF-07, DF-11, DF-12 | NOT CLEARED | [Verified Fact] |
| RA-08 | `app/store.py` (import-time DB binding, fan-in 11 app modules) | none | W5 (last of `app/`) | DF-07, DF-08 | NOT CLEARED | [Verified Fact] |
| RA-09 | Seven shipped legacy test files `tests/test_*.py` (destructive; sandbox only) | none | W5 | DF-04, DF-11 | NOT CLEARED | [Verified Fact] |
| RA-10 | Build/env: `Dockerfile`, `compose.yaml`, `environments/*.env.example`, `.github/workflows/verify.yml`, legacy parts of `pyproject.toml` | none | W5 | DF-11 | NOT CLEARED | [Verified Fact] |
| RA-11 | Legacy data stores `data/` (1,512 files, `legacy.sqlite3` c254649f…d70aa) | n/a | never | DF-05, DF-08 | PROTECTED (NR-1) | [Verified Fact] |
| RA-12 | Nightly file exchange (ADR-007 archive; owner "transferred 2024", unnamed; PA-25) | outside repo | not planned | DF-10 | NOT CLEARED; owner VACANT | [Verified Fact] |
| RA-13 | Older-customer parallel workflow CO-WF-01 (PA-26) | out of product scope | never | DF-10 | PROTECTED (NR-4) | [Verified Fact] |
| RA-14 | Legacy documentation `docs/*.md` (as-found), `operations/runbook.md`, `operations/incidents/` | n/a | W5 | DF-13 | NOT CLEARED | [Verified Fact] |
| RA-15 | Hub shadow service and stores (`hub/`, `<data-dir>/hub.sqlite3`, anchor file) | all | engagement end only | DF-14; NR-2 | PROTECTED (records) / NOT CLEARED (service) | [Verified Fact] |
| RA-16 | Hub derived keyword index (FTS5 inside the hub store; `hub/search/fts.py`) | R2 search | with RA-15 | rebuildable from retained records | NOT CLEARED (derived, rebuildable) | [Verified Fact] FTS5 is optional (`hub/runtime.py`); [Inference] rebuildable |
| RA-17 | Sandbox copies (outside the working tree; OD-03a, OD-16) | n/a | W1 | none known; confirm no unique evidence | NOT CLEARED (check pending) | [Verified Fact] practice; [Unknown] current contents |
| RA-18 | Orchestrator cloud-workspace copy of git-ignored data and the provider account (V-05; provider Unknown) | n/a | W1/W6 | DF-15 | NOT CLEARED | [Verified Fact] usage; [Unknown] terms |
| RA-19 | AI coding assistant access (V-04, dev tooling) | n/a | W6 | DF-15 | NOT CLEARED | [Verified Fact] |
| RA-20 | GitHub remote and account (V-03) | n/a | W6 (access only; repo history is protected NR-6) | DF-15 | NOT CLEARED | [Verified Fact] |
| RA-21 | Backup folder `../_data-backup-2026-10-17/` + `SHA256SUMS.txt` (single device, no second copy) | n/a | never without HAR-03 | DF-05 | PROTECTED (NR-1) | [Verified Fact] |
| RA-22 | Hub credentials: principals, sessions, service tokens, `HUB_ANCHOR_SEAL_KEY` | n/a | with RA-15 | `secret-key-revocation.md` | NOT CLEARED | [Verified Fact] |
| RA-23 | Models, prompts, agents, tool APIs, model indexes | n/a | n/a | none exist (OD-08, PA-28) | N/A | [Verified Fact] |
| RA-24 | Optional CI file `ci/hub-hardening.yml` (not installed; HAR-07 approval pending, OD-34) | n/a | n/a | not installed, nothing to uninstall | N/A | [Verified Fact] |
| RA-25 | Reference laptop and device VM (V-10), Python 3.10.12 goldens host | n/a | W6 | DF-04, DF-15 | NOT CLEARED | [Verified Fact] |

### DC-2 Live dependency findings (six-field format)
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| DF-01 | [Verified Fact] The hub builds its three as-found candidate rule sets by reading legacy source files at a given `legacy_root`: `app/legacy_logic.py`, `legacy_js/legacy_policy.js`, `contracts/decision-policies-archive.json`, and the night-shift source; a mismatch raises `AsFoundDrift` | `hub/policy/asfound.py` `build_python`, `build_js`, `build_batch`, `_read_pinned` | Removing or moving these files breaks loading of the as-found rule sets (error text on a missing file is [Unknown], not exercised) | High | High | Move the pin source to an archived, hash-pinned reference copy (D-41-04) |
| DF-02 | [Verified Fact] Golden comparison and the observation step take a `legacy_root` and run the legacy side; gate G1 (golden diff) in the release evaluator rests on it | `hub/golden/run.py` (`_baseline_values`, `_observation`, `observe`); `docs/30-release/evidence/gate-results.json` G1 | Without a runnable legacy, G1 cannot be re-evaluated and parity cannot be re-proved | High | High | Decide whether parity is frozen at a final comparison and archived |
| DF-03 | [Verified Fact] TST-CO-05 fails if any legacy path differs from tag `baseline-as-found` | `tests/hub/test_tst_co_05_legacy_paths_unchanged.py` L32-39 | Any removal or edit fails the regression until the test is changed under an approved, recorded change (frozen-test rule: a test may not be silently edited) | Medium | High | Approval route for the test change (HAR/CC) |
| DF-04 | [Verified Fact] The characterization harness executes the UNMODIFIED legacy code in child processes (Python 3.10.12 on the laptop) and the CT-01..CT-16 checks depend on it | `tests/characterization/harness.py` header (lines 3-5, 55); OD-23 | Retiring legacy code ends the ability to regenerate goldens; existing goldens in `docs/07-repo-assessment/evidence/golden/` remain as frozen evidence | Medium | High | Is "frozen goldens only" acceptable after retirement? |
| DF-05 | [Verified Fact] The hub opens legacy DB snapshots read-only (`mode=ro&immutable=1`) against pinned sha256 values for each store | `hub/adapters/legacy_sqlite.py`; `hub/adapters/baseline_pins.json` | The data files are a dependency, not just the code; they are protected | High | High | none: stays protected |
| DF-06 | [Verified Fact] Intake, crosswalk, decision backfill, golden observation and search corpus modules take a legacy root | `hub/adapters/intake_sources.py`, `hub/crosswalk/sources.py`, `hub/decision/backfill.py` (125-case backfill from a legacy snapshot), `hub/decision/cli.py`, `hub/golden/observe.py`, `hub/search/corpus.py`, `hub/intake/cli.py`; raw grep in `evidence/e41-02-hub-legacy-references.txt` | Hub shadow inputs come from legacy-shaped sources; retiring the legacy producer leaves the hub without its shadow input unless it is repointed | Medium | Medium (modules identified by grep; call paths not traced) | Which hub inputs remain after CUT-3 |
| DF-07 | [Verified Fact] Internal import graph: `app.store` imported by 11 app modules; `app.legacy_logic` by `app.baseline` and `app.server`; `app.enterprise_data` by `generate`, `generate_documents`, `server` | `dependency-map.md` internal graph (static AST) | Retirement order inside `app/` must be consumers first, `store` last | Medium | High | none |
| DF-08 | [Verified Fact] `data/legacy.sqlite3` is shared by API, bridge, reconcile, importer, baseline, report, gateway (read only) and the smoke script; the integration bus is a file | `dependency-map.md` DM-10; `scripts/smoke.py` ignores `LEGACY_DB` | Stopping one legacy writer does not remove the shared file dependency | Medium | High | none |
| DF-09 | [Unknown] Consumers of the 13 legacy outputs outside the repo | `cutover-plan.md` CF-1; OD-28 (b); U-14-01 | PR-04 cannot be met; CUT-2..CUT-4 step 4 cannot be planned concretely | Medium | High | Business to identify |
| DF-10 | [Verified Fact] Two legacy-estate assets have no owner of record: nightly file exchange (PA-25) and CO-WF-01 (PA-26); ADR-007 has no recorded supersession | `service-ownership-map.md` SO-1; `docs/decisions/ADR-archived-007.md`; OPD-15 | They cannot be cleared by anyone; CO-WF-01 is protected | High | High | Owner / retirement question OPD-15 |
| DF-11 | [Verified Fact] Legacy CI (`verify.yml`) runs `unittest discover -s tests`, regenerates 6,000 cases and runs `app.baseline`; never run; `run.sh` starts `app.server` and regenerates data if missing | `.github/workflows/verify.yml`; `run.sh` | CI and `run.sh` assume the legacy tree exists | Low | High | Retire together with RA-07/09 |
| DF-12 | [Verified Fact] README and legacy docs describe the legacy tree as the product (`run.sh`, `PORT 8080`) | `README.md`, `environments/*.env.example` (e.g. `HOST=0.0.0.0` in the production-like example) | Documentation drift if code is retired without doc updates | Low | Medium | Docs retired or marked superseded |
| DF-13 | [Verified Fact] Runbook and incident record cover the legacy estate (INC-2025-014, follow-up owner unknown, DR-27) | `operations/runbook.md`, `operations/incidents/` | Operators lose their procedure if code is retired first | Medium | Medium | New runbook owner |
| DF-14 | [Verified Fact] No purge path exists for hub retained tables; insert-only triggers; backup restore sets aside later records rather than merging (F-29-06) | `evidence-retention-policy.md` RP-2; `rollback-plan.md` L2 | A hub store cannot be partially retired; only archived whole or kept | Medium | High | Archive format (D-41-06) |
| DF-15 | [Verified Fact] Toolchain accounts hold copies or context with terms Unknown (cloud workspace, AI coding assistant, GitHub) | `vendor-inventory.md` V-03..V-05; U-33-01, U-33-02 | Revocation and deletion proof cannot be specified against terms that are not in the repo | Medium | High | Dinesh supplies terms or marks not applicable |

### DC-3 Re-check commands for clearance time (not run here)
Each is read-only and must be re-run on a full copy outside the working tree, never against the working-tree `data/` (OD-03a), with output stored under a stage `evidence/` folder and hashed:
1. `git grep -n "legacy_root\|app/legacy_logic\|legacy_js\|legacy_batch\|legacy_java" -- hub tests` to list every hub/test reference to a legacy path (DF-01..DF-06).
2. `git diff --name-status baseline-as-found -- <legacy paths>` (as TST-CO-05) to confirm the legacy tree state.
3. The Stage 7 AST import scan for the retiring module (fan-in must be 0 outside retiring modules; DF-07).
4. `python -m hub.golden` golden-compare on a sandbox copy, final run before RL-1 or higher (DF-02).
5. `sha256sum -c` of the backup manifest, and `python -m hub.security verify-audit` on the hub store (PR-09).
6. Consumer confirmation from the owner for each output (PR-04), recorded as a signed list.
[Assumption] these commands reflect the CLIs described in `docs/30-release/evidence/s30-rehearse.sh`; exact flags to be taken from that script at clearance time.

## Evidence References
See `evidence_sources`; counts and file facts come from the repository at `main` b1de232 read in a separate worktree. Stage 30 evidence: `docs/30-release/evidence/{approvals-register.json,gate-results.json}`.

## Assumptions
- A-41-DC-1 [Assumption] The 25-asset list is complete as far as the repo shows; assets outside the repo (hosting, DNS, certificates, secrets stores) are not visible (consistent with A-33-02, A-37-SO-1). Confirm: Engagement lead (Dinesh Naik).
- A-41-DC-2 [Assumption] Module-level references found by grep are real call paths; call-path tracing was not done. Confirm: Build agent at clearance time.

## Unknowns
- U-41-DC-1 Error behaviour of the hub if a legacy file is absent (not exercised).
- U-41-DC-2 Contents of the sandbox copies (RA-17) and of the cloud workspace (RA-18) at any given date.
- U-41-DC-3 Consumers of the 13 outputs (DF-09).

## Unresolved Issues
- UI-41-DC-1 DF-01..DF-05 need a design decision on archived reference copies and an approved change to TST-CO-05 and G1 (D-41-04, D-41-05).
- UI-41-DC-2 Owners for RA-12 and RA-13.

## Residual Risks
- RR-41-DC-1 Hidden consumers outside the repo (Medium).
- RR-41-DC-2 Retiring a legacy file that a hub test or gate reads would turn the regression red and disable the comparator (High).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 41). |
