---
stage: "18 — Evidence-Driven Delivery Planning"
artifact: "evaluation-rubric.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: [".fde/orchestrator-decisions.md OD-08 (No-AI, Dinesh 2026-10-18)", "docs/08-ai-qualification/qualification-decision.md (T1..T5, RQ-1..RQ-3)", "docs/13-traceability/ai-quality-traceability.md", "docs/17-implementation-prd/{finalized-acceptance-criteria,release-boundaries}.md (FA-3 RH-1..RH-7, RB-2 FR-REV-03)", "docs/15-modernization/remaining-technical-debt.md RTD-79, RTD-80", "docs/14-transformation/transformation-gates.md TG-4 (D0..D5)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08): there is no model, prompt, retrieval or agent to evaluate. The stage prompt asks for an AI-quality rubric "where applicable"; it is not applicable. This file records that, defines the rubric that guards the No-AI decision, and gives the deterministic quality rubric used to evaluate each delivery increment.**

## Summary
Three rubrics: **ER-1 AI quality - not applicable** (with the re-qualification triggers that would make it applicable); **ER-2 No-AI tripwire rubric** (binary, every increment and Stage 32); **ER-3 Deterministic delivery-quality rubric** (scored per increment, used at increment exit and by Stage 26). A fourth, **ER-4 keyword-search relevance**, is defined but cannot be scored until a labelled question set exists (OPD-12). No score in this file has been measured.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### ER-1 AI quality rubric - NOT APPLICABLE
[Verified Fact] OD-08: product = rules / keyword-FTS search / templates / deterministic core; Stage 19 = not-applicable record; Stage 22 not triggered; Stage 32 tracks zero model calls. Groundedness, relevance, abstention, hallucination, prompt-injection and model-cost criteria therefore have no object. Re-qualification only via RQ-1..RQ-3 and a new Dinesh decision; if that happens, this rubric must be re-issued (v0.2) before any AI work item is planned. AI coding assistants used to build the system are dev tooling, not product AI (OD-08).

### ER-2 No-AI tripwire rubric (pass = all rows pass)
| # | Criterion | Measure | Pass | Evidence | Tag |
|---|---|---|---|---|---|
| N1 | No model / AI dependency | `python -m hub no-ai-check` deny-list (TST-CO-11) | rc 0 | check output | [Verified Fact] |
| N2 | No egress | egress tripwires (TST-CO-12, per-increment E0xEGRESS groups) | 0 attempts | test log | [Verified Fact] |
| N3 | Model calls counter | `model_calls_total` (G5, TST-NFR-18) | = 0 | metric dump | [Verified Fact] |
| N4 | Deterministic outputs | determinism across PYTHONHASHSEED / TZ / locale (G10, TST-CO-13) | bit-identical | test log | [Verified Fact] |
| N5 | No new dependency | stdlib-only import scan (HAR-08) | 0 non-stdlib imports in `hub/` | import scan | [Verified Fact] |

### ER-3 Deterministic delivery-quality rubric (per increment)
Scale per criterion: **0** = evidence missing or failing; **1** = evidence exists with a registered gap; **2** = evidence complete. An increment may exit only with **no 0 on a mandatory (M) row**; optional (O) rows inform the TEVV gate.
| # | Criterion | M/O | 2 = | Evidence source | Tag |
|---|---|---|---|---|---|
| Q1 | Behaviour preservation | M | golden-compare D5 = 0 with observed probes (FAC-05) | golden-compare report | [Verified Fact] TG-4 |
| Q2 | Acceptance coverage | M | every touched FR / FAC has a linked passing test; class-B in both modes | rtm.csv + logs | [Verified Fact] |
| Q3 | Negative-path coverage | M | refusal codes asserted for each new error code | test log; registry diff | [Inference] |
| Q4 | Safety defaults | M | shipped defaults unchanged or changed with approval_ref | config dump; audit | [Verified Fact] FF-2 |
| Q5 | Data integrity | M | backup checksum rc 0 before / after; legacy paths unchanged | checksum log; git diff | [Verified Fact] |
| Q6 | Audit integrity | M | `verify-audit` rc 0 after the run | command output | [Verified Fact] G3 |
| Q7 | Mutation strength | O | sampled mutants KILLED | mutation json | [Verified Fact] |
| Q8 | Runtime parity | O (M from W4) | green on 3.10 floor and 3.12+ | CI log | [Verified Fact] OD-24 |
| Q9 | Debt honesty | M | new debt registered with owner / due / risk | stage debt register | [Inference] |
| Q10 | Label honesty | M | all synthetic figures labelled; no approval implied | artifact review | [Verified Fact] OD-04 |

### ER-4 Keyword-search relevance (FR-REV-03, R2, OFF) - defined, not scorable
| Metric | Definition | Threshold | Status | Tag |
|---|---|---|---|---|
| Recall@10 | share of labelled relevant docs in top 10 | none set (OPD-12) | not scorable: no labelled set | [Unknown] |
| Engine parity | FTS5 and fallback return the same set for each query | identical | testable now (TST-REV-09..15) | [Verified Fact] |
| C3 read control | C3 results only with reason | 100 % | testable now | [Verified Fact] |
[Verified Fact] RTD-80: ranking quality unassessable on the shipped corpus; search stays off (RB-2).

### ER-5 Release-hypothesis evidence (Stage 9 RH-1..RH-7) as a product rubric
[Verified Fact] FA-3 status is carried unchanged: RH-1, -2, -3, -5, -6, -7 supported at mechanism level on synthetic data; RH-4 not yet shown (no completed cycles). Stage 26 re-scores each RH using ER-3 evidence; no value, time or cost claim (Stage 9 RH-C).

## Evidence References
OD-08; `docs/13-traceability/ai-quality-traceability.md`; `docs/17-implementation-prd/finalized-acceptance-criteria.md` FA-3.

## Assumptions
- A-18-ER-1 [Assumption] The 0/1/2 scale and M/O split are adequate for increment exit. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-18-ER-1 Labelled search set (OPD-12) - owner Engagement lead (Dinesh Naik); resolves only if R2 search enablement is wanted.

## Unresolved Issues
- None blocking.

## Residual Risks
- RR-ER-1 Scoring is done by agents; human review is limited to one person (Low-Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
