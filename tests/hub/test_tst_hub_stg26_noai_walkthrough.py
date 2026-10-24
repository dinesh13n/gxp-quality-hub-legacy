"""Stage 26 No-AI proof and walkthrough rehearsal (DW-21 / DW-22; OD-08; thresholds RT-11, RT-13). Synthetic, unvalidated.

  D01  the product has no model or network client: deny-list scan rc 0, no client import in hub/, and under a socket tripwire the hostile corpus (which contains URLs
       and 'call the model' instructions) causes zero connection attempts, zero DNS lookups and zero model calls
  D02  AGENT REHEARSAL of the human walkthroughs TST-REV-03 / 04 / 08 against the rendered pages. It is NOT a walkthrough: it is not observed, performed or signed by
       Dinesh or any reviewer, and RT-13 stays open until the signed records exist (docs/26-tevv/walkthrough-records.md).
"""
import ast
import json
import os
import re
import socket
import unittest

import _support as S
import _inc06 as I
import _inc08 as W
import _stg26 as T

CLIENT_MODULES = {"requests", "httpx", "aiohttp", "urllib3", "http.client", "urllib.request", "ftplib", "smtplib", "poplib", "imaplib", "telnetlib", "xmlrpc.client",
                  "openai", "anthropic", "cohere", "transformers", "torch", "tensorflow", "langchain", "sklearn", "numpy", "google.generativeai", "boto3"}


def setUpModule():
    T.skip_in_inner_egress_run()


def tearDownModule():
    W.close_shipped()


def imports_of(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module)
            out.update(n.module + "." + a.name for a in n.names)
    return out


