"""INC-05 egress check (AC-CO-12 for INC-05, PNFR-18, RTD-44 split): the INC-05 test modules (TST-DEC-*, TST-ID-*, INC-05 supplementary) run in an
inner process with the egress guard installed -> suite green, zero non-loopback connection attempts, model_calls_total = 0.

TST-CO-12 e (frozen) skips the INC-05 modules in its inner run (HUB_EGRESS_INNER) so group C keeps its size; this module runs them instead, in its own
device-call group (-k E05EGRESS). It is skipped inside both inner runs. Recursion guard: HUB_EGRESS_INNER5.
"""
import json
import os
import subprocess
import sys
import unittest

import _support as S


def setUpModule():
    if os.environ.get("HUB_EGRESS_INNER") or os.environ.get("HUB_EGRESS_INNER5"):
        raise unittest.SkipTest("outer driver of the INC-05 egress-guarded run")
    S.require_sandbox()


class TST_HUB_E05EGRESS_Guard(unittest.TestCase):

    def test_TST_HUB_E05EGRESS_S90_inc05_suite_under_egress_guard(self):
        """S90: INC-05 modules under the egress guard -> green, 0 egress attempts, model_calls_total = 0."""
        out = os.path.join(S.tmpdir("e05-"), "inner.json")
        env = S.child_env({"HUB_EGRESS_INNER5": "1"})
        cmd = [sys.executable, "-B", os.path.join(S.CODE_ROOT, "tests", "hub", "_driver.py"), "--out", out, "--egress-guard",
               "-k", "TST_DEC", "-k", "TST_ID", "-k", "INC05"]
        p = subprocess.run(cmd, cwd=S.CODE_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=600)
        with open(out, encoding="utf-8") as f:
            res = json.load(f)
        self.assertTrue(res["successful"], p.stdout[-3000:])
        ok = sum(1 for r in res["records"] if r["status"] == "ok")
        self.assertGreaterEqual(ok, 39 + 10)
        self.assertEqual([r for r in res["records"] if r["status"] == "skipped"], [])
        self.assertEqual(res["egress_attempts"], [])
        self.assertEqual(res["tripwires"], {"egress_attempts_total": 0, "model_calls_total": 0})


if __name__ == "__main__":
    unittest.main()
