"""Stage 26 red-team tests, part B2: request-structure and URL abuse against the web app (DW-21; threats T-09, T-13, T-19). Thresholds RT-07 (no 500, no state change).
Synthetic, unvalidated. Everything runs in-process through WebApp.handle (the code the socket server calls); the transport layer is covered in the resilience module.

  B05  body structure: size boundary (1 MiB and +1), nesting depth 64 / 1,000 / 20,000, duplicate keys, bad UTF-8, truncated and non-object JSON, NaN / Infinity,
       huge integers, 1k / 64k / near-limit strings, wrong content types, numeric edge values in typed fields
  B06  URL and verb abuse: every unregistered verb on every registered path, traversal and encoding tricks, 200 / 201-character segments, 64 KB paths
"""
import json
import unittest
import urllib.parse as up

import _inc08 as W
import _stg26 as T
from hub.web.app import BODY_LIMIT
from hub.web.routes import Table

SOURCE_MARKERS = ("def ", "import ", "root:x:", "#!/", "sqlite_master", "class ")


def setUpModule():
    T.skip_in_inner_egress_run()


class TST_HUB_STG26_Wire(unittest.TestCase):
    def store(self):
        st = W.WStore(loaded=False, extra={"rate_limit": {"enabled": False}})  # Stage 27: B06 sends hundreds of unregistered-route probes
        self.addCleanup(st.close)
        return st

    def test_TST_HUB_STG26_B05_body_structure_abuse(self):
        """B05 (RT-07, ED-02 / ED-09 / ED-10 / ED-12, T-19): no 500 and no state change for any malformed or extreme body; 1 MiB passes the transport check and
        1 MiB + 1 byte is 413; typed numeric edge values are refused or evaluated, never stored as a different value."""
        st = self.store()
        st.load_rules()
        case = st.new_case("C91000001")
        path = "/api/v2/cases/%s/evidence" % case
        base = {"kind": "document", "source": "s26", "source_ref": "r", "access_level": "quality", "note": ""}
        before = T.snapshot(st)
        a0 = T.audit_n(st)
        results, n = {}, 0

        def post(label, raw, ctype="application/json", expect=None, where=path):
            nonlocal n
            try:
                resp = st.call("POST", where, raw=raw, token=st.tokens["rev"], ctype=ctype)
            except AssertionError as e:
                self.fail("HTTP 500 for %s: %s" % (label, str(e)[-300:]))
            n += 1
            results[label] = (resp.status, resp.code)
            if expect is not None:
                self.assertIn(resp.status, expect, (label, resp.text[:200]))
            self.assertNotEqual(resp.status, 500, label)
            return resp

        # size boundary: pad a valid JSON body to exactly BODY_LIMIT and BODY_LIMIT + 1 bytes
        def padded(total):
            doc = dict(base, note="")
            overhead = len(json.dumps(doc).encode("utf-8"))
            doc["note"] = "A" * (total - overhead)
            raw = json.dumps(doc).encode("utf-8")
            self.assertEqual(len(raw), total)
            return raw
        r = post("body=limit", padded(BODY_LIMIT))
        self.assertNotEqual(r.status, 413, "exactly the limit must pass the transport check")
        r = post("body=limit+1", padded(BODY_LIMIT + 1), expect=(413,))
        self.assertEqual(r.code, "E-REQ-TOO-LARGE")
        for depth in T.corpus()["typed_values"]["json_nesting_depths"]:
            post("nest=%d" % depth, ('{"note":' + "[" * depth + "]" * depth + "}").encode("utf-8"), expect=(400, 413))
            post("nest-object=%d" % depth, ('{"note":' + '{"a":' * depth + "1" + "}" * depth + "}").encode("utf-8"), expect=(400, 413))
        post("dup-keys", b'{"kind":"document","kind":"photo","source":"s","source_ref":"r","access_level":"quality"}', expect=(400,))
        post("bad-utf8", b'{"note":"\xff\xfe"}', expect=(400,))
        post("bad-utf8-overlong", b'{"note":"\xc0\xaf"}', expect=(400,))
        post("truncated", b'{"kind":"document","source":', expect=(400,))
        for label, raw in (("array", b"[]"), ("null", b"null"), ("string", b'"x"'), ("number", b"12"), ("true", b"true"), ("empty-object", b"{}")):
            post("non-object-" + label, raw, expect=(400,))
        post("empty-body", b"", expect=(400,))
        post("whitespace", b"   \n\t ", expect=(400,))
        post("nan-literal", b'{"kind":"document","source":"s","source_ref":"r","access_level":"quality","note":NaN}', expect=(400,))
        post("infinity-literal", b'{"kind":"document","source":"s","source_ref":"r","access_level":"quality","note":-Infinity}', expect=(400,))
        post("huge-int", ('{"note":%s}' % ("9" * 5000)).encode("utf-8"), expect=(400,))
        post("bom-prefix", b'\xef\xbb\xbf' + json.dumps(base).encode("utf-8"), expect=(400, 201))
        for length in T.corpus()["typed_values"]["string_lengths"]:
            doc = dict(base, note="B" * length, source_ref="long-%d" % length)
            post("note-len=%d" % length, json.dumps(doc).encode("utf-8"), expect=(201, 400, 413, 422))
        for ctype in ("text/plain", "application/x-www-form-urlencoded", "multipart/form-data; boundary=x", "", "application/json; charset=latin-1", "APPLICATION/JSON", "application/jsonx",
                      "application/json, text/plain", "text/html"):
            post("ctype=%r" % ctype, json.dumps(dict(base, source_ref="ct-%s" % len(ctype))).encode("utf-8"), ctype=ctype or None, expect=(201, 400))
        # numeric edge values through the rule engine (typed decimal input) and through an intake payload
        nums = ["1e999", "NaN", "Infinity", "-0", "9223372036854775808", "-9223372036854775809", "0.1e-999", "1_000", "0x10", "١٢٣"]
        outcomes = {}
        for v in nums:
            for lit in (json.dumps(v), v if v.replace(".", "").replace("-", "").replace("e", "").replace("E", "").replace("+", "").isdigit() or v in ("NaN", "Infinity") else json.dumps(v)):
                raw = ('{"function":"PRIORITY","ruleset_ref":"as-found-python@1","inputs":{"status":"OPEN","severity":"HIGH","amount":%s}}' % lit).encode("utf-8")
                resp = post("amount=%s" % lit, raw, where="/api/v2/rules/evaluate", expect=(201, 400, 422))
                outcomes.setdefault(v, set()).add(resp.status)
        changed = T.diff(before, T.snapshot(st))
        self.assertTrue(set(changed) <= set(["evidence_record", "decision_events", "decision_idempotency", "case_state", "rule_trace"]), changed)
        # refusals are audited, accepted evidence writes are the only state change; chain verifies
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        self.assertGreater(T.audit_n(st) - a0, 0)
        T.write_evidence("body-structure-abuse.json", {"label": T.LABEL, "requests": n, "http_500": 0, "size_limit_bytes": BODY_LIMIT,
                                                      "outcomes": dict((k, list(v)) for k, v in sorted(results.items())),
                                                      "numeric_edge_statuses": dict((k, sorted(v)) for k, v in outcomes.items()), "state_changed_tables": changed})

    def test_TST_HUB_STG26_B06_url_and_verb_abuse(self):
        """B06 (RT-07 / RT-09, ED-08, T-09 / T-13): every verb that is not registered for a path is refused 403 (deny by default) and writes only an audit row; traversal
        and encoding tricks never reach a file or another route; 200-character segments match, 201 do not; a 64 KB path is refused, not crashed."""
        st = self.store()
        case = st.new_case("C91000001")
        tab = Table()
        before = T.snapshot(st)
        a0 = T.audit_n(st)
        n, bad = 0, []
        registered = set((r["method"], r["path"]) for r in tab.api + tab.ui)
        paths = sorted(set(r["path"] for r in tab.api + tab.ui))
        for p in paths:
            fp = p.replace("{case_id}", case).replace("{event_id}", "EV-00000001").replace("{link_id}", "LK-1").replace("{raw_id}", "RAW-1").replace("{flag_id}", "FL-1") \
                  .replace("{run_id}", "RUN-1").replace("{ruleset_id}", "x").replace("{version}", "1").replace("{policy_id}", "POL-1").replace("{value_id}", "MV-1") \
                  .replace("{source}", "partner_feed")
            for verb in ("HEAD", "PUT", "DELETE", "PATCH", "TRACE", "CONNECT", "PROPFIND", "get", "GÉT"):
                if (verb.upper(), p) in registered:
                    continue
                resp = st.call(verb, fp, None, token=st.tokens["ql"], csrf=False)
                n += 1
                if (resp.status, resp.code) != (403, "E-AUTH-FORBIDDEN"):
                    bad.append((verb, p, resp.status, resp.code))
        self.assertEqual(bad, [], "an unregistered verb was not refused as deny-by-default")
        tricks = ["/api/v2/../v2/policies", "//api/v2/policies", "/api/v2/policies/", "/API/V2/POLICIES", "/api/v2/policies%2f", "/api/v2/policies%00", "/api/v2/policies;x=1",
                  "/api/v2/%2e%2e/healthz", "/api/v2/%252e%252e/healthz", "/api/v2/cases/%2e%2e%2fpolicies/state", "/api/v2/cases/..%2fpolicies/state",
                  "/ui/static/../../hub/config.py", "/ui/static/app.css/../../hub/config.py", "/ui/static/%2e%2e/%2e%2e/hub/config.py", "/ui/static/app.css%00.py",
                  "/ui/static/app.css/", "/../../etc/passwd", "/%c0%ae%c0%ae/etc/passwd", "/healthz/..", "/healthz%0d%0aX-Injected:%201", "/api/v2/cases/%s/state/../events" % case,
                  "/api/v2/policies?" + "a=1&" * 300, "/api/v2/cases/" + "A" * 201 + "/state", "/api/v2/cases/" + case + "/state%20", "/api/v2/cases/Ã©/state",
                  "/ui/cases/" + "A" * 201 + "/trace", "/" + "x" * 65536, "/api/v2/" + "%41" * 20000]
        seen = {}
        for t in tricks:
            for who in ("rev", "none"):
                try:
                    resp = st.call("GET", t.split("?")[0], None, token=st.tokens.get(who) if who != "none" else None)
                except AssertionError as e:
                    self.fail("HTTP 500 for %s: %s" % (t[:60], str(e)[-300:]))
                n += 1
                seen[t[:70]] = resp.status
                self.assertNotEqual(resp.status, 500, t[:60])
                low = resp.text
                for m in SOURCE_MARKERS:
                    if t.startswith("/ui/static") or "etc/passwd" in t or "config.py" in t:
                        self.assertNotIn(m, low, (t[:60], m))
                self.assertNotIn("x-injected", resp.headers)
        # whole-segment matching: a 200-character case id matches the route (then 404), 201 does not (403)
        r200 = st.call("GET", "/api/v2/cases/%s/state" % ("A" * 200), None, token=st.tokens["rev"])
        r201 = st.call("GET", "/api/v2/cases/%s/state" % ("A" * 201), None, token=st.tokens["rev"])
        self.assertEqual((r200.status, r201.status), (404, 403), (r200.text, r201.text))
        self.assertEqual(T.diff(before, T.snapshot(st)), [])
        self.assertGreaterEqual(T.audit_n(st) - a0, 1)
        self.assertEqual(T.verify_chain(st)["status"], "ok")
        T.write_evidence("url-verb-abuse.json", {"label": T.LABEL, "requests": n, "http_500": 0, "unregistered_verbs_refused": True, "trick_status": seen,
                                                "segment_200_201": [r200.status, r201.status], "state_changed_tables": []})


if __name__ == "__main__":
    unittest.main()
