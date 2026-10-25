"""Stage 31 tests, part 2: SLO candidates, error-budget arithmetic, burn rates, alert rules, the zero-model-call tripwire. Synthetic, unvalidated.

  S01  error-budget arithmetic: NO_DATA is not 100 %, states by remaining budget, zero-budget targets, low volume flag, invalid input refused
  S02  burn rate and the two-window verdict
  S03  SLO catalogue: every SLO is a CANDIDATE with a basis and no SLA; the SLI counts come from the measured reports and samples
  A01  alert-rule quality: owner, action, runbook anchor in the runbook, closed rule types, SEV scale, no duplicate ids
  A02  evaluator semantics: gt / delta / ratio / state / slo rules, absent metric = no_data (tripwires: sensor_absent fires), deterministic
  A03  the zero-model-call tripwire is observable end to end: store samples -> ALT-01 / ALT-02 -> report; pulsed and put back
  A04  report: lint findings raise ALT-12, an SLO with no SLI source is NO_DATA, never met; exit semantics via the CLI are in test part 3
"""
import re
import unittest

import _inc08 as W
import _stg31 as T
import _support as S
from hub.obs import alerts, catalog, collect, report, slo
from hub.web import nfr


def setUpModule():
    T.skip_in_inner_egress_run()


class TST_HUB_STG31_Slo(unittest.TestCase):

    def test_TST_HUB_STG31_S01_error_budget_arithmetic(self):
        """S01: 99.5 % of 1000 allows 5 bad; the state follows the remaining budget; no events = NO_DATA; a 100 % target has no budget."""
        s = slo.by_id("SLO-01")
        r = slo.evaluate(s, 998, 1000)
        self.assertEqual((r["sli_pct"], r["allowed_bad"], r["budget_remaining_pct"], r["state"]), ("99.80", "5.00", "60.00", "GREEN"))
        self.assertEqual(slo.evaluate(s, 996, 1000)["state"], "AMBER")      # 4 of 5 used -> 20 % left
        self.assertEqual(slo.evaluate(s, 995, 1000)["state"], "EXHAUSTED")   # 5 of 5 used -> 0 % left
        self.assertEqual(slo.evaluate(s, 990, 1000)["state"], "EXHAUSTED")
        self.assertEqual(slo.evaluate(s, 995, 1000)["budget_remaining_pct"], "0.00")
        r = slo.evaluate(s, 0, 0)
        self.assertEqual((r["state"], r["sli_pct"]), ("NO_DATA", None))
        self.assertEqual(slo.evaluate(s, 100, 100)["state"], "GREEN")
        red = slo.evaluate(slo.by_id("SLO-03"), 9993, 10000)               # budget 100, 7 used... still green; 95 used -> RED
        self.assertEqual(red["state"], "GREEN")
        self.assertEqual(slo.evaluate(slo.by_id("SLO-03"), 9905, 10000)["state"], "RED")
        zero = slo.by_id("SLO-04")
        self.assertEqual(slo.evaluate(zero, 30, 30)["state"], "GREEN")
        self.assertEqual(slo.evaluate(zero, 29, 30)["state"], "EXHAUSTED")
        self.assertTrue(slo.evaluate(s, 20, 20)["low_volume"])               # 0.1 allowed bad: one failure is the whole budget
        self.assertFalse(slo.evaluate(s, 998, 1000)["low_volume"])
        for g, t in ((2, 1), (-1, 5)):
            with self.assertRaises(ValueError):
                slo.evaluate(s, g, t)

    def test_TST_HUB_STG31_S02_burn_rates(self):
        """S02: burn 1.0 = on budget; a 100 % target has no burn rate; both windows must burn for BURNING; missing data is NO_DATA."""
        self.assertEqual(slo.burn_rate(5, 1000, "99.5"), "1.0")
        self.assertEqual(slo.burn_rate(72, 1000, "99.5"), "14.4")
        self.assertIsNone(slo.burn_rate(1, 100, "100"))
        self.assertIsNone(slo.burn_rate(0, 0, "99"))
        self.assertEqual(slo.burn_verdict("20.0", "15.0", 14.4), "BURNING")
        self.assertEqual(slo.burn_verdict("20.0", "3.0", 14.4), "OK")
        self.assertEqual(slo.burn_verdict(None, "15.0", 14.4), "NO_DATA")
        self.assertEqual([p[0] for p in slo.BURN_PAIRS], ["fast", "slow", "ticket"])

    def test_TST_HUB_STG31_S03_slo_catalogue_and_sli_sources(self):
        """S03: SLO ids are unique, every SLO is a CANDIDATE with a basis and no SLA, targets are plausible; the SLI counts match the measured reports."""
        ids = [s["id"] for s in slo.SLOS]
        self.assertEqual(len(ids), len(set(ids)))
        for s in slo.SLOS:
            self.assertEqual(s["status"], "CANDIDATE")
            self.assertTrue(s["sla"].startswith("none"))
            self.assertTrue(s["basis"] and s["source"])
            self.assertTrue(0 < float(s["target_pct"]) <= 100 and s["window_days"] > 0)
        self.assertEqual([s["id"] for s in slo.SLOS if not s["sli_available"]], ["SLO-04", "SLO-05"])
        rep = nfr.availability_report([(m, m not in (3, 4)) for m in range(10)], 10)
        self.assertEqual(slo.counts_availability(rep), (8, 10))
        tl = nfr.timeliness_report([{"run_id": "r%d" % i, "ended_local": "x", "deadline_local": "y", "finished_before_deadline": i != 2} for i in range(4)])
        self.assertEqual(slo.counts_timeliness(tl), (3, 4))
        samples = [T.sample("http_requests_total", value=90, op_id="OP-A", status="200"), T.sample("http_requests_total", value=7, op_id="OP-A", status="403"),
                   T.sample("http_requests_total", value=3, op_id="OP-B", status="503")]
        self.assertEqual(slo.counts_http(samples), (97, 100))
        self.assertEqual([i["id"] for i in slo.INVARIANTS], ["INV-01", "INV-02", "INV-03"])


