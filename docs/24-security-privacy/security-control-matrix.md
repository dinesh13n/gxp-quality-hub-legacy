---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "security-control-matrix.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/*.py", "hub/web/*.py", "hub/gate/", "hub/r2/protection.py", "hub/core/untrusted.py", "hub/guards/", "tests/hub/test_tst_hub_stg24_*.py", "docs/24-security-privacy/evidence/", "docs/12-specs/security-spec.md", "docs/16-repo-validation/security-scan-summary.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
Threat to control to test, with the control VALUES and the decision each one still needs. 30 controls: 24 present before this stage, 6 added or tightened by Stage 24 (SCM-03, SCM-11, SCM-40, SCM-41, SCM-44, SCM-45 in part). Every value in section SCM-2 is a PROPOSAL carried from Stage 12 (A-12-F09-1) and still needs the Engagement lead's decision (DQ-09). "Present" means it exists in code and has the cited test; it does not mean the obligation is met (GD-11).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SCM-1 Control matrix [Verified Fact: code + test; status words are Stage 24's]
| ID | Control | Implemented in | Value / rule | Tests | Stage 24 change | Threats |
|---|---|---|---|---|---|---|
| SCM-01 | Deny-by-default routing and role matrix | `hub/web/routes.py`, `hub/web/authz.py`, `hub/security/route_registry.json` | 48 operations pinned to the OpenAPI; unknown route 403, audited | TST-SEC-01, I8 | none | T-09 |
| SCM-02 | Password store, lockout, generic errors | `hub/security/auth.py` | SC-01..SC-05 | TST-SEC-04..06, INC08-S11 | boundary test S22; floors S21 | T-10 |
| SCM-03 | Sessions and cookie | `hub/security/auth.py`, `hub/web/api.py`, `hub/security/transport.py` | SC-06, SC-07, SC-20 | S23 (logout, fixation, disabled principal), S24 (cookie attributes, Secure with TLS) | `Secure` flag when TLS settings exist (A-INC08-3) | T-11 |
| SCM-04 | CSRF | `hub/web/csrf.py` | SC-21 | I8-SEC-17 | none (login POST has no token: A-INC08-5) | T-12 |
| SCM-05 | Service tokens, non-human role | `hub/web/tokens.py` | SC-22 | TST-SEC-08, I8 | none | T-17 |
| SCM-06 | Exposure refusal | `hub/security/exposure.py`, `hub/web/server.py` | SC-11, SC-12 | TST-SEC-16, Stage 23 S03..S05 | none | T-18 |
| SCM-10 | `Untrusted` wrapper and static lint | `hub/core/untrusted.py`, `hub/intake/untrusted_lint.py` | text is data, never a decision parameter | TST-INT-17..29, INC08-S09 | none | T-01 |
| SCM-11 | Output encoding, CSP, nosniff, no CORS | `hub/web/ui.py`, `hub/web/app.py` | CSP `default-src 'self'`; exact values pinned by Stage 23 S01/S02 | INC08-S10, Stage 23 S01, Stage 24 S40/S41 | 17-string hostile corpus over 5 pages and 85 requests | T-02 |
| SCM-12 | No model reads data | `hub/guards/no_ai.py` | deny-list, `model_calls_total = 0` | TST-CO-11, TST-NFR-13 | none | T-01, T-04 |
| SCM-13 | Quarantine, contract check, replay safety | `hub/intake/` | outcomes never auto-corrected | TST-INT-01..16 | none | T-05 |
| SCM-14 | SQL safety | bound parameters; identifier allow-lists | 36 formatted + 23 indirect `execute` calls are the reviewed baseline | S32 | NEW lint-style baseline test (closes SS-03) | T-13 |
| SCM-15 | Gateway URL and scheme allow-list | `hub/adapters/gateway_client.py` | http(s) loopback, no redirects | TST-INT-25 | none | T-14 |
| SCM-20 | Zone H single choke point | `hub/gate/actions.py`, `hub/security/zone_h.py` | one holder rule, written once | Stage 20 S20, TST-GATE | none | T-03 |
| SCM-21 | Holders empty, human + re-auth | `hub/security/settings.py` | SC-08, SC-09 | TST-GATE-01..22 | none | T-03 |
| SCM-22 | Approval-gated authority switch | `hub/control/` | CLI + `approval_ref` (OD-31) | Stage 23 S10..S16 | none | T-23 |
| SCM-30 | Dependency control | stdlib only | no manifest, no third-party import | TST-CO-11, S30, S31 | NEW S30/S31 | T-21 |
| SCM-31 | Egress guard | `hub/guards/egress.py` | loopback only | TST-CO-12, E21/E23/E24 | E24 added | T-06 |
| SCM-40 | Retained-table protection | `hub/security/tables.py`, `scan.py`, triggers | 39 retained tables (was 18), 3 mutable, 2 derived; reviewed delete sites | S01..S04 | RETAINED_TABLES gap closed (RF-02) | T-15, T-16 |
| SCM-41 | No secrets in audit / log | `hub/security/audit.py`, `hub/obs/log.py` | credential keys refused; patterns redacted | TST-SEC-15, S12 | S12 | T-07 |
| SCM-42 | Hash-chained audit trail | `hub/security/audit.py` | per-record chain | TST-SEC-09..12 | none | T-15 |
| SCM-43 | Anchor | `hub/security/audit.py` | SC-10 | TST-SEC-11, -12 | none | T-15 |
| SCM-44 | Anchor seal (opt-in HMAC) | `hub/security/anchor_seal.py`, `python -m hub.security seal / check-seal` | key in `HUB_ANCHOR_SEAL_KEY` (>= 32 bytes) | S26 | NEW; OFF unless an operator runs it | T-15 |
| SCM-45 | Field classes, C3 reasons, masking | `hub/r2/protection.py`, `hub/security/datamap.py` | C0..C3 proposed; 345 store columns classified | I9-SEC-20, I9-NFR-12, S10..S13, S25 | field map; reason by header | T-20, T-24 |
| SCM-50 | Secret scan | `hub/security/scan.py` | regex over hub, tests/hub, Stage 24 docs | TST-SEC-18, S33 | scope widened to the Stage 24 docs | T-08 |
| SCM-51 | Insert-only decision / policy / intake history | triggers M002..M007 | no update, no delete | TST-NFR-10, S04 | S04 exercises 28 populated tables | T-16 |
| SCM-52 | Kill switch, runtime floor | `hub/runtime.py`, config `hub.kill` | floor Python 3.10 / SQLite 3.37 | TST-CO-14 | none | T-19 |
| SCM-53 | Backup with checksums | `hub/ops/backup.py` | manifest verified before restore | TST-CO-07, -09 | none | T-16 |
| SCM-54 | Request limits | `hub/web/app.py`, `server.py` | 1 MiB body, no Transfer-Encoding, one request per connection | I8 | none | T-19 |
| SCM-55 | Correlation id, structured log | `hub/obs/log.py` | id regex-validated; no secrets | TST-OBS | S41 (hostile id never echoed) | T-07 |
| SCM-56 | Release gate G6 | `hub/ops/release.py`, `hub/security/scan.py` | release not ready unless scan clean | TST-CO-10, -15 | covers 39 tables | T-16 |

