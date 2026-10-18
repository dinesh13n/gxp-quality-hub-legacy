---
stage: "12 — Spec-Driven Design"
artifact: "features/f04-safe-intake-exceptions.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/partner_feeds.py", "app/gateway_bridge.py", "integration/source-contract-v1.json", "integration/source-gateway.json", "data/legacy.sqlite3 (read-only, immutable; tables partner_feeds, source_messages, gateway_inbox)", "docs/11-data-context/data-quality-rules.md", "docs/05-current-state/integration-landscape.md (IL-05..IL-09)", "docs/10-architecture/adrs/ADR-008-intake-pipeline.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Feature spec for non-destructive, idempotent, content-aware intake (CAP-04): 12 behaviours, 29 acceptance criteria for FR-INT-01..08. Adds four new read-only findings: the item identity key, the source-contract scope evidence, the observed unit/currency vocabularies, and the absence of a corrected-replay in shipped data.

## Findings
### F04-1 Scope and traceability [Verified Fact: requirement text and data counts; Inference: design]
Feature **F04 Safe Intake & Exception Handling** = CAP-04, component C6 (+ C11 read-only adapters), ADR-008 (append-only raw store, content-hash idempotency, quarantine), ADR-002 (Untrusted type), data contracts DC-01..DC-05, DC-11, quality rules DQ-01..DQ-06, DQ-09..DQ-11, DQ-19.

| Implements | FR-INT-01, FR-INT-02, FR-INT-03, FR-INT-04, FR-INT-05, FR-INT-06, FR-INT-07 (R1); FR-INT-08 (R2) |
|---|---|
| Also constrained by | PNFR-11, PNFR-13, PNFR-17, PNFR-14; BR-04, BR-05, BR-06; RC-5, RC-6, RC-7; CT-06..CT-09 |
| Open decisions | OD-S12-11 (scope of `integration/source-contract-v1.json`), OD-S12-17 (item identity key), OD-S12-13 (preserve vs fix) |
| Legacy evidence | `app/partner_feeds.py reconcile()` L60-71 overwrites `processing_status`, marks every REPLAY DUPLICATE without comparison, rejects quantity < 0 and unsupported/no-key rows (`UPDATE partner_feeds SET processing_status`); 8,567 feed rows (NEW 8,000, RETRY 500, REPLAY 67; schema_rev 1.0 2,609 / 1.1 2,659 / 2.0 3,075 / unsupported 224) |

### F04-2 New evidence found while specifying (read-only queries on `data/legacy.sqlite3`, `mode=ro&immutable=1`; baseline sha256 prefix c254649f57e2 unchanged)
| ID | Finding | Class |
|---|---|---|
| FND-INT-1 | The 67 REPLAY rows are all content-identical to an original row that shares the natural key `(partner, record_kind, ref_id, source_ts)`: 67/67 pairs, 0 differ. The shipped data therefore contains **no** corrected-replay (different content, same natural key) example; FR-INT-03 needs a synthetic fixture. | [Verified Fact] |
| FND-INT-2 | `business_key` is NOT an item identity: 2,407 business keys occur on 6,219 rows and 2,386 of those groups carry differing payloads (different partners, kinds, times). Using `(partner, business_key)` as the re-delivery key (DC-03 wording `feed_id/business_key`) would quarantine thousands of legitimate distinct events. The spec uses the natural key above (SBR-INT-01). | [Verified Fact] on counts; [Inference] on impact |
| FND-INT-3 | `integration/source-contract-v1.json` (required `ref`, `status`, `schema_version`) is satisfied by 15 of 15 `source_messages.body` payloads (source `external-feed`), by 0 of 8,567 `partner_feeds.raw_json` payloads (consistent with DQ-04) and by the single `gateway_inbox` payload only if it had those keys (it has `business_key, event_type, message_id, occurred_at, system`: 0 of 1). Stage 11's wording 'not met by any feed' holds for the partner feed and gateway but not for `source_messages`. | [Verified Fact] |
| FND-INT-4 | Observed vocabularies in partner payloads: `unit` {lb 1,494; kg 1,440; hour 1,413; each 1,413; percent 1,408; ppm 1,399}; `currency` {USD 1,843; GBP 1,722; INR 1,683; JPY 1,666; EUR 1,653}; `object_type` {BATCH, SAMPLE, MATERIAL}; payload `state` {QA_REVIEW, REOPENED, INVESTIGATING, OPEN, DISPOSITIONED} - a fifth status vocabulary. This closes the 'unit enumerated at Stage 12' item in DC-02. | [Verified Fact] |

