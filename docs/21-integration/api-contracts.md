---
stage: "21 — Enterprise Integration"
artifact: "api-contracts.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["services/source_gateway/server.py", "integration/source-gateway.json", "app/gateway_bridge.py", "hub/adapters/gateway_client.py", "hub/intake/cli.py (gateway-pull)", "docs/12-specs/api-contracts.md (API-1..API-6)", "docs/12-specs/contracts/openapi.yaml", "hub/security/route_registry.json (48 routes)", "docs/12-specs/interface-contracts.md IF-4 GatewayReader", "docs/16-repo-validation/data-contract-results.md DC-3", "docs/21-integration/evidence/gateway-stub-conformance.json (STG21 S02)", "tests/hub/test_tst_hub_stg21_integration.py S02-S04", "tests/hub/test_tst_int_17_29_match_untrusted_sources.py TST-INT-25/26", "tests/hub/test_inc06_supplementary.py S09"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The only consumed API is the repo's own loopback source-gateway stub; the only provided API is the hub's loopback HTTP surface. No real endpoint exists.**

## Summary
Two API contracts are in scope. **AC-S21-01 (provided)**: the hub HTTP API, 48 operations in the DRAFT OpenAPI, mirrored 1:1 by `hub/security/route_registry.json` (TST-SEC-01 drift test), loopback only; Stage 21 changes nothing in it and re-states its integration-relevant rules. **AC-S21-02 (consumed)**: `GET /api/events` of the shipped source-gateway stub, now **written down from observed behaviour** and proven against the unchanged stub by STG21 S02 (125 events, pages 50/50/25/0, clamp at 200, `next_offset` arithmetic, catalog = `integration/source-gateway.json`). The hub client's expectations hold on every point; two semantic gaps are recorded for decision (shape errors are retried; `schema_version` 0.9 events are accepted because the gateway profile has no revision set).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AC-S21-01 Provided: hub HTTP API (no change in Stage 21)
| Rule | Value | Evidence | Tag |
|---|---|---|---|
| Operations | 48 (`openapi.yaml` operationIds) = 48 registry routes, deny by default | TST-SEC-01; Stage 16 DC-3 | [Verified Fact] |
| Bind | loopback only; a non-loopback bind raises E-SEC-EXPOSURE-NOT-APPROVED (exposure = Stage 24 decision) | `hub/web/server.py` `bind_address` | [Verified Fact] |
| Auth | session token (sha256 stored), roles per route, Zone H re-auth + holders (empty) | authentication-map.md AM-3 | [Verified Fact] |
| Errors | JSON error envelope (schema `error-envelope`); CLI shape per `spec-addendum-cli-error-shape.md` | I8 tests; DQ-05 | [Verified Fact] |
| Additive details not in DRAFT OpenAPI | `reason` query on C3 reads, login body fields, `view=freshness` (DEV-84/94/98) | Stage 16 DC-3 | [Verified Fact]; addendum at Stage 23 (DW-13) |
| External consumers | none in the repository; reviewer UI only | integration-inventory.md II-1 | [Verified Fact] / [Unknown] outside |

### AC-S21-02 Consumed: source-gateway `GET /api/events` (as observed; stub unchanged)
| Element | Observed contract | Hub client expectation (`gateway_client.fetch_events`) | Conforms? | Evidence | Tag |
|---|---|---|---|---|---|
| Transport | HTTP on `HOST:SOURCE_PORT` (default 127.0.0.1:8090), no TLS, no auth | http/https, **loopback host only**, no proxy, no redirects, 5 MiB cap | yes | `server.py`; TST-INT-25; S02 | [Verified Fact] |
| Request | `GET /api/events?offset=<int>&limit=<int>[&source=mes|lims|qms]` | sends `offset`, `limit` as integers; never `source` | yes | S03 (request line recorded) | [Verified Fact] |
| Paging | `limit` clamped to 1..200, `offset` >= 0; rows of `batch_records` ordered by `batch_id` | follows `next_offset` from the response, not its own arithmetic | yes: limit 500 -> 125 items, `next_offset` 125 | S02 | [Verified Fact] |
| Response | `200 {"items": [...], "count": n, "next_offset": offset + n}`; empty page at the end (`next_offset` = offset) | requires `items` list and integer `next_offset`; ignores `count` | yes: pages 50/50/25/0 | S02 | [Verified Fact] |
| Event | `message_id` (sha256 prefix of system+key+type), `business_key`, `system` (mes/lims/qms), `event_type` (4 types), `schema_version` ("1.0", or "0.9" every 19th), `occurred_at`, `published_at` (formulaic), `payload {identifier, note, source_status}` | mapped by `gateway_event_deliveries`: source_key=message_id, partner=system, ref_id=business_key, record_kind=event_type, source_ts=occurred_at, schema_rev=schema_version; whole event = payload | yes: 125 distinct message_ids, 8 keys | S02; `evidence/gateway-stub-conformance.json` | [Verified Fact] |
| Errors | `400 {"error": "bad pagination"}` / `{"error": "unknown source"}`; failure simulator on a separate path: `/api/failure?mode=timeout` -> 503 retryable, `rate_limit` -> 429 retryable, `schema` -> 200 `{"unexpected_schema": "v3", "records": null}` | 5xx / 429 / connection / timeout / shape error -> retried up to `retries` with back-off 0.5 x 2^i; other 4xx not retried; then E-INT-SOURCE-UNREACHABLE (run error, no item) | yes | S03 (stub bodies replayed), S04, TST-INT-26, INC06 S09 | [Verified Fact] |
| Other routes | `/health`, `/api/catalog` (= `integration/source-gateway.json`), `/api/record/<id>` | not used by the hub | n/a | S02 (catalog equal) | [Verified Fact] |
| Versioning | none on the URL; per-event `schema_version` | gateway profile has `schema_revs: None` (not constrained) | gap | S02: 7 of 125 events are "0.9", all VALIDATED | [Verified Fact] / [Unknown] meaning of 0.9 |

