---
stage: "8 — AI-vs-No-AI Qualification"
artifact: "ai-vs-no-ai-matrix.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/08-ai-qualification/intervention-options.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/business-requirements.md", "docs/00-preflight/ai-economics/cost-scenarios.md", "docs/00-preflight/ai-economics/quality-latency-cost-envelope.md", "docs/00-preflight/operating-contract/stop-conditions.md"]
supersedes: "none"
---
## Summary

Two scoring views: (A) the ten options against seven criteria plus three pass/fail gates, and (B) the five hypothetical touchpoints T1-T5 across No-AI / Rules / AI-assisted / Agentic. Scores are **agent judgements (Inference)** on a 0-3 scale with the rationale shown; they are not measurements. Totals are a sanity aid only: the decision rests on the hard gates and root-cause coverage (`intervention-options.md` F-08-OPT-2), not on the sum. Recommendation only, pending Dinesh Naik's decision.

## Findings

### A. Hard gates (pass/fail before scoring)

| Gate | Source | Meaning |
|---|---|---|
| G1 Human disposition preserved | BR-08, DR-22, HAR-12, STOP-07 | Option must not make, pre-fill as final or simulate batch disposition/QA release/e-signature |
| G2 Inbound content is data, never instruction | NFR-13, STOP-05, DF-08 (>=286 injected strings) | Option must have no path where inbound text can alter a decision |
| G3 Attributable and auditable | NFR-09, BR-07 | Every output traceable to inputs and rule/model version |

| Option | G1 | G2 | G3 |
|---|---|---|---|
| O0 | Pass (nothing automated) | Pass | **Fail** (no audit mechanism today, NFR-09 gap) |
| O1 | Pass | Pass | Partial (depends on human records) |
| O2 | Pass **by design requirement** (gate must exist and be tested, CT-16) | Pass (no text interpreted) | Pass |
| O3 | Pass | Pass | Pass if run records written |
| O4 | Pass | Pass | Pass |
| O5 | Pass | Pass | Pass |
| O6 | Pass if advisory only | Pass (structured features) | Conditional (model version/label provenance) |
| O7 | Pass only with mandatory human review of every output | **Conditional fail**: LLM reads text containing injected instructions (22 of 1,200 source docs and 86 feed rows contain instruction-like strings) so it needs guardrails that are themselves unproven here | Conditional (non-deterministic output) |
| O8 | Conditional (read-only tools per 0B) | **Conditional fail** (tool loop widens injection surface) | **Fail** (multi-step non-deterministic trace) unless fully logged |

### B. Option scoring (0 = poor, 3 = strong; maximum 21)

Criteria are the seven Required Analysis dimensions. C1 root-cause fit; C2 proportionality of intelligence to the evidenced need (3 = capability matched to need, 0 = grossly over- or under-powered); C3 safety and reliability; C4 cost and TCO versus 0C; C5 latency and operability; C6 explainability and auditability; C7 minimum agency (3 = least agency).

| Option | C1 | C2 | C3 | C4 | C5 | C6 | C7 | Total | Rationale highlights |
|---|---|---|---|---|---|---|---|---|---|
| O0 Status quo | 0 | 0 | 1 | 3 | 3 | 0 | 3 | 10 | Zero cost but root causes remain; under-powered |
| O1 Process/policy | 2 | 3 | 2 | 3 | 2 | 1 | 3 | 16 | Only route to RC-3; not self-enforcing |
| O2 Deterministic core | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 20 | Covers 5 RCs directly; effort is the cost (0C S1: indicative USD 13.4k gross 3-yr, Assumption) |
| O3 Workflow automation | 1 | 3 | 2 | 3 | 3 | 2 | 2 | 16 | RC-5 only; a scheduler acts without a person (low agency, no judgement) |
| O4 Analytics | 1 | 3 | 3 | 3 | 3 | 3 | 3 | 19 | RC-8 only; high on the rest because it is read-only |
| O5 Rules/search/templates | 1 | 3 | 3 | 3 | 3 | 3 | 3 | 19 | Matches the categorical/stub content; low root-cause coverage by itself |
| O6 Classical ML | 0 | 0 | 1 | 2 | 2 | 1 | 2 | 8 | No labels, no statistical root cause |
| O7 GenAI/RAG | 0 | 1 | 1 | 2 | 2 | 1 | 2 | 9 | Possible match only if real unstructured corpus exists (Unknown); token cost negligible but oversight and validation dominate |
| O8 Agentic | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 2 | Gap is a missing key, loop adds risk and cost |

