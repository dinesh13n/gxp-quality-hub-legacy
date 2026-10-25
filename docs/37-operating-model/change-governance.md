---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "change-governance.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/operating-contract/change-control-rules.md CC-01..CC-08", "docs/25-governance/governance-model.md GM-5", "docs/25-governance/compliance-control-matrix.md CM-3", "docs/14-transformation/feature-flag-plan.md", "docs/14-transformation/{cutover-plan,rollback-strategy,transformation-gates}.md", "docs/17-implementation-prd/release-boundaries.md", "hub/ops/release.py", "docs/16-repo-validation/ (DV-01..DV-11)", ".fde/orchestrator-decisions.md OD-13, OD-23, OD-27, OD-28, OD-32"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
Change governance for the steady state, formalising what the engagement already does and marking where a role is needed. Evidenced practice: one `stage-NN-*` branch per build, PR, orchestrator review, a full hub regression before merge, squash-merge (OD-13, OD-23); frozen Stage 12 files changed only by addendum; rule sets arrive inactive; decision flags ship at the safe value and move only with a recorded decision; behaviour changes need a characterisation baseline and an approved deviation; release checklist G1 needs zero unapproved differences. The proposal here assigns each approval to a **role** and keeps Dinesh Naik as the interim approver. **The repo is not under a client change board; none exists.** CI does not cover `hub/` and has never run (V-06), so most gates are run manually by the orchestrator.

## Findings
### CG-1 Change classes
| Class | Examples | Approver (role) | Holder today | Required evidence | Source |
|---|---|---|---|---|---|
| C0 Documentation-only | stage docs, ADR addenda | RL-01 at gate; no code risk | Dinesh (INTERIM) | versioned file, errata not overwrite, no edit to Stage 0B originals | CC-06, CC-07, HAR-13 |
| C1 Code, behaviour-preserving | refactor, hardening that leaves goldens unchanged | RL-02 | VACANT; Dinesh INTERIM | full regression green (25 groups at Stage 26), harness PASS, data checksums verified, non-add edits listed in `tests/hub/non_add_edits.json` | OD-23, OD-27 (DEV-05) |
| C2 Code, behaviour-changing | any change to legacy-visible outputs | RL-01 via deviation DV-xx (HAR-06), consult RL-03/RL-08/RL-06 | Dinesh | characterisation baseline first, deviation row `approved` with `approval_ref`, golden-compare exit 0 | CC-05; AP-3 |
| C3 Decision-flag or mode move | any OD-S12-xx flag, mode `none` to other, schedule on | RL-03 plus `approval_ref`; RL-04 for Zone H acts | VACANT; Dinesh decides OD-S12-xx | recorded decision; `CONFIG_CHANGED` audit once DW-17 is verified live | DW-17; FF-2 |
| C4 Rule-set change or activation | new/changed named rule set; activation | RL-03 proposes; RL-04 activates | **VACANT** | versioned named inactive set; audited Zone H event; refused today | OD-16; AP-4 |
| C5 Exposure, auth, data scope | non-loopback bind, TLS, tokens, real data, new tenant | RL-01 with RL-05 | Dinesh | `exposure_approved` + `exposure_approval_ref`; bind still refused (DEV-75) | AP-6; OD-32 |
| C6 Toolchain/vendor change | new dependency, CI, runtime upgrade (Python 3.12+), workspace | RL-01 with RL-05 (HAR-07/08/09) | Dinesh | ADR + decision; SBOM at Stage 27 (not yet); goldens re-baselined on runtime move | VA-01, VA-06, VA-07; RA-02 |
| C7 AI introduction | any model call | RL-01 new decision + HAR-08/09/10 | Dinesh | re-qualification RQ-1..RQ-3 | OD-08 |
| C8 Cutover step | CUT-1..CUT-5 | RL-01 (HAR-11), consult RL-03/RL-09/RL-06/RL-04 | Dinesh | go/no-go record per step; none can start (RB-4) | AP-5 |
| E Emergency change | fix a SEV-A/B defect | RL-02, ratified by RL-01 within the next gate | VACANT / Dinesh | same tests, run after the fact only if safe default is kept; never waives a release gate (HAR-14) | EH-08 |

