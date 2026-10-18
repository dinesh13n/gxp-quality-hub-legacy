"""Process-local counters and the No-AI zero-tripwires (observability-spec BEH-OBS-06, PNFR-18, OD-08).

`model_calls_total` is the Stage 32 tripwire: the product has no model client, so nothing increments it.
`record_model_call` exists only as the sensor any future (re-qualified, Dinesh-approved) AI element would be
obliged to call; calling it makes the release gate G5 fail. `egress_attempts_total` is incremented by the
egress guard. Both are exported at the end of every CLI run and must equal 0.
"""
import threading

TRIPWIRES = ("model_calls_total", "egress_attempts_total")
_lock = threading.Lock()
_counters = {}


def reset():
    with _lock:
        _counters.clear()
        for name in TRIPWIRES:
            _counters[name] = 0


def inc(name, n=1):
    with _lock:
        _counters[name] = _counters.get(name, 0) + n


def value(name):
    with _lock:
        return _counters.get(name, 0)


def snapshot():
    with _lock:
        return dict(sorted(_counters.items()))


def tripwires():
    snap = snapshot()
    return dict((k, snap.get(k, 0)) for k in TRIPWIRES)


def record_model_call(provider="unknown"):
    """Tripwire sensor. Must never be reached in a No-AI product (OD-08)."""
    inc("model_calls_total")


def check_tripwires():
    from hub.core.errors import TripwireTripped
    bad = dict((k, v) for k, v in tripwires().items() if v)
    if bad:
        raise TripwireTripped(bad)
    return tripwires()


reset()
