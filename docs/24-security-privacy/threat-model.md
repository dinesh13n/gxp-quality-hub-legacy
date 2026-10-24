---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "threat-model.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/web/app.py", "hub/web/server.py", "hub/security/*.py", "hub/gate/*.py", "hub/r2/protection.py", "docs/12-specs/security-spec.md", "docs/10-architecture/security-architecture.md", "docs/11-data-context/metadata-model.md", "docs/16-repo-validation/security-scan-summary.md", "docs/23-human-control/", "docs/25-governance/", ".fde/orchestrator-decisions.md", "tests/hub/test_tst_hub_stg24_*.py", "docs/24-security-privacy/evidence/"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
Threat model of the whole system, including the places where an AI could enter. 12 components, 26 threats over every threat class the stage lists. 18 are controlled by something present and tested, 6 only partly, 2 (T-22 runtime vulnerabilities, T-26 legacy defects) have no control in this stage; no threat is rated Critical; the highest residual ratings are High, all conditional on leaving loopback (RS-01, RS-02, RS-04). The product is No-AI (OD-08), so the AI-specific classes (prompt / indirect injection, excessive agency, insecure tool use, poisoning) are assessed as *structural* threats: instruction-like text in data that no model reads, and the day an AI is added. Method: components from `docs/10-architecture/component-model.md` and the repository; threats by STRIDE per component plus the stage's named classes; likelihood and impact on a 3-level scale (Low / Medium / High) judged by the agent, not measured (no real users or telemetry exist, OD-04).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TM-1 Components and trust boundaries [Verified Fact: from the code; boundaries are Inference]
| ID | Component | Where | Trust boundary |
|---|---|---|---|
| CP-01 | Loopback HTTP API + UI (48 API operations + 10 UI routes) | `hub/web/` | the one network-facing surface; binds 127.0.0.1 only, non-loopback peers dropped |
| CP-02 | Identity: local PBKDF2 users, sessions, service tokens | `hub/security/auth.py`, `hub/web/tokens.py` | credentials cross here |
| CP-03 | Zone H gate (disposition, adoption, release, e-signature analogue) | `hub/gate/`, `hub/security/zone_h.py` | the human-only choke point; holders EMPTY |
| CP-04 | Store + audit chain + anchor | `hub/store/`, `hub/security/audit.py` | SQLite file and an anchor file on the same host |
| CP-05 | Intake adapters (partner feed, vendor CSV, gateway, documents) | `hub/intake/`, `hub/adapters/` | UNTRUSTED data enters here |
| CP-06 | Search + R2 reports + data protection | `hub/review/`, `hub/search/`, `hub/r2/` | field classes, C3 reasons |
| CP-07 | Operator CLIs (`python -m hub.*`) | `hub/*/__main__.py` | host operator = trusted, same host |
| CP-08 | Configuration and decision flags | `hub/config.py`, `hub/control/` | file edited by the operator; approval_ref is a pointer, not verified |
| CP-09 | Build and supply chain | `pyproject.toml`, `tests/hub/`, CI absent for hub | stdlib only |
| CP-10 | AI coding assistant used to BUILD (dev tooling, not product AI; BR-AI-7) | outside the product | listed in the AI register (OD-31) |
| CP-11 | Legacy estate (unchanged) | `app/`, `legacy_*`, `services/`, `compose.yaml` | pre-existing defects, byte-identical (SS-05) |
| CP-12 | Backups and restore | `hub/ops/backup.py` | files on the same host |

