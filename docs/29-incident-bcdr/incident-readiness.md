---
stage: "29 — AI Incident Response + BC/DR"
artifact: "incident-readiness.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["docs/29-incident-bcdr/ (all 12 other artifacts)", "docs/29-incident-bcdr/evidence/SHA256SUMS.txt", "docs/37-operating-model/escalation-model.md", "docs/37-operating-model/support-model.md", "docs/25-governance/governance-readiness.md", "docs/27-hardening/production-readiness-checklist.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-30, OD-32, OD-33, OD-34)", "docs/00-preflight/operating-contract/stop-conditions.md (STOP-11)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
**Gate outcome (agent computation, a recommendation to the Engagement lead): CONDITIONAL PASS.** The documentary part of the completion gate is met: all 13 artifacts exist; each of the ten scope scenarios has a procedure (IS-01..IS-12 with containment CT-01..CT-12 and recovery RV-1..RV-11); a tabletop was run and recorded (as a desk walk-through plus a sandbox rehearsal); RTO/RPO are defined as targets. It is **not a PASS** because the evidence does not show that anyone can *do* this: the tabletop had no participants other than the agent, three of the five dimensions are Unknown or Partial, the highest-impact recoveries (restore of `data/`, rebuild on a second host) are unrehearsed, and the Stage 28 resilience design that this stage depends on was not available. **No blocking gap is recorded against this docs-only stage** [Inference; see the STOP-11 note in IR-3]. Nothing is accepted: every residual risk stays OPEN with owner "Engagement lead (Dinesh Naik)".

What "AI incident" means here was settled in the playbook: the product is No-AI (OD-08), so there is no model incident to prepare for; the realistic AI incident is a **build-side agent error** or a **deterministic control failure**, and dormant model scenarios are listed but have no procedures until AI is ever added.

## Findings
### IR-1 Completion-gate checklist
| Gate condition | Status | Evidence |
|---|---|---|
| Every listed scenario has a procedure | Met | playbook PB-3; containment CT-01..CT-12; recovery RV-1..RV-11 (prompt injection IS-01, unsafe actions IS-02, compromised tools IS-03, data leakage IS-04, bad retrieval IS-05, model/provider failure IS-06, cost runaway IS-07, corrupted configuration IS-08, infrastructure outages IS-09, disaster IS-10; plus IS-11, IS-12) |
| Detection, severity, containment, evidence preservation | Met (documents) | playbook PB-4; severity matrix; containment; forensics policy |
| Communications, recovery, RTO/RPO, failover | Met (documents); targets unmeasured | communications plan; `recovery-procedure.md`; `rto-rpo.md`; `failover-procedure.md` |
| Tabletop or simulation results recorded | Met, with limits | `tabletop-results.md` (desk + sandbox; no participants) |
| RTO/RPO defined | Met as targets/assumptions | `rto-rpo.md` RR-1 |
| All required artifacts at the paths | Met | 13 files under `docs/29-incident-bcdr/` (list in IR-5) |
| Critical gaps resolved or documented | Met (documented) | F-29-01..F-29-16 below; none resolved |
| Evidence supports the conclusion | Partly | see IR-2 |

### IR-2 Readiness by dimension
| Dimension | Rating | Why |
|---|---|---|
| Detection coverage | Partial | signals exist in code, nothing watches them (F-29-03, F-29-13) |
| Severity classification | Adequate on paper | proposed scale reuses Stage 37 classes; no clock times by design |
| Containment speed | Unknown | no responders to time; kill switch tool time 0.06 s (RH-12) |
| Evidence preservation | Partial | restore keeps replaced files; verification writes to the store (F-29-04) |
| Recovery to RTO/RPO | Not demonstrated | targets assumed; store restore works in a sandbox; device loss defeats RPO (F-29-02) |
| Communication | Not exercised | only Dinesh exists; templates drafted (F-29-07) |

### IR-3 Dependencies and notes
- **Stage 28 (resilience design): not available.** At the time of this run `docs/28-resilience/` does not exist on `main`; a branch `stage-28-resilience` exists in the local repo (it is checked out in the main working tree by the Stage 28 agent) and had no commits ahead of `main` when checked; its working-tree content was not read [Verified Fact: path absent on `main`, no commits ahead]. `failover-procedure.md`, `rto-rpo.md` and `dr-plan.md` therefore rest on the exit plan, failure semantics and the existing backup tooling. **Reconcile before Stage 30 consumes this stage (condition C-2).** The stop condition STOP-11 ("required upstream artifacts missing") is arguably triggered; the orchestrator told this run to proceed, so this run proceeded and flags it for the orchestrator and Dinesh to confirm or override [Inference].
- Stage 24 inputs were available and used (threat model T-01..T-26, RS-01..RS-16).
- Downstream: Stage 30 (release) should treat F-29-01 and the conditions as inputs; Stage 37 support model and escalation model should be reconciled with the severity matrix (the three SEV classes are unchanged, so no contradiction); Stage 38 handover should carry the runbook content (F-29-09).

