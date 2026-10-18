---
stage: "13 — Requirements → Specs → Tests → Evidence Traceability"
artifact: "security-traceability.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/12-specs/acceptance-criteria.md", "docs/12-specs/business-rules.md", "docs/12-specs/spec-readiness.md", "docs/13-traceability/evidence/coverage.json", "docs/13-traceability/evidence/coverage_output.txt", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09, OD-10)", "docs/12-specs/security-spec.md", "docs/12-specs/api-contracts.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Planned tests are PLANNED / NOT-RUN: nothing in this stage was executed against the application, and no evidence listed here as "expected" exists yet. Approval is Dinesh Naik's decision (HAR-11).**

Security view: 19 requirements -> 83 acceptance criteria (56 negative) -> evidence at Stage 26 (TEVV). 15 of 15 threats have a planned test. Mechanism-level evidence only; no real users, holders or environment exist.

## Findings
### SEC-1 Scope and counts [Verified Fact: computed]
19 requirements in the security view (13 FR + 6 PNFR); they carry **83 distinct acceptance criteria, 56 of them negative (forbidden-path)** (67%). Class mix of those criteria: A 66 / B 17 / C 0. Threat register SEC-01..SEC-15 (security-spec.md): **15 of 15 threats have >= 1 planned test**; threats with none: none.

