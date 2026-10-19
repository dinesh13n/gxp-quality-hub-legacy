"""TST-REV-01..08, 10, 14, 16, 17, 19 (F08 reviewer support: exception queue, rule-trace explanations, fallback search; INC-08). Synthetic, unvalidated.

TST-REV-03/04/08 are 'ui/manual-walkthrough' in the plan; here they are automated against the rendered pages (the human walkthrough stays a Stage 16 item).
TST-REV-10/14/16/17 are R2 criteria: the fallback engine exists and is disabled by default (`search.enabled`); these tests enable it on an injected document
provider and do not make search an R1 claim. TST-REV-16 is class B (OD-S12-12: FTS5 / runtime): FTS5 itself is INC-09.
"""
import ast
import json
import os
import random
import unittest

import _support as S
import _inc06 as I
import _inc08 as W


def setUpModule():
    W.skip_in_inner_egress_run()


def tearDownModule():
    W.close_shipped()


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

    def queue_fixture(self, st):
        """5 quarantined, 3 unmatched, 2 ambiguous and 4 NOOP_DUPLICATE items."""
        st.isvc.ingest("partner_feed", [I.feed(i, payload_text="{broken") for i in range(0, 5)] +
                       [I.feed(i, ref_id="C0000999%d" % i) for i in range(5, 8)], "t-q1", "t-q1")
        st.isvc.ingest("partner_feed", [I.feed(8), I.feed(9)], "t-q2", "t-q2", targets={"C00000009": ["C00000009", "DEV00000001"],
                                                                                         "C00000010": ["C00000010", "DEV00000002"]})
        st.isvc.ingest("partner_feed", [I.feed(i) for i in range(10, 14)], "t-q3", "t-q3")
        st.isvc.ingest("partner_feed", [I.feed(i) for i in range(10, 14)], "t-q4", "t-q4")  # the same four again -> NOOP_DUPLICATE


