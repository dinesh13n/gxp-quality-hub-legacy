"""Stage 23 error-code registry and exit-code tests (DW-13; IC-2; OD-29 DQ-04). Synthetic, unvalidated.

  S20  codes in the code = codes in the committed registry (diff 0), from three derivations: a text scan, the runtime HubError classes, the committed JSON
  S21  code literals that are not an error class are limited to a reviewed list; spec codes without a class are reviewed too
  S22  exit-code uniqueness: the only clashes are the DOCUMENTED 2 and 9 (numbers KEPT, OD-29); families 19 / 31 / 32 documented; specified numbers pinned
  S23  the clash check itself works: an undocumented clash, a renumbered documented clash and a vanished family are reported
  S24  `python -m hub.control registry --check DIR` is rc 0 on the committed registry and rc 1 on a stale copy
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

import _support as S
import _stg23 as T
from hub.control import registry as R

# Stage 27 (S27-DEV-10): the committed registry is the regenerated one in docs/27-hardening/error-registry (three new HTTP codes: E-REQ-TIMEOUT, E-REQ-RATE-LIMITED,
# E-STORE-UNAVAILABLE). The Stage 12 v0.2 registry (docs/23-human-control/stage12-v0.2) stays untouched as the baseline; test_tst_hub_stg27_registry.py proves the new one only ADDS.
REG_DIR = os.path.join(S.CODE_ROOT, "docs", "27-hardening", "error-registry")
REFERENCED_ONLY = {"E-RUN-ABANDONED", "E-STORE-DB-BUSY"}


def setUpModule():
    T.skip_in_inner_egress_run()


def _scan_text():
    """Codes defined as `code = "E-..."` or `code, exit_code, ... = "E-...", ...` (class attribute) in any hub/**/*.py, by plain text."""
    found = set()
    for d, dirs, fns in os.walk(os.path.join(S.CODE_ROOT, "hub")):
        for fn in fns:
            if fn.endswith(".py"):
                with open(os.path.join(d, fn), encoding="utf-8") as f:
                    found |= set(re.findall(r'^\s+code(?:\s*,\s*\w+)*\s*=\s*"(E-[A-Z0-9-]+)"', f.read(), re.M))
    return found


class TST_HUB_STG23_Registry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = R.build(S.CODE_ROOT)
        with open(os.path.join(REG_DIR, "error-code-registry.json"), encoding="utf-8") as f:
            cls.committed = json.load(f)

    def test_TST_HUB_STG23_S20_codes_in_code_equal_codes_in_registry(self):
        """S20 (DW-13, IC-2): the text scan, the runtime classes and the committed registry list the same error codes (diff 0); the committed files equal the generated ones."""
        text = _scan_text()
        runtime = set(r["code"] for r in self.reg["codes"])
        committed = set(r["code"] for r in self.committed["codes"])
        self.assertEqual(text - runtime, set())
        self.assertEqual(runtime - text, set())
        self.assertEqual(runtime ^ committed, set())
        self.assertEqual(self.committed["count"], len(committed))
        self.assertGreaterEqual(len(committed), 100)
        self.assertEqual(R.diff_against(self.reg, REG_DIR), [])
        T.write_evidence("error-registry-check.json", {"label": T.LABEL, "text_scan": len(text), "runtime": len(runtime), "committed": len(committed), "diff": 0})

    def test_TST_HUB_STG23_S21_unclassed_codes_are_reviewed(self):
        """S21 (DW-13): code literals that are not an error class are exactly the reviewed list; every spec code without a class is named in the registry."""
        self.assertEqual(set(self.reg["referenced_only"]), REFERENCED_ONLY)
        self.assertEqual(self.committed["referenced_only"], self.reg["referenced_only"])
        self.assertEqual(self.committed["spec_codes_not_in_code"], self.reg["spec_codes_not_in_code"])
        self.assertTrue(REFERENCED_ONLY.isdisjoint(set(r["code"] for r in self.reg["codes"])))

    def test_TST_HUB_STG23_S22_exit_codes_unique_except_documented_clashes(self):
        """S22 (DW-13, OD-29 / DQ-04): exit 2 and 9 are the documented clashes and keep their numbers; 19 / 31 / 32 are documented families; nothing else clashes."""
        self.assertEqual(self.reg["exit_code_problems"], [])
        table = dict((e["exit_code"], e) for e in self.reg["exit_codes"])
        clashes = set(k for k, e in table.items() if e["classification"] == "documented_clash")
        fam = set(k for k, e in table.items() if e["classification"] == "documented_family")
        self.assertEqual(clashes, {2, 9})
        self.assertEqual(fam, {19, 31, 32})
        self.assertEqual([k for k, e in table.items() if e["classification"] == "UNDOCUMENTED_CLASH"], [])
        by = dict((r["code"], r["exit_code"]) for r in self.reg["codes"])
        for code in ("E-FX-HASH", "E-CFG-INVALID", "E-AUTH-PASSWORD-POLICY"):
            self.assertEqual(by[code], 2, code)
        for code in ("E-CO-DENYLIST-IMPORT", "E-SEC-EXPOSURE-NOT-APPROVED"):
            self.assertEqual(by[code], 9, code)
        self.assertEqual(sorted(table[2]["codes"]), sorted(["E-FX-HASH", "E-CFG-INVALID", "E-AUTH-PASSWORD-POLICY"]))
        self.assertEqual(sorted(table[9]["codes"]), sorted(["E-CO-DENYLIST-IMPORT", "E-SEC-EXPOSURE-NOT-APPROVED"]))
        T.write_evidence("exit-code-uniqueness.json", {"label": T.LABEL, "documented_clashes": sorted(clashes), "documented_families": sorted(fam),
                                                       "undocumented": [], "exit_codes": self.reg["exit_codes"]})

    def test_TST_HUB_STG23_S23_clash_check_detects_planted_problems(self):
        """S23 (DW-13): the exit-code check reports a new undocumented clash, a renumbered documented clash and a vanished family."""
        codes = copy.deepcopy(self.reg["codes"])
        self.assertEqual(R.check_exit_codes(codes), [])
        planted = copy.deepcopy(codes)
        free = max(r["exit_code"] for r in planted) + 1
        for r in planted:
            if r["code"] == "E-CFG-INVALID":
                r["exit_code"] = free  # renumbering one of the exit-2 codes
        self.assertEqual(R.check_exit_codes(planted), [])  # exit 2 still has 2 areas (FX, AUTH): still a documented clash
        for r in planted:
            if r["code"] in ("E-FX-HASH", "E-AUTH-PASSWORD-POLICY"):
                r["exit_code"] = free + 1
        self.assertTrue(any("exit 2" in p for p in R.check_exit_codes(planted)))
        clash = copy.deepcopy(codes)
        victim = [r for r in clash if r["exit_code"] == 6][0]
        other = [r for r in clash if r["area"] != victim["area"] and r["exit_code"] not in (2, 9, 19, 31, 32, 6)][0]
        other["exit_code"] = 6
        self.assertTrue(any("undocumented clash on exit 6" in p for p in R.check_exit_codes(clash)))
        gone = [r for r in copy.deepcopy(codes) if r["exit_code"] != 32]
        self.assertTrue(any("family on exit 32" in p for p in R.check_exit_codes(gone)))

    def test_TST_HUB_STG23_S24_registry_cli_check(self):
        """S24 (DW-13): `python -m hub.control registry --check DIR` is rc 0 on the committed registry and rc 1 on a stale copy; --out regenerates identical files."""
        def run(args):
            return subprocess.run([sys.executable, "-B", "-m", "hub.control", "registry"] + args, cwd=S.CODE_ROOT, env=S.child_env(),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)
        ok = run(["--check", REG_DIR])
        self.assertEqual(ok.returncode, 0, ok.stderr)
        d = T.tempfile_dir("s23reg")
        self.addCleanup(shutil.rmtree, d, True)
        for fn in ("error-code-registry.json", "error-code-registry.md"):
            shutil.copy(os.path.join(REG_DIR, fn), d)
        with open(os.path.join(d, "error-code-registry.md"), "a", encoding="utf-8") as f:
            f.write("stale\n")
        self.assertEqual(run(["--check", d]).returncode, 1)
        out = T.tempfile_dir("s23regout")
        self.addCleanup(shutil.rmtree, out, True)
        self.assertEqual(run(["--out", out]).returncode, 0)
        for fn in ("error-code-registry.json", "error-code-registry.md"):
            with open(os.path.join(out, fn), encoding="utf-8") as a, open(os.path.join(REG_DIR, fn), encoding="utf-8") as b:
                self.assertEqual(a.read(), b.read(), fn)


if __name__ == "__main__":
    unittest.main()