class TST_HUB_STG26_NoAI(unittest.TestCase):

    def test_TST_HUB_STG26_D01_no_model_or_network_client(self):
        """D01 (RT-11, OD-08): (a) no-ai-check rc 0; (b) no hub/ module imports a model or network CLIENT library (the listener uses http.server only); (c) hostile
        corpus (URLs, 'call the model' text) through the API with socket tripwires installed -> 0 connects, 0 name lookups; (d) obs tripwire model_calls_total = 0."""
        p = S.run_hub(["no-ai-check"])
        self.assertEqual(p.returncode, 0, p.stderr)
        found = {}
        for dp, _, fs in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            for f in fs:
                if f.endswith(".py"):
                    hit = sorted(m for m in imports_of(os.path.join(dp, f)) if m in CLIENT_MODULES)
                    if hit:
                        found[os.path.relpath(os.path.join(dp, f), S.CODE_ROOT)] = hit
        # the ONE documented exception: the loopback-only, GET-only gateway adapter (ADR-002 R2, AD-04); it is not a model client and its URL guard is probed below
        self.assertEqual(found, {"hub/adapters/gateway_client.py": ["urllib.request"]}, "client library imported in hub/ outside the documented adapter")
        from hub.adapters import gateway_client
        from hub.intake.errors import UrlSchemeRefused
        refused = 0
        for u in ("http://example.com/x", "https://api.openai.com/v1/chat", "http://10.0.0.1/", "http://169.254.169.254/latest/meta-data", "file:///etc/passwd", "ftp://127.0.0.1/",
                  "http://127.0.0.1.evil.example/", "http://localhost.evil.example/", "gopher://127.0.0.1/", "javascript:alert(1)", "http://[::ffff:8.8.8.8]/", None, 5):
            with self.assertRaises(UrlSchemeRefused, msg=repr(u)):
                gateway_client.check_url(u)
            refused += 1
        for u in ("http://127.0.0.1:8080/feed", "http://localhost/feed", "http://[::1]/feed"):
            gateway_client.check_url(u)
        attempts = []
        real = (socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo, socket.create_connection)

        def trip(name):
            def f(*a, **k):
                attempts.append((name, repr(a[1:2] if name.startswith("socket") else a[:1])))
                raise OSError("S26 tripwire: " + name)
            return f
        socket.socket.connect = trip("socket.connect")
        socket.socket.connect_ex = trip("socket.connect_ex")
        socket.getaddrinfo = trip("getaddrinfo")
        socket.create_connection = trip("create_connection")
        st = W.WStore()
        try:
            case = st.new_case("C92000001")
            urls = [s for _, _, s in T.strings() if "http" in s.lower() or "model" in s.lower() or "ignore" in s.lower()]
            self.assertGreaterEqual(len(urls), 5)
            for s in urls:
                st.call("POST", "/api/v2/cases/%s/evidence" % case, {"kind": "document", "source": "s", "source_ref": s[:200], "access_level": "quality", "notes": s},
                        token=st.tokens["rev"])
            for path in ("/ui/queue", "/ui/cases/%s/trace" % case):
                st.call("GET", path, cookie=st.login_cookie("rev"))
            tw = st.con.execute("SELECT name, SUM(value) FROM obs_metric WHERE name IN ('model_calls_total','egress_attempts_total') GROUP BY name").fetchall()
        finally:
            socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo, socket.create_connection = real
            st.close()
        self.assertEqual(attempts, [], "network activity from the product")
        self.assertEqual([r for r in tw if r[1]], [], "tripwire counter non-zero")
        T.write_evidence("no-ai-proof.json", {"label": T.LABEL, "no_ai_check_rc": 0, "client_imports_in_hub": "1 (loopback-only gateway adapter, URL guard probed: %d hostile URLs refused)" % refused, "hostile_strings_sent": len(urls), "connect_attempts": 0,
                                             "dns_lookups": 0, "model_calls_total": 0, "egress_attempts_total": 0,
                                             "scope": "deterministic product only; the sandbox harness tripwires are exercised again by E26"})

    def test_TST_HUB_STG26_D02_agent_rehearsal_of_walkthroughs_REV_03_04_08(self):
        """D02 (RT-13 stays OPEN): an AGENT REHEARSAL of the three human walkthroughs, producing evidence for the reviewer to compare against. Not observed or signed
        by any person."""
        rec = {"label": T.LABEL, "kind": "AGENT REHEARSAL - NOT a human walkthrough - NOT observed or signed by Dinesh or any reviewer", "rt_13": "OPEN", "steps": {}}
        # REV-03: shipped backlog paging
        sh = W.shipped_store()
        p1 = sh.get("/api/v2/queues/exceptions?limit=500", "rev").json()
        total = sh.count("intake_current", "queue IS NOT NULL")
        self.assertEqual((len(p1["items"]), p1["limit"], p1["total"]), (100, 100, total))
        self.assertIsNotNone(p1["next"])
        page = sh.call("GET", "/ui/queue", cookie=sh.login_cookie("rev"))
        self.assertEqual(page.status, 200)
        rec["steps"]["TST-REV-03"] = {"expected": "limit 500 is clamped to 100; next link; total shown", "observed": {"items": 100, "limit": 100, "total": total,
                                      "has_next": True, "queue_page_status": 200}}
        # REV-04: script in notes
        st = W.WStore()
        try:
            st.isvc.ingest("partner_feed", [I.feed(1, payload={"notes": "<script>alert(1)</script>"}, ref_id="C00009999")], "t-d02", "t-d02")
            pg = st.call("GET", "/ui/queue", cookie=st.login_cookie("rev"))
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", pg.text)
            self.assertNotIn("<script", pg.text.lower())
            self.assertIn("untrusted source text", pg.text)
            rec["steps"]["TST-REV-04"] = {"expected": "script text shown escaped, untrusted marker, no live script, CSP default-src 'self'",
                                          "observed": {"escaped": True, "untrusted_marker": True, "live_script": False,
                                                       "csp": pg.headers["content-security-policy"][:60]}}
            # REV-08: controls
            st.load_rules()
            case = st.new_case()
            for fn, ref, inp in (("PRIORITY", "as-found-python@1", {"status": "OPEN", "severity": "HIGH", "amount": 10}),
                                 ("MANUAL_REVIEW", "as-found-python@1", {"status": "CLOSED", "severity": "HIGH"}),
                                 ("AMOUNT_LIMIT", "as-found-js@1", {"amount": 1000, "region": "MARS", "year": 2026})):
                st.add_trace(case, fn, inp, ref)
            tp = st.call("GET", "/ui/cases/%s/trace" % case, cookie=st.login_cookie("rev"))
            counts = [tp.text.count('<option value="%s">%s</option>' % (a, a)) for a in ("override", "dismiss", "refuse")]
            self.assertEqual(counts, [3, 3, 3])
            rec["steps"]["TST-REV-08"] = {"expected": "override / dismiss / refuse offered for every open flag", "observed": {"flags": 3, "controls_per_flag": counts}}
        finally:
            st.close()
        rec["human_checks_not_covered"] = ["layout and readability on the reviewer's screen", "whether the escaped text is understandable to a reviewer",
                                           "whether the control labels are clear", "any visual defect or truncation", "the reviewer's own judgement of the wording"]
        T.write_evidence("walkthrough-rehearsal.json", rec)


if __name__ == "__main__":
    unittest.main()
