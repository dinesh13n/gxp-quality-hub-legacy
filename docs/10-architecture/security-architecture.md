---
stage: "10 — Target Architecture + ADRs"
artifact: "security-architecture.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/07-repo-assessment/security-code-quality-findings.md", "docs/00-preflight/operating-contract/data-use-constraints.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

Security is designed in: deny-by-default authn/RBAC, tamper-evident audit, human-only Zone H, untrusted-content handling, no egress, no secrets in source. Full threat model is Stage 24.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SA-1 Controls
| Control | Design | PNFR / FR | ADR |
|---|---|---|---|
| Authentication | Authenticator interface; local PBKDF2 first; lockout; SSO later | PNFR-07, FR-SEC-01 | 013 |
| Authorisation | Role matrix; deny by default; service actors tagged non-human | FR-GATE-03 | 006, 013 |
| Zone H protection | Authorised-holder list empty by default; mode none by default | FR-GATE-04 | 006 |
| Audit | Hash-chained, anchored; logs authz failures and policy changes | PNFR-09, FR-SEC-02 | 005 |
| Untrusted content | Typed wrapper; escaping on output; injection fixture gate (86 feed rows, 22 documents, 44 hits) | PNFR-13, FR-INT-07 | 002, 008 |
| Transport | Loopback; TLS before any exposure | PNFR-08 | 015 |
| Secrets | env; secret scan 0 findings | PNFR-08 | 015 |
| SSRF / scheme | Gateway URL allow-list http/https loopback (legacy `urlopen` accepts file:/ftp: - DM-15) | PNFR-08 | integration |
| SQL | Parameterised queries; identifier allow-list (legacy interpolates names - DM-16) | - | 008, 009 |
| CSRF/XSS | tokens on forms; escape all untrusted text | - | 014 |
| Data protection | Field classes per data-use-constraints; access levels (R2) | PNFR-12 | - |
| Retention | Hold-all, no delete code path | PNFR-10 | 004 |
| Supply chain | stdlib only; deny-list; HAR-08 for additions | PNFR-18 | 002, 018 |

### SA-2 Identity model [Assumption]
Roles derived from documentary personas PER-01..08 (A-09-06): reviewer, quality lead, compliance, finance (read), integration (non-human), authorised dispositioner (human only, configured).

### SA-3 Known weaknesses carried
[Verified Fact] Shipped system fails R-11 (no auth/TLS/audit). The hub must not be exposed beyond loopback until Stage 23-25 close this. Local credential store is a stopgap.

## Evidence References
docs/07-repo-assessment/security-code-quality-findings.md; app/gateway_bridge.py; nfrs.md.

## Assumptions
Synthetic data only (STOP-04 not triggered).

## Unknowns
Threat model (Stage 24); real IdP.

## Unresolved Issues
HAR-05.

## Residual Risks
Hand-rolled HTTP/auth code is itself a risk.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

