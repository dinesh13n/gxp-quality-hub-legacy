"""HTTP observability metrics (observability-spec OBS-4, BEH-OBS-05; RTD-60 closed for the HTTP part in INC-08).

  http_requests_total{op_id,status}            counter    in-process; written to obs_metric by `snapshot`
  http_request_duration_ms{op_id}              histogram  {count, sum_ms, max_ms}
  auth_failures_total{reason}                  counter    in-process
  override_total{action}                       counter    derived from the insert-only flag_action table (re-computable)
  defaulted_outputs_total{function}            counter    derived from the stored rule traces (defaulted results)
Durations come from the injected clock (no `time` import). Labels are closed sets (op ids from the registries, numeric status, fixed reasons): no user
text can become a label. Counters are process-local; `snapshot(con)` appends insert-only obs_metric rows (the same table as hub.obs.collect).
"""
import json
import threading

from hub.obs import collect
from hub.security.canonical import canonical

REASONS = ("unauthenticated", "session_expired", "bad_credentials", "locked", "forbidden", "csrf", "unknown_route", "zone_h_denied", "rate_limited")


class HttpMetrics(object):
    def __init__(self):
        self._lock = threading.Lock()
        self.requests, self.durations, self.auth_failures = {}, {}, {}

    def request(self, op_id, status, ms):
        with self._lock:
            k = (op_id, int(status))
            self.requests[k] = self.requests.get(k, 0) + 1
            d = self.durations.setdefault(op_id, {"count": 0, "sum_ms": 0.0, "max_ms": 0.0})
            d["count"] += 1
            d["sum_ms"] += ms
            d["max_ms"] = max(d["max_ms"], ms)

    def auth_failure(self, reason):
        with self._lock:
            reason = reason if reason in REASONS else "forbidden"
            self.auth_failures[reason] = self.auth_failures.get(reason, 0) + 1

    def samples(self, con=None):
        out = []
        with self._lock:
            for (op, st), n in sorted(self.requests.items()):
                out.append(collect._s("http_requests_total", "counter", {"op_id": op, "status": str(st)}, n))
            for op, d in sorted(self.durations.items()):
                out.append(collect._s("http_request_duration_ms", "histogram", {"op_id": op},
                                      canonical({"count": d["count"], "max_ms": round(d["max_ms"], 3), "sum_ms": round(d["sum_ms"], 3)})))
            for r, n in sorted(self.auth_failures.items()):
                out.append(collect._s("auth_failures_total", "counter", {"reason": r}, n))
        if con is not None:
            out += derived(con)
        return sorted(out, key=lambda s: (s["name"], canonical(s["labels"])))

    def snapshot(self, con, clock, run_id=None):
        """Append the current samples as insert-only obs_metric rows (no other transaction may be open)."""
        return collect.snapshot(con, clock, self.samples(con), run_id)


def derived(con):
    out = []
    for action, n in con.execute("SELECT action, count(*) FROM flag_action GROUP BY 1 ORDER BY 1"):
        out.append(collect._s("override_total", "counter", {"action": action}, n))
    counts = {}
    for fn, res in con.execute('SELECT "function", result FROM rule_trace ORDER BY trace_id'):
        if json.loads(res).get("defaulted"):
            counts[fn] = counts.get(fn, 0) + 1
    for fn, n in sorted(counts.items()):
        out.append(collect._s("defaulted_outputs_total", "counter", {"function": fn}, n))
    return out
