---
stage: "12 — Spec-Driven Design"
artifact: "event-contracts.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/11-data-context/data-contracts.md (DC-04, DC-10, DC-11, DC-15)", "docs/10-architecture/adrs/ADR-004-data-store-and-event-model.md", "docs/10-architecture/adrs/ADR-005-audit-trail-tamper-evidence.md", "docs/07-repo-assessment/baseline-behaviour.md (BB-03)", "docs/12-specs/contracts/ddl/hub-schema-v0.1.sql", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Event contracts for the append-only streams (decision, policy/config, intake, crosswalk, run, audit): 15 decision events, 12 policy/config events, intake/crosswalk/run events, 12 audit action groups, transactional exactly-once semantics, and the rule that inbound external events (incl. gateway qa_disposition and feed state DISPOSITIONED) are data only. No outbound events.

## Findings
### EV-1 Eventing model [Inference: ADR-004/005/010/016; Verified Fact: no event infrastructure exists in the repo]
- Events are **persisted rows in append-only tables**, not messages on a bus. There is no broker and no outbound publication (component rule 7, FR-CO-04, ADR-015). Consumers read the tables or are called in-process inside the same transaction.
- **Delivery**: a state change, its event row, its projection update and its audit record are written in one SQLite transaction (exactly once). If any part fails the whole write aborts (BEH-DEC-11, SBR-SEC-02). A crash leaves no partial event.
- **Ordering**: per-case total order by `seq` (decision events); per-run order by `run_seq`; per-item order by `outcome_seq`; global order of audit by `audit_seq`. No cross-stream ordering is promised other than `occurred_at`/`recorded_at`.
- **Idempotency**: record-creating calls take an `Idempotency-Key` (api-contracts API-1); intake is idempotent by (`identity_key`, `content_hash`); jobs are idempotent on `(raw_id, stage)`.
- **Schema evolution**: every event carries its schema version through the table's schema file version (`contracts/schemas/*.schema.json` `$id`); additive fields only; a changed meaning requires a new `event_type`, never a redefinition. Old events are never rewritten (hold-all).
- **Projections** (`case_state`, `intake_current`, exception queues, metric inputs) are derived, rebuildable and verified (`verify-projection`).

### EV-2 Decision events (stream `decision_events`, producer C3/C5, schema `decision-event`)
| ID | event_type | Trigger | Required beyond common fields | Zone | Consumers | Implements |
|---|---|---|---|---|---|---|
| EV-DEC-01 | CASE_CREATED | case created through a defined creation path (OD-S12-19) | `from_state = null`, `to_state` = creation state | D | projection, metrics | FR-DEC-02 |
| EV-DEC-02 | CASE_IMPORTED | legacy backfill (C11) | `basis = "legacy snapshot"`, `actor_kind = system`; marker `LEGACY_UNEVIDENCED_REOPEN` in payload where applicable | D | projection | FR-DEC-02, FR-CO-01 |
| EV-DEC-03 | STATUS_CHANGE | OP-DEC-01 | `from_state`, `to_state`, `basis`, `evidence_refs` (closing check) | D (closing without evidence = H) | projection, metrics, pack | FR-DEC-01, FR-DEC-05 |
| EV-DEC-04 | REOPEN | OP-DEC-01 | `to_state = REOPENED`, non-empty `basis`; `cycle` + 1 | D | projection, metrics | FR-DEC-03 |
| EV-DEC-05 | EVIDENCE_ATTACHED | OP-DEC-06 | `payload.ev_id`; `affects_state = false` | D | pack, retrieval | FR-DEC-04 |
| EV-DEC-06 | FACT_RECEIVED | case creation/import | `occurred_at` = receipt; `cycle` | D | metrics | FR-DEC-06 |
| EV-DEC-07 | FACT_OPS_CLOSED | OP-DEC-05 | `cycle`; `affects_state = false` | D | metrics | FR-DEC-06 |
| EV-DEC-08 | FACT_EVIDENCE_COMPLETE | OP-DEC-05 | `cycle`; `affects_state = false` | D | metrics | FR-DEC-06 |
| EV-DEC-09 | CLOSE_EXCEPTION | ZH-04 | `exception = true`, `payload.authority`, `payload.reason`, human + `holder_check_ref` | **H** | exception report, pack | FR-DEC-05, FR-GATE-03 |
| EV-DEC-10 | DISPOSITION_RECORDED | ZH-01 (mode `event`) | `mode_at_write = event`, `payload.decision`, `evidence_refs`, `payload.pack_hash`, human + `holder_check_ref` | **H** | pack, metrics | FR-GATE-05 |
| EV-DEC-11 | DISPOSITION_REFERENCED | ZH-01 (mode `external_ref`) | `mode_at_write = external_ref`, `payload {system, reference, uri?, decided_at, decided_by_declared, verified:false}` | **H** | pack | FR-GATE-05 |
| EV-DEC-12 | QA_RELEASE_RECORDED | ZH-02 | as EV-DEC-10 or 11 per mode | **H** | pack | FR-GATE-03 |
| EV-DEC-13 | ESIGNATURE_RECORDED | ZH-03 | `payload {signed_object_ref, meaning, signer_declared}`; not a cryptographic signature | **H** | pack | FR-GATE-03 |
| EV-DEC-14 | OVERRIDE_RECORDED | OP-GATE-04 | `payload {flag_id, action, reason, replacement?, original_ref}` | D | pack, metrics (override rate) | FR-GATE-06 |
| EV-DEC-15 | CORRECTION | any authorised role | `payload.corrects_event_id`, `basis`; the corrected event stays unchanged | D | pack | FR-DEC-01 |

