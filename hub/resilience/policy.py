"""Retry / breaker / bulkhead primitives (Stage 28, S28-DEV-01). Pure standard library; the clock, sleep and jitter are always injected.

Retry budget (storm guard): every first attempt deposits `budget_percent` of a retry token, every retry withdraws a whole token, the balance never
exceeds `budget_cap` whole tokens. Over any run of calls, retries <= budget_cap + calls * budget_percent / 100, whatever the outage looks like, so the
total attempt count is bounded by calls * (1 + budget_percent/100) + budget_cap. Integer arithmetic only (percent units; one token = 100).

Breaker: CLOSED -> OPEN after `failure_threshold` consecutive failed calls; OPEN rejects without calling the dependency until `cooldown_seconds` have
passed; then HALF_OPEN lets `half_open_probes` calls through; a success closes it, a failure re-opens it (cooldown restarts). A clock that moved back
restarts the cooldown from the current reading (fail closed). snapshot() / restore() carry the state across processes (the caller persists it).

Bulkhead: a non-blocking concurrency cap. Excess work is refused at once, never queued.
"""
import threading

from hub.core.errors import ConfigInvalid

DEFAULTS = {
    "retry": {"max_retries": 3, "base_seconds": 0.5, "factor": 2, "cap_seconds": 8, "timeout_seconds": 5, "retry_shape_errors": False,
              "budget_percent": 20, "budget_cap": 10},
    "breaker": {"failure_threshold": 3, "cooldown_seconds": 60, "half_open_probes": 1},
    "bulkhead": {"max_concurrent": 1},
}
_RANGES = {"retry": {"max_retries": (0, 10), "base_seconds": (0.01, 60), "factor": (1, 10), "cap_seconds": (0.01, 600), "timeout_seconds": (0.1, 300),
                     "budget_percent": (0, 100), "budget_cap": (0, 1000)},
           "breaker": {"failure_threshold": (1, 1000), "cooldown_seconds": (1, 86400), "half_open_probes": (1, 100)},
           "bulkhead": {"max_concurrent": (1, 10000)}}
_INTS = {"max_retries", "budget_percent", "budget_cap", "failure_threshold", "cooldown_seconds", "half_open_probes", "max_concurrent", "factor"}


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and v not in (float("inf"), float("-inf"))


def resolve(section=None):
    """Defaults overlaid with `section` ({"retry": {...}, "breaker": {...}, "bulkhead": {...}}); any unknown key, wrong type or out-of-range value is ConfigInvalid."""
    out = dict((k, dict(v)) for k, v in DEFAULTS.items())
    if section is None:
        return out
    if not isinstance(section, dict):
        raise ConfigInvalid({"resilience": "must be an object"})
    for part, over in section.items():
        if part not in out:
            raise ConfigInvalid({"resilience." + str(part)[:30]: "unknown section"})
        if not isinstance(over, dict):
            raise ConfigInvalid({"resilience." + part: "must be an object"})
        for k, v in over.items():
            if k not in out[part]:
                raise ConfigInvalid({"resilience.%s.%s" % (part, str(k)[:30]): "unknown key"})
            out[part][k] = v
    for part, vals in out.items():
        for k, v in vals.items():
            where = "resilience.%s.%s" % (part, k)
            if k == "retry_shape_errors":
                if not isinstance(v, bool):
                    raise ConfigInvalid({where: "boolean"})
                continue
            lo, hi = _RANGES[part][k]
            ok = _num(v) and lo <= v <= hi and (isinstance(v, int) if k in _INTS else True)
            if not ok:
                raise ConfigInvalid({where: str(v)[:20], "allowed": [lo, hi]})
    if out["retry"]["cap_seconds"] < out["retry"]["base_seconds"]:
        raise ConfigInvalid({"resilience.retry.cap_seconds": "below base_seconds"})
    return out


def backoff_delay(i, base, factor, cap, jitter=None):
    """Delay before retry number i (0-based): min(cap, base * factor**i); `jitter(d)` (injected, e.g. full jitter) is clamped into [0, d]."""
    d = min(float(cap), float(base) * (int(factor) ** int(i)))
    if jitter is not None:
        d = max(0.0, min(d, float(jitter(d))))
    return d


