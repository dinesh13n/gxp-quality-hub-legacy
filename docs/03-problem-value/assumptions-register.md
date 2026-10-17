---
stage: "3 — Frame Problem & Value"
artifact: "assumptions-register.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/*.md", "docs/00-preflight/discovery/assumptions-unknowns.md", "docs/02-stakeholders/decision-rights-map.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

Assumptions and unknowns introduced or relied on in Stage 3. Every owner is "Engagement lead (Dinesh Naik)" because no other human exists (OD-04); confirmation due before the named resolving stage starts (no calendar dates can be committed without stakeholders).

## Findings

| ID | Assumption | Used in | Risk if wrong | Resolve by (stage) | Owner | Confidence |
|---|---|---|---|---|---|---|
| A-03-01 | Synthetic Gxp Group documents stand in for real client intent | all | Business case overstated | 4 | Engagement lead (Dinesh Naik) | Medium |
| A-03-02 | Role descriptions approximate real needs | personas | Wrong persona | 4 | Same | Low |
| A-03-03 | Synthetic data shows direction, not magnitude | canvas, value | False precision | 4 | Same | Medium |
| A-03-04 | Problem statement P-1..P-5 holds outside the simulator | statement | Solving a non-problem | 4, 6 | Same | Low |
| A-03-05 | Desired outcomes in JTBD are plausible | JTBD | Misprioritised work | 4 | Same | Low |
| A-03-06 | Documented five-step workflow is complete enough | journeys | Missed shadow practice | 5 | Same | Medium |
| A-03-07 | Workflow steps 1-5 bound the scope | scope | Scope gap | 4 | Same | Medium |
| A-03-08 | OD-02 (125-case DB) stays provisional baseline | scope, criteria | Wrong baseline | 4 | Same | Low |
| A-03-09 | MoSCoW priorities proposed by agent | requirements | Wrong order | 9 | Same | Low |
| A-03-10 | "Unless owner authorises" wording safely avoids deciding policy | BR-09 | Hidden policy choice | 9 | Same | Medium |
| A-03-11 | Archived SLO targets are usable starting points | NFRs | False thresholds | 4, 11 | Same | Low |
| A-03-12 | Thresholds are placeholders pending baseline and owner | criteria | Trivial targets | 4 | Same | Medium |
| A-03-13 | Relative "improve vs baseline" acceptable until Stage 4 | criteria | Unfalsifiable | 4 | Same | Medium |
| A-03-14 | Value hypothesis V0 is worth testing | value | Wasted effort | 4, 6 | Same | Low |
| A-03-15 | Regenerable synthetic dataset validates method only | value | Overclaim | 4 | Same | High |
| A-03-16 | Engagement lead is the sole decider for capstone decisions incl. DR-20/21 if he chooses (carried A-02-04) | all | Unowned policy remains | 4 | Same | High |

### Carried unknowns

| ID | Unknown | How resolved | Stage |
|---|---|---|---|
| U-03-01 | Magnitude and trend of exception effort | Baseline measurement | 4 |
| U-03-02 | Which of RP1-RP3 dominates | Root-cause analysis | 6 |
| U-03-03 | Whether the 2024 conflict is still live | Dinesh decision or documented waiver | 4 |
| U-03-04..08 | Headcount, priorities, step times, evidence location, sites | Stakeholder access (none) / baseline | 4, 5 |
| U-03-09..17 | Priorities, performance targets, retention policy, regulation, baselines, effect size, labour rate | Stage 4, 8, 11, 36 | various |

## Evidence References

As cited in each artifact.

## Assumptions

(this register)

## Unknowns

(see above)

## Unresolved Issues

- Decision requested of Dinesh Naik: record a capstone decision on D-OPS / D-EVID / D-FIN and closure-time expectation, or record them as "accepted open". Until then the problem is framed with both candidates measured separately.

## Residual Risks

- Sixteen unvalidated assumptions share one owner (ER-11).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial register. |
