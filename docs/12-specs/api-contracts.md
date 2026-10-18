---
stage: "12 — Spec-Driven Design"
artifact: "api-contracts.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/adrs/ADR-014-api-and-ui-surface.md", "docs/10-architecture/adrs/ADR-013-authn-authz.md", "docs/07-repo-assessment/baseline-behaviour.md (BB-02)", "docs/12-specs/contracts/openapi.yaml", "docs/12-specs/contracts/schemas/", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

API contract for the new /api/v2 surface: 48 operations (40 R1 / 8 R2) with roles, request/response shapes, error codes and requirement trace, plus conventions (idempotency, concurrency, paging, correlation) and the single Zone H choke point (OP-GATE-02) with payloads for all ten actions. Machine form: contracts/openapi.yaml (OpenAPI 3.0.3) referencing 16 JSON Schemas.

## Findings
### API-1 Conventions [Inference: design from ADR-014; Assumption where marked]
| Topic | Contract |
|---|---|
| Surface | New versioned surface `/api/v2/*` on a new process (default `127.0.0.1:8081`; legacy `PORT` 8080 [Assumption]). Legacy `/api/*` (GET-only, POST/PUT/DELETE -> 501) is **not changed** (FR-CO-01, CT-04, CT-16). The new surface never exposes a route that mutates legacy tables. |
| Media | `application/json; charset=utf-8` request and response; HTML pages (queue, pack, trace, policy views) are separate server-rendered routes under `/ui/*` using the same service calls (ADR-014). |
| Auth | Cookie session (`hub_session`, HttpOnly, SameSite=Strict) or `Authorization: Bearer <token>` for service principals. Every route except `/healthz` and `OP-SEC-01` requires authentication (BEH-SEC-01). Writes from a browser need `X-Hub-Request: 1` and a CSRF token. |
| Authorisation | Role letters in the table: reviewer, quality_lead, compliance, finance_read, integration, dispositioner. Zone H actions additionally need the holder list and re-authentication (F02). Matrix in security-spec.md. |
| Identifiers | `case_id` `C########`; event/raw/link ids are server-generated opaque strings (ULID-like, lexicographically time-ordered) [Assumption]. |
| Time | UTC ISO-8601 with `Z`. Client `occurred_at` accepted only where the operation says so. |
| Idempotency | `Idempotency-Key` header (<= 128 chars) on every POST that creates a record; same key + same canonical body returns the original response (HTTP 200 with header `Idempotent-Replay: true`); different body -> E-DEC-IDEMPOTENCY-MISMATCH (422). |
| Concurrency | `expected_seq` in bodies for case-scoped writes (E-DEC-SEQ-CONFLICT, 409). |
| Pagination | `limit` (default 50, max 100, larger values are clamped, as in the legacy API) and opaque `cursor`; responses carry `next` (null at end). Deterministic default order stated per operation. |
| Errors | Single envelope `{"error":{"code","message","correlation_id","details","retryable"}}` (schemas/error-envelope.schema.json). Codes, HTTP status and retry semantics: error-handling-spec.md. |
| Correlation | Client may send `X-Correlation-Id`; server generates one if absent and returns it on every response and in every log/audit record (observability-spec.md). |
| Untrusted text | Any field derived from external text is returned in a wrapper `{"text": "...", "trust": "untrusted"}` where it appears in free-text positions, and HTML views escape it (BEH-INT-09). |
| Compatibility | Additive changes only within `v2`; removed or changed fields require `v3`. Contract tests (Stage 21) pin the OpenAPI file. |
| No generation | No endpoint returns generated prose other than template-rendered explanations (OP-REV-02) (FR-CO-04). |

