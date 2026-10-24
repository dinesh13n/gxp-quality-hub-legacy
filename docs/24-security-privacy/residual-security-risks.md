---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "residual-security-risks.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/*.py", "tests/hub/test_tst_hub_stg24_*.py", "docs/24-security-privacy/evidence/", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
16 residual risks and 10 decisions needed from the Engagement lead. None is accepted: every owner is Dinesh Naik and acceptance requires his recorded decision. No risk is blocking for the synthetic, loopback, shadow deployment; several become blocking for any real exposure.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RR-1 Risk register [Inference: ratings; Verified Fact: the facts behind them]
| ID | Risk | L | I | Rating | Mitigation today | Status |
|---|---|---|---|---|---|---|
| RS-01 | No TLS; any exposure is plaintext | Low (loopback) | High | Medium | bind refusal, `Secure` rule | open |
| RS-02 | Single-factor local passwords | Medium | High | Medium | PBKDF2, lockout | open |
| RS-03 | Anchor same host, unsealed by default | Low | Medium | Low | seal built | open |
| RS-04 | No per-source rate limiting | Low | Low | Low | lockout per user | open |
| RS-05 | Finance read path unreachable (masking untested over HTTP) | Low | Low | Low | unit test | open |
| RS-06 | Field classes, tenant dimension, privacy regime unknown | Medium | High | Medium (High if real) | proposals | open |
| RS-07 | Login CSRF; token in login body | Low | Low | Low | SameSite=Strict | open |
| RS-08 | Service-token expiry optional | Medium | Medium | Medium | revocation, role limits | open |
| RS-09 | `?reason=` in URL still accepted | Low | Low | Low | header preferred | open |
| RS-10 | Python 3.10 / SQLite 3.37 CVE and end of life (about Oct 2026, recalled, re-check) | Medium | Medium | Medium | stdlib only | open |
| RS-11 | Legacy defects (T-26) | Medium | Medium | Medium | read-only adapters | open |
| RS-12 | `schema_migrations` no trigger; mutable `case_state`/`active_ruleset` | Low | Medium | Low | reviewed delete sites | open |
| RS-13 | Hand-written HTTP and auth code | Medium | High | Medium | tests, hostile corpus | open |
| RS-14 | Static analysis only; no pentest | Medium | Medium | Medium | mutation gate | open |
| RS-15 | AI added later without re-qualification | Low | High | Medium | OD-08 triggers, deny-list | open |
| RS-16 | Single approver (DQ-17) | Medium | Medium | Medium | audit, hash chain | accepted by Dinesh in OD-30 as a general risk; not as a Stage 24 acceptance |
### RR-2 Decisions needed from Dinesh
| ID | Question | Recommended default (applied as assumption) |
|---|---|---|
| DQ-S24-01 | Approve the control values (PBKDF2 600k, min 12, lockout 5/15/15, session 30 min/8 h, re-auth 300 s)? | keep as shipped |
| DQ-S24-02 | Anchor strength: A unsealed, B opt-in seal with key custody, C external witness | B |
| DQ-S24-03 | TLS and exposure: stay loopback, or approve a proxy at Stage 27? | loopback |
| DQ-S24-04 | Retire the `?reason=` query form at exposure? | yes, at exposure |
| DQ-S24-05 | Require service-token expiry? | yes, 90 days |
| DQ-S24-06 | Accept login CSRF and token in login body? | accept |
| DQ-S24-07 | Build the finance read surface? | not yet |
| DQ-S24-08 | Field classes, tenant column, privacy regime, retention period | decide before real data |
| DQ-S24-09 | Rate limiting and hardening migration (trigger on `schema_migrations`)? | defer to Stage 27 |
| DQ-S24-10 | Responsible-AI scope for a No-AI product; runtime upgrade timing; external pentest | confirm scope; schedule upgrade |

## Evidence References
`threat-model.md`, `security-control-matrix.md`, `security-test-results.md`, `.fde/orchestrator-decisions.md` (OD-08, OD-30, OD-31).

## Assumptions
- A-S24-RR-1 Ratings are the agent's judgement with no organisational scale.

## Unknowns
- U-S24-RR-1 Risk appetite and scale of the organisation.

## Unresolved Issues
- All 10 DQ-S24 items.

## Residual Risks
This document is the register.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