### IR-4 Finding register (all OPEN; none fixed, none accepted)
Severity words are the agent's Inference. Owner of every item: Engagement lead (Dinesh Naik).
| ID | Finding | Evidence | Impact | Risk | Confidence | Suggested route |
|---|---|---|---|---|---|---|
| F-29-01 | [Verified Fact] A malformed anchor line makes `verify-audit` print the right tamper envelope, then crash with `KeyError` in the end-of-run anchor write; exit 1 instead of 17 | `evidence/s29-log-07-verify-audit-after-damage.txt`; `hub/security/audit.py` `read_anchors`; `hub/admin/cli.py` `close` | Automation keyed on 17 mis-handles it; fail-closed direction is kept | Medium-Low | High | Stage 30 hardening fix plus a test; not fixed here (VALIDATE mode) |
| F-29-02 | [Verified Fact] Baseline `data/` and its only backup (and the hub backups) are on one device; no off-device copy; HAR-09 requires approval | `../_data-backup-2026-10-17/`, RC-7/RC-8 | Device loss destroys baseline and backups together; regeneration equivalence is Unknown (F-29-12) | High if real data; Medium for synthetic | High | Dinesh decides on an encrypted off-device copy (HAR-09) |
| F-29-03 | [Verified Fact] No alerting, on-call or ticketing; logs are not persisted | support-model SM-3; `hub/obs/log.py` | Signals fire unseen; log evidence lost | High if activated; Low while inert | High | Stage 30/38 before any activation |
| F-29-04 | [Verified Fact] `verify-audit`, `backup`, `restore`, `migrate` append audit records and rewrite the anchor; no read-only verify mode | `hub/admin/cli.py`; logs 03-06 | Inspection alters evidence unless a copy is checked | Medium | High | policy FE-03 now; code option later |
| F-29-05 | [Inference] Backup `SHA256SUMS`/`MANIFEST.json` sit beside the files and share the host; no independent record of the audit head | `hub/ops/backup.py` | A host-level actor could alter files and manifest together | Low-Medium | Medium | option: record head + manifest hash in git-tracked evidence |
| F-29-06 | [Verified Fact] Restore does not merge records written after the backup; they are set aside | `restore`; log 08 | Real RPO loss; manual handling | Medium | High | decide re-ingest vs. review (A-29-RV-1) |
| F-29-07 | [Verified Fact] Single human rung (Dinesh), no alternate; RL-02/03/05/06/08 VACANT; INC-2025-014 follow-up owner unknown | escalation-model EF-01, EF-02; INC-2025-014 | Incidents stall or invite shortcuts; no independent reviewer for SEV-A | High (real use) | High | Dinesh names owners/alternate when real use is planned |
| F-29-08 | [Verified Fact] Stage 28 resilience design unavailable | `docs/28-resilience/` absent on main | Failover/RTO/RPO may need revision | Medium | High | reconcile (C-2) |
| F-29-09 | [Verified Fact] `operations/runbook.md` has no incident, restore, release or BC sections | runbook; SUF-02 | Procedures live only in stage docs | Medium | High | transcribe at Stage 30/38 (outside this stage's write boundary) |
| F-29-10 | [Verified Fact] RV-3, RV-4, RV-5, RV-10 unrehearsed | recovery-procedure RVF-04 | Highest-impact recoveries have no evidence | Medium | High | rehearse RV-3 on a sandbox copy of `data/` (Q-29-09) |
| F-29-11 | [Unknown] Whether a running HTTP server honours `hub.kill` after start | PBF-05 | Containment of a running server relies on stopping the process | Medium | Medium | sandbox check at Stage 30 |
| F-29-12 | [Unknown] Whether `python -m app.generate --reset` reproduces the 125-case baseline | DRF-02, OD-09 | Regeneration may not replace the baseline | Medium | Low | sandbox test (Q-29-09) |
| F-29-13 | [Inference] `data/` change is detected at stage boundaries by a check run by the same actor that could cause it; no preventive barrier; instruction-following detection is the agent's own self-check | STOP-01, STOP-05, TF-01/02 | Detection delayed and not independent | Medium | Medium | orchestrator check after each stage (exists informally); consider OS read-only for `data/` (Dinesh decision) |
| F-29-14 | [Verified Fact] No people-based tabletop has occurred | tabletop-results | Coordination and decision latency unproven | Medium | High | C-1 |
| F-29-15 | [Unknown] Where the hub config lives, who may edit it, how it is backed up | `hub/config.py`; DRF-05 | A wrong config after recovery could change authority | Medium | Medium | decide config home; commit with approval refs |
| F-29-16 | [Inference] No backup schedule; RPO depends on operator discipline | DRF-06 | RPO unbounded in practice | Medium | Medium | schedule when a service owner exists |

### IR-5 Artifact inventory (13)
`ai-incident-playbook.md`, `incident-severity-matrix.md`, `containment-procedures.md`, `forensics-evidence-policy.md`, `communications-plan.md`, `bc-plan.md`, `dr-plan.md`, `rto-rpo.md`, `failover-procedure.md`, `recovery-procedure.md`, `tabletop-scenario.md`, `tabletop-results.md`, `incident-readiness.md`, plus `evidence/` (17 files with `SHA256SUMS.txt`).

### IR-6 Conditions attached to CONDITIONAL PASS (owner, due, risk)
| ID | Condition | Owner | Due | Risk if not met |
|---|---|---|---|---|
| C-1 | Run a conversational tabletop with Dinesh as the L3 participant, or record that it is accepted open | Engagement lead (Dinesh Naik) | before the Stage 30 release decision | decision latency and comms untested (Medium) |
| C-2 | Reconcile failover, RTO/RPO and DR with the Stage 28 design once merged; issue v0.2 as an addendum | Engagement lead (Dinesh Naik); orchestrator drafts | before Stage 30 uses this stage | contradictory resilience claims (Medium) |
| C-3 | Triage F-29-01 (fix at Stage 30 with a test, or record a decision) | Engagement lead (Dinesh Naik) | Stage 30 | exit-code mismatch in automation (Low-Medium) |
| C-4 | Decide on an off-device copy of baseline and hub backups (HAR-09) or accept the single-device risk in writing | Engagement lead (Dinesh Naik) | before any real data and before Stage 38 handover | baseline loss on device failure (High if real data) |
| C-5 | Confirm or amend RTO/RPO targets and the AI-incident framing (A-29-RR-1..4, A-29-PB-1) | Engagement lead (Dinesh Naik) | Stage 30 | targets stay unadopted (Low) |
| C-6 | Transcribe incident, restore and continuity steps into the operations runbook | Engagement lead (Dinesh Naik) to assign | Stage 30/38 | procedures not where operators look (Medium) |
| C-7 | Name an alternate decision-maker and owners for RL-02/05/06/08 before any pilot | Engagement lead (Dinesh Naik) | before any pilot | stalls and shortcut approvals (High in real use) |
Dates are milestones, not calendar dates, because no schedule exists; no condition is accepted by anyone.

### IR-7 Questions for Dinesh (defaults taken under OD-32; not approvals)
| ID | Question | Default assumed |
|---|---|---|
| Q-29-01 | Take part in a live tabletop of TT-1 (as L3)? | desk + sandbox accepted for now |
| Q-29-02 | Confirm the AI-incident meaning AI-1..AI-4 | as written |
| Q-29-03 | Confirm RTO/RPO targets in `rto-rpo.md` | targets, unadopted |
| Q-29-04 | Approve an encrypted off-device copy of `data/` backup and hub backups (HAR-09)? | no copy; risk stays open |
| Q-29-05 | Route F-29-01 to a Stage 30 fix? | yes, as a finding |
| Q-29-06 | Name an alternate decision-maker (ES-09)? | none |
| Q-29-07 | Where should the hub config live and be backed up? | repo-tracked file with approval refs |
| Q-29-08 | Add incident/restore/BC sections to `operations/runbook.md` at Stage 30? | yes |
| Q-29-09 | Allow a sandbox test of data regeneration equivalence and a sandbox rehearsal of RV-3 on a copy of `data/`? | not run |

## Evidence References
Every artifact in this folder; `evidence/SHA256SUMS.txt`; OD-04, OD-08, OD-30, OD-32, OD-33, OD-34; STOP-01..STOP-12; HAR-01..HAR-16.

## Assumptions
- A-29-IR-1 [Assumption] CONDITIONAL PASS is the right outcome for a docs-only stage whose procedures are unexercised by people. Confirm: Engagement lead (Dinesh Naik).
- A-29-IR-2 [Assumption] The Stage 28 absence is non-blocking for a documentation stage; the orchestrator may overrule.
- A-29-IR-3 [Assumption] Milestone due dates (not calendar dates) are acceptable.

## Unknowns
- U-29-IR-1 Stage 28 content and its conflict with this stage.
- U-29-IR-2 Whether any consumer, business owner or auditor will ever use these documents.
- U-29-IR-3 Real RTO/RPO expectations.

## Unresolved Issues
- F-29-01..F-29-16 and conditions C-1..C-7.

## Residual Risks
- RR-29-IR-1 The documents may be read as capability when they are intent (Medium). Mitigation: every file carries the unvalidated label.
- RR-29-IR-2 The agent wrote, ran and graded the exercise (Medium).
- RR-29-IR-3 No risk is accepted; all stay OPEN (this stage cannot accept; HAR-11, TP-14).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