### API-2 Operation register (48 operations; machine form: `contracts/openapi.yaml`)
| Op ID | Method and path | Roles | Purpose | Request | Response | Error codes |
|---|---|---|---|---|---|---|
| OP-DEC-01 | POST `/api/v2/cases/{case_id}/transitions` | reviewer,quality_lead,compliance | Append a state-changing decision event (BEH-DEC-01..10). With close_exception the call is Zone H: use OP-GATE-02 ZH-04. | TransitionRequest | decision-event | E-DEC-IMMUTABLE, E-DEC-TIME-ORDER, E-DEC-REOPEN-EXPLICIT, E-DEC-EVIDENCE-REQUIRED, E-DEC-EVIDENCE-UNRESOLVED, E-DEC-SEQ-CONFLICT, E-DEC-IDEMPOTENCY-MISMATCH, E-DEC-NOOP, E-DEC-CASE-NOT-FOUND, E-DEC-FIELD-TOO-LONG, E-GATE-NOT-AUTHORISED |
| OP-DEC-02 | GET `/api/v2/cases/{case_id}/events` | reviewer,quality_lead,compliance,dispositioner | List events of a case in seq order (cursor paging, limit<=100). | - | EventPage | E-DEC-CASE-NOT-FOUND |
| OP-DEC-03 | GET `/api/v2/cases/{case_id}/state` | reviewer,quality_lead,compliance,dispositioner | Current state or state at ?as_of=<ISO UTC>. | - | CaseStateView | E-DEC-CASE-NOT-FOUND, E-DEC-NOT-YET-EXISTS |
| OP-DEC-04 | GET `/api/v2/events/{event_id}` | reviewer,quality_lead,compliance,dispositioner | One event with resolved evidence and source (denied evidence redacted). | - | EventWithEvidence | E-DEC-CASE-NOT-FOUND |
| OP-DEC-05 | POST `/api/v2/cases/{case_id}/facts` | reviewer,quality_lead,compliance | Record FACT_OPS_CLOSED or FACT_EVIDENCE_COMPLETE (FACT_RECEIVED is written at case creation/import). | FactRequest | decision-event | E-DEC-TIME-ORDER, E-DEC-SEQ-CONFLICT, E-DEC-CASE-NOT-FOUND |
| OP-DEC-06 | POST `/api/v2/cases/{case_id}/evidence` | reviewer,quality_lead,compliance | Attach an evidence record (EVIDENCE_ATTACHED event). | EvidenceRequest | evidence-record | E-DEC-CASE-NOT-FOUND, E-DEC-FIELD-TOO-LONG |
| OP-GATE-01 | GET `/api/v2/cases/{case_id}/evidence-pack` | dispositioner | Read-only evidence pack with pack_hash. | - | EvidencePack | E-DEC-CASE-NOT-FOUND, E-GATE-NO-HOLDERS |
| OP-GATE-02 | POST `/api/v2/zone-h/actions` | dispositioner | Single choke point for every Zone H action ZH-01..ZH-10. | ZoneHRequest | ZoneHResult | E-GATE-NOT-AUTHORISED, E-GATE-NO-HOLDERS, E-GATE-MODE-NONE, E-GATE-VALUES-UNSET, E-GATE-PACK-STALE, E-GATE-REAUTH-REQUIRED, E-GATE-UNKNOWN-ACTION, E-GATE-EXTREF-INVALID, E-POL-AUTHORITY-REQUIRED, E-POL-OVERLAP |
| OP-GATE-03 | GET `/api/v2/gate/status` | reviewer,quality_lead,compliance,dispositioner | Gate mode, values_set, holders_configured, available. | - | GateStatus | - |
| OP-GATE-04 | POST `/api/v2/flags/{flag_id}/overrides` | reviewer,quality_lead,compliance | Override, dismiss or refuse a rule-generated item (reason required). | OverrideRequest | OverrideResult | E-GATE-REASON-REQUIRED, E-REV-NOT-FOUND |
| OP-POL-01 | GET `/api/v2/policies` | reviewer,quality_lead,compliance,finance_read,dispositioner | List policy objects (filters kind, status). | - | PolicyPage | - |
| OP-POL-02 | POST `/api/v2/policies` | quality_lead,compliance | Create a CANDIDATE policy object or a new candidate version. Adoption/edit of adopted content is Zone H (OP-GATE-02). | PolicyCreateRequest | policy-object | E-POL-AUTHORITY-REQUIRED, E-POL-CLOCK-CALENDAR-REQUIRED, E-POL-OVERLAP |
| OP-POL-03 | GET `/api/v2/policies/{policy_id}/versions/{version}` | reviewer,quality_lead,compliance,finance_read,dispositioner | One policy version with change events. | - | policy-object | E-POL-NOT-FOUND |
| OP-POL-04 | GET `/api/v2/rulesets` | reviewer,quality_lead,compliance,dispositioner | List loaded rule sets and active pointers. | - | RuleSetPage | - |
| OP-POL-05 | GET `/api/v2/rulesets/{ruleset_id}/{version}` | reviewer,quality_lead,compliance,dispositioner | One rule set with rows. | - | rule-set | E-POL-NOT-FOUND |
| OP-POL-06 | POST `/api/v2/rules/evaluate` | reviewer,quality_lead,compliance,dispositioner | Pure rule evaluation (explicit ruleset_ref or active set). | EvaluateRequest | rule-result | E-POL-NO-ACTIVE-RULESET, E-POL-INPUT-INVALID, E-POL-UNKNOWN-FUNCTION, E-POL-NOT-FOUND |
| OP-POL-07 | GET `/api/v2/rules/divergence` | quality_lead,compliance | Divergence report across loaded rule sets (R2). | - | DivergenceReport | E-POL-NOT-FOUND |
| OP-POL-08 | GET `/api/v2/cases/{case_id}/clocks` | reviewer,quality_lead,compliance,dispositioner | Elapsed time under every configured clock; verdict only for adopted clocks. | - | ClockElapsed | E-DEC-CASE-NOT-FOUND |
| OP-INT-01 | POST `/api/v2/intake/items` | integration | Receive one item (raw stored, outcome appended). | IntakeRequest | IntakeReceipt | E-INT-ENVELOPE-INVALID, E-INT-URL-SCHEME-REFUSED |
| OP-INT-02 | GET `/api/v2/intake/items/{raw_id}` | reviewer,quality_lead,compliance,integration | Raw record, outcome history, contract_check. | - | IntakeItemView | E-INT-ITEM-NOT-FOUND |
| OP-INT-03 | POST `/api/v2/intake/conflicts/{raw_id}/resolve` | reviewer,quality_lead | Human resolution of a REVISED_CONFLICT (accept_revision | keep_original | reject_both). | ConflictResolution | IntakeItemView | E-INT-ITEM-NOT-FOUND, E-INT-RESOLUTION-REASON-REQUIRED, E-INT-CONFLICT-ALREADY-RESOLVED |
| OP-INT-04 | GET `/api/v2/intake/sources/{source}/delays` | quality_lead,compliance | Delay/missing/revised per source (R2). | - | DelayReport | E-INT-ITEM-NOT-FOUND |
| OP-ID-01 | GET `/api/v2/crosswalk/lookup` | reviewer,quality_lead,compliance,dispositioner | Direct links for an identifier (?id=&id_type=). | - | LinkList | E-ID-AMBIGUOUS-TYPE, E-ID-NOT-FOUND |
| OP-ID-02 | POST `/api/v2/crosswalk/links` | reviewer,quality_lead,compliance | Create a human link (registered pair, reason required). | LinkRequest | crosswalk-link | E-ID-LINK-EXISTS, E-ID-PAIR-NOT-REGISTERED, E-ID-SELF-LINK, E-ID-REASON-REQUIRED |
| OP-ID-03 | POST `/api/v2/crosswalk/links/{link_id}/retract` | reviewer,quality_lead,compliance | Retract a link (event, reason required). | RetractRequest | crosswalk-link | E-ID-LINK-NOT-FOUND, E-ID-REASON-REQUIRED |
| OP-ID-04 | GET `/api/v2/crosswalk/view` | reviewer,quality_lead,compliance,dispositioner | Joined read-only view of the connected set (R2). | - | JoinedView | E-ID-AMBIGUOUS-TYPE, E-ID-NOT-FOUND |
| OP-ID-05 | GET `/api/v2/crosswalk/findings` | quality_lead,compliance | Consistency findings (R2). | - | FindingPage | - |
| OP-RUN-01 | POST `/api/v2/runs` | quality_lead,compliance,integration | Manual trigger of a job (closed catalogue). | RunRequest | run-record | E-RUN-UNKNOWN-JOB, E-RUN-ALREADY-RUNNING, E-RUN-SCHEDULE-DISABLED, E-RUN-CHECKPOINT-INVALID |
| OP-RUN-02 | GET `/api/v2/runs` | reviewer,quality_lead,compliance,integration | List run records. | - | RunPage | - |
| OP-RUN-03 | GET `/api/v2/runs/{run_id}` | reviewer,quality_lead,compliance,integration | One run record with events. | - | run-record | E-RUN-UNKNOWN-JOB |
| OP-MET-01 | GET `/api/v2/metrics/time-to-close` | quality_lead,compliance,finance_read | Median and p90 per configured clock (separate series). | - | metric-value | E-MET-DEFINITION-REQUIRED |
| OP-MET-02 | GET `/api/v2/metrics/month-end-total` | quality_lead,compliance,finance_read | Month-end total (cutoff_ts, denominator_ref, source required). | - | metric-value | E-MET-CUTOFF-REQUIRED, E-MET-UNPARSABLE-INPUT, E-MET-SOURCE-REFUSED |
| OP-MET-03 | GET `/api/v2/metrics/backlog` | quality_lead,compliance | Backlog ageing and unresolved-exception rate per site (definition tag required). | - | metric-value | E-MET-DEFINITION-REQUIRED |
| OP-MET-04 | GET `/api/v2/metrics/values/{value_id}/reproduce` | quality_lead,compliance | Recompute a stored metric value and diff. | - | ReproduceResult | E-MET-NOT-REPRODUCIBLE, E-MET-UNKNOWN-METRIC |
| OP-MET-05 | GET `/api/v2/metrics/case-cost` | quality_lead,compliance,finance_read | Placeholder: not available until cost input exists (R2). | - | error-envelope | E-MET-NOT-AVAILABLE |
| OP-MET-06 | GET `/api/v2/metrics/source-quality` | quality_lead,compliance | Unmatched rate and reconciliation delay per source (R2). | - | metric-value | - |
| OP-MET-07 | GET `/api/v2/metrics/registry` | reviewer,quality_lead,compliance,finance_read | Metric registry with documentation, tags, windows. | - | MetricRegistry | - |
| OP-MET-08 | POST `/api/v2/metrics/combine` | quality_lead,compliance,finance_read | Arithmetic/comparison of metric values; refuses mixed tags. | CombineRequest | metric-value | E-MET-TAG-MIX |
| OP-REV-01 | GET `/api/v2/queues/exceptions` | reviewer,quality_lead,compliance,integration | Exception queue view (filters queue, reason, source, min_age_hours). | - | ExceptionPage | - |
| OP-REV-02 | GET `/api/v2/cases/{case_id}/rule-trace` | reviewer,quality_lead,compliance,dispositioner | Template-generated rule-trace explanation. | - | RuleTraceView | E-DEC-CASE-NOT-FOUND, E-POL-NO-ACTIVE-RULESET |
| OP-REV-03 | GET `/api/v2/search` | reviewer,quality_lead,compliance,dispositioner | Keyword/field search over documents (fixed grammar; R2). | - | SearchPage | E-REV-QUERY-INVALID, E-REV-QUERY-TOO-LONG, E-REV-SEARCH-DISABLED |
| OP-REV-04 | POST `/api/v2/drafts` | reviewer,quality_lead,compliance | Create a template draft owned by the author (R2, Could). | DraftRequest | DraftView | E-REV-TEMPLATE-INVALID |
| OP-SEC-01 | POST `/api/v2/auth/login` | public | Login (rate-limited, lockout). | LoginRequest | SessionInfo | E-AUTH-BAD-CREDENTIALS, E-AUTH-LOCKED |
| OP-SEC-02 | POST `/api/v2/auth/logout` | reviewer,quality_lead,compliance,finance_read,integration,dispositioner | Logout. | - | Empty | E-AUTH-UNAUTHENTICATED |
| OP-SEC-03 | GET `/api/v2/audit/records` | quality_lead,compliance | Read audit records (cursor). | - | AuditPage | - |
| OP-SEC-04 | POST `/api/v2/audit/verify` | quality_lead,compliance | Verify the audit chain against the anchor. | - | AuditVerifyResult | E-SEC-AUDIT-TAMPER-DETECTED |
| OP-SEC-05 | POST `/api/v2/auth/reauth` | dispositioner | Step-up re-authentication, returns short-lived reauth_token. | ReauthRequest | ReauthToken | E-AUTH-BAD-CREDENTIALS, E-AUTH-LOCKED |
| OP-SYS-01 | GET `/healthz` | public | Liveness only; no data. | - | Health | - |

