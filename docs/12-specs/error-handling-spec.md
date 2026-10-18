---
stage: "12 — Spec-Driven Design"
artifact: "error-handling-spec.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/12-specs/features/*.md", "docs/10-architecture/adrs/ADR-014-api-and-ui-surface.md", "docs/07-repo-assessment/baseline-behaviour.md (BB-02)", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Error handling specification: 8 principles incl. fail-closed and deterministic check precedence, HTTP mapping, a registry of 82 error codes (every code referenced anywhere in the specs is defined), and 12 edge/failure-mode requirements.

## Findings
### ER-1 Principles [Inference: design]
1. **Fail closed.** Any doubt about identity, authorisation, Zone H eligibility, evidence or data integrity refuses the operation; nothing is partially applied (single transaction per write, SBR-SEC-02).
2. **One envelope.** Every HTTP error uses `{"error":{"code","message","correlation_id","details","retryable"}}` (schemas/error-envelope.schema.json). Messages are generic for authentication failures; `details` never contains secrets, stack traces, SQL or file paths.
3. **Deterministic precedence.** Checks run in this order and the first failure is returned: (1) transport/body size/malformed JSON `E-REQ-INVALID`; (2) authentication; (3) CSRF; (4) authorisation (RBAC); (5) Zone H eligibility (holders, mode, re-auth); (6) schema validation; (7) existence (404); (8) state/concurrency (409); (9) business rules (422). A refusal at steps 2-5 is audited.
4. **Item-level vs request-level.** Problems with an *item* inside an intake batch are reason codes on the outcome (SCH-REASON), never request failures; the request succeeds and reports per-item results.
5. **No silent failure.** Dropped, skipped or defaulted data always yields a visible marker: error, reason code, `defaulted`, `partial`, or `limit_reached`.
6. **Untrusted text never changes control flow.** Error `message` text is fixed per code; user-supplied text appears only inside `details`, escaped.
7. **Retry semantics.** `retryable = true` only when repeating the identical request can succeed without human action (409 seq conflict after re-read, run lock, DB busy). Non-retryable errors need a changed request or a human decision.
8. **Audit.** Errors in the 'audit = yes' column write an audit record (outcome `denied` or `error`) with the correlation id.

### ER-2 HTTP status mapping
400 malformed; 401 unauthenticated/expired; 403 forbidden / Zone H not authorised / CSRF; 404 not found; 409 state or concurrency conflict (including immutability and tamper); 422 business-rule or validation failure; 423 locked/unavailable by configuration (no holders, mode none, account locked); 500 internal; 501 not available in this release; 503 dependency busy or unreachable. Legacy routes keep their as-found codes (501 for writes, 400/404, 414).

