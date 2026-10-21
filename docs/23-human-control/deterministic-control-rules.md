---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "deterministic-control-rules.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/guards/no_ai.py", "hub/guards/egress.py", "hub/guards/sandbox.py", "hub/security/audit.py", "hub/control/flags.py", "hub/web/server.py", "hub/web/app.py", "hub/control/registry.py", "tests/hub/test_tst_hub_stg23_controls.py", "tests/hub/test_tst_hub_stg23_registry.py", "tests/hub/test_tst_hub_stg23_schemas.py", "docs/20-application/deterministic-ai-boundary.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
These are the rules that hold with no human in the loop: the code enforces them and a test fails when they are broken. Stage 23 adds four (DC-04 approval rule, DC-05 loopback-only bind, DC-06 exact security headers, DC-07 contract schemas) and a generated error-code registry (DC-08). Mutants of the new rules are killed (H3, H5, A1, A2, and H1 for the Zone H matrix; see `human-control-test-results.md`).

## Findings
| ID | Rule | Enforced by | Test | Tag |
|---|---|---|---|---|
| DC-01 | No AI, model, prompt or network egress beyond loopback in the product | `hub/guards/no_ai.py` (deny-list), `hub/guards/egress.py`, `model_calls_total` tripwire | TST-CO-11, TST-CO-12, groups E8 / E9 / E20 / E21 / E23 | [Verified Fact] |
| DC-02 | Zone H: one choke point, interactive human, holder, re-auth, `authority_ref`; DB trigger refuses a Zone H event without a human actor and `holder_check_ref` | `hub/gate/actions.py`, `hub/gate/service.py`, `hub/decision/migrations/M003_decision_crosswalk.sql` | TST-GATE-02/09/10/11/12/21, STG23 S41/S42 | [Verified Fact] |
| DC-03 | Audit log is insert-only and hash-chained; a credential-like detail key is refused | `hub/security/audit.py` | TST-SEC | [Verified Fact] |
| DC-04 | A decision flag at a non-default value (and any `capability_authority.<cap> = authoritative`) needs `approval_refs[flag]`; the change is audited CONFIG_CHANGED (old, new, approval_ref, source); a return to default needs no ref (L3) | `hub/control/flags.py` `check`, `hub/config.py` `validate`, `hub/control/switch.py`, `hub/control/cli.py` | STG23 S10..S16; mutants A1, A2 | [Verified Fact] |
| DC-05 | A non-loopback bind is refused even with `network.exposure_approved` and TLS keys (exit 9, E-SEC-EXPOSURE-NOT-APPROVED); non-loopback peers are refused | `hub/web/server.py`, `hub/security/exposure.py` | STG23 S03..S05; mutant H5 | [Verified Fact] |
| DC-06 | Security response headers have exact values: `Cache-Control: no-store`, `Content-Security-Policy: default-src 'self'`, `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, on API, UI and error responses | `hub/web/app.py` | STG23 S01/S02; mutant H3 | [Verified Fact] |
| DC-07 | Every hub object type written to the store validates against its Stage 12 v0.2 JSON schema (16 of 16 schemas exercised; 10 store tables mapped) | `docs/23-human-control/stage12-v0.2/schemas/` | STG23 S30..S34 | [Verified Fact] |
| DC-08 | Error codes in code = codes in the generated registry (109, diff 0); exit codes unique except the documented 2 and 9 clashes | `hub/control/registry.py` | STG23 S20..S24 | [Verified Fact] |
| DC-09 | Raw intake is insert-only; inbound text is Untrusted data; intake is idempotent | `hub/intake/`, `hub/core/untrusted.py` | TST-INT, TST-GATE-13 | [Verified Fact] |
| DC-10 | No `random` or wall clock in the deterministic core; golden outputs reproduce bit for bit | TST-CO-13 | TST-CO-13 | [Verified Fact] |
| DC-11 | Legacy code and `data/` are byte-identical; tests run only in sandbox copies | `hub/guards/sandbox.py`, characterization harness | TST-CO-05/06/07; harness | [Verified Fact] |
| DC-12 | The configuration is validated at load; an unknown value for a decision flag is refused | `hub/config.py` | tests/hub/test_inc02_supplementary.py | [Verified Fact] |

### Findings
- [Verified Fact] Stage 16 had no test for DC-05 with an approved exposure (mutant H5 survived) nor for DC-06 exact values (H3 survived); STG23 kills both (`evidence/hub-mutation-s23.json`).
- [Verified Fact] The approval rule is checked in one place (`flags.check`, called by `config.validate`), so a flag set by hand in the config file, by the CLI or by a test fixture takes the same path.
- [Inference] `approval_ref` is a non-empty reference string (length-bounded, no credential-like content). The hub cannot tell a real approval from a made-up reference; the rule makes a missing approval visible and audited, it does not prove one exists.
- [Verified Fact] A hand-edit of `capability_authority` in the config file is audited at the next start (`record_authority_changes`); a hand-edit of another decision flag is visible only in the CONFIG_LOADED config hash (S23-DEV-03).
- [Verified Fact] The Stage 12 spec names the headers' purpose (BEH-SEC-09, SEC-07: CSP default-src 'self', nosniff) and Stage 15 design note D-06 lists the five headers; the exact values were asserted by no test before STG23.
- [Assumption] The values built in INC-08 (D-06) are the intended contract; no client has set different ones (confirm: Dinesh Naik).

## Evidence References
Tests and mutants listed in the table; `docs/23-human-control/evidence/header-values.json`, `authority-switch-audit.json`, `l3-flip-log.json`, `error-registry-check.json`, `exit-code-uniqueness.json`, `schema-validation.json`, `hub-mutation-s23.json`.

## Assumptions
- A-23-03 The header values built in INC-08 (design note D-06) are the intended contract.
- A-23-04 A reference string is an acceptable proof of an approval for the hub's purposes (confirm: Dinesh Naik).

## Unknowns
- U-23-03 Whether `approval_ref` should be checked against an approval register (none exists in the repo).

## Unresolved Issues
- Hand-edited non-authority flags are not individually audited (S23-DEV-03); decision for Dinesh.

## Residual Risks
- A bad reference passes the rule (RR-HC-1, Medium).
- A new decision flag added later is not covered until it is added to `DECISION_FLAGS`; STG23 S10 compares the `flags` command's list with `DECISION_FLAGS`, and the catalogue / registry tests do not detect a flag that was never registered.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
