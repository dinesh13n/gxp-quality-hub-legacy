---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "inc05-design-notes.md"
version: "v0.1"
date: "2026-10-19"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-05 decision record (C3, F01, ADR-004/005), identity crosswalk (C7, F05, ADR-009), shared Zone H gate eligibility (F02 part, DEV-34), 125-case legacy backfill (DM-1), M003"
evidence_sources: ["docs/12-specs/features/f01-decision-evidence-record.md", "docs/12-specs/features/f02-human-disposition-gate.md", "docs/12-specs/features/f05-identity-crosswalk.md", "docs/12-specs/contracts/ddl/hub-schema-v0.1.sql", "docs/14-transformation/schema-migration-plan.md (M003, DM-1, DM-5)", "docs/14-transformation/transformation-backlog.md (TB-13, TB-14)", "docs/14-transformation/transformation-gates.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-12, OD-15, OD-16, OD-17)", "docs/15-modernization/inc04-design-notes.md"]
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved.**

## Summary
Design decisions for INC-05, written before the code so a dead session leaves the reasoning on the branch. INC-05 adds
the append-only decision and evidence record (C3), the explicit identity crosswalk (C7), the shared Zone H eligibility
gate (the part of F02 that INC-04 needed, DEV-34) and the backfill of the 125 shipped cases (OD-09). No model call, no
new dependency (ADR-002, OD-08). `zone_h.holders` stays empty in shipped config (OD-17): nothing can be adopted,
activated or excepted until Dinesh names real holders; tests use synthetic holders labelled as such.