### API-3 Operation-to-requirement trace (for Stage 13)
| Op ID | Implements | Release |
|---|---|---|
| OP-DEC-01 | FR-DEC-01,FR-DEC-03,FR-DEC-05 | R1 |
| OP-DEC-02 | FR-DEC-01,FR-DEC-02 | R1 |
| OP-DEC-03 | FR-DEC-02 | R1 |
| OP-DEC-04 | FR-DEC-04 | R1 |
| OP-DEC-05 | FR-DEC-06 | R1 |
| OP-DEC-06 | FR-DEC-04,FR-DEC-05 | R1 |
| OP-GATE-01 | FR-GATE-02 | R1 |
| OP-GATE-02 | FR-GATE-01,FR-GATE-03,FR-GATE-04,FR-GATE-05 | R1 |
| OP-GATE-03 | FR-GATE-04,FR-GATE-05 | R1 |
| OP-GATE-04 | FR-GATE-06 | R1 |
| OP-POL-01 | FR-POL-01 | R1 |
| OP-POL-02 | FR-POL-01,FR-POL-02,FR-POL-03 | R1 |
| OP-POL-03 | FR-POL-01,FR-POL-03 | R1 |
| OP-POL-04 | FR-POL-04 | R1 |
| OP-POL-05 | FR-POL-04 | R1 |
| OP-POL-06 | FR-POL-04,FR-POL-06 | R1 |
| OP-POL-07 | FR-POL-05 | R2 |
| OP-POL-08 | FR-POL-02,FR-DEC-06 | R1 |
| OP-INT-01 | FR-INT-01,FR-INT-02,FR-INT-04 | R1 |
| OP-INT-02 | FR-INT-01,FR-INT-06 | R1 |
| OP-INT-03 | FR-INT-03 | R1 |
| OP-INT-04 | FR-INT-08 | R2 |
| OP-ID-01 | FR-ID-01 | R1 |
| OP-ID-02 | FR-ID-01,FR-ID-02 | R1 |
| OP-ID-03 | FR-ID-01 | R1 |
| OP-ID-04 | FR-ID-04 | R2 |
| OP-ID-05 | FR-ID-03 | R2 |
| OP-RUN-01 | FR-RUN-01,FR-RUN-02,FR-RUN-03 | R1 |
| OP-RUN-02 | FR-RUN-02 | R1 |
| OP-RUN-03 | FR-RUN-02 | R1 |
| OP-MET-01 | FR-MET-03 | R1 |
| OP-MET-02 | FR-MET-04 | R1 |
| OP-MET-03 | FR-MET-05 | R1 |
| OP-MET-04 | FR-MET-06 | R1 |
| OP-MET-05 | FR-MET-08 | R2 |
| OP-MET-06 | FR-MET-07 | R2 |
| OP-MET-07 | FR-MET-01,FR-MET-06 | R1 |
| OP-MET-08 | FR-MET-02 | R1 |
| OP-REV-01 | FR-REV-02 | R1 |
| OP-REV-02 | FR-REV-01 | R1 |
| OP-REV-03 | FR-REV-03 | R2 |
| OP-REV-04 | FR-REV-04 | R2 |
| OP-SEC-01 | FR-SEC-01 | R1 |
| OP-SEC-02 | FR-SEC-01 | R1 |
| OP-SEC-03 | FR-SEC-02 | R1 |
| OP-SEC-04 | FR-SEC-02 | R1 |
| OP-SEC-05 | FR-GATE-03 | R1 |
| OP-SYS-01 | FR-SEC-01 | R1 |

