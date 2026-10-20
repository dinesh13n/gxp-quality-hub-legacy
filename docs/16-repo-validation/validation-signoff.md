---
stage: "16 — Validate the Good Repo"
artifact: "validation-signoff.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/16-repo-validation/repo-quality-gate.md", "docs/16-repo-validation/regression-results.md", "docs/16-repo-validation/test-results.md", "docs/16-repo-validation/behavior-difference-report.md", "docs/16-repo-validation/evidence/SHA256SUMS.txt", ".fde/orchestrator-decisions.md (OD-04, OD-22, OD-23)"]
supersedes: "none"
---
**Label: synthetic repository. This records the validating agent's sign-off and the human sign-off that is still required. No human approval is claimed or implied (OD-04).**

## Summary
The validating agent signs off that the evidence in `docs/16-repo-validation/` supports a **CONDITIONAL PASS** for the repository at `main` 2c63b07. The engagement lead's acceptance is **pending**; until it is recorded, Stage 17 may proceed on the conditions listed (Stage 15 / OD-12 practice), but no cutover, exposure or activation may rely on this sign-off.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### VS-1 What is signed
| Item | Value | Tag |
|---|---|---|
| Repository / commit | `gxp-quality-hub-legacy`, branch `main`, HEAD `2c63b07` (tree `0d2e5c7`, identical to `6a4472d` at stage start; laptop working tree = cloud clone) | [Verified Fact] |
| Baseline compared against | Stage 7 goldens (`docs/07-repo-assessment/evidence/golden/*_run1.json`), FX-BASE125 (`legacy.sqlite3` sha256 `c254649f…d70aa`, OD-09), tag `baseline-as-found` | [Verified Fact] |
| Runtimes | reference: laptop Python 3.10.12 / SQLite 3.37.2 / Node 22.23.2 / JDK 11; hub regression: cloud Python 3.13.16 / SQLite 3.45.1 (OD-23) | [Verified Fact] |
| Data integrity | `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0 on the laptop before and after every Stage 16 execution; working tree `git status` shows only `docs/16-repo-validation/` | [Verified Fact] |
| Evidence integrity | `docs/16-repo-validation/evidence/SHA256SUMS.txt` | [Verified Fact] |
| Gate outcome | CONDITIONAL PASS (repo-quality-gate.md) | [Verified Fact] |

[Verified Fact] Commit identity: Stage 16 started when `main` was `6a4472d`; during the stage the orchestrator reset `main` on both the laptop and the cloud clone to `origin/main` `2c63b07` (reflog `reset: moving to refs/remotes/origin/main`). Both commits have the same parent `ad5514f` and the **same tree `0d2e5c73b64f…`** (`git diff --quiet 6a4472d 2c63b07` = no difference), so every result here applies to `2c63b07` unchanged.

### VS-2 Sign-off record
| Role | Name | Decision | Date | Reference |
|---|---|---|---|---|
| Validating agent | claude-fde-agent | Evidence supports CONDITIONAL PASS; D5 = 0; no regression | 2026-10-20 | this folder |
| Engagement lead (acceptance of the gate and its conditions) | Dinesh Naik | **PENDING** - not recorded | — | to be recorded in `.fde/orchestrator-decisions.md` |
| Approval of any behaviour deviation (HAR-06) | Dinesh Naik | **NOT GIVEN** - DV-01..DV-09 remain `proposed` | — | OD-S12-13 |

### VS-3 Conditions attached to the sign-off
1. No cutover step (CUT-1..CUT-5), exposure beyond loopback, rule-set activation, policy adoption or scheduler switch may cite this validation as approval.
2. The Stage 17 PRD must carry: the DV register addendum (S16-D02), the runtime decision (S16-D07), the Stage 12 schema / code addenda (S16-D11, RTD lists) and the human-decision list in repo-quality-gate.md.
3. The orchestrator fixes the regression selector gap (S16-D10) before the next full regression.

## Evidence References
- All artifacts in `docs/16-repo-validation/`; scripts and raw outputs in `docs/16-repo-validation/evidence/`.

## Assumptions
- A-16-VS-1 [Assumption] An agent sign-off plus a pending human acceptance is sufficient to start Stage 17 (consistent with OD-01/OD-12 practice for earlier CONDITIONAL PASS stages). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- None beyond those in the other artifacts.

## Unresolved Issues
- Human acceptance pending.

## Residual Risks
- RR-VS-1 If the conditions are lost in hand-over, a later stage could treat this CONDITIONAL PASS as approval (Low, mitigated by VS-3 and the gate file).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue (agent sign-off; human acceptance pending). |
