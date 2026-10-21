"""Stage 21 integration evidence tests (DI-05: DW-10, DW-11, DW-12; Stage 21 Required Analysis 1-7). Synthetic, unvalidated.

No hub behaviour, binding, legacy path or working-tree file is changed: the tests read the shipped sources through the existing adapters, ingest
them into private sandbox stores under the shipped default binding (record_only), and run the repo's own source-gateway stub on loopback.

  S01  DW-10 source-contract pack: source-contract-v1 over the 4 shipped sources = committed evidence; equals the Stage 16 observation
  S02  shipped gateway stub (services/source_gateway, unchanged) through the AD-04 client: paging, clamp, empty page, stale re-pull = NOOP
  S03  failure semantics of the stub's own failure responses (503 / 429 retried with back-off; shape error bounded; 400 not retried);
       GET only, no credentials sent
  S04  timeout: a loopback source that accepts and never answers -> bounded retries -> E-INT-SOURCE-UNREACHABLE, no item
  S05  DW-11 legacy-output consumer scan (LO-01..LO-13) = committed evidence (frozen legacy part)
  S06  DW-12 read-only re-proof: every FX-BASE125 file byte-identical after S01-S05; adapters open nothing for writing
  S07  late / out-of-order delivery (RTD-61 characterised): a delivery that appears later with an order key before the job checkpoint is
       not seen by a resumed job; the idempotent catch-up ingest stores exactly that item; shipped partner rows with source_ts > ingest_ts
"""
import ast
import inspect
import json
import os
import threading
import unittest

import _inc06 as I
import _stg21 as T
import _support as S
from hub.adapters import gateway_client, intake_sources
from hub.intake import contracts
from hub.intake import errors as E
from hub.intake.profiles import PROFILES

OBS16 = os.path.join(S.CODE_ROOT, "docs", "16-repo-validation", "evidence", "obs-laptop.json")
_BEFORE = {}


def setUpModule():
    T.skip_in_inner_egress_run()
    _BEFORE["tree"] = T.tree_digest(S.LEGACY_ROOT)


class _Replay(object):
    """Loopback double that replays recorded (status, body bytes) responses at /api/events and records each request line and headers."""

    def __init__(self, plan):
        import http.server
        outer = self
        self.plan, self.hits, self.headers, self.methods = list(plan), [], [], []

        class H_(http.server.BaseHTTPRequestHandler):
            def _any(self):
                outer.hits.append(self.path)
                outer.methods.append(self.command)
                outer.headers.append(dict((k.lower(), v) for k, v in self.headers.items()))
                status, body = outer.plan[min(len(outer.hits), len(outer.plan)) - 1]
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            do_GET = do_POST = do_PUT = do_DELETE = _any

            def log_message(self, *a):
                pass
        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H_)
        self.url = "http://127.0.0.1:%d" % self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.t.start()

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


