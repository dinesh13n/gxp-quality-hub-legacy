"""TST-SEC-15 (AC-SEC-15, PNFR-08, BEH-SEC-07) - after a login failure (and a success), neither the audit records
(`details` or any column) nor the logs contain the password, the session token or its hash; credential-like keys
are refused in audit details."""
import logging
import os
import unittest

import _support as S
import _inc03 as H
from hub.security import audit
from hub.security.auth import token_digest
from hub.security.errors import AuthBadCredentials, SecretInAudit


def setUpModule():
    S.require_sandbox()


class TST_SEC_15_NoSecretsInAuditOrLogs(unittest.TestCase):

    def test_TST_SEC_15_a_login_failure_audit_and_logs_clean(self):
        """TST-SEC-15 / AC-SEC-15: wrong + right password; audit rows and captured hub.* logs hold no password/token/hash."""
        st = H.Store("sec15-")
        try:
            pw = H.password()
            wrong = H.password()
            st.authn.create_user("u1", pw, ["reviewer"], "op")
            with self.assertLogs("hub", level="INFO") as logs:
                with self.assertRaises(AuthBadCredentials):
                    st.authn.login("u1", wrong, "c-fail")
                token = st.authn.login("u1", pw, "c-ok")
            row = st.con.execute("SELECT pw_hash, pw_salt FROM principal").fetchone()
            secrets_ = [pw, wrong, token, token_digest(token), row[0], row[1]]
            text = "\n".join(repr(r) for r in st.audit_rows()) + "\n" + "\n".join(logs.output)
            for s in secrets_:
                self.assertNotIn(s, text)
            fail = [r for r in st.audit_rows() if r["correlation_id"] == "c-fail"]
            self.assertEqual(len(fail), 1)
            self.assertEqual((fail[0]["action"], fail[0]["outcome"]), ("LOGIN", "denied"))
        finally:
            st.close()

    def test_TST_SEC_15_b_credential_keys_refused_in_details(self):
        """TST-SEC-15: details keys like password/token/secret/api_key (nested too) -> E-SEC-SECRET-IN-AUDIT, nothing written."""
        st = H.Store("sec15b-")
        try:
            n = audit.head(st.con)[0]
            for d in ({"password": "x"}, {"outer": {"session_token": "y"}}, {"list": [{"api_key": "z"}]}, {"Client_Secret": 1}):
                with self.assertRaises(SecretInAudit):
                    audit.append(st.con, st.clock, actor="a", actor_kind="system", action="X", outcome="success",
                                 correlation_id="c", details=d)
            self.assertEqual(audit.head(st.con)[0], n)
        finally:
            st.close()

    def test_TST_SEC_15_c_cli_user_create_never_echoes_password(self):
        """TST-SEC-15: `hub.admin user create` (password via env) - stdout/stderr and the audit trail do not contain it."""
        base = S.tmpdir("sec15c-")
        cfg = H.write_config(base)
        d = os.path.join(base, "data")
        H.admin(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg)
        pw = H.password()
        p = H.admin(["user", "create", "--data-dir", d, "--principal", "cli-user", "--role", "reviewer"], cfg,
                    env={"HUB_NEW_USER_PASSWORD": pw})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn(pw, p.stdout + p.stderr)
        import sqlite3
        con = sqlite3.connect(os.path.join(d, "hub.sqlite3"))
        try:
            dump = "\n".join(con.iterdump())
        finally:
            con.close()
        self.assertNotIn(pw, dump)


if __name__ == "__main__":
    unittest.main()
