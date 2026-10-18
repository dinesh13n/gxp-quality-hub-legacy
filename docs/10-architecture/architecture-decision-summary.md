---
stage: "10 — Target Architecture + ADRs"
artifact: "architecture-decision-summary.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

Index of 18 ADRs, all PROPOSED; open-item dependency table.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DS-1 Index
| ADR | Decision | Status | Root causes |
|---|---|---|---|
| [ADR-001](adrs/ADR-001-architecture-style.md) | Overall architecture style: modular monolith built beside the legacy estate | PROPOSED (recommended option B) | RC-1..RC-8 (all) |
| [ADR-002](adrs/ADR-002-no-ai-boundary-enforcement.md) | Enforcing the No-AI decision (OD-08) in the architecture | PROPOSED (mechanism); underlying No-AI decision approved by Dinesh in OD-08 | RC-1, RC-6 |
| [ADR-003](adrs/ADR-003-legacy-coexistence-pattern.md) | Coexistence pattern with the legacy estate (read-only adapters, shadow comparison, no dual-write) | PROPOSED (recommended option B) | RC-4, RC-6, RC-8 |
| [ADR-004](adrs/ADR-004-data-store-and-event-model.md) | Data store and decision-record model (append-only events in SQLite) | PROPOSED (recommended option B) | RC-1, RC-2, RC-6 |
| [ADR-005](adrs/ADR-005-audit-trail-tamper-evidence.md) | Tamper-evident audit trail (hash chain in application layer) | PROPOSED (recommended option B) | RC-1, RC-2 |
| [ADR-006](adrs/ADR-006-disposition-gate-recording-modes.md) | Human disposition gate (Zone H) with two configurable recording modes | PROPOSED - depends on open OPD-05 (where disposition is recorded), OPD-06 (role holders) | RC-1 |
| [ADR-007](adrs/ADR-007-policy-and-rule-service.md) | Versioned policy objects and one table-driven rule service (no adopted defaults) | PROPOSED (recommended option B) | RC-3, RC-4 |
| [ADR-008](adrs/ADR-008-intake-pipeline.md) | Intake pipeline: append-only raw store, content-hash idempotency, quarantine | PROPOSED (recommended option B) | RC-5, RC-6, RC-7 |
| [ADR-009](adrs/ADR-009-identity-crosswalk.md) | Shared identity via explicit crosswalk table (no inference of links) | PROPOSED (recommended option B) | RC-7 |
| [ADR-010](adrs/ADR-010-run-orchestration-scheduling.md) | Run orchestration and scheduling (idempotent CLI jobs + run records; schedule held pending OPD-11) | PROPOSED - depends on open OPD-11 (is a deterministic scheduler an "automated action" unde | RC-5 |
| [ADR-011](adrs/ADR-011-metrics-and-definition-tags.md) | Metrics module: one query path, definition tags, exact decimals | PROPOSED (recommended option B) | RC-3, RC-8 |
| [ADR-012](adrs/ADR-012-reviewer-search.md) | Reviewer retrieval: SQLite FTS5 keyword/field search (R2) - no semantic search | PROPOSED (recommended option B, R2 scope) | RC-1 |
| [ADR-013](adrs/ADR-013-authn-authz.md) | Authentication and role-based authorisation | PROPOSED (recommended option B) |  |
| [ADR-014](adrs/ADR-014-api-and-ui-surface.md) | Service surface: layered HTTP API + minimal server-rendered pages on the standard library | PROPOSED (recommended option B) | RC-1 |
| [ADR-015](adrs/ADR-015-deployment-topology.md) | Deployment topology: single-host, loopback-bound process with file-based store; containerisation and cloud deferred | PROPOSED (recommended option A for R1) | RC-5 |
| [ADR-016](adrs/ADR-016-observability.md) | Observability: structured logs + run records + metrics tables (stdlib) | PROPOSED (recommended option B) | RC-5 |
| [ADR-017](adrs/ADR-017-buy-vs-build.md) | Buy versus build (commercial QMS) - NOT EVALUATED | PROPOSED / OPEN - OPD-10 is unanswered |  |
| [ADR-018](adrs/ADR-018-runtime-stack.md) | Runtime and language stack: Python 3.12 stdlib for new code; legacy Java/JS/SQL retained as read-only comparators | PROPOSED (recommended option B) | RC-4, RC-8 |

### DS-2 Status counts and rule
All ADRs are PROPOSED/DRAFT. None is ACCEPTED: only Engagement lead (Dinesh Naik) can accept (HAR-11). ADR-002 rests on an already-approved decision (OD-08) but its enforcement mechanism is PROPOSED.

### DS-3 Decisions blocked or shaped by open items
| ADR | Open item | Treatment |
|---|---|---|
| 006 | OPD-05, OPD-06 | both modes, default blocked |
| 007 | OPD-01..04, OPD-07 | no adopted defaults |
| 010 | OPD-11 | schedule disabled |
| 017 | OPD-10 | no selection |
| 004/015 | OPD-09, OPD-14 | hold-all; measure only |
| all | OPD-13 | PRD approval pending |

### DS-4 Coverage
Every one of RC-1..RC-8 is covered by at least one ADR; all 10 CAP groups map to components; the ADR list covers application, API, data, integration, security, identity, observability, human control, deployment, and AI (No-AI).

## Evidence References
adrs/ADR-001..018.

## Assumptions
See ADRs.

## Unknowns
See ADRs.

## Unresolved Issues
OPD-05, OPD-10, OPD-11, OPD-13.

## Residual Risks
Decision drift if ADRs are not maintained.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