### API-4 Zone H action payloads (`OP-GATE-02`, `ZoneHRequest.payload`)
| Action | Payload fields | Extra checks |
|---|---|---|
| ZH-01 BATCH_DISPOSITION | mode `event`: `decision` in `disposition.values`, `basis`, `evidence_refs[]`; mode `external_ref`: `system`, `reference`, `uri?`, `decided_at`, `decided_by_declared` | `pack_hash` current; mode not `none` |
| ZH-02 QA_RELEASE | as ZH-01 | as ZH-01 |
| ZH-03 ESIGNATURE_RECORD | `signed_object_ref`, `meaning` (free text, Untrusted), `signer_declared` | records that a human acted; not a cryptographic or legal signature |
| ZH-04 CLOSE_EXCEPTION | `to_state`, `basis`, `close_exception {authority, reason}` | produces a CLOSE_EXCEPTION decision event with `exception = true` |
| ZH-05 POLICY_ADOPT | `policy_ref`, `target_status` in {adopted, accepted-open}, `effective_from`, `reason` | no overlap (E-POL-OVERLAP) |
| ZH-06 RULESET_ACTIVATE | `function`, `ruleset_ref` | set must contain the function |
| ZH-07 EXCEPTION_RULE_ACCEPT | `exception_rule_ref`, `reason` | rule must exist as candidate |
| ZH-08 DISPOSITION_MODE_CHANGE | `mode`, `values[]`, `closure_unconfigured_behaviour?` | old and new values recorded |
| ZH-09 SCHEDULE_ENABLE | `enabled` boolean | OD-S12-10 |
| ZH-10 POLICY_CHANGE | `policy_ref` or `rule_row_ref`, `new_value`, `contract_binding?` | `authority_ref` non-empty |
Every action returns `ZoneHResult` or an error from the table above; rejected attempts are audited (BEH-GATE-07).

