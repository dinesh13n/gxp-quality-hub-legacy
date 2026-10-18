---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-014-api-and-ui-surface.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "app/server.py"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-014 — Service surface: layered HTTP API + minimal server-rendered pages on the standard library. Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B). UI scope is Unknown.

### Traceability
FR-REV-02, FR-GATE-02, FR-DEC-04, FR-SEC-01; PNFR-06, PNFR-08, PNFR-15; RC-1; OPD-14.

### Context
[Verified Fact] `app/server.py` is a GET-only `BaseHTTPRequestHandler` mixing routing, SQL and formatting (god handler). [Verified Fact] No frontend exists. [Unknown] Who the users are in practice and which screens are needed (Stage 12 specs); latency target (OPD-14).

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Keep extending `app/server.py` | Add POST routes there | Familiar | Untested god handler (High risk); couples to `store` import-time DB | Poor |
| B. New thin HTTP layer (stdlib) over service interfaces - RECOMMENDED | Router + authn/authz middleware + JSON API; server-rendered HTML for queue, evidence pack, policy views; handlers hold no business logic; CSRF token on state-changing forms; output escaping for all untrusted text | No dependency; swap-able | Hand-rolled router needs care; stdlib server is low-throughput | Fit ok at 125 cases |
| C. Web framework + SPA (e.g., FastAPI + React) | Mainstream stack | Productivity, ecosystem | HAR-08; adds JS build chain; no scale/UX evidence; Dinesh prefers Python/FastAPI per profile but evidence does not require it | Defer; adopt if throughput/UX need is measured |

### Decision / recommendation
Recommend B, with service-layer interfaces so C is a replaceable shell. This is an evidence-based minimalism choice, not a preference against C.

### Consequences
- Positive: security review surface small.
- Negative: more boilerplate.

### Trigger to decide / revisit
Revisit at Stage 12/14 once UI needs and HAR-08 stance are known.

## Evidence References
app/server.py

## Assumptions
A-10-15 Few concurrent users.

## Unknowns
U-10-19 UI needs and latency target.

## Unresolved Issues
OPD-14.

## Residual Risks
Hand-rolled HTTP security gaps; mitigated by threat model and tests.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

