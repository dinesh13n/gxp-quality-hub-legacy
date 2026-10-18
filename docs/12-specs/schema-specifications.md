---
stage: "12 — Spec-Driven Design"
artifact: "schema-specifications.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/11-data-context/data-contracts.md (DC-01..DC-16)", "docs/11-data-context/data-quality-rules.md", "docs/11-data-context/knowledge-model.md", "docs/12-specs/contracts/schemas/", "docs/12-specs/contracts/ddl/hub-schema-v0.1.sql", "data/legacy.sqlite3 (read-only, immutable)", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Logical schemas for the new hub store: 16 JSON Schema (draft-07) files with 13 valid and 16 invalid examples, an executed-and-tested logical DDL with immutability and Zone H triggers, the 15-code reason catalogue, canonical forms, and baseline conformance measured read-only (8,567/8,567 feed rows conform to the envelope and payload schemas).

## Findings
### SC-1 Machine-checkable artifacts delivered with this spec [Verified Fact: files exist and were self-tested in a throwaway sandbox]
| File (under `docs/12-specs/contracts/`) | Content | Self-test performed |
|---|---|---|
| `schemas/*.schema.json` (16 files, JSON Schema draft-07) | decision-event, evidence-record, policy-object, rule-set, rule-result, partner-feed-envelope, partner-feed-payload, raw-intake, intake-outcome, crosswalk-link, run-record, metric-definition, metric-value, audit-record, hub-config, error-envelope | each passes `Draft7Validator.check_schema`; 13 valid examples accepted, 17 invalid cases rejected (`examples/`) |
| `examples/*.valid-N.json`, `examples/invalid-cases.json` | positive and negative instances for the schemas above | as above |
| `ddl/hub-schema-v0.1.sql` | logical DDL for `hub.sqlite3`: tables, CHECK constraints, immutability triggers, Zone H trigger, `intake_current` view | executed on an in-memory SQLite 3.37.2 database: UPDATE/DELETE on event tables abort with `E-DEC-IMMUTABLE`/`E-INT-RAW-IMMUTABLE`; Zone H event types abort unless `actor_kind='human'` and `holder_check_ref` present; duplicate `(case_id, seq)` rejected; metric without tag, synthetic label mismatch, empty authority_ref, human link without reason and self-link all rejected |
| `openapi.yaml` | OpenAPI 3.0.3 text for the `/api/v2` surface (see api-contracts.md) | parsed with a YAML loader; every operationId unique |
No test touched `data/` or any repo database for write; the only repo-data access was read-only (`mode=ro&immutable=1`) to measure the conformance numbers in SC-4.

### SC-2 Logical entities (SCH- IDs)
| ID | Entity / table | Schema file | Key rules | Implements |
|---|---|---|---|---|
| SCH-DEC-EVENT | `decision_events` | decision-event | insert-only; `UNIQUE(case_id, seq)`; `to_state` required when `affects_state`; Zone H types need human + holder_check_ref; REOPEN -> to_state REOPENED with basis; CASE_CREATED has null from_state; per-case hash chain (`prev_hash` of first = 64 zeros) | FR-DEC-01..06 |
| SCH-EVIDENCE | `evidence_record` | evidence-record | kind in {document, intake_item, crosswalk_object, external_ref}; `access_level` default `restricted` | FR-DEC-04 |
| SCH-CASE-STATE | `case_state` (projection) | (derived; no file) | rebuildable from events; `last_seq`, `cycle` | FR-DEC-02 |
| SCH-POLICY | `policy_object`, `policy_events` | policy-object | immutable versions; CLOCK body validated; adopted needs `effective_from` and an owner other than `unassigned` | FR-POL-01..03 |
| SCH-RULE-SET | `rule_set`, `rule_row`, `active_ruleset` | rule-set, rule-result | as-found sets read_only; rows ordered; default rows flagged | FR-POL-04, FR-POL-06 |
| SCH-RAW-INTAKE | `raw_intake` | raw-intake | insert-only; `raw_bytes` verbatim; identity_key and content_hash sha256 | FR-INT-01 |
| SCH-INTAKE-OUTCOME | `intake_outcome`, view `intake_current` | intake-outcome | append-only; NOOP_DUPLICATE never counts and has no queue | FR-INT-02..06 |
| SCH-REASON | reason-code catalogue (SC-3) | intake-outcome (enum) | deterministic precedence | FR-INT-06 |
| SCH-CROSSWALK | `crosswalk_link`, `crosswalk_link_event` | crosswalk-link | human link needs reason; no self-link | FR-ID-01, FR-ID-02 |
| SCH-RUN-RECORD | `run_event` (+ derived record) | run-record | limit_reached implies checkpoint; ended jobs have ended_at | FR-RUN-02, FR-RUN-03 |
| SCH-METRIC-DEF | `metric_definition` | metric-definition | `involves_definition` implies tag | FR-MET-01, FR-MET-06 |
| SCH-METRIC-VALUE | `metric_value` | metric-value | synthetic origin implies label 'synthetic, unvalidated'; null needs reason | FR-MET-01, PNFR-20 |
| SCH-AUDIT | `audit_log` | audit-record | hash chain; insert-only | FR-SEC-02 |
| SCH-GATE-CONFIG | configuration file | hub-config | fresh-install defaults: holders [], mode none, schedule disabled, closure behaviour `treat_label_CLOSED_as_closing` | FR-GATE-04/05, FR-RUN-01 |
| SCH-ERROR | error envelope | error-envelope | `code` matches `^E-[A-Z]+(-[A-Z0-9]+)+$` | all |

