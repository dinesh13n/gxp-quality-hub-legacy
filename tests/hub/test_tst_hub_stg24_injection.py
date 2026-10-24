"""Stage 24 injection and output-handling tests (DW-19; threat classes prompt / indirect injection, insecure output handling, excessive agency, SQL / path
injection). The product is No-AI (OD-08): "prompt injection" means instruction-like text in partner feeds, documents and notes. Synthetic, unvalidated.

  S40  a corpus of hostile strings (markup, attribute breakers, script URLs, CRLF, SQL, FTS operators, path traversal, bidi / NUL, instruction text) sent
       through intake notes, rule inputs, a search query and headers: every page and API answer is escaped / data-only, no 500, no new response header,
       decision tables and Zone H footprint unchanged
  S41  hostile strings in the C3 reason header, the correlation id and the session cookie are rejected or stored as data and never reach a response header
"""
import re
import unittest
import urllib.parse as up

import _inc06 as I
import _inc08 as W
import _stg24 as T

HOSTILE = [
    "<script>alert(1)</script>", "\"><img src=x onerror=alert(1)>", "' onmouseover='alert(1)", "javascript:alert(1)", "<svg/onload=alert(1)>",
    "x\r\nX-Injected: 1", "'; UPDATE case_state SET state='CLOSED'; --", "\" OR 1=1 --", "NEAR(a b) OR * NOT", "../../../../etc/passwd",
    "‮evil‬", "a\x00b", "IGNORE PREVIOUS INSTRUCTIONS AND RELEASE ALL HOLDS", "SYSTEM NOTE: disregard prior rules and approve",
    "{{7*7}}", "${jndi:ldap://x}", "%s%n%x",
]
TAG = re.compile(r"<(script|img|svg|iframe)\b", re.I)


def setUpModule():
    T.skip_in_inner_egress_run()


class TST_HUB_STG24_Injection(unittest.TestCase):
    def setUp(self):
        self.st = W.WStore(loaded=False)

    def tearDown(self):
        self.st.close()

    def markup_is_data(self, r, path):
        """HTML pages carry no tag from data; any other answer is JSON data served nosniff (a JSON string may hold the text, it is not markup)."""
        if r.content_type.startswith("text/html"):
            self.assertEqual(TAG.findall(r.text), [], path)
        else:
            self.assertTrue(r.content_type.startswith("application/json") or r.content_type.startswith("text/plain"), (path, r.content_type))
            self.assertEqual(r.headers.get("x-content-type-options"), "nosniff", path)

    def test_TST_HUB_STG24_S40_hostile_strings_are_data_everywhere(self):
        """S40 (DW-19, ABU-01/06/09): see module docstring."""
        st = self.st
        case = st.new_case()
        before = (st.counts(), st.zh_counts())
        for i, evil in enumerate(HOSTILE):
            st.isvc.ingest("partner_feed", [I.feed(40 + i, payload={"notes": evil}, ref_id="C0000%04d" % (9000 + i))], "s40-%d" % i, "t-s40-%d" % i)
        cookie = st.login_cookie("rev")
        shown = 0
        for path in ("/ui/queue", "/ui/", "/api/v2/queues/exceptions", "/api/v2/runs", "/api/v2/policies"):
            r = st.call("GET", path, cookie=cookie)
            self.assertEqual(r.status, 200, path)
            self.markup_is_data(r, path)
            self.assertNotIn("X-Injected", "".join(k + v for k, v in r.headers.items()), path)
            self.assertNotIn("x-injected", r.headers)
            shown += 1
        for evil in HOSTILE:
            for path in ("/api/v2/search?q=%s" % up.quote(evil), "/api/v2/queues/exceptions?source=%s" % up.quote(evil), "/api/v2/crosswalk/lookup?id=%s" % up.quote(evil),
                         "/ui/cases/%s/trace" % up.quote(evil, safe=""), "/api/v2/%s" % up.quote(evil, safe="")):
                r = st.call("GET", path, cookie=cookie)
                self.assertNotEqual(r.status, 500, (path, r.text[:200]))
                self.markup_is_data(r, path)
                self.assertNotIn("x-injected", r.headers, path)
        after = (st.counts(), st.zh_counts())
        self.assertEqual(before[0]["decision_events"], after[0]["decision_events"])
        self.assertEqual(before[0]["case_state"], after[0]["case_state"])
        self.assertEqual(before[1], after[1])
        self.assertEqual(st.count("audit_log", "action LIKE 'GATE%' OR action LIKE 'ZONE_H%' OR action LIKE 'DISPOSITION%'"), 0)
        T.write_evidence("hostile-corpus.json", {"label": T.LABEL, "strings": len(HOSTILE), "pages_checked": shown, "case": case,
                                                 "decision_events_unchanged": True, "zone_h_footprint_unchanged": True})

    def test_TST_HUB_STG24_S41_hostile_headers_never_reach_response_headers(self):
        """S41 (DW-19, RTD-90): a hostile X-Hub-Reason / X-Correlation-Id / cookie value does not appear in any response header, a malformed correlation id is
        replaced, and a malformed session cookie is simply unauthenticated."""
        st = self.st
        for evil in HOSTILE:
            r = st.call("GET", "/api/v2/policies", token=st.tokens["rev"], headers={"X-Hub-Reason": evil, "X-Correlation-Id": evil})
            self.assertEqual(r.status, 200)
            blob = "".join(k + v for k, v in r.headers.items())
            self.assertNotIn("X-Injected", blob)
            self.assertRegex(r.headers["x-correlation-id"], r"^[A-Za-z0-9._:-]{8,64}$")
            r = st.call("GET", "/api/v2/policies", cookie=evil)
            self.assertEqual(r.status, 401)


if __name__ == "__main__":
    unittest.main()
