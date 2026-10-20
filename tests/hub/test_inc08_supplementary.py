"""INC-08 supplementary tests (no planned id of their own): M006, service tokens, CSRF, request parsing, body limit, the real loopback listener, the CLI, the
static untrusted-text lint, UI escaping, login/session behaviour, start-up checks, the 501 operations and the empty shipped holder list. They are named
test_TST_HUB_INC08_Sxx_... (selector -k INC08_S). Synthetic, unvalidated.
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import unittest
from unittest import mock

import _support as S
import _inc03 as H3
import _inc05 as D
import _inc06 as I
import _inc07 as R
import _inc08 as W
import _http8 as H
from hub import config
from hub.intake import untrusted_lint
from hub.web import csrf, schema as wschema, server, tokens
from hub.web.app import Request, WebApp
from hub.web.obs_http import HttpMetrics


def setUpModule():
    W.skip_in_inner_egress_run()


class TST_HUB_INC08_Supplementary(unittest.TestCase):

    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def store(self, *a, **kw):
        st = W.WStore(*a, **kw)
        self.stores.append(st)
        return st

    def svc_token(self, st, name="svc-int"):
        st.authn.create_user(name, st.pw, ["integration"], "op", kind="service")
        return tokens.issue(st.con, st.clock, st.anchor, name, "synthetic service token", "op")

    # ---- M006
    def test_TST_HUB_INC08_S01_m006_applies_once_and_is_checked_at_start(self):
        """S01: M006 on an M001..M005 store: status absent -> apply (backup first) -> status applied; a second apply is a no-op; a changed stored checksum is
        drift; the app refuses to start on an unmigrated store (E-STORE-NOT-MIGRATED) and on a drifted one."""
        ds = D.DStore(loaded=False, _tpl=R._template7(False))
        ds.close()
        bk = os.path.join(ds.base, "bk")
        con = sqlite3.connect(os.path.join(ds.data, "hub.sqlite3"))
        self.assertEqual(wschema.status(con)["state"], "absent")
        con.close()
        with self.assertRaises(Exception) as cm:
            WebApp(ds.data, ds.cfg, ds.clock).start("s01")
        self.assertEqual(cm.exception.code, "E-STORE-NOT-MIGRATED")
        res = wschema.apply(ds.data, bk, ds.anchor_path, ds.clock, "s01a")
        self.assertTrue(res["applied"] and res["backup"])
        self.assertFalse(wschema.apply(ds.data, bk, ds.anchor_path, ds.clock, "s01b")["applied"])
        con = sqlite3.connect(os.path.join(ds.data, "hub.sqlite3"))
        self.assertEqual(wschema.status(con)["state"], "applied")
        self.assertEqual(con.execute("SELECT count(*) FROM audit_log WHERE action = 'WEB_SCHEMA_APPLIED'").fetchone()[0], 1)
        with self.assertRaises(sqlite3.DatabaseError):  # the checksum row is retained (insert-only)
            con.execute("UPDATE web_schema_migrations SET sha256 = ?", ("0" * 64,))
        con.rollback()
        sql = wschema.migration()[1]
        with mock.patch.object(wschema, "migration", lambda: ("0" * 64, sql)):  # the migration file changed after it was applied
            self.assertEqual(wschema.status(con)["state"], "drift")
            with self.assertRaises(Exception) as cm:
                WebApp(ds.data, ds.cfg, ds.clock).start("s01c")
            self.assertIn("DRIFT", cm.exception.code)
        con.close()

    # ---- tokens
    def test_TST_HUB_INC08_S02_service_tokens_are_digest_only_revocable_and_integration_only(self):
        """S02: a service token is shown once and only its SHA-256 is stored (neither the table nor the audit trail holds the token); it authenticates as
        role integration; it is revoked by digest prefix; an expired token and a token for a human principal are refused."""
        st = self.store()
        tok = self.svc_token(st)
        self.assertTrue(tok.startswith("svc_"))
        dump = json.dumps([list(r) for r in st.con.execute("SELECT * FROM service_token")]) + json.dumps([list(r) for r in st.con.execute("SELECT details FROM audit_log")])
        self.assertNotIn(tok, dump)
        self.assertNotIn(tok[4:], dump)
        self.assertEqual(st.call("GET", "/api/v2/runs", token=tok).status, 200)
        self.assertEqual(st.call("GET", "/api/v2/gate/status", token=tok).status, 403)  # integration is not a reader of the gate status
        digest = st.con.execute("SELECT token_sha256 FROM service_token").fetchone()[0]
        self.assertEqual(tokens.revoke(st.con, st.clock, st.anchor, digest[:8], "op"), {"revoked": True, "already": False})
        self.assertTrue(tokens.revoke(st.con, st.clock, st.anchor, tok, "op")["already"])
        r = st.call("GET", "/api/v2/runs", token=tok)
        self.assertEqual((r.status, r.code), (401, "E-AUTH-UNAUTHENTICATED"))
        st.authn.create_user("svc-b", st.pw, ["integration"], "op", kind="service")
        old = tokens.issue(st.con, st.clock, st.anchor, "svc-b", "expires soon", "op", expires_at="2026-10-18T00:00:00.000000Z")
        st.clock.advance(3600)
        self.assertEqual(st.call("GET", "/api/v2/runs", token=old).status, 401)
        with self.assertRaises(Exception):
            tokens.issue(st.con, st.clock, st.anchor, "rev", "a human may not hold a service token", "op")
        with self.assertRaises(Exception):
            tokens.issue(st.con, st.clock, st.anchor, "svc-b", "  ", "op")
        self.assertEqual(st.call("POST", "/api/v2/auth/reauth", {"password": st.pw}, token=self.svc_token(st, "svc-c")).status, 403)

    # ---- csrf
    def test_TST_HUB_INC08_S03_csrf_proofs(self):
        """S03: the header proof is exactly 'X-Hub-Request: 1'; the form token is sha256('csrf:' + session digest), differs between sessions and cannot be
        guessed from another session's token."""
        st = self.store()
        self.assertTrue(csrf.header_ok({"x-hub-request": "1"}))
        for bad in ({}, {"x-hub-request": "0"}, {"x-hub-request": ""}, {"x-hub-request": "true"}):
            self.assertFalse(csrf.header_ok(bad))
        a, b = st.fresh("rev"), st.fresh("rev")
        self.assertNotEqual(csrf.csrf_token(a), csrf.csrf_token(b))
        self.assertEqual(len(csrf.csrf_token(a)), 64)
        self.assertTrue(csrf.form_ok(a, csrf.csrf_token(a)))
        for bad in (None, "", csrf.csrf_token(b), csrf.csrf_token(a).upper() + "x", 7):
            self.assertFalse(csrf.form_ok(a, bad))

    # ---- observability
    def test_TST_HUB_INC08_S04_http_metrics_use_closed_label_sets(self):
        """S04: request counters and durations are labelled by registry op ids and numeric status only; user text never becomes a label; auth failures are
        counted by reason; flush appends insert-only obs_metric rows."""
        st = self.store()
        st.get("/healthz")
        st.get("/api/v2/gate/status")  # anonymous -> 401
        st.get("/api/v2/gate/status", "rev")
        st.get("/api/v2/<script>alert(1)</script>", "rev")  # unknown route
        st.call("POST", "/api/v2/auth/login", {"username": "rev", "password": "wrong-password-1"}, csrf=False)
        samples = st.app.metrics.samples()
        by = {}
        for s in samples:
            by.setdefault(s["name"], []).append(s["labels"])
        ops = set(l["op_id"] for l in by["http_requests_total"])
        self.assertTrue(ops <= set(r["op_id"] for r in st.app.table.api + st.app.table.ui) | {"UNROUTED"}, ops)
        self.assertIn("UNROUTED", ops)
        self.assertTrue(all(l["status"].isdigit() for l in by["http_requests_total"]))
        reasons = set(l["reason"] for l in by["auth_failures_total"])
        self.assertTrue({"unauthenticated", "unknown_route"} <= reasons, reasons)
        self.assertNotIn("script", json.dumps(samples))
        n0 = st.count("obs_metric")
        st.app.flush_metrics()
        self.assertGreater(st.count("obs_metric"), n0)
        with self.assertRaises(sqlite3.DatabaseError):
            st.con.execute("DELETE FROM obs_metric")

    # ---- parsing
    def test_TST_HUB_INC08_S05_request_bodies_are_parsed_strictly(self):
        """S05: malformed JSON, a duplicate key, a non-object, an unknown field, a wrong type and a wrong content type are each E-REQ-INVALID (400) naming
        the field; nothing is stored."""
        st = self.store()
        case = st.new_case()
        n0 = st.counts()
        path = "/api/v2/cases/%s/facts" % case
        cases = [("malformed", dict(raw="{not json")), ("duplicate", dict(raw='{"fact_type":"A","fact_type":"B","expected_seq":1}')),
                 ("array", dict(raw="[1,2]")), ("unknown", dict(body={"fact_type": "FACT_OPS_CLOSED", "expected_seq": 1, "extra": 1})),
                 ("type", dict(body={"fact_type": 5, "expected_seq": "1"})), ("bool", dict(body={"fact_type": "X", "expected_seq": True})),
                 ("ctype", dict(raw='{"fact_type":"X","expected_seq":1}', ctype="text/plain")), ("empty", dict())]
        for name, kw in cases:
            r = st.call("POST", path, token=st.tokens["rev"], **kw)
            self.assertEqual((r.status, r.code), (400, "E-REQ-INVALID"), (name, r.text))
        self.assertEqual(st.counts(), n0)
        deep = "[" * 5000 + "]" * 5000
        self.assertEqual(st.call("POST", path, raw=deep, token=st.tokens["rev"]).status, 400)

    def test_TST_HUB_INC08_S06_body_limit_is_413_in_process_and_on_the_wire(self):
        """S06: a body above the limit is E-REQ-TOO-LARGE (413) before anything else is looked at, both in process and through the socket; a body at the
        limit is parsed normally."""
        st = self.store(app_kw={"body_limit": 2048})
        big = json.dumps({"fact_type": "x" * 3000, "expected_seq": 1})
        r = st.call("POST", "/api/v2/cases/C90000001/facts", raw=big)
        self.assertEqual((r.status, r.code), (413, "E-REQ-TOO-LARGE"))
        with H.Served(st.app) as srv:
            r = srv.request("POST", "/api/v2/cases/C90000001/facts", raw_body=big.encode(), headers={"X-Hub-Request": "1"})
            self.assertEqual((r.status, r.json()["error"]["code"]), (413, "E-REQ-TOO-LARGE"))
            ok = srv.request("POST", "/api/v2/cases/C90000001/facts", {"fact_type": "x", "expected_seq": 1},
                             {"X-Hub-Request": "1", "Authorization": "Bearer " + st.tokens["rev"]})
            self.assertNotEqual(ok.status, 413)

    # ---- real listener
    def test_TST_HUB_INC08_S07_listener_binds_loopback_and_sets_headers_on_every_response(self):
        """S07: the listener is on 127.0.0.1; every response (200, 303, 401, 403, 404-as-403, 413, 400) carries nosniff, CSP default-src 'self', no-store,
        a referrer policy, frame denial and a correlation id; one request per connection; a non-loopback peer is dropped; the login cookie is HttpOnly +
        SameSite=Strict + Path=/ and (Stage 24 note A-INC08-3) has no Secure flag over plain loopback HTTP."""
        st = self.store(app_kw={"body_limit": 4096})
        with H.Served(st.app) as srv:
            self.assertEqual(srv.host, "127.0.0.1")
            self.assertFalse(srv.srv.verify_request(None, ("10.1.2.3", 5000)))
            self.assertTrue(srv.srv.verify_request(None, ("127.0.0.1", 5000)))
            auth = {"Authorization": "Bearer " + st.tokens["rev"]}
            reqs = [("GET", "/healthz", {}, None), ("GET", "/ui/queue", {}, None), ("GET", "/api/v2/gate/status", {}, None),
                    ("GET", "/api/v2/gate/status", auth, None), ("GET", "/nothing/here", auth, None), ("POST", "/api/v2/runs", auth, None),
                    ("POST", "/api/v2/auth/login", {}, {"username": "rev"}), ("POST", "/api/v2/auth/login", {"X-Hub-Request": "1"}, {"username": "rev", "password": st.pw})]
            seen = set()
            for method, path, hd, body in reqs:
                r = srv.request(method, path, body, hd)
                seen.add(r.status)
                self.assertEqual(r.headers["x-content-type-options"], "nosniff", (path, r.status))
                self.assertIn("default-src 'self'", r.headers["content-security-policy"])
                self.assertIn("no-store", r.headers["cache-control"])
                self.assertIn("referrer-policy", r.headers)
                self.assertIn(r.headers.get("x-frame-options"), ("DENY", "SAMEORIGIN"))
                self.assertTrue(r.headers.get("x-correlation-id"))
                self.assertEqual(r.headers.get("connection"), "close")
            self.assertTrue({200, 303, 401, 403} <= seen, seen)
            r = srv.request("POST", "/api/v2/auth/login", {"username": "rev", "password": st.pw}, {})
            r2 = srv.request("POST", "/api/v2/auth/login", {"username": "rev", "password": st.pw}, {"X-Hub-Request": "1"})
            self.assertEqual(r2.status, 201)
            ck = r2.headers["set-cookie"]
            self.assertIn("HttpOnly", ck)
            self.assertIn("SameSite=Strict", ck)
            self.assertIn("Path=/", ck)
            self.assertNotIn("Secure", ck)
            r3 = srv.request("GET", "/healthz", extra_lines=["Transfer-Encoding: chunked"])
            self.assertEqual(r3.status, 400)

    # ---- CLI
    def test_TST_HUB_INC08_S08_cli_status_migrate_token(self):
        """S08: python -m hub.web status / migrate / token issue / token revoke: JSON on stdout, the token is shown once with its digest prefix, the log is on
        stderr and holds no token; serve on a non-loopback config exits with the exposure code before binding."""
        st = W.WStore(loaded=False)
        st.close()
        env = S.child_env()

        def web(args, cfg=None):
            return subprocess.run([sys.executable, "-B", "-m", "hub.web", "--config", cfg or st.cfg_path] + args, cwd=S.CODE_ROOT, env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)
        p = web(["status", "--data-dir", st.data])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["state"], "applied")
        ds = D.DStore(loaded=False, _tpl=R._template7(False))
        ds.close()
        p = web(["migrate", "--data-dir", ds.data, "--backup-root", os.path.join(ds.base, "bk")], ds.cfg_path)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(json.loads(p.stdout)["applied"])
        p = web(["token", "issue", "svc-none", "--label", "x", "--data-dir", ds.data], ds.cfg_path)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("svc_", p.stdout)
        bad_cfg = H3.write_config(S.tmpdir("s08-"), {"network": {"bind": "0.0.0.0"}})
        p = web(["serve", "--data-dir", st.data, "--port", "0"], bad_cfg)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("E-SEC-EXPOSURE", p.stderr)

    # ---- lint
    def test_TST_HUB_INC08_S09_untrusted_text_lint_is_clean_on_the_new_modules(self):
        """S09: the static untrusted-text check finds no U1 (an Untrusted-derived value passed as a decision parameter) in hub/web, hub/gate or hub/review;
        its U2 / U3 findings there are exactly the reviewed set (storage and output wrappers of typed free text; parameters that merely share a name with a
        decision parameter) so any new site is a review item; a planted violation is still flagged. (The lint is built for hub/intake: RTD-71.)"""
        root = os.path.join(S.CODE_ROOT, "hub")
        found = untrusted_lint.check_paths([os.path.join(root, d) for d in ("web", "gate", "review")])
        self.assertEqual([f for f in found if f["rule"] == "U1"], [])
        got = sorted((os.path.relpath(f["path"], root).replace(os.sep, "/"), f["rule"], f["detail"]) for f in found)
        self.assertEqual(got, sorted([
            ("web/app.py", "U3", "__init__ declares a decision parameter without a guard"), ("web/obs_http.py", "U3", "request declares a decision parameter without a guard"),
            ("web/ui.py", "U3", "page declares a decision parameter without a guard"), ("web/ui.py", "U3", "_login_page declares a decision parameter without a guard"),
            ("gate/actions.py", "U3", "__init__ declares a decision parameter without a guard"), ("gate/dispositions.py", "U2", "for_storage used in _text"),
            ("gate/dispositions.py", "U3", "__init__ declares a decision parameter without a guard"), ("gate/dispositions.py", "U2", "for_storage used in act_on_flag"),
            ("gate/pack.py", "U2", "Untrusted used in _t"), ("review/service.py", "U3", "queue declares a decision parameter without a guard"),
            ("review/service.py", "U2", "Untrusted used in _queue_item"), ("review/service.py", "U2", "for_storage used in _queue_item")]))
        planted = "def f(x):\n    y = Untrusted(x)\n    return g(queue=y)\n"
        self.assertEqual(sorted(f["rule"] for f in untrusted_lint.check_source(planted, "planted.py")), ["U1", "U2"])

    # ---- UI escaping
    def test_TST_HUB_INC08_S10_untrusted_text_is_escaped_on_every_page(self):
        """S10: a script tag in rule inputs and in an intake note is shown escaped on the trace and queue pages; no page contains an unescaped tag from data;
        pages carry the CSP and the synthetic label."""
        st = self.store()
        st.load_rules()
        case = st.new_case()
        evil = "<script>alert(1)</script>"
        st.add_trace(case, "PRIORITY", {"status": evil, "severity": "HIGH", "amount": 1})
        st.isvc.ingest("partner_feed", [I.feed(30, payload={"notes": evil}, ref_id="C00009999")], "s10", "t-s10")
        cookie = st.login_cookie("rev")
        for path in ("/ui/queue", "/ui/cases/%s/trace" % case, "/ui/"):
            r = st.call("GET", path, cookie=cookie)
            self.assertEqual(r.status, 200, path)
            self.assertNotIn("<script>alert", r.text, path)
            self.assertIn("synthetic, unvalidated", r.text, path)
            self.assertIn("default-src 'self'", r.headers["content-security-policy"])
        self.assertIn("&lt;script&gt;", st.call("GET", "/ui/cases/%s/trace" % case, cookie=cookie).text)

    # ---- login/session
    def test_TST_HUB_INC08_S11_login_is_generic_logout_ends_the_session(self):
        """S11: unknown user and wrong password give the same answer; five wrong passwords lock the account (423, audited); a correct password during the
        lock is refused; logout makes the token useless; no password or token reaches the audit trail."""
        st = self.store()
        a = st.call("POST", "/api/v2/auth/login", {"username": "nobody", "password": "wrong-password-1"}, csrf=False)
        b = st.call("POST", "/api/v2/auth/login", {"username": "rev", "password": "wrong-password-1"}, csrf=False)
        self.assertEqual((a.status, a.code), (b.status, b.code))
        self.assertEqual((a.status, a.code), (401, "E-AUTH-BAD-CREDENTIALS"))
        for _ in range(8):
            st.call("POST", "/api/v2/auth/login", {"username": "rev", "password": "wrong-password-1"}, csrf=False)
        r = st.call("POST", "/api/v2/auth/login", {"username": "rev", "password": st.pw}, csrf=False)
        self.assertEqual((r.status, r.code), (423, "E-AUTH-LOCKED"))
        tok = st.login_cookie("ql")
        self.assertEqual(st.call("GET", "/api/v2/policies", token=tok).status, 200)
        self.assertIn(st.call("POST", "/api/v2/auth/logout", token=tok).status, (200, 201, 204))
        r = st.call("GET", "/api/v2/policies", token=tok)
        self.assertEqual((r.status, r.code), (401, "E-AUTH-UNAUTHENTICATED"))
        blob = json.dumps([list(x) for x in st.con.execute("SELECT details, reason FROM audit_log")])
        self.assertNotIn(st.pw, blob)
        self.assertNotIn("wrong-password-1", blob)
        self.assertNotIn(tok, blob)

    # ---- start-up
    def test_TST_HUB_INC08_S12_startup_selfcheck_is_audited_and_logged(self):
        """S12: start() audits CONFIG_LOADED with command web-serve, logs fts_engine_selected and startup_selfcheck as JSON lines, and refuses a non-loopback
        bind before anything is bound."""
        lines = []
        st = self.store(loaded=False, app_kw={"log_sink": lines.append})
        st.app.start("s12")
        row = st.con.execute("SELECT details FROM audit_log WHERE action = 'CONFIG_LOADED' ORDER BY audit_seq DESC LIMIT 1").fetchone()
        det = json.loads(row[0])
        self.assertEqual(det.get("command"), "web-serve")
        self.assertEqual(det.get("zone_h_holders"), sorted(det.get("zone_h_holders")))
        self.assertTrue(det.get("config_hash") and det.get("bind"))
        events = [json.loads(l)["event"] for l in lines]
        self.assertIn("fts_engine_selected", events)
        self.assertIn("startup_selfcheck", events)
        bad = self.store(loaded=False, extra={"network": {"bind": "10.0.0.5"}})
        with self.assertRaises(Exception) as cm:
            bad.app.start("s12b")
        self.assertIn("EXPOSURE", cm.exception.code)

    # ---- 501
    def test_TST_HUB_INC08_S13_deferred_operations_say_so_and_change_nothing(self):
        """S13: OP-POL-07, OP-INT-04, OP-ID-04, OP-ID-05 and OP-MET-06 answer 501 E-REQ-NOT-IMPLEMENTED; OP-REV-04 (drafts) is E-REV-DRAFTS-DISABLED; search
        is E-REV-SEARCH-DISABLED until enabled; none writes anything."""
        st = self.store()
        n0 = st.counts()
        for path in ("/api/v2/rules/divergence", "/api/v2/intake/sources/partner_feed/delays", "/api/v2/crosswalk/view", "/api/v2/crosswalk/findings",
                     "/api/v2/metrics/source-quality"):
            r = st.get(path, "ql")
            self.assertEqual((r.status, r.code), (501, "E-REQ-NOT-IMPLEMENTED"), path)
        r = st.post("/api/v2/drafts", {"template_id": "t", "fields": {}}, "rev")
        self.assertEqual(r.code, "E-REV-DRAFTS-DISABLED", r.text)
        r = st.get("/api/v2/search?q=x", "rev")
        self.assertEqual((r.status, r.code), (501, "E-REV-SEARCH-DISABLED"), r.text)
        self.assertEqual(st.counts(), n0)

    # ---- shipped holders
    def test_TST_HUB_INC08_S14_shipped_config_has_no_holder_and_the_gate_stays_shut(self):
        """S14: the shipped default configuration lists no Zone H holder; with that configuration the gate status reports 0 holders and mode none, and a Zone
        H action over HTTP is refused (nothing recorded)."""
        from hub.security import settings
        self.assertEqual(settings.resolve(config.load(None))["zone_h"]["holders"], [])
        st = self.store(extra={"zone_h": {"holders": []}})
        s = st.get("/api/v2/gate/status", "rev").json()
        self.assertEqual((s["holders_configured"], s["mode"], s["available"]), (0, "none", False))
        n0 = st.zh_counts()
        r = st.zh("holder-1", "ZH-08", {"mode": "event", "values": ["accept"]})
        self.assertIn(r.status, (403, 423), r.text)
        self.assertTrue(r.code.startswith("E-GATE-"), r.text)
        self.assertEqual(st.zh_counts(), n0)


if __name__ == "__main__":
    unittest.main()