### SC-3 Reason-code catalogue (SCH-REASON)
| Code | Class | Queue | Trigger (stage) | Legacy counterpart / baseline count |
|---|---|---|---|---|
| UNSUPPORTED_REVISION | QUARANTINE | quarantine_invalid | `schema_rev` not in {1.0, 1.1, 2.0} (L1) | legacy REJECTED 'schema/key validation'; 224 rows |
| INVALID_JSON | QUARANTINE | quarantine_invalid | payload not a JSON object (L2) | 0 of 8,567 |
| MISSING_ENVELOPE_FIELD | QUARANTINE | quarantine_invalid | required envelope field absent (L1) | 0 observed |
| UNKNOWN_RECORD_KIND | QUARANTINE | quarantine_invalid | not in {OOS_RESULT, DEVIATION, CAPA_UPDATE} (L1) | 0 observed |
| MISSING_PAYLOAD_FIELD | QUARANTINE | quarantine_invalid | `object_type`, `state` or `source_version` absent (L2) | 0 observed |
| CONTRACT_VIOLATION | QUARANTINE (only when binding = enforce) | quarantine_invalid | declared contract check fails (L3) | partner_feeds 8,567 if enforced |
| REVISED_CONFLICT | QUARANTINE | revision_review | same identity_key, different content_hash | 0 in shipped data (FND-INT-1) |
| UNPARSABLE_AMOUNT | QUARANTINE | quarantine_invalid | amount/quantity not a decimal | vendor CSV blank 10 of 2,400 |
| NO_BUSINESS_KEY | EXCEPTION | unmatched | `business_key` absent | 210 rows (DQ-01) |
| AMBIGUOUS_MATCH | EXCEPTION | ambiguous_match | >1 entity for a registered key | none expected |
| UNMATCHED_REF | EXCEPTION | unmatched | no entity for `ref_id` | 8,394 rows (DQ-06) |
| NEGATIVE_VALUE | FLAG | flagged_value | decimal < 0 | feed quantity negatives present; vendor 11 of 2,400 (legacy REJECTED) |
| UNKNOWN_UNIT | FLAG | flagged_value | unit outside {lb, kg, hour, each, percent, ppm} | 0 in partner feeds; `pct` appears in batch tables (DQ-09) |
| UNKNOWN_CURRENCY | FLAG | flagged_value | not in {USD, GBP, INR, JPY, EUR} | 0 observed |
| IDENTIFIER_PATTERN | FLAG | flagged_value | `GXP-########` mismatch | 2,400 of 2,400 vendor ids (`GXP--`) |
`NOOP_DUPLICATE` and `CONFLICT_RESOLVED` (human resolution of a REVISED_CONFLICT; carries `resolution`, `resolution_reason`, `resolved_by`, no queue) are outcomes, not reasons. Outcome mapping: no reasons -> VALIDATED; FLAG-class only -> VALIDATED_WITH_FLAGS (queue flagged_value); EXCEPTION-class -> EXCEPTION; QUARANTINE-class -> QUARANTINED. Counts marked 'observed 0' are [Verified Fact] for the synthetic data only.

### SC-4 Baseline conformance measured in this stage (read-only) [Verified Fact]
| Check | Result |
|---|---|
| `partner-feed-envelope` schema over 8,567 `partner_feeds` rows | 8,567 valid (the 224 `unsupported` rows are valid envelopes and are quarantined by the revision rule) |
| `partner-feed-payload` schema (closed unit and currency sets, object_type set) over 8,567 payloads | 8,567 valid |
| `source-contract-v1.json` required keys over `source_messages` (15), `partner_feeds` (8,567), `gateway_inbox` (1) | 15, 0, 0 conform |
| natural-key duplicate groups | 67 groups, 67 pairs identical |

### SC-5 Canonical forms (normative)
- **Timestamps**: ISO-8601 UTC, `Z` or `+00:00` accepted on input, stored as `YYYY-MM-DDTHH:MM:SS[.ffffff]Z`.
- **Hashing**: `sha256` over canonical JSON (`json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)`, UTF-8); event hash input = canonical record without the `hash` field, concatenated after `prev_hash`.
- **Decimal**: money and quantities as decimal strings in JSON (`"622826.44"`), never JSON floats; arithmetic with `decimal.Decimal`.
- **Identifiers**: case `C[0-9]{8}`, batch `BT[0-9]{8}`; others registered in the key registry (F05).
- **Unicode**: NFC + trim before key comparison; UTF-8 everywhere (DQ-22).
- **Retention**: no schema has a delete path (hold-all).

## Evidence References
DDL and schemas were validated in a throwaway interpreter session (no repo data written). Schema generator script lives outside the repo ($HOME/fde_sbx/s12/gen_schemas.py) and is reproducible from the committed JSON files.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-SCH-1 Closed unit/currency/object_type sets are the synthetic observed sets; real feeds may differ (flag-class codes, not rejection).
- A-12-SCH-2 `actor_kind` for service principals in decision events is `system`, preserving DC-10's three-value enum.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-SCH-1 Whether the target store will be SQLite (ADR-004 option B) or PostgreSQL; the DDL is SQLite-dialect and the schemas are store-neutral.

## Unresolved Issues
- DC-03 in Stage 11 names (partner, feed_id/business_key) as the re-delivery key; this stage replaces it with the natural key (OD-S12-17). A Stage 11 v0.2 addendum is needed; Stage 11 was not edited.

## Residual Risks
- DDL is logical v0.1; Stage 14/15 must add migrations and indexes after measurement.
- Triggers can be dropped by a DBA; hash chain is the compensating control.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
