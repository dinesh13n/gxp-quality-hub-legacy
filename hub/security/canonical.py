"""Canonical JSON and UTC timestamps for the audit chain (BEH-SEC-05):
sorted keys, separators (",", ":"), ensure_ascii=True; timestamps YYYY-MM-DDTHH:MM:SS.ffffffZ.
The wall clock lives only in `utc_now`; every caller takes an injectable `clock` (BEH-CO-08)."""
import datetime
import hashlib
import json

GENESIS = "0" * 64
TS_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_hex(text):
    if isinstance(text, str):
        text = text.encode("utf-8")
    return hashlib.sha256(text).hexdigest()


def fmt(dt):
    if dt.tzinfo is None:
        raise ValueError("naive datetime")
    return dt.astimezone(datetime.timezone.utc).strftime(TS_FORMAT)


def parse(ts):
    return datetime.datetime.strptime(ts, TS_FORMAT).replace(tzinfo=datetime.timezone.utc)


def utc_now():
    return fmt(datetime.datetime.now(datetime.timezone.utc))


class FixedClock(object):
    """Deterministic clock for tests and rehearsals: starts at `start` and moves only when advanced
    (or by `step_us` microseconds per call, so audit timestamps stay strictly increasing)."""

    def __init__(self, start="2026-10-18T00:00:00.000000Z", step_us=1):
        self._t = parse(start)
        self._step = datetime.timedelta(microseconds=step_us)

    def advance(self, seconds):
        self._t += datetime.timedelta(seconds=seconds)

    def __call__(self):
        self._t += self._step
        return fmt(self._t)

    def seconds(self):
        return self._t.timestamp()
