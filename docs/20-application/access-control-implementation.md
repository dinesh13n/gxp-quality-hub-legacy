---
stage: "20 — Application & Services Engineering"
artifact: "access-control-implementation.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/zone_h.py", "hub/gate/service.py", "hub/policy/gate.py", "hub/security/authz.py", "hub/gate/actions.py", "hub/security/settings.py (zone_h.holders ships [])", "docs/20-application/evidence/mutation-gate.json", "docs/20-application/evidence/static-checks-*.json", "tests/hub/test_tst_gate_01_22_disposition_gate.py", "tests/hub/test_tst_hub_stg20_structure.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. zone_h.holders ships EMPTY (OD-S12-06 accepted open); every holder below is synthetic test data. Nothing in Stage 20 changes a shipped default.**

## Summary
The Zone H holder rule is now written once (`hub/security/zone_h.py`, DW-06, S16-D04 closed) and used by the gate service, the INC-04 policy gate and the route authorizer, each keeping its own error class and audit fields (behaviour pinned by TST-GATE, TST-POL, TST-SEC, INC-05 suites - green in targeted runs). Withdrawal is a Zone H action (ZH-10) through the single choke point. The producer and the observation run as host-operator / system actors and decide nothing.

## Findings
| Control | Implementation | Evidence | Tag |
|---|---|---|---|
| One holder rule | `zone_h.refusal(principal, reauth_at, clock, zone_h, ...)`; first failing condition named; clock read only at the re-auth step (as before) | STG20 S20 (one AST occurrence), S21 (all reasons) | [Verified Fact] |
| Mutation of the rule is detected | H1S20 (non-holder accepted) KILLED by TST-GATE-21 | `evidence/mutation-gate.json` | [Verified Fact] |
| Shipped default refuses every Zone H action incl. withdrawal | holders [] -> E-GATE-NO-HOLDERS (HTTP 423) | STG20 S12; TST-GATE-02 | [Verified Fact] |
| Withdrawal needs human holder + fresh re-auth + authority_ref | choke point `ZoneHActions.execute` then `_Preapproved` one-shot check | STG20 S11/S12 | [Verified Fact] |
| No automated caller reaches Zone H | producer imports nothing from hub.gate; jobs AST test (TST-RUN) unchanged | STG20 S14; TST-RUN green | [Verified Fact] |
| Flag actions (override/dismiss/refuse) | reviewer / quality_lead / compliance, human only (unchanged); reason required | STG20 S15 | [Verified Fact] |
| Producer / observe actors | `rule-trace-producer` (kind rule) audited per trace; observe writes only a scratch store that is deleted | STG20 S14, S05 | [Verified Fact] |
| Layering | no domain module imports hub.web (4 -> 0) | STG20 S22; static checks | [Verified Fact] |
- [Inference] The gate service and the policy gate still name the re-auth failure differently (E-GATE-REAUTH-REQUIRED vs E-GATE-NOT-AUTHORISED) because tests pin both; the policy gate is used only by the plain INC-04 PolicyService, never by the choke point (DEV-34). Unifying the error class is a behaviour change left for DW-13 (Stage 23).

## Evidence References
As in the table.

## Assumptions
- A-20-AC-1 [Assumption] The `produce-traces` command is a host-operator command like `record-trace` (no HTTP route, no role check beyond host access); confirm: Engagement lead (Dinesh Naik), Stage 24.

## Unknowns
- U-20-AC-1 Real holder identities (SH roles) - unchanged Unknown.

## Unresolved Issues
- Error-class naming difference of the INC-04 local gate (above).

## Residual Risks
- RR-AC-1 Single human performs and approves (RR-DB-1) - unchanged (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
