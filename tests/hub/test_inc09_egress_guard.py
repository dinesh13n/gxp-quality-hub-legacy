"""INC-09 egress check (AC-CO-12 for INC-09, PNFR-18; same split as INC-05 .. INC-08): the INC-09 test modules (the 20 planned I9_ tests and the
INC-09 supplementary tests) run in an inner process with the egress guard installed -> suite green, zero egress attempts, model_calls_total = 0, no
skipped test. INC-09 opens no listener socket (in-process WebApp only), so no loopback exception is needed beyond the guard's existing one.

TST-CO-12 (frozen) skips the INC-09 modules in its inner run (HUB_EGRESS_INNER) so group C keeps its size. Recursion guard: HUB_EGRESS_INNER9.
"""
import json
import os
import subprocess
import sys
import unittest

import _support as S


def setUpModule():
    if os.environ.get("HUB_EGRESS_INNER") or os.environ.get("HUB_EGRESS_INNER9"):
        raise unittest.SkipTest("outer driver of the INC-09 egress-guarded run")
    S.require_sandbox()


class TST_HUB_E09EGRESS_Guard(unittest.TestCase):

    def test_TST_HUB_E09EGRESS_S90_inc09_suite_under_egress_guard(self):
        """S90: INC-09 modules under the egress guard -> green, 0 egress attempts, model_calls_total = 0, nothing skipped."""
        out = os.path.join(S.tmpdir("e09-"), "inner.json")
        env = S.child_env({"HUB_EGRESS_INNER9": "1"})
        cmd = [sys.executable, "-B", os.path.join(S.CODE_ROOT, "tests", "hub", "_driver.py"), "--out", out, "--egress-guard", "-k", "I9_", "-k", "INC09_S"]
        p = subprocess.run(cmd, cwd=S.CODE_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=900)
        with open(out, encoding="utf-8") as f:
            res = json.load(f)
        self.assertTrue(res["successful"], p.stdout[-3000:])
        ok = sum(1 for r in res["records"] if r["status"] == "ok")
        self.assertGreaterEqual(ok, 20 + 13)
        self.assertEqual([r for r in res["records"] if r["status"] == "skipped"], [])
        self.assertEqual(res["egress_attempts"], [])
        self.assertEqual(res["tripwires"], {"egress_attempts_total": 0, "model_calls_total": 0})


if __name__ == "__main__":
    unittest.main()
