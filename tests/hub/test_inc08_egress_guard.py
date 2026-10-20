"""INC-08 egress check (AC-CO-12 for INC-08, PNFR-18; same split as INC-05 .. INC-07): the INC-08 test modules (TST-GATE-*, TST-REV-*, TST-NFR-*, TST-CO-08,
the I8_ HTTP-surface tests and the INC-08 supplementary tests) run in an inner process with the egress guard installed -> suite green, zero non-loopback
connection attempts, model_calls_total = 0, no skipped test.

Documented exception (inc08-design-notes D-12): the tests open real listener sockets on 127.0.0.1 (ephemeral ports) and connect to them. The egress guard
already allows loopback and refuses everything else, so no relaxation of the guard is needed; the exception is confined to 127.0.0.1 and the inner run still
asserts egress_attempts == [].

TST-CO-12 (frozen) skips the INC-08 modules in its inner run (HUB_EGRESS_INNER) so group C keeps its size. This module is skipped inside both inner runs.
Recursion guard: HUB_EGRESS_INNER8. The inner selectors do not match this class or method name.
"""
import json
import os
import subprocess
import sys
import unittest

import _support as S


def setUpModule():
    if os.environ.get("HUB_EGRESS_INNER") or os.environ.get("HUB_EGRESS_INNER8"):
        raise unittest.SkipTest("outer driver of the INC-08 egress-guarded run")
    S.require_sandbox()


class TST_HUB_E08EGRESS_Guard(unittest.TestCase):

    def test_TST_HUB_E08EGRESS_S90_inc08_suite_under_egress_guard(self):
        """S90: INC-08 modules under the egress guard -> green, 0 egress attempts, model_calls_total = 0, nothing skipped."""
        out = os.path.join(S.tmpdir("e08-"), "inner.json")
        env = S.child_env({"HUB_EGRESS_INNER8": "1"})
        cmd = [sys.executable, "-B", os.path.join(S.CODE_ROOT, "tests", "hub", "_driver.py"), "--out", out, "--egress-guard",
               "-k", "TST_GATE", "-k", "TST_REV", "-k", "TST_NFR", "-k", "TST_CO_08", "-k", "I8_", "-k", "INC08_S"]
        p = subprocess.run(cmd, cwd=S.CODE_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=900)
        with open(out, encoding="utf-8") as f:
            res = json.load(f)
        self.assertTrue(res["successful"], p.stdout[-3000:])
        ok = sum(1 for r in res["records"] if r["status"] == "ok")
        self.assertGreaterEqual(ok, 22 + 13 + 17 + 1 + 11 + 14)
        self.assertEqual([r for r in res["records"] if r["status"] == "skipped"], [])
        self.assertEqual(res["egress_attempts"], [])
        self.assertEqual(res["tripwires"], {"egress_attempts_total": 0, "model_calls_total": 0})


if __name__ == "__main__":
    unittest.main()
