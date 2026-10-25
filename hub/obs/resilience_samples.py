"""Resilience telemetry (Stage 31 over Stage 28): turns the counters the Stage 28 primitives already keep into catalogue samples.

`samples(dependency, breaker, budget, bulkhead, gateway)` reads attributes of hub.resilience.policy.Breaker / RetryBudget / Bulkhead and of
hub.resilience.guarded.GuardedGateway; every argument is optional. It changes nothing in them and nothing calls it by default (S31-DEV-01): wiring a
caller is decision D-31-02 together with D-28-01. `dependency` is a closed identifier (the source name), never a URL.
"""
from hub.obs.catalog import LABEL_VALUE, sample
from hub.resilience import policy

STATE_CODE = {policy.CLOSED: 0, policy.OPEN: 1, policy.HALF_OPEN: 2}


def samples(dependency, breaker=None, budget=None, bulkhead=None, gateway=None):
    if not (isinstance(dependency, str) and LABEL_VALUE.match(dependency)):
        raise ValueError("dependency must be an identifier, not free text or a URL")
    lab = {"dependency": dependency}
    out = []
    if gateway is not None:
        breaker, budget, bulkhead = breaker or gateway.breaker, budget or gateway.budget, bulkhead or gateway.bulkhead
        out += [sample("resilience_calls_total", "counter", lab, gateway.calls_total),
                sample("resilience_attempts_total", "counter", lab, gateway.attempts_total)]
    if breaker is not None:
        out += [sample("resilience_breaker_state", "gauge", lab, STATE_CODE[breaker.state]),
                sample("resilience_breaker_opened_total", "counter", lab, breaker.opened_count),
                sample("resilience_breaker_rejected_total", "counter", lab, breaker.rejected)]
    if budget is not None:
        out += [sample("resilience_retry_budget_tokens", "gauge", lab, int(budget.tokens)),
                sample("resilience_retries_granted_total", "counter", lab, budget.retries_granted),
                sample("resilience_retries_denied_total", "counter", lab, budget.retries_denied)]
    if bulkhead is not None:
        out += [sample("resilience_bulkhead_rejected_total", "counter", lab, bulkhead.rejected),
                sample("resilience_bulkhead_in_flight", "gauge", lab, bulkhead.in_flight)]
    return sorted(out, key=lambda s: s["name"])
