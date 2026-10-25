---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "support-model.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["operations/runbook.md", "operations/incidents/INC-2025-014.md", "docs/operations-service-levels.md", "docs/23-human-control/escalation-matrix.md", "hub/ops/", "hub/obs/", "docs/21-integration/failure-semantics.md", "docs/33-vendor-risk/exit-plan.md", "docs/02-stakeholders/escalation-map.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
Support tiers for the hub in steady state. **There is no support function, no user base, no on-call, no ticketing system, no SLA and no incident history for the hub** (the one incident on file, INC-2025-014, concerns the legacy estate and has no follow-up owner). The hub is not deployed beyond loopback. So this model defines **tiers by capability and routing**, maps each tier to what the repo already provides (runbook, CLI, health, audit verification, release checklist), and leaves **every staffing, hours, response-time and tooling item as Unknown / VACANT**. Nothing here is a commitment by anyone.

## Findings
### SM-1 Tiers
| Tier | Purpose | Role | Holder | What the repo provides | State |
|---|---|---|---|---|---|
| T0 Self-service | Users and reviewers use the queue; error codes explain refusals | RL-11 | VACANT | stable error codes with exit-code map (Stage 12 v0.2; OD-29 keeps numbers); `E-*` codes in EH-01..EH-10 | codes [Verified Fact]; users VACANT |
| T1 Operate | Start/stop, health, logs, backup/checksum, `verify-audit`, catch-up run, kill switch | RL-02 Service owner (operator duty) | VACANT; Dinesh INTERIM | `operations/runbook.md` (`./run.sh`, `GET /health`); `hub/cli.py`; `hub/ops/backup.py`; `hub/obs/` | [Verified Fact] tools; owner not accepted |
| T2 Diagnose | Reproduce, trace via audit chain and run records, classify SEV-A/B/C | RL-02 with RL-08 (feeds), RL-03 (rules/definitions) | VACANT | `hub/runs/`, `hub/metrics/`, audit chain; characterization harness; `docs/21-integration/failure-semantics.md` | [Verified Fact] tools |
| T3 Change | Fix, release, flag move, rule-set change under `change-governance.md` | RL-02 under RL-03/RL-05 consent | VACANT; Dinesh INTERIM; agents execute | PR + regression + release checklist (OD-13, OD-23); `hub/ops/release.py` | [Verified Fact] mechanism |
| T4 Authority | Anything needing a human-only or risk decision | RL-01, RL-04, RL-05, RL-06 | Dinesh (RL-01) only | `escalation-model.md` | INTERIM / VACANT |

### SM-2 What each tier may do and may not do
| Action | T0 | T1 | T2 | T3 | T4 | Evidence |
|---|---|---|---|---|---|---|
| Restore from backup | no | request | request | prepare | approve (HAR-01) | STOP-01 |
| Add a Zone H holder | no | no | no | no | RL-01 approves (OD-17/31); RL-04 performs ZH acts | `zone_h.holders` |
| Waive a failed release gate | no | no | no | no | RL-01 (HAR-14) | EH-08 |
| Expose beyond loopback | no | no | no | no | RL-01 with RL-05 (HAR-05) | EH-05 |
| Make or simulate a disposition | never | never | never | never | RL-04 outside engagement only | HAR-12 |

### SM-3 Support-readiness checklist (what exists vs not)
| Item | Exists? | Evidence | Tag |
|---|---|---|---|
| Runbook | Partial: start, health, regenerate data; no incident, restore or release procedures in `operations/runbook.md` | `operations/runbook.md` (3 short paragraphs read) | [Verified Fact] |
| Health endpoint and metrics | Yes (loopback) | `GET /health`; `hub/obs/` | [Verified Fact] |
| Alerting / on-call | No | grep finds none; no telemetry sink (V-11, PIA) | [Verified Fact] |
| Ticketing / ITSM | No | none in repo | [Verified Fact] |
| Support hours, SLA, response targets | No | U-02-13; `operations-service-levels.md` is legacy history, not a hub SLA | [Verified Fact]; legacy doc not re-read in full |
| Knowledge base / user guide | Docs only (`docs/20-application`, `docs/21-integration`); no end-user guide verified | - | [Unknown] |
| Training for reviewers | No | no reviewer exists | [Verified Fact] |
| Backup and restore test | Backup + checksum verified at stage level (OD-03, OD-03a); restore drill by a service owner not evidenced | `SHA256SUMS.txt` | [Inference] |
| Capacity | 125 cases baseline; `group C` regression near the 180 s device cap (OD-21) is a test constraint, not a production limit | OD-21 | [Verified Fact] |
| Exit/continuity of toolchain | `exit-plan.md` exists at Stage 33 (PROPOSED) | `docs/33-vendor-risk/exit-plan.md` | [Verified Fact] |

### SM-4 Required before first real support (gate for any pilot, proposed)
1. Named RL-02 holder who has accepted the role (decision by Dinesh recorded).
2. Runbook extended with restore, incident and release sections (a Stage 28/29/30 matter; not done here).
3. Stage 29 incident model reconciled with `escalation-model.md`.
4. Support hours and response classes agreed with a real user group (Unknown today).

### SM-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| SUF-01 | [Verified Fact] No staffed support exists at any tier above T0 tooling | SM-1, SM-3 | A defect or alert has no first responder | Low while inert; High if activated | High | Who is RL-02? |
| SUF-02 | [Verified Fact] Runbook covers start, health and regenerate only | `operations/runbook.md` | Restore, incident and release steps live only in stage docs | Medium | High | Stage 28/30 to author runbook |
| SUF-03 | [Inference] The hub's refusal-by-default design reduces what T1 must do before activation to four things: keep the DB and anchor backed up, run `verify-audit`, keep the loopback bind, and keep the tripwires green | EH-03..EH-05; `hub/guards/` | A small initial support burden | Low-Medium | Medium | Confirm after Stage 27 |

## Evidence References
See `evidence_sources`. Escalation: `escalation-model.md`. Change: `change-governance.md`.

## Assumptions
- A-37-SM-1 [Assumption] Tier names and duties are a proposal, not an SLA. Confirm: Engagement lead (Dinesh Naik).
- A-37-SM-2 [Assumption] T1 and T2 can be the same person at pilot scale. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-37-SM-1 Number of users, hours, time zones, languages, and criticality classification.
- U-37-SM-2 Whether support would be in-house or outsourced; any tool (not present).
- U-37-SM-3 Runbook adequacy beyond the first lines read for this stage; a full read is advised at Stage 38.

## Unresolved Issues
- Staffing of T1..T3; incident integration with Stage 29; runbook extension.

## Residual Risks
- RR-37-SM-1 Defects found with nobody on the hook: High if activated, Low while inert (not accepted).
- RR-37-SM-2 Knowledge sits in stage documents and one person's head: Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