### API-5 Shapes (informal; strict JSON Schema for file-backed shapes is in `contracts/schemas/`)
| Shape | Kind | Fields (type) | Required |
|---|---|---|---|
| TransitionRequest | req | to_state: enum case_status; event_type: STATUS_CHANGE|REOPEN; basis: string<=2000; evidence_refs: array<ev_id>; expected_seq: integer; occurred_at: ISO UTC (optional) | to_state, event_type, basis, expected_seq |
| FactRequest | req | fact_type: FACT_OPS_CLOSED|FACT_EVIDENCE_COMPLETE; occurred_at: ISO UTC (optional); basis: string; expected_seq: integer | fact_type, expected_seq |
| EvidenceRequest | req | kind: document|intake_item|crosswalk_object|external_ref; source: string; source_ref: string; source_hash: string (optional); access_level: engineering|quality|operations|restricted | kind, source, source_ref, access_level |
| ZoneHRequest | req | action: ZH-01..ZH-10; case_id: string (ZH-01..04); payload: object by action (decision, basis, evidence_refs, external reference, policy ref, mode, values, schedule flag...); pack_hash: sha256 (ZH-01..03); authority_ref: string non-empty; reauth_token: string from OP-SEC-05 | action, authority_ref, reauth_token |
| OverrideRequest | req | action: override|dismiss|refuse; reason: string non-empty; replacement: any (optional) | action, reason |
| PolicyCreateRequest | req | policy_id: string; kind: DEFINITION|CLOCK|CLOSURE|CONSISTENCY|CUTOFF; name: string; definition_tag: string; body: object (kind-specific); owner: string|unassigned; authority_ref: string non-empty | policy_id, kind, name, body, authority_ref |
| EvaluateRequest | req | function: PRIORITY|MANUAL_REVIEW|AMOUNT_LIMIT|SHIFT_FLAG; ruleset_ref: ruleset_id@version (optional); inputs: object | function, inputs |
| IntakeRequest | req | source: partner_feed|gateway|source_messages|vendor_csv; envelope: object per partner-feed-envelope (or source equivalent); idempotency_key: string | source, envelope |
| ConflictResolution | req | resolution: accept_revision|keep_original|reject_both; reason: string non-empty | resolution, reason |
| LinkRequest | req | from_type: string; from_id: string; to_type: string; to_id: string; reason: string non-empty | from_type, from_id, to_type, to_id, reason |
| RetractRequest | req | reason: string non-empty | reason |
| RunRequest | req | job: enum job catalogue; trigger: manual; batch_size: integer (optional); until_empty: boolean | job |
| CombineRequest | req | values: array<value_id>; op: sum|ratio|difference|compare | values, op |
| DraftRequest | req | template_id: string; fields: object | template_id |
| LoginRequest | req | username: string; password: string | username, password |
| ReauthRequest | req | password: string | password |
| EventPage | resp | items: array<decision-event>; next: cursor|null | items |
| CaseStateView | resp | case_id: string; state: enum; as_of: ISO UTC; cycle: integer; last_seq: integer | case_id, state, as_of |
| EventWithEvidence | resp | event: decision-event; evidence: array<evidence-record|{ev_id,access:denied}|{ev_id,unresolvable:true}> | event, evidence |
| EvidencePack | resp | case: object; history: array<decision-event>; linked_objects: object by type incl. 'none found'; evidence: array; rule_traces: array<rule-result>; open_findings: array; overrides: array; policy_versions: object; active_rulesets: object; pack_hash: sha256 | case, history, linked_objects, evidence, rule_traces, pack_hash |
| ZoneHResult | resp | action: ZH-xx; event_ref: string; mode_at_write: event|external_ref|null; audit_seq: integer | action, event_ref, audit_seq |
| GateStatus | resp | mode: none|event|external_ref; values_set: boolean; holders_configured: integer; available: boolean | mode, values_set, holders_configured, available |
| OverrideResult | resp | event_id: string; flag_id: string; original_output_retained: true | event_id, flag_id |
| PolicyPage | resp | items: array<policy-object>; next: cursor|null | items |
| RuleSetPage | resp | items: array<{ruleset_id,version,name,origin,read_only,functions}>; active: object function->ruleset | items, active |
| DivergenceReport | resp | compared_sets: array; inputs: integer; divergent: array<{input,outputs,traces}> | compared_sets, divergent |
| ClockElapsed | resp | case_id: string; clocks: array<{policy_ref,status,elapsed_hours,verdict}> | case_id, clocks |
| IntakeReceipt | resp | raw_id: string; outcome: enum; primary_reason: enum|null; queue: enum|null; contract_check: pass|fail|not_bound | raw_id, outcome |
| IntakeItemView | resp | raw: raw-intake; outcomes: array<intake-outcome>; conflicts_with: array | raw, outcomes |
| DelayReport | resp | source: string; items: array<{raw_id,delay_hours,flag}>; summary: object | source, items |
| LinkList | resp | id: string; id_type: string; links: array<crosswalk-link> | id, links |
| JoinedView | resp | entities: array<{type,id,access}>; links: array; truncated: boolean; total: integer | entities, truncated |
| FindingPage | resp | items: array<{rule_ref,object_refs,detected_at,policy_version}> | items |
| RunPage | resp | items: array<run-record>; next: cursor|null | items |
| ReproduceResult | resp | value_id: string; equal: boolean; diff: object|null | value_id, equal |
| MetricRegistry | resp | items: array<metric-definition> | items |
| ExceptionPage | resp | items: array<{raw_id,primary_reason,all_reasons,queue,source,receipt_time,age_hours,matched_case,flag_id}>; next: cursor|null; total: integer | items, total |
| RuleTraceView | resp | case_id: string; explanations: array<{function,ruleset_ref,text,defaulted,flag_id}> | case_id, explanations |
| SearchPage | resp | engine: fts5|fallback; items: array<hit>; total: integer (permitted rows only); next: cursor|null | engine, items, total |
| DraftView | resp | draft_id: string; template_id: string; fields: object; owner: string | draft_id |
| SessionInfo | resp | user: string; roles: array; expires_idle_at: ISO UTC; expires_abs_at: ISO UTC; csrf_token: string | user, roles |
| Empty | resp | (empty) | - |
| AuditPage | resp | items: array<audit-record>; next: cursor|null | items |
| AuditVerifyResult | resp | ok: boolean; checked: integer; first_broken_seq: integer|null; failure_kind: altered|missing|reordered|head_mismatch|null | ok, checked |
| ReauthToken | resp | reauth_token: string; expires_in_seconds: integer | reauth_token |
| Health | resp | status: ok | status |

