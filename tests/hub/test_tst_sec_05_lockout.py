"""TST-SEC-05 (AC-SEC-05, FR-SEC-01, BEH-SEC-02) - 5 consecutive bad logins lock the account: a 6th login with the
correct password within 15 min -> E-AUTH-LOCKED; after 15 min it succeeds. Values 5/15/15 are the Stage 12
proposals (A-12-F09-1, Stage 24 to confirm), read from config; a non-default setting is honoured too."""
import unittest

import _support as S
import _inc03 as H
from hub.security.errors import AuthBadCredentials, AuthLocked


def setUpModule():
    S.require_sandbox()


class TST_SEC_05_Lockout(unittest.TestCase):

    def _run(self, st, threshold, duration):
        pw = H.password()
        st.authn.create_user("lock-user", pw, ["reviewer"], "op")
        for i in range(threshold):
            st.clock.advance(10)
            with self.assertRaises(AuthBadCredentials):
                st.authn.login("lock-user", "wrong-" + str(i), "sec05")
        st.clock.advance(60)
        with self.assertRaises(AuthLocked) as cm:
            st.authn.login("lock-user", pw, "sec05")
        self.assertEqual((cm.exception.code, cm.exception.http), ("E-AUTH-LOCKED", 423))
        st.clock.advance(duration - 60 - 1)
        with self.assertRaises(AuthLocked):
            st.authn.login("lock-user", pw, "sec05")
        st.clock.advance(2)
        token = st.authn.login("lock-user", pw, "sec05")
        self.assertEqual(len(token), 64)
        actions = [(r["action"], r["outcome"]) for r in st.audit_rows()]
        self.assertEqual(actions.count(("LOCKOUT", "success")), 1)
        self.assertEqual(actions.count(("LOGIN", "denied")), threshold + 2)
        self.assertEqual(actions[-1], ("LOGIN", "success"))

    def test_TST_SEC_05_a_default_5_15_15(self):
        """TST-SEC-05 / AC-SEC-05: default 5 failures / 15 min window / 15 min lock."""
        st = H.Store("sec05a-")
        try:
            self.assertEqual((st.s["auth"]["lockout_threshold"], st.s["auth"]["lockout_window_seconds"],
                              st.s["auth"]["lockout_duration_seconds"]), (5, 900, 900))
            self._run(st, 5, 900)
        finally:
            st.close()

    def test_TST_SEC_05_b_configurable(self):
        """TST-SEC-05: lockout values are configuration (3 failures, 120 s lock)."""
        st = H.Store("sec05b-", extra={"auth": {"lockout_threshold": 3, "lockout_duration_seconds": 120}})
        try:
            self._run(st, 3, 120)
        finally:
            st.close()

    def test_TST_SEC_05_c_failures_outside_window_do_not_lock(self):
        """TST-SEC-05: 4 failures, 16 min pause, 4 failures -> never 5 inside 15 min -> correct password still works."""
        st = H.Store("sec05c-")
        try:
            pw = H.password()
            st.authn.create_user("slow-user", pw, ["reviewer"], "op")
            for burst in range(2):
                for i in range(4):
                    with self.assertRaises(AuthBadCredentials):
                        st.authn.login("slow-user", "nope", "sec05")
                st.clock.advance(16 * 60)
            self.assertEqual(len(st.authn.login("slow-user", pw, "sec05")), 64)
        finally:
            st.close()


if __name__ == "__main__":
    unittest.main()
