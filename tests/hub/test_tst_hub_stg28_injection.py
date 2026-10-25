"""Stage 28 tests, part 2: failure injection (docs/28-reliability/failure-injection-plan.md). Synthetic, unvalidated. Sandbox stores, loopback doubles and fake clocks only.

  F01  source down (connection refused): bounded attempts, then the breaker opens and later calls never touch the source
  F02  retry storm: 200 calls against a failing source -> attempts bounded by the retry budget; with the default breaker the source sees 12 requests, not 800
  F03  source accepts and never answers: per-attempt timeout, bounded, breaker counts one failure
  F04  recovery: cooldown -> one probe -> close; a failed probe re-opens; only one probe in flight
  F05  shape error fails fast (FG-01 / DQ-S21-03), client error is never retried and never opens the breaker
  F06  bulkhead: a second concurrent pull is refused at once while the first is in flight
  F07  listener connection cap: the excess connection is shed with 429, no audit row, the service recovers when the idle ones go
  F08  degraded-mode usefulness: source down -> run recorded as failed with 0 rows, health / reads / chain verification keep working
"""
import json
import threading
import time
import unittest

import _http8 as H
import _inc06 as I
import _inc08 as W
import _stg21 as T21
import _stg26 as T26
import _stg28 as T
from hub.adapters import gateway_client
from hub.intake import errors as E
from hub.resilience import policy
from hub.web.bounded_server import make_bounded_server
from hub.resilience.guarded import GuardedGateway, classify


def setUpModule():
    T.skip_in_inner_egress_run()


