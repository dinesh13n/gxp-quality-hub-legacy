---
stage: "3 — Frame Problem & Value"
artifact: "value-hypothesis.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/success-criteria.md", "docs/00-preflight/ai-economics/economics-readiness.md", "docs/00-preflight/ai-economics/volume-assumptions.md", "docs/00-preflight/discovery/data-flow-overview.md", "docs/01-engagement/use-case-hypothesis.md", "docs/baseline-measurement-notes.md"]
supersedes: "none"
---
## Summary

**Value is a hypothesis: synthetic, unvalidated. No monetary figure is asserted.** There is no real labour rate, volume, or cost; Stage 0C items C-1..C-5 (owner Engagement lead (Dinesh Naik)) remain open. The hypothesis is given as a formula with unknown inputs and a plan to prove or kill it. Value is not tied to any technology; whether AI contributes is decided at Stage 8.

## Findings

### Hypothesis

> V0. If case-state definitions, external-information matching and evidence availability are made consistent while human approval is preserved, then reviewers will spend less time on reconciliation and rework, and finance, operations and compliance will be able to report the same case consistently. [Assumption]

### Value drivers (all unquantified)

| ID | Driver | Formula (inputs are unknowns) | Inputs | Class |
|---|---|---|---|---|
| VD-01 | Reduced manual reconciliation time | cases with manual reconciliation × minutes saved × loaded labour rate | Counts: Unknown; minutes: Unknown; rate: Unknown (0C C-5) | [Assumption] |
| VD-02 | Reduced rework | reworked cases × effort per rework × rate | Unknown (U-24) | [Assumption] |
| VD-03 | Fewer queue-inflation incidents | incidents/year × effort per incident | One documented in 2025 (`historic-decisions.md`), one in INC-2025-014; frequency Unknown | [Assumption] |
| VD-04 | Faster, uncontested month-end | hours/month before - after | Unmeasured | [Assumption] |
| VD-05 | Audit defensibility (risk avoided) | not monetised; reported qualitatively as evidence-complete share | SUC-02 | [Assumption] |

Only reference number in the repo: a **modelled** 0.601 labour hours/case on a regenerated 6,000-case dataset and 65.14 hours on the 125-case DB (DF-06). These are generator outputs ("modelled estimate"), **not** observations and are not used as value claims.

### How the hypothesis will be proven or killed

1. Stage 4: fix window, denominator, exclusions and baseline dataset (OQ-03, OD-02); measure SUC-04..SUC-10.
2. Stage 6: test whether RP1-RP3 explain measured effort; kill criterion FAIL-06.
3. Stage 8: compare no-AI deterministic options vs any AI option on the same measures (H5 vs H6).
4. Economics (Stage 36): needs real prices, volumes and labour rates (0C C-1..C-5).

### Plausibility assessment

| Dimension | Assessment |
|---|---|
| Direction of effect | Plausible [Inference]; stakeholders' own statements point there |
| Magnitude | [Unknown]; no data |
| Evidence strength | Low: synthetic documents, test-residue DB |
| Dependence on policy owner | High: V0 partly requires decisions DR-20/21 that no one owns |

## Evidence References

`docs/00-preflight/ai-economics/economics-readiness.md` C-1..C-5; DF-06; `use-case-hypothesis.md`.

## Assumptions

- A-03-14: V0 is worth testing. A-03-15: value can be measured on a regenerable synthetic dataset for method validation only.

## Unknowns

- U-03-16 Any real volume, labour rate, cost per case (U-24). U-03-17 Whether any value remains if the policy conflict is not decided.

## Unresolved Issues

- Dollar value cannot be stated; business case is not decision-grade (0C).

## Residual Risks

- Stakeholders or reviewers may read modelled hours as savings (FAIL-05).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial value hypothesis. |