### SCM-2 Control values and the decisions still needed (DW-19) [Verified Fact: value; Assumption: that it is right]
| Value | Shipped | Recommended default (applied) | Alternative | Status | Decision |
|---|---|---|---|---|---|
| PBKDF2-HMAC-SHA256 iterations (SC-01) | 600,000 (floor 600,000) | keep | raise; scrypt / Argon2 not guaranteed in the 3.10 stdlib | PROPOSED | DQ-S24-01 |
| Password minimum length (SC-02) | 12 (floor 12) | keep 12 with no composition rules, no forced expiry | 15 for a sole authenticator (current NIST SP 800-63B guidance, recalled, re-check) | PROPOSED | DQ-S24-01 |
| Lockout (SC-03..05) | 5 failures / 15 min window / 15 min lock | keep | progressive delay; unlock procedure | PROPOSED | DQ-S24-01 |
| Session idle / absolute (SC-06, SC-07) | 30 min / 8 h | keep | shorter for Zone H sessions (re-auth already 5 min) | PROPOSED | DQ-S24-01 |
| Zone H re-auth window (SC-08) | 300 s | keep | 120 s | PROPOSED | DQ-S24-01 |
| Zone H holders (SC-09) | empty | stay empty | named holders (needs real people) | Dinesh only | OD-31 |
| Audit anchor (SC-10, location) | JSON lines file, outside the DB directory, every 100 records | keep, plus run the seal where any real use begins | witness on another host | PROPOSED | DQ-S24-02 |
| Anchor strength | unsigned, same host | seal built, OFF | required seal + key custody; or external append-only witness | PROPOSED | DQ-S24-02 |
| TLS / exposure (SC-11, SC-12) | loopback only | stay loopback-only; `Secure` cookie rule built | terminate TLS at a proxy (Stage 27) | PROPOSED | DQ-S24-03 |
| Cookie flags (SC-20) | HttpOnly; SameSite=Strict; Path=/; Secure iff TLS | as built | `__Host-` prefix when TLS | built, PROPOSED | DQ-S24-03 |
| C3 reason transport (SC-25) | header or query (header wins) | keep both now; retire the query form at exposure | header only | built, PROPOSED | DQ-S24-04 |
| Service tokens (SC-22) | no mandatory expiry; rotation = issue + revoke | keep; require an expiry (for example 90 days) before real use | none | PROPOSED | DQ-S24-05 |
| Login body returns token (SC-24) | yes (CLI clients) | keep | omit for browser flows | PROPOSED | DQ-S24-06 |
| Login CSRF (SC-21) | none on login POST | accept (loopback, single organisation) | pre-session token | PROPOSED | DQ-S24-06 |
| Finance read surface (RTD-82) | no route reaches the masking path | leave unreachable | add routes after a stakeholder exists | open | DQ-S24-07 |
| Field classes / tenant dimension (RTD-83) | C0..C3 proposed; no tenant column in the hub store | keep | add tenant column (migration) | PROPOSED | DQ-S24-08 |

