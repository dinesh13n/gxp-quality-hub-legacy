"""TST-POL-22, TST-POL-23, TST-POL-25 (AC-POL-22/23/25; PNFR-17, BEH-POL-06/11, FR-POL-01/03) - determinism and purity of the
evaluation function (1000 evaluations in two processes, I/O patched to raise), rejection of non-decimal amounts
(OD-S12-13 class B: the legacy outputs are characterised, the service rejects), and immutability of policy rows.
"""
import ast
import hashlib
import json
import math
import os
import socket
import sqlite3
import subprocess
import sys
import time
import unittest
from unittest import mock

import _support as S
import _inc04 as P
from hub.policy import engine
from hub.policy.errors import InputInvalid
from hub.security.canonical import canonical

AUTH = "TEST-AUTH-4 (synthetic)"
_CHILD = r"""
import hashlib, json, sys
sys.path.insert(0, sys.argv[1])
from hub.policy import engine
doc = json.load(open(sys.argv[2]))
cases = json.load(open(sys.argv[3]))
out = []
for i in range(1000):
    fn, inp = cases[i % len(cases)]
    out.append(engine.evaluate(doc["python"] if fn in ("PRIORITY", "MANUAL_REVIEW") else doc["js"] if fn == "AMOUNT_LIMIT" else doc["batch"], fn, inp))
print(hashlib.sha256(json.dumps(out, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
"""


def setUpModule():
    S.require_sandbox()


CASES = [["PRIORITY", {"status": "OPEN", "severity": "HIGH", "amount": 50000.01}], ["PRIORITY", {"status": "WEIRD", "severity": "LOW", "amount": "12.5"}],
         ["MANUAL_REVIEW", {"status": "REOPENED", "severity": "LOW"}], ["AMOUNT_LIMIT", {"amount": 26250.01, "region": "APAC", "year": 2026}],
         ["AMOUNT_LIMIT", {"amount": 5, "region": "MARS", "year": 2026}], ["SHIFT_FLAG", {"status": "OPEN", "value": 6100.5, "threshold": 6100}],
         ["SHIFT_FLAG", {"status": "HOLD", "value": 1, "region": "DE", "policy_code": "GXP-RULE-2"}]]


