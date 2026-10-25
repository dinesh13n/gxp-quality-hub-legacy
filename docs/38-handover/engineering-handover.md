---
stage: "38 — Handover + Knowledge Transfer"
artifact: "engineering-handover.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["README.md", "pyproject.toml", ".gitignore", ".github/workflows/verify.yml", "ci/hub-hardening.yml", "tests/hub/run_hub_groups.py", "tests/hub/regression_groups.json", "tests/hub/non_add_edits.json", "tests/characterization/", "docs/18-delivery/", "docs/20-application/application-readiness.md", "docs/27-hardening/production-readiness-checklist.md", "docs/37-operating-model/change-governance.md", ".fde/orchestrator-decisions.md OD-01, OD-03a, OD-11, OD-13, OD-23, OD-27, OD-28, OD-32..OD-37"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. This is the handover of a PREPARED-BUT-UNRELEASED system: Stage 30 is BLOCKED (0 of 40 approvals), no cutover, authority flip, tag or release happened, and the hub is not deployed beyond loopback. The only human is Dinesh Naik, Engagement lead (OD-04). No receiving team, trainee, walkthrough audience, exercise result, sign-off or approval is invented here; vacant roles stay vacant (Stage 37). Nothing here accepts a risk (HAR-11). The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
How the code is built, tested and changed, and the conventions that bite a newcomer. The engineering process was: one branch plus PR per increment or stage (`stage-NN-*`), squash-merged by the orchestrator after a full hub regression (OD-13, OD-23); build agents run only their own new tests. **Dinesh Naik is the only person who has operated this flow; the receiver inherits habits that exist only in the OD log.**

## Findings
### EH-1 Repository and language [Verified Fact]
Python, standard library only (`pyproject.toml`: `requires-python >=3.10`, no dependencies). Legacy estate in `app/`, `legacy_batch/`, `legacy_java/`, `legacy_js/`, `services/source_gateway/` is **frozen** (TST-CO-05 a fails on any change). New code lives in `hub/`; tests in `tests/hub/`; characterization harness in `tests/characterization/`; stage documents in `docs/NN-*/`; decisions in `.fde/orchestrator-decisions.md`. Baseline commit `a6eb4e8` is tagged `baseline-as-found` (OD-06).

### EH-2 Rules a newcomer would break without being told [Verified Fact: OD log]
| Rule | Source | Why it matters |
|---|---|---|
| Never run tests, scripts or servers against the working-tree `data/`; run in a **full copy** outside the tree, then `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` | OD-03, OD-03a | Several modules write repo-relative `data/` paths |
| Delete sandbox copies after each run | OD-16 | Device disk about 9.8 GB |
| Frozen test TST-CO-12 group C: do not add tests to it; new modules go in their own egress-guarded group; guarded modules must not import `time`/`random` | OD-17..OD-19 | Group C near the 180 s device cap |
| Edits to earlier-increment files must be listed in `tests/hub/non_add_edits.json` with a work item; each build stage resets the list | OD-27 (DEV-05) | TST-CO-05 c enforces add-only |
| A new helper under `tests/hub` must have group B run by its author | OD-28 (S21-DEV-02) | A real R2 defect slipped through once |
| Do not name a test variable `secret` or similar | OD-36 (S31-DEV-08) | Tripped the TST-SEC-18 scan |
| Do not import `hub.web` from `hub/resilience` | OD-35 (S28-DEV-08) | Capped listener moved to `hub/web` |
| Squash-merge only, never force-push, no history rewrite | OD-13, WB-08, C2 | Evidence preservation |
| Documents are not edited in place when frozen-provisional; corrections go in addenda / v0.2 | OD-07, OD-10, Stage 0B | Before/after comparison must stay possible |

