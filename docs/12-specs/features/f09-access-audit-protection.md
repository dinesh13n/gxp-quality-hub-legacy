---
stage: "12 — Spec-Driven Design"
artifact: "features/f09-access-audit-protection.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/security-architecture.md", "docs/10-architecture/adrs/ADR-013-authn-authz.md", "docs/10-architecture/adrs/ADR-005-audit-trail-tamper-evidence.md", "docs/11-data-context/metadata-model.md", "docs/07-repo-assessment/security-code-quality-findings.md", "docs/00-preflight/operating-contract/data-use-constraints.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Feature spec for authentication, RBAC, hash-chained tamper-evident audit and field-class protection (CAP-09): 11 behaviours, 21 acceptance criteria for FR-SEC-01..03 and PNFR-07/08/09/10/12. Stopgap local authenticator behind an interface; audit anchor residual risk stated.

## Findings
### F09-1 Scope and traceability [Verified Fact: gaps; Inference: design]
Feature **F09 Access Control, Audit & Data Protection** = CAP-09, component C2 (+ C1 middleware), ADR-013 (Authenticator interface + RBAC, local PBKDF2 first), ADR-005 (hash-chained audit with out-of-DB anchor), ADR-014 (CSRF, escaping), `docs/11-data-context/metadata-model.md` M1-M6, `docs/10-architecture/security-architecture.md` SA-1..SA-3.

| Implements | FR-SEC-01, FR-SEC-02 (R1); FR-SEC-03 (R2) |
|---|---|
| Also constrained by | FR-GATE-03, FR-DEC-01, FR-POL-03, PNFR-07, PNFR-08, PNFR-09, PNFR-12, PNFR-10; BR-08; DQ-15; RC-1; A-09-06 |
| Open decisions | OD-S12-06 (role holders, user administration), OD-S12-18 (audit anchor location), OD-S12-09 (retention) |
| Legacy evidence | shipped API is unauthenticated GET-only on 127.0.0.1; no TLS, no logging, no audit trail (R-11 Not met, security-code-quality-findings.md); `access_audit` (4,167 rows, 220 with empty `access_reason`) is enterprise data, not a product audit |