### F04-3 Behaviours
| ID | Behaviour (binding once approved) | Implements |
|---|---|---|
| BEH-INT-01 | **Receive.** Every delivered item gets a new `raw_intake` row (SCH-RAW-INTAKE): `raw_id`, `source`, `source_key` (e.g. feed_id), `partner`, `schema_rev`, `receipt_time` (server UTC), `content_hash`, `identity_key`, `raw_bytes` verbatim, `run_id`. UPDATE/DELETE are rejected by trigger (E-INT-RAW-IMMUTABLE). Processing results go only to the separate append-only `intake_outcome` table (SCH-INTAKE-OUTCOME); the current outcome is the row with the highest `outcome_seq` per `raw_id`. Raw count always equals received count. The legacy `partner_feeds.processing_status` is never read as truth or written. | FR-INT-01, PNFR-11 |
| BEH-INT-02 | **Identity and hash.** `identity_key` = sha256 of canonical `[source, partner, record_kind, ref_id, source_ts]` (SBR-INT-01). `content_hash` = sha256 of the canonical form (UTF-8, JSON with sorted keys and no insignificant whitespace; for CSV the header-keyed row) of `{schema_rev, payload}`; transport fields (`feed_id`, `ingest_ts`, `processing_status`, `error_reason`) are excluded. | FR-INT-02, FR-INT-03 |
| BEH-INT-03 | **Identical re-delivery.** A new item whose `identity_key` and `content_hash` equal those of an already-received item gets a raw row (`duplicate_of = first raw_id`) and outcome `NOOP_DUPLICATE`, `counts_toward_totals = false`. Queues, queue ages, totals and metrics are computed excluding `NOOP_DUPLICATE`, so replaying changes none of them. | FR-INT-02 |
| BEH-INT-04 | **Changed re-delivery.** Same `identity_key`, different `content_hash`: outcome `QUARANTINED`, reason `REVISED_CONFLICT`, queue `revision_review`; both versions stay stored and linked (`conflicts_with`). It is never discarded and never auto-classified as duplicate. A human (reviewer or quality_lead) resolves it with `accept_revision`, `keep_original` or `reject_both` plus a reason; resolution is an event and does not change any case decision. | FR-INT-03 |
| BEH-INT-05 | **Validation, three layers.** L1 envelope (DC-01): required `feed_id, partner, schema_rev, source_ts (ISO-8601 UTC), ref_id, record_kind, raw_json`; `schema_rev` in {1.0, 1.1, 2.0} else `UNSUPPORTED_REVISION`; `record_kind` in {OOS_RESULT, DEVIATION, CAPA_UPDATE} else `UNKNOWN_RECORD_KIND`. L2 payload (DC-02): valid JSON object else `INVALID_JSON`; required `object_type, state, source_version` else `MISSING_PAYLOAD_FIELD`; `business_key` absent -> `NO_BUSINESS_KEY`; `quantity` numeric (Decimal) negative -> `NEGATIVE_VALUE`, non-numeric -> `UNPARSABLE_AMOUNT`; `unit` outside {lb, kg, hour, each, percent, ppm} -> `UNKNOWN_UNIT`; `currency` not ISO-4217 shaped (3 upper letters) or outside {USD, GBP, INR, JPY, EUR} -> `UNKNOWN_CURRENCY` (closed sets are Assumptions). L3 declared contract: see BEH-INT-06. Invalid items are stored in quarantine with a reason code, never merely counted. | FR-INT-04, FR-INT-06 |
| BEH-INT-06 | **Declared contract binding.** `contract_binding(source -> contract_file, mode)`, `mode` in {`enforce`, `record_only`}. Default for every source is `record_only` until OD-S12-11 is decided: the L3 check runs and its result (`contract_check` in {pass, fail, not_bound}, missing keys) is stored on the outcome, but a failure alone does not quarantine. With `mode = enforce` a failure gives `CONTRACT_VIOLATION` and quarantine. Changing a binding is Zone H-classified configuration (ZH-10). Expected effect of `enforce` on the baseline: partner_feeds 8,567/8,567 quarantined; source_messages 0/15; gateway_inbox 1/1. | FR-INT-04 |
| BEH-INT-07 | **Classification** is a pure deterministic function of (item, validation config version). Every non-clean outcome has one `primary_reason` chosen by the fixed precedence in SBR-INT-03 plus the full `all_reasons[]` and exactly one queue (reason-code catalogue in schema-specifications.md SCH-REASON). Same input and config give the same codes. No randomness, no model. | FR-INT-06, PNFR-17 |
| BEH-INT-08 | **Match** (after validation) via the crosswalk (F05): exact string equality of the item `ref_id` against the configured keys of core entities, in configured order. Exactly one hit -> `crosswalk_link(creator=rule)` created and the item shown to reviewers as matched; zero -> outcome reason `UNMATCHED_REF`, queue `unmatched`; more than one -> `AMBIGUOUS_MATCH`, queue `ambiguous_match`, candidates listed, **no link created**. No normalisation beyond Unicode NFC and trim; no similarity. Baseline expectation: 173 of 8,567 feed `ref_id` equal a `cases.id`; 8,394 unmatched (DQ-06). | FR-INT-05, FR-ID-02 |
| BEH-INT-09 | **Untrusted text.** All free-text fields (feed `notes`, document bodies, e-mail bodies, gateway/CSV payload text) are typed `Untrusted`. The type cannot be passed to any decision, status, priority, queue, approval or disposition parameter (static type-check test + runtime guard raising E-INT-UNTRUSTED-USE). Also payload fields such as `state`, `quality_flag`, `subtype` are stored as `source_*` attributes and never mapped to case status. Output is HTML-escaped, length-bounded for display and marked 'untrusted source text'. | FR-INT-07, PNFR-13 |
| BEH-INT-10 | **Adapters and backfill.** Legacy tables are read via C11 with `file:...?mode=ro`; backfill of the 8,567 feed rows into `raw_intake` is idempotent by `content_hash` + `identity_key`, uses `receipt_time = ingest_ts` as a proxy (Assumption A-12-F04-1) and never writes to legacy. | FR-INT-01, ADR-003 |
| BEH-INT-11 | **Gateway and file sources.** Gateway reads accept only `http`/`https` URLs resolving to loopback (rejecting `file:`, `ftp:` - DM-15), 5 s timeout, bounded retry (`gateway.retries`, default 3, exponential back-off); unreachable source is a run error, not a data outcome (F06). Invalid gateway events are stored in quarantine (DC-04). Vendor CSV is parsed by header names (never position), `amount` kept as text plus Decimal, unparsable -> `UNPARSABLE_AMOUNT` (never skipped), identifier pattern `GXP-########` mismatch (all 2,400 `GXP--`) -> flag `IDENTIFIER_PATTERN` with original preserved. | FR-INT-04, FR-INT-06 |
| BEH-INT-12 | **Delay, missing, revised (R2).** For each source the system computes `delay = receipt_time - source_ts` (negative values flagged `FUTURE_SOURCE_TS`; 2,234 of 8,567 rows have source_ts > ingest_ts today) and lists items by source and time without manual spreadsheet work. Thresholds are configuration (PNFR-03/04 are Assumptions). | FR-INT-08 |

