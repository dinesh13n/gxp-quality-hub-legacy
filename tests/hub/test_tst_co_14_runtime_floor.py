"""TST-CO-14 (AC-CO-14, OD-S12-12, BEH-CO-09) - class B, decision-dependent: both modes tested.
Mode "3.10" (OD-S12-12 default accepted under OD-12/OD-14): Python 3.9 -> E-CO-RUNTIME-UNSUPPORTED (exit 8);
on 3.10.12 / SQLite 3.37.2 the product starts and prints versions.
Mode "3.12" (ADR-018 PROPOSED target): the same dev runtime is refused (exit 8).
A real 3.9 interpreter is not installed on the dev device, so the old runtime is simulated with the
(hidden) --assume-python / --assume-sqlite seams; this limitation is recorded in the INC-02 evidence.
"""
import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import unittest

import _support as S
from hub import runtime
from hub.core.errors import RuntimeUnsupported


def setUpModule():
    S.require_sandbox()


class TST_CO_14_RuntimeFloor(unittest.TestCase):

    def test_TST_CO_14_a_floor_310_starts_and_prints_versions(self):
        """TST-CO-14 mode 3.10: selfcheck exit 0 and prints Python, SQLite and FTS5."""
        p = S.run_hub(["selfcheck"])
        self.assertEqual(p.returncode, 0, p.stderr)
        rt = json.loads(p.stdout)["runtime"]
        self.assertEqual(rt["python"], platform.python_version())
        self.assertEqual(rt["sqlite"], sqlite3.sqlite_version)
        self.assertIn("fts5", rt)
        self.assertEqual((rt["floor"], rt["floor_python"], rt["floor_sqlite"]), ("3.10", "3.10", "3.37.0"))

    def test_TST_CO_14_b_python39_refused(self):
        """TST-CO-14 / AC-CO-14 edge: Python 3.9 -> E-CO-RUNTIME-UNSUPPORTED exit 8, for selfcheck and golden-compare, nothing created."""
        d = os.path.join(S.tmpdir("co14b-"), "hubdata")
        for args in (["--assume-python", "3.9.18", "selfcheck"],
                     ["--assume-python", "3.9.18", "golden-compare", "--data-dir", d, "--legacy-root", S.LEGACY_ROOT]):
            with self.subTest(args=args):
                p = S.run_hub(args)
                self.assertEqual(p.returncode, 8, p.stderr)
                self.assertEqual(S.error_code(p), "E-CO-RUNTIME-UNSUPPORTED")
        self.assertFalse(os.path.exists(d))

    def test_TST_CO_14_c_sqlite_below_floor_refused(self):
        """TST-CO-14: SQLite 3.36 -> exit 8; SQLite 3.37.2 accepted."""
        self.assertEqual(S.run_hub(["--assume-sqlite", "3.36.0", "selfcheck"]).returncode, 8)
        self.assertEqual(S.run_hub(["--assume-sqlite", "3.37.2", "selfcheck"]).returncode, 0)

    def test_TST_CO_14_d_floor_312_mode(self):
        """TST-CO-14 mode 3.12 (ADR-018): the 3.10.12 dev runtime is refused; 3.12 accepted (flag and config)."""
        expect = 8 if sys.version_info[:2] < (3, 12) else 0
        self.assertEqual(S.run_hub(["--floor", "3.12", "selfcheck"]).returncode, expect)
        cfg = os.path.join(S.tmpdir("co14d-"), "hub-config.json")
        with open(cfg, "w") as f:
            json.dump({"runtime": {"floor": "3.12"}}, f)
        self.assertEqual(S.run_hub(["--config", cfg, "selfcheck"]).returncode, expect)
        self.assertEqual(S.run_hub(["--floor", "3.12", "--assume-python", "3.12.4", "selfcheck"]).returncode, 0)
        with self.assertRaises(RuntimeUnsupported):
            runtime.check("3.11.9", "3.45.1", floor="3.12")

    def test_TST_CO_14_e_real_old_interpreter_if_present(self):
        """TST-CO-14: if a real python3.9 exists, `python3.9 -m hub selfcheck` exits 8 (else recorded as not available)."""
        old = shutil.which("python3.9")
        if not old:
            self.skipTest("python3.9 not installed on this device (simulated in TST-CO-14 b)")
        p = subprocess.run([old, "-B", "-m", "hub", "selfcheck"], cwd=S.CODE_ROOT, env=S.child_env(),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(p.returncode, 8, p.stderr)


if __name__ == "__main__":
    unittest.main()
