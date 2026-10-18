---
stage: "10 — Target Architecture + ADRs"
artifact: "deployment-architecture.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "Dockerfile", "compose.yaml", "environments/"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

R1 topology: one host, process bound to 127.0.0.1, SQLite files, CLI jobs, file-based backups with checksum manifest. Containers and cloud deferred (ADR-015).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DA-1 Topology (R1)
| Element | Choice | Constraint |
|---|---|---|
| Runtime | Python 3.12 (tested on 3.10) | HAR-07 for Docker/CI/pyproject edits |
| Process | `hub serve` on 127.0.0.1 | non-loopback requires HAR-05 + TLS |
| Store | `hub.sqlite3` WAL + audit anchor file outside the DB dir | path via env, never repo-relative |
| Jobs | `hub run <job>` | schedule disabled until OPD-11 |
| Config | env vars + config file; secrets never in repo | secret scan gate |
| Legacy | read-only mount of legacy data | working-tree `data/` never written (OD-03a) |

### DA-2 Environments
[Verified Fact] `environments/{dev,staging,production-like}.env.example` are templates; no real environment exists. Test tier uses a full repo copy outside the working tree with hash-verified baseline 125/4100 (CT-H1).

### DA-3 Release, rollback, recovery
Release gate: golden diff empty except approved deviations, replay-safety check (FR-INT-02), mutation gate, tamper test, zero-model-call check. Rollback: redeploy previous tag, restore DB from verified backup, audit chain verify. Backup: copy + `sha256sum -c` manifest (pattern used for `_data-backup-2026-10-17`). RTO 8 h / RPO 24 h are Assumptions; a restore rehearsal is an R1 deliverable (PNFR-05).

### DA-4 Deferred
Compose/container (Stage 25 + HAR-05/07), HA, SSO, cloud. No vendor chosen.

## Evidence References
Dockerfile; compose.yaml; environments/*.env.example; docs/operations-service-levels.md.

## Assumptions
Single host acceptable for R1.

## Unknowns
Hosting target and operator.

## Unresolved Issues
HAR-05, HAR-07.

## Residual Risks
No HA; availability target not demonstrable.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

