"""TST-SEC-12 (AC-SEC-12, FR-SEC-02, residual risk R-SEC-1) - records deleted AFTER the last anchor are NOT detected:
this test documents the limitation (it asserts the undetected outcome and that the report states the limitation)."""
import sqlite3
import unittest

import _support as S
import _inc03 as H
from hub.security import audit


def setUpModule():
    S.require_sandbox()


class TST_SEC_12_TruncationAfterLastAnchor(unittest.TestCase):

    def test_TST_SEC_12_a_tail_after_last_anchor_undetected(self):
        """TST-SEC-12 / AC-SEC-12: 1,030 records (last anchor 1,000); delete 1,001-1,030 -> verify still 'ok' (limitation R-SEC-1)."""
        dbp, anp = H.chain_1000(extra_after_anchor=30)
        con = sqlite3.connect(dbp)
        self.assertEqual(audit.verify(con, anp)["records"], 1030)
        con.close()
        con = H.offline_attacker(dbp)
        try:
            with con:
                con.execute("DELETE FROM audit_log WHERE audit_seq > 1000")
            rep = audit.verify(con, anp)
        finally:
            con.close()
        self.assertEqual((rep["status"], rep["records"]), ("ok", 1000))
        self.assertIn("R-SEC-1", rep["limitation"])

    def test_TST_SEC_12_b_deleting_into_the_anchored_range_is_detected(self):
        """TST-SEC-12: control - deleting from seq 1,000 onwards reaches the anchored head -> head_mismatch."""
        dbp, anp = H.chain_1000(extra_after_anchor=30)
        con = H.offline_attacker(dbp)
        try:
            with con:
                con.execute("DELETE FROM audit_log WHERE audit_seq >= 1000")
            rep = audit.verify(con, anp)
        finally:
            con.close()
        self.assertEqual((rep["status"], rep["kind"]), ("broken", "head_mismatch"))


if __name__ == "__main__":
    unittest.main()
