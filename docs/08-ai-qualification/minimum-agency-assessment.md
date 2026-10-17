---
stage: "8 — AI-vs-No-AI Qualification"
artifact: "minimum-agency-assessment.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md", "docs/00-preflight/operating-contract/provisional-tool-agent-permissions.md", "docs/00-preflight/operating-contract/stop-conditions.md", "docs/00-preflight/ai-economics/provisional-loop-budget.md", "docs/00-preflight/ai-economics/solution-scenarios.md", "docs/06-root-cause/confirmed-root-causes.md"]
supersedes: "none"
---
## Summary

**Minimum agency required: A1 (system flags or recommends; a human acts) for review-queue support, and A0 (no autonomy) for everything near disposition.** The only autonomous behaviour needed by the root causes is a scheduled job (RC-5), which is automation, not agency: it executes a fixed procedure and exercises no judgement. Agentic behaviour (A3+) is **explicitly rejected**, which means Stage 22 (agentic engineering) has nothing to build under this recommendation. Recommendation only; Dinesh Naik decides (HAR-10).

## Findings

### MA-1 Agency ladder

| Level | Behaviour | Applies here |
|---|---|---|
| A0 | Passive: stores, displays, answers a query | Reports, search, crosswalk view |
| A1 | Flags or recommends; human performs the action | Review-queue flag from rule (e.g. `manual_review_required`), exception reason codes |
| A2 | Drafts an action for explicit human approval | Not needed (T4 drafting not selected) |
| A3 | Takes reversible actions within a fixed policy, human reviews after | Not needed; scheduled reconcile is a fixed procedure (see MA-3) |
| A4 | Multi-step planning with tool use toward a goal | Rejected (T5/O8) |
| A5 | Autonomous in a regulated decision | Prohibited (HAR-12, STOP-07) |

### MA-2 Evidence per decision

| Question | Finding | Confidence |
|---|---|---|
| Which problem needs a system to act without a person? | Only RC-5 (reconcile starts only when someone runs it; `reconcile(limit=1000)` vs 8,567 backlog; no scheduler). A cron-style job of fixed logic suffices | High (mechanism), Low (impact) |
| Which problem needs a system to choose between alternatives? | None. RC-3/RC-4 choices belong to the owner (Zone H) | High |
| Which problem needs multi-step planning? | T5 only, and T5's blocker is the missing key (RC-7); planning cannot create a key | High |
| What is the downside of a wrong autonomous action? | Disposition or closure error in a regulated setting; corrupt or discarded evidence (RC-6) | High (as risk), no frequency data |
| Is the human approval path preserved at every level? | Required: BR-08, DR-22, HAR-12, STOP-07, CT-16. No option in this document bypasses it; the recommendation places an explicit approval gate in the write path (RC-1) | High |

### MA-3 Scheduled automation is not agency

[Inference] A scheduled reconcile (O3) runs the same code on a clock, records a run, and stops. It does not select tools, interpret text, or alter its plan. It is classed A1/A3-lite for risk purposes only because it writes statuses, so it must (a) write append-only, (b) record a run id, (c) be idempotent (NFR-11), (d) never touch disposition. HAR-07 applies if CI/config files change.

### MA-4 Agentic option explicitly evaluated and rejected (drives Stage 22)

| Aspect | Finding (0C reference) |
|---|---|
| Justifying requirement | None. T5 is hypothetical (A-S01) and the underlying gap is solvable at L1 |
| Cost shape | 0C: 6-step loop about 0.0305/0.0898/0.1573 USD per run (low/mid/high, assumption), quadratic context growth; trivial in USD, but each investigation still needs about 5 reviewer minutes (assumption) |
| Safety | Largest injection surface (tool results re-enter context); non-deterministic trace conflicts with NFR-09/NFR-16 |
| Limits if it were ever reconsidered | Read-only tools, no write tools, step cap per `provisional-loop-budget.md`, human review of every conclusion; plus a fresh re-qualification (BR-AI-1, BR-AI-6) |

### MA-5 Consequence for Stage 22

If Dinesh approves this recommendation, Stage 22 has no agent to design and should be recorded as "not applicable: agency rejected at Stage 8". If he does not approve, Stage 22 must start from MA-4 limits and cannot proceed without an RQ-4 result (qualification-decision.md).

## Evidence References

`provisional-human-approval-rules.md` HAR-07, HAR-10, HAR-12; `stop-conditions.md` STOP-05, STOP-07; `confirmed-root-causes.md` RC-5, RC-7; `solution-scenarios.md` S4; `cost-scenarios.md` T5 row.

## Assumptions

- A-08-09 Fixed-procedure schedulers are acceptable to the engagement lead as automation (not subject to HAR-10, which concerns AI/LLM calls and "automated action"). **Ambiguity:** HAR-10 also lists "automated action into the product"; Dinesh should confirm that a deterministic scheduled reconcile is covered by ordinary BUILD approval and not by HAR-10. Owner: Engagement lead (Dinesh Naik).

## Unknowns

- U-08-07 Whether the real organisation already schedules reconcile elsewhere (A-05-06). Would remove RC-5 work.

## Unresolved Issues

- A-08-09 interpretation of HAR-10 (non-blocking; resolve at Stage 9 PRD or before Stage 15).

## Residual Risks

- Scope creep: scheduled jobs tend to acquire decisions over time; BR-AI-2 and Zone H prohibit it but only tests will enforce it.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial assessment. |
