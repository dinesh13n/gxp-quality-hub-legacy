"""INC-08 tests of the HTTP surface that the plan assigns to earlier test families but that need the HTTP/UI surface (override rule C1):
TST-DEC-22, TST-INT-02, TST-MET-02, TST-MET-12, TST-MET-21, TST-RUN-04, TST-SEC-02, TST-SEC-03, TST-SEC-07, TST-SEC-08, TST-SEC-17.

Naming: the methods are test_I8_<FAMILY>_<NN>_... (not test_TST_<FAMILY>_<NN>_...) on purpose. The frozen selectors of the earlier groups (`-k TST_SEC`, `-k TST_DEC`,
`-k TST_INT`, `-k TST_MET`, `-k TST_RUN`) must keep selecting the same tests, so the INC-08 additions carry the `I8_` marker and are run by the INC-08 group
(-k I8_). Each docstring starts with the planned test id. Synthetic, unvalidated data.
"""
import json
import threading
import unittest

import _support as S
import _inc08 as W
import _http8 as H
from hub.metrics.sources import RowsSource
from hub.security import audit
from hub.web import tokens
from hub.web.routes import Table


def setUpModule():
    W.skip_in_inner_egress_run()


class _Base(unittest.TestCase):
    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def store(self, *a, **kw):
        st = W.WStore(*a, **kw)
        self.stores.append(st)
        return st


def fill(path):
    """A concrete path for a route template (authorisation happens before any handler, so any well-formed value serves)."""
    out = []
    for seg in path.split("/"):
        out.append("C90000001" if seg.startswith("{") else seg)
    return "/".join(out)


def strip_computed(o):
    if isinstance(o, dict):
        return dict((k, strip_computed(v)) for k, v in o.items() if k != "computed_at")
    if isinstance(o, list):
        return [strip_computed(v) for v in o]
    return o


