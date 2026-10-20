"""INC-09 planned tests, R2 reports (the five operations that answered 501 in INC-08 plus OP-MET-05): TST-ID-13..17, TST-INT-28, TST-NFR-03, -04,
TST-MET-19, -20, TST-POL-24. Named test_I9_<FAMILY>_<NN> (frozen earlier selectors keep their counts, inc09-design-notes D-12). Synthetic deliveries
are labelled 'synthetic, unvalidated'; shipped-data checks read the hash-gated FX-BASE125 sandbox copy through the read-only snapshot adapter.
"""
import hashlib
import json
import unittest

import _inc06 as I
import _inc09 as N
from hub.r2 import consistency
from hub.security.canonical import fmt, parse

AUTH = "TEST-AUTH-09 (synthetic)"
REASON = "synthetic reason: INC-09 test of a C3 read"


def setUpModule():
    N.skip_in_inner_egress_run()


def table_digest(con, skip=("consistency_finding", "audit_log", "sqlite_sequence", "session")):
    """sha256 per table of every row, except the finding rows, the audit trail and the session bookkeeping (last_seen_at of a request)."""
    out = {}
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'search_fts%' AND name NOT LIKE 'search_tri%'"
                            " ORDER BY name").fetchall():
        if t in skip:
            continue
        h = hashlib.sha256()
        for r in con.execute("SELECT * FROM \"%s\" ORDER BY 1" % t):
            h.update(repr(r).encode("utf-8"))
        out[t] = h.hexdigest()
    return out


def get_fresh(st, path, name):
    """GET with a session issued at the CURRENT test-clock time (the template tokens idle out when a test moves the clock)."""
    return st.call("GET", path, token=st.authn.login(name, st.pw, "t-fresh-login"))


class _Base(unittest.TestCase):
    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def store(self, **kw):
        st = N.R2Store(**kw)
        self.stores.append(st)
        return st

    def view(self, st, i, name="rev", **q):
        import urllib.parse as up
        r = st.get("/api/v2/crosswalk/view?" + up.urlencode(dict(q, id=i)), name)
        self.assertEqual(r.status, 200, r.text[:300])
        return r.json()


