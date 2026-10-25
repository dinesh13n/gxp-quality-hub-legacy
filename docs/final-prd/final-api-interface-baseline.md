---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "final-api-interface-baseline.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/12-specs/contracts/openapi.yaml", "docs/21-integration/integration-inventory.md", "docs/21-integration/api-contracts.md", "docs/17-implementation-prd/implementation-prd.md", "docs/27-hardening/hardening-plan.md", "hub/security/route_registry.json", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
The hub provides a loopback-only HTTP API (48 operations) and CLI, consumes ten read-only inputs and publishes to nothing. No external consumer or real system exists. Stage 27 error/behaviour changes lack a spec addendum.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### API-1 Provided surfaces [Verified Fact]
| Surface | Built form | State | Evidence |
|---|---|---|---|
| HTTP API | `/api/v2` + server-rendered pages; **48 operations** (`operationId` count in `docs/12-specs/contracts/openapi.yaml`; deny-by-default route registry `hub/security/route_registry.json`); stdlib `ThreadingHTTPServer`; **loopback only**, no TLS | Built, shadow, no consumer | implementation-prd IP-4; integration-inventory INT-11 |
| Two HTTP entry points | R1 `python -m hub.web serve` (R2 operations answer 501) and R2 `python -m hub.r2 serve` (R2 operations only); choose one before exposure | Open (PCH-21, S16-D05) | prd-change-log |
| CLI | `python -m hub` (no-ai-check, golden-compare, guards); `hub.admin`, `hub.policy`, `hub.decision`, `hub.intake`, `hub.runs`, `hub.metrics`, `hub.web`, `hub.search`, `hub.r2`, `hub.release` (evaluate) | Built; error shape per `docs/20-application/spec-addendum-cli-error-shape.md` (DQ-05, OD-26) | IP-4 |
| Logs | JSON lines on stderr, results on stdout; 4 of 21 declared log events emitted | Partial | observability-validation; DEV-70 |
| Outbound | **None.** The hub publishes to no external system (no event bus, webhook, file drop) | Verified | integration-inventory |

### API-2 Inbound integrations (all read-only) [Verified Fact]
INT-01..INT-10: legacy case DB, enterprise DB, partner feed (8,567 rows), source messages (15), gateway inbox (1), gateway client (loopback stub `services/source_gateway/server.py`, GET only), vendor CSV (2,400 rows), policy-source transcription, documents, captured goldens. Contracts: `docs/21-integration/{api-contracts,data-contracts,event-contracts,failure-semantics}.md`. [Verified Fact] Source-contract binding is `record_only` everywhere (OD-28); the contract fails 3 of 4 sources, so `enforce` is unusable on the shipped data. [Unknown] Real enterprise systems, endpoints, credentials, SLAs: none exist (OD-28 (a)); the outside consumers of the 13 legacy outputs are Unknown.

### API-3 Error and exit-code baseline [Verified Fact: implementation-prd IC-1/IC-2, plus Stage 27]
- Exit codes 0-32 allocated by package (IC-1); **clashes at 2 and 9 are documented and kept** (DQ-04, OD-29). Exit 17 = audit tamper detected, now also malformed anchor line (S30-DEV-01; acceptance OPEN, HO-12).
- Codes beyond the 82-code registry (IC-2) are recorded in the implementation-contract addendum IC-1..IC-8 (Stage 12 files are not edited; Stage 12 v0.2 content under `docs/23-human-control/stage12-v0.2`).
- Stage 27 added or changed behaviours that have **no spec addendum** (D-27-05): 401 for an anonymous unknown action, 400 for a lone surrogate, `E-CFG-INVALID` for unknown/mistyped config keys, 408 read timeout (`E-REQ-TIMEOUT`), 429 after 100 refusals in 60 s (`E-REQ-RATE-LIMITED`), 503 store fault (`E-STORE-UNAVAILABLE`), restricted-evidence note placeholder for reviewer/finance/integration roles. [Assumption] These are agent defaults (A-27-02, A-27-04, A-27-05), not approved.

### API-4 Token and session formats [Verified Fact: IC-5]
Session cookie `hub_session` (HttpOnly, SameSite=Strict, no `Secure` over loopback HTTP); service token prefix `svc_` (role integration, never Zone H, SHA-256 stored, optional expiry); CSRF header `X-Hub-Request: 1` for JSON writes; login POST has no CSRF (accepted gap, DQ-S24, assumption); re-auth window 300 s.

### API-5 Contract status
[Verified Fact] OpenAPI and JSON schemas are Stage 12 baselines plus the addendum. [Verified Fact] Contract approval HAR-13 (IC-1..IC-8 as Stage 12 v0.2 content) was approved in OD-25 (DQ-03). [Unknown] Whether Stage 12 v0.2 text was finalised for later additions (Stage 20-31 surfaces): D-27-05 says none written for the Stage 27 additions.

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-06 [Assumption] The route count 48 is current (Stage 17/21 figure; `operationId` count of openapi.yaml was 48 at main 08add05 as grepped).

## Unknowns
- U-43-05 Real consumers and their expectations (OD-28).

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