### TM-2 Threat register [Inference unless marked; evidence is a path or a test]
Likelihood (L) and Impact (I) are agent judgements for the loopback shadow deployment; "if exposed" means after leaving loopback, which is not allowed (HAR-05). Control status: P = present and tested, S = added by Stage 24, Pt = partial, O = open.
| ID | Class | Threat | Comp | L | I | Controls (matrix id) | Status | Residual | Conf |
|---|---|---|---|---|---|---|---|---|---|
| T-01 | Prompt / indirect injection | instruction-like text in a feed row, document, note or evidence payload steers a decision | CP-05, CP-06 | Medium | High | `Untrusted` type, no model call, escape on output, S40 corpus (SCM-10..12) | P, S | RS-15 (only if AI is added) | High |
| T-02 | Insecure output handling | stored markup rendered as active HTML / JSON | CP-01 | Medium | Medium | HTML escaping, CSP `default-src 'self'`, nosniff, S40 (SCM-11) | P, S | Low | High |
| T-03 | Excessive agency | an automated actor performs a Zone H action | CP-03 | Low | High | holders empty, human-only role, re-auth, static import test, trigger (SCM-20..22) | P | Low | High |
| T-04 | Insecure tool use | model or script given tools | CP-10 | Low | Medium | no agent / tool runtime in the product; deny-list + egress tripwire (SCM-30) | P | Low | High |
| T-05 | Poisoning | corrupted feed / document / rule input changes policy or history | CP-05 | Medium | High | quarantine outcomes, insert-only history, inactive rule sets, replay safety (SCM-13, SCM-40) | P | Medium (RS-06) | Medium |
| T-06 | Data exfiltration | data leaves the host | all | Low | High | egress guard (loopback only), no outbound client outside adapters, `model_calls_total = 0` (SCM-31) | P | Low | High |
| T-07 | Exfiltration via logs / audit | secrets or PII written to logs / audit | CP-04 | Low | High | credential-key refusal in audit, log redaction, S12 (SCM-41) | P, S | Low | High |
| T-08 | Secrets exposure | secret in source, config, backup | CP-09 | Low | High | regex scan on hub, tests/hub and Stage 24 docs (S33), env-only seal key (SCM-50) | P, S | Low | Medium |
| T-09 | Authorisation bypass | route reachable without role | CP-01 | Low | High | deny-by-default route registry pinned to OpenAPI (TST-SEC-01), role matrix (SCM-01) | P | Low | High |
| T-10 | Broken authentication | guessing, stuffing, timing | CP-02 | Medium | High | PBKDF2 600k, lockout 5/15/15, generic errors, dummy hash for unknown users (SCM-02) | P | RS-02, RS-04 (High if exposed) | Medium |
| T-11 | Session theft / fixation | stolen or reused token | CP-02 | Low | High | 256-bit tokens, hash stored, HttpOnly, SameSite=Strict, Secure with TLS, logout revokes, S23 / S24 (SCM-03) | P, S | RS-07 | Medium |
| T-12 | CSRF | cross-site write | CP-01 | Low | Medium | custom header, derived form token, no CORS (SCM-04); login POST has none | Pt | RS-07 | Medium |
| T-13 | SQL / FTS / path injection | hostile identifier or term | CP-01, CP-06 | Low | High | bound parameters, identifier allow-lists, FTS term quoting, S32 lint baseline (SCM-14) | P, S | Low (Inference: review, not proof) | Medium |
| T-14 | SSRF / scheme abuse | gateway URL `file:` / non-loopback | CP-05 | Low | Medium | http/https loopback allow-list, no redirects (SCM-15) | P | Low | High |
| T-15 | Audit tampering | edit / truncate history | CP-04 | Low | High | insert-only triggers (39 tables), hash chain, anchor; opt-in seal (SCM-42..44) | Pt | RS-03 | High |
| T-16 | Destructive change | delete / drop evidence | CP-04 | Low | High | triggers, deletion-path grep over all 39 retained tables, reviewed delete sites (SCM-40) | P, S | RS-12 | High |
| T-17 | Privilege creep via roles | service token used as human; role escalation | CP-02 | Low | High | `integration` role non-human, never re-auth fresh, human-only routes (SCM-05) | P | Low | High |
| T-18 | Exposure beyond loopback | bind 0.0.0.0, no TLS | CP-01 | Low | High | startup guard + server refusal even with approval (S23) (SCM-06) | P | RS-01 | High |
| T-19 | Denial of service | slow or flood requests | CP-01 | Low | Medium | body limit 1 MiB, one request per connection, loopback only | Pt | RS-04 | Medium |
| T-20 | Over-exposure of sensitive fields | C3 read without reason; finance sees identifiers | CP-06 | Low | Medium | C3 reason (header or query), masking, deny default, audited (SCM-45) | Pt | RS-05, RS-06 | Medium |
| T-21 | Supply chain | third-party package or hostile dependency | CP-09 | Low | High | stdlib-only test S30, deny-list TST-CO-11, no manifest (SCM-30) | P, S | RS-10 | High |
| T-22 | Runtime vulnerabilities | CPython 3.10.12 / SQLite 3.37.2 / Node 22 CVEs, end of support | CP-09 | Medium | Medium | none offline; production targets 3.12+ (OD-24) | O | RS-10 | Low |
| T-23 | Config / flag tampering | a decision flag or authority switched without a human decision | CP-08 | Low | High | approval_ref rule, CONFIG_CHANGED audit, L3 flip (S23) | Pt | approval_ref is unverifiable (Unknown) | Medium |
| T-24 | Privacy: staff identifiers | `actor` ids and free text are personal-data analogues | CP-04 | Medium | Medium | field map (345 columns classified), audit is C3, hold-all retention | Pt | RS-06 (regime Unknown) | Medium |
| T-25 | Responsible-AI | AI added later without controls (bias, opacity, over-reliance) | CP-10 | Low | High | RQ-1..RQ-3 re-qualification triggers (OD-08), deterministic-AI boundary, AI register | P (structural) | RS-15 | Medium |
| T-26 | Legacy defects | weak hash, `urlopen` without scheme check, `0.0.0.0` in compose, destructive tests | CP-11 | Medium | Medium | not changed (byte-identical); retire at cutover | O | RS-11 | High |

### TM-3 What the model does not cover [Inference]
Insider with host access (the operator is trusted: CP-07, CP-08 and CP-12 sit on the same host as the store); physical or OS-level attack; real identity provider; real data. A penetration test and red team are Stage 26.

## Evidence References
`docs/12-specs/security-spec.md` SEC-01..15 and abuse cases ABU-01..10; `docs/16-repo-validation/security-scan-summary.md` SS-01..SS-08; `docs/10-architecture/security-architecture.md`; `hub/security/route_registry.json` (48 operations); `hub/web/ui_routes.json` (10 routes); Stage 24 tests S01..S41 and `evidence/hub-mutation-s24.json` (8 of 8 mutants killed).

## Assumptions
- A-S24-TM-1 Likelihood and impact ratings are agent judgements for a synthetic, loopback-only shadow deployment; they have not been reviewed by a security owner. Confirm: Engagement lead (Dinesh Naik).
- A-S24-TM-2 The operator (CLI user on the host) is trusted. If that is wrong, T-15, T-16, T-23 rise.

## Unknowns
- U-S24-TM-1 Real user population, identity provider and data (SEC-6; U-12-SEC-1).
- U-S24-TM-2 CVE status of the runtimes (no offline vulnerability database).
- U-S24-TM-3 Whether any consumer outside the repository reads the hub outputs (OD-28 (b): Unknown).

## Unresolved Issues
- Security values are still proposals (DQ-09); see `residual-security-risks.md` for the decisions needed.
- T-22 and T-26 have no control in this stage.

## Residual Risks
RS-01..RS-16 in `residual-security-risks.md`. Highest if the product were exposed: RS-01 (no TLS), RS-02 (single-factor passwords), RS-04 (no rate limiting).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
