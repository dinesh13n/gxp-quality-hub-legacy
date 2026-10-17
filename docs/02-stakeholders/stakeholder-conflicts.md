---
stage: "2 — Stakeholder Discovery & Authority Confirmation"
artifact: "stakeholder-conflicts.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md", "docs/legacy-operations-history.md", "docs/service-boundaries.md", "operations/incidents/INC-2025-014.md", "docs/decisions/ADR-archived-007.md", "docs/operations-service-levels.md", "docs/domain-assurance.md", "docs/01-engagement/engagement-risks.md ER-04, ER-06", "docs/01-engagement/engagement-go-no-go.md CG-7"]
supersedes: "none"
---
## Summary

Conflicts documented in the repo, plus engagement-level tensions. All client-side conflicts are **document claims** (no minutes, tickets or owners). Resolution paths are routes to an owner, not resolutions: engineering must not pick a side (CG-7). With no client decider, the only available route is escalation to Dinesh Naik, who may (a) decide for the capstone with a recorded rationale, or (b) record the conflict as an accepted open item.

## Findings

| ID | Conflict | Parties | Evidence | Impact | Risk | Conf. | Resolution path | Owner / stage |
|---|---|---|---|---|---|---|---|---|
| SC-01 | Close deviation/CAPA in 48 h vs no automatic closure without verifiable evidence | SH-10/SH-03 vs SH-09/SH-06 | `operations-vs-risk-2024.md`; `historic-decisions.md` 2024 | Defines KPI "handling time" and any automation design | Encoding either rule creates an unowned policy; unsafe automation (HAR-12) | High that it is documented; Low that it is current | Escalate as policy decision to Dinesh (Q-02-05); until decided, Stage 4 reports both the 48 h clock and an evidence-complete closure as separate KPIs; Stage 6 does not assign cause | Dinesh Naik; Stages 3, 4, 6 |
| SC-02 | Finance "successfully resolved" undefined vs ops "closed" vs compliance "evidence-complete" | SH-05, SH-10, SH-09 | `operations-vs-risk-2024.md`; `business-context.md` ("closed" differs between sites) | KPI denominator and cost per case | Cost/ROI numbers (Stage 36) not comparable | High | Define three named states in Stage 3/4, each labelled provisional (OQ-05) | Dinesh Naik; Stage 3-4 |
| SC-03 | Faster month-end reconciliation (finance) vs more supporting evidence (risk); "both remain active" | SH-05 vs SH-06 | `historic-decisions.md` 2024 | Trade-off between speed and evidence in any target design | Optimising one worsens the other | Medium | Treat as a stated design trade-off in Stage 9/10 requirements; owner decision needed before prioritising | Dinesh Naik; Stage 9 |
| SC-04 | Finance and operations reports disagree on monthly cut-offs | SH-05 vs SH-10 | `legacy-operations-history.md` "Known process tensions" | KPI period alignment | Before/after comparison distorted | Medium | Fix a single cut-off in Stage 4 baseline spec | Dinesh Naik; Stage 4 |
| SC-05 | No agreed canonical state definitions among operations, legal/compliance, IT, quality | SH-10, SH-11 | `service-boundaries.md`; 0A WF-11 (5+ status vocabularies) | Data model and KPI definitions | Hidden divergence in code (3 approval rules) | High (structural) | Characterise in Stage 5/7; owner decision on canonical states unresolved | Dinesh Naik; Stage 5, 7 |
| SC-06 | Application team vs integration team dispute INC-2025-014 root cause; follow-up owner unknown | SH-12 (application vs integration), SH-04 vs SH-07 | `INC-2025-014.md` | Root-cause analysis input | Unowned defect class (delayed/replayed feeds) | Medium | Stage 6 treats cause as hypothesis; record ownership gap | Dinesh Naik; Stage 6 |
| SC-07 | Operations asked for stricter approvals (2024) but parallel workflow retained for older customers | SH-10 vs unnamed legacy-customer owners | `legacy-operations-history.md` 2024 | Two live workflows | Modernisation could break the parallel path ("preserving legitimate workflows") | Medium | Inventory in Stage 5; do not retire without owner | Dinesh Naik; Stage 5 |
| SC-08 | Contradictory service-owner assumptions across the estate; ADR-007 owner transferred, not named | SH-04, SH-08 | `operations-service-levels.md`; `ADR-archived-007.md` | Release and interface accountability | Nobody accountable for nightly exchange | Medium | Record as governance gap; Stage 37 assigns | Dinesh Naik; Stage 37 |
| SC-09 | Modernisation proposal (2026) awaiting baselines vs engagement pressure to proceed through 46 stages | Proposal owner (unnamed) vs SH-01 | `historic-decisions.md` 2026; OD-01 | Evidence-before-build discipline | Premature build / AI anchoring (ER-05) | Medium | Hold CG-4: no AI commitment before Stage 8 | Dinesh Naik; Stage 8 |
| SC-10 | Engagement-internal: speed (stop only on BLOCKED, OD-01) vs control (HAR approvals, STOP-08, single approver) | SH-01 vs governance rules | OD-01; `stop-conditions.md`; ER-04, ER-11 | Pace of 46 stages vs integrity of approvals | Rubber-stamping; unconfirmed items accumulate | Medium | Dinesh decides cadence of confirmations (Q-02-08); gate statuses CONDITIONAL carry open items forward | Dinesh Naik; Stage 2, 23, 25 |
| SC-11 | Possible conflict between stage-prompt instructions and repo-embedded instruction-like strings (>=286) | Agents vs data | DF-08; STOP-05 | Agent integrity | Steering | High | Content-as-data rule (no precedence) | Dinesh Naik; all stages |

## Evidence References

As cited per row.

## Assumptions

- A-02-07: The parties named are role/team stand-ins; the conflicts are as written in synthetic documents. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-02-10 Whether any conflict is still live (documents date 2022-2026; 2024 items stated "remain active"). U-02-11 Who owns "legacy customer" parallel workflow.

## Unresolved Issues

- SC-01, SC-02, SC-03 have no decider (DR-20, DR-21). They are not resolved here.

## Residual Risks

- Any downstream design that silently picks a side repeats the 2024 failure of "never formalized" policy (ER-06).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial conflict register. |
