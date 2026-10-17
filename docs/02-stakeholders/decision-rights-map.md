---
stage: "2 — Stakeholder Discovery & Authority Confirmation"
artifact: "decision-rights-map.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md OD-01..OD-06", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md", "docs/00-preflight/operating-contract/provisional-tool-agent-permissions.md", "docs/00-preflight/operating-contract/open-governance-decisions.md", "docs/01-engagement/team-charter.md", "docs/01-engagement/engagement-go-no-go.md", "docs/domain-assurance.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/decisions/ADR-archived-007.md"]
supersedes: "none"
---
## Summary

Who decides what. Legend: **D** = decides (evidenced), **D\*** = decides PROVISIONALLY (assumed, not confirmed), **C** = consulted (role named in repo, unconfirmed), **I** = informed, **GAP** = no owner assigned anywhere in repo evidence. The only evidenced decision-maker is Dinesh Naik, and only for the decisions he has actually recorded: **OD-01 and OD-04 "Approved by Dinesh"; OD-03/OD-03a/OD-06 "Done"** (`.fde/orchestrator-decisions.md`). His authority beyond those is the Stage 0B assumption A-0B-06 / A-ENG-02 and remains **PROVISIONAL**. No client-side decision right is evidenced.

Key point: the repo documents a **decision that needs an authorised human** (`batch_disposition`, `domain-assurance.md`) but names no holder; this is a governance gap, not something to fill.

## Findings

### Engagement and agent-governance decisions

| ID | Decision | Decider | Consulted / Informed | Status | Evidence |
|---|---|---|---|---|---|
| DR-01 | Run all 46 stages sequentially; stop only on BLOCKED; merge BUILD branches after review | Dinesh Naik | orchestrator (I) | **D, confirmed** [Verified Fact] (OD-01 "Approved by Dinesh") | OD-01 |
| DR-02 | No real stakeholders; never fabricate approvals/KPIs | Dinesh Naik | all agents (I) | **D, confirmed** [Verified Fact] (OD-04 "Approved") | OD-04 |
| DR-03 | Baseline dataset choice (125-case DB vs 6,000-case regen) | Dinesh Naik | SH-03 (C, role unfilled) | D\* provisional default OD-02; **open** (OQ-03, GD-02) | OD-02 |
| DR-04 | Data backup and sandbox execution rule | Dinesh Naik via OD log | orchestrator (I) | Recorded "Done" (OD-03, OD-03a); no explicit "approved by" wording [Inference: executed under OD-01 delegation] | OD-03/03a |
| DR-05 | Tag `baseline-as-found` on a6eb4e8 | Dinesh Naik / orchestrator | none | Recorded "Done" (OD-06); GD-08 still lists confirmation to Stage 25 | OD-06 |
| DR-06 | Remote repo creation, push, CI-on-push | Dinesh Naik | none | D\*; OD-05 "Pending repo creation"; GD-09 open | OD-05 |
| DR-07 | Go / No-Go and gate overrides | Dinesh Naik | orchestrator proposes | D\*; Stage 1 "CONDITIONAL GO" is a **recommendation**, not an approval | `engagement-go-no-go.md` |
| DR-08 | HAR-01..HAR-16 approvals (data writes, deletes, merges, Docker, logic changes, CI, egress, AI introduction, etc.) | Dinesh Naik | none | D\* PROVISIONAL (confirm Stage 23/25) | `provisional-human-approval-rules.md` |
| DR-09 | Tool/agent permission matrix TP-01..TP-15 | Dinesh Naik | none | D\* PROVISIONAL (GD-04) | `provisional-tool-agent-permissions.md` |
| DR-10 | Whether a second reviewer is required for GxP-relevant changes | Dinesh Naik | SH-06, SH-09 (C, unfilled) | **Open** (GD-05, OQ-14) | `open-governance-decisions.md` |
| DR-11 | Precedence of instructions | Dinesh Naik | none | D\* PROVISIONAL (GD-15) | `stop-conditions.md` precedence |
| DR-12 | Setting a stage gate status | Stage agent self-assesses; orchestrator accepts/rejects; Dinesh overrides | none | D\* (TP-13) | `provisional-tool-agent-permissions.md` |

### Business / domain decisions (no confirmed decider)

| ID | Decision | Candidate decider (role named in repo, unconfirmed) | Status | Evidence |
|---|---|---|---|---|
| DR-20 | Definition of "closed" / "resolved", and 48 h clock | SH-03, SH-09, SH-05 disagree; **no decider** | **GAP** | `operations-vs-risk-2024.md`: "never formalized in the shared policy repository" |
| DR-21 | Faster month-end vs more evidence (finance vs risk) | **No decider**; "both requests remain active" | **GAP** | `historic-decisions.md` 2024 |
| DR-22 | Batch disposition / QA release | "Authorized human" (SH-15), unnamed | **GAP** (holder). Agents/engagement must never make or simulate it (HAR-12, STOP-07) | `domain-assurance.md` |
| DR-23 | Approval/priority thresholds (3 divergent rules) | None; "business rules have different effective dates and ownership" | **GAP** | `legacy-operations-history.md`; WF-06 (0A) |
| DR-24 | Retention, authorisation, audit-evidence rules | SH-06 role named; no policy decision recorded | **GAP** (decision), role unfilled | `business-context.md` |
| DR-25 | Release and interface changes | SH-04 role named | Role unfilled | `business-context.md` |
| DR-26 | Nightly file exchange (ADR-007) | "Owner transferred 2024", new owner unnamed | **GAP** | `ADR-archived-007.md` |
| DR-27 | Root-cause ownership and follow-up for INC-2025-014 | "Follow-up owner unknown" | **GAP** | `INC-2025-014.md` |
| DR-28 | Modernisation / AI intervention go-ahead | "2026: proposal awaiting baseline measurements and architecture review"; reviewer unnamed. Engagement-level go-ahead sits with SH-01 proxy | **GAP** (client) / D\* (engagement) | `historic-decisions.md` 2026 |
| DR-29 | GxP / Part 11 treatment (framing vs obligation) | None client-side; SH-01 may declare framing | **Open** (A-08, GD-11, OQ-09) | `domain-assurance.md` ("not compliance certification") |
| DR-30 | Steady-state ownership of contract, repo, data, runbooks | None | **GAP** (GD-13, Stage 37) | `open-governance-decisions.md` |
| DR-31 | Budget, deadline, success criteria | None; no SOW | **GAP** (OQ-07) | absence in repo |

## Evidence References

See `evidence_sources`.

## Assumptions

- A-02-04: Dinesh Naik is the sole sponsor, business owner and technical owner of this synthetic capstone until he states otherwise (A-ENG-02, A-0B-06). Confirm: Engagement lead (Dinesh Naik), Decision D-02-01.

## Unknowns

- U-02-06 Whether any client decider exists even as a persona. U-02-07 Who owns ADR-007 and INC-2025-014 follow-up.

## Unresolved Issues

- 10 business-domain decision rights (DR-20..DR-28, DR-30, DR-31) have no owner. These are governance gaps; engineering must not encode rules for them (CG-7).

## Residual Risks

- Silent adoption of one side of the ops/compliance/finance dispute in later design stages (ER-06).
- Sole-approver bottleneck and no separation of duties (ER-04, GD-05).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial decision-rights map. |