### API-6 Legacy coexistence endpoints (unchanged, preserved) [Verified Fact: docs/07-repo-assessment/baseline-behaviour.md BB-02]
`GET /api/cases`, `/api/cases/<id>`, `/api/metrics`, `/api/incidents`, `/api/domain/*`, `/api/partners/*` keep their as-found behaviour (pagination clamp <= 100, 400/404/501 behaviour) until cut-over under ADR-003 and an approved deviation; the golden harness (F10) compares them. No `/api/v2` route proxies to them.

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-API-1 Port 8081, ULID-like ids and the 128-char idempotency key limit are conventions chosen here.
- A-12-API-2 The case-creation entry path is not specified: R1 brings cases in by backfill (CASE_IMPORTED); a creation operation is not defined because no workflow exists in the repo or PRD (OD-S12-19).

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-API-1 Consumers of the legacy API are unknown (TD register), so v2 cannot be validated against real clients.

## Unresolved Issues
- Informal response shapes (API-5) need strict JSON Schema at Stage 13/15; request shapes for the file-backed entities are strict.

## Residual Risks
- Hand-rolled stdlib router (ADR-014) may drift from OpenAPI; contract tests (Stage 21) must pin it.
- A single Zone H endpoint concentrates risk by design; AC-GATE-09/11/12 target it.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
