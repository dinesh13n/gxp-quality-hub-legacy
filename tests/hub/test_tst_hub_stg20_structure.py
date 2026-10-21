"""Stage 20 DI-03 structure tests (DW-06; S16-D04 / AC-02, S16-D06 / AC-04, S16-D08). Static (AST) plus small unit checks. Synthetic, unvalidated.

  S20  one Zone H holder rule: the `principal_id not in holders` comparison exists only in hub/security/zone_h.py; the three callers use it
  S21  zone_h.refusal: every reason, in order, with the three caller profiles (gate service / INC-04 policy gate / route authorizer)
  S22  no domain package imports hub.web (only the HTTP layers hub/web and the R2 HTTP surface in hub/r2); ReqInvalid is one class
  S23  M006 check moved out of hub.web: hub.store.m006 and hub.web.schema agree (absent -> E-STORE-NOT-MIGRATED; applied -> ok)
"""
import ast
import os
import unittest

import _stg20 as T
import _support as S
from hub.security import zone_h

HUB = os.path.join(S.CODE_ROOT, "hub")


def setUpModule():
    T.skip_in_inner_egress_run()


def _py():
    for d, dirs, fns in os.walk(HUB):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for fn in fns:
            if fn.endswith(".py"):
                p = os.path.join(d, fn)
                yield os.path.relpath(p, S.CODE_ROOT).replace(os.sep, "/"), p


class _P(object):
    def __init__(self, pid="h1", kind="human", roles=("dispositioner",)):
        self.principal_id, self.kind, self.roles = pid, kind, list(roles)


class TST_HUB_STG20_Structure(unittest.TestCase):

    def test_TST_HUB_STG20_S20_one_zone_h_holder_rule(self):
        """S20 (DW-06, S16-D04): the holder comparison is written once (hub/security/zone_h.py); gate service, policy gate and authorizer
        call zone_h.refusal."""
        found = []
        for rel, p in _py():
            text = open(p, encoding="utf-8").read()
            for n in ast.walk(ast.parse(text)):
                if isinstance(n, ast.Compare) and any(isinstance(o, ast.NotIn) for o in n.ops):
                    seg = ast.get_source_segment(text, n) or ""
                    if "principal_id" in seg and "holders" in seg:
                        found.append(rel)
        self.assertEqual(found, ["hub/security/zone_h.py"])
        for rel in ("hub/gate/service.py", "hub/policy/gate.py", "hub/security/authz.py"):
            self.assertIn("zone_h.refusal(", open(os.path.join(S.CODE_ROOT, rel), encoding="utf-8").read(), rel)

    def test_TST_HUB_STG20_S21_refusal_reasons_in_order(self):
        """S21 (DW-06): first failing condition wins; caller profiles reproduce the three original copies."""
        z = {"holders": ["h1"], "reauth_window_seconds": 300}
        t0, fresh, stale = "2026-10-18T00:00:00.000000Z", lambda: "2026-10-18T00:04:00.000000Z", lambda: "2026-10-18T00:06:00.000000Z"
        R = zone_h.refusal
        self.assertIsNone(R(_P(), t0, fresh, z))
        self.assertEqual(R(_P(), t0, stale, z), zone_h.REAUTH)
        self.assertEqual(R(_P(pid="x"), t0, fresh, z), zone_h.NOT_A_HOLDER)
        self.assertEqual(R(_P(), t0, fresh, dict(z, holders=[])), zone_h.NO_HOLDERS)
        self.assertEqual(R(_P(), t0, fresh, dict(z, holders=[]), distinguish_empty=False), zone_h.NOT_A_HOLDER)
        self.assertEqual(R(_P(kind="service"), t0, fresh, z), zone_h.NOT_HUMAN_DISPOSITIONER)
        self.assertEqual(R(_P(roles=("reviewer",)), t0, fresh, z), zone_h.NOT_HUMAN_DISPOSITIONER)
        self.assertIsNone(R(_P(roles=("dispositioner", "integration")), t0, fresh, z))
        self.assertEqual(R(_P(roles=("dispositioner", "integration")), t0, fresh, z, reject_integration=True), zone_h.NOT_HUMAN_DISPOSITIONER)
        self.assertEqual(R(_P(kind="service", roles=()), t0, fresh, z, require_dispositioner=False), zone_h.NON_HUMAN)
        self.assertIsNone(R(_P(roles=()), t0, fresh, z, require_dispositioner=False))
        calls = []
        self.assertEqual(R(_P(pid="x"), t0, lambda: calls.append(1) or fresh(), z), zone_h.NOT_A_HOLDER)
        self.assertEqual(calls, [])  # the clock is read only for the re-authentication condition (as in the original copies)

    def test_TST_HUB_STG20_S22_no_domain_import_of_http_layer(self):
        """S22 (DW-06, S16-D06): outside hub/web and hub/r2 (R2 HTTP surface) no module imports hub.web; ReqInvalid is the same class."""
        offenders = []
        for rel, p in _py():
            if rel.startswith(("hub/web/", "hub/r2/")):
                continue
            for n in ast.walk(ast.parse(open(p, encoding="utf-8").read())):
                mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module or ""] if isinstance(n, ast.ImportFrom) else [])
                if isinstance(n, ast.ImportFrom) and n.module == "hub":
                    mods += ["hub." + a.name for a in n.names]
                offenders += ["%s -> %s" % (rel, m) for m in mods if m == "hub.web" or m.startswith("hub.web.")]
        self.assertEqual(offenders, [])
        from hub.core.req_errors import ReqInvalid as A
        from hub.web.errors import ReqInvalid as B
        self.assertIs(A, B)

    def test_TST_HUB_STG20_S23_m006_check_outside_http_layer(self):
        """S23 (DW-06): hub.store.m006 and hub.web.schema give the same answer on an unmigrated store and on an M006 store."""
        import sqlite3
        import _inc08 as W
        from hub.security.errors import StoreNotMigrated
        from hub.store import m006
        from hub.web import schema as wschema
        con = sqlite3.connect(":memory:")
        for f in (m006.require, wschema.require):
            with self.assertRaises(StoreNotMigrated):
                f(con)
        con.close()
        st = W.WStore(loaded=False)
        try:
            self.assertEqual(m006.migration(), wschema.migration())
            self.assertEqual(m006.applied(st.con), wschema.applied(st.con))
            m006.require(st.con)
            wschema.require(st.con)
        finally:
            st.close()


if __name__ == "__main__":
    unittest.main()
