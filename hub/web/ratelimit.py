"""Per-peer limiter for REJECTED requests (Stage 27, S24 DQ-S24-09 / RS-04, S27-DEV-07). Pure standard library, no clock of its own.

What it counts: requests that were refused before any identity was established - 401 (no / unknown / bad credentials) and 403 for a route that is not
registered. What it does when a peer has `max_rejected` such refusals inside `window_seconds`: every further request from that peer is answered
429 E-REQ-RATE-LIMITED (Retry-After) WITHOUT opening the store and WITHOUT an audit row, so a flood no longer grows the audit log (S26 A07 / RS-04) and
costs the server almost nothing. Authenticated traffic, 4xx validation errors and role refusals do not count.

Limits of the design (recorded as residual risk, not hidden): on the loopback-only listener every local client has the same peer address, so while a
flood is blocked a legitimate local client is blocked too for at most `window_seconds` (fail closed; a restart clears the state). Per-process memory only;
at most MAX_PEERS peers are tracked (the oldest idle peer is dropped first). Time comes from the caller (the injected application clock).
Defaults (rate_limit.enabled true, window_seconds 60, max_rejected 100) are Stage 27 ASSUMPTIONS A-27-04, not measured needs.
"""
import collections
import threading

from hub.core.errors import ConfigInvalid

DEFAULTS = {"enabled": True, "window_seconds": 60, "max_rejected": 100}
MAX_PEERS = 1024


def resolve(cfg):
    s = dict(DEFAULTS)
    over = (cfg or {}).get("rate_limit")
    if over is not None:
        if not isinstance(over, dict):
            raise ConfigInvalid({"rate_limit": "must be an object"})
        s.update(over)
    if not isinstance(s["enabled"], bool):
        raise ConfigInvalid({"rate_limit.enabled": "boolean"})
    for k, hi in (("window_seconds", 86400), ("max_rejected", 1000000)):
        v = s[k]
        if isinstance(v, bool) or not isinstance(v, int) or v < 1 or v > hi:
            raise ConfigInvalid({"rate_limit." + k: str(v)[:20], "allowed": [1, hi]})
    return s


class RejectLimiter(object):
    def __init__(self, settings):
        self.enabled, self.window, self.limit = settings["enabled"], settings["window_seconds"], settings["max_rejected"]
        self._lock = threading.Lock()
        self._peers = collections.OrderedDict()

    def _prune(self, q, now):
        while q and (now - q[0] >= self.window or q[0] > now + self.window):  # an entry from the future (clock rolled back) is dropped too
            q.popleft()

    def blocked(self, peer, now):
        """0 when the peer may proceed, else the whole seconds (>= 1) until its oldest counted refusal leaves the window."""
        if not self.enabled:
            return 0
        with self._lock:
            q = self._peers.get(peer)
            if q is None:
                return 0
            self._prune(q, now)
            if len(q) < self.limit:
                if not q:
                    del self._peers[peer]
                return 0
            return max(1, int(q[0] + self.window - now) + 1)

    def record(self, peer, now):
        if not self.enabled:
            return
        with self._lock:
            q = self._peers.get(peer)
            if q is None:
                while len(self._peers) >= MAX_PEERS:
                    self._peers.popitem(last=False)
                q = self._peers[peer] = collections.deque()
            self._prune(q, now)
            q.append(now)
            self._peers.move_to_end(peer)
