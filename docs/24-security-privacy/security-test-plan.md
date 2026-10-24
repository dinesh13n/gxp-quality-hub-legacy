---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "security-test-plan.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/*.py", "tests/hub/test_tst_hub_stg24_*.py", "docs/24-security-privacy/evidence/", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
Plan and method of Stage 24 testing. Static review of code, a new 22-method test set in two groups (S24 21, E24 1), a mutation gate of 8 hostile code changes, and re-use of earlier groups. All tests run only on sandbox copies outside the working tree; `data/` is never touched and the backup checksum is verified before and after. There is no penetration test, no dynamic scanner and no fuzzing campaign (RS-14).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TP-1 Test set [Verified Fact]
| ID | Test | Threat / control |
|---|---|---|
| S01..S04 | table register vs live store; scan list; delete sites; delete refusal on 28 tables | T-15, T-16, SCM-40 |
| S10..S13 | every column classified; credential columns C3; free text and staff ids tagged; no secret in audit | T-07, T-20 |
| S20..S26 | control register drift; floors; lockout and session boundaries; ABU-10; cookie Secure; X-Hub-Reason; anchor seal | SCM-02, -03, -44, -45 |
| S30..S33 | stdlib-only imports; no dangerous APIs; SQL baseline; secret scan | T-13, T-21, T-08 |
| S40, S41 | 17-string hostile corpus; header injection | T-01, T-02 |
| E24 | egress guard around the whole S24 run | T-06 |
### TP-2 Mutation gate [Verified Fact]
8 mutants (for example drop a retained table from the register, remove a delete trigger, relax a floor, drop `Secure`, break the seal check, let the header reason be ignored). A mutant is killed when at least one S24 test fails. Target 8 of 8.
### TP-3 Regression [Verified Fact]
Groups B (No-AI/other), A, I8a, I8b, I9 re-run; the orchestrator runs the full regression in the cloud. Characterization harness run on the laptop.
### TP-4 Not tested [Verified Fact]
Penetration test, TLS, load/DoS beyond the request-size limit, browsers other than a raw HTTP client, real identity providers, concurrency attacks beyond the existing tests, supply-chain of the Python runtime itself.

## Evidence References
`tests/hub/test_tst_hub_stg24_*.py`, `evidence/s24_mutation_gate.py`, `tests/hub/regression_groups.json`.

## Assumptions
- A-S24-TP-1 A killed mutant demonstrates the test can see that class of change, not that the class is exhaustive.

## Unknowns
- U-S24-TP-1 Outcome of an external penetration test.

## Unresolved Issues
- Pentest not planned (needs Dinesh decision).

## Residual Risks
RS-14.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
