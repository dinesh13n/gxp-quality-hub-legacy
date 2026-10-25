---
stage: "28 — Reliability & Resilience Engineering"
artifact: "timeout-retry-policy.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
One table of every timeout and retry in the hub (as shipped) and the Stage 28 policy defaults for the guarded gateway path. Rules: retry only idempotent reads; every retry is bounded per call, paid from a budget and stopped by a breaker; back-off is deterministic (optional injected jitter); a client error is never retried. All Stage 28 numbers are **assumptions A-28-01..A-28-03**, validated for range by `hub/resilience/policy.resolve` (STG28 P01) and tested in P02/P03/F01-F05; none is a measured need.

## Findings
### TR-1 Shipped timeouts and limits [Verified Fact]
| ID | Where | Value | Behaviour at the limit | Evidence |
|---|---|---|---|---|
| TO-01 | gateway client attempt | 5 s (`timeout=5`) | `TimeoutError` -> retried | `gateway_client.py`, STG21 S04 |
| TO-02 | gateway client response size | 5 MiB | `ValueError` -> retried (FG-01) | `MAX_BYTES` |
| TO-03 | listener read timeout | 10 s (`READ_TIMEOUT_SECONDS`) | 408 E-REQ-TIMEOUT / socket closed | `hub/web/server.py`, STG26 C06 |
| TO-04 | request body | 1 MiB | 413 | `BODY_LIMIT` |
| TO-05 | SQLite busy wait | 30 000 ms | OperationalError -> 503 E-STORE-UNAVAILABLE (F-DB-01) | `hub/web/app.py:109` |
| TO-06 | job heartbeat stale | 900 s | stale `run_lock` is abandoned, next run resumes | `hub/runs/settings.py` |
| TO-07 | rejected-request limiter | 100 refusals / 60 s per peer | 429 E-REQ-RATE-LIMITED | `hub/web/ratelimit.py` |

### TR-2 Retry policy [Verified Fact for shipped, Assumption for Stage 28 defaults]
| Item | Shipped client (`fetch_events`) | Stage 28 guarded path (`GuardedGateway`) | Why |
|---|---|---|---|
| Retried | connection error, timeout, 5xx, 429, shape error | connection error, timeout, 5xx, 429 | shape errors are deterministic (S28-DEV-02) |
| Not retried | other 4xx | other 4xx (reason `client_error`, breaker untouched) | a client error says nothing about source health |
| Max retries | 3 (`retries`, config `gateway.retries`) | 3 (`retry.max_retries`, range 0-10) | unchanged default |
| Back-off | 0.5 x 2^i (0.5, 1, 2), no cap | min(8, 0.5 x 2^i), optional injected jitter clamped to [0, d] | cap protects larger retry counts; jitter de-synchronises several callers (none exist today) |
| Cross-call bound | none | retry budget: each first attempt earns 20 % of a retry, a retry costs 1, balance <= 10; retries <= 10 + calls x 0.2 | prevents a retry storm even if the breaker is off (F02 a) |
| Stop condition | after the last retry | + breaker open (3 consecutive failed calls, 60 s cooldown) | F01, F02 b |
| Worst-case time of one call | 4 x 5 s + 3.5 s = 23.5 s | same, and only while the budget and breaker allow | F03 |
| Outcome of failure | E-INT-SOURCE-UNREACHABLE; run recorded failed | same, `details.reason` in circuit_open, bulkhead_full, retry_budget_exhausted, retries_exhausted, shape_error, client_error | existing error code kept (FS-1) |

### TR-3 Non-idempotent operations [Verified Fact]
Ingest, binding changes, conflict resolutions, Zone H actions and job runs are **never retried automatically** (FS-2); re-running is safe by construction, but the hub does not do it for the operator. The guarded client issues GET only (static check in STG21 S03 on the wrapped client; `GuardedGateway` adds no verb).

### TR-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved |
|---|---|---|---|---|---|---|
| F-TO-01 | Worst-case gateway call 23.5 s with the shipped defaults; fine for an operator CLI, long for any service caller | arithmetic on TO-01 and the schedule; F03 measured one 0.3 s x 2 case | operator waits | Low | High | real source latency (U-28-01) |
| F-TO-02 | `busy_timeout` 30 s is long compared with the 10 s read timeout | TO-05 vs TO-03 | thread held on a locked store | Low | Medium | D-28-09 |

## Evidence References
`hub/adapters/gateway_client.py`, `hub/resilience/policy.py`, `hub/resilience/guarded.py`, `tests/hub/test_tst_hub_stg28_policy.py` P01-P03, `test_tst_hub_stg28_injection.py` F01-F05, `docs/21-integration/failure-semantics.md` FS-1/FS-2, `evidence/retry-budget-bound.json`, `evidence/f02-retry-storm.json`.

## Assumptions
- A-28-01 [Assumption] retry defaults 3 / 0.5 s / x2 / cap 8 s / 5 s timeout (the first three equal the shipped values). A-28-02 [Assumption] retry budget 20 % / cap 10. Confirm: Engagement lead (Dinesh Naik) once a real source exists.

## Unknowns
- U-28-01 (source latency, error mix, rate limits) - no real source.

## Unresolved Issues
- Wiring the guarded path into `gateway-pull` (D-28-01).

## Residual Risks
- RR-28-04 The shipped command is still the unguarded one.

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
