---
stage: "42 — Executive Defence & Final Value Story"
artifact: "ai-decision-defence.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/08-ai-qualification/qualification-decision.md", "docs/08-ai-qualification/ai-vs-no-ai-matrix.md", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/39-drift/prompt-model-drift-metrics.md", "docs/26-tevv/tevv-results.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** The product is **No-AI**. Dinesh answered "Accept No-AI" (OD-08, 2026-10-18). Agentic AI was rejected; AI-assisted document Q&A (T3) was held as a conditional, re-qualifiable option. Stage 19 (intelligence core) and Stage 22 (agent engineering) are NOT APPLICABLE; the cost of model spend is USD 0 by design. This is a **decision defended on fit and risk, not on measured outcome superiority** (C-05, C-06).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### AI-1 The argument, link by link
1. [Verified Fact] All eight confirmed root causes are absences or design defects; none concerns interpreting uncertain or unstructured input. (`confirmed-root-causes.md` CR-A)
2. [Verified Fact] RC-3 (no owned definition of closed/resolved) is a governance decision; AI cannot supply an owner.
3. [Verified Fact] Candidate-touchpoint content is categorical and tiny: 11 fixed keys in 8,567 of 8,567 feed rows, 6 distinct `notes` values, 5 distinct exception explanations over 224 rows, 3 distinct first body lines over 1,200 documents. (Stage 8 EA-1..EA-6)
4. [Verified Fact] No business requirement BR-01..BR-13 asks for language understanding, generation or prediction; BR-08 forbids automating the disposition.
5. [Verified Fact] Instruction-like strings exist in the data (86 feed rows, 22 of 1,200 documents), so an LLM consumer would carry a risk that rules do not.
6. [Inference] The AI options scored 0 of 8 on root-cause coverage (O6 = 8, O7 = 9, O8 = 2 of 21 on the matrix) and fail or conditionally fail gates G2/G3. Reasoning: the matrix scored root-cause coverage, risk and fit.
7. [Inference] The decision is insensitive to price: AI loses with token cost set to zero (ER-3).
8. [Inference] The deterministic package is also the precondition for any honest later AI evaluation (ground truth, ids, history).

### AI-2 Per-touchpoint outcome
| Touchpoint | Outcome | Confidence |
|---|---|---|
| T1 case triage explanation | Rules, rule-trace text | High |
| T2 partner-feed exception classification | Rules with reason codes and quarantine, no ML | High (synthetic) / Medium (real) |
| T3 document Q&A | Keyword/field search now (R2, switched off by default); AI-assisted not selected; conditional via RQ-1..RQ-3 | Medium |
| T4 deviation/CAPA narrative | Rules/template; generation not selected | Medium |
| T5 cross-store investigation | Rules (crosswalk); agentic rejected | High |

### AI-3 How the decision is enforced
[Verified Fact] ADR-002 mechanisms: deny-list scan (TST-CO-11), egress tripwires (E05..E09, E26), `model_calls_total = 0`, `no-ai-check` rc 0, zero non-stdlib imports (Stage 26 RT-05 met; Stage 30 G5 pass). A single documented loopback-only `urllib.request` adapter exists (13 hostile URLs refused). Coding assistants used to build the system are development tooling, not product AI (OD-08); they remain in the AI register (OD-31).

### AI-4 Where the decision was tested against reality, and where it was not
| Aspect | Status |
|---|---|
| A real document corpus | **Not available**; real content could be multilingual or OCR-noisy and the synthetic bodies are English stubs (RQ-2) [Unknown] |
| Keyword-search recall vs a labelled question set | **Not measured**: no question set exists (RQ-1 proposes at least 50 questions and 80 % at top-5, unapproved thresholds) |
| A stakeholder asking for a language feature | None (RQ-3) |
| Reviewer time saved by rules vs AI | **Not measured**: reviewer minutes unknown |
| Whether No-AI helps users | **Unknown**: no users |

### AI-5 Hard questions
| Question | Defensible answer |
|---|---|
| Is the decision just conservatism? | It is explicit and reversible: three triggers (RQ-1..RQ-3) and a requirement that any AI element meet BR-AI-1..BR-AI-7 including HAR-08/09/10 approvals and an injection test set. |
| Are you saying AI would be worse? | No. We say the evidence does not show a need, and the risks are higher. We did not measure an AI alternative. |
| Why does this prove anything about GenAI skill? | It shows disciplined qualification: the right answer for this problem was not to use it, and that decision was approved by a human and enforced by tests. |
| What if the real data is messy text? | Then re-qualify via RQ-2; the baseline (FTS) gives the comparison that AI would have to beat. |
| Is there any AI in production? | No product AI exists. AI coding assistants were used to build the repository; that is declared, in the AI register, and a source of drift risk (`agent-drift-metrics.md`). |

## Evidence References
`docs/08-ai-qualification/` all files; OD-08; `docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md`; `docs/26-tevv/tevv-results.md` TR (D01, E26); `docs/30-release/go-no-go-criteria.md` G5; `docs/39-drift/prompt-model-drift-metrics.md`; C-05, C-06.

## Assumptions
- A-08-* (carried) agent-set thresholds RQ-1..RQ-3 are proposals; owner Dinesh. 
- A-42-06 [Assumption] The synthetic content shape is representative enough to rule out a language need. Confidence Low-Medium; resolved only by a real corpus.

## Unknowns
Real corpus characteristics; reviewer minutes; value of any AI element.

## Unresolved Issues
DN-1 (formal approval of the Stage 8 package P-NOAI is recorded through OD-08 for the No-AI answer; the remaining DN-2..DN-7 items belong to later decisions, most now "accepted open").

## Residual Risks
Re-qualification drift: an AI feature introduced later without the triggers being checked (mitigated by tripwires and the drift framework, not yet wired to CI).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
