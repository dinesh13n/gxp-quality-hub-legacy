"""TST-SEC-11 (AC-SEC-11, FR-SEC-02, PNFR-09, ABU-05) - the 1,000-record chain tampered offline (triggers dropped):
(a) one record's details edited, (b) one record deleted, (c) two records swapped -> verify-audit reports the first
broken seq and the kind; (d) last 50 records deleted after an anchor at seq 1,000 -> head mismatch against the anchor.
"""
import os
import unittest

import _support as S
import _inc03 as H
from hub.security import audit

COLS = "occurred_at, actor, actor_kind, action, object_ref, outcome, reason, correlation_id, details, prev_hash, hash"


def setUpModule():
    S.require_sandbox()


class TST_SEC_11_TamperDetection(unittest.TestCase):

    def _verify(self, mutate):
        dbp, anp = H.chain_1000()
        con = H.offline_attacker(dbp)
        try:
            with con:
                mutate(con)
            return audit.verify(con, anp), dbp
        finally:
            con.close()

    def _swap(self, con, i, j):
        a = con.execute("SELECT %s FROM audit_log WHERE audit_seq = ?" % COLS, (i,)).fetchone()
        b = con.execute("SELECT %s FROM audit_log WHERE audit_seq = ?" % COLS, (j,)).fetchone()
        sets = ", ".join("%s = ?" % c.strip() for c in COLS.split(","))
        con.execute("UPDATE audit_log SET %s WHERE audit_seq = ?" % sets, tuple(b) + (i,))
        con.execute("UPDATE audit_log SET %s WHERE audit_seq = ?" % sets, tuple(a) + (j,))

    def test_TST_SEC_11_a_details_edited(self):
        """TST-SEC-11 (a): details of seq 500 edited -> first_broken_seq 500, kind altered_record."""
        rep, _ = self._verify(lambda c: c.execute("UPDATE audit_log SET details = ? WHERE audit_seq = 500", ('{"n":5000}',)))
        self.assertEqual((rep["status"], rep["first_broken_seq"], rep["kind"]), ("broken", 500, "altered_record"))

    def test_TST_SEC_11_b_record_deleted(self):
        """TST-SEC-11 (b): seq 400 deleted -> first_broken_seq 400, kind missing_record."""
        rep, _ = self._verify(lambda c: c.execute("DELETE FROM audit_log WHERE audit_seq = 400"))
        self.assertEqual((rep["first_broken_seq"], rep["kind"]), (400, "missing_record"))

    def test_TST_SEC_11_c_two_records_swapped(self):
        """TST-SEC-11 (c): records 300 and 700 swapped (and, separately, adjacent 301/302) -> first broken = lower seq, kind reordered."""
        rep, _ = self._verify(lambda c: self._swap(c, 300, 700))
        self.assertEqual((rep["first_broken_seq"], rep["kind"], rep.get("original_seq")), (300, "reordered", 700))
        rep, _ = self._verify(lambda c: self._swap(c, 301, 302))
        self.assertEqual((rep["first_broken_seq"], rep["kind"], rep.get("original_seq")), (301, "reordered", 302))

    def test_TST_SEC_11_d_tail_deleted_after_anchor(self):
        """TST-SEC-11 (d): anchor at 1,000, records 951-1,000 deleted -> head_mismatch at the anchored seq 1,000."""
        rep, _ = self._verify(lambda c: c.execute("DELETE FROM audit_log WHERE audit_seq > 950"))
        self.assertEqual((rep["first_broken_seq"], rep["kind"], rep["records"]), (1000, "head_mismatch", 950))

    def test_TST_SEC_11_e_cli_exit_17(self):
        """TST-SEC-11: the CLI reports tamper with exit 17 E-SEC-AUDIT-TAMPER-DETECTED."""
        rep, dbp = self._verify(lambda c: c.execute("UPDATE audit_log SET actor = 'mallory' WHERE audit_seq = 10"))
        base = os.path.dirname(os.path.dirname(dbp))
        p = H.admin(["verify-audit", "--data-dir", os.path.dirname(dbp)], H.write_config(base))
        self.assertEqual(p.returncode, 17)
        self.assertEqual(H.out_json(p)["first_broken_seq"], 10)
        self.assertIn("E-SEC-AUDIT-TAMPER-DETECTED", p.stderr)


if __name__ == "__main__":
    unittest.main()
