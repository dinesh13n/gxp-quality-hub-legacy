---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-009-identity-crosswalk.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/09-initial-prd/functional-requirements.md FR-ID-*", "app/store.py"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-009 — Shared identity via explicit crosswalk table (no inference of links). Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B).

### Traceability
FR-ID-01..04, FR-INT-05, FR-GATE-02; RC-7; PNFR-11.

### Context
[Verified Fact] `cases` has no batch/deviation/CAPA/feed key; `partner_feeds.ref_id` has no FK; five status vocabularies; 98% orphan rate is generator-shaped (R-05, only absence of constraints is claimed) (RC-7). [Verified Fact] FOREIGN KEY pragma is set in `store.connect` but not in other direct connections (DM-02).

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Add FK columns to legacy tables | ALTER legacy schemas | Familiar | Modifies legacy data/schema; generated data has no true keys | Poor |
| B. `crosswalk_link` table in hub DB - RECOMMENDED | Rows: from_type/id, to_type/id, key_used, creator (rule|human), created time; unique matches only by exact configured key; orphans stay orphans; human-created links are events; read-only joined view by any id (R2) | No guessing; auditable; no legacy change | Link coverage limited by source data quality | High fit |
| C. Fuzzy/similarity matching or entity-resolution model | Match by text similarity | Higher link rate | Violates FR-ID-02; wrong links in a GxP context; ML-ish | Rejected |

### Decision / recommendation
Recommend B. Cross-object contradiction findings (FR-ID-03, R2) are read-only findings driven by policy rules.

### Consequences
- Positive: lookup by any identifier returns same linked set.
- Negative: low match rate on current synthetic data is expected and reported, not hidden.

### Trigger to decide / revisit
Decide at Stage 11.

## Evidence References
docs/09-initial-prd/functional-requirements.md FR-ID-*; app/store.py

## Assumptions
A-10-10 Exact-key matching suffices for R1.

## Unknowns
U-10-14 Real key quality.

## Unresolved Issues
None.

## Residual Risks
Orphans accumulate with no owner.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

