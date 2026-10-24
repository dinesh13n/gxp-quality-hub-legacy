---
stage: "26 — TEVV + AI Red Teaming"
artifact: "residual-tevv-risks.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["docs/26-tevv/red-team-findings.md", "docs/24-security-privacy/residual-security-risks.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW. Every risk below is OPEN. Nothing is accepted by this stage; acceptance is Dinesh Naik's (OD-30, OD-32).**

## Summary
Fifteen residual items remain after Stage 26: eleven findings, the open human walkthroughs, missing 3.12+ evidence, the untested full-regression-at-HEAD, and the structural limits of an agent-run, single-laptop, synthetic-data validation.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Risk | Source | Severity [Inference] | Owner / route | Due |
|---|---|---|---|---|---|
| RTR-01 | Restricted evidence note readable by reviewer through events | S26-F-02 | High | Dinesh (rule) + Stage 27 | before any real data |
| RTR-02 | Lone-surrogate 500 on 5 write surfaces | S26-F-03 | Medium | Stage 27 | Stage 27 |
| RTR-03 | Pre-auth validation on OP-GATE-02 | S26-F-01 | Medium | Stage 27 | Stage 27 |
| RTR-04 | Mistyped safety config keys are inert | S26-F-05 | Medium | Stage 27 | Stage 27 |
| RTR-05 | Tripwire and authority_ref controls have no killing test | S26-F-08, S26-F-09 | Medium | Stage 27 | Stage 27 |
| RTR-06 | CLI config errors show a traceback; no read timeout; generic 500 on store faults; duplicate authz layer untested; slow groups | S26-F-04, F-06, F-07, F-10, F-11 | Low | Stage 27 / 29 | backlog |
| RTR-07 | Human walkthroughs TST-REV-03/04/08 not performed or signed (RT-13) | OD-24 | blocks PASS | Dinesh (Engagement lead) | before PASS |
| RTR-08 | Python 3.12+ / 3.13 regression evidence missing (RT-14) | A-26-02 | blocks PASS | orchestrator cloud run (OD-23) | before PASS |
| RTR-09 | Full 23+2 group regression at final HEAD not run by this agent | S26-DEV-03 | process | orchestrator | at merge |
| RTR-10 | CT-13 fails on Node patch drift (golden v22.23.2, laptop v22.23.4) | S24-DEV-04 | Low | Stage 30 / refresh golden under approval | backlog |
| RTR-11 | Host-level full audit rewrite verifies ok (opt-in seal not enabled) | RS-03 | known | Dinesh | OPEN |
| RTR-12 | Unauthenticated request growth of the audit table | RS-04, `audit-amplification.json` (81 bytes/request) | Low on loopback | Stage 29 | backlog |
| RTR-13 | 12-mutant sample; the mutant space is larger | A-26-03 | method | Stage 27 may extend | - |
| RTR-14 | Agent-run red team on one laptop with synthetic data: no human adversary, no real browser, no production traffic, no performance or availability claim (class C) | method | method | Stages 28 / 29 | - |
| RTR-15 | Severity ratings are the agent's reading of TH-1 | A-26-13 | method | Dinesh may re-rate | - |

## Evidence References
`red-team-findings.md`, `tevv-results.md`, `docs/24-security-privacy/residual-security-risks.md` (RS-01..RS-16 remain OPEN).

## Assumptions
- A-26-17 [Assumption] Due dates are routes (stage names), not commitments; no person has agreed to any.

## Unknowns
- U-26-10 Real-world exposure of any finding (no production data, no real users).

## Unresolved Issues
- All risks open; none accepted.

## Residual Risks
- This file is the register.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