Nothing in this table is an approval. Where the stage applied a "recommended default", it simply left the shipped value; the only behaviour added is default-off or default-equal (`Secure` only with TLS, a header that is also accepted, the opt-in seal).

## Evidence References
Tests: `tests/hub/test_tst_hub_stg24_{tables,fields,controls,supply,injection}.py` (21 methods) and `test_tst_hub_stg24_egress_guard.py` (1); evidence under `docs/24-security-privacy/evidence/` (`control-values.json`, `store-table-dispositions.json`, `field-map.json`, `sql-dynamic-sites.json`, `cookie-attributes.json`, `anchor-seal.json`, `hostile-corpus.json`, `hub-mutation-s24.json`, `regression-s24.json`). Earlier-stage tests named above were last run in full by the orchestrator at the Stage 23 merge (OD-30: 19 groups green); this stage re-ran groups A, B, I8a, I8b, I9 (see `security-test-results.md`).

## Assumptions
- A-S24-CM-1 Every value above is a proposal; the recommended default is only a suggestion until Dinesh decides (DQ-09).
- A-S24-CM-2 The NIST and OWASP figures quoted are recalled public guidance and were not re-fetched in this stage; re-check before adopting.

## Unknowns
- U-S24-CM-1 Applicable policy or regulation for password and session values (none in the repository).
- U-S24-CM-2 Whether MFA or SSO will ever be required (SA-3: local store is a stopgap).

## Unresolved Issues
- DQ-S24-01..08 open (list in `residual-security-risks.md`).

## Residual Risks
RS-01, RS-02, RS-03, RS-04, RS-07, RS-08, RS-09.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
