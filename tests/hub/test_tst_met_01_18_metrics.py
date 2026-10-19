"""TST-MET-01, 03..11, 13..18 (F07 metrics with definition tags; INC-07). TST-MET-02, 12 and 21 need the HTTP / UI surface (INC-08); their service-level
equivalents are TST-HUB-INC07-S05 / S06. TST-MET-19 / 20 are R2 (INC-09). Every figure here is computed from synthetic or shipped-baseline rows and is
labelled 'synthetic, unvalidated'; no policy used is adopted, no verdict is produced.
"""
import datetime
import unittest
from unittest import mock

import _support as S
import _inc05 as D
import _inc06 as I
import _inc07 as R
from hub.metrics import values as V
from hub.metrics.errors import (MetCutoffRequired, MetDefinitionRequired, MetNotReproducible, MetSourceRefused, MetTagMix, MetTagRequired,
                                MetUnparsableInput)
from hub.metrics.registry import BUILTIN
from hub.metrics.sources import CASES_SQL, CasesAmountSource, RowsSource, case_sites
from hub.security.canonical import fmt, parse

CUTOFF = "2030-01-01T00:00:00.000000Z"
HOUR = datetime.timedelta(hours=1)


def setUpModule():
    R.skip_in_inner_egress_run()


def mv(tag, value, pol=None, metric="X", n=1, status="candidate"):
    return V.MetricValue(metric, 1, tag, pol or "%s@1" % tag, status, value, None if value is not None else "none", n, denominator="d%s" % tag, exclusions="e")


class _Base(unittest.TestCase):
    def setUp(self):
        self.stores, self.handles = [], []

    def tearDown(self):
        for st in self.stores:
            st.close()
        for h in self.handles:
            if hasattr(h, "close"):
                h.close()

    def store(self, *a, **kw):
        st = R.RStore(*a, **kw)
        self.stores.append(st)
        return st

    def legacy(self):
        h = D.legacy_handle("p7leg-")
        self.handles.append(h)
        return h

    def cycles(self, st, prefix, specs):
        """specs: [(ops_hours | None, evidence_hours | None)]; every case is received 100 days before the (advanced) test clock."""
        st.clock.advance(120 * 86400)
        base = parse(st.now()) - datetime.timedelta(days=100)
        ids, who = [], st.fresh("rev")
        for i, (ops, evid) in enumerate(specs):
            cid = "C%02d%06d" % (int(prefix), i)
            rec = fmt(base + i * HOUR)
            st.svc.create_case(who, cid, "OPEN", "synthetic case", rec, rec, "t-mk")
            facts = sorted([(h, t) for h, t in ((ops, "FACT_OPS_CLOSED"), (evid, "FACT_EVIDENCE_COMPLETE")) if h is not None])
            for h, t in facts:
                st.svc.record_fact(who, cid, t, occurred_at=fmt(base + i * HOUR + datetime.timedelta(hours=h)), correlation_id="t-cyc")
            ids.append(cid)
        return ids


