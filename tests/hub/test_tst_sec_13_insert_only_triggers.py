"""TST-SEC-13 (AC-SEC-13, FR-SEC-02, INV-02, PNFR-10) - UPDATE/DELETE on the audit table is rejected by trigger;
the other INC-03 retained tables (hold-all, OD-S12-09 / OD-15) reject deletion as well."""
import sqlite3
import unittest

import _support as S
import _inc03 as H
from hub.ops import release
from hub.security import audit, scan


def setUpModule():
    S.require_sandbox()


class TST_SEC_13_InsertOnlyTriggers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.st = H.Store("sec13-")
        pw = H.password()
        cls.st.authn.create_user("u1", pw, ["reviewer"], "op")
        cls.st.authn.login("u1", pw, "seed")  # login_attempt + session rows (empty tables never fire row triggers)
        release.record_checklist(cls.st.con, cls.st.clock, "R-seed", {}, "op", "seed")
        audit.append(cls.st.con, cls.st.clock, actor="x", actor_kind="system", action="E", outcome="success", correlation_id="c")

    @classmethod
    def tearDownClass(cls):
        cls.st.close()

    def _rejected(self, sql, msg):
        con = self.st.con
        before = con.execute("SELECT count(*), max(hash) FROM audit_log").fetchone()
        with self.assertRaises(sqlite3.IntegrityError) as cm:
            with con:
                con.execute(sql)
        self.assertIn(msg, str(cm.exception))
        self.assertEqual(con.execute("SELECT count(*), max(hash) FROM audit_log").fetchone(), before)

    def test_TST_SEC_13_a_audit_update_delete_rejected(self):
        """TST-SEC-13 / AC-SEC-13: UPDATE (any column) and DELETE on audit_log -> RAISE(ABORT, 'E-DEC-IMMUTABLE')."""
        for sql in ("UPDATE audit_log SET details = '{}' WHERE audit_seq = 1", "UPDATE audit_log SET outcome = 'error'",
                    "DELETE FROM audit_log WHERE audit_seq = 1", "DELETE FROM audit_log"):
            with self.subTest(sql=sql):
                self._rejected(sql, "E-DEC-IMMUTABLE")
        self.assertEqual(audit.verify(self.st.con, self.st.anchor_path)["status"], "ok")

    def test_TST_SEC_13_b_other_retained_tables_reject_delete(self):
        """TST-SEC-13: principal, principal_role, session, login_attempt, release_*, deviation_register reject DELETE."""
        for t in ("principal", "principal_role", "session", "login_attempt", "release_record", "release_gate_result",
                  "deviation_register"):
            self.assertGreater(self.st.con.execute("SELECT count(*) FROM %s" % t).fetchone()[0], 0, t)
        for t in ("principal", "principal_role", "session", "login_attempt", "release_record", "release_gate_result",
                  "deviation_register"):
            with self.subTest(table=t):
                self._rejected("DELETE FROM %s" % t, "E-SEC-RETAINED")
        for sql in ("UPDATE principal_role SET role = 'dispositioner'", "UPDATE login_attempt SET outcome = 'success'",
                    "UPDATE principal SET principal_id = 'other'"):
            with self.subTest(sql=sql):
                self._rejected(sql, "E-SEC-RETAINED")
        self.assertEqual(scan.retention_triggers(self.st.con), [])


if __name__ == "__main__":
    unittest.main()