class TST_POL_PurityInputsImmutability(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.st = P.PStore(loaded=True)
        cls.docs = {"python": cls.st.svc.get_ruleset("as-found-python@1"), "js": cls.st.svc.get_ruleset("as-found-js@1"),
                    "batch": cls.st.svc.get_ruleset("as-found-batch@1")}

    @classmethod
    def tearDownClass(cls):
        cls.st.close()

    @staticmethod
    def _doc_for(docs, fn):
        return docs["python"] if fn in ("PRIORITY", "MANUAL_REVIEW") else docs["js"] if fn == "AMOUNT_LIMIT" else docs["batch"]

    # ---- AC-POL-22
    def test_TST_POL_22_a_1000_evaluations_bit_identical_in_two_processes(self):
        """TST-POL-22 / AC-POL-22: the same (ruleset version, inputs) evaluated 1000 times in this process and in two child
        processes (PYTHONHASHSEED 0 and 12345) gives bit-identical JSON."""
        out = []
        for i in range(1000):
            fn, inp = CASES[i % len(CASES)]
            out.append(engine.evaluate(self._doc_for(self.docs, fn), fn, inp))
        mine = hashlib.sha256(json.dumps(out, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        d = S.tmpdir("pol22-")
        with open(os.path.join(d, "docs.json"), "w") as f:
            json.dump(self.docs, f)
        with open(os.path.join(d, "cases.json"), "w") as f:
            json.dump(CASES, f)
        digests = []
        for seed in ("0", "12345"):
            p = subprocess.run([sys.executable, "-B", "-c", _CHILD, S.CODE_ROOT, os.path.join(d, "docs.json"), os.path.join(d, "cases.json")],
                               env=S.child_env({"PYTHONHASHSEED": seed}), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True, timeout=150)
            self.assertEqual(p.returncode, 0, p.stderr)
            digests.append(p.stdout.strip())
        self.assertEqual(digests, [mine, mine])
        self.assertEqual(len(set(canonical(o) for o in out[:len(CASES)])), len(CASES))
        self.assertTrue(all(o["authoritative"] is False for o in out))

    def test_TST_POL_22_b_evaluation_performs_no_io_clock_or_randomness(self):
        """TST-POL-22 / AC-POL-22: with file, network, clock, randomness and database access patched to RAISE, evaluate still returns the same result."""
        want = [engine.evaluate(self._doc_for(self.docs, fn), fn, inp) for fn, inp in CASES]
        boom = RuntimeError("I/O attempted inside the pure evaluation function")

        def raiser(*a, **k):
            raise boom
        patches = [mock.patch("builtins.open", raiser), mock.patch("io.open", raiser), mock.patch("os.open", raiser), mock.patch("os.stat", raiser),
                   mock.patch("os.urandom", raiser), mock.patch("socket.socket", raiser), mock.patch("socket.create_connection", raiser),
                   mock.patch("time.time", raiser), mock.patch("time.monotonic", raiser), mock.patch("time.perf_counter", raiser),
                   mock.patch("sqlite3.connect", raiser), mock.patch("subprocess.Popen", raiser)]
        for p in patches:
            p.start()
        try:
            got = [engine.evaluate(self._doc_for(self.docs, fn), fn, inp) for fn, inp in CASES * 20]
        finally:
            for p in patches:
                p.stop()
        self.assertEqual(got[:len(CASES)], want)

    def test_TST_POL_22_c_engine_imports_only_pure_modules(self):
        """TST-POL-22 / BEH-POL-06: hub/policy/engine.py imports only decimal plus the pure hub.policy.inputs / errors modules (static check)."""
        for fn, allowed in (("engine.py", {"decimal", "hub.policy.inputs", "hub.policy.errors", "hub.policy"}),
                            ("inputs.py", {"decimal", "re", "hub.policy.errors"})):
            tree = ast.parse(open(os.path.join(S.CODE_ROOT, "hub", "policy", fn), encoding="utf-8").read())
            mods = set()
            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    mods |= {a.name for a in n.names}
                elif isinstance(n, ast.ImportFrom):
                    mods.add(n.module)
                    if n.module == "hub.policy":
                        mods |= {"hub.policy." + a.name for a in n.names}
            self.assertTrue(mods <= allowed | {"hub.policy.inputs"}, (fn, sorted(mods)))
            self.assertFalse({"os", "io", "time", "datetime", "random", "socket", "sqlite3", "subprocess", "json", "hashlib"} & mods)

    # ---- AC-POL-23
    def test_TST_POL_23_non_decimal_amounts_are_rejected(self):
        """TST-POL-23 / AC-POL-23: amount 'abc', null, NaN (and infinities, bool, blank) -> E-POL-INPUT-INVALID, no outcome, for every amount-taking function.
        Legacy characterisation (golden CT-13): JS gave abc -> false and null -> true by coercion; recorded as DEV-30 (OD-S12-13 stays open)."""
        legacy = {(a if isinstance(a, str) or a is None else None): w for a, _, _, w in P.golden(["js_policy_table", "allows"]) if a is None or isinstance(a, str)}
        self.assertEqual(legacy, {"abc": False, None: True})
        bad = ["abc", None, float("nan"), float("inf"), -float("inf"), "NaN", "Infinity", "", " 5", "1_000", "0x10", True, [1], {"a": 1}, "1e999999"]
        svc = self.st.svc
        for amount in bad:
            with self.subTest(amount=repr(amount)):
                with self.assertRaises(InputInvalid) as cm:
                    svc.evaluate("AMOUNT_LIMIT", {"amount": amount, "region": "APAC", "year": 2026}, "as-found-js@1")
                self.assertEqual(cm.exception.code, "E-POL-INPUT-INVALID")
                with self.assertRaises(InputInvalid):
                    svc.evaluate("PRIORITY", {"status": "OPEN", "severity": "LOW", "amount": amount}, "as-found-python@1")
                with self.assertRaises(InputInvalid):
                    svc.evaluate("SHIFT_FLAG", {"status": "OPEN", "value": amount, "threshold": 1}, "as-found-batch@1")
        for amount in (0, -3, 12.5, "12.50", "1e3", "-0.5", ".5", "7."):  # plain decimals are accepted
            self.assertIn(svc.evaluate("AMOUNT_LIMIT", {"amount": amount, "region": "APAC", "year": 2026}, "as-found-js@1")["outcome"]["allowed"], (True, False))
        self.assertTrue(math.isnan(float("nan")))

    # ---- AC-POL-25
    def test_TST_POL_25_policy_version_rows_are_immutable(self):
        """TST-POL-25 / AC-POL-25: an UPDATE (or DELETE) of any policy_object / policy_events / rule_set / rule_row row is rejected by trigger."""
        st = P.PStore(loaded=True)
        try:
            st.svc.adopt(st.sess("holder-1"), "D-OPS", 1, "2026-01-01", "ops-owner", AUTH)
            st.svc.accept_open(st.sess("holder-1"), "D-FIN", 1, "deferred (synthetic)", AUTH)
            con = st.con
            snap = lambda: [con.execute("SELECT count(*), group_concat(policy_id || version || status) FROM policy_object").fetchone(),
                            con.execute("SELECT count(*) FROM policy_events").fetchone(), con.execute("SELECT count(*) FROM rule_row").fetchone()]
            before = snap()
            n = 0
            for pid, ver in con.execute("SELECT policy_id, version FROM policy_object").fetchall():
                for col, val in (("status", "'adopted'"), ("owner", "'someone'"), ("body", "'{}'"), ("effective_from", "'1999-01-01'"),
                                 ("name", "'x'"), ("created_by", "'x'")):
                    with self.assertRaises(sqlite3.IntegrityError) as cm:
                        with con:
                            con.execute("UPDATE policy_object SET %s = %s WHERE policy_id = ? AND version = ?" % (col, val), (pid, ver))
                    self.assertIn("E-DEC-IMMUTABLE", str(cm.exception))
                    n += 1
                with self.assertRaises(sqlite3.IntegrityError):
                    with con:
                        con.execute("DELETE FROM policy_object WHERE policy_id = ? AND version = ?", (pid, ver))
            self.assertGreaterEqual(n, 6 * 7)
            for sql in ("UPDATE policy_events SET authority_ref = 'x'", "DELETE FROM policy_events",
                        "UPDATE rule_set SET name = 'x'", "DELETE FROM rule_set", "UPDATE rule_row SET outcome = '{}'", "DELETE FROM rule_row"):
                with self.assertRaises(sqlite3.IntegrityError, msg=sql):
                    with con:
                        con.execute(sql)
            self.assertEqual(snap(), before)
            self.assertEqual(st.verify()["status"], "ok")
        finally:
            st.close()


if __name__ == "__main__":
    unittest.main()