[Inference] Reading: O2+O1 carry the coverage; O4/O5/O3 add narrow, low-risk value. Rank by total is O2 (20) > O4 = O5 (19) > O1 = O3 (16) > O0 (10) > O7 (9) > O6 (8) > O8 (2). Combined package P-NOAI = O1+O2+O3+O4+O5 covers all of RC-1..RC-8 either directly or by naming the decision needed (RC-3). Sensitivity: replacing every C4 score of O7/O8 with 3 (i.e., pretending AI were free) gives O7 = 10 and O8 = 4, which does not change the ordering; cost is not what rejects AI here.

### C. Touchpoint view (T1-T5)

Options per touchpoint: **N** = No-AI (manual/process or plain deterministic code), **R** = Rules/search/templates, **A** = AI-assisted (GenAI, human reviews), **G** = Agentic.

| Touchpoint | N | R | A | G | Deciding evidence | Outcome (recommendation) |
|---|---|---|---|---|---|---|
| T1 Case triage explanation | meets (rule trace only after RC-4/RC-3 decision) | **meets exactly** (8-line rule, 3 inputs) | adds paraphrase risk; no benefit evidenced | n/a | `app/legacy_logic.py`; NFR-15 override | **Rules** (rule-trace explanation); no AI |
| T2 Partner-feed exception classification | partial (today) | **meets** (fixed keys, 6 distinct notes values, 4 branches, reason codes) | no free text to interpret; injection channel (86 rows) | n/a | `app/partner_feeds.py`; 0C DF-05/08 | **Rules** with quarantine and reason codes; no AI, no ML |
| T3 Document Q&A | no search today | **meets current content** (FTS5/keyword over short stubs; fallback structured filters on `reference`, `doc_id`) | untested: needs real corpus (U-V02) and a labelled question set | n/a | 1,200 docs/3 distinct first lines; 421 files avg 339 B; no stakeholder request | **Rules now; AI-assisted not selected**; re-qualify on triggers RQ-1..RQ-3 |
| T4 Deviation/CAPA narrative | partial | **meets** (structured form/template; fields are classification, root_cause, status) | generated regulated text, no BR, no workflow | n/a | `deviations`, `capa_actions`; WF-04 data-only | **Rules/template**; narrative generation not selected |
| T5 Cross-store investigation | manual lookup by hand (MH-09) | **meets after RC-7 fix** (crosswalk + deterministic join, read-only view) | not needed | **rejected**: guessing links without keys | RC-7; Stage 6 "must not fabricate links" | **Rules** (read-only crosswalk view); no agent |

## Evidence References

`intervention-options.md`; `docs/06-root-cause/confirmed-root-causes.md`; `docs/00-preflight/ai-economics/cost-scenarios.md` (S1 TCO quoted from `economics-readiness.md` finding 4); `docs/00-preflight/ai-economics/solution-scenarios.md`; counts per `qualification-decision.md` Evidence Appendix.

## Assumptions

- A-08-03 Scores are agent judgement; Dinesh may re-weight. If he assigns a different weighting, gates G1-G3 and RC coverage remain the primary basis.
- A-08-04 "Indicative USD 13.4k" is the 0C Assumption (unverified price, effort and rates); not a quote.

## Unknowns

- U-08-03 Real reviewer-minute cost and labour rate (U-24, U-P02) that would shift C4. Owner: Engagement lead (Dinesh Naik); Stage 4/34.
- U-08-04 Whether keyword search satisfies real users on real documents (RQ-1).

## Unresolved Issues

- None blocking the matrix. Gate G2 for O7/O8 is "conditional" because no guardrail has been built or tested; this is a reason for non-selection, not a measured failure.

## Residual Risks

- Judgement scores may encode the author's bias against AI; mitigated by showing the sensitivity run and by explicit re-qualification triggers.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial matrix. |
