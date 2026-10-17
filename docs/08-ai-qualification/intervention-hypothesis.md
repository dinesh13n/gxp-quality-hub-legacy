---
stage: "8 — AI-vs-No-AI Qualification"
artifact: "intervention-hypothesis.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/08-ai-qualification/ai-vs-no-ai-matrix.md", "docs/08-ai-qualification/intervention-options.md", "docs/03-problem-value/success-criteria.md", "docs/03-problem-value/value-hypothesis.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/repo-transformation-readiness.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

**Proposed (recommended, not approved) intervention: package P-NOAI = O1 + O2 + O3 + O4 + O5, with no AI element and no agency above A1.** Expected effect is stated as testable, mostly structural outcomes (attributable decisions, reconstructable history, one rule, one definition per figure, replay-safe intake, shared identity, reproducible totals). **No monetary benefit and no time-saving is asserted**: S1 (rising effort) is unmeasurable and every cost figure is an unverified assumption (OD-04, OD-07, C-4). Label: synthetic, unvalidated.

## Findings

### IH-1 Hypothesis statement

If the organisation (1) records an owner decision on the definition of closed/resolved/approved, or an explicit "accepted open" (O1), and (2) the system gains an append-only, attributable decision/event write path with a human approval gate, a single table-driven rule, a shared identity crosswalk, and non-destructive intake (O2), run on a schedule with run records (O3), and reported with one declared definition per figure (O4), supported by rule-based explanation, search and templates for the review touchpoints (O5), then the structural gaps RC-1..RC-8 close without any AI, and the Stage 3 success criteria that depend on them become measurable and attainable. [Inference]

### IH-2 Expected effect, by success criterion (Stage 3 `success-criteria.md`)

| Criterion | Mechanism in P-NOAI | Measurable after | Baseline status |
|---|---|---|---|
| SUC-01 no unsafe action = 0 | Approval gate in write path; CT-16 guard; no automation of disposition | Stage 15+ | Invariant |
| SUC-02 source attribution 100% of sample | Decision record carries actor, time, basis, evidence ref (RC-1, RC-2) | Stage 15+ | Unmeasured |
| SUC-03 definition transparency 100% | Definition tag on each figure (RC-3 decision, O4) | Stage 15+ | Unmeasured |
| SUC-07 replay safety = 0 change | Content-aware, non-destructive intake (RC-6) | Stage 15+ | Unknown |
| SUC-10 month-end comparability | One query/definition (RC-8) | Stage 15+ | Claim only (SC-04) |
| SUC-11 decision recorded | O1 outcome | Before Stage 13 | Gap |
| SUC-04/05/06/08/09 time and backlog measures | Enabled by timestamps and keys that do not exist today (RC-1, RC-2, RC-7) | Needs real baselines (Stage 34) | Unmeasured; K-04/K-05 unmeasurable (OD-07) |

[Inference] Several criteria cannot be baselined today because the system records no closure/evidence timestamps; P-NOAI therefore produces the first measurable baseline rather than an improvement over an existing one.

### IH-3 What would falsify the hypothesis

| ID | Falsifier | Consequence |
|---|---|---|
| FH-1 | Dinesh or any real owner reports that decisions and history are already recorded in an external system (U-05-02, H-10) | Scope of O2 shrinks to integration; re-run Stage 8 on the changed premise |
| FH-2 | Stage 34 baselining shows effort or delay is negligible (FAIL-06) | Reframe or stop |
| FH-3 | Deterministic rule/search quality is shown inadequate on real data (RQ-1..RQ-3) | Reopen AI qualification for that touchpoint only |
| FH-4 | RC-3 cannot be decided and engineering would have to choose a rule | Stop condition for O2's rule table; carry both definitions with tags (BR-01/BR-03), do not merge |

### IH-4 Sequencing constraints from Stage 7 (`repo-transformation-readiness.md`)

Planning is a "go"; changing code is a "no-go" until R-1 (executable), R-2, R-4, R-5 are met. P-NOAI must therefore be built behind the characterisation harness (CT-H1..H7) and the 15/15 mutant kill check on a BUILD branch, never in the working tree (OD-03a).

### IH-5 Why not "AI first, fix structure later"

[Inference] Evaluation of any AI element requires ground truth: decisions with outcomes, stable ids and history. Today none exist (RC-1, RC-2, RC-7). Building AI first would have nothing to measure itself against, and its outputs would sit on unowned definitions (RC-3). The deterministic package is therefore also the prerequisite for any later honest AI evaluation.

## Evidence References

`success-criteria.md` SUC-01..SUC-11, FAIL-01..FAIL-06; `confirmed-root-causes.md` CR-A, CR-D; `repo-transformation-readiness.md` R-1..R-5 and go/no-go table; OD-03a, OD-07.

## Assumptions

- A-08-10 P-NOAI is the unit Dinesh approves or amends; individual components may be dropped without invalidating the AI conclusion. Confirm: Engagement lead (Dinesh Naik).
- A-08-11 Effects are expected on the repository system; their transfer to a real organisation is untested (Stage 6 C-1).

## Unknowns

- U-08-08 Magnitude of any benefit (labour, delay, rework): no data. Stage 34.
- U-08-09 Build effort of P-NOAI: 0C S1/S2 envelopes may not include RC-6/RC-7/RC-8 work. Stage 9/13 estimate.

## Unresolved Issues

- RC-3 decision, R-4 dataset, R-5 rule authority, location of disposition (all Dinesh Naik).

## Residual Risks

- A purely structural benefit may not be what a real sponsor values; value remains a hypothesis (`value-hypothesis.md`).
- Self-approval: author and approver share one human/agent pair (ER-11).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial hypothesis. |