class TST_HUB_STG31_Alerts(unittest.TestCase):

    def test_TST_HUB_STG31_A01_alert_rule_quality(self):
        """A01: every rule is actionable (owner + action + runbook anchor that exists), uses a closed type and the Stage 29 severity scale; ids unique."""
        runbook = open(T.DOCS + "/operational-runbook.md", encoding="utf-8").read()
        anchors = set(re.findall(r"^#{2,4} (RB-\d\d)\b", runbook, re.M))
        ids = [r["id"] for r in alerts.RULES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, sorted(ids))
        for r in alerts.RULES:
            for f in alerts.FIELDS:
                self.assertTrue(r.get(f), (r["id"], f))
            self.assertIn(r["severity"], ("SEV-A", "SEV-B", "SEV-C"))
            self.assertIn(r["type"], alerts._EVAL)
            self.assertIn(r["runbook"], anchors, r["id"])
            self.assertNotIn("FYI", r["action"])
            if r["type"] != "slo":
                self.assertIn(r["metric"], catalog.CATALOG, r["id"])
        self.assertEqual([r["id"] for r in alerts.RULES if r.get("absent_fires")], ["ALT-01", "ALT-02", "ALT-03"])
        self.assertEqual([r["id"] for r in alerts.RULES if r["severity"] == "SEV-A"], ["ALT-03", "ALT-04"])

    def test_TST_HUB_STG31_A02_evaluator_semantics(self):
        """A02: each rule type fires and clears on the right input; an absent metric is no_data (tripwires: sensor_absent fires); inputs untouched; repeatable."""
        zero = [T.sample(n, value=0) for n in ("model_calls_total", "egress_attempts_total", "zone_h_service_actor_accepted")]
        res = alerts.evaluate(zero)
        self.assertEqual(res["firing"], [])
        self.assertEqual(sorted(x["id"] for x in res["ok"]), ["ALT-01", "ALT-02", "ALT-03"])
        self.assertIn("ALT-04", [x["id"] for x in res["no_data"]])                       # gap metric: unknown, not fine
        absent = alerts.evaluate([])
        self.assertEqual([(x["id"], x["reason"]) for x in absent["firing"]], [("ALT-01", "sensor_absent"), ("ALT-02", "sensor_absent"), ("ALT-03", "sensor_absent")])
        # ratio: below min denominator = no_data; above threshold fires; below stays ok
        few = [T.sample("http_requests_total", value=5, op_id="OP-A", status="500")]
        self.assertIn("ALT-06", [x["id"] for x in alerts.evaluate(zero + few)["no_data"]])
        bad = [T.sample("http_requests_total", value=90, op_id="OP-A", status="200"), T.sample("http_requests_total", value=10, op_id="OP-A", status="502")]
        self.assertIn("ALT-06", [x["id"] for x in alerts.evaluate(zero + bad)["firing"]])
        good = [T.sample("http_requests_total", value=199, op_id="OP-A", status="200"), T.sample("http_requests_total", value=1, op_id="OP-A", status="500")]
        self.assertIn("ALT-06", [x["id"] for x in alerts.evaluate(zero + good)["ok"]])        # exactly 0.5 % <= 1 %
        # delta: needs the previous evaluation
        now = [T.sample("auth_failures_total", value=15, reason="bad_credentials"), T.sample("auth_failures_total", value=3, reason="locked")]
        before = [T.sample("auth_failures_total", value=2, reason="bad_credentials"), T.sample("auth_failures_total", value=0, reason="locked")]
        self.assertIn("ALT-07", [x["id"] for x in alerts.evaluate(zero + now)["no_data"]])
        self.assertIn("ALT-07", [x["id"] for x in alerts.evaluate(zero + now, before)["firing"]])      # +16 > 10
        self.assertIn("ALT-07", [x["id"] for x in alerts.evaluate(zero + now, now)["ok"]])
        # state_eq: breaker open
        self.assertIn("ALT-10", [x["id"] for x in alerts.evaluate(zero + [T.sample("resilience_breaker_state", "gauge", 1, dependency="g")])["firing"]])
        self.assertIn("ALT-10", [x["id"] for x in alerts.evaluate(zero + [T.sample("resilience_breaker_state", "gauge", 0, dependency="g")])["ok"]])
        # slo rule
        self.assertIn("ALT-13", [x["id"] for x in alerts.evaluate(zero, slo_states={"SLO-01": "RED", "SLO-02": "GREEN"})["firing"]])
        self.assertIn("ALT-13", [x["id"] for x in alerts.evaluate(zero, slo_states={"SLO-01": "AMBER"})["ok"]])
        # inputs untouched, deterministic
        import copy
        snap = copy.deepcopy(zero + now)
        a, b = alerts.evaluate(zero + now, before), alerts.evaluate(zero + now, before)
        self.assertEqual(a, b)
        self.assertEqual(snap, zero + now)

    def test_TST_HUB_STG31_A03_zero_model_call_tripwire_is_observable(self):
        """A03: the store exports the three tripwires; a pulsed model call / egress attempt fires ALT-01 / ALT-02 through the report; the counters are put back."""
        st = W.WStore()
        try:
            clean = collect.samples(st.con)
            with T.tripwire_pulse("model_calls_total"):
                pulsed_model = collect.samples(st.con)
            with T.tripwire_pulse("egress_attempts_total"):
                pulsed_egress = collect.samples(st.con)
            after = collect.samples(st.con)
        finally:
            st.close()
        fire = lambda smp: sorted(x["id"] for x in report.evaluate(smp)["alerts"]["firing"])  # noqa: E731
        self.assertEqual(fire(clean), [])
        self.assertEqual(fire(pulsed_model), ["ALT-01"])
        self.assertEqual(fire(pulsed_egress), ["ALT-02"])
        self.assertEqual(fire(after), [])
        self.assertEqual(report.evaluate(pulsed_model)["tripwires"]["model_calls_total"], "1")
        self.assertEqual(report.evaluate(after)["tripwires"], {"egress_attempts_total": "0", "model_calls_total": "0", "zone_h_service_actor_accepted": "0"})
        # the sensor is real: record_model_call is the function a future model client must call (OD-08); it moves the counter the alert reads
        from hub.obs import metrics as tm
        tm.record_model_call("test")
        try:
            self.assertEqual(tm.tripwires()["model_calls_total"], 1)
            with self.assertRaises(Exception):
                tm.check_tripwires()
        finally:
            tm.inc("model_calls_total", -1)
        self.assertEqual(tm.tripwires(), {"model_calls_total": 0, "egress_attempts_total": 0})

    def test_TST_HUB_STG31_A04_report_lint_slo_no_data(self):
        """A04: a leaky sample raises ALT-12 (and the report does not echo it); SLOs without an SLI source are NO_DATA with a reason; supplied reports feed SLO-01 / SLO-02."""
        zero = [T.sample(n, value=0) for n in ("model_calls_total", "egress_attempts_total", "zone_h_service_actor_accepted")]
        leak = T.sample("search_engine", "gauge", 1, engine="x" * 64 + "")
        leak["labels"]["engine"] = "0123456789abcdef" * 4
        res = report.evaluate(zero + [leak])
        self.assertIn("ALT-12", [x["id"] for x in res["alerts"]["firing"]])
        self.assertNotIn("0123456789abcdef", repr(res))
        rows = dict((r["slo"], r) for r in res["slo"])
        self.assertEqual(rows["SLO-04"]["state"], "NO_DATA")
        self.assertIn("GAP", rows["SLO-04"]["reason"])
        self.assertEqual(rows["SLO-01"]["state"], "NO_DATA")
        av = nfr.availability_report([(m, True) for m in range(1000)], 1000)
        res2 = report.evaluate(zero, availability=av)
        self.assertEqual(dict((r["slo"], r) for r in res2["slo"])["SLO-01"]["state"], "GREEN")
        self.assertIn("no SLA", res2["claim"])
        self.assertEqual(res2["label"], T.LABEL)


if __name__ == "__main__":
    unittest.main()
