"""Stage 27 egress check (AC-CO-12 for the Stage 27 tests, PNFR-18; same split as Stages 20, 21, 23 and 26): the Stage 27 test modules
(STG27) run in an inner process with the egress guard installed -> suite green, zero egress attempts, model_calls_total = 0, no skipped test.
The Stage 27 tests use in-process requests and CLI subprocesses; the guard allows loopback.

TST-CO-12 skips the Stage 27 modules in its inner run (HUB_EGRESS_INNER) so groups C1 / C2 / C3 keep their size. Recursion guard:
HUB_EGRESS_INNER27.
"""
import json
import os
import subprocess
import sys
import unittest

import _support as S


def setUpModule():
    if os.environ.get("HUB_EGRESS_INNER") or os.environ.get("HUB_EGRESS_INNER27"):
        raise unittest.SkipTest("outer driver of the Stage 27 egress-guarded run")
    S.require_sandbox()


class TST_HUB_E27EGRESS_Guard(unittest.TestCase):

    def test_TST_HUB_E27EGRESS_S90_stage27_suite_under_egress_guard(self):
        """S90: Stage 27 modules under the egress guard -> green, 0 egress attempts, model_calls_total = 0, nothing skipped."""
        out = os.path.join(S.tmpdir("e27-"), "inner.json")
        env = S.child_env({"HUB_EGRESS_INNER27": "1"})
        cmd = [sys.executable, "-B", os.path.join(S.CODE_ROOT, "tests", "hub", "_driver.py"), "--out", out, "--egress-guard", "-k", "STG27"]
        p = subprocess.run(cmd, cwd=S.CODE_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=900)
        with open(out, encoding="utf-8") as f:
            res = json.load(f)
        self.assertTrue(res["successful"], p.stdout[-3000:])
        ok = sum(1 for r in res["records"] if r["status"] == "ok")
        self.assertEqual(ok, 25)
        self.assertEqual([r for r in res["records"] if r["status"] == "skipped"], [])
        self.assertEqual(res["egress_attempts"], [])
        self.assertEqual(res["tripwires"], {"egress_attempts_total": 0, "model_calls_total": 0})


if __name__ == "__main__":
    unittest.main()
