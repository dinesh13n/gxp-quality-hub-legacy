---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "hitl-workflow.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/gate/actions.py", "hub/gate/service.py", "hub/security/zone_h.py", "hub/gate/reauth.py", "hub/gate/dispositions.py", "hub/review/service.py", "docs/12-specs/api-contracts.md OP-GATE-01..04", "docs/12-specs/business-rules.md SBR-GATE-02", "tests/hub/test_tst_gate_01_22_disposition_gate.py", "tests/hub/test_tst_hub_stg23_catalogue.py", "docs/23-human-control/autonomy-catalogue.json"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
Human-in-the-loop (HITL) is built for exactly the actions the system must never take alone: ZH-01..ZH-10, rule-output overrides, conflict resolution, crosswalk links and decision-flag changes. In each, the system prepares information and refuses; a named human acts; the act is an append-only event with an audit record. **The shipped configuration has no holder, so no Zone H action can complete today** (E-GATE-NO-HOLDERS); the workflow below has been run only with synthetic holders in tests.

## Findings
### H-1 Zone H action (ZH-01..ZH-10), the only path
1. [Verified Fact] The actor logs in as a **human** interactive session (service tokens, the scheduler identity and `integration`-role humans are refused: TST-GATE-09).
2. [Verified Fact] `GateService.require_holder` is called once, before the payload is read: unknown action -> E-GATE-UNKNOWN-ACTION; empty `zone_h.holders` -> E-GATE-NO-HOLDERS; role not `dispositioner` or not in `zone_h.holders` -> E-GATE-NOT-AUTHORISED; last step-up re-authentication older than `zone_h.reauth_window_seconds` (default 300, a Stage 12 proposal) -> E-GATE-REAUTH-REQUIRED. Every outcome is audited (ZONE_H_ATTEMPT, `holder_check_ref` = its audit_seq).
3. [Verified Fact] The request must carry a non-empty `authority_ref` (E-POL-AUTHORITY-REQUIRED) and a `reauth_token` from the latest step-up (E-GATE-REAUTH-REQUIRED); nothing else is trusted from the caller.
4. [Verified Fact] ZH-01..03 read the evidence pack first (`GET /api/v2/cases/{id}/evidence-pack`) and send its current `pack_hash` (stale: E-GATE-PACK-STALE). The pack never pre-selects a decision (TST-GATE-16). Mode `none` -> E-GATE-MODE-NONE; `event` needs `disposition.values` and a `decision` in them; `external_ref` stores a reference only (`verified = false`).
5. [Verified Fact] The event is written with actor kind `human` and `holder_check_ref`; a database trigger refuses a Zone H event without both (TST-GATE-12). The audit chain verifies afterwards.

### H-2 Reviewer work (not Zone H)
- [Verified Fact] Rule output is a flag with a template-rendered explanation (no generation). The reviewer may **override, dismiss or refuse** with a reason; the original output is kept (TST-GATE-18/19, `hub/review/service.py`).
- [Verified Fact] A revised-conflict intake item stays quarantined until a reviewer or quality lead resolves it (accept_revision / keep_original / reject_both) with a reason (OP-INT-03).
- [Verified Fact] Crosswalk links are created or retracted by a human with a reason (OP-ID-02/03).

### H-3 Decision-flag change (DW-17)
- [Verified Fact] A host operator runs `python -m hub.control set-flag --flag K --value V --approval-ref R --data-dir D`. Without a reference the command is refused (ConfigInvalid, exit 2) and nothing is written; with it the change is audited first and then the config file is replaced atomically. `flip-to-shadow` returns a capability to `shadow` without a reference (L3) and is idempotent.

### H-4 Refusal map (what the human sees)
| Situation | Code | HTTP / exit | Event written | Test |
|---|---|---|---|---|
| no holder configured | E-GATE-NO-HOLDERS | 423 | none | TST-GATE-02 |
| not a holder | E-GATE-NOT-AUTHORISED | 403 | none | TST-GATE-09, S41 |
| stale / missing re-auth | E-GATE-REAUTH-REQUIRED | 401 | none | TST-GATE-10, S41 |
| no `authority_ref` | E-POL-AUTHORITY-REQUIRED | 422 | none | S41 |
| mode none | E-GATE-MODE-NONE | 423 | none | TST-GATE-03 |
| stale pack | E-GATE-PACK-STALE | 409 | none | TST-GATE-17 |
| flag change without `approval_ref` | E-CFG-INVALID | exit 2 (clashes with two other meanings; documented, OD-29) | none | S11 |

### Findings
- [Verified Fact] Across ZH-01..ZH-10, a missing authority_ref, a wrong re-auth proof and a non-holder dispositioner are each refused and write nothing (STG23 S41, 30 requests, zero events).
- [Verified Fact] ZH-01, 02, 03, 07, 08, 09 each write exactly one event with a `holder_check_ref` that points at an accepted ZONE_H_ATTEMPT of that holder (S42).
- [Inference] The HITL design places a human at every regulated decision, but **who** that human is cannot be known by the hub (U-23-01); the two-person rule for GxP-relevant changes (DR-10) is open and not implemented.
- [Unknown] Review time, queue ownership and shift cover for real holders (no client data).

## Evidence References
Tests above; `evidence/zone-h-refusal-matrix.json`, `zone-h-success-matrix.json`, `authority-switch-audit.json`; `autonomy-catalogue.json`.

## Assumptions
- A-23-05 A 300-second re-authentication window is acceptable until Stage 24 confirms it.

## Unknowns
- U-23-01 Real holders (SH-15). U-23-04 Whether GxP-relevant changes need a second reviewer (DR-10, GD-05).

## Unresolved Issues
- No holder is configured; the workflow cannot complete in the shipped state by design.

## Residual Risks
- Single approver (Dinesh) for the engagement; no alternate (ES-09).
- A holder's session could be shared out of band; the hub ties the act to a login and a re-authentication, not to a person's identity.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
