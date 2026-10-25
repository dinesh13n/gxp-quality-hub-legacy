---
stage: "28 — Reliability & Resilience Engineering"
artifact: "resilience-architecture.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/resilience/policy.py", "hub/resilience/guarded.py", "hub/web/bounded_server.py", "hub/adapters/gateway_client.py", "hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/runs/service.py", "docs/21-integration/failure-semantics.md", "docs/26-tevv/tevv-results.md", "docs/27-hardening/runtime-hardening.md", "tests/hub/test_tst_hub_stg28_policy.py", "tests/hub/test_tst_hub_stg28_injection.py", "tests/hub/test_tst_hub_stg28_ai_capacity.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Status IN REVIEW: nothing here is an approval, no risk is accepted, no real holder, stakeholder or production system is named or touched. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY. Every default below is an AGENT ASSUMPTION under OD-32, not a measured need and not approved by Dinesh Naik.**

## Summary
The hub is a single-process, single-store, loopback-only system with exactly one remote dependency (the AD-04 source gateway, loopback in this repo) and no model or provider dependency. Its resilience architecture therefore has four layers: (1) **bounded work** at every boundary (timeouts, body and response limits, batch size, run lock); (2) **fail closed, never fabricate** (a failure is a run error, a 4xx/5xx envelope or a refusal, never data); (3) **new in Stage 28: protection of the callers of a failing dependency** (retry budget, circuit breaker, bulkhead, connection cap) as an additive package `hub/resilience/`; (4) **AI-disabled operation as the only mode** (nothing to degrade to). The Stage 28 package is built, tested and **not wired** into any shipped command (S28-DEV-01, D-28-01, D-28-02): the shipped `gateway-pull` and listener keep their Stage 27 behaviour.

## Findings
### RA-1 Components and failure boundaries
| ID | Component | Dependency | Boundary / limit today | Tag |
|---|---|---|---|---|
| RA-C1 | Loopback listener `hub/web/server.py` (ThreadingHTTPServer) | clients on 127.0.0.1 | read timeout 10 s (408), body limit 1 MiB, rate limit on refused requests (429 after 100 / 60 s), **no cap on concurrent connections** | [Verified Fact] |
| RA-C2 | `WebApp` + SQLite store `hub/web/app.py` | one SQLite file | `busy_timeout` 30 000 ms, store fault = 503 E-STORE-UNAVAILABLE (Stage 27), single writer | [Verified Fact] |
| RA-C3 | Gateway client `hub/adapters/gateway_client.py` | source gateway (loopback, GET only) | 5 s timeout, 3 retries, back-off 0.5 x 2^i, 5 MiB response cap, no redirect, no proxy; **no budget, jitter, cap or breaker** | [Verified Fact] |
| RA-C4 | Intake / run services `hub/intake`, `hub/runs` | store, sources | one transaction per run, `run_lock` single flight with heartbeat, checkpointed jobs, batch size explicit | [Verified Fact] |
| RA-C5 | Legacy read-only adapters `hub/adapters/legacy_*` | frozen legacy snapshot | hash-gated, fail closed on drift, never written | [Verified Fact] |
| RA-C6 | Audit chain + anchor `hub/security/audit.py` | store, anchor file | insert-only triggers, tamper detected by `verify`, clock rollback does not revive sessions (S26 C05) | [Verified Fact] |
| RA-C7 | **`hub/resilience/policy.py`** (new) | none (pure) | settings validation, back-off, RetryBudget, Breaker (+ snapshot/restore), Bulkhead | [Verified Fact] built + tested |
| RA-C8 | **`hub/resilience/guarded.py`** (new) | gateway client | bulkhead -> breaker -> budgeted retries; failures are `E-INT-SOURCE-UNREACHABLE` with `details.reason` | [Verified Fact] built + tested |
| RA-C9 | **`hub/web/bounded_server.py`** (new) | listener | hard connection cap, shed with 429 `E-REQ-RATE-LIMITED` | [Verified Fact] built + tested |

