"""TST-SEC-04 (AC-SEC-04, FR-SEC-01, SYS-4) - a fresh install has zero users and no default credentials; login with
any password fails (generic E-AUTH-BAD-CREDENTIALS) and is audited."""
import unittest

import _support as S
import _inc03 as H
from hub.security.errors import AuthBadCredentials


def setUpModule():
    S.require_sandbox()


class TST_SEC_04_FreshInstall(unittest.TestCase):

    def test_TST_SEC_04_a_zero_users_after_fresh_migrate(self):
        """TST-SEC-04 / AC-SEC-04: after `migrate` on an empty data dir the principal and role tables are empty."""
        st = H.Store("sec04a-")
        try:
            self.assertEqual(st.con.execute("SELECT count(*) FROM principal").fetchone()[0], 0)
            self.assertEqual(st.con.execute("SELECT count(*) FROM principal_role").fetchone()[0], 0)
            self.assertEqual(st.con.execute("SELECT count(*) FROM session").fetchone()[0], 0)
        finally:
            st.close()

    def test_TST_SEC_04_b_any_login_fails_generically(self):
        """TST-SEC-04: login as admin/root/hub/operator/'' with any password -> E-AUTH-BAD-CREDENTIALS; one denied LOGIN audit each."""
        st = H.Store("sec04b-")
        try:
            names = ("admin", "root", "hub", "operator", "")
            for name in names:
                for pw in ("", name, H.password()):
                    with self.assertRaises(AuthBadCredentials) as cm:
                        st.authn.login(name, pw, "sec04")
                    self.assertEqual(cm.exception.message, "login failed")
            rows = [r for r in st.audit_rows() if r["action"] == "LOGIN"]
            self.assertEqual(len(rows), len(names) * 3)
            self.assertTrue(all(r["outcome"] == "denied" and r["actor"] == "unknown-principal" for r in rows))
            self.assertEqual(st.con.execute("SELECT count(*) FROM session").fetchone()[0], 0)
        finally:
            st.close()

    def test_TST_SEC_04_c_cli_fresh_install_lists_no_users(self):
        """TST-SEC-04: `python -m hub.admin migrate` then `user list` -> principals []; there is no web/bootstrap path."""
        base = S.tmpdir("sec04c-")
        cfg = H.write_config(base)
        import os
        d = os.path.join(base, "data")
        self.assertEqual(H.admin(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg).returncode, 0)
        p = H.admin(["user", "list", "--data-dir", d], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(H.out_json(p), {"principals": []})


if __name__ == "__main__":
    unittest.main()
