"""GuardedGateway (Stage 28): the AD-04 gateway client behind a bulkhead, a circuit breaker and a retry budget.

Per call: bulkhead slot (refused at once when full) -> breaker.allow() (an OPEN breaker answers without touching the source) -> up to 1 + max_retries
attempts of gateway_client.fetch_events(retries=0), each with `timeout_seconds`; waits follow policy.backoff_delay and every retry must be paid from the
RetryBudget. A call ends in one of: a page; a client error (HTTP 4xx other than 429: never retried, says nothing about source health, breaker untouched);
or E-INT-SOURCE-UNREACHABLE with details.reason in {circuit_open, bulkhead_full, retry_budget_exhausted, retries_exhausted, shape_error, client_error}.
Shape errors (200 with an unexpected body) fail fast unless retry_shape_errors is true (S28-DEV-02, answers FG-01 / DQ-S21-03 with the safer default).
A failed call is a run failure, never data: nothing is fabricated (FS-1 rule 1). Only GET is ever issued (the wrapped client is GET-only).
"""
from hub.adapters import gateway_client
from hub.intake.errors import SourceUnreachable
from hub.resilience import policy

_SHAPE = ("ValueError", "JSONDecodeError", "UnicodeDecodeError")


def classify(last_error):
    le = last_error or ""
    if le.startswith("http_"):
        try:
            code = int(le[5:])
        except ValueError:
            return "transient"
        return "client" if code < 500 and code != 429 else "transient"
    return "shape" if le in _SHAPE else "transient"


class GuardedGateway(object):
    def __init__(self, url, clock, sleep, settings=None, fetch=None, jitter=None, breaker=None, budget=None, bulkhead=None):
        s = policy.resolve(settings)
        self.url, self.r, self.sleep, self.jitter = url, s["retry"], sleep, jitter
        self.fetch = fetch or gateway_client.fetch_events
        b = s["breaker"]
        self.breaker = breaker or policy.Breaker(b["failure_threshold"], b["cooldown_seconds"], clock, b["half_open_probes"])
        self.budget = budget or policy.RetryBudget(self.r["budget_percent"], self.r["budget_cap"])
        self.bulkhead = bulkhead or policy.Bulkhead(s["bulkhead"]["max_concurrent"])
        self.attempts_total = 0
        self.calls_total = 0

    def _fail(self, reason, attempts, last, retries_used, **extra):
        d = {"reason": reason, "attempts": attempts, "last_error": last, "retries": retries_used, "retries_allowed": self.r["max_retries"]}
        d.update(extra)
        return SourceUnreachable(d)

    def fetch_events(self, offset=0, limit=50):
        self.calls_total += 1
        if not self.bulkhead.try_enter():
            raise self._fail("bulkhead_full", 0, None, 0)
        try:
            ok, wait = self.breaker.allow()
            if not ok:
                raise self._fail("circuit_open", 0, None, 0, retry_after_seconds=wait)
            self.budget.deposit()
            attempts, last, reason = 0, None, "retries_exhausted"
            for i in range(self.r["max_retries"] + 1):
                attempts += 1
                self.attempts_total += 1
                try:
                    page = self.fetch(self.url, offset, limit, retries=0, timeout=self.r["timeout_seconds"])
                except SourceUnreachable as e:
                    last = (e.details or {}).get("last_error")
                    kind = classify(last)
                    if kind == "client":
                        self.breaker.cancel()
                        raise self._fail("client_error", attempts, last, i)
                    if kind == "shape" and not self.r["retry_shape_errors"]:
                        reason = "shape_error"
                        break
                    if i == self.r["max_retries"]:
                        break
                    if not self.budget.withdraw():
                        reason = "retry_budget_exhausted"
                        break
                    self.sleep(policy.backoff_delay(i, self.r["base_seconds"], self.r["factor"], self.r["cap_seconds"], self.jitter))
                else:
                    self.breaker.record_success()
                    return dict(page, attempts=attempts)
            self.breaker.record_failure()
            raise self._fail(reason, attempts, last, attempts - 1)
        finally:
            self.bulkhead.leave()
