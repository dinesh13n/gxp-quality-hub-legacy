---
stage: "28 — Reliability & Resilience Engineering"
artifact: "circuit-breaker-policy.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
Policy and behaviour of the Stage 28 breaker (`hub.resilience.policy.Breaker`) and of the two bulkheads (`Bulkhead` for pulls, connection cap for the listener). The breaker is per dependency (one: the gateway), counts **failed calls** (a call that exhausted its retries), not attempts, and is deterministic (injected clock). It is tested at unit level (P04, P05) and through real loopback failures (F01, F02, F04, F08).

## Findings
### CB-1 State machine [Verified Fact: STG28 P04]
| From | Event | To | Notes |
|---|---|---|---|
| CLOSED | failed call, consecutive count < threshold (3) | CLOSED | a success resets the count (two failures, a success, two failures stays closed) |
| CLOSED | 3rd consecutive failed call | OPEN | `opened_at` = injected clock |
| OPEN | call before cooldown (60 s) | OPEN | refused unseen: reason `circuit_open`, `retry_after_seconds` >= 1, source gets no request (F01, F02) |
| OPEN | cooldown elapsed | HALF_OPEN | |
| HALF_OPEN | call, probe slot free (`half_open_probes` = 1) | HALF_OPEN | exactly one probe at a time; a concurrent second caller is refused (F04) |
| HALF_OPEN | probe fails | OPEN | cooldown restarts from the failure |
| HALF_OPEN | probe succeeds | CLOSED | counts reset (F04, F08) |
| any | client error (4xx other than 429) | unchanged | `cancel()` frees the probe slot, counts nothing (F05) |
| OPEN | clock moved backwards | OPEN, cooldown restarts from the current reading | fail closed (P04) |

### CB-2 What counts as a failure
Counts: connection error, timeout, 5xx, 429, shape error (the source is reachable but misbehaving). Does not count: client error 4xx, bulkhead refusal, breaker refusal (F05, F06).

### CB-3 Persistence across runs
`snapshot()` / `restore()` carry the state to another process (P05, F08). **Nothing persists it today**: `gateway-pull` is one process per run, so a breaker only protects within a process until the caller stores the snapshot (open decision D-28-01: file next to the audit anchor vs a store table with a migration; the file option needs no schema change but needs an atomic write and a malformed-file rule - restore refuses a malformed snapshot with E-CFG-INVALID, P05).

### CB-4 Bulkheads
| ID | Where | Limit | Excess | Evidence |
|---|---|---|---|---|
| BH-01 | `GuardedGateway` | 1 concurrent pull (`bulkhead.max_concurrent`) | refused at once, reason `bulkhead_full`, 0 attempts, breaker untouched | F06 |
| BH-02 | `BoundedLoopbackServer` | 64 concurrent connections (default; the F07 test uses 3) | 429 E-REQ-RATE-LIMITED + Retry-After 1, no thread, no store open, no audit row | F07 |
| BH-03 | job single flight (shipped) | 1 run per job | E-RUN-ALREADY-RUNNING and a refused record | TST-RUN, FM-06 |

### CB-5 Cascading failure analysis [Inference from verified structure]
The dependency graph is a star: operator/CLI -> store, operator -> gateway. The gateway is not on any request path of the web listener (STG28 F08: reads and health stay 200 while the source is down), so a gateway failure cannot cascade into the web surface. The only shared resource is the store file; its fault is 503 for all (FM-08). There are no agents or tools calling each other (Stage 22 not applicable), so agent/tool cascades cannot occur.

### CB-6 Findings
| ID | Finding | Impact | Risk | Confidence |
|---|---|---|---|---|
| F-BRK-01 | No cross-run breaker state (FG-03) | repeated manual pulls retry independently (each bounded) | Low (single loopback source) | High |
| F-BRK-02 | Breaker thresholds are not tuned to any observed error pattern | too sensitive or too slow once a real source exists | Low | High |

## Evidence References
`hub/resilience/policy.py`, `hub/resilience/guarded.py`, `hub/web/bounded_server.py`, STG28 P04, P05, P06, F01, F02, F04, F05, F06, F07, F08; `docs/21-integration/failure-semantics.md` FG-03.

## Assumptions
- A-28-03 [Assumption] threshold 3 failed calls, cooldown 60 s, 1 probe; connection cap 64. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-28-04 Whether breaker state should be shared by several operators / processes.

## Unresolved Issues
- D-28-01 persistence and wiring; D-28-02 listener cap wiring.

## Residual Risks
- RR-28-05 A restored stale OPEN snapshot would delay a pull by at most the cooldown (60 s); a lost snapshot only loses protection, never data.

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