### CG-2 Standard path (target, from observed practice)
1. Request raised and classified (C0..C8); STOP/HAR check by the author (ES-01, ES-02).
2. Branch `stage-NN-<slug>`; author runs only its own new tests (OD-23).
3. PR opened; orchestrator runs full regression (cloud workspace, checksum-gated) and harness on the reference laptop (Python 3.10.12) (OD-23, OD-30).
4. Release checklist from `hub/ops/release.py`: No-AI guard, egress tripwires, golden-compare, mutation gates, checksum verification (`sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt`).
5. Approval by the class approver; recorded as OD entry or `approval_ref`.
6. Squash-merge; OD log updated; residual items carried with owner.
No step may be skipped by an agent. A failed gate is fixed, not waived, unless RL-01 records a waiver (HAR-14).

### CG-3 Standing change-freeze conditions (proposed)
- Golden-compare exits 6 (unapproved deviations), checksum mismatch, tripwire red, `verify-audit` failing, `zone_h.holders` modified without a recorded approval. [Inference] drawn from STOP-01 and EH-03..EH-08.

### CG-4 Evidence of operation
| Evidence | Value | Tag |
|---|---|---|
| Merged PRs through the process | 15 (PR #1..#15; OD-13..OD-33) | [Verified Fact] |
| Defects caught by the manual full regression | 2 I6 failures (S24-DEV-05); a No-AI R2 helper defect (S21-DEV-02) | [Verified Fact] |
| Known gap in tooling | CT-13 harness failure by Node patch drift (S24-DEV-04) open environment item | [Verified Fact] |
| CI coverage of `hub/` | none | [Verified Fact] |
| Second reviewer | none | [Verified Fact] |

### CG-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CHF-01 | [Verified Fact] Change control depends on an orchestrator running tests manually; there is no automated enforcement | RTD-01/02/14; RP-05; V-06 | A control can regress between runs | Medium | High | Stage 27 CI wiring (HAR-07) |
| CHF-02 | [Verified Fact] C4 and parts of C3 cannot be exercised: no Zone H holder | `zone_h.holders` empty | Rule activation is impossible, which is the safe state | Low now, blocks value | High | OD-S12-06 |
| CHF-03 | [Inference] The class approver for C1 (service owner) is the author's own organisation in practice, so there is no independence | OM-2; RP-01 | Self-review | Medium | High | DQ-17 |
| CHF-04 | [Unknown] Whether Stage 27 (running on branch `stage-27-hardening`) changes any gate described here | not merged at this stage | Re-check at merge | Low | Medium | Reconcile after Stage 27 |

## Evidence References
See `evidence_sources`. CC-01..CC-08 are read from the Stage 0B originals (unchanged). Stage 27 content was not read.

## Assumptions
- A-37-CG-1 [Assumption] The class table is a proposal; the practice it describes is evidenced, the approver roles are not. Confirm: Engagement lead (Dinesh Naik).
- A-37-CG-2 [Assumption] The emergency path (E) is acceptable as long as the safe default holds. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-37-CG-1 Whether a client release calendar, freeze windows or CAB exist (SH-04 role; no holder).
- U-37-CG-2 Impact of Stage 27 (SBOM, CI parity, hardening) on CG-2 and CG-3.

## Unresolved Issues
- RL-02/RL-03 holders; CI wiring; DQ-17; DV-01..DV-11 preserve-or-fix.

## Residual Risks
- RR-37-CG-1 Manual gates may be skipped under pressure when the only approver is also the author (Medium).
- RR-37-CG-2 Emergency changes without a second pair of eyes (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