class TST_HUB_STG28_Injection(unittest.TestCase):
    def gw(self, url, settings=None, clock=None, **kw):
        sleeps = []
        g = GuardedGateway(url, clock or T.FakeClock(), sleeps.append, settings, **kw)
        g.sleeps = sleeps
        return g

    def fails(self, g, **kw):
        with self.assertRaises(E.SourceUnreachable) as cm:
            g.fetch_events(**kw)
        return cm.exception.details

    def test_TST_HUB_STG28_F01_source_down_is_bounded_then_fails_fast(self):
        """F01 (FM-01): connection refused. Each of the first 3 calls makes 1 + 3 attempts with back-off [0.5, 1, 2]; the 3rd failed call opens the breaker; call 4 is refused with reason
        circuit_open and details.attempts 0 without any connection attempt (attempts_total stays 12); the error is E-INT-SOURCE-UNREACHABLE, never data."""
        g = self.gw(T.refused_url())
        for n in (1, 2, 3):
            d = self.fails(g)
            self.assertEqual((d["reason"], d["attempts"], d["retries"]), ("retries_exhausted", 4, 3), n)
        self.assertEqual(g.sleeps, [0.5, 1.0, 2.0] * 3)
        self.assertEqual((g.breaker.state, g.attempts_total), (policy.OPEN, 12))
        d = self.fails(g)
        self.assertEqual((d["reason"], d["attempts"]), ("circuit_open", 0))
        self.assertGreaterEqual(d["retry_after_seconds"], 1)
        self.assertEqual((g.attempts_total, g.breaker.rejected, len(g.sleeps)), (12, 1, 9))
        T.write_evidence("f01-source-down.json", {"label": T.LABEL, "calls_failed": 3, "attempts": 12, "fast_fail_attempts": 0, "backoff": [0.5, 1.0, 2.0]})

    def test_TST_HUB_STG28_F02_retry_storm_is_bounded(self):
        """F02 (FM-02): 200 calls against a source answering 503. (a) breaker off in effect (threshold 1000): total requests that reach the source <= calls + cap + calls * percent / 100 = 250
        (an unguarded 1 + 3 retries each would be 800); (b) default breaker: the source sees exactly 12 requests for 200 calls (3 calls x 4 attempts), 197 calls are refused unseen."""
        st = T.Stub(503, b"{}")
        try:
            g = self.gw(st.url, {"breaker": {"failure_threshold": 1000}})
            for _ in range(200):
                self.fails(g)
            self.assertEqual(st.hits, g.attempts_total)
            self.assertLessEqual(st.hits, 200 + 10 + 200 * 20 // 100)
            self.assertLess(st.hits, 800)
            storm_a = st.hits
            st.hits = 0
            g2 = self.gw(st.url)
            reasons = {}
            for _ in range(200):
                r = self.fails(g2)["reason"]
                reasons[r] = reasons.get(r, 0) + 1
            self.assertEqual((st.hits, reasons), (12, {"retries_exhausted": 3, "circuit_open": 197}))
        finally:
            st.close()
        T.write_evidence("f02-retry-storm.json", {"label": T.LABEL, "calls": 200, "unguarded_requests": 800, "budget_only_requests": storm_a, "default_requests": 12,
                                                  "bound_budget_only": 250, "reasons_default": reasons})

    def test_TST_HUB_STG28_F03_hanging_source_times_out_once_per_attempt(self):
        """F03 (FM-03): a listener that accepts and never answers. timeout_seconds 0.3, max_retries 1 -> 2 attempts, each bounded by the timeout (whole call < 3 s), the source saw exactly 2 GETs,
        the breaker holds 1 failure."""
        hs = T21.hanging_server()
        try:
            g = self.gw(hs.url, {"retry": {"timeout_seconds": 0.3, "max_retries": 1}})
            t0 = time.time()
            d = self.fails(g)
            wall = time.time() - t0
        finally:
            hs.close()
        self.assertEqual((d["reason"], d["attempts"]), ("retries_exhausted", 2))
        self.assertIn(d["last_error"], ("TimeoutError", "timeout"))
        self.assertLess(wall, 3.0)
        self.assertEqual(len(hs.received), 2)
        self.assertEqual(g.breaker.snapshot()["failures"], 1)

    def test_TST_HUB_STG28_F04_recovery_by_probe(self):
        """F04 (FM-04): after the cooldown ONE probe goes through. 59 s: still refused unseen; 60 s: probe succeeds -> breaker closed, later calls pass; a probe that fails re-opens it and the
        cooldown restarts; while a probe is in flight a second caller is refused (half-open admits `half_open_probes`)."""
        st = T.Stub(503, b"{}")
        clock = T.FakeClock()
        try:
            g = self.gw(st.url, {"breaker": {"failure_threshold": 3, "cooldown_seconds": 60}}, clock=clock)
            for _ in range(3):
                self.fails(g)
            hits = st.hits
            clock.advance(59)
            self.assertEqual(self.fails(g)["reason"], "circuit_open")
            self.assertEqual(st.hits, hits)
            clock.advance(1)
            self.assertEqual(g.breaker.state, policy.HALF_OPEN)
            d = self.fails(g)          # the probe: still 503; the budget drained by the first 3 calls pays for one retry only
            self.assertEqual((d["reason"], d["attempts"]), ("retry_budget_exhausted", 2))
            self.assertEqual(g.breaker.state, policy.OPEN)
            clock.advance(30)
            self.assertEqual(self.fails(g)["reason"], "circuit_open")
            clock.advance(30)
            st.set(200)
            page = g.fetch_events(7, 50)
            self.assertEqual((page["next_offset"], page["attempts"], g.breaker.state), (7, 1, policy.CLOSED))
            self.assertEqual(g.fetch_events()["attempts"], 1)
        finally:
            st.close()
        seen = {}

        def probing_fetch(url, offset, limit, retries=0, timeout=5):
            seen["inner"] = self.fails(g2)["reason"]          # a second caller while the probe is in flight
            return {"items": [], "next_offset": 0}
        clock2 = T.FakeClock()
        g2 = self.gw("http://127.0.0.1:1", {"breaker": {"failure_threshold": 1, "cooldown_seconds": 10}, "bulkhead": {"max_concurrent": 2}}, clock=clock2, fetch=probing_fetch)
        g2.breaker.allow()
        g2.breaker.record_failure()
        clock2.advance(10)
        g2.fetch_events()
        self.assertEqual(seen["inner"], "circuit_open")
        self.assertEqual(g2.breaker.state, policy.CLOSED)

    def test_TST_HUB_STG28_F05_shape_and_client_errors(self):
        """F05 (FM-05, FG-01): 200 with an unexpected body -> 1 request, reason shape_error (S28-DEV-02; retry_shape_errors true restores the bounded retries: 4 requests); HTTP 400 -> 1 request,
        reason client_error, never opens the breaker however often it repeats; classify() mirrors the shipped client's error names."""
        st = T.Stub(200, b'{"foo": 1}')
        try:
            g = self.gw(st.url)
            self.assertEqual(self.fails(g)["reason"], "shape_error")
            self.assertEqual(st.hits, 1)
            st.hits = 0
            g = self.gw(st.url, {"retry": {"retry_shape_errors": True}})
            self.assertEqual(self.fails(g)["reason"], "retries_exhausted")
            self.assertEqual(st.hits, 4)
            st.set(200, b"not json")
            st.hits = 0
            self.assertEqual(self.fails(self.gw(st.url))["reason"], "shape_error")
            self.assertEqual(st.hits, 1)
            st.set(400, b"{}")
            st.hits = 0
            g = self.gw(st.url)
            for _ in range(10):
                d = self.fails(g)
                self.assertEqual((d["reason"], d["attempts"]), ("client_error", 1))
            self.assertEqual((st.hits, g.breaker.state, g.breaker.snapshot()["failures"]), (10, policy.CLOSED, 0))
            st.set(429, b"{}")
            st.hits = 0
            self.assertEqual(self.fails(self.gw(st.url))["reason"], "retries_exhausted")
            self.assertEqual(st.hits, 4)
        finally:
            st.close()
        self.assertEqual([classify(x) for x in ("http_400", "http_404", "http_429", "http_500", "http_503", "ValueError", "JSONDecodeError", "URLError", "TimeoutError", None)],
                         ["client", "client", "transient", "transient", "transient", "shape", "shape", "transient", "transient", "transient"])

    def test_TST_HUB_STG28_F06_bulkhead_refuses_a_concurrent_pull(self):
        """F06 (FM-06): while one pull is in flight (silent source) a second pull is refused at once (reason bulkhead_full, 0 attempts, < 0.5 s), the source sees one request, and the bulkhead
        refusal does not count against the breaker."""
        hs = T21.hanging_server()
        try:
            g = self.gw(hs.url, {"retry": {"timeout_seconds": 1, "max_retries": 0}})
            box = {}
            t = threading.Thread(target=lambda: box.setdefault("d", self.fails(g)))
            t.start()
            for _ in range(100):
                if g.bulkhead.in_flight == 1:
                    break
                threading.Event().wait(0.02)
            t0 = time.time()
            d = self.fails(g)
            self.assertLess(time.time() - t0, 0.5)
            self.assertEqual((d["reason"], d["attempts"]), ("bulkhead_full", 0))
            t.join(10)
        finally:
            hs.close()
        self.assertEqual(box["d"]["attempts"], 1)
        self.assertEqual((len(hs.received), g.breaker.snapshot()["failures"], g.bulkhead.in_flight, g.bulkhead.rejected), (1, 1, 0, 1))

    def test_TST_HUB_STG28_F07_listener_connection_cap(self):
        """F07 (FM-07, F-CAP-01): BoundedLoopbackServer(max 3): with 3 idle connections held, the 4th is answered 429 E-REQ-RATE-LIMITED + Retry-After at once, no audit row is written and the
        store is not touched; when the idle connections end (read timeout 1 s) /healthz answers 200 again. The shipped LoopbackServer has no such cap (static: no bulkhead attribute)."""
        from hub.web import server
        self.assertFalse(hasattr(server.LoopbackServer, "bulkhead"))
        st = W.WStore(loaded=False)
        self.addCleanup(st.close)
        srv = make_bounded_server(st.app, 0, read_timeout=1, max_connections=3)
        th = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        th.start()
        host, port = srv.server_address[:2]
        import socket
        idle = []
        try:
            a0 = T26.audit_n(st)
            for _ in range(3):
                s = socket.create_connection((host, port), timeout=5)
                idle.append(s)
            for _ in range(100):
                if srv.bulkhead.in_flight == 3:
                    break
                threading.Event().wait(0.02)
            self.assertEqual(srv.bulkhead.in_flight, 3)
            r = H.raw(host, port, b"GET /healthz HTTP/1.1\r\nHost: x\r\n\r\n")
            self.assertEqual(r.status, 429)
            self.assertEqual(r.json()["error"]["code"], "E-REQ-RATE-LIMITED")
            self.assertEqual(r.headers.get("retry-after"), "1")
            self.assertEqual(T26.audit_n(st), a0)
            self.assertGreaterEqual(srv.bulkhead.rejected, 1)
            for _ in range(60):
                if srv.bulkhead.in_flight == 0:
                    break
                threading.Event().wait(0.1)
            self.assertEqual(srv.bulkhead.in_flight, 0, "idle connections must end at the read timeout")
            r = H.raw(host, port, b"GET /healthz HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n")
            self.assertEqual(r.status, 200)
            self.assertLessEqual(srv.bulkhead.peak, 3)
        finally:
            for s in idle:
                s.close()
            srv.shutdown()
            srv.server_close()
            th.join(5)

    def test_TST_HUB_STG28_F08_source_down_hub_stays_useful(self):
        """F08 (FM-01 degraded mode): the source is down. The failed pull is a RUN_FAILED record with 0 raw rows and 0 outcomes (nothing fabricated); /healthz and an authorised read still answer
        200; the audit chain verifies; once the source is back the next pull proceeds (breaker closed after the probe)."""
        st = W.WStore(loaded=False)
        self.addCleanup(st.close)
        clock = T.FakeClock()
        g = self.gw(T.refused_url(), {"breaker": {"failure_threshold": 1, "cooldown_seconds": 5}}, clock=clock)
        d = self.fails(g)
        rep = st.isvc.fail_run("gateway", "s28-f08", "SOURCE_UNREACHABLE", d, "s28")
        self.assertEqual(rep["status"], "failed")
        c = st.isvc.counts()
        self.assertEqual((c["raw"], c["outcomes"]), (0, 0))
        self.assertEqual(st.get("/healthz").status, 200)
        rev = {"Authorization": "Bearer " + st.tokens["rev"], "X-Hub-Request": "1"}
        from hub.web.app import Request
        r = st.app.handle(Request("GET", "/api/v2/policies", {}, rev, b"", peer="127.0.0.1"))
        self.assertEqual(r.status, 200)
        st.app.last_exception = None
        self.assertEqual(T26.verify_chain(st)["status"], "ok")
        sv = T.Stub(200)
        try:
            g2 = self.gw(sv.url, {"breaker": {"cooldown_seconds": 5}}, clock=clock)
            g2.breaker.restore(g.breaker.snapshot())
            self.assertEqual(self.fails(g2)["reason"], "circuit_open")
            clock.advance(5)
            self.assertEqual(g2.fetch_events(0, 50)["next_offset"], 7)
        finally:
            sv.close()


if __name__ == "__main__":
    unittest.main()
