---
stage: "13 — Requirements → Specs → Tests → Evidence Traceability"
artifact: "ai-quality-traceability.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/12-specs/acceptance-criteria.md", "docs/12-specs/business-rules.md", "docs/12-specs/spec-readiness.md", "docs/13-traceability/evidence/coverage.json", "docs/13-traceability/evidence/coverage_output.txt", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09, OD-10)", "docs/08-ai-qualification/qualification-decision.md", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Planned tests are PLANNED / NOT-RUN: nothing in this stage was executed against the application, and no evidence listed here as "expected" exists yet. Approval is Dinesh Naik's decision (HAR-11).**

No-AI product (OD-08): there are no AI-quality requirements to trace. The view traces the controls that keep it No-AI (FR-CO-04 -> PNFR-18 -> 37 ACs incl. static egress guards, Stage 32 tripwire) and the deterministic stand-ins (touchpoints T1-T5, determinism PNFR-17). Search recall is a baseline only (class C).

## Findings
### AIQ-1 Position [Verified Fact: OD-08; docs/08-ai-qualification/qualification-decision.md]
Dinesh answered **Accept No-AI** (OD-08, 2026-10-18). The product contains **no model call**. There are therefore **no AI-quality requirements** (no accuracy, groundedness, hallucination, bias or prompt-regression metrics) to trace: Stage 19 is not-applicable, Stage 22 is not triggered. Tracing AI-quality evidence here would be fabricating requirements. What *is* traceable is the **absence** of AI and the quality of the deterministic stand-ins.

