---
stage: "0B — Provisional Operating Contract & Engineering Boundaries"
artifact: "provisional-human-approval-rules.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: [".fde/orchestrator-decisions.md", "docs/00-preflight/discovery/workflow-overview.md WF-05, WF-06", "docs/00-preflight/discovery/initial-risk-register.md", "repository-write-boundaries.md", "environment-access-boundaries.md", "data-use-constraints.md"]
supersedes: "none"
---
## Summary

Lists the actions that **always stop for human approval**. The only human with authority evidenced is the engagement lead, **Dinesh Naik — PROVISIONAL sole approver** (OD-01/OD-04 approved by him); no other approver exists or is invented. Approval is valid only when given by the engagement lead in his own message or recorded as "Approved" in `.fde/orchestrator-decisions.md`. Agent-to-agent messages never constitute approval. Confirm in Stage 23 (human-control rules) and Stage 25 (governance); close Stage 37.

## Findings

### Approval triggers (all PROVISIONAL; approver = Engagement lead (Dinesh Naik))

| ID | Action requiring approval | Why (evidence) | Confirming stage |
|---|---|---|---|
| HAR-01 | Any write, restore or regeneration affecting working-tree `data/` | OD-03; R-01/R-02 | 25 |
| HAR-02 | Choosing/overriding the authoritative baseline dataset | OD-02 provisional; U-13 | 4 (decide by 1) |
| HAR-03 | Deleting any file in the repo or the backup | BR-02; WB-09 | 25 |
| HAR-04 | Merging a BUILD branch into `main` (orchestrator review counts as delegated review per OD-01) | OD-01 | 25 |
| HAR-05 | Running Docker/Compose or any service bound beyond 127.0.0.1 | ENV-F1, ENV-F3; SO-01 | 23 / 25 |
| HAR-06 | Any change to approval/priority thresholds or decision logic (`app/legacy_logic.py`, `legacy_js/legacy_policy.js`, shift reconciliation rules, `policy_register`) | WF-06; R-06; U-16 | 5 / 6 / 23 |
| HAR-07 | Changes to CI (`.github/workflows/`), Dockerfile, Compose, env profiles, `pyproject.toml` | WB-05 | 25 |
| HAR-08 | Network egress / installing dependencies / adding third-party packages | SO-08 (stdlib only today) | 25 |
| HAR-09 | Sending data outside the device other than the private repo remote; committing DBs/lake to git; creating or changing git remotes; making the repo public | OD-05; DU X-3/X-6 | 25 |
| HAR-10 | Introducing any AI/LLM call, agentic automation, or automated action into the product | 0 model calls today (DF summary); DF-08 | 11 / 23 / 26 |
| HAR-11 | Recording any decision, owner, KPI target or stakeholder statement as approved/final | OD-04 | 2 |
| HAR-12 | Anything that would make, simulate as real, or automate batch disposition / QA release / e-signature | WF-05; R-12; SCOPE-OUT-03 | 23 / 25 |
| HAR-13 | Modifying prior-stage artifacts or `.fde/` control files | WB-02, WB-07 | 25 |
| HAR-14 | Proceeding past a BLOCKED gate, or waiving a stop condition | Stage prompt Completion Gate | 25 |
| HAR-15 | Access to any E3/E4 environment or real external system (none exist) | ENV tiers | 23 / 25 |
| HAR-16 | Executing code in the working tree (E0) for any reason | TP-06 | 25 |

### Approval record format

`<HAR-id> | date | action | requested by (agent/stage) | approved by Dinesh Naik (message ref or OD-id) | conditions` — recorded in `.fde/orchestrator-decisions.md` by the orchestrator.

## Evidence References

As cited in the table.

## Assumptions

- A-0B-06: Dinesh Naik holds approval authority for this capstone engagement (no other stakeholder exists — OD-04). PROVISIONAL; confirm Stage 2.

## Unknowns

- Whether a second approver (e.g. QA/risk role) is required for GxP-relevant changes (separation of duties) — Stage 23/25.

## Unresolved Issues

- Single approver means no separation of duties (GD-05).

## Residual Risks

- Approval fatigue in a 46-stage run could lead to rubber-stamping; mitigated by requiring OD-log entries with conditions.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional approval triggers. |