### F04-4 Error cases
E-INT-RAW-IMMUTABLE, E-INT-ENVELOPE-INVALID, E-INT-UNTRUSTED-USE, E-INT-SOURCE-UNREACHABLE, E-INT-URL-SCHEME-REFUSED, E-INT-RESOLUTION-REASON-REQUIRED, E-INT-ITEM-NOT-FOUND, E-INT-CONFLICT-ALREADY-RESOLVED (error-handling-spec.md). Item-level problems are reason codes (SCH-REASON), not API errors.

### F04-5 Acceptance criteria
| ID | Given | When | Then | Implements | Kind |
|---|---|---|---|---|---|
| AC-INT-01 | a fixture of 100 valid items | the intake job runs twice | raw_intake has 200 rows (each delivery stored), original 100 raw rows are byte-unchanged, intake_outcome holds both runs' outcomes | FR-INT-01 | positive |
| AC-INT-02 | any raw_intake row | UPDATE or DELETE is attempted | rejected E-INT-RAW-IMMUTABLE | FR-INT-01 | negative |
| AC-INT-03 | the code base | searched in a test | no statement updates a status column of an intake table and the legacy `partner_feeds` is opened only `mode=ro` | FR-INT-01 | negative |
| AC-INT-04 | 100 processed items and a queue snapshot | the same 100 are re-delivered | queue size, queue ages, per-reason counts and all totals are identical before and after; 100 `NOOP_DUPLICATE` outcomes exist with `counts_toward_totals = false` | FR-INT-02, PNFR-11 | positive |
| AC-INT-05 | the 134 shipped rows forming 67 natural-key pairs | ingested | 67 pairs are classified one original + one `NOOP_DUPLICATE` (67/67), none quarantined | FR-INT-02 | positive |
| AC-INT-06 | the shipped rows sharing a business_key but different natural keys | ingested | none is classified duplicate or revised-conflict because of the shared business_key | FR-INT-02, SBR-INT-01 | negative |
| AC-INT-07 | a synthetic corrected-replay fixture (same identity_key, changed `quantity`) | ingested | outcome QUARANTINED `REVISED_CONFLICT`, queue revision_review, both versions retrievable and linked, not marked duplicate | FR-INT-03 | positive |
| AC-INT-08 | a quarantined conflict | a reviewer resolves `accept_revision` with a reason | resolution event stored, no case state changes; a resolution without reason gives E-INT-RESOLUTION-REASON-REQUIRED | FR-INT-03 | edge |
| AC-INT-09 | the 224 `unsupported` rows | ingested | 224 outcomes with `UNSUPPORTED_REVISION` in queue quarantine_invalid; quarantine rows = 224; raw rows = 224 | FR-INT-04, DQ-02 | positive |
| AC-INT-10 | items with invalid JSON, missing envelope field, unknown record_kind and missing payload field | ingested | each lands in quarantine with INVALID_JSON, MISSING_ENVELOPE_FIELD, UNKNOWN_RECORD_KIND, MISSING_PAYLOAD_FIELD; counts of reasons equal counts of quarantine rows | FR-INT-04 | negative |
| AC-INT-11 | the 210 shipped rows without `business_key` | ingested | 210 outcomes with NO_BUSINESS_KEY, queue unmatched, none linked | FR-INT-04, FR-INT-05, DQ-01 | positive |
| AC-INT-12 | binding for partner_feed = `record_only` (default) | the shipped 8,567 rows are ingested | every outcome carries `contract_check = fail` (8,567), none is quarantined by contract alone | FR-INT-04, BEH-INT-06 | edge |
| AC-INT-13 | binding for partner_feed = `enforce` | same input | 8,567 CONTRACT_VIOLATION quarantine outcomes (100%) and no item is dropped | FR-INT-04, BEH-INT-06 | edge |
| AC-INT-14 | binding for `external-feed` source_messages = `enforce` | the 15 shipped messages are ingested | 15 `contract_check = pass`, 0 quarantined | FR-INT-04, FND-INT-3 | positive |
| AC-INT-15 | a quantity of -4.942 | validated | flag NEGATIVE_VALUE, queue flagged_value, value kept verbatim (legacy rejected it: recorded as OD-S12-13 difference) | FR-INT-06, DQ-10 | edge |
| AC-INT-16 | units 'pct' and 'percent', currency 'XXX' and 'usd' | validated | `pct` -> UNKNOWN_UNIT; `percent` clean; 'XXX' and 'usd' -> UNKNOWN_CURRENCY; raw values preserved | FR-INT-04 | edge |
| AC-INT-17 | a feed `ref_id` equal to exactly one `cases.id` | matched | one crosswalk link with creator rule and key_used | FR-INT-05 | positive |
| AC-INT-18 | a `ref_id` equal to no case | matched | UNMATCHED_REF in queue unmatched, no link | FR-INT-05 | negative |
| AC-INT-19 | a `ref_id` equal to two entities under the configured keys | matched | AMBIGUOUS_MATCH with both candidates listed, no link created, item not shown as matched | FR-INT-05 | negative |
| AC-INT-20 | 1,000 randomly ordered fixture items (fixed seed) classified twice, in different orders | outputs compared | identical primary_reason, all_reasons and queue per item | FR-INT-06, PNFR-17 | positive |
| AC-INT-21 | an item failing three checks | classified | one primary reason by SBR-INT-03 precedence, `all_reasons` has all three, exactly one queue | FR-INT-06 | edge |
| AC-INT-22 | the 86 shipped feed rows with instruction-like notes plus the 22 document bodies and 44 regex-hit fixtures | processed end to end | zero events, status changes, priority/queue changes, approvals or dispositions result from any of them (compare full store before/after except raw/outcome rows) | FR-INT-07, PNFR-13 | negative |
| AC-INT-23 | code that tries to pass an `Untrusted` value into a decision parameter | the type check and runtime guard run | static check fails the build; runtime raises E-INT-UNTRUSTED-USE | FR-INT-07 | negative |
| AC-INT-24 | payload `state = 'DISPOSITIONED'` | ingested | stored as `source_state`; case state unchanged; no gate event | FR-INT-07, FR-GATE-01 | negative |
| AC-INT-25 | the gateway URL `file:///etc/passwd` or `ftp://x` | configured | refused E-INT-URL-SCHEME-REFUSED, no read | FR-INT-04, PNFR-08 | negative |
| AC-INT-26 | an unreachable gateway | the job runs | retries up to `gateway.retries`, then run record shows error SOURCE_UNREACHABLE; no item outcome fabricated | FR-INT-04, FR-RUN-02 | edge |
| AC-INT-27 | a vendor CSV with a blank amount and a negative amount | imported | blank -> UNPARSABLE_AMOUNT quarantined (not skipped), negative -> NEGATIVE_VALUE; totals use Decimal | FR-INT-04, FR-MET-04 | negative |
| AC-INT-28 | R2: a source with late items | the delay report runs | items listed per source with delay and no manual step; future `source_ts` flagged | FR-INT-08 | positive |
| AC-INT-29 | the backfill of the 8,567 legacy rows run twice | row counts compared | raw_intake count equals 8,567 after run 1 and run 2 adds 0 new content (idempotent by hash) while legacy file checksum is unchanged | FR-INT-01, BEH-INT-10 | positive |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-F04-1 Legacy `ingest_ts` is an acceptable proxy for receipt_time in backfill. Confirm: Engagement lead (Dinesh Naik).
- A-12-F04-2 Closed unit and currency sets are the observed sets (synthetic); real sets unknown.
- A-12-F04-3 Natural key (partner, record_kind, ref_id, source_ts) is the right item identity; supported only by the 67 replay pairs (OD-S12-17).

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-F04-1 Whether real partners ever send corrected replays (none in shipped data).
- U-12-F04-2 Human capacity for quarantine queues (volume unknown).
- U-12-F04-3 Intended scope of source-contract-v1.json (OD-S12-11).

## Unresolved Issues
- OD-S12-11 contract scope: default `record_only` is a safe interim, not a decision.
- OD-S12-17 identity key needs Dinesh confirmation; DC-03 text in Stage 11 should be amended in a Stage 11 v0.2 addendum (not edited here).

## Residual Risks
- A wrong identity key silently merges or splits events; AC-INT-05/06 pin it on shipped data only.
- Quarantine volume under `enforce` on partner feeds would be 100%.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