### F09-2 Behaviours
| ID | Behaviour (binding once approved) | Implements |
|---|---|---|
| BEH-SEC-01 | **Authenticate everything.** Every route except `GET /healthz` (liveness only, no data) and `POST /auth/login` requires authentication; unauthenticated requests get 401 `E-AUTH-UNAUTHENTICATED`. A route registry test enumerates all registered routes and fails if any route lacks a declared permission (deny by default). | FR-SEC-01, PNFR-07 |
| BEH-SEC-02 | **Local authenticator (stopgap, behind the `Authenticator` interface).** Users stored with salted PBKDF2-HMAC-SHA256 (`hashlib.pbkdf2_hmac`, per-user 16-byte salt, iterations configurable, proposed >= 600,000), constant-time comparison (`hmac.compare_digest`), password length >= 12. Sessions: 256-bit random token (`secrets`), only its SHA-256 stored server-side; idle expiry 30 min, absolute 8 h (proposals); cookie `HttpOnly; SameSite=Strict` (+`Secure` under TLS). Lockout: 5 failed logins per user in 15 min lock the account 15 min; failure responses are generic. No default or bootstrap account; users are created offline by the host operator with `hub user create` (no web bootstrap). | FR-SEC-01, PNFR-07 |
| BEH-SEC-03 | **Service identities.** Service accounts (`principal_kind = service`, recorded as `actor_kind = system` in decision events and `service` in the audit log) authenticate with bearer tokens (stored hashed, rotatable), cannot start interactive sessions, and are rejected for every Zone H action and human-link action (F02, F05). Scheduler/importer runs use a service identity. | FR-GATE-03, FR-SEC-01 |
| BEH-SEC-04 | **Roles and permissions.** Roles: reviewer, quality_lead, compliance, finance_read, integration, dispositioner. The permission matrix (security-spec.md SEC-MATRIX) is data; a request needs an explicit permission for its operation, otherwise 403 `E-AUTH-FORBIDDEN`. finance_read is read-only with masked identifiers; integration is non-human and limited to intake/run operations; `dispositioner` alone does not grant Zone H (the holder list also must contain the principal). | FR-SEC-01 |
| BEH-SEC-05 | **Audit chain.** Every decision event, policy/rule change, Zone H attempt (accepted or rejected), authorisation failure, login success/failure, lockout, configuration load, export, read of C3 data, audit verification and schedule change appends an `audit_log` record (SCH-AUDIT): `audit_seq`, `occurred_at`, `actor`, `actor_kind`, `action`, `object_ref`, `outcome` in {success, denied, error}, `reason` (non-empty for C3 reads and exports), `correlation_id`, `details` (canonical JSON), `prev_hash`, `hash = sha256(prev_hash ‖ canonical(record))`. Canonical form: JSON with sorted keys, `separators=(",", ":")`, `ensure_ascii=true`, UTC timestamps `YYYY-MM-DDTHH:MM:SS.ffffffZ`. The audit write is in the same transaction as the change it records; failure aborts the change. Audit rows are insert-only (trigger). | FR-SEC-02, PNFR-09 |
| BEH-SEC-06 | **Anchor and verify.** The head `{audit_seq, hash, occurred_at}` is appended to an anchor file at `audit.anchor_path` (outside the database directory) every `audit.anchor_every` records (proposed 100) and at the end of every run; `hub verify-audit` recomputes the chain from the first record, checks each anchored head against the chain, and reports `ok` or the first broken `audit_seq` with the failure kind (altered record, missing record, reordered, head mismatch). Verification is a release gate (CO-03). Truncation of records after the last anchor is not detectable (documented residual risk). | FR-SEC-02, PNFR-09 |
| BEH-SEC-07 | **No secrets in the repository or logs.** Secrets only via environment; a secret-scan gate has 0 findings; logs and audit `details` never contain passwords, tokens or hashes of credentials. | PNFR-08 |
| BEH-SEC-08 | **Transport.** Default bind is 127.0.0.1. A non-loopback bind requires `network.exposure_approved = true` (HAR-05 evidence reference in config) and TLS settings; otherwise start-up is refused (E-SEC-EXPOSURE-NOT-APPROVED). No outbound network calls except the loopback gateway reader (component rule 7). | PNFR-08 |
| BEH-SEC-09 | **Web protections.** State-changing HTML forms carry a per-session CSRF token (E-SEC-CSRF); JSON writes require a custom header `X-Hub-Request: 1` plus SameSite cookie or bearer token; all output is HTML-escaped; `Content-Security-Policy: default-src 'self'` and `X-Content-Type-Options: nosniff` are set; request body limit (default 1 MiB) and `414/413` handling as in legacy (page size clamps). | PNFR-07, PNFR-13 |
| BEH-SEC-10 | **(R2) Data protection by field class.** Classes C1-C3 and the per-field handling of metadata-model M3 are enforced: finance_read sees `account_id` masked; `restricted` documents and legal-hold data need a named role; missing `access_level`/`classification` = `restricted`; every C3 read and export writes an audit record with a non-empty `reason` (E-SEC-REASON-REQUIRED). Tenant filters are mandatory in queries. | FR-SEC-03, PNFR-12 |
| BEH-SEC-11 | **Retention hold.** No code path deletes cases, events, evidence, audit rows or intake rows (PNFR-10, OD-S12-09); a test greps for `DELETE FROM` against those tables and verifies triggers. | PNFR-10 |

### F09-3 Error cases
E-AUTH-UNAUTHENTICATED, E-AUTH-FORBIDDEN, E-AUTH-LOCKED, E-AUTH-BAD-CREDENTIALS, E-AUTH-SESSION-EXPIRED, E-SEC-CSRF, E-SEC-EXPOSURE-NOT-APPROVED, E-SEC-REASON-REQUIRED, E-SEC-AUDIT-WRITE-FAILED, E-SEC-AUDIT-TAMPER-DETECTED (error-handling-spec.md).

