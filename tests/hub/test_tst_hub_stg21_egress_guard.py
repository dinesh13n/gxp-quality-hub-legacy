"""Stage 21 egress check (AC-CO-12 for the Stage 21 tests, PNFR-18; same split as INC-05 .. INC-09 and Stage 20): the Stage 21 test modules
(STG21) run in an inner process with the egress guard installed -> suite green, zero egress attempts, model_calls_total = 0, no skipped test.
The source-gateway stub and the timeout listener are loopback only, which the guard allows (ADR-015).

TST-CO-12 skips the Stage 21 modules in its inner run (HUB_EGRESS_INNER) so groups C1 / C2 / C3 keep their size. Recursion guard:
HUB_EGRESS_INNER21.
"""
import json
import os
import subprocess
import sys
import unittest

import _support as S


def setUpModule():
    if os.environ.get("HUB_EGRESS_INNER") or os.environ.get("HUB_EGRESS_INNER21"):
        raise unittest.SkipTest("outer driver of the Stage 21 egress-guarded run")
    S.require_sandbox()


class TST_HUB_E21EGRESS_Guard(unittest.TestCase):

    def test_TST_HUB_E21EGRESS_S90_stage21_suite_under_egress_guard(self):
        """S90: Stage 21 modules under the egress guard -> green, 0 egress attempts, model_calls_total = 0, nothing skipped."""
        out = os.path.join(S.tmpdir("e21-"), "inner.json")
        env = S.child_env({"HUB_EGRESS_INNER21": "1"})
        cmd = [sys.executable, "-B", os.path.join(S.CODE_ROOT, "tests", "hub", "_driver.py"), "--out", out, "--egress-guard", "-k", "STG21"]
        p = subprocess.run(cmd, cwd=S.CODE_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=900)
        with open(out, encoding="utf-8") as f:
            res = json.load(f)
        self.assertTrue(res["successful"], p.stdout[-3000:])
        ok = sum(1 for r in res["records"] if r["status"] == "ok")
        self.assertEqual(ok, 7)
        self.assertEqual([r for r in res["records"] if r["status"] == "skipped"], [])
        self.assertEqual(res["egress_attempts"], [])
        self.assertEqual(res["tripwires"], {"egress_attempts_total": 0, "model_calls_total": 0})


if __name__ == "__main__":
    unittest.main()