class TST_REV_Reviewer(_Base):

    def test_TST_REV_01_queue_lists_ten_items_without_duplicates(self):
        """AC-REV-01: 5 quarantined, 3 unmatched, 2 ambiguous and 4 NOOP_DUPLICATE items -> the queue view lists 10 (duplicates excluded), each with
        primary reason, queue, source, receipt_time and age."""
        st = self.store()
        self.queue_fixture(st)
        self.assertEqual(st.count("intake_outcome", "outcome = 'NOOP_DUPLICATE'"), 4)
        r = st.get("/api/v2/queues/exceptions", "rev")
        self.assertEqual(r.status, 200, r.text)
        out = r.json()
        self.assertEqual((out["total"], len(out["items"])), (10, 10))
        for it in out["items"]:
            for k in ("primary_reason", "queue", "source", "receipt_time", "age_hours", "raw_id", "flag_id"):
                self.assertIsNotNone(it[k], (k, it))
        self.assertEqual(sorted(it["queue"] for it in out["items"]), ["ambiguous_match"] * 2 + ["quarantine_invalid"] * 5 + ["unmatched"] * 3)
        self.assertEqual(sorted(set(it["source"] for it in out["items"])), ["partner_feed"])
        f = st.get("/api/v2/queues/exceptions?queue=unmatched", "rev").json()
        self.assertEqual((f["total"], len(f["items"])), (3, 3))

    def test_TST_REV_02_every_queue_item_appears_once(self):
        """AC-REV-02: a mixed store of several hundred items -> the queue view (paged) equals the set of items whose current outcome has a queue: 100% listed,
        none twice."""
        st = self.store()
        rnd = random.Random(8202)
        batch = []
        for i in range(300):
            k = rnd.randrange(8)
            batch.append(I.feed(i, payload_text="{broken") if k == 0 else I.feed(i, ref_id="C0000%04d" % (9000 + i)) if k == 1
                         else I.feed(i, payload={"quantity": -rnd.random() - 0.01}) if k == 2 else I.feed(i, schema_rev="unsupported") if k == 3
                         else I.feed(i))
        st.isvc.ingest("partner_feed", batch, "t-r02", "t-r02")
        st.isvc.ingest("partner_feed", batch[:40], "t-r02b", "t-r02b")  # replays: NOOP_DUPLICATE, never queued
        want = sorted(st.rev.all_queue_raw_ids())
        seen, cursor, pages = [], None, 0
        while True:
            r = st.get("/api/v2/queues/exceptions?limit=100" + ("&cursor=" + cursor if cursor else ""), "rev").json()
            seen += [it["raw_id"] for it in r["items"]]
            pages += 1
            cursor = r["next"]
            if not cursor:
                break
        self.assertGreater(len(want), 100)
        self.assertGreaterEqual(pages, 2)
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(sorted(seen), want)
        self.assertEqual(r["total"], len(want))

    def test_TST_REV_03_page_size_is_clamped_and_next_works_on_shipped_backlog(self):
        """AC-REV-03 (automated stand-in for the UI walkthrough): the shipped partner-feed backlog; limit=500 is clamped to 100, `next` works, totals are
        reported."""
        st = W.shipped_store()
        r = st.get("/api/v2/queues/exceptions?limit=500", "rev")
        self.assertEqual(r.status, 200, r.text[:300])
        p1 = r.json()
        self.assertEqual((len(p1["items"]), p1["limit"]), (100, 100))
        self.assertIsNotNone(p1["next"])
        total = st.count("intake_current", "queue IS NOT NULL")
        self.assertEqual(p1["total"], total)
        self.assertGreater(total, 1000)
        p2 = st.get("/api/v2/queues/exceptions?limit=500&cursor=" + p1["next"], "rev").json()
        self.assertEqual(len(p2["items"]), 100)
        self.assertFalse(set(i["raw_id"] for i in p1["items"]) & set(i["raw_id"] for i in p2["items"]))
        self.assertEqual(p2["total"], total)
        by_reason = dict(st.con.execute("SELECT primary_reason, count(*) FROM intake_current WHERE queue IS NOT NULL GROUP BY 1"))
        print("REV-03 shipped backlog by primary reason:", json.dumps(by_reason, sort_keys=True))

    def test_TST_REV_04_script_in_notes_is_shown_escaped(self):
        """AC-REV-04 (automated stand-in for the UI walkthrough): notes `<script>alert(1)</script>` -> the queue page shows `&lt;script&gt;`, carries the
        untrusted marker, and contains no live script."""
        st = self.store()
        st.isvc.ingest("partner_feed", [I.feed(1, payload={"notes": "<script>alert(1)</script>"}, ref_id="C00009999")], "t-r04", "t-r04")
        page = st.call("GET", "/ui/queue", cookie=st.login_cookie("rev"))
        self.assertEqual(page.status, 200, page.text[:300])
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page.text)
        self.assertNotIn("<script", page.text.lower())
        self.assertIn("untrusted source text", page.text)
        self.assertIn("default-src 'self'", page.headers["content-security-policy"])
        api = st.get("/api/v2/queues/exceptions", "rev").json()["items"][0]["notes"]
        self.assertEqual((api["trust"], api["text_escaped"]), ("untrusted", "&lt;script&gt;alert(1)&lt;/script&gt;"))

    def test_TST_REV_05_explanation_is_deterministic_and_names_the_row(self):
        """AC-REV-05: a stored trace of as-found-python for status CLOSED -> the explanation, generated twice, is identical and names the rule set, the row id,
        the input values and the outcome 'archive'."""
        st = self.store()
        st.load_rules()
        case = st.new_case()
        st.add_trace(case, "PRIORITY", {"status": "CLOSED", "severity": "LOW", "amount": 1})
        a, b = st.get("/api/v2/cases/%s/rule-trace" % case, "rev"), st.get("/api/v2/cases/%s/rule-trace" % case, "rev")
        self.assertEqual((a.status, a.raw), (200, b.raw))
        x = a.json()["explanations"][0]
        for needle in ("as-found-python@1", "PY-P1", "status=CLOSED", "Outcome: archive"):
            self.assertIn(needle, x["text"])
        self.assertEqual((x["function"], x["defaulted"], x["template_version"]), ("PRIORITY", False, "trace_template/1"))

    def test_TST_REV_06_defaulted_result_shows_marker_and_retained_value(self):
        """AC-REV-06: a defaulted result (region MARS) -> the explanation includes `defaulted: NO_MATCH_REGION_YEAR` and the retained as-found value."""
        st = self.store()
        st.load_rules()
        case = st.new_case()
        st.add_trace(case, "AMOUNT_LIMIT", {"amount": 1000, "region": "MARS", "year": 2026}, "as-found-js@1")
        x = st.get("/api/v2/cases/%s/rule-trace" % case, "rev").json()["explanations"][0]
        self.assertTrue(x["defaulted"])
        self.assertEqual(x["defaulted_reason"], "NO_MATCH_REGION_YEAR")
        self.assertIn("defaulted: NO_MATCH_REGION_YEAR", x["text"])
        self.assertIn("the retained as-found value is", x["text"])
        self.assertIn("999999", x["text"])

    def test_TST_REV_07_explanation_module_has_no_network_model_or_random(self):
        """AC-REV-07: the explanation module source (hub/review) is scanned: no network, model client, clock or random import or call."""
        banned = {"socket", "ssl", "urllib", "http", "requests", "random", "secrets", "time", "subprocess", "ftplib", "smtplib",
                  "openai", "anthropic", "langchain", "torch", "transformers", "httpx", "aiohttp"}
        calls = {"eval", "exec", "compile", "__import__", "open"}
        root = os.path.join(S.CODE_ROOT, "hub", "review")
        files = sorted(f for f in os.listdir(root) if f.endswith(".py"))
        self.assertIn("templates.py", files)
        for f in files:
            tree = ast.parse(open(os.path.join(root, f), encoding="utf-8").read())
            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    mods = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom):
                    mods = [n.module or ""]
                else:
                    mods = []
                for m in mods:
                    self.assertNotIn(m.split(".")[0], banned, (f, m))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                    self.assertNotIn(n.func.id, calls, (f, n.func.id))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                    self.assertNotIn(n.func.attr, ("now", "utcnow", "today", "monotonic", "perf_counter", "random", "urandom"), (f, n.func.attr))
        # the template module is pure: it imports only json
        tree = ast.parse(open(os.path.join(root, "templates.py"), encoding="utf-8").read())
        imported = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        self.assertEqual(imported, ["json"])

    def test_TST_REV_08_every_explanation_offers_override_dismiss_refuse(self):
        """AC-REV-08 (automated stand-in for the UI walkthrough): the explanation page shows the override / dismiss / refuse control for every open flag."""
        st = self.store()
        st.load_rules()
        case = st.new_case()
        for fn, ref, inp in (("PRIORITY", "as-found-python@1", {"status": "OPEN", "severity": "HIGH", "amount": 10}),
                             ("MANUAL_REVIEW", "as-found-python@1", {"status": "CLOSED", "severity": "HIGH"}),
                             ("AMOUNT_LIMIT", "as-found-js@1", {"amount": 1000, "region": "MARS", "year": 2026})):
            st.add_trace(case, fn, inp, ref)
        page = st.call("GET", "/ui/cases/%s/trace" % case, cookie=st.login_cookie("rev"))
        self.assertEqual(page.status, 200, page.text[:300])
        self.assertEqual(page.text.count('<option value="override">override</option>'), 3)
        self.assertEqual(page.text.count('<option value="dismiss">dismiss</option>'), 3)
        self.assertEqual(page.text.count('<option value="refuse">refuse</option>'), 3)
        self.assertEqual(page.text.count('name="csrf_token"'), 4)  # 3 forms + the log-out form
        self.assertEqual(page.text.count("/override"), 3)
        # the control works through the form post (csrf token from the page), and the page then shows the flag as overridden
        import re
        tok = re.search(r'name="csrf_token" value="([0-9a-f]{64})"', page.text).group(1)
        fid = st.con.execute("SELECT flag_id FROM rule_trace ORDER BY trace_id LIMIT 1").fetchone()[0]
        cookie = st.login_cookie("rev")
        tok = re.search(r'name="csrf_token" value="([0-9a-f]{64})"', st.call("GET", "/ui/cases/%s/trace" % case, cookie=cookie).text).group(1)
        r = st.call("POST", "/ui/flags/%s/override" % fid, raw="csrf_token=%s&action=override&reason=not+applicable" % tok, cookie=cookie,
                    ctype="application/x-www-form-urlencoded", csrf=False)
        self.assertEqual(r.status, 303, r.text)
        after = st.call("GET", "/ui/cases/%s/trace" % case, cookie=cookie)
        self.assertIn("is overridden", after.text)

    # ---- R2 search criteria (fallback engine, injected provider, disabled by default)
    def search_store(self):
        provider = W.corpus_provider()
        if provider is None:
            self.skipTest("the sandbox copy has no data/documents/source_documents.jsonl")
        return self.store(extra={"search": {"enabled": True}}, app_kw={"documents": provider})

    def test_TST_REV_10_injection_phrase_is_ordinary_text(self):
        """AC-REV-10 (R2): query "ignore previous" -> the 22-document injection set is found as ordinary matches, labelled untrusted; nothing else changes."""
        st = self.search_store()
        before = (st.zh_counts(), st.count("audit_log", "action <> 'AUTHZ_DENIED'"))
        r = st.get("/api/v2/search?q=%22ignore%20previous%22&limit=100", "ql")
        self.assertEqual(r.status, 200, r.text[:300])
        out = r.json()
        self.assertEqual((out["engine"], out["total"], len(out["items"])), ("fallback", 22, 22))
        for h in out["items"]:
            self.assertEqual((h["trust"], h["label"]), ("untrusted", "untrusted source text"))
            self.assertNotIn("<", h["snippet"])
        self.assertEqual(st.zh_counts(), before[0])
        # a reviewer is not a reader of 'restricted' documents: those are never ranked or counted for him
        rv = st.get("/api/v2/search?q=%22ignore%20previous%22&limit=100", "rev").json()
        self.assertEqual(rv["total"], 17)
        self.assertEqual(st.get("/api/v2/search?q=ignore", "ql").json()["total"], 22)

    def test_TST_REV_14_equal_scores_keep_a_stable_order(self):
        """AC-REV-14 (R2): two identical-score hits -> searched twice, the same order (effective_at desc, then doc_id)."""
        docs = [{"doc_id": "DOC-%08d" % i, "version": "revA", "effective_at": ea, "source": "synthetic", "locale": "en-US", "access_level": "quality",
                 "reference": None, "hash": "h", "body": "batch genealogy discrepancy", "ocr_confidence": None}
                for i, ea in ((3, "2025-01-01"), (1, "2025-01-01"), (2, "2026-01-01"), (5, "2024-01-01"), (4, "2025-01-01"))]
        st = self.store(extra={"search": {"enabled": True}}, app_kw={"documents": lambda: docs})
        a, b = st.get("/api/v2/search?q=genealogy", "rev"), st.get("/api/v2/search?q=genealogy", "rev")
        self.assertEqual(a.raw, b.raw)
        self.assertEqual([h["doc_id"] for h in a.json()["items"]], ["DOC-00000002", "DOC-00000001", "DOC-00000003", "DOC-00000004", "DOC-00000005"])

    def test_TST_REV_16_fallback_engine_is_selected_and_order_is_identical(self):
        """AC-REV-16 (class B, OD-S12-12; R2): FTS5 is not used (INC-09) -> the product starts with search.engine = fallback, announced in the start-up log, and
        the order for the REV-14 fixture is the documented one."""
        lines = []
        docs = [{"doc_id": "DOC-%08d" % i, "version": "revA", "effective_at": "2025-01-01", "source": "s", "locale": "en-US", "access_level": "quality",
                 "reference": None, "hash": "h", "body": "same words here", "ocr_confidence": None} for i in (2, 1, 3)]
        st = self.store(extra={"search": {"enabled": True}}, app_kw={"documents": lambda: docs, "log_sink": lines.append})
        st.app.start("t-start")
        ev = [json.loads(l) for l in lines]
        self.assertIn("fts_engine_selected", [e["event"] for e in ev])
        self.assertEqual(st.app.search.engine(), "fallback")
        out = st.get("/api/v2/search?q=words", "rev").json()
        self.assertEqual((out["engine"], [h["doc_id"] for h in out["items"]]), ("fallback", ["DOC-00000001", "DOC-00000002", "DOC-00000003"]))
        # disabled by default: no engine claim, E-REV-SEARCH-DISABLED
        st2 = self.store()
        r = st2.get("/api/v2/search?q=words", "rev")
        self.assertEqual((r.status, r.code), (501, "E-REV-SEARCH-DISABLED"))

    def test_TST_REV_17_search_responses_have_no_answer_field(self):
        """AC-REV-17 (R2): any search response is scanned: no field named answer / summary / recommendation (also none of the generation-like names)."""
        st = self.search_store()
        names = ("answer", "summary", "recommend", "suggest", "generated", "completion", "conclusion")
        bad = []

        def walk(o, w):
            if isinstance(o, dict):
                for k, v in o.items():
                    if any(n in k.lower() for n in names):
                        bad.append((w, k))
                    walk(v, w + "/" + k)
            elif isinstance(o, list):
                for v in o:
                    walk(v, w)
        for q in ("ignore", "%22batch%20genealogy%22", "locale:de-DE%20batch", "nomatchatall"):
            r = st.get("/api/v2/search?q=" + q, "ql")
            self.assertEqual(r.status, 200, (q, r.text[:200]))
            walk(r.json(), q)
        bad_q = st.get("/api/v2/search?q=nofield:value", "ql")
        self.assertEqual((bad_q.status, bad_q.code), (422, "E-REV-QUERY-INVALID"))
        self.assertEqual(bad, [])

    def test_TST_REV_19_queue_and_search_latency_is_recorded(self):
        """AC-REV-19: the queue and search endpoints under the 125-case baseline, 200 calls each -> p50 and p95 are recorded in a report (measure-only: no
        pass/fail threshold on the numbers; the label says so)."""
        import time
        provider = W.corpus_provider() or (lambda: [])
        st = self.store(extra={"search": {"enabled": True}}, app_kw={"documents": provider})
        self.queue_fixture(st)
        report = {"label": "synthetic, unvalidated; measure-only, no threshold (PNFR-06)", "baseline_cases": st.count("case_state") - 0, "calls": 200}
        for name, path in (("queue", "/api/v2/queues/exceptions"), ("search", "/api/v2/search?q=batch%20genealogy")):
            ms = []
            for _ in range(200):
                t0 = time.perf_counter()
                r = st.get(path, "ql")
                ms.append((time.perf_counter() - t0) * 1000.0)
                self.assertEqual(r.status, 200, r.text[:200])
            ms.sort()
            report[name] = {"p50_ms": round(ms[99], 3), "p95_ms": round(ms[189], 3), "max_ms": round(ms[-1], 3)}
            self.assertLessEqual(report[name]["p50_ms"], report[name]["p95_ms"])
        self.assertGreaterEqual(report["baseline_cases"], 125)
        out = os.path.join(S.tmpdir("rev19-"), "latency-report.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, sort_keys=True, indent=1)
        print("REV-19 latency report:", json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