### AC-S21-03 Legacy bridge vs hub client (same stub, different semantics)
| Aspect | `app/gateway_bridge.py` (legacy, unchanged) | Hub AD-04 | Tag |
|---|---|---|---|
| Timeout / retry | `urlopen(..., timeout=5)`, no retry | timeout 5 s, retries 3 (`gateway.retries`), back-off 0.5/1/2 s | [Verified Fact] |
| Invalid / unknown-key event | counted `invalid`, **not stored** (at-most-once) | stored verbatim, classified (quarantine / exception), never dropped | [Verified Fact] |
| Duplicate | PK on `message_id` -> `duplicates` counter | stored again as a new raw row, outcome NOOP_DUPLICATE (natural key + content hash) | [Verified Fact] S02 stale re-pull |
| Checkpoint | legacy `gateway_checkpoints` upsert | hub-owned `intake_run_event` RUN_CHECKPOINT; legacy table never touched | [Verified Fact] |

### AC-S21-04 Findings register
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| AF-01 | The shipped stub conforms to every expectation of the hub client (shape, paging, clamp, empty page, catalog) | S02 | AD-04 is proven against the real counterpart, not only a double | Low | High | — |
| AF-02 | A 200 response with an unexpected shape is retried like a transient error (bounded: `retries` + 1 attempts) before E-INT-SOURCE-UNREACHABLE | S03 (3 attempts at retries=2); `gateway_client.py` except clause | wasted attempts on a deterministic error; no data effect | Low | High | DQ-S21-03: keep (bounded, harmless) or fail fast? |
| AF-03 | `schema_version` "0.9" events (7 / 125) are VALIDATED: the gateway profile has no closed revision set | S02 `schema_version_counts`; `hub/intake/profiles.py` | an unsupported upstream revision would pass silently | Medium | High | DQ-S21-04: is 0.9 supported? (owner: Engagement lead (Dinesh Naik)) |
| AF-04 | The stub cannot produce a 5xx or timeout on `/api/events` itself; failure modes exist only on `/api/failure`, so they are replayed through a loopback double with the stub's own bodies | `server.py`; S03 | failure tests rely on recorded bodies, not live faults | Low | High | — |
| AF-05 | No API versioning, auth or rate contract exists on the consumed API | `server.py` | any real source would need a new contract (Stage 24 / real system) | Medium | High | U-21-AC-1 |

## Evidence References
- `docs/21-integration/evidence/gateway-stub-conformance.json` (reproduce: `python3 -B tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s21-stub --label stub -k TST_HUB_STG21_S02`).
- STG21 S03, S04; TST-INT-25, TST-INT-26; INC06 S09; TST-SEC-01.

## Assumptions
- A-21-AC-1 [Assumption] The stub's observed behaviour is the contract the legacy estate relied on (no written gateway API contract exists besides `docs/source-gateway.md`). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-21-AC-1 Contract (versioning, auth, rate limits, SLAs) of any real upstream gateway - none exists; Engagement lead (Dinesh Naik).
- U-21-AC-2 Meaning of `schema_version` 0.9 (AF-03) - Engagement lead (Dinesh Naik).

## Unresolved Issues
- AF-02, AF-03 await decisions DQ-S21-03 / DQ-S21-04 (no code change made in Stage 21: evidence-only increment, no defect against an approved spec).

## Residual Risks
- RR-21-AC-1 Upstream revision drift on the gateway is not detected (AF-03) (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