class RetryBudget(object):
    def __init__(self, percent, cap, initial=None):
        self.percent, self.cap = int(percent), int(cap) * 100
        self._tokens = self.cap if initial is None else min(self.cap, int(initial) * 100)
        self._lock = threading.Lock()
        self.retries_granted = 0
        self.retries_denied = 0

    def deposit(self):
        with self._lock:
            self._tokens = min(self.cap, self._tokens + self.percent)

    def withdraw(self):
        with self._lock:
            if self._tokens >= 100:
                self._tokens -= 100
                self.retries_granted += 1
                return True
            self.retries_denied += 1
            return False

    @property
    def tokens(self):
        return self._tokens / 100.0


CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"


class Breaker(object):
    def __init__(self, failure_threshold, cooldown_seconds, clock, half_open_probes=1):
        self.threshold, self.cooldown, self.probes_max, self.clock = int(failure_threshold), cooldown_seconds, int(half_open_probes), clock
        self._lock = threading.Lock()
        self._state, self._failures, self._opened_at, self._probes = CLOSED, 0, None, 0
        self.rejected = 0
        self.opened_count = 0

    def _refresh(self, now):
        if self._state == OPEN:
            if now < self._opened_at:       # the clock moved back: restart the cooldown from the current reading (fail closed)
                self._opened_at = now
            elif now - self._opened_at >= self.cooldown:
                self._state, self._probes = HALF_OPEN, 0

    @property
    def state(self):
        with self._lock:
            self._refresh(self.clock())
            return self._state

    def allow(self):
        """(True, 0) when a call may go to the dependency, else (False, whole seconds >= 1 until a probe is allowed)."""
        with self._lock:
            now = self.clock()
            self._refresh(now)
            if self._state == CLOSED:
                return True, 0
            if self._state == HALF_OPEN and self._probes < self.probes_max:
                self._probes += 1
                return True, 0
            self.rejected += 1
            wait = 1 if self._state == HALF_OPEN else max(1, int(self._opened_at + self.cooldown - now) + 1)
            return False, wait

    def record_success(self):
        with self._lock:
            self._state, self._failures, self._opened_at, self._probes = CLOSED, 0, None, 0

    def record_failure(self):
        with self._lock:
            now = self.clock()
            self._refresh(now)
            if self._state == HALF_OPEN:
                self._trip(now)
            elif self._state == CLOSED:
                self._failures += 1
                if self._failures >= self.threshold:
                    self._trip(now)

    def cancel(self):
        """The admitted call ended in a way that says nothing about the dependency (e.g. a client error): free a probe slot, count nothing."""
        with self._lock:
            if self._state == HALF_OPEN and self._probes > 0:
                self._probes -= 1

    def _trip(self, now):
        self._state, self._opened_at, self._probes, self._failures = OPEN, now, 0, 0
        self.opened_count += 1

    def snapshot(self):
        with self._lock:
            return {"state": self._state, "failures": self._failures, "opened_at": self._opened_at}

    def restore(self, snap):
        """Adopt a snapshot (unknown / malformed -> stay CLOSED is NOT done: a malformed snapshot is ConfigInvalid so the caller decides)."""
        ok = (isinstance(snap, dict) and snap.get("state") in (CLOSED, OPEN, HALF_OPEN) and isinstance(snap.get("failures"), int)
              and not isinstance(snap.get("failures"), bool) and (snap.get("opened_at") is None or _num(snap.get("opened_at"))))
        if not ok or (snap["state"] != CLOSED and snap.get("opened_at") is None):
            raise ConfigInvalid({"breaker_snapshot": "malformed"})
        with self._lock:
            self._state, self._failures, self._opened_at, self._probes = snap["state"], snap["failures"], snap["opened_at"], 0


class BulkheadFull(Exception):
    """Internal signal of Bulkhead.slot(); callers translate it (it never reaches a client as a traceback)."""


class Bulkhead(object):
    def __init__(self, max_concurrent):
        self.max, self._n, self._lock = int(max_concurrent), 0, threading.Lock()
        self.rejected, self.peak = 0, 0

    def try_enter(self):
        with self._lock:
            if self._n >= self.max:
                self.rejected += 1
                return False
            self._n += 1
            self.peak = max(self.peak, self._n)
            return True

    def leave(self):
        with self._lock:
            self._n = max(0, self._n - 1)

    @property
    def in_flight(self):
        return self._n