class TST_MET_Metrics(_Base):

    def test_TST_MET_01_every_definition_dependent_metric_has_a_tag(self):
        """AC-MET-01: enumerate the registry: every metric of category time / money / age or mentioning closed / resolved / approved / cost / handling has a
        non-null tag; registering one without a tag fails E-MET-TAG-REQUIRED (nothing is stored)."""
        st = self.store(loaded=False)
        reg = st.met.registry
        self.assertEqual(sorted(reg.seed_builtin()), sorted(d["metric_id"] for d in BUILTIN))
        self.assertEqual(reg.seed_builtin(), [])  # idempotent
        tagged = [d for d in reg.list() if d["involves_definition"]]
        self.assertTrue(all(d["definition_tag"] for d in tagged))
        self.assertEqual(sorted(d["metric_id"] for d in tagged if d["category"] in ("time", "age")), ["MET-TTC-C-EVID", "MET-TTC-C-OPS"])
        base = {"metric_id": "MET-X", "name": "X", "category": "count", "window": "w", "denominator": "d", "exclusions": "e", "basis": "event_derived",
                "documentation": "doc"}
        before = len(reg.list(latest_only=False))
        for bad in (dict(base, category="time"), dict(base, category="age"), dict(base, name="Cases closed per week"),
                    dict(base, documentation="share of approved items"), dict(base, denominator="cost per handling hour"),
                    dict(base, category="money", name="Resolved value"), dict(base, category="time", definition_tag="  ")):
            with self.assertRaises(MetTagRequired) as cm:
                reg.register(bad)
            self.assertEqual(cm.exception.code, "E-MET-TAG-REQUIRED")
        self.assertEqual(len(reg.list(latest_only=False)), before)
        self.assertEqual(reg.register(base), 1)  # a plain count needs no tag
        self.assertEqual(reg.register(dict(base, category="time", definition_tag="D-OPS")), 2)

    def test_TST_MET_03_mixing_tags_is_refused(self):
        """AC-MET-03: one D-OPS and one D-EVID figure -> combine(sum) and compare raise E-MET-TAG-MIX; two policy versions of one tag too."""
        a, b = mv("D-OPS", "89"), mv("D-EVID", "40")
        for fn in (lambda: V.combine([a, b], "sum"), lambda: V.combine([a, b], "max"), lambda: V.compare(a, b)):
            with self.assertRaises(MetTagMix) as cm:
                fn()
            self.assertEqual(cm.exception.code, "E-MET-TAG-MIX")
        with self.assertRaises(MetTagMix):
            V.compare(mv("D-OPS", "1", "D-OPS@1"), mv("D-OPS", "2", "D-OPS@2"))
        self.assertEqual(V.combine([mv("D-OPS", "1.5"), mv("D-OPS", "2.25")], "sum").value, "3.75")  # same definition: allowed
        self.assertEqual(V.compare(mv("D-OPS", "1"), mv("D-OPS", "2"))["relation"], "<")

    def test_TST_MET_04_side_by_side_has_no_derived_value(self):
        """AC-MET-04: the same two figures -> separate labelled columns, the 'not comparable' note, no derived cross-column value."""
        sbs = V.side_by_side([mv("D-OPS", "89"), mv("D-EVID", "40")])
        self.assertEqual([c["definition_tag"] for c in sbs["columns"]], ["D-OPS", "D-EVID"])
        self.assertEqual([c["value"] for c in sbs["columns"]], ["89", "40"])
        self.assertEqual((sbs["derived"], sbs["note"]), (None, "different definitions - not comparable"))
        self.assertTrue(all(c["label"] == "synthetic, unvalidated" for c in sbs["columns"]))
        self.assertNotIn("sum", sbs)
        with self.assertRaises(MetTagMix):
            V.side_by_side([mv("D-OPS", "1"), mv("D-OPS", "2")])  # two columns for one tag is not a comparison of definitions

    def test_TST_MET_05_conflicting_trends_flagged(self):
        """AC-MET-05: D-OPS improves and D-EVID worsens between two periods -> FAIL-02-conflict flag and no single 'improved' headline."""
        prev = [mv("D-OPS", "100"), mv("D-EVID", "10")]
        curr = [mv("D-OPS", "80"), mv("D-EVID", "15")]
        t = V.trend(prev, curr)
        self.assertEqual({r["definition_tag"]: r["direction"] for r in t["rows"]}, {"D-OPS": "improved", "D-EVID": "worsened"})
        self.assertIn("FAIL-02-conflict", t["flags"])
        self.assertIsNone(t["headline"])
        self.assertEqual(t["note"], "different definitions - not comparable")
        one = V.trend(prev[:1], curr[:1])
        self.assertEqual((one["headline"], one["flags"]), ("improved", []))
        pv = V.trend([mv("D-OPS", "100", "D-OPS@1")], [mv("D-OPS", "80", "D-OPS@2")])
        self.assertEqual(pv["rows"][0]["direction"], "not_comparable_policy_version")

    def test_TST_MET_06_time_to_close_two_separate_series(self):
        """AC-MET-06: 10 completed cycles under C-OPS and 8 under C-EVID -> two separate series, each with n, median, p90 per the stated method and
        open_count; no pooled series."""
        st = self.store(loaded=False)
        specs = [(h, None) for h in range(1, 11)]
        specs[:8] = [(h, e) for (h, _), e in zip(specs[:8], (2, 4, 6, 8, 10, 12, 14, 100))]
        specs.append((None, None))  # an open cycle: received, nothing closed
        self.cycles(st, "6", specs)
        out = {m.metric_id: m for m in st.met.time_to_close()}
        self.assertEqual(sorted(out), ["MET-TTC-C-EVID", "MET-TTC-C-OPS"])
        ops, ev = out["MET-TTC-C-OPS"], out["MET-TTC-C-EVID"]
        self.assertEqual((ops.n, ops.detail["median"], ops.detail["p90"], ops.detail["open_count"]), (10, "5.5", "9", 1))
        self.assertEqual((ev.n, ev.detail["median"], ev.detail["p90"], ev.detail["open_count"]), (8, "9", "100", 3))
        self.assertEqual((ops.definition_tag, ev.definition_tag), ("C-OPS", "C-EVID"))
        self.assertEqual(ops.detail["method"], V.METHOD)
        self.assertEqual(ops.detail["verdict"], "not_available_no_adopted_policy")
        self.assertEqual((ops.policy_status, ev.policy_status), ("candidate", "candidate"))
        self.assertEqual(ops.label, "synthetic, unvalidated")
        self.assertEqual(len(st.met.values_for("MET-TTC-C-OPS")), 1)  # stored, one per series, nothing pooled
        self.assertIsNone(st.con.execute("SELECT 1 FROM metric_value WHERE metric_id NOT IN ('MET-TTC-C-OPS','MET-TTC-C-EVID')").fetchone())

    def test_TST_MET_07_median_and_p90_methods(self):
        """AC-MET-07: [1,2,3,4,100] -> median 3, p90 100; [1,2,3,4] -> median 2.5, p90 4 (mean of the middle two; nearest rank); also through the service."""
        D_ = V.D
        a, b = [D_(x) for x in (1, 2, 3, 4, 100)], [D_(x) for x in (1, 2, 3, 4)]
        self.assertEqual((V.dtext(V.median(a)), V.dtext(V.p90(a))), ("3", "100"))
        self.assertEqual((V.dtext(V.median(b)), V.dtext(V.p90(b))), ("2.5", "4"))
        self.assertEqual(V.summarise([]), {"n": 0, "median": None, "p90": None})
        self.assertEqual(V.dtext(V.p90([D_(x) for x in range(1, 11)])), "9")
        st = self.store(loaded=False)
        self.cycles(st, "7", [(1, None), (2, None), (3, None), (4, None), (100, None)])
        ops = [m for m in st.met.time_to_close(["C-OPS"])][0]
        self.assertEqual((ops.value, ops.detail["p90"], ops.n), ("3", "100", 5))

    def test_TST_MET_08_baseline_has_no_completed_cycles(self):
        """AC-MET-08 (class C proxy): the 125 shipped cases carry FACT_RECEIVED only -> value null, reason no_completed_cycles, n = 0 for both clocks;
        never zero, never invented (K-04 / K-05 stay unmeasurable, OD-07)."""
        st = self.store()
        for m in st.met.time_to_close():
            self.assertIsNone(m.value)
            self.assertEqual((m.null_reason, m.n), ("no_completed_cycles", 0))
            self.assertEqual(m.detail["open_count"], 125)
            self.assertIsNone(m.detail["median"])
            self.assertIn("null (no_completed_cycles)", V.render_text(m))
            self.assertNotIn(" 0 ", V.render_text(m).split("n=")[0])
        row = st.con.execute("SELECT value, null_reason FROM metric_value WHERE metric_id = 'MET-TTC-C-OPS'").fetchone()
        self.assertEqual(row, (None, "no_completed_cycles"))

    def test_TST_MET_09_month_end_total_on_the_baseline(self):
        """AC-MET-09: the 125 shipped cases, explicit cutoff after all case dates, source cases.amount -> 622826.44 exactly, n = 125; the legacy 742,956.61
        is not produced."""
        st = self.store()
        src = CasesAmountSource(self.legacy())
        m = st.met.month_end_total(CUTOFF, "cases:125 (FX-BASE125)", src)
        self.assertEqual((m.value, m.n, m.partial, m.errors), ("622826.44", 125, False, []))
        self.assertNotEqual(m.value, "742956.61")
        self.assertEqual((m.metric_id, m.label, m.data_origin), ("MET-MONTH-END-TOTAL", "synthetic, unvalidated", "synthetic"))
        self.assertEqual(m.denominator, "cases:125 (FX-BASE125)")
        self.assertIsNone(m.definition_tag)
        stored = st.met.get_value(m.value_id)
        self.assertEqual((stored.value, stored.inputs_hash), (m.value, m.inputs_hash))

    def test_TST_MET_10_cutoff_and_denominator_are_required(self):
        """AC-MET-10: the same call without cutoff or denominator -> E-MET-CUTOFF-REQUIRED (no hidden default); nothing stored."""
        st = self.store(loaded=False)
        src = CasesAmountSource(R.RO(R.cases_db([("A", 1.0, "2025-01-01T00:00:00Z", "S1")], [])))
        for kw in ({}, {"cutoff_ts": CUTOFF}, {"denominator_ref": "d"}, {"cutoff_ts": " ", "denominator_ref": "d"}):
            with self.assertRaises(MetCutoffRequired) as cm:
                st.met.month_end_total(source=src, **kw)
            self.assertEqual(cm.exception.code, "E-MET-CUTOFF-REQUIRED")
        self.assertEqual(st.con.execute("SELECT count(*) FROM metric_value").fetchone()[0], 0)

    def test_TST_MET_11_no_join_fan_out(self):
        """AC-MET-11: two cases with 2 events and 1 event -> each amount counted once; the equivalent join query inflates and differs; the query plan
        touches one table."""
        st = self.store(loaded=False)
        con = R.cases_db([("A", 100.0, "2025-01-01T00:00:00Z", "S1"), ("B", 50.0, "2025-01-02T00:00:00Z", "S1")], ["A", "A", "B"])
        src = CasesAmountSource(R.RO(con))
        m = st.met.month_end_total(CUTOFF, "fixture", src)
        self.assertEqual((m.value, m.n), ("150.00", 2))
        joined = con.execute("SELECT SUM(c.amount) FROM cases c JOIN events e ON e.case_id = c.id").fetchone()[0]
        self.assertEqual(joined, 250.0)
        self.assertNotEqual(str(joined), m.value)
        plan = " ".join(src.plan()).lower()
        self.assertIn("cases", plan)
        self.assertNotIn("events", plan)
        self.assertNotIn("join", CASES_SQL.lower())

    def test_TST_MET_13_exact_decimal_sums(self):
        """AC-MET-13: 0.1 + 0.2 -> 0.30 exactly (the binary float sum drifts); 100 x 0.1 -> 10.00."""
        st = self.store(loaded=False)
        self.assertNotEqual(0.1 + 0.2, 0.3)
        m = st.met.month_end_total(CUTOFF, "fx", RowsSource("vendor_rows.amount_text", [("r1", 0.1), ("r2", 0.2)]))
        self.assertEqual(m.value, "0.30")
        m = st.met.month_end_total(CUTOFF, "fx", RowsSource("vendor_rows.amount_text", [("r%d" % i, 0.1) for i in range(100)]))
        self.assertEqual(m.value, "10.00")
        half = st.met.month_end_total(CUTOFF, "fx", RowsSource("vendor_rows.amount_text", [("a", "0.125"), ("b", "0.005")]))
        self.assertEqual(half.value, "0.13")  # 0.130 -> ROUND_HALF_EVEN at presentation

    def test_TST_MET_14_stored_values_reproduce(self):
        """AC-MET-14: a stored metric is recomputed after unrelated data are added -> equal value and inputs_hash; if a code change alters the result
        E-MET-NOT-REPRODUCIBLE is reported."""
        st = self.store(loaded=False)
        self.cycles(st, "14", [(h, None) for h in (3, 5, 8)])
        t = st.met.time_to_close(["C-OPS"])[0]
        con = R.cases_db([("A", 10.0, "2025-01-01T00:00:00Z", "S1"), ("B", 5.5, "2025-01-02T00:00:00Z", "S2")], [])
        src = CasesAmountSource(R.RO(con))
        me = st.met.month_end_total(CUTOFF, "fx", src)
        sites = {"C14%06d" % i: "S1" for i in range(3)}
        bl = st.met.backlog_by_site("D-OPS", st.now(), site_of=sites)
        ex = st.met.unresolved_exception_rate("D-OPS", site_of=sites)
        # unrelated data arrive after the values were stored
        self.cycles(st, "15", [(1, None), (2, None)])
        con.execute("INSERT INTO cases VALUES ('Z', 999.0, '2025-02-01T00:00:00Z', 'S3')")
        st.isvc.ingest("partner_feed", I.batch(5), "unrelated-1", "t-14")
        for v, kw in ((t, {}), (me, {"source": src}), (bl, {"site_of": sites}), (ex, {"site_of": sites})):
            r = st.met.reproduce(v.value_id, **kw)
            self.assertTrue(r["equal"], r)
            self.assertEqual(r["diff"], {})
        self.assertEqual(st.met.reproduce(me.value_id, source=src)["recomputed"], "15.50")
        with mock.patch("hub.metrics.values.median", lambda vals: V.D("999")):
            r = st.met.reproduce(t.value_id)
            self.assertFalse(r["equal"])
            self.assertIn("value", r["diff"])
            with self.assertRaises(MetNotReproducible) as cm:
                st.met.reproduce(t.value_id, strict=True)
            self.assertEqual(cm.exception.code, "E-MET-NOT-REPRODUCIBLE")

    def test_TST_MET_15_documentation_is_complete_or_the_build_fails(self):
        """AC-MET-15: documentation is generated for all registered KPIs; each page has window, denominator, exclusions and tag; a KPI missing one
        fails the build (E-MET-DEFINITION-REQUIRED) - at registration and when a row was written around the registry."""
        st = self.store(loaded=False)
        reg = st.met.registry
        reg.seed_builtin()
        pages = reg.documentation_pages()
        self.assertEqual(len(pages), len(BUILTIN))
        for p in pages:
            self.assertTrue(p["window"].strip() and p["denominator"].strip() and p["exclusions"].strip() and p["text"].strip())
        self.assertTrue(all(p["definition_tag"] for p in pages if p["metric_id"] != "MET-MONTH-END-TOTAL"))
        with self.assertRaises(MetDefinitionRequired):
            reg.register({"metric_id": "MET-BAD", "name": "n", "category": "count", "window": "w", "denominator": "d", "exclusions": "  ",
                          "basis": "event_derived", "documentation": "x"})
        st.con.execute("INSERT INTO metric_definition(metric_id, version, name, category, definition_tag, involves_definition, \"window\", denominator,"
                       " exclusions, basis, documentation) VALUES ('MET-ROGUE', 1, 'n', 'count', NULL, 0, 'w', 'd', ' ', 'event_derived', 'x')")
        st.con.commit()
        with self.assertRaises(MetDefinitionRequired) as cm:
            reg.documentation_pages()
        self.assertEqual(cm.exception.details["incomplete"], [{"metric_id": "MET-ROGUE", "missing": ["exclusions"]}])

    def test_TST_MET_16_operating_costs_is_not_cases_created(self):
        """AC-MET-16: operating_costs.total_cases offered as 'cases created' -> E-MET-SOURCE-REFUSED (registration and computation); a metric using
        operating_costs is only accepted as basis = modelled."""
        st = self.store(loaded=False)
        reg = st.met.registry
        base = {"metric_id": "MET-OPC", "name": "Cases created", "category": "count", "window": "w", "denominator": "d", "exclusions": "e",
                "basis": "event_derived", "documentation": "doc", "source": "operating_costs.total_cases", "source_meaning": "cases_created"}
        with self.assertRaises(MetSourceRefused) as cm:
            reg.register(base)
        self.assertEqual(cm.exception.code, "E-MET-SOURCE-REFUSED")
        with self.assertRaises(MetSourceRefused):
            reg.register(dict(base, source_meaning="spend"))  # not modelled
        self.assertEqual(reg.register(dict(base, source_meaning="spend", basis="modelled")), 1)
        with self.assertRaises(MetSourceRefused):
            st.met.month_end_total(CUTOFF, "fx", RowsSource("operating_costs.total_cases", [("r", 5)]))
        with self.assertRaises(MetSourceRefused):
            st.met.month_end_total(CUTOFF, "fx", RowsSource("something.else", [("r", 5)]))
        self.assertEqual(st.con.execute("SELECT count(*) FROM metric_value").fetchone()[0], 0)

    def test_TST_MET_17_backlog_by_site_on_the_baseline(self):
        """AC-MET-17: tag D-OPS, as_of 2025-12-19 -> per-site backlog and bucket counts; total backlog = cases not CLOSED = 89 of 125 (K-09-OPS); one tag."""
        st = self.store()
        sites = case_sites(self.legacy())
        self.assertEqual(len(sites), 125)
        m = st.met.backlog_by_site("D-OPS", "2025-12-19", site_of=sites)
        self.assertEqual((m.value, m.n, m.definition_tag), ("89", 125, "D-OPS"))
        by_site = m.detail["by_site"]
        self.assertEqual(sum(s["backlog"] for s in by_site.values()), 89)
        self.assertEqual(sum(s["cases"] for s in by_site.values()), 125)
        for s in by_site.values():
            self.assertEqual(sum(s["buckets"].values()), s["backlog"])
            self.assertEqual(sorted(s["buckets"]), sorted(["<=90", "91-365", "366-730", ">730"]))
        self.assertEqual(sorted(by_site), sorted(set(sites.values())))
        self.assertEqual(m.detail["closure_basis"], "label")  # no CLOSURE policy adopted: the label CLOSED is the stated default
        self.assertEqual((m.policy_status, m.policy_version), ("candidate", "D-OPS@1"))
        self.assertEqual(V.render_text(m).count("tag=D-OPS"), 1)

    def test_TST_MET_18_backlog_needs_a_definition_tag(self):
        """AC-MET-18: backlog requested without a definition tag -> E-MET-DEFINITION-REQUIRED (also blank, unknown tag, missing as_of); the untagged
        D-EVID state definition is not silently answered."""
        st = self.store(loaded=False)
        for kw in ({"as_of": "2025-12-19"}, {"definition_tag": " ", "as_of": "2025-12-19"}, {"definition_tag": "D-NOPE", "as_of": "2025-12-19"},
                   {"definition_tag": "D-OPS"}):
            with self.assertRaises(MetDefinitionRequired) as cm:
                st.met.backlog_by_site(**kw)
            self.assertEqual(cm.exception.code, "E-MET-DEFINITION-REQUIRED")
        from hub.metrics.errors import MetNotAvailable
        with self.assertRaises(MetNotAvailable):
            st.met.backlog_by_site("D-EVID", "2025-12-19")
        self.assertEqual(st.con.execute("SELECT count(*) FROM metric_value").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
