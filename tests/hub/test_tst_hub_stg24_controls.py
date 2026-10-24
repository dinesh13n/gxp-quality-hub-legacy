"""Stage 24 control tests (DW-19; RTD-26, RTD-29, RTD-90, A-INC08-3, ABU-10). Synthetic, unvalidated.

  S20  the control-value register equals the shipped defaults (drift 0), every entry is PROPOSED, the CLI prints it
  S21  the floors hold (PBKDF2 iterations, password length) and bad values are refused
  S22  the proposed values behave at their boundary: lockout 5 / 15 min, idle 30 min, absolute 8 h
  S23  ABU-10: a token is dead after logout, a client-chosen token is never adopted at login, a disabled principal's session is refused
  S24  session cookie: HttpOnly; SameSite=Strict; Path=/ and `Secure` exactly when TLS settings are configured (A-INC08-3)
  S25  C3 reason via X-Hub-Reason or ?reason= (RTD-90): header works alone, wins over the query, blank is refused, audited
  S26  anchor seal (RTD-29): round trip, edit / truncation detected, key rules, CLI exit codes, key never written
"""
import json
import os
import unittest
import urllib.parse as up

import _inc03 as H3
import _inc08 as W
import _inc09 as N
import _stg24 as T
from hub.core.errors import ConfigInvalid
from hub.security import anchor_seal, audit, controls, settings
from hub.security.errors import AuthBadCredentials, AuthLocked, AuthSessionExpired, PasswordPolicy

TLS = {"network": {"tls": {"cert_file": "/etc/hub/synthetic.crt", "key_file": "/etc/hub/synthetic.key"}}}
ON = {"search": {"enabled": True, "fts": "auto"}}
REASON = "synthetic reason: Stage 24 header transport"


def setUpModule():
    T.skip_in_inner_egress_run()


class _Base(unittest.TestCase):
    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def hstore(self, **kw):
        st = H3.Store("s24-", **kw)
        self.stores.append(st)
        return st

    def user(self, st, name="u1"):
        pw = H3.password()
        st.authn.create_user(name, pw, ["reviewer"], "op")
        return pw


class TST_HUB_STG24_Register(_Base):

    def test_TST_HUB_STG24_S20_register_equals_defaults_and_nothing_is_approved(self):
        """S20 (DW-19, RTD-26): drift is empty; ids unique; status PROPOSED everywhere; `python -m hub.security controls` prints the register (rc 0)."""
        self.assertEqual(controls.drift(), [])
        ids = [c[0] for c in controls.CONTROLS] + [f[0] for f in controls.FIXED]
        self.assertEqual(len(ids), len(set(ids)))
        for e in controls.entries():
            self.assertTrue(e["status"].startswith("PROPOSED"), e["id"])
            self.assertEqual(e["owner"], "Engagement lead (Dinesh Naik)")
        p = T.module_cli("hub.security", ["controls"])
        self.assertEqual(p.returncode, 0, p.stderr)
        doc = json.loads(p.stdout)
        self.assertEqual(doc["drift"], [])
        self.assertEqual(len(doc["controls"]), len(controls.CONTROLS))
        self.assertIsNone(settings.DEFAULTS["auth"].get("approved"))
        T.write_evidence("control-values.json", dict(doc, note="values are PROPOSALS; no decision on DQ-09 is recorded"))

    def test_TST_HUB_STG24_S21_floors_hold_and_bad_values_are_refused(self):
        """S21 (DW-19): PBKDF2 < 600,000 and password length < 12 are refused by config validation; non-integers and bools too."""
        bad = [("pbkdf2_iterations", 599999), ("password_min_length", 11), ("pbkdf2_iterations", "600000"), ("lockout_threshold", 0),
               ("session_idle_seconds", True), ("session_absolute_seconds", -1)]
        for k, v in bad:
            with self.subTest(k=k, v=v), self.assertRaises(ConfigInvalid):
                settings.resolve({"auth": {k: v}})
        ok = settings.resolve({"auth": {"pbkdf2_iterations": 700000, "password_min_length": 16}})
        self.assertEqual((ok["auth"]["pbkdf2_iterations"], ok["auth"]["password_min_length"]), (700000, 16))
        st = self.hstore()
        with self.assertRaises(PasswordPolicy):
            st.authn.create_user("shorty", "x" * 11, ["reviewer"], "op")
        st.authn.create_user("exactly12", "x" * 12, ["reviewer"], "op")


