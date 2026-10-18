---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-013-authn-authz.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "app/server.py", "docs/07-repo-assessment/security-code-quality-findings.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-013 — Authentication and role-based authorisation. Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B). Production IdP integration Unknown.

### Traceability
FR-SEC-01, FR-GATE-03, FR-GATE-04, FR-SEC-03; PNFR-07, PNFR-08, PNFR-12; R-11 (not met); HAR-05, HAR-15.

### Context
[Verified Fact] No authentication, authorisation or TLS exist; server binds locally (SC-01/02/06; R-11 Not met). [Verified Fact] No identity provider or real environment exists (OD-04). [Verified Fact] Personas PER-01..08 are documentary (A-09-06).

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Reverse proxy / network trust only | Rely on perimeter | No code | Not enforceable here; no perimeter exists | Insufficient |
| B. App-level authn behind an interface + RBAC - RECOMMENDED | `Authenticator` interface; initial implementation local users with salted PBKDF2 (hashlib), session tokens, lockout; roles reviewer, quality lead, compliance, finance(read), integration, authorised dispositioner; deny by default; service actors flagged non-human; every authz failure audited; secrets via env, secret scan gate. TLS required for any non-loopback binding (HAR-05) | Works with no external service; swap-in point for OIDC/SAML | Local credential store is weak vs enterprise SSO | Fit High; lock-in none |
| C. OIDC/SAML against corporate IdP (e.g., Entra ID) | Enterprise SSO | Best practice | No IdP exists to integrate; vendor choice without evidence | Deferred behind interface (trigger: real deployment) |

### Decision / recommendation
Recommend B now, C when a real environment and IdP exist. Mapping of identity to the authorised-dispositioner role is configuration (empty default).

### Consequences
- Positive: PNFR-07 testable (unauthenticated -> refusal).
- Negative: credential lifecycle in-app until SSO.

### Trigger to decide / revisit
Revisit at Stage 23-25 / on any HAR-05/HAR-15 approval.

## Evidence References
app/server.py; docs/07-repo-assessment/security-code-quality-findings.md

## Assumptions
A-10-14 Loopback single-host use for R1.

## Unknowns
U-10-18 Corporate IdP.

## Unresolved Issues
HAR-05.

## Residual Risks
Password handling flaws; mitigated by threat model (Stage 24).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

