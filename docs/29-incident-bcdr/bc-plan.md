---
stage: "29 — AI Incident Response + BC/DR"
artifact: "bc-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["docs/37-operating-model/service-ownership-map.md", "docs/37-operating-model/support-model.md", "docs/33-vendor-risk/exit-plan.md", "docs/33-vendor-risk/concentration-risk-analysis.md", "docs/21-integration/failure-semantics.md", "docs/operations-service-levels.md (legacy)", "operations/runbook.md", "operations/incidents/INC-2025-014.md", ".fde/orchestrator-decisions.md (OD-08, OD-23, OD-28)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
Business continuity plan for two things that can stop: (1) **the engagement's delivery** (building, testing, documenting the hub), and (2) **the hub in shadow operation**. The most important honest statement: **no business process depends on the hub today.** It is loopback-only, shadow, synthetic, has no known consumers (OD-28 b: complete as far as the repo shows; outside consumers Unknown), and the legacy estate is unchanged and byte-identical (SS-05). The legacy estate and its manual work-arounds continue regardless of the hub. So BC here is mostly about **keeping the engagement and its evidence recoverable**, not about keeping a production service up. The plan says what changes the day real users, real data or a scheduler exist.

## Findings
### BC-1 Critical functions and dependencies
| ID | Function | Depends on | Who does it today | Impact if lost | Tolerable outage (target, Assumption) |
|---|---|---|---|---|---|
| BF-1 | Build and test the hub (stages, PRs, regression) | AI coding assistant (V-04), laptop/VM (V-10), cloud workspace (V-05), GitHub (V-03), Python 3.10.12 | agent + orchestrator, Dinesh decides | Delivery delay; no data loss if repo and backups intact | days (A-29-BC-1) |
| BF-2 | Decide and approve (L3) | Dinesh Naik only | Dinesh | All T0 decisions stall (ER-18) | days; no alternate |
| BF-3 | Run the hub in shadow (loopback) | hub code, SQLite store, anchor, config, Python | operator (Dinesh INTERIM) | None for the business; shadow comparison paused | weeks (A-29-BC-1) |
| BF-4 | Keep evidence and baseline | `data/`, `../_data-backup-2026-10-17/`, git, `docs/*/evidence` | the orchestrator | Loss of baseline = loss of before/after comparison (SEV-A) | n/a: loss is not tolerable, recovery target in `rto-rpo.md` |
| BF-5 | Legacy partner-feed reconciliation (the real operational process) | legacy estate, manual spreadsheet practice (INC-2025-014) | not the hub; unknown people | Outside the repo; the hub does not own it | Unknown |
| BF-6 | Regulated acts (disposition, QA release, e-signature) | humans outside the engagement (HAR-12) | none in the repo; real authority outside | Never done by the hub | not applicable |

### BC-2 Scenarios and continuity strategy
| Disruption | Strategy | Manual work-around | Needs approval |
|---|---|---|---|
| Assistant unavailable (IS-06) | wait, or hand to another assistant / developers per exit plan V-04; `.fde/` working agreements and the OD log are the handover | Dinesh or a developer continues PRs with the same regression gates | Dinesh (vendor change) |
| Laptop/VM lost or full (IS-09/IS-10) | rebuild per `dr-plan.md` DR-3 from GitHub + backup | none | HAR-01 for `data/` restore |
| GitHub unavailable (V-03) | local clones carry full history; mirror to a new remote on Dinesh's decision (HAR-09) | continue locally | HAR-09 |
| Cloud workspace unavailable (V-05) | full hub regression on the reference laptop (slower; goldens are laptop-specific, OD-23) | split groups to stay under the 180 s call cap (OD-21) | none |
| Dinesh unavailable (ER-18) | **no alternate exists**; work pauses at the next T0 decision | agents continue only non-T0, read-only or docs work; SEV-A waits | a named alternate must be chosen by Dinesh (A-29-BC-3) |
| Hub outage in shadow (IS-08/IS-11/IS-12) | stop the hub; legacy estate unaffected | n/a | none to stop |
| Feed late/diverged (IS-12) | manual catch-up run (scheduler OFF); keep run record | the historical manual spreadsheet reconciliation exists but is NOT a designed fallback and loses the audit trail (INC-2025-014) | none |

### BC-3 What changes if the hub goes live (re-plan triggers)
Before any of these, this plan and the RTO/RPO targets must be redone and re-approved: (a) a real user or consumer exists, (b) real data enters (STOP-04), (c) the scheduler is switched on (HAR-10/OPD-11), (d) any non-loopback exposure (HAR-05), (e) a rule set or authority switch becomes active (RC-3/RC-4), (f) an owner accepts RL-02. At that point also required: a second host, off-device backups with a tested restore, persisted logs, alerting and an on-call rota (all absent today; support-model SM-4).

### BC-4 Roles during a continuity event (roles only)
| Role | Holder | Duty |
|---|---|---|
| Continuity lead | Dinesh Naik (only human) | decides invoke/stand down, approves restore and vendor changes |
| Orchestrator | `claude-fde-agent` | executes the documented steps, keeps records, never approves |
| Technical recovery | agent in a sandbox first | rehearse before touching working-tree data |
| Alternate decision-maker | none (ES-09) | gap |

### BC-5 Maintenance of this plan
Review at every release gate (Stage 30) and at each re-plan trigger in BC-3; contact lists are TBD; test by tabletop at least once per milestone [Assumption A-29-BC-2]; changes go in as a new version.

### BC-6 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| BCF-01 | [Verified Fact] No business process depends on the hub at present | OD-08, OD-28, loopback bind, SS-05 | BC burden is low today | Low (inert) | High | outside consumers Unknown |
| BCF-02 | [Verified Fact] Continuity of decisions rests on one person with no alternate | ER-18, EF-02 | Single point of failure | High (real use) | High | DQ-17 acknowledged for approvals, not for continuity |
| BCF-03 | [Verified Fact] The only operational incident on file (INC-2025-014) ended with manual spreadsheet reconciliation and no follow-up owner | `operations/incidents/INC-2025-014.md` | The real continuity practice is informal and outside the hub | Medium | High | who owns the legacy feed process |
| BCF-04 | [Inference] Tool concentration: assistant, workspace and GitHub are single providers with no contract | concentration-risk-analysis | A provider event stops delivery | Medium | Medium | VA-01..VA-07 proposals pending |
| BCF-05 | [Verified Fact] Runbook has no continuity content | `operations/runbook.md` | Procedures exist only in stage docs | Medium | High | transcribe at Stage 30/38 |

## Evidence References
See `evidence_sources`; `docs/33-vendor-risk/exit-plan.md` V-01..V-11; `docs/37-operating-model/escalation-model.md` ER-18.

## Assumptions
- A-29-BC-1 [Assumption] Tolerable-outage figures (days/weeks) are agent targets for the engagement, not agreed with anyone. Confirm: Dinesh.
- A-29-BC-2 [Assumption] Review cadence is per gate/milestone.
- A-29-BC-3 [Assumption] An alternate decision-maker is desirable; naming one is Dinesh's choice and is not done here.

## Unknowns
- U-29-BC-1 Business owners and real recovery expectations.
- U-29-BC-2 Whether outside consumers exist.
- U-29-BC-3 Real-world impact of legacy-estate outages (outside scope).

## Unresolved Issues
- No alternate approver; no business owner; no real RTO from a business; runbook lacks BC content.

## Residual Risks
- RR-29-BC-1 Engagement stalls if Dinesh or the assistant is unavailable (Medium).
- RR-29-BC-2 BC plan is untested by a team (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