### ER-3 Error registry (82 codes)
| Code | HTTP | Retryable | Audited | Feature | Meaning |
|---|---|---|---|---|---|
| E-REQ-INVALID | 400 | no | no | all | Malformed JSON, missing/ill-typed field, unknown field (details lists JSON pointers). |
| E-AUTH-UNAUTHENTICATED | 401 | no | yes | F09 | No/invalid credentials or session. |
| E-AUTH-BAD-CREDENTIALS | 401 | no | yes | F09 | Login or re-authentication failed (generic message). |
| E-AUTH-SESSION-EXPIRED | 401 | no | yes | F09 | Idle or absolute session timeout. |
| E-AUTH-LOCKED | 423 | yes (after lockout) | yes | F09 | Account locked after repeated failures. |
| E-AUTH-FORBIDDEN | 403 | no | yes | F09 | Authenticated but role lacks permission. |
| E-SEC-CSRF | 403 | no | yes | F09 | Missing/invalid CSRF token or custom header. |
| E-SEC-REASON-REQUIRED | 422 | no | yes | F09 | C3 read/export without reason. |
| E-SEC-EXPOSURE-NOT-APPROVED | n/a (CLI/CI) | no | yes | F09 | Start-up refused: non-loopback bind without approval/TLS (process exit 9). |
| E-SEC-AUDIT-WRITE-FAILED | 500 | yes | yes (best effort to stderr) | F09 | Audit append failed; the change was rolled back. |
| E-SEC-AUDIT-TAMPER-DETECTED | 409 | no | yes | F09 | verify-audit found a broken chain/anchor mismatch. |
| E-DEC-IMMUTABLE | 409 | no | yes | F01 | Attempt to modify/delete an immutable record (trigger abort). |
| E-DEC-CASE-NOT-FOUND | 404 | no | no | F01 | Unknown case id. |
| E-DEC-NOT-YET-EXISTS | 404 | no | no | F01 | as_of earlier than first event. |
| E-DEC-TIME-ORDER | 422 | no | no | F01 | occurred_at in the future or before the previous event. |
| E-DEC-REOPEN-EXPLICIT | 422 | no | no | F01 | Transition into REOPENED without a REOPEN event/basis. |
| E-DEC-EVIDENCE-REQUIRED | 422 | no | yes | F01 | Closing transition with neither evidence nor accepted exception. |
| E-DEC-EVIDENCE-UNRESOLVED | 422 | no | no | F01 | Evidence reference does not exist. |
| E-DEC-SEQ-CONFLICT | 409 | yes (re-read) | no | F01 | expected_seq mismatch. |
| E-DEC-IDEMPOTENCY-MISMATCH | 422 | no | no | F01 | Idempotency-Key reused with a different body. |
| E-DEC-NOOP | 422 | no | no | F01 | Same-state transition. |
| E-DEC-FIELD-TOO-LONG | 422 | no | no | F01 | Text field above limit. |
| E-GATE-NOT-AUTHORISED | 403 | no | yes | F02 | Zone H attempt by a non-human, non-holder or wrong role. |
| E-GATE-NO-HOLDERS | 423 | no | yes | F02 | Holder list empty; Zone H unavailable. |
| E-GATE-MODE-NONE | 423 | no | yes | F02 | disposition.mode = none. |
| E-GATE-VALUES-UNSET | 423 | no | yes | F02 | disposition.values empty in event mode. |
| E-GATE-PACK-STALE | 409 | yes (re-read pack) | yes | F02 | pack_hash no longer current. |
| E-GATE-REAUTH-REQUIRED | 401 | yes (after OP-SEC-05) | yes | F02 | Step-up window elapsed. |
| E-GATE-REASON-REQUIRED | 422 | no | no | F02 | Override without reason. |
| E-GATE-UNKNOWN-ACTION | 422 | no | yes | F02 | Action not in ZH-01..ZH-10. |
| E-GATE-EXTREF-INVALID | 422 | no | no | F02 | external_ref payload incomplete. |
| E-POL-NO-ACTIVE-RULESET | 409 | no | no | F03 | No active rule set and no explicit ruleset_ref. |
| E-POL-OVERLAP | 409 | no | no | F03 | Overlapping effective windows. |
| E-POL-AUTHORITY-REQUIRED | 422 | no | no | F03 | authority_ref empty. |
| E-POL-INPUT-INVALID | 422 | no | no | F03 | Non-numeric/NaN/null where a decimal is required. |
| E-POL-READONLY-SET | 409 | no | yes | F03 | Edit of an as-found rule set. |
| E-POL-UNKNOWN-FUNCTION | 422 | no | no | F03 | Function not in the catalogue. |
| E-POL-NOT-FOUND | 404 | no | no | F03 | Unknown policy/rule set/version. |
| E-POL-CLOCK-CALENDAR-REQUIRED | 422 | no | no | F03 | business_calendar without calendar_ref. |
| E-INT-RAW-IMMUTABLE | 409 | no | yes | F04 | Modification of raw/outcome rows. |
| E-INT-ENVELOPE-INVALID | 422 | no | no | F04 | Request envelope unusable (item-level problems are reason codes instead). |
| E-INT-UNTRUSTED-USE | 500 | no | yes | F04 | Untrusted value reached a decision parameter (programming error; the operation is aborted). |
| E-INT-SOURCE-UNREACHABLE | 503 | yes | no | F04 | Gateway/source cannot be read (run error). |
| E-INT-URL-SCHEME-REFUSED | 422 | no | yes | F04 | Non-http(s) or non-loopback source URL. |
| E-INT-RESOLUTION-REASON-REQUIRED | 422 | no | no | F04 | Conflict resolution without reason. |
| E-INT-ITEM-NOT-FOUND | 404 | no | no | F04 | Unknown raw_id/source. |
| E-INT-CONFLICT-ALREADY-RESOLVED | 409 | no | no | F04 | Conflict already has a resolution. |
| E-ID-LINK-EXISTS | 409 | no | no | F05 | Duplicate active link. |
| E-ID-PAIR-NOT-REGISTERED | 422 | no | no | F05 | Type pair not in the registry. |
| E-ID-SELF-LINK | 422 | no | no | F05 | Link to itself. |
| E-ID-AMBIGUOUS-TYPE | 422 | no | no | F05 | Identifier matches several id patterns; id_type required. |
| E-ID-REASON-REQUIRED | 422 | no | no | F05 | Human link/retract without reason. |
| E-ID-NOT-FOUND | 404 | no | no | F05 | Unknown identifier. |
| E-ID-LINK-NOT-FOUND | 404 | no | no | F05 | Unknown link. |
| E-RUN-SCHEDULE-DISABLED | 409 | no | yes | F06 | scheduled trigger while schedule.enabled = false. |
| E-RUN-ALREADY-RUNNING | 409 | yes | yes | F06 | Another run of the job holds the lock. |
| E-RUN-TOTALS-MISMATCH | 500 | no | yes | F06 | Run totals do not reconcile with outcome rows (run marked failed). |
| E-RUN-UNKNOWN-JOB | 404 | no | no | F06 | Job not in the catalogue. |
| E-RUN-CHECKPOINT-INVALID | 409 | no | yes | F06 | Corrupt/unknown checkpoint. |
| E-RUN-ABANDONED | n/a (CLI/CI) | no | yes | F06 | Informational: stale run closed by a later invocation. |
| E-MET-TAG-REQUIRED | 422 | no | no | F07 | Metric registration without definition_tag. |
| E-MET-TAG-MIX | 422 | no | no | F07 | Arithmetic/comparison across different tags or policy versions. |
| E-MET-CUTOFF-REQUIRED | 422 | no | no | F07 | month_end_total without cutoff/denominator. |
| E-MET-UNPARSABLE-INPUT | 422 | no | no | F07 | Unparsable amounts present (details list rows). |
| E-MET-SOURCE-REFUSED | 422 | no | no | F07 | Forbidden source (e.g. operating_costs.total_cases as cases created). |
| E-MET-NOT-AVAILABLE | 501 | no | no | F07 | Feature not available (cost/rework). |
| E-MET-NOT-REPRODUCIBLE | 409 | no | yes | F07 | Stored value does not recompute. |
| E-MET-UNKNOWN-METRIC | 404 | no | no | F07 | Unknown metric/value id. |
| E-MET-DEFINITION-REQUIRED | 422 | no | no | F07 | Backlog/time metric requested without definition tag/clock. |
| E-REV-QUERY-INVALID | 422 | no | no | F08 | Unknown search field or malformed filter. |
| E-REV-QUERY-TOO-LONG | 422 | no | no | F08 | Query over 200 chars or 12 terms. |
| E-REV-SEARCH-DISABLED | 501 | no | no | F08 | Search not enabled (R1). |
| E-REV-NOT-FOUND | 404 | no | no | F08 | Unknown flag/queue item. |
| E-REV-TEMPLATE-INVALID | 422 | no | no | F08 | Template fields invalid. |
| E-CO-NOT-SANDBOX | n/a (CLI/CI) | no | yes | F10 | Harness refused: working data inside original repo (exit 7). |
| E-CO-UNAPPROVED-DEVIATION | n/a (CLI/CI) | no | yes | F10 | golden-compare found an unapproved difference (exit 6). |
| E-CO-LEGACY-WRITE-REFUSED | n/a (CLI/CI) | no | yes | F10 | Write to a legacy path refused. |
| E-CO-DENYLIST-IMPORT | n/a (CLI/CI) | no | n/a (CI) | F10 | Deny-listed dependency/import found. |
| E-CO-EGRESS-ATTEMPT | n/a (CLI/CI) | no | n/a (test) | F10 | Outbound connection attempt detected. |
| E-CO-RUNTIME-UNSUPPORTED | n/a (CLI/CI) | no | no | F10 | Python/SQLite below the floor (exit 8). |
| E-SYS-DB-BUSY | 503 | yes | no | all | SQLite busy after bounded retry (busy_timeout, then 3 attempts). |
| E-SYS-INTERNAL | 500 | no | yes | all | Unexpected failure; generic message; details only in logs. |