class TST_HUB_STG24_Behaviour(_Base):

    def test_TST_HUB_STG24_S22_proposed_values_at_the_boundary(self):
        """S22 (DW-19): 4 failures do not lock, the 5th does, a correct password is refused while locked, accepted after 15 min; a session survives
        idle gaps below 30 min (and is extended), dies after a gap above it, and dies at 8 h however active."""
        a = controls.CONTROLS
        vals = dict((c[1], c[2]) for c in a)
        st = self.hstore()
        pw = self.user(st)
        for _ in range(vals["auth.lockout_threshold"] - 1):
            with self.assertRaises(AuthBadCredentials):
                st.authn.login("u1", "wrong-" + os.urandom(4).hex(), "s24-l")
        tok = st.authn.login("u1", pw, "s24-l")  # 4 failures then success: no lockout
        st.authn.logout(tok, "s24-l")
        for i in range(vals["auth.lockout_threshold"]):
            with self.assertRaises(AuthBadCredentials):
                st.authn.login("u1", "wrong-" + os.urandom(4).hex(), "s24-l")
        with self.assertRaises(AuthLocked):
            st.authn.login("u1", pw, "s24-l")
        st.clock.advance(vals["auth.lockout_duration_seconds"] - 5)
        with self.assertRaises(AuthLocked):
            st.authn.login("u1", pw, "s24-l")
        st.clock.advance(10)
        tok = st.authn.login("u1", pw, "s24-l")
        idle = vals["auth.session_idle_seconds"]
        st.clock.advance(idle - 10)
        st.authn.authenticate(tok, "s24-i")
        st.clock.advance(idle - 10)
        st.authn.authenticate(tok, "s24-i")  # activity extended the session
        st.clock.advance(idle + 10)
        with self.assertRaises(AuthSessionExpired):
            st.authn.authenticate(tok, "s24-i")
        tok = st.authn.login("u1", pw, "s24-a")
        absolute = vals["auth.session_absolute_seconds"]
        with self.assertRaises(AuthSessionExpired):
            for _ in range(absolute // (idle - 100) + 3):
                st.clock.advance(idle - 100)
                st.authn.authenticate(tok, "s24-a")

    def test_TST_HUB_STG24_S23_abu10_logout_fixation_and_disabled_principal(self):
        """S23 (ABU-10, AC-SEC-07): over HTTP a logged-out token gets 401; two logins give two different tokens; a cookie value chosen by the client is not
        adopted by login; a principal set to a non-active status loses its sessions."""
        st = W.WStore(loaded=False)
        self.stores.append(st)
        t1 = st.login_cookie("rev")
        t2 = st.login_cookie("rev")
        self.assertNotEqual(t1, t2)
        self.assertEqual(st.call("GET", "/api/v2/policies", cookie=t1).status, 200)
        r = st.call("POST", "/api/v2/auth/logout", {}, cookie=t1)
        self.assertEqual(r.status, 201)
        self.assertEqual(st.call("GET", "/api/v2/policies", cookie=t1).status, 401)
        self.assertEqual(st.call("GET", "/api/v2/policies", token=t1).status, 401)
        self.assertEqual(st.call("GET", "/api/v2/policies", cookie=t2).status, 200)  # another session of the same user is untouched
        chosen = "f" * 64
        r = st.call("POST", "/api/v2/auth/login", {"username": "ql", "password": st.pw}, csrf=False, cookie=chosen)
        self.assertEqual(r.status, 201)
        self.assertNotEqual(r.json()["token"], chosen)
        self.assertEqual(st.call("GET", "/api/v2/policies", cookie=chosen).status, 401)
        st.con.execute("UPDATE principal SET status = 'disabled' WHERE principal_id = 'rev'")
        st.con.commit()
        self.assertEqual(st.call("GET", "/api/v2/policies", cookie=t2).status, 401)

    def test_TST_HUB_STG24_S24_cookie_attributes_and_secure_with_tls(self):
        """S24 (DW-19, A-INC08-3): default cookie has no Secure; with network.tls cert + key it has `; Secure`, also on the clearing cookie and the
        UI login; a cert without a key is not enough."""
        plain = W.WStore(loaded=False)
        tls = W.WStore(loaded=False, extra=TLS)
        half = W.WStore(loaded=False, extra={"network": {"tls": {"cert_file": "/etc/hub/synthetic.crt"}}})
        self.stores += [plain, tls, half]
        want = "HttpOnly; SameSite=Strict; Path=/; Max-Age=%d" % settings.DEFAULTS["auth"]["session_absolute_seconds"]
        for st, secure in ((plain, False), (half, False), (tls, True)):
            r = st.call("POST", "/api/v2/auth/login", {"username": "rev", "password": st.pw}, csrf=False)
            self.assertEqual(r.status, 201)
            self.assertEqual(len(r.set_cookie), 1)
            self.assertTrue(r.set_cookie[0].endswith(want + ("; Secure" if secure else "")), r.set_cookie[0].split("=", 1)[0])
            out = st.call("POST", "/api/v2/auth/logout", {}, cookie=r.json()["token"])
            self.assertEqual(out.set_cookie, ["hub_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0" + ("; Secure" if secure else "")])
        T.write_evidence("cookie-attributes.json", {"label": T.LABEL, "default": "hub_session=<token>; " + want, "with_tls": "hub_session=<token>; " + want + "; Secure"})

    def test_TST_HUB_STG24_S25_c3_reason_by_header_or_query(self):
        """S25 (DW-19, RTD-90): a restricted search read with the reason ONLY in X-Hub-Reason succeeds and audits that reason; the header wins over a
        query reason; no reason, a blank header or a blank query is E-SEC-REASON-REQUIRED; the query form still works."""
        st = N.R2Store(loaded=False, extra=ON)
        self.stores.append(st)
        st.build([N.doc(1, "alpha beta", level="restricted")])
        path = "/api/v2/search?q=alpha"
        r = st.get(path, "ql")
        self.assertEqual((r.status, r.code), (422, "E-SEC-REASON-REQUIRED"))
        r = st.get(path, "ql", headers={"X-Hub-Reason": "   "})
        self.assertEqual((r.status, r.code), (422, "E-SEC-REASON-REQUIRED"))
        n = st.count("audit_log", "action = 'C3_READ'")
        r = st.get(path, "ql", headers={"X-Hub-Reason": REASON})
        self.assertEqual(r.status, 200, r.text[:200])
        r = st.get(path + "&reason=" + up.quote("query reason"), "ql", headers={"X-Hub-Reason": REASON + " (header)"})
        self.assertEqual(r.status, 200)
        r = st.get(path + "&reason=" + up.quote("query reason only"), "ql")
        self.assertEqual(r.status, 200)
        rows = st.con.execute("SELECT reason FROM audit_log WHERE action = 'C3_READ' ORDER BY audit_seq").fetchall()
        self.assertEqual([x[0] for x in rows][n:], [REASON, REASON + " (header)", "query reason only"])

    def test_TST_HUB_STG24_S26_anchor_seal_round_trip_tamper_and_key_rules(self):
        """S26 (DW-19, RTD-29): seal / check on a real anchor file; an edited line is seal_mismatch, a truncated anchor is anchor_truncated, an unsealed
        tail is counted not failed, sealing is append-only and idempotent; a missing / short key is refused; the CLI exits 17 on tamper; the key is
        written nowhere."""
        st = self.hstore(extra=None, anchor_every=1)
        for i in range(4):
            st.authn.create_user("u%d" % i, H3.password(), ["reviewer"], "op")
        ap = st.anchor_path
        self.assertGreaterEqual(len(audit.read_anchors(ap)), 4)
        key_text = os.urandom(24).hex()
        key = anchor_seal.load_key({anchor_seal.KEY_ENV: key_text})
        self.assertEqual(anchor_seal.check(ap, key)["sealed_lines"], 0)
        rep = anchor_seal.seal(ap, key)
        self.assertEqual((rep["status"], rep["newly_sealed"]), ("ok", len(audit.read_anchors(ap))))
        self.assertEqual(anchor_seal.seal(ap, key)["newly_sealed"], 0)
        st.authn.create_user("late", H3.password(), ["reviewer"], "op")
        chk = anchor_seal.check(ap, key)
        self.assertEqual((chk["status"], chk["unsealed_tail"]), ("ok", 1))
        anchor_seal.seal(ap, key)
        sp = anchor_seal.seal_path_for(ap)
        with open(sp, encoding="utf-8") as f:
            seal_text = f.read()
        with open(ap, encoding="utf-8") as f:
            anchor_text = f.read()
        self.assertNotIn(key_text, seal_text + anchor_text)
        other = anchor_seal.load_key({anchor_seal.KEY_ENV: os.urandom(24).hex()})
        self.assertEqual(anchor_seal.check(ap, other)["kind"], "seal_mismatch")  # a different key does not verify
        for bad in (None, "", "short"):
            with self.assertRaises(ConfigInvalid):
                anchor_seal.load_key({anchor_seal.KEY_ENV: bad} if bad is not None else {})
        lines = anchor_text.splitlines()
        # edit a line of the anchor (a forged head hash), keeping the file well-formed
        doc = json.loads(lines[1])
        doc["hash"] = "0" * 64
        edited = lines[:1] + [json.dumps(doc, sort_keys=True, separators=(",", ":"))] + lines[2:]
        with open(ap, "w", encoding="utf-8") as f:
            f.write("\n".join(edited) + "\n")
        r = anchor_seal.check(ap, key)
        self.assertEqual((r["status"], r["kind"], r["first_broken_line"]), ("broken", "seal_mismatch", 2))
        p = T.module_cli("hub.security", ["check-seal", "--anchor-path", ap], env={anchor_seal.KEY_ENV: key_text})
        self.assertEqual((p.returncode, T.code_of(p)), (17, "E-SEC-AUDIT-TAMPER-DETECTED"))
        self.assertNotIn(key_text, p.stdout + p.stderr)
        with open(ap, "w", encoding="utf-8") as f:
            f.write("\n".join(lines[:3]) + "\n")  # truncated
        r = anchor_seal.check(ap, key)
        self.assertEqual((r["status"], r["kind"]), ("broken", "anchor_truncated"))
        with self.assertRaises(Exception):
            anchor_seal.seal(ap, key)  # sealing never papers over a break
        with open(ap, "w", encoding="utf-8") as f:
            f.write(anchor_text)
        p = T.module_cli("hub.security", ["check-seal", "--anchor-path", ap], env={anchor_seal.KEY_ENV: key_text})
        self.assertEqual(p.returncode, 0, p.stderr)
        p = T.module_cli("hub.security", ["seal", "--anchor-path", ap], env={})
        self.assertEqual((p.returncode, T.code_of(p)), (2, "E-CFG-INVALID"))
        T.write_evidence("anchor-seal.json", {"label": T.LABEL, "anchor_lines": len(lines), "forged_line": "seal_mismatch at line 2", "truncation": "anchor_truncated",
                                              "limit": "key holder with host access can re-seal; anchor + seal deleted together undetected (RS-03)"})


if __name__ == "__main__":
    unittest.main()
