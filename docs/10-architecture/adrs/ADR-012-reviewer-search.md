---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-012-reviewer-search.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/08-ai-qualification/qualification-decision.md", "docs/09-initial-prd/functional-requirements.md FR-REV-03"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-012 — Reviewer retrieval: SQLite FTS5 keyword/field search (R2) - no semantic search. Status: PROPOSED (recommended option B, R2 scope).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B, R2 scope).

### Traceability
FR-REV-03, FR-REV-02, FR-REV-01; PNFR-13; RC-1 (enabling); OD-08; OPD-12; RQ-1..RQ-3.

### Context
[Verified Fact] No search exists today; 1,200 + 420 documents (W-05). [Unknown] Whether the bundled SQLite build includes FTS5 (not checked - code execution is out of scope this stage); verify in sandbox at Stage 12/14. [Verified Fact] OD-08 excludes AI Q&A.

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. No search | Reviewers browse by id | Zero effort | Misses T3 baseline | Acceptable fallback |
| B. SQLite FTS5 + field filters - RECOMMENDED (R2) | Index text; filter by reference, doc_id, locale, version, effective_at; results are documents, never generated answers; snippets escaped | No new infra; deterministic | FTS5 availability Unknown; ranking quality unmeasured | High fit |
| C. Elasticsearch/OpenSearch | Search server | Powerful | Infra, HAR-05/08, cost | Over-built |
| D. Vector/semantic search | Embeddings | Better recall on paraphrase | Model dependency = violates OD-08 | Rejected |

### Decision / recommendation
Recommend B in R2 only; if FTS5 is unavailable fall back to LIKE/inverted index in Python.

### Consequences
- Positive: RQ-1 baseline measurable.
- Negative: no NL Q&A.

### Trigger to decide / revisit
Revisit via RQ-1..RQ-3 only.

## Evidence References
docs/08-ai-qualification/qualification-decision.md; docs/09-initial-prd/functional-requirements.md FR-REV-03

## Assumptions
A-10-13 Keyword search adequate (A-09-05).

## Unknowns
U-10-17 FTS5 present; U-S01 user need.

## Unresolved Issues
OPD-12.

## Residual Risks
Prompt-injection-like text displayed to users; mitigated by escaping/typing.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