### AIQ-2 Requirements that carry the No-AI position (planned tests) [Verified Fact: computed]
| ID | Requirement (abridged) | Rel | Acceptance criteria | #AC | #neg | Class | Evidence stage | Domain note |
|---|---|---|---|---|---|---|---|---|
| FR-CO-04 | The product SHALL contain no AI, LLM or ML call and SHALL perform no model-inference egress. Any change requir | R1 | AC-CO-11; AC-REV-07,17 | 4 | 4 | A | 16 |  |
| PNFR-18 | No model call in the product - 0 model calls; 0 model-inference egress; Stage 32 tripwire = 0 | R1 | AC-CO-11; AC-NFR-18; AC-OBS-06 | 4 | 4 | A | 16,31,32 |  |
| PNFR-17 | Core decision, rule, intake and metric paths reproducible - Identical input -> bit-identical output; character | R1 | AC-CO-13; AC-DEC-05; AC-GATE-15; AC-INT-20; AC-MET-21; AC-NFR-17; AC-POL-22; AC-REV-14 | 8 | 0 | A | 16 |  |
| FR-REV-01 | For triage outcomes the system SHALL display a rule-trace explanation generated from the rule table inputs (to | R1 | AC-REV-05..08 | 4 | 1 | A | 16 |  |
| FR-REV-03 | Keyword and field search (e.g. SQLite FTS5 or equivalent) SHALL retrieve evidence documents by text and by ref | R2 | AC-REV-09..15,17 | 8 | 4 | AC | 16 |  |
| FR-REV-04 | A structured, templated form for deviation/CAPA narrative fields MAY be provided; the author writes and signs  | R2 | AC-REV-18 | 1 | 1 | A | 16 |  |
| FR-INT-06 | Every exception SHALL carry an enumerated reason code and queue; classification SHALL be rule-based and determ | R1 | AC-INT-15,20 | 3 | 0 | AB | 16 |  |
| FR-ID-04 | A read-only joined view SHALL let an investigator see all linked objects for any identifier (touchpoint T5, de | R2 | AC-ID-13,17 | 3 | 1 | A | 16 |  |
| FR-GATE-06 | A reviewer SHALL be able to override, dismiss or refuse any rule-generated flag, classification or priority, w | R1 | AC-GATE-18..20; AC-REV-08 | 4 | 1 | A | 16 |  |
| PNFR-15 | Humans can understand, override and refuse any flag or recommendation - 100% of rule outputs show rule trace a | R1 | AC-GATE-20; AC-NFR-15 | 2 | 0 | A | 16 |  |
| PNFR-13 | Inbound content never acts as instruction or approval - 0 effects on decision fields from the planted-string f | R1 | AC-DEC-25; AC-INT-22; AC-NFR-13; AC-REV-04,10 | 5 | 5 | A | 16,26 |  |

Totals: 37 acceptance criteria (16 negative); class A 35 / B 1 / C 1.

### AIQ-3 AI-related criteria found by text scan [Inference]
AC-CO-11 (negative), AC-CO-12 (negative), AC-CO-15 (positive), AC-NFR-18 (negative), AC-NFR-20 (positive), AC-OBS-06 (negative), AC-REV-05 (positive), AC-REV-07 (negative)

### AIQ-4 Findings
- **[Verified Fact]** `FR-CO-04` (no AI/LLM/ML call, no model-inference egress) -> `PNFR-18` (0 model calls, tripwire = 0 at Stage 32) -> AC-CO-11, AC-CO-12, AC-OBS-06, AC-NFR-18 (static import/egress guards and a run-time counter). Evidence stages 16, 31, 32. All class A and negative/static in nature.
- **[Verified Fact]** The five Stage 8 touchpoints are deterministic: | Touchpoint | Requirement | Mechanism (No-AI) | Planned tests |
|---|---|---|---|
| T1 | FR-REV-01 | rules / templates / keyword-FTS / deterministic join | AC-REV-05..08 |
| T2 | FR-INT-06 | rules / templates / keyword-FTS / deterministic join | AC-INT-15,20 |
| T3 | FR-REV-03 | rules / templates / keyword-FTS / deterministic join | AC-REV-09..15,17 |
| T4 | FR-REV-04 | rules / templates / keyword-FTS / deterministic join | AC-REV-18 |
| T5 | FR-ID-04 | rules / templates / keyword-FTS / deterministic join | AC-ID-13,17 |. Each has an FR and planned tests; none requires a model.
- **[Verified Fact]** Search quality (`FR-REV-03`, R2): the only quality evidence possible is a recall *baseline* on a synthetic corpus of 3 base sentences (AC-REV-15, class C). It cannot support or refute a case for AI-assisted Q&A. Re-qualification is allowed only via RQ-1..RQ-3 (real corpus + >= 50 labelled questions, multilingual/OCR failure, or a named stakeholder request) and a new Dinesh decision [Verified Fact: qualification-decision.md].
- **[Inference]** Determinism is the "quality" property: PNFR-17 (identical input -> bit-identical output) with AC-DEC-05, AC-GATE-15, AC-POL-22, AC-INT-20, AC-MET-21, AC-REV-14, AC-CO-13, AC-NFR-17 and the Stage 7 goldens (CT-01..CT-03) as evidence. Template-rendered explanations (FR-REV-01) are tested for faithfulness to the rule trace by exact match, not by a judge model.
- **[Verified Fact]** Coding assistants used to build the system are dev tooling, not product AI (OD-08); their output is subject to the same tests.
- **[Unknown]** Whether a future AI-assisted touchpoint will be requested. If so, a new Stage 8 qualification and new requirements are needed before any AI-quality traceability exists.

### AIQ-5 Gap statement
No AI-quality gap exists *because* no AI-quality requirement exists. This is not a coverage claim; it is a scope fact tied to OD-08. The tripwire (PNFR-18) is the only continuing control and must be wired at Stage 32 [GAP-13-14].

## Evidence References
- `.fde/orchestrator-decisions.md` OD-08; `docs/08-ai-qualification/qualification-decision.md` (T1-T5, RQ-1..RQ-3); `docs/09-initial-prd/nfrs.md` PNFR-17/18; `docs/12-specs/acceptance-criteria.md`.

## Assumptions
- A-13-10 [Assumption]: OD-08 stands for R1/R2. [Verified Fact] A read-only grep in this stage for openai|anthropic|langchain|llm|gpt- over *.py, *.js, *.java, *.toml, *.txt outside docs/, .fde/ and data/ returned 0 files, so no model client is present in the legacy source (a name scan, not a proof of absence of egress).

## Unknowns
- U-13-09: any future request for AI-assisted Q&A (RQ-1..RQ-3).

## Unresolved Issues
- Tripwire wiring is a Stage 32 task (GAP-13-14).

## Residual Risks
- R-13-09 Scope creep: an AI feature added without re-qualification would have no requirement, test or evidence.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial traceability produced by script from docs/ (evidence/trace_parse.py, trace_compute.py). |