### RA-2 Design principles (each backed by a test)
1. **A dependency failure is a run failure, never data** (FS-1 rule 1; STG28 F08: RUN_FAILED, 0 raw rows, 0 outcomes).
2. **Retries are bounded three ways**: per call (`max_retries`), across calls (retry budget: retries <= cap + calls x percent/100; STG28 P03/F02) and by state (breaker stops all calls to a dependency that keeps failing; STG28 F01/F02: 200 calls reach the source 12 times, not 800).
3. **Only idempotent reads are retried** (GET; FS-2). Client errors (4xx except 429) are never retried and never count against the breaker (STG28 F05).
4. **Fail fast beats queueing**: an open breaker, a full bulkhead and a full connection table answer at once (STG28 F01, F06, F07). Nothing is queued, so there is no backlog to drain into a recovering dependency.
5. **Recover by one probe** after a cooldown, not by a burst (STG28 F04).
6. **The core never depends on the optional**: the source being down leaves health, reads, reviewer queue and audit verification working (STG28 F08); AI is absent by design (STG28 A01-A03).
7. **No new error vocabulary**: the package reuses `E-INT-SOURCE-UNREACHABLE` and `E-REQ-RATE-LIMITED` (static test P07), so the Stage 27 error registry is unchanged.

### RA-3 What is NOT in the architecture (and why) [Verified Fact unless stated]
- No fallback model or provider, no prompt/response cache: the product has no model (OD-08). The only cache in `hub/` is the per-load token-statistics memo in `hub/search/engine.py:187` (derived data, rebuilt on load); there is no response or result cache, so caching is not a resilience lever here [Verified Fact: grep of hub/; Inference: conclusion].
- No scheduler (HAR-10 open): there is no unattended retry loop at all; every pull is operator-started. This removes the largest retry-storm source (unattended re-runs) and creates the late-delivery catch-up gap (FG-02).
- No multi-node, replica or failover: single SQLite file; recovery is backup/restore (RTD-33; Stage 29).
- Stage 22 agent loops: NOT APPLICABLE (no agents, `docs/22-agentic-engineering/not-applicable.md`); cascading agent/tool failure cannot occur [Verified Fact].

## Evidence References
- Code: `hub/resilience/*.py`, `hub/adapters/gateway_client.py`, `hub/web/server.py`, `hub/web/app.py:109`, `hub/runs/service.py` (run_lock), `hub/web/ratelimit.py`.
- Tests: `tests/hub/test_tst_hub_stg28_policy.py` (P01-P07), `test_tst_hub_stg28_injection.py` (F01-F08), `test_tst_hub_stg28_ai_capacity.py` (A01-A03, C01), `test_tst_hub_stg28_egress_guard.py` (E28 S90); Stage 26 `test_tst_hub_stg26_resilience.py` C01-C06; Stage 21 `test_tst_hub_stg21_integration.py` S03/S04/S07.
- Docs: `docs/10-architecture/*`, `docs/21-integration/failure-semantics.md`, `docs/26-tevv/tevv-results.md`, `docs/27-hardening/runtime-hardening.md`.

## Assumptions
- A-28-00 [Assumption] Loopback-only, single-operator operation remains the deployment shape until Stage 30 / a recorded exposure decision (OD-32 DQ-S24). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-28-01 Real source behaviour (latency, error mix, rate limits): no real enterprise source exists (OD-28 a). Resolved only when a real source is named.

## Unresolved Issues
- Wiring of the new package into `gateway-pull` and `hub web serve` (D-28-01, D-28-02).

## Residual Risks
- RR-28-01 The mechanisms protect nothing until wired; the shipped commands remain bounded but unguarded (see resilience-readiness.md).

## Change History
v0.1 (2026-10-25): first version, Stage 28 BUILD.
