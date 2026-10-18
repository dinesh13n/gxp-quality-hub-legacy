---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-018-runtime-stack.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "pyproject.toml", "docs/07-repo-assessment/dependency-map.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-018 — Runtime and language stack: Python 3.12 stdlib for new code; legacy Java/JS/SQL retained as read-only comparators. Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B).

### Traceability
PNFR-17, PNFR-18, PNFR-19, FR-CO-01, FR-POL-04; RC-4, RC-8; HAR-07, HAR-08.

### Context
[Verified Fact] pyproject `>=3.10`; CI/Docker 3.12; sandbox 3.10.12; JDK 11 source-launcher and Node 22 work; none of Java/Node are in CI/Docker (DM-01, 03, 04). [Verified Fact] Java reads CSV by positional index (DM-17); JS reads policy JSON by cwd (DM-13). [Verified Fact] No third-party libraries (DM-08).

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Keep polyglot, extend all three | Evolve Java/JS/Python logic | No porting | Perpetuates RC-4; no CI for Java/JS | Poor |
| B. Python 3.12 for all new code; Java/JS/SQL frozen as characterised comparators - RECOMMENDED | Rule logic re-expressed as data (ADR-007), not ported line-by-line; legacy kept runnable in sandbox for golden comparison; upgrade path 3.10 -> 3.12 verified by CT-H5 | One language, matches estate majority; no dependencies | Legacy Java/JS never "fixed"; need JDK/Node in test tier E2 | High |
| C. Rewrite in another stack (Java/.NET/Go) | Greenfield | Possible org alignment | No evidence of need; rewrite risk; skills Unknown | Not justified |

### Decision / recommendation
Recommend B. Third-party packages only via HAR-08 with recorded justification.

### Consequences
- Positive: small supply-chain surface (none).
- Negative: stdlib-only limits some convenience.

### Trigger to decide / revisit
Stage 14 confirms along with tooling (R-8, R-9).

## Evidence References
pyproject.toml; docs/07-repo-assessment/dependency-map.md

## Assumptions
A-10-19 Python 3.12 available on target host.

## Unknowns
U-10-25 Org-standard stack.

## Unresolved Issues
HAR-07/08.

## Residual Risks
Python 3.10 EOL (Oct 2026) if 3.12 move slips.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