class TST_HUB_STG21_Integration(unittest.TestCase):
    maxDiff = 4000

    def _committed_equal(self, name, doc, path):
        exp = T.committed(name)
        self.assertIsNotNone(exp, "no committed %s; generated evidence at %s" % (name, path))
        self.assertEqual(doc, exp, "%s differs from the committed evidence; regenerated at %s" % (name, path))

    def test_TST_HUB_STG21_S01_source_contract_pack(self):
        """S01 (DW-10, OD-S12-11 decision support): source-contract-v1 (bundled = integration/ copy) over the shipped sources -> partner_feed 0/8,567,
        source_message 15/15, gateway inbox 0/1, vendor_csv 0/2,400 pass; the stores' record_only contract_check equals the static check;
        enforce would quarantine 8,500 partner items (67 replays stay NOOP); per-source outcome digests equal the Stage 16 laptop observation."""
        pack = T.contract_pack(I.IStore())
        path = T.write_evidence("contract-pack.json", pack)
        st, sto = pack["static"], pack["store"]
        self.assertTrue(pack["contract"]["byte_identical"])
        self.assertEqual(dict((k, (st[k]["pass"], st[k]["fail"])) for k in T.SOURCES),
                         {"partner_feed": (0, 8567), "source_message": (15, 0), "gateway": (0, 1), "vendor_csv": (0, 2400)})
        for src in T.SOURCES:
            self.assertEqual((sto[src]["binding"], sto[src]["binding_origin"]), ("record_only", "default"), src)
            self.assertEqual(sto[src]["contract_check"], dict((k, st[src][k]) for k in ("fail", "pass") if st[src][k]), src)
            self.assertNotIn("CONTRACT_VIOLATION", json.dumps(sto[src]["outcomes"]))
        pf = sto["partner_feed"]
        self.assertEqual(pf["enforce_would_keep_noop_duplicate"], 67)
        self.assertEqual(sum(n for o, n in pf["contract_fail_current_outcomes"].items() if o != "NOOP_DUPLICATE"), 8500)
        with open(OBS16, encoding="utf-8") as f:
            runs16 = json.load(f)["ingest"]["runs"]
        self.assertEqual(dict((k, sto[k]["outcomes_digest"]) for k in T.SOURCES), dict((k, runs16[k]["outcomes_digest"]) for k in T.SOURCES))
        self.assertEqual(dict((k, sto[k]["outcomes"]) for k in T.SOURCES), dict((k, runs16[k]["outcomes"]) for k in T.SOURCES))
        self._committed_equal("contract-pack.json", pack, path)

    def test_TST_HUB_STG21_S02_shipped_gateway_stub_conformance(self):
        """S02 (AD-04 vs the shipped stub, analysis 1/3/6): catalog = integration/source-gateway.json; pages of 50 -> 50/50/25/0 with
        next_offset = offset + len(items); limit 500 is clamped by the stub and the client follows next_offset; an empty page keeps the
        checkpoint; a stale re-pull from offset 0 is stored and becomes NOOP_DUPLICATE (totals unchanged); contract profile of live events."""
        stub = T.GatewayStub()
        try:
            code, body = T.get_json(stub.url + "/api/catalog")
            with open(os.path.join(S.CODE_ROOT, "integration", "source-gateway.json"), encoding="utf-8") as f:
                self.assertEqual((code, json.loads(body)), (200, json.load(f)))
            pages, off = [], 0
            while True:
                pg = gateway_client.fetch_events(stub.url, off, 50, retries=0)
                self.assertEqual((pg["next_offset"], pg["attempts"]), (off + len(pg["items"]), 1))
                pages.append({"offset": off, "items": pg["items"], "next_offset": pg["next_offset"]})
                if not pg["items"]:
                    break
                off = pg["next_offset"]
            self.assertEqual([len(p["items"]) for p in pages], [50, 50, 25, 0])
            items = [e for p in pages for e in p["items"]]
            big = gateway_client.fetch_events(stub.url, 0, 500, retries=0)
            self.assertEqual((len(big["items"]), big["next_offset"]), (125, 125))
            self.assertEqual(big["items"], items)
            fail = {}
            for mode in ("timeout", "schema", "rate_limit"):
                c, b = T.get_json(stub.url + "/api/failure?mode=" + mode)
                fail[mode] = {"status": c, "body": json.loads(b)}
            c, b = T.get_json(stub.url + "/api/events?offset=x")
            fail["bad_pagination"] = {"status": c, "body": json.loads(b)}
        finally:
            stub.close()
        keys = sorted(set(k for e in items for k in e))
        self.assertEqual(keys, ["business_key", "event_type", "message_id", "occurred_at", "payload", "published_at", "schema_version", "system"])
        self.assertEqual(len(set(e["message_id"] for e in items)), 125)
        contract = contracts.load("source-contract-v1")
        prof = T.static_contract_profile(contract, intake_sources.gateway_event_deliveries(items), PROFILES["gateway"])
        self.assertEqual((prof["pass"], prof["fail"], prof["fail_signatures"]), (0, 125, {"ref,status": 125}))
        store = I.IStore()
        reps = []
        for i, p in enumerate(pages):
            reps.append(store.isvc.ingest("gateway", intake_sources.gateway_event_deliveries(p["items"]), "s21-gw-%d" % i, "s21-gw",
                                          checkpoint={"next_offset": p["next_offset"], "attempts": 1}))
        self.assertEqual(store.isvc.last_checkpoint("gateway"), {"next_offset": 125, "attempts": 1})
        snap1 = store.isvc.queue_snapshot(store.isvc.clock())
        replay = store.isvc.ingest("gateway", intake_sources.gateway_event_deliveries(items), "s21-gw-stale", "s21-gw")
        snap2 = store.isvc.queue_snapshot(store.isvc.clock())
        self.assertEqual((replay["stored"], replay["noop_duplicate"], replay["outcomes"]), (125, 125, {"NOOP_DUPLICATE": 125}))
        self.assertEqual((snap1["totals"], snap1["total_items"]), (snap2["totals"], snap2["total_items"]))
        self.assertEqual(snap1["total_items"], 125)
        outcomes = {}
        for r in reps:
            for k, n in r["outcomes"].items():
                outcomes[k] = outcomes.get(k, 0) + n
        ev = {"schema": "s21-gateway-stub/v1", "label": T.LABEL, "stage": "21", "work_items": ["DW-10", "DW-12"],
              "stub": "services/source_gateway/server.py (unchanged, run from the sandbox copy on a free loopback port, LEGACY_DB = scratch copy)",
              "pages_limit_50": [len(p["items"]) for p in pages], "events": len(items), "event_keys": keys,
              "schema_version_counts": dict(sorted((v, sum(1 for e in items if e["schema_version"] == v)) for v in set(e["schema_version"] for e in items))),
              "systems": sorted(set(e["system"] for e in items)), "event_types": sorted(set(e["event_type"] for e in items)),
              "occurred_after_published": sum(1 for e in items if e["occurred_at"] > e["published_at"]),
              "contract_source_contract_v1": {"pass": prof["pass"], "fail": prof["fail"], "fail_signatures": prof["fail_signatures"]},
              "hub_outcomes_first_pull": dict(sorted(outcomes.items())), "stale_repull": {"stored": replay["stored"], "outcomes": replay["outcomes"]},
              "checkpoint_after": store.isvc.last_checkpoint("gateway"), "limit_500": {"items": len(big["items"]), "next_offset": big["next_offset"]},
              "failure_endpoints": fail,
              "reproduce": "python3 -B tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s21-stub --label stub -k TST_HUB_STG21_S02"}
        path = T.write_evidence("gateway-stub-conformance.json", ev)
        self._committed_equal("gateway-stub-conformance.json", ev, path)

    def test_TST_HUB_STG21_S03_stub_failure_responses_through_the_client(self):
        """S03 (analysis 3/7): the stub's own failure responses replayed at /api/events: 503 then 429 then a page -> 3 attempts, back-off
        [0.5, 1.0]; the 'schema' body (200, unexpected shape) is a run error after the bounded retries; 400 is not retried; every request
        is a GET without Authorization / Cookie / body; the client source has no write verb or request body (GET only, idempotent)."""
        rec = T.committed("gateway-stub-conformance.json")
        self.assertIsNotNone(rec, "S02 evidence not committed")
        f = rec["failure_endpoints"]
        self.assertEqual((f["timeout"]["status"], f["rate_limit"]["status"], f["schema"]["status"], f["bad_pagination"]["status"]), (503, 429, 200, 400))
        body = lambda k: json.dumps(f[k]["body"]).encode()
        page = json.dumps({"items": [], "count": 0, "next_offset": 7}).encode()
        sleeps = []
        g = _Replay([(503, body("timeout")), (429, body("rate_limit")), (200, page)])
        try:
            got = gateway_client.fetch_events(g.url, 7, 50, retries=3, sleep=sleeps.append, backoff=0.5)
            self.assertEqual((got["attempts"], got["next_offset"], sleeps), (3, 7, [0.5, 1.0]))
            self.assertEqual(set(g.methods), {"GET"})
            self.assertEqual(g.hits, ["/api/events?offset=7&limit=50"] * 3)
            for h in g.headers:
                self.assertFalse(set(h) & {"authorization", "cookie", "proxy-authorization", "content-length"}, h)
        finally:
            g.close()
        for plan, retries, attempts, last in (([(200, body("schema"))], 2, 3, "ValueError"), ([(400, body("bad_pagination"))], 3, 1, "http_400"),
                                              ([(503, body("timeout"))], 2, 3, "http_503")):
            g = _Replay(plan)
            try:
                with self.assertRaises(E.SourceUnreachable) as cm:
                    gateway_client.fetch_events(g.url, retries=retries, sleep=lambda s: None)
                self.assertEqual((cm.exception.details["attempts"], cm.exception.details["last_error"], len(g.hits)), (attempts, last, attempts))
            finally:
                g.close()
        src = inspect.getsource(gateway_client)
        tree = ast.parse(src)
        kws = [k.arg for n in ast.walk(tree) if isinstance(n, ast.Call) for k in n.keywords]
        self.assertNotIn("data", kws)
        self.assertNotIn("method", kws)
        self.assertFalse([n for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr in ("Request", "urlopen", "post", "put")])

    def test_TST_HUB_STG21_S04_timeout_is_bounded_and_fabricates_nothing(self):
        """S04 (analysis 5/7): a loopback source that accepts and never answers -> each attempt ends at the timeout, retries are bounded,
        E-INT-SOURCE-UNREACHABLE carries attempts / last_error; the run is a failed run with no item; shipped defaults timeout 5 s, retries 3."""
        sig = inspect.signature(gateway_client.fetch_events).parameters
        self.assertEqual((sig["timeout"].default, sig["retries"].default, sig["backoff"].default), (5, 3, 0.5))
        hs = T.hanging_server()
        sleeps = []
        try:
            with self.assertRaises(E.SourceUnreachable) as cm:
                gateway_client.fetch_events(hs.url, 0, 50, retries=1, timeout=0.3, sleep=sleeps.append, backoff=0.1)
        finally:
            hs.close()
        d = cm.exception.details
        self.assertEqual((d["attempts"], d["retries"], sleeps), (2, 1, [0.1]))
        self.assertIn(d["last_error"], ("TimeoutError", "timeout"))
        self.assertEqual(len(hs.received), 2)
        self.assertTrue(all(r.startswith(b"GET /api/events?offset=0&limit=50 ") for r in hs.received), hs.received)
        store = I.IStore()
        rep = store.isvc.fail_run("gateway", "s21-timeout", "SOURCE_UNREACHABLE", d, "s21")
        self.assertEqual((rep["status"], store.isvc.counts()["raw"], store.isvc.counts()["outcomes"]), ("failed", 0, 0))
        self.assertIsNone(store.isvc.last_checkpoint("gateway"))

    def test_TST_HUB_STG21_S05_legacy_output_consumer_scan(self):
        """S05 (DW-11, DQ-15 / U-14-01): every CUT-2..CUT-4 legacy output LO-01..LO-13 has a row; the readers found under the frozen legacy
        paths equal the committed scan (hub / harness readers are reported, not pinned); no legacy CI job reads a month-end / night-shift output."""
        scan = T.consumer_scan(S.CODE_ROOT)
        path = T.write_evidence("consumer-scan.json", scan)
        self.assertEqual([o["id"] for o in scan["outputs"]], ["LO-%02d" % i for i in range(1, 14)])
        by = dict((o["id"], o) for o in scan["outputs"])
        for lo in ("LO-09", "LO-10", "LO-11"):
            self.assertEqual(by[lo]["legacy_ci_readers"], [], lo)
        exp = T.committed("consumer-scan.json")
        self.assertIsNotNone(exp, "no committed consumer-scan.json; generated at %s" % path)
        self.assertEqual(T.frozen_view(scan), T.frozen_view(exp), "frozen part differs; regenerated at %s" % path)

    def test_TST_HUB_STG21_S06_read_only_re_proof(self):
        """S06 (DW-12): after S01-S05 (full shadow intake of 4 sources, stub runs on a scratch copy) every file of the FX-BASE125 copy is
        byte-identical; legacy.sqlite3 still has the OD-09 hash; hub/adapters open files only for reading and connect to SQLite in one place."""
        by, sha = I.legacy_deliveries()
        rows, _ = intake_sources.vendor_csv_deliveries(intake_sources.csv_path(S.LEGACY_ROOT, "tiny"))
        self.assertEqual((len(by["partner_feed"]), len(by["source_message"]), len(by["gateway"]), len(rows)), (8567, 15, 1, 2400))
        self.assertEqual(T.tree_digest(S.LEGACY_ROOT), _BEFORE["tree"])
        self.assertTrue(sha.startswith("c254649f"))
        adir = os.path.join(S.CODE_ROOT, "hub", "adapters")
        connects, bad_opens = [], []
        for fn in sorted(os.listdir(adir)):
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(adir, fn), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for n in ast.walk(tree):
                if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "open":
                    mode = n.args[1] if len(n.args) > 1 else next((k.value for k in n.keywords if k.arg == "mode"), None)
                    m = mode.value if isinstance(mode, ast.Constant) else ("r" if mode is None else "?")
                    if set(m) & set("wax+?"):
                        bad_opens.append((fn, n.lineno, m))
                if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "connect":
                    connects.append(fn)
        self.assertEqual(bad_opens, [])
        self.assertEqual(connects, ["legacy_sqlite.py"])

    def test_TST_HUB_STG21_S07_late_delivery_before_checkpoint(self):
        """S07 (analysis 6, RTD-61 characterised, no behaviour change): OrderedSource orders by (source_ts, source_key, n); a delivery that
        arrives after a checkpoint with an EARLIER source_ts is not returned by items_after(checkpoint) - a resumed job does not see it; the
        idempotent catch-up path (ingest with idempotent_backfill, as `hub.intake ingest-legacy`) stores exactly that one item. 2,234 of the
        8,567 shipped partner rows have source_ts later than ingest_ts (Stage 5 IL-05), so source order and delivery order differ."""
        from hub.runs.sources import OrderedSource
        a, b = I.feed(10), I.feed(20)
        late = I.feed(5, source_key="FEED-LATE-000005")
        ckpt = OrderedSource("partner_feed", [a, b]).items[-1][0]
        later = OrderedSource("partner_feed", [a, b, late])
        self.assertEqual(later.items_after(ckpt), [])
        self.assertEqual([d["source_key"] for _, d in later.items_after(None)], ["FEED-LATE-000005", a["source_key"], b["source_key"]])
        st = I.IStore()
        first = st.isvc.ingest("partner_feed", [a, b], "s21-late-1", "s21")
        rep = st.isvc.ingest("partner_feed", [a, b, late], "s21-late-catchup", "s21", idempotent_backfill=True)
        self.assertEqual((first["stored"], rep["stored"], rep["skipped_existing"], rep["noop_duplicate"]), (2, 1, 2, 0))
        self.assertEqual(st.isvc.counts()["raw"], 3)
        by, _ = I.legacy_deliveries()
        self.assertEqual(sum(1 for d in by["partner_feed"] if d["raw"]["source_ts"] > d["raw"]["ingest_ts"]), 2234)


if __name__ == "__main__":
    unittest.main()
