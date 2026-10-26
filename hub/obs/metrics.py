"""Process-local counters and the No-AI zero-tripwires (observability-spec BEH-OBS-06, PNFR-18, OD-08).

`model_calls_total` is the Stage 32 tripwire. Since Stage 44 (OD-40) the product has ONE optional model client,
hub/adapters/azure_openai.py (off by default). It is the only caller of `record_model_call`, and it calls it only when it is
reached WITHOUT the ai.enabled gate (then it opens no socket and refuses): a model path used outside the gate makes the
release gate G5 fail. A gated advisory call increments `ai_advisory_calls_total` instead (a counter, not a tripwire).
`egress_attempts_total` is incremented by the egress guard. The two tripwires are exported at the end of every CLI run and must equal 0.
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
    """Tripwire sensor. Called only by hub/adapters/azure_openai.py when its client is used without the ai.enabled gate (OD-08, OD-40)."""
    inc("model_calls_total")


def check_tripwires():
    from hub.core.errors import TripwireTripped
    bad = dict((k, v) for k, v in tripwires().items() if v)
    if bad:
        raise TripwireTripped(bad)
    return tripwires()


reset()