### ER-4 Edge-case and failure-mode specification
| ID | Situation | Required behaviour | Test |
|---|---|---|---|
| EC-01 | Process killed during an intake batch | no partial outcome rows for an item (per-item transaction); RUN_ABANDONED on next start; resume from checkpoint | AC-RUN-07 |
| EC-02 | SQLite busy/locked | bounded retry (busy_timeout then 3 attempts, back-off) then `E-SYS-DB-BUSY` 503; no partial write | CT-17 (Unknown) |
| EC-03 | Disk full while writing audit | change rolled back with `E-SEC-AUDIT-WRITE-FAILED`; no event exists | AC-SEC-14 |
| EC-04 | Clock moves backwards | `recorded_at` monotonic per case is enforced by taking max(previous.recorded_at, now); event flagged `clock_regression` in payload | to be tested at Stage 14 |
| EC-05 | Two identical requests race with the same Idempotency-Key | one record, both callers receive it | AC-DEC-22/23 |
| EC-06 | Unicode: NFC vs NFD identifiers | compared after NFC + trim; display preserves original | AC-ID-04 |
| EC-07 | Very large payload / many items | body limit 1 MiB (413); page clamps (100); search query caps | AC-REV-03 |
| EC-08 | Legacy file missing/locked/corrupt | adapter returns `E-INT-SOURCE-UNREACHABLE` for the job; no fabricated data; hub keeps serving | AC-INT-26 |
| EC-09 | Source sends `source_ts` in the future (2,234 shipped rows have source_ts > ingest_ts) | accepted; flagged `FUTURE_SOURCE_TS` in delay report; no quarantine | AC-INT-28 |
| EC-10 | Backup restore returns an older store than the anchor | `verify-audit` reports head mismatch; operators must treat as data loss | AC-CO-09 |
| EC-11 | Unknown event_type/field in a request | `E-REQ-INVALID` (additionalProperties false) | schemas |
| EC-12 | Config invalid at start-up | refuse to start with a clear message; no partial start | AC-SEC-16 |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-ER-1 HTTP code choices (423 for configuration-locked states, 501 for not-in-release) are conventions.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-ER-1 Real lock-contention behaviour under concurrent writers (CT-17) is Unknown.

## Unresolved Issues
- EC-04 clock regression handling is a proposal without a repo precedent.

## Residual Risks
- Generic auth messages hamper support; correlation id is the diagnostic path.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