### SEC-2 Requirement -> test (security view)
| ID | Requirement (abridged) | Rel | Acceptance criteria | #AC | #neg | Class | Evidence stage | Domain note |
|---|---|---|---|---|---|---|---|---|
| FR-GATE-01 | No component of the product (rules, scheduler, importer, report, template, search) SHALL make, pre-fill as fin | R1 | AC-GATE-09,11..14,21; AC-INT-24; AC-RUN-12 | 8 | 8 | A | 16 |  |
| FR-GATE-02 | The system SHALL present, read-only, an evidence pack for a case needing disposition (case, linked objects, ev | R1 | AC-GATE-15 | 2 | 1 | A | 16 |  |
| FR-GATE-03 | Transitions classified as Zone H (disposition, release, e-signature, closure of a case failing the evidence ru | R1 | AC-DEC-17; AC-GATE-09,12; AC-OBS-06; AC-POL-02,18; AC-RUN-03; AC-SEC-08 | 9 | 7 | AB | 16,26,31 |  |
| FR-GATE-04 | The authorised-role holder list SHALL be configuration and SHALL ship empty; until at least one holder is conf | R1 | AC-GATE-01,22 | 3 | 1 | B | 16 | blocked by OD-S12-05/06 |
| FR-GATE-05 | The recording mode of a disposition SHALL be a configuration choice: (a) record the human's decision as an eve | R1 | AC-GATE-01,03,05..08 | 6 | 2 | B | 16 | OD-S12-05 both modes |
| FR-GATE-06 | A reviewer SHALL be able to override, dismiss or refuse any rule-generated flag, classification or priority, w | R1 | AC-GATE-18..20; AC-REV-08 | 4 | 1 | A | 16 |  |
| FR-SEC-01 | All read and write paths to case data SHALL require authentication and role-based authorisation; roles SHALL i | R1 | AC-DEC-13; AC-ID-08; AC-SEC-01..05,07 | 9 | 7 | A | 16,26 |  |
| FR-SEC-02 | Every decision event, policy change, Zone H transition and authorisation failure SHALL be written to a tamper- | R1 | AC-DEC-24; AC-GATE-22; AC-SEC-03,09..14,21 | 10 | 5 | AB | 16,26 |  |
| FR-SEC-03 | Sensitive/identifying fields SHALL be handled per docs/00-preflight/operating-contract/data-use-constraints.md | R2 | AC-ID-17; AC-REV-12; AC-SEC-19 | 4 | 3 | A | 16,26 | R2: no R1 control |
| FR-INT-07 | Inbound text (feed notes, document bodies, emails) SHALL be treated strictly as data: no inbound string SHALL  | R1 | AC-GATE-13; AC-INT-22..24 | 4 | 4 | A | 16 |  |
| FR-DEC-05 | A transition to any state that the active closure policy (FR-POL-01) designates as a closing state SHALL be re | R1 | AC-DEC-15..19,27 | 7 | 3 | B | 16 |  |
| FR-POL-03 | Every change to a policy object or rule table SHALL itself be an immutable event (who, when, old value, new va | R1 | AC-GATE-08; AC-POL-03,09,25 | 5 | 2 | AB | 16 |  |
| FR-ID-02 | Orphans SHALL remain orphans: no link SHALL be created by guessing or similarity. A human MAY create a link; t | R1 | AC-ID-02..08 | 7 | 5 | A | 16 |  |
| PNFR-07 | Only authenticated, authorised users read or change case data - 100% of endpoints authenticated and authorised | R1 | AC-NFR-07; AC-SEC-01,06,17 | 4 | 4 | A | 26 |  |
| PNFR-08 | Data in transit protected; no secrets in source - Secret scan finds 0; any non-loopback binding uses TLS and r | R1 | AC-INT-25; AC-NFR-08; AC-OBS-04; AC-SEC-06,15,18 | 7 | 7 | AB | 16,26,31 |  |
| PNFR-09 | Every decision and state change attributable and tamper-evident (framing only, not Part 11 certification) - 10 | R1 | AC-NFR-09; AC-SEC-10 | 3 | 1 | A | 26 |  |
| PNFR-12 | Sensitive fields handled per data-use constraints - 100% of field classes covered by an access test | R2 | AC-NFR-12; AC-SEC-19 | 2 | 0 | A | 26 | R2 |
| PNFR-13 | Inbound content never acts as instruction or approval - 0 effects on decision fields from the planted-string f | R1 | AC-DEC-25; AC-INT-22; AC-NFR-13; AC-REV-04,10 | 5 | 5 | A | 16,26 |  |
| PNFR-10 | Retention follows a policy once decided - 0 deletions of case/evidence records while no retention policy is ad | R1 (hold-all) | AC-DEC-03; AC-NFR-10; AC-SEC-18 | 3 | 3 | AB | 16,25,26 |  |

### SEC-3 Threat -> control -> requirement -> test
| Threat | Objective | Control (spec ref) | Requirements | Planned tests (cited ACs + ACs of cited behaviours) | #AC | Fixture / planted data |
|---|---|---|---|---|---|---|
| SEC-01 | Unauthenticated access to case data | authenticate every route; deny by default; route-registry test (BEH-SEC-01, AC-S | FR-SEC-01, PNFR-07 | AC-SEC-01 | 2 |  |
| SEC-02 | Privilege misuse / role creep | RBAC matrix below; permission per operation; service identities flagged non-huma | FR-GATE-03, FR-SEC-01 | AC-SEC-08 | 1 |  |
| SEC-03 | Automated or forged disposition / release / e-signature | single Zone H choke point, holder list empty by default, human + step-up + pack_ | FR-GATE-01, BR-08 | AC-GATE-09,11..14,21; AC-INT-24; AC-RUN-12 | 8 |  |
| SEC-04 | Prompt/instruction injection in inbound text | `Untrusted` type, escape-on-output, no parsing of text, fixture gate 86/22/44 (B | FR-INT-07, PNFR-13 | AC-INT-22..24 | 3 | planted-string set (86/22/44) |
| SEC-05 | Tampering with history/audit | insert-only triggers + per-case and audit hash chains + out-of-DB anchor (ADR-00 | FR-SEC-02, PNFR-09 | AC-SEC-09,13 | 3 |  |
| SEC-06 | Credential theft/guessing | PBKDF2 salt, lockout, generic errors, hashed session tokens, rotation for servic | PNFR-07 | AC-SEC-04..07 | 4 |  |
| SEC-07 | Web attacks (XSS, CSRF, clickjacking) | escaping, CSRF tokens, custom header, CSP default-src 'self', nosniff (BEH-SEC-0 | PNFR-07, PNFR-13 | AC-SEC-17 | 1 |  |
| SEC-08 | Injection into SQL/FTS/shell/paths | parameterised SQL, identifier allow-lists, FTS term quoting (BEH-REV-03), no she | PNFR-13 | AC-REV-09..11 | 3 |  |
| SEC-09 | SSRF / scheme abuse via gateway URL | http/https loopback only (BEH-INT-11, AC-INT-25) | PNFR-08 | AC-INT-25..27 | 3 |  |
| SEC-10 | Network exposure | loopback bind default; non-loopback needs approval flag + TLS (BEH-SEC-08) | PNFR-08 | AC-SEC-16 | 1 |  |
| SEC-11 | Secrets in code/logs | env-only secrets, secret scan gate, no secrets in logs/audit (BEH-SEC-07) | PNFR-08 | AC-OBS-04; AC-SEC-15,18 | 3 |  |
| SEC-12 | Sensitive data over-exposure | field classes, masking, deny default, C3 read/export reasons (BEH-SEC-10) | FR-SEC-03, PNFR-12 | AC-SEC-19 | 2 |  |
| SEC-13 | Supply chain / AI egress | stdlib only, deny-list, no outbound network, `model_calls_total = 0` (BEH-CO-07) | FR-CO-04, PNFR-18 | AC-CO-11 | 2 |  |
| SEC-14 | Data loss / destructive change | hold-all, no delete paths, backups with checksum, rollback rehearsal (BEH-SEC-11 | PNFR-05, PNFR-10, PNFR-19 | AC-CO-09; AC-SEC-18 | 3 |  |
| SEC-15 | Tenant/data leakage across access levels | access filter before ranking/counting (BEH-REV-04); tenant filter mandatory | FR-SEC-03 | AC-REV-12..14 | 3 |  |

### SEC-4 Findings
- **[Verified Fact]** Zone H (human-only disposition/release/e-signature, BR-08, FR-GATE-01..06) has 32 ACs; 20 are negative. The fresh-install state (holders empty, mode `none`) is itself tested (FR-GATE-04, OD-S12-05/06), so *no pilot use of Zone H is permitted or testable with real holders* until Dinesh decides (RD-4).
- **[Verified Fact]** Evidence class for authentication/authorisation (PNFR-07), transport/secrets (PNFR-08), audit tamper-evidence (PNFR-09), untrusted content (PNFR-13): class A/B sandbox tests, evidence stage 26 (TEVV). They prove the mechanism on synthetic data only. No penetration test, secret-scan baseline or TLS configuration review is planned in any AC beyond AC-SEC-15/16/18 and AC-NFR-08 [Inference].
- **[Verified Fact]** Error codes with security meaning not asserted by any AC: E-AUTH-BAD-CREDENTIALS, E-GATE-UNKNOWN-ACTION, E-SEC-AUDIT-TAMPER-DETECTED [GAP-13-12].
- **[Verified Fact]** `FR-SEC-03` and `PNFR-12` (sensitive-field access levels) are **R2**; no R1 control covers field-level protection (data-use-constraints). Impact: R1 treats all data as restricted by default (`evidence_record.access_level` default `restricted`) [Inference].
- **[Inference]** The planted-string fixture (86 feed rows, 22 document bodies, 44 regex hits) is the single evidence source for FR-INT-07/PNFR-13; its counts come from Stage 9/12 and were not re-counted in this documentation-only stage.
- **[Unknown]** Who administers users and holder lists in real operation (OD-S12-06); where the audit anchor lives in a deployment (OD-S12-18). Without them AC-SEC-10/11 can only prove the mechanism.
- **[Assumption]** "Tamper-evident" is framing only; there is no Part 11 / GxP compliance claim (DR-29; ACC-8).

## Evidence References
- `docs/12-specs/security-spec.md` (threat register), `docs/12-specs/features/f02-human-disposition-gate.md`, `f09-access-audit-protection.md`, `docs/09-initial-prd/functional-requirements.md`, `nfrs.md`, `docs/12-specs/acceptance-criteria.md`, `error-handling-spec.md`.

## Assumptions
- A-13-08 [Assumption]: the security view membership (FR-SEC, FR-GATE, FR-INT-07, FR-DEC-05, FR-POL-03, FR-ID-02, PNFR-07..10,12,13) is correct; Stage 24 may extend it.

## Unknowns
- U-13-07: real role holders, admin model and audit anchor location (OD-S12-06, OD-S12-18).

## Unresolved Issues
- Zone H unusable until OD-S12-05/06 decided (owner: Engagement lead (Dinesh Naik), before pilot, Stage 15+).
- Unasserted security error codes (GAP-13-12).

## Residual Risks
- R-13-07 Passing sandbox security tests could be mistaken for a security assessment; none was performed (no pen test, no threat-model review beyond security-spec.md).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial traceability produced by script from docs/ (evidence/trace_parse.py, trace_compute.py). |