class I8_Http(_Base):

    def test_I8_DEC_22_concurrent_posts_with_the_same_expected_seq(self):
        """TST-DEC-22 / AC-DEC-22: two clients both read seq 4 and each posts with expected_seq 4 over the loopback listener -> exactly one succeeds, the
        other receives E-DEC-SEQ-CONFLICT (409, retryable); repeated for several cases."""
        st = self.store()
        cases = ["C9000010%d" % i for i in range(5)]
        for c in cases:
            st.mk(c)
            st.move(c, "UNDER_REVIEW", expected_seq=1)
            st.move(c, "ESCALATED", expected_seq=2)
            st.move(c, "UNDER_REVIEW", expected_seq=3)
        with H.Served(st.app) as srv:
            for c in cases:
                seen = st.get("/api/v2/cases/%s/state" % c, "rev").json()
                self.assertEqual(seen["last_seq"], 4, seen)
                out, gate = [], threading.Barrier(2)

                def post(to_state, who):
                    gate.wait(10)
                    r = srv.request("POST", "/api/v2/cases/%s/transitions" % c,
                                    {"to_state": to_state, "event_type": "STATUS_CHANGE", "basis": "synthetic %s" % who, "expected_seq": 4},
                                    {"Authorization": "Bearer " + st.tokens["rev"], "X-Hub-Request": "1"})
                    out.append((r.status, r.json()))
                ts = [threading.Thread(target=post, args=a) for a in (("ESCALATED", "A"), ("OPEN", "B"))]
                for t in ts:
                    t.start()
                for t in ts:
                    t.join(30)
                self.assertEqual(sorted(s for s, _ in out), [201, 409], out)
                lost = [b for s, b in out if s == 409][0]
                self.assertEqual(lost["error"]["code"], "E-DEC-SEQ-CONFLICT")
                self.assertTrue(lost["error"]["retryable"])
                self.assertEqual(st.con.execute("SELECT last_seq FROM case_state WHERE case_id = ?", (c,)).fetchone()[0], 5)
        self.assertEqual(st.app.last_exception, None)

    def test_I8_INT_02_raw_intake_is_immutable_over_http_and_sql(self):
        """TST-INT-02 / AC-INT-02: any raw_intake row -> UPDATE or DELETE is rejected E-INT-RAW-IMMUTABLE (trigger); the HTTP surface has no update or
        delete route for it (PUT / PATCH / DELETE are refused as unregistered); posting the same item again stores a new row, never an overwrite."""
        import sqlite3
        import _inc06 as I
        st = self.store()
        env = dict((k, I.feed(3)[k]) for k in ("source_key", "partner", "schema_rev", "source_ts", "ref_id", "record_kind", "payload_text"))
        r = st.post("/api/v2/intake/items", {"source": "partner_feed", "envelope": env}, "ql")
        self.assertEqual(r.status, 403, r.text)  # a quality_lead is not an intake caller
        stok = self.service_token(st)
        r1 = st.call("POST", "/api/v2/intake/items", {"source": "partner_feed", "envelope": env}, token=stok)
        self.assertEqual(r1.status, 201, r1.text)
        raw = r1.json()["raw_id"]
        digest = st.con.execute("SELECT content_hash, raw_bytes FROM raw_intake WHERE raw_id = ?", (raw,)).fetchone()
        for sql in ("UPDATE raw_intake SET partner = 'x' WHERE raw_id = ?", "DELETE FROM raw_intake WHERE raw_id = ?"):
            with self.assertRaises(sqlite3.DatabaseError) as cm:
                st.con.execute(sql, (raw,))
            self.assertIn("E-INT-RAW-IMMUTABLE", str(cm.exception))
            st.con.rollback()
        for method in ("PUT", "PATCH", "DELETE"):
            r = st.call(method, "/api/v2/intake/items/" + raw, {"partner": "x"}, token=stok)
            self.assertEqual((r.status, r.code), (403, "E-AUTH-FORBIDDEN"), (method, r.text))
        r2 = st.call("POST", "/api/v2/intake/items", {"source": "partner_feed", "envelope": env}, token=stok)
        self.assertEqual(r2.status, 201, r2.text)
        self.assertNotEqual(r2.json()["raw_id"], raw)
        self.assertEqual(r2.json()["outcome"], "NOOP_DUPLICATE")
        self.assertEqual(st.con.execute("SELECT content_hash, raw_bytes FROM raw_intake WHERE raw_id = ?", (raw,)).fetchone(), digest)
        got = st.get("/api/v2/intake/items/" + raw, "rev").json()
        self.assertEqual(got["raw"]["raw_id"], raw)

    def service_token(self, st, name="svc-int"):
        st.authn.create_user(name, st.pw, ["integration"], "op", kind="service")
        return tokens.issue(st.con, st.clock, st.anchor, name, "synthetic service token", "op")

    def metric_store(self):
        rows = [("r%03d" % i, "10.00") for i in range(97)] + [("blank", ""), ("bad", "abc"), ("neg", "-5.50")]
        return self.store(app_kw={"sources": {"fixture": RowsSource("vendor_rows.amount_text", rows)}})

    def test_I8_MET_02_every_figure_carries_tag_policy_status_and_label(self):
        """TST-MET-02 / AC-MET-02: every figure returned by the metric endpoints (time to close, month-end total, backlog, unresolved-exception rate, combine)
        carries the definition tag, policy version, policy status and the label 'synthetic, unvalidated'."""
        st = self.metric_store()
        cutoff = "cutoff_ts=2030-01-01T00:00:00.000000Z&denominator_ref=fixture&source=fixture&allow_partial=1"
        figures = []
        r = st.get("/api/v2/metrics/time-to-close", "ql")
        self.assertEqual(r.status, 200, r.text)
        figures += r.json()["items"]
        self.assertGreaterEqual(len(figures), 2)  # one separate series per configured clock
        for path in ("/api/v2/metrics/month-end-total?" + cutoff, "/api/v2/metrics/backlog?definition_tag=D-OPS&as_of=2030-01-01",
                     "/api/v2/metrics/backlog?definition_tag=D-OPS&as_of=2030-01-01&kind=exception_rate"):
            r = st.get(path, "ql")
            self.assertEqual(r.status, 200, (path, r.text))
            figures.append(r.json())
        c = st.post("/api/v2/metrics/combine", {"values": [], "op": "sum"}, "ql")
        self.assertEqual(c.status, 400)  # nothing to combine is a request error, never a figure
        stored = st.met.backlog_by_site("D-OPS", "2030-01-01", None)
        stored2 = st.met.backlog_by_site("D-OPS", "2030-01-02", None)
        comb = st.post("/api/v2/metrics/combine", {"values": [stored.value_id, stored2.value_id], "op": "sum"}, "ql")
        self.assertEqual(comb.status, 201, comb.text)
        figures.append(comb.json())
        for f in figures:
            self.assertIn("definition_tag", f)
            self.assertIn("policy_version", f)
            self.assertIn("policy_status", f)
            self.assertEqual(f["label"], W.LABEL, f)
        tagged = [f for f in figures if f["metric_id"] != "MET-MONTH-END-TOTAL"]
        for f in tagged:
            self.assertIsNotNone(f["definition_tag"], f["metric_id"])
            self.assertIn(f["policy_status"], ("candidate", "adopted", "accepted-open"))
        reg = st.get("/api/v2/metrics/registry", "ql")
        self.assertEqual(reg.status, 200)

    def test_I8_MET_12_unparsable_amounts_are_named_or_flagged_partial(self):
        """TST-MET-12 / AC-MET-12: 100 text amounts with 1 blank, 1 'abc' and 1 negative -> the default call is E-MET-UNPARSABLE-INPUT naming the 2 rows; with
        allow_partial the result is flagged partial with 2 errors; the negative value is summed as-is and flagged NEGATIVE_VALUE."""
        st = self.metric_store()
        base = "/api/v2/metrics/month-end-total?cutoff_ts=2030-01-01T00:00:00.000000Z&denominator_ref=fixture&source=fixture"
        r = st.get(base, "ql")
        self.assertEqual((r.status, r.code), (422, "E-MET-UNPARSABLE-INPUT"), r.text)
        det = r.json()["error"]["details"]
        self.assertEqual((det["count"], sorted(x["row_id"] for x in det["rows"])), (2, ["bad", "blank"]))
        ok = st.get(base + "&allow_partial=true", "ql")
        self.assertEqual(ok.status, 200, ok.text)
        v = ok.json()
        self.assertIs(v["partial"], True)
        self.assertEqual(len(v["errors"]), 2)
        self.assertEqual(sorted(e["code"] for e in v["errors"]), ["BLANK_AMOUNT", "UNPARSABLE_AMOUNT"])
        self.assertEqual(v["value"], "964.50")  # 97 x 10.00 + (-5.50), the negative summed as-is
        self.assertEqual([f["code"] for f in v["detail"]["flags"]], ["NEGATIVE_VALUE"])
        miss = st.get("/api/v2/metrics/month-end-total?denominator_ref=fixture&source=fixture", "ql")
        self.assertEqual((miss.status, miss.code), (422, "E-MET-CUTOFF-REQUIRED"))

    def test_I8_MET_21_metric_endpoints_are_deterministic(self):
        """TST-MET-21 / AC-MET-21: any metric endpoint called twice with identical parameters returns byte-identical JSON (computed_at excluded)."""
        st = self.metric_store()
        stored = st.met.backlog_by_site("D-OPS", "2030-01-01", None)
        paths = ["/api/v2/metrics/time-to-close", "/api/v2/metrics/backlog?definition_tag=D-OPS&as_of=2030-01-01",
                 "/api/v2/metrics/backlog?definition_tag=D-OPS&as_of=2030-01-01&kind=exception_rate", "/api/v2/metrics/registry",
                 "/api/v2/metrics/month-end-total?cutoff_ts=2030-01-01T00:00:00.000000Z&denominator_ref=fixture&source=fixture&allow_partial=1",
                 "/api/v2/metrics/values/%s/reproduce" % stored.value_id]
        for p in paths:
            a, b = st.get(p, "ql"), st.get(p, "ql")
            self.assertEqual((a.status, b.status), (200, 200), (p, a.text))
            self.assertEqual(json.dumps(strip_computed(a.json()), sort_keys=True), json.dumps(strip_computed(b.json()), sort_keys=True), p)
        n = st.count("metric_value")
        st.get(paths[0], "ql")
        self.assertEqual(st.count("metric_value"), n)  # a GET stores nothing: reads are repeatable and side-effect free

    def test_I8_RUN_04_manual_run_needs_a_run_role(self):
        """TST-RUN-04 / AC-RUN-04: an authenticated reviewer (no manual-run role) -> POST /runs is E-AUTH-FORBIDDEN; with role quality_lead the run starts and
        its record is returned; the trigger over HTTP is only 'manual'."""
        st = self.store()
        body = {"job": "verify_projection", "trigger": "manual"}
        r = st.post("/api/v2/runs", body, "rev")
        self.assertEqual((r.status, r.code), (403, "E-AUTH-FORBIDDEN"), r.text)
        self.assertEqual(st.count("run_event"), 0)
        self.assertEqual(st.count("audit_log", "action = 'AUTHZ_DENIED' AND actor = 'rev' AND object_ref = 'OP-RUN-01'"), 1)
        ok = st.post("/api/v2/runs", body, "ql")
        self.assertEqual(ok.status, 201, ok.text)
        rec = ok.json()
        self.assertEqual((rec["job"], rec["trigger"], rec["outcome"]), ("verify_projection", "manual", "finished"))
        self.assertEqual(st.get("/api/v2/runs/" + rec["run_id"], "rev").json()["run_id"], rec["run_id"])
        self.assertEqual([x["run_id"] for x in st.get("/api/v2/runs", "rev").json()["items"]], [rec["run_id"]])
        sched = st.post("/api/v2/runs", {"job": "verify_projection", "trigger": "scheduled"}, "ql")
        self.assertEqual((sched.status, sched.code), (400, "E-REQ-INVALID"))
        unk = st.post("/api/v2/runs", {"job": "nope"}, "ql")
        self.assertEqual((unk.status, unk.code), (404, "E-RUN-UNKNOWN-JOB"))

    def test_I8_SEC_02_unregistered_or_undeclared_routes_are_denied(self):
        """TST-SEC-02 / AC-SEC-02: a route registered without a permission declaration -> the route-registry test fails; at run time such a route denies every
        caller, and an unregistered path is refused 403 and audited. Every shipped route (48 API + 10 pages) declares its roles."""
        t = Table()
        self.assertEqual((len(t.api), len(t.ui)), (48, 10))

        def problems(routes):
            return [r["op_id"] for r in routes if not isinstance(r.get("roles"), list) or not r["roles"] or not r.get("method") or not r.get("path")]
        self.assertEqual(problems(t.api + t.ui), [])
        bad = {"op_id": "OP-X-99", "method": "GET", "path": "/api/v2/undeclared", "roles": []}
        self.assertEqual(problems([bad]), ["OP-X-99"])  # the registry check fails for a route without a declaration
        st = self.store()
        st.app.table = Table(api=t.api + [bad], ui=t.ui)
        r = st.get("/api/v2/undeclared", "comp")
        self.assertEqual((r.status, r.code), (403, "E-AUTH-FORBIDDEN"))
        before = st.count("audit_log", "action = 'AUTHZ_DENIED'")
        for method, path in (("GET", "/api/v2/not-a-route"), ("POST", "/api/v2/cases"), ("DELETE", "/api/v2/runs"), ("GET", "/"), ("GET", "/admin"),
                             ("OPTIONS", "/api/v2/runs"), ("GET", "/api/v2/runs/../auth/login")):
            r = st.call(method, path, token=st.tokens["comp"])
            self.assertEqual((r.status, r.code), (403, "E-AUTH-FORBIDDEN"), (method, path))
        self.assertEqual(st.count("audit_log", "action = 'AUTHZ_DENIED'") - before, 7)
        self.assertNotIn("not-a-route", json.dumps([r["details"] for r in st.audit_actions("AUTHZ_DENIED")]))  # the probed path is never copied into audit

    def test_I8_SEC_03_roles_outside_their_matrix_row_are_forbidden_and_audited(self):
        """TST-SEC-03 / AC-SEC-03: roles reviewer, finance_read and integration each call every operation outside their matrix row -> 403 E-AUTH-FORBIDDEN (or
        E-GATE-NOT-AUTHORISED on the Zone H choke point) and an audit record with outcome denied."""
        st = self.store()
        st.authn.create_user("fin", st.pw, ["finance_read"], "op")
        ftok = st.login_cookie("fin")
        stok = self.service_token(st)
        t = Table()
        callers = {"reviewer": ("rev", st.tokens["rev"]), "finance_read": ("fin", ftok), "integration": ("svc-int", stok)}
        total = 0
        for role, (actor, token) in callers.items():
            before = st.count("audit_log", "outcome = 'denied' AND actor = ?", (actor,))
            n = 0
            for rt in t.api:
                if role in rt["roles"] or "public" in rt["roles"]:
                    continue
                r = st.call(rt["method"], fill(rt["path"]), {} if rt["method"] == "POST" else None, token=token)
                want = "E-GATE-NOT-AUTHORISED" if rt["op_id"] in ("OP-GATE-01", "OP-GATE-02") else "E-AUTH-FORBIDDEN"
                self.assertEqual((r.status, r.code), (403, want), (role, rt["op_id"], r.text))
                n += 1
            self.assertGreaterEqual(n, 10, role)
            self.assertEqual(st.count("audit_log", "outcome = 'denied' AND actor = ?", (actor,)) - before, n, role)
            total += n
        self.assertEqual(st.zh_counts()[0], st.count("decision_events"))
        self.assertGreaterEqual(total, 45)

    def test_I8_SEC_07_idle_and_absolute_session_limits(self):
        """TST-SEC-07 / AC-SEC-07: a session idle beyond 30 minutes, or older than 8 hours, is 401 E-AUTH-SESSION-EXPIRED (audited); a session in use is kept
        alive until the absolute limit."""
        st = self.store()
        tok = st.login_cookie("rev")
        self.assertEqual(st.call("GET", "/api/v2/gate/status", token=tok).status, 200)
        st.clock.advance(30 * 60 + 5)
        r = st.call("GET", "/api/v2/gate/status", token=tok)
        self.assertEqual((r.status, r.code), (401, "E-AUTH-SESSION-EXPIRED"), r.text)
        self.assertEqual(st.count("audit_log", "action = 'SESSION_EXPIRED'"), 1)
        again = st.call("GET", "/api/v2/gate/status", token=tok)
        self.assertEqual((again.status, again.code), (401, "E-AUTH-UNAUTHENTICATED"))  # the expired session stays revoked
        tok2 = st.login_cookie("rev")
        for _ in range(19):  # 19 x 25 min = 7 h 55 min of use
            st.clock.advance(25 * 60)
            self.assertEqual(st.call("GET", "/api/v2/gate/status", token=tok2).status, 200)
        st.clock.advance(10 * 60)
        r = st.call("GET", "/api/v2/gate/status", token=tok2)
        self.assertEqual((r.status, r.code), (401, "E-AUTH-SESSION-EXPIRED"), r.text)
        page = st.call("GET", "/ui/queue", cookie=tok2)
        self.assertEqual((page.status, page.headers.get("location")), (303, "/ui/login"))

    def test_I8_SEC_08_service_token_cannot_log_in_or_act_for_a_human(self):
        """TST-SEC-08 / AC-SEC-08: a service token used on interactive login, on a Zone H route or on a human-link route -> login refused; Zone H and the human
        link refused and audited; zero Zone H events."""
        st = self.store()
        stok = self.service_token(st)
        before = st.zh_counts()
        r = st.call("POST", "/api/v2/auth/login", {"username": "svc-int", "password": stok}, csrf=False)
        self.assertEqual((r.status, r.code), (401, "E-AUTH-BAD-CREDENTIALS"), r.text)
        r = st.call("POST", "/api/v2/auth/login", {"username": stok, "password": st.pw}, csrf=False)
        self.assertEqual((r.status, r.code), (401, "E-AUTH-BAD-CREDENTIALS"))
        denied = st.count("audit_log", "outcome = 'denied'")
        z = st.call("POST", "/api/v2/zone-h/actions", {"action": "ZH-01", "authority_ref": "x", "reauth_token": "0" * 64}, token=stok)
        self.assertEqual((z.status, z.code), (403, "E-GATE-NOT-AUTHORISED"), z.text)
        lk = st.call("POST", "/api/v2/crosswalk/links", {"from_type": "case", "from_id": "C00000001", "to_type": "case", "to_id": "C00000002",
                                                         "reason": "x"}, token=stok)
        self.assertEqual((lk.status, lk.code), (403, "E-AUTH-FORBIDDEN"), lk.text)
        self.assertEqual(st.count("audit_log", "outcome = 'denied'") - denied, 2)
        self.assertEqual(st.count("crosswalk_link", "creator_kind = 'human'"), 0)
        self.assertEqual(st.zh_counts(), before)
        ses = st.call("POST", "/api/v2/auth/reauth", {"password": st.pw}, token=stok)
        self.assertEqual(ses.status, 403)
        self.assertNotIn(stok, json.dumps(st.audit_actions()))  # the token itself is never written to audit
        tokens.revoke(st.con, st.clock, st.anchor, stok, "op")
        gone = st.call("GET", "/api/v2/runs", token=stok)
        self.assertEqual((gone.status, gone.code), (401, "E-AUTH-UNAUTHENTICATED"))

    def test_I8_SEC_17_writes_without_csrf_proof_are_refused(self):
        """TST-SEC-17 / AC-SEC-17: a state-changing form post without a CSRF token, or a JSON write without the custom header -> E-SEC-CSRF and no change; with
        the proof the same request works."""
        st = self.store()
        st.load_rules()
        case = st.new_case()
        t = st.add_trace(case)
        n0 = st.counts()
        r = st.call("POST", "/api/v2/cases/%s/facts" % case, {"fact_type": "FACT_OPS_CLOSED", "expected_seq": 1}, token=st.tokens["rev"], csrf=False)
        self.assertEqual((r.status, r.code), (403, "E-SEC-CSRF"), r.text)
        r = st.call("POST", "/api/v2/cases/%s/facts" % case, {"fact_type": "FACT_OPS_CLOSED", "expected_seq": 1}, token=st.tokens["rev"], csrf=False,
                    ctype="text/plain")
        self.assertIn(r.status, (400, 403))  # a cross-site "simple" request (text/plain, no header) never reaches the handler
        cookie = st.login_cookie("rev")
        for form in ("action=override&reason=x", "csrf_token=&action=override&reason=x", "csrf_token=%s&action=override&reason=x" % ("0" * 64)):
            r = st.call("POST", "/ui/flags/%s/override" % t["flag_id"], raw=form, cookie=cookie, ctype="application/x-www-form-urlencoded", csrf=False)
            self.assertEqual((r.status, r.code), (403, "E-SEC-CSRF"), (form, r.text))
        self.assertEqual(st.counts(), n0)
        self.assertEqual(st.count("flag_action"), 0)
        self.assertGreaterEqual(st.count("audit_log", "action = 'CSRF_REFUSED'"), 4)
        ok = st.call("POST", "/api/v2/cases/%s/facts" % case, {"fact_type": "FACT_OPS_CLOSED", "expected_seq": 1}, token=st.tokens["rev"])
        self.assertEqual(ok.status, 201, ok.text)
        self.assertEqual(st.get("/api/v2/gate/status", "rev").status, 200)  # reads need no proof


if __name__ == "__main__":
    unittest.main()