class R2CrosswalkPlanned(_Base):

    def test_I9_ID_13_same_linked_set_from_every_member(self):
        """AC-ID-13 (TST-ID-13): batch BT00000000 with a deviation and a CAPA -> lookup by batch id, deviation id and capa id returns the same linked
        set (3 entities). The shipped data also links LAB00000000 to the batch (LT-03): with that rule run the set is 4 from every member (DEV-92)."""
        st = self.store()
        st.run_rules("LT-01", "LT-02")
        sets = []
        for i in ("BT00000000", "DEV00000000", "CAPA00000000"):
            v = self.view(st, i)
            sets.append(sorted((e["type"], e["id"]) for e in v["entities"]))
            self.assertEqual((v["total"], v["truncated"], v["read_only"]), (3, False, True))
        self.assertEqual(sets[0], [("batch", "BT00000000"), ("capa", "CAPA00000000"), ("deviation", "DEV00000000")])
        self.assertEqual(sets[0], sets[1])
        self.assertEqual(sets[1], sets[2])
        st.run_rules("LT-03")
        four = [sorted((e["type"], e["id"]) for e in self.view(st, i)["entities"]) for i in ("BT00000000", "DEV00000000", "CAPA00000000", "LAB00000000")]
        self.assertTrue(all(s == four[0] for s in four) and len(four[0]) == 4)
        self.assertEqual(self.view(st, "BT00000000"), self.view(st, "BT00000000"))  # deterministic

    def test_I9_ID_14_size_cap_is_flagged_never_silent(self):
        """AC-ID-14 (TST-ID-14): a view that exceeds the size cap -> truncated = true with the total count; no silent cut."""
        st = self.store(extra={"crosswalk_view": {"size_cap": 2}})
        st.run_rules("LT-01", "LT-02", "LT-03")
        v = self.view(st, "BT00000000")
        self.assertEqual((v["truncated"], v["total"], len(v["entities"]), v["size_cap"]), (True, 4, 2, 2))
        self.assertEqual([(e["type"], e["id"]) for e in v["entities"]], [("batch", "BT00000000"), ("capa", "CAPA00000000")])
        st2 = self.store(extra={"crosswalk_view": {"size_cap": 4}})
        st2.run_rules("LT-01", "LT-02", "LT-03")
        v2 = self.view(st2, "BT00000000")
        self.assertEqual((v2["truncated"], v2["total"], len(v2["entities"])), (False, 4, 4))
        st3 = self.store(extra={"crosswalk_view": {"depth_cap": 1}})
        st3.run_rules("LT-01", "LT-02", "LT-03")
        v3 = self.view(st3, "CAPA00000000")
        self.assertTrue(v3["depth_capped"])  # CAPA -> DEV at depth 1; the batch behind DEV is beyond the cap and flagged, not silently dropped
        self.assertEqual(sorted(e["id"] for e in v3["entities"]), ["CAPA00000000", "DEV00000000"])

    def test_I9_ID_15_consistency_rule_raises_one_finding_and_changes_nothing(self):
        """AC-ID-15 (TST-ID-15): a configured test CONSISTENCY rule (case state X while the linked batch qa_status is Y) and a seeded contradictory
        fixture -> the check runs twice -> exactly one open finding; the store diff is empty except the finding row (and audit records)."""
        st = self.store()
        facts, _ = N.legacy_facts()
        state = st.con.execute("SELECT state FROM case_state WHERE case_id = 'C00000002'").fetchone()[0]
        st.cw.create_human_link(st.sess("rev"), "case", "C00000002", "batch", "BT00000000", "synthetic contradictory fixture (TST-ID-15)")
        st.cw.create_human_link(st.sess("rev"), "case", "C00000003", "batch", "BT00000001", "synthetic consistent fixture (TST-ID-15)")
        body = {"left": {"type": "case", "field": "state", "in": [state]}, "right": {"type": "batch", "field": "qa_status", "in": ["REVIEW"]}}
        st.pol.create_candidate(st.sess("ql"), "CONS-1", "CONSISTENCY", "synthetic test rule", body, AUTH)
        st.pol.adopt(st.sess("holder-1"), "CONS-1", 1, st.clock()[:10], "qa-owner-synthetic", AUTH)
        other_state = st.con.execute("SELECT state FROM case_state WHERE case_id = 'C00000003'").fetchone()[0]
        before = table_digest(st.con)
        r1 = consistency.run(st.con, st.clock, st.anchor, "host-operator", facts, "CONS-RUN-1")
        r2 = consistency.run(st.con, st.clock, st.anchor, "host-operator", facts, "CONS-RUN-2")
        self.assertEqual((r1["findings_new"], r2["findings_new"], r2["findings_open"]),
                         (1 + (1 if other_state == state and facts("batch", "BT00000001")["qa_status"] == "REVIEW" else 0), 0, r1["findings_open"]))
        self.assertEqual(table_digest(st.con), before)
        out = st.get("/api/v2/crosswalk/findings", "ql").json()
        objs = [f["object_refs"] for f in out["items"]]
        self.assertIn(["batch:BT00000000", "case:C00000002"], objs)
        self.assertEqual(len(objs), len(set(json.dumps(o) for o in objs)))
        f = [x for x in out["items"] if x["object_refs"] == ["batch:BT00000000", "case:C00000002"]][0]
        self.assertEqual((f["rule_ref"], f["policy_version"], f["status"]), ("CONS-1@2", "2", "open"))
        self.assertNotIn("statement", out)
        self.assertEqual(st.get("/api/v2/crosswalk/findings", "rev").status, 403)

    def test_I9_ID_16_no_adopted_policy_means_no_findings(self):
        """AC-ID-16 (TST-ID-16): fresh install, no adopted CONSISTENCY policy -> the check runs -> zero findings and the statement 'no consistency
        policy adopted' (also with the 5 seeded candidate policies of the loaded store, none of which is adopted)."""
        for loaded in (False, True):
            st = self.store(loaded=loaded)
            res = consistency.run(st.con, st.clock, st.anchor, "host-operator", None, "CONS-FRESH")
            self.assertEqual((res["findings_new"], res["findings_open"], res["statement"]), (0, 0, "no consistency policy adopted"))
            out = st.get("/api/v2/crosswalk/findings", "comp").json()
            self.assertEqual((out["items"], out["statement"]), ([], "no consistency policy adopted"))
            self.assertEqual(st.count("consistency_finding"), 0)

    def test_I9_ID_17_restricted_documents_are_denied_and_not_counted(self):
        """AC-ID-17 (TST-ID-17): a caller lacking access to restricted documents requests the joined view -> restricted linked documents appear as
        {access: denied} and are not counted in the totals revealed to the caller."""
        st = self.store(corpus=True)
        st.run_rules("LT-05")
        st.cw.create_human_link(st.sess("rev"), "case", "C00000002", "batch", "BT00000000", "synthetic link (TST-ID-17)")
        v = self.view(st, "C00000002", "rev")
        denied = [e for e in v["entities"] if e.get("access") == "denied"]
        self.assertEqual(len(denied), 2)
        self.assertTrue(all(set(e) == {"type", "access"} for e in denied))
        self.assertEqual(v["total"], 2)  # case + batch; the two restricted documents are not counted
        self.assertNotIn("DOC-00000062", json.dumps(v))
        self.assertNotIn("DOC-00000848", json.dumps(v))
        q = self.view(st, "C00000002", "ql", reason=REASON)
        self.assertEqual((q["total"], sorted(e["id"] for e in q["entities"] if e["type"] == "document")), (4, ["DOC-00000062", "DOC-00000848"]))


