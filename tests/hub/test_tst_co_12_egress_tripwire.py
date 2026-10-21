"""TST-CO-12 (AC-CO-12, FR-CO-04, PNFR-18, BEH-CO-07, BEH-OBS-06) - the full INC-02 acceptance suite runs
with socket connect patched to record attempts: zero non-loopback connection attempts and
model_calls_total = 0. Plus unit checks of the egress guard and the zero-tripwire.

Recursion guard: the inner (egress-guarded) suite run sets HUB_EGRESS_INNER=1 and this module is skipped
there, because its unit tests deliberately provoke (blocked) egress attempts.

Stage 20 (DW-03, OD-21: group C was ~145 s of the 180 s device-call cap): the inner run is split into two module shards
(`_driver.py --shard K/3`, a partition by construction) run by tests e1, e2 and e3, so the regression manifest can put them
in separate device calls (groups C1 / C2 / C3 in tests/hub/regression_groups.json). Assertions per shard are unchanged except the
minimum ok count, which is split (25 -> >= 8 per shard).
"""
import ast
import json
import os
import socket
import subprocess
import sys
import unittest

import _support as S
from hub.core.errors import EgressAttempt, TripwireTripped
from hub.guards import egress
from hub.obs import metrics


def setUpModule():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("TST-CO-12 is the outer driver of the egress-guarded run")
    S.require_sandbox()


class TST_CO_12_EgressAndTripwire(unittest.TestCase):

    def setUp(self):
        self._was = egress.installed()
        egress.install()
        egress.reset()
        metrics.reset()

    def tearDown(self):
        if not self._was:
            egress.uninstall()
        egress.reset()
        metrics.reset()

    def test_TST_CO_12_a_non_loopback_refused_before_send(self):
        """TST-CO-12: connect/connect_ex/sendto/getaddrinfo to non-loopback targets raise E-CO-EGRESS-ATTEMPT and are counted."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with self.assertRaises(EgressAttempt):
                s.connect(("203.0.113.10", 9))  # TEST-NET-3: blocked before any packet
            with self.assertRaises(EgressAttempt):
                s.connect_ex(("198.51.100.7", 443))
        finally:
            s.close()
        u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            with self.assertRaises(EgressAttempt):
                u.sendto(b"x", ("192.0.2.1", 53))
        finally:
            u.close()
        with self.assertRaises(EgressAttempt):
            socket.getaddrinfo("api.example.invalid", 443)
        self.assertEqual(metrics.value("egress_attempts_total"), 4)
        self.assertEqual([a["op"] for a in egress.attempts()], ["connect", "connect_ex", "sendto", "getaddrinfo"])

    def test_TST_CO_12_b_loopback_allowed(self):
        """TST-CO-12: loopback (the legacy gateway's only network, ADR-015) is allowed and not counted."""
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        c = socket.create_connection(srv.getsockname(), timeout=5)
        conn, _ = srv.accept()
        for x in (c, conn, srv):
            x.close()
        self.assertEqual(metrics.tripwires(), {"egress_attempts_total": 0, "model_calls_total": 0})

    def test_TST_CO_12_c_model_call_tripwire(self):
        """TST-CO-12 / BEH-OBS-06: model_calls_total starts at 0; any recorded model call trips E-OBS-TRIPWIRE."""
        self.assertEqual(metrics.check_tripwires()["model_calls_total"], 0)
        metrics.record_model_call("synthetic-test")
        with self.assertRaises(TripwireTripped):
            metrics.check_tripwires()

    def test_TST_CO_12_d_no_model_call_sites_in_product(self):
        """TST-CO-12: no hub module calls record_model_call (the sensor exists only for future re-qualification)."""
        calls = []
        for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            for fn in fns:
                if fn.endswith(".py"):
                    p = os.path.join(d, fn)
                    for n in ast.walk(ast.parse(open(p, encoding="utf-8").read())):
                        if isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", None)) == "record_model_call":
                            calls.append(p)
        self.assertEqual(calls, [])

    def _inner_shard(self, k):
        out = os.path.join(S.tmpdir("co12e%d-" % k), "inner.json")
        env = S.child_env({"HUB_EGRESS_INNER": "1"})
        p = subprocess.run([sys.executable, "-B", os.path.join(S.CODE_ROOT, "tests", "hub", "_driver.py"),
                            "--out", out, "--egress-guard", "--shard", "%d/3" % k], cwd=S.CODE_ROOT, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, universal_newlines=True, timeout=600)
        with open(out, encoding="utf-8") as f:
            res = json.load(f)
        self.assertTrue(res["successful"], p.stdout[-3000:])
        self.assertGreaterEqual(sum(1 for r in res["records"] if r["status"] == "ok"), 8)
        self.assertEqual(res["egress_attempts"], [])
        self.assertEqual(res["tripwires"], {"egress_attempts_total": 0, "model_calls_total": 0})

    def test_TST_CO_12_e1_full_suite_under_egress_guard_shard1(self):
        """TST-CO-12 / AC-CO-12 (shard 1/3): full INC-02 suite (all other tests) with the egress guard installed ->
        suite green, zero non-loopback attempts, model_calls_total = 0 (CLI children also install the guard)."""
        self._inner_shard(1)

    def test_TST_CO_12_e2_full_suite_under_egress_guard_shard2(self):
        """TST-CO-12 / AC-CO-12 (shard 2/3): as e1 for the second module shard (Stage 20 DW-03 split of group C)."""
        self._inner_shard(2)

    def test_TST_CO_12_e3_full_suite_under_egress_guard_shard3(self):
        """TST-CO-12 / AC-CO-12 (shard 3/3): as e1 for the third module shard (Stage 20 DW-03 split of group C)."""
        self._inner_shard(3)


if __name__ == "__main__":
    unittest.main()