### EV-3 Policy and configuration events (stream `policy_events`, producer C4/C5, no schema file; fields in DDL)
| ID | event_type | Trigger | Required | Zone |
|---|---|---|---|---|
| EV-POL-01 | POLICY_VERSION_CREATED | OP-POL-02 (candidate) | `new_value`, `authority_ref` | D (candidate), H if it edits adopted content (ZH-10) |
| EV-POL-02 | POLICY_ADOPTED | ZH-05 | `old_value`, `new_value`, `authority_ref`, `holder_check_ref` | **H** |
| EV-POL-03 | POLICY_ACCEPTED_OPEN | ZH-05 | reason in `new_value`, dated | **H** |
| EV-POL-04 | POLICY_WITHDRAWN | ZH-05/ZH-10 | `authority_ref` | **H** |
| EV-POL-05 | RULE_ROW_CHANGED | ZH-10 | old/new row | **H** |
| EV-POL-06 | RULESET_ACTIVATED | ZH-06 | function, ruleset_ref | **H** |
| EV-POL-07 | RULESET_DEACTIVATED | ZH-06 | function | **H** |
| EV-POL-08 | EXCEPTION_RULE_ACCEPTED | ZH-07 | rule ref | **H** |
| EV-POL-09 | CLOSURE_ACTIVATED | ZH-05 | closure policy ref | **H** |
| EV-POL-10 | DISPOSITION_MODE_CHANGED | ZH-08 | old/new mode and values | **H** |
| EV-POL-11 | SCHEDULE_CHANGED | ZH-09 | old/new flag | **H** |
| EV-POL-12 | CONTRACT_BINDING_CHANGED | ZH-10 | source, old/new mode | **H** |
All carry `actor`, `occurred_at`, non-empty `authority_ref` (FR-POL-03).

### EV-4 Intake, crosswalk and run events
| ID | Stream | Event | Trigger | Notes |
|---|---|---|---|---|
| EV-INT-01 | raw_intake | item received | every delivery | one row per delivery; `duplicate_of` set for identical re-delivery |
| EV-INT-02 | intake_outcome | VALIDATED / VALIDATED_WITH_FLAGS / EXCEPTION / QUARANTINED / NOOP_DUPLICATE | classification | `outcome_seq` increments on each re-processing; history kept |
| EV-INT-03 | intake_outcome | CONFLICT_RESOLVED | OP-INT-03 | human; `resolution`, `resolution_reason`, `resolved_by`; no queue after |
| EV-ID-01 | crosswalk_link_event | LINK_CREATED_RULE | matcher | exact registered key only |
| EV-ID-02 | crosswalk_link_event | LINK_CREATED_HUMAN | OP-ID-02 | reason required |
| EV-ID-03 | crosswalk_link_event | LINK_RETRACTED | OP-ID-03 | reason required |
| EV-RUN-01 | run_event | RUN_STARTED | job start | written before any work |
| EV-RUN-02 | run_event | RUN_CHECKPOINT | per batch | `{receipt_time, raw_id}` |
| EV-RUN-03 | run_event | RUN_FINISHED / RUN_FAILED | job end | counts, errors, backlog |
| EV-RUN-04 | run_event | RUN_ABANDONED | next start finds stale heartbeat | |
| EV-RUN-05 | run_event | RUN_REFUSED | schedule disabled, already running, unknown job | no work performed |