class R2IntakePlanned(_Base):

    def delay_fixture(self, st):
        """Items with delays 1 h, 3.9 h, 4.1 h and one future source_ts (synthetic, unvalidated)."""
        now = parse(st.clock())
        import datetime
        ts = lambda h: fmt(now - datetime.timedelta(hours=h))
        st.isvc.ingest("partner_feed", [I.feed(30, source_ts=ts(1)), I.feed(31, source_ts=ts(3.9)), I.feed(32, source_ts=ts(4.1)),
                                        I.feed(33, source_ts=ts(-2))], "t-delay", "t-delay")

    def test_I9_INT_28_delay_report_lists_items_per_source(self):
        """AC-INT-28 (TST-INT-28): a source with late items -> the delay report lists the items of that source with their delay and no manual step;
        a future source_ts is flagged."""
        st = self.store()
        self.delay_fixture(st)
        r = st.get("/api/v2/intake/sources/partner_feed/delays", "ql")
        self.assertEqual(r.status, 200, r.text[:300])
        out = r.json()
        got = dict((i["ref_id"], (i["delay_hours"], i["flag"])) for i in out["items"])
        self.assertEqual(out["source"], "partner_feed")
        self.assertEqual(sorted(got.values()), sorted([("1.000", None), ("3.900", None), ("4.100", None), ("-2.000", "FUTURE_SOURCE_TS")]))
        self.assertEqual(st.get("/api/v2/intake/sources/partner_feed/delays", "ql").raw, r.raw)
        self.assertEqual(st.get("/api/v2/intake/sources/gateway/delays", "ql").code, "E-INT-ITEM-NOT-FOUND")
        self.assertEqual(st.get("/api/v2/intake/sources/partner_feed/delays", "rev").status, 403)

    def test_I9_NFR_03_share_within_four_hours(self):
        """AC-NFR-03 (TST-NFR-03, class C): delays 1 h, 3.9 h, 4.1 h and a future source_ts -> share within 4 h = 2 of 3 non-future items (66.7%);
        the future item is flagged and excluded from the share. The 4 h value is an Assumption (PNFR-03), not a validated target."""
        st = self.store()
        self.delay_fixture(st)
        s = st.get("/api/v2/intake/sources/partner_feed/delays", "comp").json()["summary"]
        self.assertEqual((s["within_threshold"], s["usable_delays"], s["share_within_threshold_pct"], s["future_source_ts"]), (2, 3, "66.7", 1))
        print("\n[TST-NFR-03] share within %s h: %s%% (%d of %d; %d future excluded) - against an unvalidated working target. synthetic, unvalidated"
              % (s["threshold_hours"], s["share_within_threshold_pct"], s["within_threshold"], s["usable_delays"], s["future_source_ts"]))

    def test_I9_NFR_04_source_older_than_24_hours_is_listed(self):
        """AC-NFR-04 (TST-NFR-04, class C): a source whose newest ACCEPTED item is 25 h old -> the freshness report lists it as older than 24 h with
        its age; unaccepted (exception) items do not refresh a source."""
        st = self.store()
        st.isvc.ingest("partner_feed", [I.feed(40), I.feed(41)], "t-fresh-1", "t-fresh-1")
        newest = st.con.execute("SELECT max(receipt_time) FROM raw_intake").fetchone()[0]
        st.clock.advance(24 * 3600)
        st.isvc.ingest("partner_feed", [I.feed(42, ref_id="C00009991")], "t-fresh-2", "t-fresh-2")  # unmatched -> EXCEPTION, not accepted
        self.assertEqual(st.con.execute("SELECT outcome FROM intake_current c JOIN raw_intake r ON r.raw_id = c.raw_id WHERE r.run_id = 't-fresh-2'")
                         .fetchone()[0], "EXCEPTION")
        as_of = fmt(parse(newest) + __import__("datetime").timedelta(hours=25))
        out = get_fresh(st, "/api/v2/intake/sources/partner_feed/delays?view=freshness&as_of=" + as_of, "ql").json()
        row = out["sources"][0]
        self.assertEqual((row["source"], row["age_hours"], row["older_than_threshold"], out["stale"]), ("partner_feed", "25.000", True, ["partner_feed"]))
        out2 = get_fresh(st, "/api/v2/intake/sources/partner_feed/delays?view=freshness&as_of=" + fmt(parse(newest) + __import__("datetime").timedelta(hours=23)),
                         "ql").json()
        self.assertEqual((out2["sources"][0]["older_than_threshold"], out2["stale"]), (False, []))
        print("\n[TST-NFR-04] partner_feed newest accepted item age %s h > %s h -> listed (PNFR-04 'risk signal' undefined: age of the newest "
              "accepted item measured). synthetic, unvalidated" % (row["age_hours"], out["threshold_hours"]))


