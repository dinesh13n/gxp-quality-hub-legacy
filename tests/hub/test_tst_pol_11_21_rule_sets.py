"""TST-POL-11..21 (AC-POL-11..21, FR-POL-04/06, BEH-POL-06..09; TST-POL-19..21 class B: OD-S12-04) - the three as-found rule
sets as inactive read-only data, parity with the Stage 7 goldens, explicit-ref what-if evaluation, the no-active-set refusal,
activation with a recorded human decision, and the `defaulted` marker. Fixture: FX-BASE125 sandbox copy + a loaded store.
"""
import json
import unittest

import _support as S
import _inc04 as P
from hub.policy import engine, rulesets
from hub.policy.errors import GateNotAuthorised, NoActiveRuleset, NotFound, ReadonlySet, UnknownFunction

AUTH = "TEST-AUTH-2 (synthetic)"


def setUpModule():
    S.require_sandbox()


class TST_POL_RuleSets(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.st = P.PStore(loaded=True)
        cls.svc = cls.st.svc

    @classmethod
    def tearDownClass(cls):
        cls.st.close()

    # ---- AC-POL-11
    def test_TST_POL_11_loader_lists_three_read_only_inactive_sets(self):
        """TST-POL-11 / AC-POL-11: as-found-python / -js / -batch exist, origin as-found, read_only, INACTIVE; an edit returns E-POL-READONLY-SET."""
        sets = self.svc.list_rulesets()
        self.assertEqual([(s["ruleset_ref"], s["origin"], s["read_only"], s["active_for"]) for s in sets],
                         [("as-found-batch@1", "as-found", True, []), ("as-found-js@1", "as-found", True, []),
                          ("as-found-python@1", "as-found", True, [])])
        self.assertEqual({s["ruleset_ref"]: s["functions"] for s in sets},
                         {"as-found-batch@1": ["SHIFT_FLAG"], "as-found-js@1": ["AMOUNT_LIMIT"],
                          "as-found-python@1": ["MANUAL_REVIEW", "PRIORITY"]})
        self.assertEqual(self.svc.active(), {})
        before = {r["ruleset_ref"]: rulesets.content_hash(self.svc.get_ruleset(r["ruleset_ref"])) for r in sets}
        h = self.st.sess("holder-1")
        for ref in before:
            row_id = self.svc.get_ruleset(ref)["rows"][0]["row_id"]
            with self.assertRaises(ReadonlySet) as cm:
                self.svc.edit_rule_row(h, ref, row_id, AUTH, outcome_updates={"value": 1})
            self.assertEqual(cm.exception.code, "E-POL-READONLY-SET")
        self.assertEqual({r["ruleset_ref"]: rulesets.content_hash(self.svc.get_ruleset(r["ruleset_ref"])) for r in self.svc.list_rulesets()}, before)
        self.assertEqual([a["reason"] for a in self.st.audit_actions("RULE_ROW_CHANGED") if a["outcome"] == "denied"], ["read_only_set"] * 3)
        loaded = self.st.audit_actions("RULESET_LOADED")
        self.assertEqual([(a["object_ref"], a["details"]["active"]) for a in loaded],
                         [("ruleset:as-found-python@1", False), ("ruleset:as-found-js@1", False), ("ruleset:as-found-batch@1", False)])
        self.assertEqual(len(self.svc.get_ruleset("as-found-js@1")["rows"]), 15 + 2)
        self.assertEqual(len([r for r in self.svc.get_ruleset("as-found-batch@1")["rows"] if r["outcome"]["kind"] == "register"]), 40)

    # ---- AC-POL-12
    def test_TST_POL_12_priority_truth_table_byte_equal(self):
        """TST-POL-12 / AC-POL-12: all 120 PRIORITY outcomes of as-found-python equal the Stage 7 golden (byte-equal JSON)."""
        gold = P.golden(["priority_truth_table"])
        got = []
        for status, sev, amount, _ in gold:
            r = self.svc.evaluate("PRIORITY", {"status": status, "severity": sev, "amount": amount}, "as-found-python@1")
            self.assertFalse(r["defaulted"], (status, sev, amount))
            self.assertFalse(r["authoritative"])
            got.append(r["outcome"])
        self.assertEqual(len(got), 120)
        self.assertEqual(json.dumps(got), json.dumps([g[3] for g in gold]))

    # ---- AC-POL-13
    def test_TST_POL_13_manual_review_table(self):
        """TST-POL-13 / AC-POL-13: all 20 MANUAL_REVIEW outcomes equal the golden, including CLOSED + HIGH = true."""
        gold = P.golden(["manual_review_truth_table"])
        got = [self.svc.evaluate("MANUAL_REVIEW", {"status": s, "severity": v}, "as-found-python@1")["outcome"] for s, v, _ in gold]
        self.assertEqual(json.dumps(got), json.dumps([g[2] for g in gold]))
        self.assertIs(self.svc.evaluate("MANUAL_REVIEW", {"status": "CLOSED", "severity": "HIGH"}, "as-found-python@1")["outcome"], True)
        self.assertEqual(len(got), 20)

    # ---- AC-POL-14
    def test_TST_POL_14_js_thresholds_and_tolerance(self):
        """TST-POL-14 / AC-POL-14: 32 (region, year) thresholds and the 26250 / 26250.01 tolerance cases equal the golden."""
        table = P.golden(["js_policy_table", "table"])
        known = {(v["region"], int(v["effective_from"][:4])) for v in json.load(open(S.LEGACY_ROOT + "/contracts/decision-policies-archive.json"))["historical_versions"]}
        for region, year, want in table:
            r = self.svc.evaluate("AMOUNT_LIMIT", {"amount": 0, "region": region, "year": year}, "as-found-js@1")
            self.assertEqual(r["outcome"]["threshold"], want, (region, year))
            self.assertEqual(r["defaulted"], (region, year) not in known, (region, year))  # marker exactly when the 999999 fallback applies
        self.assertEqual(len(table), 32)
        a = lambda amt: self.svc.evaluate("AMOUNT_LIMIT", {"amount": amt, "region": "APAC", "year": 2026}, "as-found-js@1")["outcome"]
        self.assertEqual((a(26250)["allowed"], a(26250.01)["allowed"], a(27000)["allowed"], a(26250)["threshold"]), (True, False, False, 25000))
        self.assertEqual((a("26250")["allowed"], a("26250.01")["allowed"], a(-5)["allowed"]), (True, False, True))

    # ---- AC-POL-15
    def test_TST_POL_15_batch_flags_equal_row_predicate_and_rows_not_multiplied(self):
        """TST-POL-15 / AC-POL-15: SHIFT_FLAG equals the row-level predicate; one result per input row (no JOIN fan-out)."""
        cases = [("OPEN", 100, 5000), ("OPEN", 5000, 5000), ("OPEN", 5000.01, 5000), ("HOLD", 1, 5000), ("REVIEW", 99999, None),
                 ("OPEN", 99999, None), ("CLOSED", 8500.01, 8500.0), ("ESCALATED", 2500, 2500), ("REOPENED", 2499.99, 2500), ("OPEN", 0, 0)]
        inputs = [{"status": s, "value": v, "threshold": t} for s, v, t in cases]
        res = self.svc.evaluate_many("SHIFT_FLAG", inputs, "as-found-batch@1")
        want = [s in ("HOLD", "REVIEW") or (t is not None and v > t) for s, v, t in cases]
        self.assertEqual([r["outcome"] for r in res], want)
        self.assertEqual(len(res), len(inputs))
        self.assertEqual([r["defaulted_reason"] for r in res], [None, None, None, None, "NULL_INPUT", "NULL_INPUT", None, None, None, None])
        doc = self.svc.get_ruleset("as-found-batch@1")
        per_region = {}
        for r in doc["rows"]:
            if r["outcome"]["kind"] == "register" and r["outcome"]["active"] == 1:
                per_region[r["outcome"]["region"]] = per_region.get(r["outcome"]["region"], 0) + 1
        self.assertEqual(sorted(per_region.items()), [tuple(x) for x in P.golden(["shift_active_policies_per_region"])])
        objs = [{"status": "OPEN", "value": 4000 + i, "region": "DE", "policy_code": "GXP-RULE-2"} for i in range(3)]
        by_reg = self.svc.evaluate_many("SHIFT_FLAG", objs, "as-found-batch@1")
        self.assertEqual(len(by_reg), 3)                      # the legacy join would give 3 x 5 = 15 rows for region DE
        self.assertEqual(3 * per_region["DE"], 15)
        self.assertEqual([r["outcome"] for r in by_reg], [False, False, False])  # DE GXP-RULE-2 threshold 8500
        self.assertEqual(self.svc.evaluate("SHIFT_FLAG", {"status": "OPEN", "value": 8500.01, "region": "DE", "policy_code": "GXP-RULE-2"},
                                            "as-found-batch@1")["outcome"], True)
        miss = self.svc.evaluate("SHIFT_FLAG", {"status": "OPEN", "value": 1, "region": "DE", "policy_code": "NOPE"}, "as-found-batch@1")
        self.assertEqual((miss["outcome"], miss["defaulted_reason"]), (False, "NO_MATCH_REGION_YEAR"))
        inactive = self.svc.evaluate("SHIFT_FLAG", {"status": "OPEN", "value": 9000, "region": "AU", "policy_code": "GXP-RULE-2"}, "as-found-batch@1")
        self.assertEqual((inactive["outcome"], inactive["defaulted_reason"]), (False, "NO_MATCH_REGION_YEAR"))  # POL-0007 is active = 0

    # ---- AC-POL-16
    def test_TST_POL_16_no_active_set_refuses(self):
        """TST-POL-16 / AC-POL-16: evaluate without ruleset_ref while no set is active -> E-POL-NO-ACTIVE-RULESET (every function)."""
        samples = {"PRIORITY": {"status": "OPEN", "severity": "LOW", "amount": 1}, "MANUAL_REVIEW": {"status": "OPEN", "severity": "LOW"},
                   "AMOUNT_LIMIT": {"amount": 1, "region": "APAC", "year": 2026}, "SHIFT_FLAG": {"status": "OPEN", "value": 1, "threshold": 2}}
        for fn, inp in samples.items():
            with self.assertRaises(NoActiveRuleset) as cm:
                self.svc.evaluate(fn, inp)
            self.assertEqual(cm.exception.code, "E-POL-NO-ACTIVE-RULESET")
            with self.assertRaises(NoActiveRuleset):
                self.svc.evaluate_many(fn, [inp])
        with self.assertRaises(UnknownFunction):
            self.svc.evaluate("NOPE", {})

    # ---- AC-POL-17
    def test_TST_POL_17_explicit_ref_is_a_what_if(self):
        """TST-POL-17 / AC-POL-17: with no active set, an explicit as-found-python ref returns an outcome with authoritative = false."""
        r = self.svc.evaluate("PRIORITY", {"status": "OPEN", "severity": "CRITICAL", "amount": 1}, "as-found-python@1")
        self.assertEqual((r["outcome"], r["authoritative"], r["ruleset_ref"], r["defaulted"]), ("urgent", False, "as-found-python@1", False))
        self.assertEqual([t["row_id"] for t in r["trace"]], ["PY-P1", "PY-P2"])
        self.assertEqual([t["matched"] for t in r["trace"]], [False, True])
        with self.assertRaises(NotFound):
            self.svc.evaluate("PRIORITY", {}, "as-found-python@9")
        with self.assertRaises(NotFound):
            self.svc.evaluate("PRIORITY", {}, "not a ref")
        with self.assertRaises(UnknownFunction):
            self.svc.evaluate("PRIORITY", {"status": "OPEN", "severity": "LOW", "amount": 1}, "as-found-js@1")

    # ---- AC-POL-18
    def test_TST_POL_18_activation_needs_holder_and_recorded_decision(self):
        """TST-POL-18 / AC-POL-18: a holder records a decision, then sets active_ruleset[PRIORITY]; RULESET_ACTIVATED audited; a service actor is rejected."""
        st = P.PStore(loaded=True)
        try:
            svc, h = st.svc, st.sess("holder-1")
            ref = "as-found-python@1"
            with self.assertRaises(GateNotAuthorised):
                svc.record_activation_decision(st.service_session(), "PRIORITY", ref, AUTH, "service attempt")
            with self.assertRaises(GateNotAuthorised):
                svc.activate(st.service_session(), "PRIORITY", ref, AUTH, 1)
            self.assertEqual(svc.active(), {})
            d = svc.record_activation_decision(h, "PRIORITY", ref, AUTH, "synthetic test decision to activate the as-found python rule")
            out = svc.activate(h, "PRIORITY", ref, AUTH, d["decision_seq"])
            self.assertEqual((out["ruleset_ref"], out["previous"]), (ref, None))
            self.assertEqual(svc.active(), {"PRIORITY": ref})
            self.assertEqual([s["active_for"] for s in svc.list_rulesets() if s["ruleset_ref"] == ref], [["PRIORITY"]])
            ev = svc.events(ref, "RULESET_ACTIVATED")
            self.assertEqual((len(ev), ev[0]["actor"], ev[0]["authority_ref"], ev[0]["new_value"]["decision_audit_seq"]),
                             (1, "holder-1", AUTH, d["decision_seq"]))
            act = st.audit_actions("RULESET_ACTIVATED")
            self.assertEqual([(a["outcome"], a["actor"], a["details"]["decision_audit_seq"]) for a in act], [("success", "holder-1", d["decision_seq"])])
            self.assertEqual(st.audit_actions("POLICY_DECISION_RECORDED")[0]["actor_kind"], "human")
            r = svc.evaluate("PRIORITY", {"status": "OPEN", "severity": "LOW", "amount": 50000.01})
            self.assertEqual((r["outcome"], r["authoritative"]), ("urgent", True))
            self.assertEqual(svc.evaluate("PRIORITY", {"status": "OPEN", "severity": "LOW", "amount": 1}, ref)["authoritative"], True)
            with self.assertRaises(NoActiveRuleset):
                svc.evaluate("AMOUNT_LIMIT", {"amount": 1, "region": "APAC", "year": 2026})  # other functions stay unset
            with self.assertRaises(GateNotAuthorised):
                svc.deactivate(st.service_session(), "PRIORITY", AUTH)
            self.assertEqual(svc.active(), {"PRIORITY": ref})
            svc.deactivate(h, "PRIORITY", "TEST-AUTH-3 (synthetic)")
            self.assertEqual(svc.active(), {})
            self.assertEqual([e["event_type"] for e in svc.events(ref)], ["RULESET_ACTIVATED", "RULESET_DEACTIVATED"])
            with self.assertRaises(NoActiveRuleset):
                svc.evaluate("PRIORITY", {"status": "OPEN", "severity": "LOW", "amount": 1})
            self.assertEqual(st.verify()["status"], "ok")
        finally:
            st.close()

    # ---- AC-POL-19 / 20 / 21 (class B: the default value and its marker are OD-S12-04 decisions; as-found value preserved AND marked)
    def test_TST_POL_19_unmatched_region_year_returns_999999_marked(self):
        """TST-POL-19 / AC-POL-19: as-found-js, region MARS, year 2026 -> limit 999999, defaulted = true, NO_MATCH_REGION_YEAR; the marker is in the result and the trace text."""
        r = self.svc.evaluate("AMOUNT_LIMIT", {"amount": 1000, "region": "MARS", "year": 2026}, "as-found-js@1")
        self.assertEqual((r["outcome"]["threshold"], r["outcome"]["allowed"], r["defaulted"], r["defaulted_reason"]), (999999, True, True, "NO_MATCH_REGION_YEAR"))
        self.assertEqual(r["trace"][-2]["row_id"], "JS-default")
        text = engine.render_text(r)
        self.assertIn("DEFAULTED: NO_MATCH_REGION_YEAR", text)
        self.assertIn('"defaulted":true', json.dumps(r, sort_keys=True, separators=(",", ":")))   # the API response body
        self.assertEqual(json.loads(json.dumps(r))["defaulted_reason"], "NO_MATCH_REGION_YEAR")
        for region, year in (("IN", 2026), ("APAC", 2027), ("APAC", 2021)):
            x = self.svc.evaluate("AMOUNT_LIMIT", {"amount": 1, "region": region, "year": year}, "as-found-js@1")
            self.assertEqual((x["outcome"]["threshold"], x["defaulted"]), (999999, True))
        self.assertEqual(self.svc.evaluate("AMOUNT_LIMIT", {"amount": 1, "region": None, "year": 2026}, "as-found-js@1")["defaulted_reason"], "NULL_INPUT")

    def test_TST_POL_20_unknown_status_falls_through_marked(self):
        """TST-POL-20 / AC-POL-20: as-found-python with status 'WEIRD' -> outcome queue (as-found) with defaulted = true, UNKNOWN_INPUT_VALUE."""
        r = self.svc.evaluate("PRIORITY", {"status": "WEIRD", "severity": "LOW", "amount": 1}, "as-found-python@1")
        self.assertEqual((r["outcome"], r["defaulted"], r["defaulted_reason"]), ("queue", True, "UNKNOWN_INPUT_VALUE"))
        self.assertIn("DEFAULTED: UNKNOWN_INPUT_VALUE", engine.render_text(r))
        r2 = self.svc.evaluate("PRIORITY", {"status": "OPEN", "severity": "SEVERE", "amount": 1}, "as-found-python@1")
        self.assertEqual((r2["outcome"], r2["defaulted_reason"]), ("queue", "UNKNOWN_INPUT_VALUE"))
        r3 = self.svc.evaluate("PRIORITY", {"status": "WEIRD", "severity": "CRITICAL", "amount": 1}, "as-found-python@1")
        self.assertEqual((r3["outcome"], r3["defaulted_reason"]), ("urgent", "UNKNOWN_INPUT_VALUE"))  # as-found value kept, still marked
        r4 = self.svc.evaluate("PRIORITY", {"status": None, "severity": "LOW", "amount": 1}, "as-found-python@1")
        self.assertEqual((r4["outcome"], r4["defaulted_reason"]), ("queue", "NULL_INPUT"))

    def test_TST_POL_21_known_inputs_reaching_the_last_row_are_not_defaulted(self):
        """TST-POL-21 / AC-POL-21: known status and severity (OPEN, LOW) falling to the final queue row -> queue, defaulted = false."""
        r = self.svc.evaluate("PRIORITY", {"status": "OPEN", "severity": "LOW", "amount": 10}, "as-found-python@1")
        self.assertEqual((r["outcome"], r["defaulted"], r["defaulted_reason"]), ("queue", False, None))
        self.assertEqual(r["trace"][-1]["row_id"], "PY-P6")
        self.assertNotIn("DEFAULTED", engine.render_text(r))
        m = self.svc.evaluate("MANUAL_REVIEW", {"status": "OPEN", "severity": "LOW"}, "as-found-python@1")
        self.assertEqual((m["outcome"], m["defaulted"]), (False, False))


if __name__ == "__main__":
    unittest.main()
