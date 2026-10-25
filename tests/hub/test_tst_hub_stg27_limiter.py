"""Stage 27 tests, part 2: the per-peer limiter for rejected requests (RS-04, DQ-S24-09; assumption A-27-04; deviation S27-DEV-07). Synthetic, unvalidated.

  L01  settings: defaults, every invalid value refused with ConfigInvalid, the section is part of the closed config key set
  L02  RejectLimiter unit behaviour: threshold, Retry-After, window expiry, per-peer isolation, disabled, clock rollback, bounded memory
  L03  integration: over the limit -> 429 with Retry-After and NO audit row and NO store write; authenticated traffic is never counted; other peers and the next window are fine
  L04  the limiter answers before the store is opened (a read-only / corrupt store is still 429 for a blocked peer, 503 for a peer that is not blocked)
"""
import json
import os
import threading
import unittest

import _inc08 as W
import _stg26 as T26
import _stg27 as T
from hub import config as hubconfig
from hub.core.errors import ConfigInvalid
from hub.web import ratelimit
from hub.web.app import Request, WebApp


def setUpModule():
    T.skip_in_inner_egress_run()


class TST_HUB_STG27_Limiter(unittest.TestCase):
    def store(self, **limits):
        st = W.WStore(loaded=False, extra={"rate_limit": dict({"enabled": True, "window_seconds": 60, "max_rejected": 5}, **limits)})
        self.addCleanup(st.close)
        return st

    def hit(self, st, path="/nope", peer="127.0.0.1", token=None, method="GET"):
        h = {"Authorization": "Bearer " + token} if token else {}
        r = st.app.handle(Request(method, path, {}, h, b"", peer=peer))
        st.app.last_exception = None
        return r

    @staticmethod
    def code(r):
        try:
            return json.loads(r.body)["error"]["code"]
        except ValueError:
            return None

    def test_TST_HUB_STG27_L01_settings_defaults_and_validation(self):
        """L01: defaults are enabled / 60 s / 100 (A-27-04); every out-of-range, wrong-type, bool-as-int or non-object value is ConfigInvalid; unknown keys inside rate_limit are refused by the config."""
        self.assertEqual(ratelimit.resolve({}), {"enabled": True, "window_seconds": 60, "max_rejected": 100})
        self.assertEqual(ratelimit.resolve({"rate_limit": {"max_rejected": 7}})["max_rejected"], 7)
        self.assertEqual(ratelimit.resolve({"rate_limit": {"enabled": False}})["enabled"], False)
        for bad in ({"enabled": "yes"}, {"enabled": 1}, {"window_seconds": 0}, {"window_seconds": -1}, {"window_seconds": 86401}, {"window_seconds": "60"},
                    {"window_seconds": 1.5}, {"window_seconds": True}, {"max_rejected": 0}, {"max_rejected": 1000001}, {"max_rejected": None}, {"max_rejected": [1]}):
            with self.assertRaises(ConfigInvalid, msg=repr(bad)):
                ratelimit.resolve({"rate_limit": bad})
        for bad in ("on", 5, [], True):
            with self.assertRaises(ConfigInvalid, msg=repr(bad)):
                ratelimit.resolve({"rate_limit": bad})
        self.assertEqual(sorted(hubconfig.KNOWN_KEYS["rate_limit"]), ["enabled", "max_rejected", "window_seconds"])
        with self.assertRaises(ConfigInvalid):
            hubconfig.validate(dict(json.loads(json.dumps(hubconfig.DEFAULTS)), rate_limit={"burst": 3}))
        with self.assertRaises(ConfigInvalid):
            WebApp(self.store().data, dict(self.store().cfg, rate_limit={"max_rejected": 0}), lambda: "2026-01-01T00:00:00Z")

    def test_TST_HUB_STG27_L02_limiter_unit_behaviour(self):
        """L02: below the limit nothing is blocked; at the limit the peer is blocked with a whole-second wait >= 1 that shrinks to the window edge; after the window the
        peer is free again; peers are independent; disabled never blocks or records; an entry from the future (clock rolled back) is dropped; tracked peers are bounded; concurrent
        record() calls from threads lose no entry."""
        lim = ratelimit.RejectLimiter({"enabled": True, "window_seconds": 10, "max_rejected": 3})
        for i in range(2):
            lim.record("a", 100 + i)
        self.assertEqual(lim.blocked("a", 102), 0)
        lim.record("a", 102)
        self.assertEqual(lim.blocked("a", 102), 9)  # oldest at 100, window 10 -> free at 110 -> int(8)+1
        self.assertGreaterEqual(lim.blocked("a", 109.5), 1)
        self.assertEqual(lim.blocked("b", 102), 0)
        self.assertEqual(lim.blocked("a", 110), 0)  # exactly one window after the oldest -> that entry has left
        self.assertEqual(lim.blocked("a", 500), 0)
        lim.record("c", 1000)
        lim.record("c", 1001)
        lim.record("c", 1002)
        self.assertGreaterEqual(lim.blocked("c", 1003), 1)
        self.assertEqual(lim.blocked("c", 10), 0)  # clock rolled back: entries from the future do not lock the peer out
        off = ratelimit.RejectLimiter({"enabled": False, "window_seconds": 10, "max_rejected": 1})
        for i in range(5):
            off.record("a", i)
        self.assertEqual(off.blocked("a", 1), 0)
        self.assertEqual(len(off._peers), 0)
        many = ratelimit.RejectLimiter({"enabled": True, "window_seconds": 10, "max_rejected": 3})
        for i in range(ratelimit.MAX_PEERS + 50):
            many.record("p%d" % i, 1)
        self.assertLessEqual(len(many._peers), ratelimit.MAX_PEERS)
        self.assertEqual(many.blocked("p0", 1), 0)
        thr = ratelimit.RejectLimiter({"enabled": True, "window_seconds": 1000, "max_rejected": 1000})
        ts = [threading.Thread(target=lambda: [thr.record("x", 5) for _ in range(100)]) for _ in range(8)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        self.assertEqual(len(thr._peers["x"]), 800)

    def test_TST_HUB_STG27_L03_over_the_limit_is_429_without_audit_rows(self):
        """L03: with max_rejected = 5, five unauthenticated refusals are answered 403 / 401 as before (and audited as before); from the sixth request the peer gets 429 E-REQ-RATE-LIMITED
        + Retry-After + X-Correlation-Id, and NO audit row, NO session / metric row and no other store row is written. Valid authenticated requests from the same peer are never
        counted (50 of them stay 200); another peer is unaffected; after the window the blocked peer is served again; the hash chain verifies throughout."""
        st = self.store()
        for i in range(5):
            r = self.hit(st, "/nope/%d" % i)
            self.assertEqual((r.status, self.code(r)), (403, "E-AUTH-FORBIDDEN"))
        a0 = st.count("audit_log")
        snap = T26.snapshot(st)
        for i in range(30):
            r = self.hit(st, "/api/v2/policies")  # a registered route, no token: would be 401 and an audit row without the limiter
            self.assertEqual((r.status, self.code(r)), (429, "E-REQ-RATE-LIMITED"), i)
            hdr = dict(r.headers)
            self.assertGreaterEqual(int(hdr["Retry-After"]), 1)
            self.assertIn("X-Correlation-Id", hdr)
        self.assertEqual(st.count("audit_log"), a0)
        self.assertEqual(T26.diff(snap, T26.snapshot(st)), [])
        other = self.hit(st, "/nope", peer="10.9.9.9")
        self.assertEqual(other.status, 403)  # a different peer has its own window
        # a valid session is still refused while the peer is blocked (pre-identity check, fail closed) - documented limit on the shared loopback peer
        self.assertEqual(self.hit(st, "/api/v2/policies", token=st.tokens["rev"]).status, 429)
        st.clock.advance(61)
        self.assertEqual(self.hit(st, "/api/v2/policies", token=st.tokens["rev"]).status, 200)
        self.assertEqual(self.hit(st, "/nope").status, 403)
        self.assertEqual(T26.verify_chain(st)["status"], "ok")

    def test_TST_HUB_STG27_L03b_authenticated_traffic_is_never_counted(self):
        """L03b: 60 valid authenticated requests, 20 role refusals (403 on a registered route for a known principal) and 20 validation errors (400) from one peer never block it: only
        refusals BEFORE an identity exists count."""
        st = self.store()
        for _ in range(60):
            self.assertEqual(self.hit(st, "/api/v2/policies", token=st.tokens["rev"]).status, 200)
        for _ in range(20):
            r = self.hit(st, "/api/v2/policies", token=st.tokens["rev"], method="POST")
            self.assertIn(r.status, (400, 403, 422))
        for _ in range(20):
            r = st.app.handle(Request("POST", "/api/v2/auth/login", {}, {"Content-Type": "application/json", "X-Hub-Request": "1"}, b"{", peer="127.0.0.1"))
            self.assertEqual(r.status, 400)
        self.assertEqual(self.hit(st, "/api/v2/policies", token=st.tokens["rev"]).status, 200)
        self.assertEqual(self.hit(st, "/nope").status, 403)

    def test_TST_HUB_STG27_L04_blocked_peer_never_reaches_the_store(self):
        """L04: the limiter answers before the store is opened. Make every store open fail: a blocked peer still gets 429, a peer that is not blocked gets the 503 of a store fault."""
        st = self.store()
        for i in range(5):
            self.hit(st, "/nope/%d" % i)
        calls = []

        def broken():
            calls.append(1)
            import sqlite3
            raise sqlite3.OperationalError("unable to open database file")
        st.app._connect = broken
        r = self.hit(st, "/api/v2/policies")
        self.assertEqual((r.status, self.code(r)), (429, "E-REQ-RATE-LIMITED"))
        self.assertEqual(calls, [])
        r = self.hit(st, "/api/v2/policies", peer="10.1.1.1")
        self.assertEqual((r.status, self.code(r)), (503, "E-STORE-UNAVAILABLE"))
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
