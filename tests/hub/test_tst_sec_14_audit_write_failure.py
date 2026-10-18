"""TST-SEC-14 (AC-SEC-14, FR-SEC-02, BEH-DEC-11, EC-03) - with the audit write forced to fail, any change is rolled
back and E-SEC-AUDIT-WRITE-FAILED is raised (no change exists without its audit record).

The failure is injected inside SQLite (a TEMP trigger aborting inserts into audit_log - the same failure surface as
a full disk / I/O error on the audit insert), not by patching hub code."""
import unittest

import _support as S
import _inc03 as H
from hub.security import audit
from hub.security.errors import AuditWriteFailed


def setUpModule():
    S.require_sandbox()


class TST_SEC_14_AuditWriteFailure(unittest.TestCase):

    def _break_audit(self, con):
        con.execute("CREATE TEMP TRIGGER fail_audit BEFORE INSERT ON main.audit_log "
                    "BEGIN SELECT RAISE(ABORT, 'simulated audit write failure'); END")

    def _counts(self, con):
        return tuple(con.execute("SELECT count(*) FROM %s" % t).fetchone()[0]
                     for t in ("audit_log", "principal", "principal_role", "session", "login_attempt"))

    def test_TST_SEC_14_a_changes_rolled_back(self):
        """TST-SEC-14 / AC-SEC-14: user creation, login (success and failure) and a generic change all roll back -> E-SEC-AUDIT-WRITE-FAILED."""
        st = H.Store("sec14-")
        try:
            pw = H.password()
            st.authn.create_user("existing", pw, ["reviewer"], "op")
            st.con.execute("CREATE TABLE scratch_change(x INTEGER)")
            st.con.commit()
            before = self._counts(st.con)
            self._break_audit(st.con)
            attempts = (lambda: st.authn.create_user("newbie", H.password(), ["reviewer"], "op"),
                        lambda: st.authn.login("existing", pw, "c1"),
                        lambda: st.authn.login("existing", "bad", "c2"))
            for fn in attempts:
                with self.assertRaises(AuditWriteFailed) as cm:
                    fn()
                self.assertEqual(cm.exception.code, "E-SEC-AUDIT-WRITE-FAILED")
            with self.assertRaises(AuditWriteFailed):
                with audit.change(st.con, st.clock, actor="a", actor_kind="human", action="DECISION_EVENT",
                                  outcome="success", correlation_id="c3"):
                    st.con.execute("INSERT INTO scratch_change VALUES (1)")
            self.assertFalse(st.con.in_transaction)
            self.assertEqual(self._counts(st.con), before)
            self.assertEqual(st.con.execute("SELECT count(*) FROM scratch_change").fetchone()[0], 0)
            st.con.execute("DROP TRIGGER temp.fail_audit")
            st.authn.login("existing", pw, "c4")  # works again once the audit path is healthy
            self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")
        finally:
            st.close()


if __name__ == "__main__":
    unittest.main()
