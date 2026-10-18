---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-015-deployment-topology.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "Dockerfile", "compose.yaml", "environments/", "docs/07-repo-assessment/dependency-map.md DM-05, DM-06", "docs/operations-service-levels.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-015 — Deployment topology: single-host, loopback-bound process with file-based store; containerisation and cloud deferred. Status: PROPOSED (recommended option A for R1).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option A for R1). Any non-loopback or container run needs HAR-05; cloud choice has no evidence.

### Traceability
PNFR-01, PNFR-02, PNFR-05, PNFR-08, PNFR-19; FR-CO-03; RC-5; HAR-05, HAR-07, HAR-08; 0C S1 (infra USD 20/40/100 per month, Assumed).

### Context
[Verified Fact] No real production environment exists; only local/sandbox runs (OD-04; ENV tiers). [Verified Fact] A `Dockerfile` (python:3.12-slim) and `compose.yaml` exist but were never executed (DM-05, U-09); CI never run (DM-06). [Verified Fact] Python 3.10 sandbox, CI/Docker 3.12; 3.10 EOL Oct 2026 [Inference from public schedule]. [Assumption] Availability 99.5%, RTO 8 h, RPO 24 h are archived working targets.

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Single host, loopback-bound process + CLI jobs, file store - RECOMMENDED for R1 | App process on 127.0.0.1, SQLite file(s) in a data dir, nightly file copy + checksum manifest (as done for `_data-backup-2026-10-17/SHA256SUMS.txt`), restore rehearsal; Python 3.12 baseline, tested on 3.10 | No infra, no egress, within 0C S1 cost, rollback = redeploy previous tag + restore | Not highly available; RTO depends on manual restore; multi-user access only via the host | Fit High for 125 cases; resilience medium; lock-in none |
| B. Containers via Compose on a VM | Reuse `Dockerfile`/`compose.yaml` after hardening | Reproducible runtime; env parity | HAR-05/07; never executed; secrets/TLS design needed | Adopt at Stage 25 if multi-user hosting approved |
| C. Managed cloud PaaS / Kubernetes | Azure/AWS app + managed DB | HA, backups, SSO integration | Vendor lock-in decision with no evidence; cost above S1; no environment; HAR-09 | Not justified now |

### Decision / recommendation
Recommend A for R1 and design everything 12-factor style (env config, no repo-relative writes, stdout logging) so B/C remain open. Environment tiers: dev/staging/production-like profiles exist as `environments/*.env.example` (templates only).

### Consequences
- Positive: no cloud commitment; low cost.
- Negative: PNFR-01 99.5% unproven and likely unattainable without HA; stated honestly.
- All data paths configurable (fixes DM-10..12 coupling for new code).

### Trigger to decide / revisit
Revisit at Stage 25 (deployment) or on approval of multi-user/non-loopback hosting (HAR-05).

## Evidence References
Dockerfile; compose.yaml; environments/; docs/07-repo-assessment/dependency-map.md DM-05, DM-06; docs/operations-service-levels.md

## Assumptions
A-10-16 R1 is a pilot on one host.

## Unknowns
U-10-20 Target hosting; U-10-21 who operates it.

## Unresolved Issues
HAR-05, HAR-07.

## Residual Risks
Single point of failure; manual backup discipline.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