### EV-5 Audit actions (stream `audit_log`, schema `audit-record`, producer C2; every write path calls it)
| ID | `action` | Outcome values | Notes |
|---|---|---|---|
| EV-AUD-01 | LOGIN_SUCCESS / LOGIN_FAILED / LOCKOUT / LOGOUT / REAUTH | success, denied | no credentials in `details` |
| EV-AUD-02 | AUTHZ_DENIED | denied | route/operation, role, object_ref |
| EV-AUD-03 | DECISION_APPENDED | success | event_id, event hash |
| EV-AUD-04 | ZONE_H_ACCEPTED / ZONE_H_REJECTED | success, denied | action code, reason for rejection |
| EV-AUD-05 | POLICY_CHANGED | success | policy_event ids |
| EV-AUD-06 | CONFIG_LOADED | success | SHA-256 of configuration (holders, mode, schedule, bindings) |
| EV-AUD-07 | LINK_CHANGED | success | link_id |
| EV-AUD-08 | RUN_TRIGGERED / RUN_REFUSED | success, denied | job, trigger |
| EV-AUD-09 | C3_READ / EXPORT | success | non-empty `reason` |
| EV-AUD-10 | AUDIT_VERIFIED | success, error | result summary |
| EV-AUD-11 | INTAKE_RESOLUTION | success | raw_id, resolution |
| EV-AUD-12 | OVERRIDE | success | flag_id |

### EV-6 Inbound external events (consumed as data only; never as instructions)
| Source | Event vocabulary (verified) | Handling |
|---|---|---|
| Partner feed (DC-01) | `record_kind` OOS_RESULT 2,923 / DEVIATION 2,817 / CAPA_UPDATE 2,827; payload `state` {QA_REVIEW, REOPENED, INVESTIGATING, OPEN, DISPOSITIONED} | stored raw; `state` kept as `source_state`; creates no decision event |
| Gateway (DC-04) | `event_type` {batch_created, lab_test, deviation_review, qa_disposition}; `source_system` {mes, lims, qms}; 0.9 schema cadence every 19th event (BB-03) | stored raw/outcome; `qa_disposition` is NOT a disposition: it can never create EV-DEC-10..12 |
| Source messages (DC contract v1) | `{ref, status, schema_version}` | contract check; `status` is source text |
| Enterprise evidence events (DC-08) | kinds and `arrival_time >= event_time` check | read-only adapter; late-arrival flag |
No outbound events exist. A future Teams or notification integration (memory areas) is out of scope and would need its own ADR and egress decision (HAR-09/10).

### EV-7 Contract tests (Stage 13/21 hooks)
1. Every row of each stream validates against its schema file (schemas/*.schema.json).
2. Hash-chain continuity per case and for audit.
3. Zone H event types never appear with `actor_kind <> 'human'` (trigger + test).
4. For every state-changing API call exactly one decision event and one audit record exist with the same `correlation_id`.
5. Replaying all events into an empty projection reproduces `case_state` exactly.

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-EV-1 In-process synchronous consumers are sufficient at 125 cases; any broker is deferred (ADR-004 trigger conditions).

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-EV-1 Whether any downstream system needs outbound events (none identified; Teams integration is a separate memory-listed plan, not in the PRD).

## Unresolved Issues
- CASE_CREATED creation path is open (OD-S12-19).

## Residual Risks
- Single-transaction writes serialise all writers on one SQLite file (H-14 contention SUPPORTED by config only, not measured).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
