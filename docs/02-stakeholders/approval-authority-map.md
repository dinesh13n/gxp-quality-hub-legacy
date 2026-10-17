---
stage: "2 — Stakeholder Discovery & Authority Confirmation"
artifact: "approval-authority-map.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md", "docs/00-preflight/operating-contract/provisional-tool-agent-permissions.md", "docs/00-preflight/operating-contract/stop-conditions.md", "docs/00-preflight/operating-contract/change-control-rules.md", "docs/domain-assurance.md", "docs/02-stakeholders/decision-rights-map.md"]
supersedes: "none"
---
## Summary

Who approves what, with evidence. Evidence grades: **E-A** = recorded approval in `.fde/orchestrator-decisions.md` ("Approved by Dinesh" or "Approved"); **E-D** = recorded as "Done" without approver wording; **E-P** = authority only proposed in a 0B/Stage 1 document written by an agent (not an approval); **E-N** = none.

**Result: no 0B approval trigger is upgraded to CONFIRMED.** Only OD-01 and OD-04 carry approval wording. A document written by an agent that names Dinesh Naik as approver is a proposal, not evidence of his authority (AG-5). Valid approval forms stay as defined in 0B: Dinesh's own message, or an "Approved" entry in the OD log (`provisional-human-approval-rules.md`). This stage's agent has TP-14 = Deny (may not record approvals).

## Findings

### A. Approvals actually evidenced

| Ref | What was approved | Approver | Evidence grade | Note |
|---|---|---|---|---|
| OD-01 | 46 sequential stages, stop only on BLOCKED, BUILD branches merged to main by orchestrator after review | Dinesh Naik | E-A [Verified Fact] | Covers HAR-04 as delegated review |
| OD-04 | No real stakeholders; repo evidence only; missing evidence = Unknown/Assumption owned by Engagement lead | Dinesh Naik | E-A [Verified Fact] | Basis for treating him as sole owner of unknowns |
| OD-02 | Baseline = shipped 125-case DB | n/a | "Provisional default - Dinesh may override" | Not an approval; HAR-02 stays open |
| OD-03, OD-03a, OD-06 | Backup, sandbox rule, tag | n/a | E-D | Executed; approval wording absent. [Inference] covered by OD-01 delegation |
| OD-05 | GitHub remote | n/a | "Pending repo creation" | HAR-09 open |

### B. Approval triggers HAR-01..HAR-16

| HAR | Action | Approver (0B) | Evidence grade | Stage 2 verdict |
|---|---|---|---|---|
| HAR-01 | Write/restore/regenerate working-tree `data/` | Dinesh | E-P | **Still PROVISIONAL** (consistent with OD-03/03a) |
| HAR-02 | Choose/override baseline dataset | Dinesh | E-P (OD-02 provisional) | **Still open**; blocks Stage 4 |
| HAR-03 | Delete repo/backup files | Dinesh | E-P | Still PROVISIONAL |
| HAR-04 | Merge BUILD branch to main | Dinesh; orchestrator review delegated | E-A for delegation (OD-01) | **Partly confirmed**: delegation to orchestrator review is approved; whether Dinesh must also personally approve is not stated |
| HAR-05 | Docker/Compose, non-loopback services | Dinesh | E-P | Still PROVISIONAL |
| HAR-06 | Change approval/priority thresholds or decision logic | Dinesh (+ domain owner unknown) | E-P | Still PROVISIONAL; domain owner of thresholds is a GAP (DR-23) |
| HAR-07 | Change CI, Dockerfile, Compose, env, pyproject | Dinesh | E-P | Still PROVISIONAL |
| HAR-08 | Egress, dependency install | Dinesh | E-P | Still PROVISIONAL |
| HAR-09 | Off-device data, git remote, public repo | Dinesh | E-P; OD-05 pending | Still PROVISIONAL |
| HAR-10 | Introduce AI/LLM or automation into the product | Dinesh | E-P | Still PROVISIONAL (Stage 23); CG-4 standing |
| HAR-11 | Record any decision/owner/KPI/stakeholder statement as final | Dinesh | E-A in spirit (OD-04) | **Confirmed in effect** [Inference]: OD-04 forbids fabricated approvals; the HAR text itself is still a 0B proposal |
| HAR-12 | Make/simulate/automate batch disposition, QA release, e-signature | Dinesh to approve any exception | E-P | **Prohibition stands**; no one is authorised to permit it; real authority is SH-15 (unnamed) |
| HAR-13 | Modify prior-stage artifacts or `.fde/` control files | Dinesh | E-P | Still PROVISIONAL |
| HAR-14 | Proceed past BLOCKED / waive a stop condition | Dinesh | E-P; OD-01 "stop only on BLOCKED" implies he is the resumer [Inference] | Still PROVISIONAL |
| HAR-15 | Access E3/E4 or real systems | Dinesh | E-P; none exist | Still PROVISIONAL; moot |
| HAR-16 | Execute code in working tree (E0) | Dinesh | E-P; OD-03a prohibits | Still PROVISIONAL |

### C. Domain approvals named in repo documents

| Approval | Approver in repo | Evidence | Verdict |
|---|---|---|---|
| Batch disposition | "authorized human review" (unnamed) | `domain-assurance.md` | Requirement [Verified Fact]; approver [Unknown]; GAP |
| Closing a deviation/CAPA | None; Compliance requires verifiable evidence | `operations-vs-risk-2024.md` | GAP |
| Modernisation proposal | "awaiting business baseline measurements and architecture review" | `historic-decisions.md` 2026 | Reviewer unnamed; GAP |
| Release of a change in the legacy service | Enterprise application owner role (release process) | `business-context.md` | Role unfilled; no approval process documented |
| "Stricter approvals" requested by operations 2024 | Outcome not recorded; parallel workflow retained | `legacy-operations-history.md` | Unknown |

## Evidence References

`.fde/orchestrator-decisions.md` (all rows), 0B approval rules, `domain-assurance.md`, `operations-vs-risk-2024.md`, `historic-decisions.md`.

## Assumptions

- A-02-05: Valid approval = Dinesh's own message or an "Approved" OD-log entry (carried from 0B). Confirm: Engagement lead (Dinesh Naik).
- A-02-06: "Done" OD entries (OD-03, OD-03a, OD-06) were executed with his knowledge under OD-01. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-02-08 Whether Dinesh must personally approve each BUILD merge (HAR-04) or OD-01 suffices. U-02-09 Who approves domain-level decisions.

## Unresolved Issues

- 14 of 16 HAR items remain PROVISIONAL because the only possible confirmation is Dinesh's explicit statement (see questions Q-02-01..Q-02-12 in `operating-contract-confirmations.md`).

## Residual Risks

- Agent-written documents repeating "approver = Dinesh" can create a false impression of ratified authority (BR-07).
- Approval fatigue / rubber-stamping across 46 stages (0B residual risk).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial approval authority map. |
