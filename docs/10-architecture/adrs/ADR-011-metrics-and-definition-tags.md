---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-011-metrics-and-definition-tags.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "sql/", "legacy_java/ReconcileLegacy.java", "docs/06-root-cause/confirmed-root-causes.md RC-8", ".fde/orchestrator-decisions.md OD-07"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-011 — Metrics module: one query path, definition tags, exact decimals. Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B).

### Traceability
FR-MET-01..08, FR-DEC-06, FR-POL-02; PNFR-16, PNFR-20; RC-8, RC-3; OD-07.

### Context
[Verified Fact] SQL `LEFT JOIN events` inflates SUM(amount) by 19.3% (742,956.61 vs 622,826.44, re-executed read-only); Java uses `double` and skips unparsable amounts (RC-8). [Verified Fact] OD-07: Stage 4 proxies are generator-bounded; K-04/K-05 unmeasurable (no real closure timestamps). [Inference] Without a declared definition no KPI is meaningful (RC-3).

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Fix the SQL/Java reports in place | Edit `sql/` and Java | Direct | Edits pinned wrong-but-golden numbers (HAR-06); consumers Unknown | Rejected for R1 |
| B. New metrics module over event store/projections - RECOMMENDED | Every figure = function(definition tag, policy version, window, denominator, exclusions) using `decimal.Decimal`; refuses mixing tags except labelled side-by-side; unparsable amounts raise errors; output labelled "synthetic, unvalidated"; legacy reports kept as comparators | Reproducible (PNFR-16); no fan-out; honest labels | Numbers will differ from legacy (documented, golden diff) | High |
| C. BI tool / warehouse | Power BI etc. | Self-service | Vendor, cost, HAR-08/09; definitions still undecided | Premature |

### Decision / recommendation
Recommend B.

### Consequences
- Positive: K-xx figures can be re-baselined at Stage 34 from event timestamps.
- Negative: no real timestamps today so most KPIs remain unmeasurable.

### Trigger to decide / revisit
Decide at Stage 12/13.

## Evidence References
sql/; legacy_java/ReconcileLegacy.java; docs/06-root-cause/confirmed-root-causes.md RC-8; .fde/orchestrator-decisions.md OD-07

## Assumptions
A-10-12 Python Decimal adequate for money.

## Unknowns
U-10-16 Month-end cut-off and cost source (OPD-08).

## Unresolved Issues
OPD-08.

## Residual Risks
Users compare new and legacy totals without context.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