### EH-3 How to test [Verified Fact: tests/hub/run_hub_groups.py docstring]
`python3 -B tests/hub/run_hub_groups.py --sandbox-base ~/fde_sbx/<x> --group <ID>` for laptop groups; `--all --log <json>` in the cloud workspace (no per-call cap). It builds the sandbox copy, gates on checksums before and after, checks executed = expected per group, deletes the sandbox. Exit 0 green, 1 failure or count mismatch, 2 refused. Full regression at last report: 31 groups green (OD-37, including S30/E30; Python 3.13 in the orchestrator's cloud workspace, OD-23). Characterization harness stays on the reference laptop (Python 3.10.12): only CT-13 differs (Node patch drift, S24-DEV-04). The 419-method manifest figure is from Stage 20 (OD-27) and has grown since; the current count is [Unknown] without re-running.

### EH-4 Change flow in steady state [Inference from Stage 37 `change-governance.md` + OD log]
Branch, PR, full regression, release checklist, squash-merge, with RL-02 owning release and change. Today: no CI over `hub/` (workflow covers legacy only); `ci/hub-hardening.yml` is not installed and installing it under `.github/` needs approval HAR-07 (D-27-03, AP-OPS entry). Steady-state executors are Dinesh plus agents; no human reviewer other than Dinesh exists (RL-13 VACANT, DQ-17 single-approver risk accepted as a general risk only).

### EH-5 Known technical debt and open defects [Verified Fact unless marked]
| Item | State | Evidence |
|---|---|---|
| F-11 plus 9 functions over complexity 15 | open | OD-34, D-27-08 |
| Package cycles (4 + 6 reported) | debt | OD-27 |
| F-29-02..16 | open (F-29-01 fixed S30-DEV-01; Dinesh to accept exit 17) | OD-35, OD-37 |
| F-31-01..07 | open | OD-36 |
| Mutants M5, M9, M10 survive | open | OD-33 |
| 23 schema-less tables (FAC-09) | deferred to Stage 27 per OD-31; status after Stage 27 [Unknown] here | OD-31 |
| Behaviour defaults (401, 400, 408, 503, 429 after 100 refusals/60 s, insert-only migrations triggers) | **agent assumptions, not approved** | OD-34 |

### EH-6 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| ENF-01 | [Verified Fact] A new engineer cannot reproduce the full regression from the repo alone: it needs the git-ignored baseline data (`data/*.sqlite3`, `data/lake/`) copied once, checksum-gated, to a Python 3.13 cloud workspace of Unknown provider | OD-23, PA-18, V-05 | Reproducibility rests on Dinesh's accounts | High | High | Provider, terms, owner |
| ENF-02 | [Verified Fact] No CI over `hub/`; every green result in the record was produced by the orchestrator's manual runs | PA-16, OD-34 | Regression is only as repeatable as the person | Medium-High | High | Install CI (HAR-07) |
| ENF-03 | [Verified Fact] Every one of the 51 commits at Stage 33 count carried the AI coding assistant co-author trailer (PA-27); terms Unknown | `service-ownership-map.md` PA-27, V-04 | Code provenance and licensing question for a receiver | Medium | High | VA-02..VA-04 decision |
| ENF-04 | [Inference] The process rules in EH-2 are encoded in tests, not prose; a receiver who ignores them will find out by red tests | OD-27, OD-28 | Learning by failure | Low-Medium | Medium | - |
| ENF-05 | [Assumption] A person (not an agent) has never executed the full change flow end to end | OD-13 (orchestrator is an agent); no human log | Flow untested for human operators | Medium | Medium | First receiver exercise OX-06 |

## Evidence References
See `evidence_sources`; `docs/27-hardening/production-readiness-checklist.md` PRC-1 to PRC-3 (24 of 38 readiness checks MET at Stage 27; 14 open with owner).

## Assumptions
- A-38-EH-1 The process in EH-4 is how a receiver should proceed; no one has accepted it (Stage 37 `change-governance.md`). Confirm: Dinesh.

## Unknowns
- U-38-EH-1 Current total test count and wall time after Stages 30 and 31. U-38-EH-2 Whether 3.12+ passes (no evidence, OD-33).

## Unresolved Issues
- D-27-01..09 (restricted-evidence note rule, Python 3.12 floor, CI install under `.github` and SHA pins, rate-limit defaults, spec addenda for new error codes, legacy Dockerfile/compose hardening, 9 complex functions, walkthrough sign-off, stay loopback-only).

## Residual Risks
- RR-38-EH-1 Bus factor 1 on engineering practice. High.
- RR-38-EH-2 Third-party accounts (code host, assistant, cloud workspace) with unknown terms (VA-02..VA-04 PROPOSED). Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 38). |
