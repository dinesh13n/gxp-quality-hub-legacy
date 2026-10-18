"""TST-SEC-10 (AC-SEC-10, FR-SEC-02, PNFR-09, BEH-SEC-06) - a chain of 1,000 audit records with anchors
(every 100, last at seq 1,000): `verify-audit` -> ok."""
import os
import sqlite3
import unittest

import _support as S
import _inc03 as H
from hub.security import audit


def setUpModule():
    S.require_sandbox()


class TST_SEC_10_VerifyAuditOk(unittest.TestCase):

    def test_TST_SEC_10_a_library_verify_ok(self):
        """TST-SEC-10 / AC-SEC-10: 1,000 records, 10 anchors -> status ok, head seq 1000, anchors_checked 10."""
        dbp, anp = H.chain_1000()
        con = sqlite3.connect(dbp)
        try:
            rep = audit.verify(con, anp)
        finally:
            con.close()
        self.assertEqual((rep["status"], rep["records"], rep["head_seq"], rep["anchors_checked"]), ("ok", 1000, 1000, 10))
        self.assertEqual([a["audit_seq"] for a in audit.read_anchors(anp)], list(range(100, 1001, 100)))

    def test_TST_SEC_10_b_cli_verify_audit_ok(self):
        """TST-SEC-10: `python -m hub.admin verify-audit` on the same chain -> exit 0, `ok` (then appends AUDIT_VERIFIED)."""
        dbp, anp = H.chain_1000()
        base = os.path.dirname(os.path.dirname(dbp))
        cfg = H.write_config(base)
        self.assertEqual(os.path.join(base, "anchor", H.ANCHOR), anp)
        p = H.admin(["verify-audit", "--data-dir", os.path.dirname(dbp)], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(H.out_json(p)["status"], "ok")
        con = sqlite3.connect(dbp)
        try:
            self.assertEqual(con.execute("SELECT action, outcome FROM audit_log ORDER BY audit_seq DESC LIMIT 1").fetchone(),
                             ("AUDIT_VERIFIED", "success"))
            self.assertEqual(audit.verify(con, anp)["status"], "ok")
        finally:
            con.close()


if __name__ == "__main__":
    unittest.main()
