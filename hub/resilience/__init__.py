"""Stage 28 reliability building blocks (additive; nothing here is wired into a shipped command, see docs/28-reliability/resilience-readiness.md).

  policy.py          validated defaults, deterministic backoff schedule, retry budget, circuit breaker, bulkhead (pure standard library, injected clock)
  guarded.py         GuardedGateway: the AD-04 gateway client behind breaker + retry budget + bulkhead (fail fast, bounded, never fabricates an item)
  (moved to hub/web/bounded_server.py, S28-DEV-08)  BoundedLoopbackServer: the INC-08 listener with a hard cap on concurrent connections (sheds the excess with 429)

No module here imports time / random: the clock, the sleep and the jitter are injected (TST-CO-13 b). No new error code: failures are the existing
E-INT-SOURCE-UNREACHABLE (details.reason says why) and E-REQ-RATE-LIMITED. Synthetic repository, unvalidated.
"""
