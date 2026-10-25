"""Stage 31 tests, part 1: metric catalogue, telemetry lint, exposition, resilience samples. Synthetic, unvalidated.

  C01  every sample the store and the HTTP layer export today is in the catalogue and lints clean
  C02  the lint refuses unknown metrics, kinds, label names, label values, values, prohibited content and runaway cardinality - and never echoes them
  C03  text exposition: deterministic, escaped, histograms expanded
  C04  resilience samples from the Stage 28 primitives: values, closed dependency label, lint clean, nothing changed by reading
  C05  the catalogue covers every metric named in observability-spec OBS-4 and the implemented ones are really exported
"""
import json
import re
import unittest

import _inc08 as W
import _stg31 as T
import _support as S
from hub.obs import catalog, collect, expo, resilience_samples
from hub.resilience import guarded, policy
from hub.web.obs_http import HttpMetrics


def setUpModule():
    T.skip_in_inner_egress_run()


class TST_HUB_STG31_Catalog(unittest.TestCase):

    def test_TST_HUB_STG31_C01_exported_samples_are_catalogued_and_clean(self):
        """C01: collect.samples + run_end_samples + HttpMetrics.samples (with a request mix) -> every name is in the catalogue as `implemented`, lint finds nothing."""
        st = W.WStore()
        try:
            hm = HttpMetrics()
            for op, status, ms in (("OP-A", 200, 3.5), ("OP-A", 500, 9.0), ("OP-B", 403, 1.0)):
                hm.request(op, status, ms)
            for r in ("bad_credentials", "rate_limited", "locked"):
                hm.auth_failure(r)
            allv = collect.samples(st.con) + collect.run_end_samples(st.con, "reconcile", 12.5, 0) + hm.samples(st.con)
        finally:
            st.close()
        names = sorted(set(s["name"] for s in allv))
        self.assertGreaterEqual(len(names), 10)
        for n in names:
            self.assertEqual(catalog.CATALOG[n]["source"], catalog.IMPLEMENTED, n)
        self.assertEqual(catalog.lint_samples(allv), [])
        for t in ("model_calls_total", "egress_attempts_total", "zone_h_service_actor_accepted"):
            self.assertIn(t, names)
        T.write_evidence("c01-exported-metric-names.json", {"names": names, "label": T.LABEL})

    def test_TST_HUB_STG31_C02_lint_refuses_and_never_echoes(self):
        """C02: each defect class is reported by position and kind; the injected text is not in the report."""
        leak_probe = "hunter2-" + "a" * 64
        inj = "<script>alert(1)</script>"
        bad = [T.sample("nope_total"),                                                   # 0 unknown metric
               T.sample("model_calls_total", "gauge", 0),                                # 1 wrong kind
               T.sample("model_calls_total", "counter", 0, extra="x"),                   # 2 label not in the closed set
               T.sample("auth_failures_total", "counter", 1, reason=inj),                # 3 label value not identifier-shaped
               T.sample("auth_failures_total", "counter", "seven", reason="locked"),     # 4 value not a number
               T.sample("run_duration_seconds", "histogram", "{\"notes\": 1}", job="j"),  # 5 histogram with a key outside the closed shape
               T.sample("search_engine", "gauge", 1, engine=leak_probe),                     # 6 64-hex digest as label value (also not identifier-shaped? it is) -> prohibited
               {"name": "http_requests_total", "kind": "counter", "labels": "x", "value": "1"}]  # 7 labels not an object
        res = catalog.lint_samples(bad)
        got = sorted(set((f["index"], f["problem"]) for f in res))
        for want in ((0, "unknown_metric"), (1, "bad_kind"), (2, "unknown_label"), (3, "bad_label_value"), (4, "bad_value"), (5, "bad_value"),
                     (6, "prohibited_content"), (7, "bad_labels")):
            self.assertIn(want, got)
        blob = json.dumps(res)
        self.assertNotIn("script", blob)
        self.assertNotIn("hunter2", blob)
        many = [T.sample("auth_failures_total", "counter", 1, reason="r%d" % i) for i in range(catalog.MAX_SERIES_PER_METRIC + 1)]
        self.assertIn("cardinality", [f["problem"] for f in catalog.lint_samples(many)])
        self.assertEqual(catalog.lint_samples([]), [])
        clean = T.sample("run_duration_seconds", "histogram", json.dumps({"count": 2, "max_s": 3, "sum_s": 4.5}), job="reconcile")
        self.assertEqual(catalog.lint_samples([clean]), [])

    def test_TST_HUB_STG31_C03_text_exposition(self):
        """C03: counters / gauges / histograms render; label values are escaped; order is independent of input order; empty -> empty text."""
        a = T.sample("http_requests_total", "counter", 4, op_id="OP-A", status="200")
        b = T.sample("http_request_duration_ms", "histogram", json.dumps({"count": 4, "max_ms": 9.5, "sum_ms": 20.25}), op_id="OP-A")
        c = T.sample("quarantine_depth", "gauge", 3, queue="quarantine_invalid")
        t1, t2 = expo.render([a, b, c]), expo.render([c, b, a])
        self.assertEqual(t1, t2)
        self.assertIn('http_requests_total{op_id="OP-A",status="200"} 4', t1)
        self.assertIn('http_request_duration_ms_count{op_id="OP-A"} 4', t1)
        self.assertIn('http_request_duration_ms_sum{op_id="OP-A"} 20.25', t1)
        self.assertIn("# TYPE quarantine_depth gauge", t1)
        self.assertEqual(expo.render([]), "")
        esc = expo.render([T.sample("search_engine", "gauge", 1, engine='a"b\nc')])   # not lint-clean on purpose: the renderer must still not break the format
        self.assertIn('engine="a\\"b\\nc"', esc)
        self.assertEqual(len([l for l in esc.splitlines() if not l.startswith("#")]), 1)

    def test_TST_HUB_STG31_C04_resilience_samples(self):
        """C04: a breaker that tripped, a budget that refused, a bulkhead that shed -> the catalogue samples carry those counts; reading changes nothing."""
        clock = [100.0]
        br = policy.Breaker(2, 60, lambda: clock[0])
        br.record_failure()
        br.record_failure()
        self.assertFalse(br.allow()[0])
        bu = policy.RetryBudget(20, 1)
        self.assertTrue(bu.withdraw())
        self.assertFalse(bu.withdraw())
        bh = policy.Bulkhead(1)
        self.assertTrue(bh.try_enter())
        self.assertFalse(bh.try_enter())
        before = (br.snapshot(), bu.tokens, bu.retries_denied, bh.rejected)
        s = resilience_samples.samples("gateway-a", breaker=br, budget=bu, bulkhead=bh)
        self.assertEqual(before, (br.snapshot(), bu.tokens, bu.retries_denied, bh.rejected))
        v = dict((x["name"], x["value"]) for x in s)
        self.assertEqual((v["resilience_breaker_state"], v["resilience_breaker_opened_total"], v["resilience_breaker_rejected_total"]), ("1", "1", "1"))
        self.assertEqual((v["resilience_retries_granted_total"], v["resilience_retries_denied_total"], v["resilience_bulkhead_rejected_total"]), ("1", "1", "1"))
        self.assertEqual(v["resilience_bulkhead_in_flight"], "1")
        self.assertEqual(catalog.lint_samples(s), [])
        clock[0] += 61
        self.assertEqual(dict((x["name"], x["value"]) for x in resilience_samples.samples("gateway-a", breaker=br))["resilience_breaker_state"], "2")
        for bad in ("http://127.0.0.1:1/x", "a b", "", None, "x" * 81):
            with self.assertRaises(ValueError):
                resilience_samples.samples(bad, breaker=br)
        # through the real guarded gateway with a stub fetch that always fails: calls / attempts are counted, retries are bounded by the budget
        from hub.intake.errors import SourceUnreachable

        def fetch(url, offset, limit, retries=0, timeout=5):
            raise SourceUnreachable({"last_error": "http_500"})
        g = guarded.GuardedGateway("http://127.0.0.1:9/", lambda: 0.0, lambda s: None, {"retry": {"max_retries": 2}}, fetch=fetch)
        for _ in range(2):
            with self.assertRaises(SourceUnreachable):
                g.fetch_events()
        gs = resilience_samples.samples("gateway-a", gateway=g)
        v = dict((x["name"], x["value"]) for x in gs)
        self.assertEqual((v["resilience_calls_total"], v["resilience_attempts_total"]), ("2", "6"))
        self.assertEqual(catalog.lint_samples(gs), [])

    def test_TST_HUB_STG31_C05_catalogue_covers_the_spec(self):
        """C05: every metric in observability-spec OBS-4 is in the catalogue (implemented or an explicit GAP); every IMPLEMENTED name appears in the source of collect / obs_http."""
        spec = open(S.CODE_ROOT + "/docs/12-specs/observability-spec.md", encoding="utf-8").read()
        sect = spec.split("### OBS-4")[1].split("### OBS-5")[0]
        named = set(re.findall(r"^\| `([a-z0-9_]+)`", sect, re.M))
        self.assertGreaterEqual(len(named), 22)
        self.assertEqual(sorted(named - set(catalog.CATALOG)), [])
        src = open(S.CODE_ROOT + "/hub/obs/collect.py", encoding="utf-8").read() + open(S.CODE_ROOT + "/hub/web/obs_http.py", encoding="utf-8").read()
        for n in catalog.names(catalog.IMPLEMENTED):
            self.assertIn(n, src, n)
        for n in catalog.names(catalog.GAP):
            self.assertNotIn('"%s"' % n, src, "gap metric %s is exported - move it to implemented" % n)


if __name__ == "__main__":
    unittest.main()
