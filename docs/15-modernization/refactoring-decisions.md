---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "refactoring-decisions.md"
version: "v0.2"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; Stage 15 overall status: IN PROGRESS."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)"]
supersedes: "v0.1 (INC-01 only)"
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

## Evidence References
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
