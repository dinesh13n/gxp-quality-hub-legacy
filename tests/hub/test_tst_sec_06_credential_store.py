"""TST-SEC-06 (AC-SEC-06, PNFR-07, PNFR-08, BEH-SEC-02) - the credential store holds PBKDF2-HMAC-SHA256 hashes with a
per-user salt (iterations >= 600,000 - Stage 12 proposal, Stage 24 to confirm); session tokens are stored only as
SHA-256; no plaintext password or token appears anywhere in the store, anchor file or backups."""
import hashlib
import hmac
import os
import unittest

import _support as S
import _inc03 as H
from hub import config
from hub.core.errors import ConfigInvalid
from hub.ops import backup
from hub.security import settings
from hub.security.auth import token_digest


def setUpModule():
    S.require_sandbox()


def _all_bytes(paths):
    out = b""
    for root in paths:
        for d, _, fns in os.walk(root):
            for fn in fns:
                with open(os.path.join(d, fn), "rb") as f:
                    out += f.read()
    return out


class TST_SEC_06_CredentialStore(unittest.TestCase):

    def test_TST_SEC_06_a_pbkdf2_per_user_salt(self):
        """TST-SEC-06 / AC-SEC-06: pbkdf2_sha256, 600000 iterations, 16-byte salt, unique salt+hash for equal passwords; recomputation matches."""
        st = H.Store("sec06a-")
        try:
            pw = H.password()
            st.authn.create_user("u1", pw, ["reviewer"], "op")
            st.authn.create_user("u2", pw, ["compliance"], "op")
            rows = st.con.execute("SELECT principal_id, pw_algo, pw_iterations, pw_salt, pw_hash FROM principal ORDER BY 1").fetchall()
            self.assertEqual([(r[1], r[2]) for r in rows], [("pbkdf2_sha256", 600000)] * 2)
            self.assertTrue(all(len(bytes.fromhex(r[3])) == 16 for r in rows))
            self.assertNotEqual(rows[0][3], rows[1][3])
            self.assertNotEqual(rows[0][4], rows[1][4])
            for r in rows:
                calc = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(r[3]), r[2]).hex()
                self.assertTrue(hmac.compare_digest(calc, r[4]))
        finally:
            st.close()

    def test_TST_SEC_06_b_tokens_only_as_sha256_and_no_plaintext_anywhere(self):
        """TST-SEC-06: session row holds sha256(token) only; password/token bytes absent from DB, anchor and a backup."""
        st = H.Store("sec06b-")
        try:
            pw = H.password()
            st.authn.create_user("u1", pw, ["reviewer"], "op")
            token = st.authn.login("u1", pw, "sec06")
            rows = st.con.execute("SELECT token_sha256 FROM session").fetchall()
            self.assertEqual(rows, [(token_digest(token),)])
            from hub.security import audit
            audit.write_anchor(st.con, st.anchor_path)
            st.con.commit()
            bk = backup.backup(st.data, st.anchor_path, os.path.join(st.base, "bk2"), "b", st.clock)
            blob = _all_bytes([st.data, os.path.dirname(st.anchor_path), bk["path"]])
            for secret in (pw, token):
                self.assertNotIn(secret.encode(), blob)
        finally:
            st.close()

    def test_TST_SEC_06_c_iteration_and_length_floors(self):
        """TST-SEC-06: config below the floors (iterations < 600000, password_min_length < 12) is refused (E-CFG-INVALID)."""
        for bad in ({"auth": {"pbkdf2_iterations": 1000}}, {"auth": {"password_min_length": 8}}):
            with self.assertRaises(ConfigInvalid):
                settings.resolve(config.load(overrides=bad))
        self.assertEqual(settings.resolve(config.load(overrides={"auth": {"pbkdf2_iterations": 700000}}))["auth"]["pbkdf2_iterations"], 700000)


if __name__ == "__main__":
    unittest.main()
