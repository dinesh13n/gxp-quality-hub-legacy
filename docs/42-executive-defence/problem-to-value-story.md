---
stage: "42 — Executive Defence & Final Value Story"
artifact: "problem-to-value-story.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/", "docs/04-baseline-kpis/", "docs/06-root-cause/confirmed-root-causes.md", "docs/34-measure-after/", "docs/35-variance/", "docs/36-roi/"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** This traces the chain *symptom -> root cause -> baseline -> intervention -> control -> measured outcome -> value* and marks, at each link, whether evidence holds. The chain holds from symptom to control. It **breaks at "measured outcome"** (no after-window) and therefore at "value".

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### PV-1 The chain, link by link

| Link | Content | Evidence holds? | Class | Claim IDs |
|---|---|---|---|---|
| 1 Symptoms | Claimed rising exception effort (S1, no trend data); feed data inconsistent with core records (synthetic residue); "closed" means different things; a 2025 replay inflated the exception queue and caused a rollback; finance and operations cut-offs disagree | Claims exist in synthetic documents; truth Unknown | [Verified Fact] claims exist / [Unknown] truth | C-01 |
| 2 Root causes | RC-1..RC-8 (no decision record, mutable state, unowned definition, three approval rules, manual execution, destructive intake, no shared identity, no shared month-end definition) | Yes at repo level; not for delay, cost or effort | [Verified Fact] | C-02 |
| 3 Baseline | 22 KPIs, 16 synthetic values, 6 Unknown, freeze unsigned | Partly: method validated, magnitudes not decision-grade | [Verified Fact] | C-03, C-04 |
| 4 Intervention choice | No-AI package: process decisions, deterministic core, scheduled runs (held off), shared metric definitions, rules/search/templates | Yes; approved by Dinesh | [Verified Fact] | C-05, C-06 |
| 5 Build | `hub/` modular monolith, additive, stdlib | Yes in sandbox | [Verified Fact] | C-07..C-11 |
| 6 Controls | Zone H gate, hash-chained audit, definition tags, replay safety, quarantine, tripwires | Mechanisms tested; not exercised by a real holder | [Verified Fact] mechanism / [Unknown] operational effect | C-12, C-14 |
| 7 Measured outcome | Sandbox only: 3 parity pairs, K-03 4 of 4 tagged, K-07 replay `ok: true` in a sandbox run | **Breaks here**: no after-window, no users | [Verified Fact] | C-21, C-22 |
| 8 Value | Zero verified benefits; ROI, NPV, payback not computable | **Not established** | [Verified Fact] (absence) | C-25, C-26 |

### PV-2 Which root cause does the hub address, and what evidence of effect exists
| RC | Hub mechanism (built) | Evidence of mechanism | Evidence of effect on a real process |
|---|---|---|---|
| RC-1 decision record | Append-only decision events with actor and basis; Zone H gate | Tests and attack suite; mutants M1, M2 killed | None (0 human dispositions, 0 holders) |
| RC-2 mutable state | Append-only events, projections | Backfill: 125 imported, 0 projection mismatches | None |
| RC-3 unowned definition | Candidate policies, definition tags on metrics; verdicts return `not_available_no_adopted_policy` | K-03 4 of 4 tagged values (sandbox) | None; **decision DR-20/21 still nobody's** (accepted open) |
| RC-4 three rules | Single rule service; as-found rule sets loaded inactive | Inactive by design | None; activation needs a human decision and holders |
| RC-5 manual execution | Idempotent runs and run records; scheduler OFF | Mechanism tests | None; scheduler deliberately off |
| RC-6 destructive intake | Raw store, content-hash idempotency, quarantine | Replay safety: 8,567 re-delivered rows all NOOP_DUPLICATE, queues unchanged (sandbox) | None |
| RC-7 no shared identity | Explicit crosswalk, exact-key matching | 8,109 exceptions on shadow intake (7,903 UNMATCHED_REF) show the legacy data does not link, as expected for test residue | None |
| RC-8 month-end definitions | One metrics query path, exact decimals | Month-end total 622,826.44 vs legacy SQL 742,956.61 (DV-01, unapproved) | None |

[Inference] The mechanisms address the root causes as diagnosed; reasoning: each RC is an absence, and each mechanism supplies the absent element. This is an argument from design, not a result.

### PV-3 What the story can honestly claim as "value" today
1. **Risk-surface reduction in design, not in operation.** The hub makes certain failures structurally refused (a decision without evidence, an AI call, an unapproved authority flip). [Verified Fact] tested in a sandbox. [Unknown] whether it reduces real incidents.
2. **A reusable, evidenced method** (baseline, comparability check, leakage and cost structure) that can be re-run the moment a real window exists (Stage 34/35/36 v0.2). [Verified Fact] the structure exists; [Unknown] the numbers.
3. **Decisions surfaced.** The engagement turned unowned policy (DR-20/21, rules, retention, holders) into an explicit register with owners. [Verified Fact] (`accepted open` records, K-11 = 2 of 2 as a record that nobody decided).

None of the three is a saving. Do not present them as one.

### PV-4 The five value drivers (all Assumptions)
VD-01 reconciliation time, VD-02 rework, VD-03 queue-inflation incidents, VD-04 month-end, VD-05 audit defensibility: [Verified Fact] none has a rate, volume or measured effect (C-26). All five depend on people using the hub; K-21 = 0 of 125 (BA-F4, [Inference]).

## Evidence References
`docs/03-problem-value/problem-framing-canvas.md`, `value-hypothesis.md`; `docs/06-root-cause/confirmed-root-causes.md`; `docs/04-baseline-kpis/baseline-kpi-sheet.md`; `docs/34-measure-after/after-intervention-kpi-sheet.md`; `docs/35-variance/before-after-analysis.md`; `docs/36-roi/verified-benefits.md`; `docs/16-repo-validation/behavior-difference-report.md`.

## Assumptions
- A-03-14 (carried) [Assumption] The value hypothesis V0 is worth testing. Owner: Dinesh Naik.
- A-42-04 [Assumption] The hub's mechanisms would work in a real process as they do in the sandbox. Owner: Dinesh; resolved only by a pilot.

## Unknowns
- Magnitude of any effect; frequency of replay incidents; time spent on reconciliation; labour rate; whether closed/resolved will ever have an owner.

## Unresolved Issues
- Baseline freeze unsigned (D-34-04); A-04-01 addendum not raised; after-window undefined (D-34-02).

## Residual Risks
- Misreading parity as improvement, or "unchanged by construction" as "no regression".

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
