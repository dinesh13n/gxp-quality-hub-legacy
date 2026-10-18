---
stage: "10 — Target Architecture + ADRs"
artifact: "model-service-scorecard.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

N/A: no AI model or AI service is in scope. The product is No-AI by decision OD-08 (approved by Dinesh Naik, 2026-10-18). This note records the non-AI service comparisons that stand in for a scorecard and the conditions under which a scorecard would be needed.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### MS-1 Status
- [Verified Fact] OD-08: no model calls, no agents. Stage 19 not applicable, Stage 22 not triggered. Model/token/context/loop budgets (0C S3/S4) are retired as active assumptions (`economics-baseline-reconciliation.md`).
- [Verified Fact] Architecture contains zero Zone A components (target-architecture TA-2).

### MS-2 Non-AI service comparison (stand-in)
| Service need | Chosen (PROPOSED) | Alternatives rejected/deferred | ADR |
|---|---|---|---|
| Search | SQLite FTS5 (R2) | Elasticsearch; vector search (violates OD-08) | 012 |
| Rules | Table-driven in-process | Rules engine product | 007 |
| Scheduling | CLI + external trigger | Workflow engine | 010 |
| Datastore | SQLite | PostgreSQL; ledger DB | 004 |
| Authn | local + interface | OIDC/SAML | 013 |
| Telemetry | stdlib logs | OTel/APM | 016 |

### MS-3 Conditions that would require a real scorecard
RQ-1..RQ-3 triggers met on a real corpus AND a new Dinesh decision AND Stage 8 re-qualification (BR-AI-1, BR-AI-6). Then candidate dimensions: quality on labelled set, injection robustness, latency p95, cost per case, data egress/HAR-09, lock-in, deterministic fallback (BR-AI-5).

### MS-4 Tripwire
Stage 32 asserts 0 model calls and 0 model-inference egress (PNFR-18).

## Evidence References
.fde/orchestrator-decisions.md OD-08; docs/08-ai-qualification/*.

## Assumptions
None new.

## Unknowns
U-S01 whether any user needs document Q&A.

## Unresolved Issues
None.

## Residual Risks
Future pressure to add AI bypassing re-qualification.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

