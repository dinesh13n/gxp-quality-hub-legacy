---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "human-override-policy.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/review/service.py", "hub/gate/flags.py", "tests/hub/test_tst_gate_01_22_disposition_gate.py TST-GATE-18/19/21", "hub/control/cli.py", "hub/core/errors.py", "docs/12-specs/business-rules.md SBR-GATE-02", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
An override is a human setting aside what the system produced. The policy: a person may override **rule output and recommendations**; a person may not override **the controls themselves** from inside the product (there is no switch that disables the Zone H gate, TST-GATE-21). Every override keeps the original output, needs a reason, and is audited. The system can be stopped or reverted by a human at any time, without a reason requirement for the safe direction.

## Findings
### Policy
| ID | Override | Who | Condition | Effect | Kept / audited | Test |
|---|---|---|---|---|---|---|
| OV-01 | Override a rule flag (set the outcome aside) | reviewer, quality_lead, compliance | reason required (E-GATE-REASON-REQUIRED / E-SEC-REASON-REQUIRED) | flag status `overridden`; the rule output is NOT changed | original output kept; audit record with reason | TST-GATE-18/19 |
| OV-02 | Dismiss or refuse a flag | same | reason required | `dismissed` / `refused` | same | TST-GATE-20 |
| OV-03 | Resolve a revised-conflict intake item | reviewer, quality_lead | reason required (E-INT-RESOLUTION-REASON-REQUIRED); one resolution only (E-INT-CONFLICT-ALREADY-RESOLVED) | accept_revision / keep_original / reject_both; raw item untouched (E-INT-RAW-IMMUTABLE) | event + audit | TST-INT |
| OV-04 | Retract a crosswalk link | reviewer, quality_lead, compliance | reason required (E-ID-REASON-REQUIRED) | retract event; link history kept | event + audit | TST-ID |
| OV-05 | Return an authority to `shadow` (L3) | host operator | none (the safe direction needs no approval); `--reason` recorded | `capability_authority.<cap>` = shadow; idempotent | CONFIG_CHANGED `rollback: L3` | STG23 S13 |
| OV-06 | Stop the hub / the schedule | host operator; ZH-09 for the schedule | none for `hub.kill`; ZH-09 needs a holder | commands refused with E-HUB-KILLED (exit 3) / schedule OFF | audit | TST-CO, TST-RUN |
| OV-07 | Correct a recorded Zone H event | holder, by a **new** event | the original is never edited | superseding event ([Inference]: only the mode-change history is tested) | both kept | TST-GATE-08 |

### What cannot be overridden
- [Verified Fact] The holder check, the `authority_ref` and the re-authentication cannot be switched off by configuration (TST-GATE-21 inspects every switch).
- [Verified Fact] The audit log cannot be edited or deleted through the product (insert-only, hash-chained; tamper -> E-SEC-AUDIT-TAMPER-DETECTED).
- [Verified Fact] A non-loopback bind cannot be enabled even by an approved exposure setting (DW-15).
- [Verified Fact] A model cannot be added by configuration (no model client exists; the deny-list and tripwire fail the build).

### Findings
- [Verified Fact] Overrides never change the rule output, so before/after comparison stays possible (SBR / AC-GATE-18).
- [Inference] OV-05 and OV-06 are operator actions with no second person; a reason is recorded for OV-05 but not verified.
- [Unknown] Whether a second person must confirm an override of a GxP-relevant flag (DR-10, GD-05 open).
- [Assumption] Override reasons are free text and Untrusted; they are displayed escaped and never interpreted (confirm: Stage 24).

## Evidence References
Tests listed; `evidence/l3-flip-log.json`; Stage 0B HAR-12.

## Assumptions
- A-23-08 Free-text reasons are sufficient for the capstone; a reason code list is not required.

## Unknowns
- U-23-04 Second-reviewer rule. U-23-09 Retention of override records (NFR-10 policy unknown, DR-24).

## Unresolved Issues
- None blocking.

## Residual Risks
- A reason can be a single character string that satisfies 'non-empty'; the hub does not judge adequacy (RR-HC-3, Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