### F09-4 Acceptance criteria
| ID | Given | When | Then | Implements | Kind |
|---|---|---|---|---|---|
| AC-SEC-01 | every registered route (enumerated by test) | called without credentials | 401 for all except `/healthz` and `/auth/login`; `/healthz` returns no case data | FR-SEC-01, PNFR-07 | negative |
| AC-SEC-02 | a route registered without a permission declaration | the route-registry test runs | the test fails (deny by default) | FR-SEC-01 | negative |
| AC-SEC-03 | roles reviewer, finance_read, integration | each calls an operation outside its matrix row | 403 E-AUTH-FORBIDDEN and an audit record with outcome denied | FR-SEC-01, FR-SEC-02 | negative |
| AC-SEC-04 | a fresh install | the user table is read | zero users exist; no default credentials; login with any password fails | FR-SEC-01 | negative |
| AC-SEC-05 | a user with 5 consecutive bad logins | a 6th login with the correct password is tried within 15 min | E-AUTH-LOCKED; after 15 min login succeeds | FR-SEC-01 | edge |
| AC-SEC-06 | the credential store | inspected | password hashes are PBKDF2 with per-user salt; session tokens are stored only as SHA-256; no plaintext secret anywhere | PNFR-07, PNFR-08 | negative |
| AC-SEC-07 | an idle session beyond 30 min or older than 8 h | used | 401 E-AUTH-SESSION-EXPIRED | FR-SEC-01 | edge |
| AC-SEC-08 | a service token | used on interactive login or a Zone H / human-link route | login refused; Zone H and human-link refused and audited | FR-GATE-03, FR-SEC-01 | negative |
| AC-SEC-09 | a decision event, a policy change, a Zone H attempt, an authz failure, a login failure | each is performed | one audit record per action with the BEH-SEC-05 fields, chain linked | FR-SEC-02 | positive |
| AC-SEC-10 | a chain of 1,000 audit records and an anchor | `verify-audit` runs | `ok` | FR-SEC-02, PNFR-09 | positive |
| AC-SEC-11 | the same chain with (a) one record's `details` edited, (b) one record deleted, (c) two records swapped, (d) the last 50 records deleted after an anchor at seq 1,000 | `verify-audit` runs for each | (a)-(c) report the first broken seq and kind; (d) reports head mismatch against the anchor | FR-SEC-02, PNFR-09 | negative |
| AC-SEC-12 | records deleted after the last anchor | `verify-audit` runs | not detected - the test documents the limitation (residual risk R-SEC-1) | FR-SEC-02 | edge |
| AC-SEC-13 | the audit table | UPDATE/DELETE attempted | rejected by trigger | FR-SEC-02 | negative |
| AC-SEC-14 | the audit write forced to fail | any change is attempted | change rolled back, E-SEC-AUDIT-WRITE-FAILED | FR-SEC-02, BEH-DEC-11 | negative |
| AC-SEC-15 | a login failure followed by the audit read | the record is inspected | no password or token appears in `details` or logs | PNFR-08 | negative |
| AC-SEC-16 | start-up with `bind = 0.0.0.0` and no exposure approval | the server starts | refused E-SEC-EXPOSURE-NOT-APPROVED; with approval but no TLS settings also refused | PNFR-08 | negative |
| AC-SEC-17 | a state-changing form post without CSRF token / a JSON write without the custom header | posted | E-SEC-CSRF, no change | PNFR-07 | negative |
| AC-SEC-18 | the code base | secret scan and deletion-path grep run | 0 secret findings; no DELETE statements on retained tables | PNFR-08, PNFR-10 | negative |
| AC-SEC-19 | R2: one fixture record per field class and each role | read through the API | handling matches metadata-model M3/M4 (finance masked account_id, restricted denied, missing access_level treated restricted); 100% of field classes covered | FR-SEC-03, PNFR-12 | positive |
| AC-SEC-20 | R2: a C3 read or export without reason | requested | E-SEC-REASON-REQUIRED; with reason it succeeds and the reason is audited (non-empty) | FR-SEC-03 | negative |
| AC-SEC-21 | holder list changed and process restarted | audit chain read | CONFIG_LOADED record with config hash (also AC-GATE-22) | FR-SEC-02 | positive |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-F09-1 PBKDF2 iterations (>= 600,000), lockout (5/15/15), session timeouts (30 min idle, 8 h absolute), password length 12, CSP and body limit are spec proposals; no organisational policy exists. Confirm in Stage 24.
- A-12-F09-2 Role set derived from documentary personas (A-09-06).

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-F09-1 Identity provider / SSO (none exists).
- U-12-F09-2 Audit anchor location for any real deployment (ADR-005).
- U-12-F09-3 Who administers users and holder lists (OD-S12-06).

## Unresolved Issues
- OD-S12-18 anchor location; OD-S12-06 user administration; Stage 24 owns threat model and final control values.

## Residual Risks
- R-SEC-1: tail truncation after the last anchor is undetectable.
- Local credential store is weak vs enterprise SSO (SA-3); the product must not be exposed beyond loopback until Stage 23-25 close gaps.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
