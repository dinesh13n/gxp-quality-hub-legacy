---
stage: "29 — AI Incident Response + BC/DR"
artifact: "communications-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["docs/37-operating-model/escalation-model.md", "docs/02-stakeholders/escalation-map.md (via Stage 37)", "docs/23-human-control/escalation-matrix.md", "docs/25-governance/accountability-map.md", "docs/37-operating-model/support-model.md", ".fde/orchestrator-decisions.md (OD-04, OD-13, OD-32)", "operations/incidents/INC-2025-014.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
Who is told what, when, by whom, and through which channel. The honest starting point: **the only human rung is Dinesh Naik; there is no customer, user group, security contact, compliance contact, regulator contact, vendor contact, press or legal role in the repository** (OD-04; ES-20..ES-25 have no owner). The plan therefore defines *audiences by role*, a fixed message template, and rules for what must never be said (no invented stakeholders, no claim of compliance, no "resolved" without evidence). Every external or role-holder contact below is **TBD/Unknown** and must be filled by Dinesh; none is invented.

## Findings
### CM-1 Audiences
| ID | Audience (role) | Holder today | Channel | Informed when |
|---|---|---|---|---|
| CM-A1 | Engagement lead / L3 / incident closer | Dinesh Naik | the engagement conversation (the interactive session where the agent reports) and OD log entry via orchestrator | any SEV-A at once; SEV-B at once if a tripwire or an approval is needed; SEV-C at the next report |
| CM-A2 | Orchestrator | `claude-fde-agent` (orchestrator duties; who runs them after Stage 38 is open, OD-34) | stage hand-off message | every incident that stops a stage |
| CM-A3 | Service owner RL-02 | VACANT (Dinesh INTERIM) | as A1 | SEV-B/C |
| CM-A4 | Security owner RL-05 | VACANT | TBD | SEV-A/SEV-B involving security; **cannot be informed today** |
| CM-A5 | Compliance/quality owner RL-06 | VACANT | TBD | SEV-A involving integrity/regulated act; **cannot be informed today** |
| CM-A6 | Integration/feed owner RL-08, process owner RL-03 | VACANT | TBD | IS-12, IS-08 |
| CM-A7 | Reviewers / users | none exist | n/a | n/a until users exist |
| CM-A8 | Vendors (GitHub, assistant, workspace) | no contract, SOW or contact on file (A-0B-01) | vendor channels Unknown | only if Dinesh decides; no data about the incident beyond what Dinesh approves (HAR-09) |
| CM-A9 | Regulators / customers' quality organisations | none; product is synthetic and not a GxP record (PNFR-20) | n/a | **not applicable while synthetic**; if real data is ever involved, notification duties are Unknown (regime Unknown, RS-06) and Dinesh decides before anyone is contacted |

### CM-2 Matrix: severity -> who, how fast (order, not clock times)
Clock times stay Unknown (no SLA; Stage 37 EM-3). "Order" means the sequence in which things happen.
| Severity | 1st | 2nd | 3rd | Follow-up |
|---|---|---|---|---|
| SEV-A | Dinesh (stop-the-line message, CM-T1) | orchestrator | role holders when staffed | written incident record to Dinesh; closure only by Dinesh |
| SEV-B | Dinesh in the next message | orchestrator | n/a | included in stage report |
| SEV-C | recorded in the stage report | n/a | n/a | none |

### CM-3 Message templates (fill in; no adjectives that claim more than evidence)
- **CM-T1 Stop-the-line (SEV-A/B).** `STOP: <scenario IS-xx> detected at <UTC> by <role> via <signal DS-xx>. Class <SEV>. What is known [Verified Fact]: ... What is inferred: ... What is unknown: ... Contained: <yes/no/how>. Evidence preserved at <path + sha256>. Needed from you: <HAR-xx approval / decision>. Nothing has been repaired or restored.`
- **CM-T2 Status update.** Same fields plus `Changed since last update`, `Next step`, `Decision needed`, each statement tagged Verified Fact / Inference / Assumption / Unknown.
- **CM-T3 Closure.** Cause (tagged), impact (what data/records/decisions were affected; "none" only with the check named), actions taken with approval references, residual risk (stays OPEN unless Dinesh records acceptance), lessons, changed documents.
- **CM-T4 Vendor/outside notice.** Not drafted: needs Dinesh's decision first (HAR-09); contact is Unknown.

### CM-4 Rules
1. Say what happened, what is known, what is not, and what you need. No blame, no speculation presented as fact.
2. Never name a person other than Dinesh Naik; refer to roles.
3. Never state or imply compliance, validation or regulatory standing (GD-11: Part 11 framing only).
4. Never state an incident is closed, a risk accepted or a restore approved unless a recorded Dinesh decision exists (HAR-11, TP-14).
5. Do not include secrets, real data or hostile payloads inline; reference path and hash.
6. Send nothing outside the engagement without Dinesh (HAR-09).
7. Disputed root cause (ER-12): state both positions as claims, do not decide; tie-break is Dinesh.

### CM-5 Gaps
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CMF-01 | [Verified Fact] Six of nine audiences have no holder or contact | escalation-model EF-01; this table | A SEV-A cannot reach any independent reviewer | High if activated | High | Who fills RL-05/RL-06? |
| CMF-02 | [Verified Fact] If Dinesh is unavailable nobody can be told or can decide (ER-18) | escalation-model | Work pauses; temptation to shortcut | High throughput, Medium quality | High | alternate approver (ES-09) |
| CMF-03 | [Verified Fact] INC-2025-014 shows the historical pattern: delayed feed, manual reconciliation, disputed root cause, follow-up owner unknown | `operations/incidents/INC-2025-014.md` | Same pattern would repeat for IS-12 | Medium | High | owner of follow-up |
| CMF-04 | [Unknown] Whether any external notification duty would apply to a real-data incident | RS-06 | Late or missed notification | Unknown | Low | compliance regime |

## Evidence References
`docs/37-operating-model/escalation-model.md` EM-1..EM-3, ER-01..ER-18; `docs/23-human-control/escalation-matrix.md`; `operations/incidents/INC-2025-014.md`; OD-04, OD-13, OD-32.

## Assumptions
- A-29-CM-1 [Assumption] Communications are in-conversation plus OD-log entries via the orchestrator, because no other channel exists. Confirm: Dinesh.
- A-29-CM-2 [Assumption] Vendor and regulator notices are out of scope until real data or a contract exists.

## Unknowns
- U-29-CM-1 All role holders and contacts except Dinesh.
- U-29-CM-2 Notification duties and clocks.
- U-29-CM-3 Who runs orchestrator duties after Stage 38 (OD-34).

## Unresolved Issues
- No contact list, no alternate approver, no non-Dinesh reviewer.

## Residual Risks
- RR-29-CM-1 Incident known only to the agent and one person (High if activated).
- RR-29-CM-2 Message accuracy depends on discipline in tagging (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