## Findings
| # | Decision | Reason | Tag |
|---|---|---|---|
| D-01 | New packages `hub/gate/`, `hub/decision/`, `hub/crosswalk/` (add-only; every existing hub file stays byte-identical, TST-CO-05 c). Own CLI `python -m hub.decision`. | Add-only rule; same pattern as INC-03/04. | [Verified Fact] rule |
| D-02 | **M003 is applied by `hub.decision.schema`** (own insert-only table `decision_schema_migrations`, backup-before-migrate, requires M001 + M002), not by `hub.store.migrate`. | Same constraint as INC-04 D-02: a file in `hub/store/forward/` would join `migrate.known_versions()` and break INC-03 S01; `migrate.py` and that test are frozen. Third migration location (RTD-37 grows). | [Verified Fact] constraint; [Inference] solution |
| D-03 | Tables = DDL v0.1 verbatim (`decision_events` with its three triggers, `evidence_record`, `case_state`, `crosswalk_link` + triggers, `crosswalk_link_event`) plus addenda: gapless-seq trigger, insert-only triggers on `evidence_record` and `crosswalk_link_event`, `decision_idempotency` (BEH-DEC-09). | AC-DEC-01/02/03, OD-S12-09 hold-all. | [Inference] |
| D-04 | Per-case hash chain: `hash = sha256(prev_hash || canonical(event fields without hash))`, first `prev_hash` = 64 zeros (SCH-DEC-EVENT). `verify_chain` recomputes. | Spec text. | [Verified Fact] |
| D-05 | Every append is ONE transaction with the projection row (`case_state`) and its hash-chained audit record (`audit.change`): audit failure rolls the event back (AC-DEC-24). | BEH-DEC-11. | [Verified Fact] |
| D-06 | **Shared gate**: `hub.gate.service.GateService.require_holder` implements BEH-GATE-01/05/07 for the closed list ZH-01..ZH-10 (human + role dispositioner + in `zone_h.holders` + re-auth window; empty list -> E-GATE-NO-HOLDERS; unauthenticated -> E-AUTH-UNAUTHENTICATED; every attempt audited as `ZONE_H_ATTEMPT`). The re-auth window failure raises the specified E-GATE-REAUTH-REQUIRED (the INC-04 copy raised E-GATE-NOT-AUTHORISED). `hub.gate.policy_binding.GatedPolicyService` is `PolicyService` with `_zone_h` routed to the shared gate. | OD-17 / DEV-34. The physical removal of `hub/policy/gate.py` and the one-line import in `hub/policy/service.py` is a NON-ADD edit, forbidden by the add-only rule (TST-CO-05 c) - recorded as a deviation and RTD. | [Verified Fact] constraint; [Inference] solution |
| D-07 | Modes, evidence pack, pack_hash, override and the HTTP layer of F02 stay in INC-08 (test map: TST-GATE-* = INC-08). | Scope = test map. | [Verified Fact] |
| D-08 | Closing-state set (SBR-DEC-03): an adopted/accepted-open CLOSURE policy effective now wins (`body.closing_states`); else `closure.unconfigured_behaviour` (default `treat_label_CLOSED_as_closing`, fail closed; `none` flags `closure_check = not_configured`). Evidence sufficiency is never judged (OD-S12-07): structural presence of >= 1 existing `ev_id` only. | OD-17 -> Stage 14 defaults. | [Verified Fact] |
| D-09 | `close_exception` is the Zone H action ZH-04: the state change is stored as a `CLOSE_EXCEPTION` event (`affects_state = 1`, `exception = 1`, `closure_check = exception`, `payload {authority, reason}`, `holder_check_ref = audit:<seq>`). The DB trigger rejects it unless `actor_kind = human` and `holder_check_ref` present. | EV-DEC-09, AC-DEC-17/18. | [Inference] (that the exception event IS the closing transition) |
| D-10 | Case creation path: R1 = legacy backfill only (OD-S12-19 default). `create_case` exists for the AC tests but is refused (`E-DEC-CREATION-DISABLED`, addendum) unless `case_creation.enabled` is true (default false). | transformation-gates INC-05 row. | [Verified Fact] |
| D-11 | Imported legacy cases: `CASE_IMPORTED` (seq 1, `to_state` = snapshot status, `basis = "legacy snapshot"`, `actor_kind = system`) + `FACT_RECEIVED` (seq 2, `occurred_at = cases.created_at`, proxy A-12-F01-1). Both `occurred_at` = `created_at` (keeps the time-order rule); `recorded_at` = import time; payload carries `source_db_sha256`, legacy `version`, and for the 8 REOPENED cases `LEGACY_UNEVIDENCED_REOPEN`. Legacy `events` rows (145) are not imported (no from/to state; "no history is invented"). | BEH-DEC-02, SBR-DEC-05, DM-1. | [Inference] |
| D-12 | Backfill = ONE transaction, ONE audit record (all 125 cases or none); idempotent on (source_db_sha256, case_id): second run writes nothing but a NOOP audit record. Reads only the hash-gated read-only snapshot adapter (AD-01); never opens working-tree `data/`. | DM-1, rollback L1+L2. | [Verified Fact] |
| D-13 | Crosswalk: registry as data (`hub/crosswalk/registry.json`: LT-01..LT-06, id patterns, registered pairs); rule links only by exact key after Unicode NFC + trim; no similarity code (deny-list test forbids difflib/fuzzy/levenshtein/similarity imports in `hub/crosswalk`). A link that was retracted is never silently re-created by a rule re-run (counted `skipped_retracted`). | BEH-ID-02/03, ADR-009. | [Verified Fact] spec; [Inference] retraction rule |
| D-14 | Human link/retract: roles reviewer, quality_lead, compliance and a human principal; service principals -> E-AUTH-FORBIDDEN + `AUTHZ_DENIED` audit. Existence of the linked entities is not verified by the hub (no entity tables in the hub, DM-5); ids must match the registered pattern of their type. | BEH-ID-04; DDL has no entity table. | [Inference] |
| D-15 | Evidence access (AC-DEC-13): level `restricted` is readable by quality_lead, compliance, dispositioner; levels engineering / quality / operations by every OP-DEC-04 role. The role-to-level matrix does not exist in the specs (FR-SEC-03 matrix unknown) - **Assumption A-15-05-1**. | AC-DEC-13 needs a rule. | [Assumption] |
| D-16 | Test isolation for the egress suite: TST-CO-12 e (frozen) re-runs every other test module under the egress guard and is at ~133 s of the 180 s device cap. INC-05 modules skip themselves when `HUB_EGRESS_INNER` is set, and one new module (`test_inc05_egress_guard.py`) runs only the INC-05 modules under the guard through `_driver.py -k ... --egress-guard`. | OD-17 / RTD-44: split instead of growing group C. | [Verified Fact] |

## Evidence References
Header. Test map: 39 INC-05 rows = TST-DEC-01..21, 23..28 (27) + TST-ID-01..12 (12). TST-DEC-22 (concurrent POST) is INC-08 (needs HTTP); TST-ID-13..17 are R2 (INC-09).

## Assumptions
- A-15-05-1 [Assumption] Evidence access matrix of D-15. Confirm: Engagement lead (Dinesh Naik).
- A-15-05-2 [Assumption] The CLOSE_EXCEPTION event is itself the closing state change (D-09). Confirm: Engagement lead (Dinesh Naik).
- A-15-05-3 [Assumption] Identifier patterns observed in the shipped data are the registered id patterns (U-12-F05-2). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-15-05-1 Who may read which evidence level (FR-SEC-03).
- U-15-05-2 Whether imported cases should expose "state as of T" for T between `created_at` and the import time (the importer only knows the snapshot status).

## Unresolved Issues
- OD-S12-01/03/07/15/16 stay at their Stage 14 defaults (accepted on Dinesh's instruction, OD-12/OD-17).

## Residual Risks
- A DBA can drop the SQLite triggers; only the per-case hash chain and the audit chain detect it (ADR-005).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-19 | claude-fde-agent | INC-05 design notes. |
