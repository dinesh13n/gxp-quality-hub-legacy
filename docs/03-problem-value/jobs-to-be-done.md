---
stage: "3 — Frame Problem & Value"
artifact: "jobs-to-be-done.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/personas.md", "docs/business-context.md", "docs/domain-assurance.md", "docs/historic-decisions.md", "docs/02-stakeholders/stakeholder-needs-matrix.md"]
supersedes: "none"
---
## Summary

Jobs and desired outcomes in technology-neutral form. Outcomes are phrased as direction plus measure; **no threshold here is agreed** (thresholds appear, labelled provisional, in `success-criteria.md`). Label: synthetic, unvalidated.

## Findings

| ID | Persona | Job (when ... I want to ... so that ...) | Desired outcome (direction, measure) | Traces to | Class |
|---|---|---|---|---|---|
| JTBD-01 | PER-01 | When an external update arrives for a case, I want to know whether it matches a case I already hold, so that I do not act on duplicates or orphans | Fewer unmatched/duplicate items reaching review (M: unmatched-reference rate; reconciliation delay) | SH-13, SH-07; IO-10 | [Inference] |
| JTBD-02 | PER-01, PER-02 | When I take a case to a decision, I want the evidence assembled and attributed to its source, so that I can decide without chasing it | Lower time to evidence (M: time to evidence); source attribution on every decision | `domain-assurance.md` | [Verified Fact] (metrics named) |
| JTBD-03 | PER-02 | When cases are open, I want to see which are ageing and why, so that I can prioritise | Backlog ageing visible and comparable (M: backlog aging) | SH-03, SH-10 | [Inference] |
| JTBD-04 | PER-03 | When a case is closed, I want proof the closure was evidence-based and approved by an authorised person, so that I can defend it in audit | 100 % of closures with retrievable evidence and approver (M: evidence-complete closure share); unsafe action count 0 | SH-06, SH-09; `domain-assurance.md` | [Verified Fact] (need), [Assumption] (100 %) |
| JTBD-05 | PER-04 | When the month ends, I want one agreed count of resolved cases and their cost, so that reconciliation is quick and uncontested | Single cut-off and denominator; month-end reconciliation effort (M: hours, unmeasured) | SH-05, SC-02, SC-04 | [Inference] |
| JTBD-06 | PER-05 | When a feed is delayed, replayed or revised, I want the effect contained and traceable, so that queues are not inflated and root cause is attributable | Replay/duplicate incidents not inflating exception queue (M: exception rate; reconciliation delay) | SH-07, SH-12; INC-2025-014 | [Verified Fact] (incident), [Inference] (outcome) |
| JTBD-07 | PER-06 | When a change is released, I want to know it will not break interfaces or the parallel workflow, so that I avoid rollback | Change failure/rollback count (M: unmeasured) | SH-04; SC-07 | [Inference] |
| JTBD-08 | PER-07 | When a batch disposition is needed, I want it presented for my human decision with sources, so that the decision stays mine | Disposition decisions made only by authorised humans (M: unsafe action count = 0) | SH-15; HAR-12 | [Verified Fact] |
| JTBD-09 | PER-02, PER-03, PER-04 | When we disagree about what "closed" or "resolved" means, I want a recorded decision from an accountable owner, so that all parties measure the same thing | Decision recorded with owner/date (non-technical outcome) | SC-01..03, DR-20 | [Verified Fact] (gap) |

## Evidence References

As per rows; metric names from `docs/domain-assurance.md` (backlog aging, unsafe action count, reconciliation delay, time to evidence, unresolved exception rate).

## Assumptions

- A-03-05: The desired outcomes are plausible direction-of-travel for the roles; none is agreed.

## Unknowns

- U-03-05 Relative priority of jobs; JTBD-09 cannot be fulfilled by this engagement (needs an owner).

## Unresolved Issues

- JTBD-09 depends on a decider who does not exist; Dinesh may record a capstone decision.

## Residual Risks

- Over-weighting JTBD-03 over JTBD-04 would repeat the unowned 48 h vs evidence trade-off.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial JTBD. |