class R2MetricsPolicyPlanned(_Base):

    def test_I9_MET_19_unmatched_rate_and_delay_per_source(self):
        """AC-MET-19 (TST-MET-19): intake and run records for two sources -> per-source unmatched rate and reconciliation-delay distribution are
        produced and reproducible (two identical calls give identical JSON; the figures equal an independent count of the stored records)."""
        st = self.store()
        st.isvc.ingest("partner_feed", [I.feed(i) for i in range(50, 56)] + [I.feed(56, ref_id="C00009991"), I.feed(57, ref_id="C00009992")],
                       "t-sq-1", "t-sq-1")
        by, _ = I.legacy_deliveries()
        st.clock.advance(3600)
        st.isvc.ingest("source_message", by["source_message"], "t-sq-2", "t-sq-2")
        a = get_fresh(st, "/api/v2/metrics/source-quality", "ql")
        self.assertEqual(a.status, 200, a.text[:300])
        self.assertEqual(get_fresh(st, "/api/v2/metrics/source-quality", "ql").raw, a.raw)
        v = a.json()
        per = v["detail"]["per_source"]
        self.assertEqual(sorted(per), ["partner_feed", "source_message"])
        for src in per:
            rows = st.con.execute("SELECT c.outcome, c.all_reasons FROM intake_current c JOIN raw_intake r ON r.raw_id = c.raw_id WHERE r.source = ?",
                                  (src,)).fetchall()
            val = [x for x in rows if x[0] in ("VALIDATED", "VALIDATED_WITH_FLAGS", "EXCEPTION")]
            un = [x for x in val if set(json.loads(x[1])) & {"UNMATCHED_REF", "NO_BUSINESS_KEY"}]
            self.assertEqual((per[src]["validated_items"], per[src]["unmatched_items"]), (len(val), len(un)))
            d = per[src]["reconciliation_delay_hours"]
            self.assertEqual(d["n"], len(rows))
            self.assertTrue(float(d["min"]) >= 0 and float(d["min"]) <= float(d["p50"]) <= float(d["p95"]) <= float(d["max"]))
        self.assertEqual(per["partner_feed"]["unmatched_items"], 2)
        for k in ("value_id", "metric_id", "metric_version", "value", "n", "partial", "denominator", "exclusions", "basis", "data_origin", "label",
                  "inputs_hash", "code_version", "computed_at"):
            self.assertIn(k, v)
        self.assertEqual((v["data_origin"], v["label"]), ("synthetic", "synthetic, unvalidated"))
        self.assertEqual(st.count("metric_value"), 0)  # computed, not stored
        print("\n[TST-MET-19] %s. synthetic, unvalidated" % json.dumps({s: {"rate": per[s]["unmatched_reference_rate"],
                                                                             "p50_h": per[s]["reconciliation_delay_hours"]["p50"]} for s in per}))

    def test_I9_MET_20_case_cost_is_not_available(self):
        """AC-MET-20 (TST-MET-20): OP-MET-05 requested -> E-MET-NOT-AVAILABLE (no cost input, OPD-08); nothing is stored."""
        st = self.store()
        for name in ("ql", "comp", "fin"):
            r = st.get("/api/v2/metrics/case-cost", name)
            self.assertEqual((r.status, r.code), (501, "E-MET-NOT-AVAILABLE"), name)
        self.assertEqual(st.get("/api/v2/metrics/case-cost", "rev").status, 403)
        self.assertEqual(st.count("metric_value"), 0)

    def test_I9_POL_24_divergence_report_over_the_shipped_cases(self):
        """AC-POL-24 (TST-POL-24): the 125 shipped cases and the three as-found sets -> the divergence report lists the cases where amount_over_limit
        differs, with traces; the count is recorded (audit); no state change and no 'correct' set named."""
        _, cases = N.legacy_facts()
        self.assertEqual(len(cases), 125)
        st = self.store(app_kw={"case_inputs": lambda: cases})
        st.load_rules()
        before = table_digest(st.con)
        r = st.get("/api/v2/rules/divergence", "ql")
        self.assertEqual(r.status, 200, r.text[:300])
        out = r.json()
        self.assertEqual(out["compared_sets"], ["as-found-batch@1", "as-found-js@1", "as-found-python@1"])
        self.assertEqual((out["inputs"], out["count"]), (125, len(out["divergent"])))
        for d in out["divergent"]:
            self.assertEqual(sorted(d["traces"]), sorted(out["compared_sets"]))
            self.assertGreater(len(set(v for v in d["outputs"].values() if v is not None)), 1)
        self.assertEqual(table_digest(st.con), before)
        rec = st.con.execute("SELECT details FROM audit_log WHERE action = 'RULE_DIVERGENCE_REPORTED' ORDER BY audit_seq DESC LIMIT 1").fetchone()
        self.assertEqual(json.loads(rec[0])["divergent"], out["count"])
        keys = " ".join(N.walk_keys(out)).lower()
        for word in ("correct", "winner", "recommend", "preferred", "resolution"):
            self.assertNotIn(word, keys)
        self.assertEqual(st.con.execute("SELECT count(*) FROM active_ruleset").fetchone()[0], 0)
        self.assertEqual(st.get("/api/v2/rules/divergence", "rev").status, 403)
        print("\n[TST-POL-24] divergent cases: %d of %d; null (not comparable) outputs per set: %s. Reported, not resolved. synthetic, unvalidated"
              % (out["count"], out["inputs"], out["null_outputs"]))


if __name__ == "__main__":
    unittest.main()
