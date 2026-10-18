---
stage: "13 — Requirements → Specs → Tests → Evidence Traceability"
artifact: "cost-traceability.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/12-specs/acceptance-criteria.md", "docs/12-specs/business-rules.md", "docs/12-specs/spec-readiness.md", "docs/13-traceability/evidence/coverage.json", "docs/13-traceability/evidence/coverage_output.txt", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09, OD-10)", "docs/00-preflight/ai-economics/preliminary-tco.md", "docs/00-preflight/ai-economics/economics-readiness.md", "docs/12-specs/features/f07-metrics-definition-tags.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Planned tests are PLANNED / NOT-RUN: nothing in this stage was executed against the application, and no evidence listed here as "expected" exists yet. Approval is Dinesh Naik's decision (HAR-11).**

Cost view: the PRD has no cost/budget requirement beyond metric correctness (BR-10, FR-MET-04), a cost placeholder (FR-MET-08, R2) and the zero-model-call tripwire (PNFR-18). 21 ACs trace; infrastructure/run-cost has no requirement (GAP-13-16). All cost inputs remain Assumptions (OD-04).

## Findings
### COST-1 What "cost" means in this PRD [Verified Fact]
Stage 9 contains **no cost, budget, TCO or capacity-cost requirement**. Cost appears in three narrow forms: (1) *case cost and avoidable rework attributable per case/period* (BR-10, Should) realised by month-end metric correctness FR-MET-04 and the R2 placeholder FR-MET-08 (OP-MET-05 returns E-MET-NOT-AVAILABLE until a cost input and owner exist, OPD-08); (2) *zero model-call cost* as a tripwire (PNFR-18, QD-4 in `nfrs.md`); (3) reproducibility/labelling of any figure (PNFR-16, PNFR-20). `docs/09-initial-prd/nfrs.md` states "No benefit is quantified" and U-09-03 "Real volumes, timings, labour and cost (no production telemetry; OD-04)".

### COST-2 Requirement -> test (cost view)
| ID | Requirement (abridged) | Rel | Acceptance criteria | #AC | #neg | Class | Evidence stage | Domain note |
|---|---|---|---|---|---|---|---|---|
| FR-MET-04 | Month-end totals SHALL be computed by one documented query/function on one configured cut-off and denominator, | R1 | AC-INT-27; AC-MET-09..13 | 6 | 4 | A | 16 |  |
| FR-MET-06 | Each KPI SHALL document its window, denominator and exclusions, and SHALL be reproducible from them; every KPI | R1 | AC-MET-14 | 2 | 1 | A | 16 |  |
| FR-MET-08 | Case cost and avoidable rework SHALL be attributable per case and per period on the agreed cut-off. | R2 | AC-MET-20 | 1 | 1 | A | 16 | R2 placeholder: E-MET-NOT-AVAILABLE |
| PNFR-18 | No model call in the product - 0 model calls; 0 model-inference egress; Stage 32 tripwire = 0 | R1 | AC-CO-11; AC-NFR-18; AC-OBS-06 | 4 | 4 | A | 16,31,32 | tripwire for Stage 32 |
| PNFR-16 | KPIs reproducible from documented window, denominator, exclusions - 100% of KPIs documented; re-run gives iden | R1 | AC-MET-14; AC-NFR-16; AC-OBS-08 | 3 | 0 | A | 16,31 |  |
| PNFR-06 | Reviewer-facing retrieval and queue refresh does not impede handling - UNKNOWN target: R1 must MEASURE p50/p95 | R1 measure | AC-NFR-06; AC-OBS-05; AC-REV-19 | 3 | 0 | A | 16,27,31 |  |
| PNFR-20 | Outputs from synthetic data are labelled - 100% of KPI outputs and reports labelled 'synthetic, unvalidated' w | R1 | AC-MET-02,08; AC-NFR-20 | 3 | 0 | AC | 16 |  |

Totals: 21 acceptance criteria (10 negative); class A 20 / B 0 / C 1.

### COST-3 Findings
- **[Verified Fact]** `docs/00-preflight/ai-economics/` (Stage 0C) holds provisional TCO, token and loop budgets: every price, effort and usage input is an **Assumption**; gross cost only, no benefits (OD-04). With OD-08 (No-AI) the token/context/loop budgets are void: expected model cost is 0, to be verified by the tripwire.
- **[Verified Fact]** `FR-MET-04`'s tests (AC-INT-27, AC-MET-09..13) check correctness of money arithmetic (exact decimal, no join fan-out, unparsable amounts surfaced); the legacy figure 742,956.61 vs 622,826.44 (DV-01) is the preserved-vs-fix case. They do **not** evaluate the economics of running the product.
- **[Verified Fact]** `operating_costs.total_cases` is random, not "cases created" (OD-07); AC-MET-16 refuses it as a source (E-MET-SOURCE-REFUSED). Therefore no cost-per-case KPI can be produced from shipped data.
- **[Inference]** There is no requirement or planned test for infrastructure cost, build/run effort, storage growth, or the cost of reviewer time; Stage 32 (FinOps/TCO) will have only PNFR-18 as a measurable control. This is a requirements gap, not a test gap [GAP-13-16].
- **[Unknown]** Cost data source and owner (OD-S12-08/OPD-08); real volumes; labour rates.

## Evidence References
- `docs/00-preflight/ai-economics/*`, `docs/09-initial-prd/nfrs.md`, `docs/12-specs/features/f07-metrics-definition-tags.md`, `docs/12-specs/acceptance-criteria.md`, `.fde/orchestrator-decisions.md` OD-04, OD-07, OD-08.

## Assumptions
- A-13-12 [Assumption]: cost is out of R1 product scope except the items above; Stage 32 may add requirements.

## Unknowns
- U-13-11: cost data owner and source (OD-S12-08).

## Unresolved Issues
- GAP-13-16 (no TCO requirement).

## Residual Risks
- R-13-11 Cost claims at Stage 32/36 may have no traced requirement or evidence.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial traceability produced by script from docs/ (evidence/trace_parse.py, trace_compute.py). |

