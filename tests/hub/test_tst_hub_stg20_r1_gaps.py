"""Stage 20 DI-04 R1-gap tests (DW-07 policy withdrawal / FAC-13 proposed; DW-08 automatic rule-trace producer; DW-09 CLI error shape
addendum / FAC-10 option 'addendum', DQ-05 / OD-26). Synthetic, unvalidated. The Zone H holders below are SYNTHETIC TEST DATA (the shipped
config keeps zone_h.holders EMPTY); nothing here is a HAR-06 approval or a real policy decision.

  S10  every CLI runner reports an error as ONE JSON object on stderr in the documented shape (docs/20-application/spec-addendum-cli-error-shape.md)
  S11  withdrawal through the Zone H choke point (ZH-10 op withdraw_policy): POLICY_WITHDRAWN event + audit; status report / get_policy /
       metric values show it; an earlier stored metric value still reproduces exactly
  S12  refusals: no holders (shipped), non-holder, no authority_ref, candidate, double withdrawal, date before effective_from - nothing written
  S13  the version stops applying: overlap window ends at withdrawn_from; clock verdict and closure policy stop
  S14  producer: traces exist without record-trace (AC-REV-05/06/08); idempotent; no active set -> E-POL-NO-ACTIVE-RULESET, nothing stored
  S15  flags of produced traces accept override (AC-GATE-18/19); an unmatched intake item's flag action has a retrievable trail (RTD-69)
"""
import json
import os
import subprocess
import sys
import unittest

import _inc06 as I
import _inc08 as W
import _stg20 as T
import _support as S
from hub.policy.errors import AuthorityRequired, NoActiveRuleset, Overlap, PolicyInvalid
from hub.policy import clocks
from hub.review import producer

AUTH = "TEST-AUTH-S20 (synthetic)"
RUNNERS = (("hub", "init", False), ("hub.admin", "status", False), ("hub.decision", "status", False), ("hub.intake", "status", False),
           ("hub.policy", "status", False), ("hub.metrics", "registry", True), ("hub.r2", "freshness", True), ("hub.runs", "status", True),
           ("hub.search", "status", True), ("hub.web", "status", True))
BASE_KEYS = ["code", "details", "message"]


def setUpModule():
    T.skip_in_inner_egress_run()


class TST_HUB_STG20_R1Gaps(unittest.TestCase):

    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def store(self, **kw):
        st = W.WStore(**kw)
        self.stores.append(st)
        return st

    # ------------------------------------------------------------------ DW-09
    def test_TST_HUB_STG20_S10_cli_error_shape_all_runners(self):
        """S10 (DW-09, FAC-10 addendum option, DQ-05): kill switch (E-HUB-KILLED, exit 3) and runtime floor 3.12 on the 3.10 reference
        runtime (E-CO-RUNTIME-UNSUPPORTED, exit 8) for all 10 runners: stderr is exactly one JSON object with the documented keys
        ({code, message, details}; + correlation_id for metrics, r2, runs, search, web), nothing on stdout, exit code = the error's code."""
        import platform
        base = S.tmpdir("s20s10-")
        cfgs = {"kill": ({"hub": {"kill": True}}, "E-HUB-KILLED", 3, "the hub kill switch is on")}
        if tuple(int(x) for x in platform.python_version_tuple()[:2]) < (3, 12):
            cfgs["floor"] = ({"runtime": {"floor": "3.12"}}, "E-CO-RUNTIME-UNSUPPORTED", 8, None)
        for name, (cfg, code, rc, _msg) in sorted(cfgs.items()):
            path = os.path.join(base, name + ".json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cfg, f)
            for mod, cmd, corr in RUNNERS:
                with self.subTest(runner=mod, case=name):
                    p = subprocess.run([sys.executable, "-B", "-m", mod, "--config", path, cmd, "--data-dir", os.path.join(base, "d")],
                                       cwd=S.CODE_ROOT, env=S.child_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True, timeout=120)
                    self.assertEqual(p.returncode, rc, p.stderr[-800:])
                    self.assertEqual(p.stdout, "")
                    env = json.loads(p.stderr)
                    self.assertIsInstance(env, dict)
                    self.assertEqual(env["code"], code)
                    self.assertTrue(isinstance(env["message"], str) and env["message"])
                    keys = sorted(env)
                    if name == "kill":
                        self.assertEqual(keys, sorted(BASE_KEYS + (["correlation_id"] if corr else [])), mod)
                    else:
                        self.assertIn(keys, (BASE_KEYS, sorted(BASE_KEYS + ["correlation_id"])), mod)
                    self.assertNotIn("error", env)  # the HTTP wrapper {"error": {...}} is not used on the CLI (addendum)

    # ------------------------------------------------------------------ DW-07
    def _adopt_dops(self, st, eff):
        r = st.zh("holder-1", "ZH-05", {"op": "adopt", "policy_id": "D-OPS", "from_version": 1, "effective_from": eff,
                                       "owner": "qa-owner-synthetic"})
        self.assertIn(r.status, (200, 201), r.text)

    def test_TST_HUB_STG20_S11_withdrawal_through_zone_h(self):
        """S11 (DW-07, FAC-13 proposed, BEH-POL-05): adopted D-OPS@2 withdrawn by a synthetic holder through ZH-10 -> one POLICY_WITHDRAWN
        policy event with authority_ref + holder_check_ref and one audit record; status report lists it as withdrawn; a metric computed after
        the withdrawal carries detail.policy_withdrawal; the value computed before it still reproduces exactly."""
        st = self.store(extra={"zone_h": {"holders": ["holder-1"]}})
        today = st.clock()[:10]
        self._adopt_dops(st, today)
        before = st.met.backlog_by_site("D-OPS", st.clock())
        self.assertEqual((before.policy_version, before.policy_status), ("D-OPS@2", "adopted"))
        self.assertNotIn("policy_withdrawal", before.detail)
        r = st.zh("holder-1", "ZH-10", {"op": "withdraw_policy", "policy_id": "D-OPS", "version": 2, "withdrawn_from": today,
                                        "reason": "synthetic withdrawal (test)"})
        self.assertIn(r.status, (200, 201), r.text)
        evs = st.pol.events("D-OPS@2", "POLICY_WITHDRAWN")
        self.assertEqual(len(evs), 1)
        self.assertEqual((evs[0]["authority_ref"], evs[0]["new_value"]["withdrawn_from"]), (W.AUTH, today))
        self.assertTrue(evs[0]["holder_check_ref"].startswith("audit:"))
        self.assertEqual(len(st.audit_actions("POLICY_WITHDRAWN")), 1)
        p = st.pol.get_policy("D-OPS", 2)
        self.assertEqual((p["status"], p["withdrawal"]["withdrawn_from"]), ("adopted", today))
        rep = st.pol.status_report()
        self.assertEqual([x["policy_ref"] for x in rep["withdrawn"]], ["D-OPS@2"])
        self.assertNotIn("D-OPS@2", [x["policy_ref"] for x in rep["adopted"]])
        after = st.met.backlog_by_site("D-OPS", st.clock())
        self.assertEqual(after.detail["policy_withdrawal"]["event_id"], evs[0]["event_id"])
        again = st.met.reproduce(before.value_id)
        self.assertTrue(again["equal"], again)

    def test_TST_HUB_STG20_S12_withdrawal_refusals_write_nothing(self):
        """S12 (DW-07): shipped empty holders -> E-GATE-NO-HOLDERS; non-holder -> E-GATE-NOT-AUTHORISED; empty authority_ref ->
        E-POL-AUTHORITY-REQUIRED; a candidate, a second withdrawal, a date before effective_from or a bad date -> E-POL-INVALID; none writes
        a POLICY_WITHDRAWN event."""
        st0 = self.store(extra={"zone_h": {"holders": []}})
        r = st0.zh("holder-1", "ZH-10", {"op": "withdraw_policy", "policy_id": "D-OPS", "version": 1, "withdrawn_from": "2030-01-01",
                                         "reason": "x"})
        self.assertEqual((r.status, r.code), (423, "E-GATE-NO-HOLDERS"), r.text)
        st = self.store(extra={"zone_h": {"holders": ["holder-1"]}})
        self._adopt_dops(st, "2030-01-01")
        n0 = st.count("policy_events", "event_type = 'POLICY_WITHDRAWN'")
        r = st.zh("nonholder", "ZH-10", {"op": "withdraw_policy", "policy_id": "D-OPS", "version": 2, "withdrawn_from": "2030-02-01",
                                         "reason": "x"})
        self.assertEqual(r.code, "E-GATE-NOT-AUTHORISED", r.text)
        h = st.reauth("holder-1")
        with self.assertRaises(AuthorityRequired):
            st.pol.withdraw(h, "D-OPS", 2, "2030-02-01", "reason", "  ")
        for args in (("D-EVID", 1, "2030-02-01", "candidate"), ("D-OPS", 2, "2029-12-31", "before effective_from"),
                     ("D-OPS", 2, "30/01/2030", "bad date"), ("D-OPS", 2, "2030-02-01", " ")):
            with self.assertRaises(PolicyInvalid, msg=args):
                st.pol.withdraw(st.reauth("holder-1"), args[0], args[1], args[2], args[3], AUTH)
        self.assertEqual(st.count("policy_events", "event_type = 'POLICY_WITHDRAWN'"), n0)
        st.pol.withdraw(st.reauth("holder-1"), "D-OPS", 2, "2030-02-01", "synthetic", AUTH)
        with self.assertRaises(PolicyInvalid):
            st.pol.withdraw(st.reauth("holder-1"), "D-OPS", 2, "2030-03-01", "again", AUTH)
        self.assertEqual(st.count("policy_events", "event_type = 'POLICY_WITHDRAWN'"), n0 + 1)

    def test_TST_HUB_STG20_S13_withdrawn_version_stops_applying(self):
        """S13 (DW-07, DEV-36): the overlap window of a withdrawn version ends at withdrawn_from (re-adoption before it is refused, from it
        accepted); an adopted clock with a duration gives a verdict until withdrawn, then none; a withdrawn CLOSURE policy no longer
        defines the closing states."""
        st = self.store(extra={"zone_h": {"holders": ["holder-1"]}})
        today = st.clock()[:10]
        st.pol.adopt(st.reauth("holder-1"), "D-FIN", 1, "2030-01-01", "fin-owner-synthetic", AUTH)
        st.pol.withdraw(st.reauth("holder-1"), "D-FIN", 2, "2030-06-01", "synthetic", AUTH)
        with self.assertRaises(Overlap):
            st.pol.adopt(st.reauth("holder-1"), "D-FIN", 1, "2030-05-31", "fin-owner-synthetic", AUTH)
        p = st.pol.adopt(st.reauth("holder-1"), "D-FIN", 1, "2030-06-01", "fin-owner-synthetic", AUTH)
        self.assertEqual((p["status"], p["version"]), ("adopted", 3))
        st.pol.adopt(st.reauth("holder-1"), "C-OPS", 1, today, "ops-owner-synthetic", AUTH, body_updates={"duration_hours": 48})
        case = [{"case_id": "CASE-S13", "events": {"FACT_RECEIVED": "2026-01-01T00:00:00Z", "FACT_OPS_CLOSED": "2026-01-02T00:00:00Z"}}]
        v = [x for x in st.pol.clock_report(case)[0]["clocks"] if x["policy_ref"] == "C-OPS@2"][0]
        self.assertEqual(v["verdict"], "within")
        st.pol.withdraw(st.reauth("holder-1"), "C-OPS", 2, today, "synthetic", AUTH)
        v = [x for x in st.pol.clock_report(case)[0]["clocks"] if x["policy_ref"] == "C-OPS@2"][0]
        self.assertEqual(v["verdict"], clocks.NO_POLICY)
        st.closure_policy()
        self.assertEqual(st.svc.closing_set()[1:], ("policy", "CL-1@2"))
        st.pol.withdraw(st.reauth("holder-1"), "CL-1", 2, today, "synthetic", AUTH)
        self.assertNotEqual(st.svc.closing_set()[1], "policy")

    # ------------------------------------------------------------------ DW-08
    def test_TST_HUB_STG20_S14_trace_producer(self):
        """S14 (DW-08, AC-REV-05/06/08 without record-trace): no active set and no --ruleset-ref -> E-POL-NO-ACTIVE-RULESET, nothing stored;
        what-if PRIORITY with as-found-python@1 over the 125 shipped cases -> one trace per case, explanation for a CLOSED case names the set,
        row and outcome 'archive', identical twice, with the three flag actions; a re-run stores nothing (idempotent); a MARS region case
        shows the defaulted marker (AMOUNT_LIMIT, as-found-js@1); the CLI command gives the same report."""
        st = self.store()
        st.load_rules()
        cases = producer.load_case_inputs(S.LEGACY_ROOT, S.tmpdir("s20s14-"))
        self.assertEqual(len(cases), 125)
        n0 = st.count("rule_trace")
        with self.assertRaises(NoActiveRuleset):
            producer.produce(st.con, st.s, st.clock, st.anchor, st.pol, cases, "PRIORITY")
        self.assertEqual(st.count("rule_trace"), n0)
        rep = producer.produce(st.con, st.s, st.clock, st.anchor, st.pol, cases, "PRIORITY", "as-found-python@1")
        self.assertEqual((rep["stored"], rep["no_case"], rep["input_invalid"], rep["authoritative"]), (125, 0, 0, False))
        closed = [c["case_id"] for c in cases if c["status"] == "CLOSED"][0]
        a = st.rev.explanations(st.sess("rev"), closed)["explanations"]
        b = st.rev.explanations(st.sess("rev"), closed)["explanations"]
        self.assertEqual(a, b)
        self.assertEqual(len(a), 1)
        self.assertIn("as-found-python@1", a[0]["text"])
        self.assertIn("archive", a[0]["text"])
        self.assertEqual(a[0]["actions"], ["override", "dismiss", "refuse"])
        again = producer.produce(st.con, st.s, st.clock, st.anchor, st.pol, cases, "PRIORITY", "as-found-python@1")
        self.assertEqual((again["stored"], again["unchanged"]), (0, 125))
        mars = [dict(cases[0], region="MARS")]
        m = producer.produce(st.con, st.s, st.clock, st.anchor, st.pol, mars, "AMOUNT_LIMIT", "as-found-js@1")
        self.assertEqual(m["stored"], 1)
        ex = [x for x in st.rev.explanations(st.sess("rev"), cases[0]["case_id"])["explanations"] if x["function"] == "AMOUNT_LIMIT"][0]
        self.assertTrue(ex["defaulted"])
        self.assertIn("defaulted: ", ex["text"])
        p = subprocess.run([sys.executable, "-B", "-m", "hub.web", "--config", st.cfg_path, "produce-traces", "--data-dir", st.data,
                            "--legacy-root", S.LEGACY_ROOT, "--function", "PRIORITY", "--ruleset-ref", "as-found-python@1"],
                           cwd=S.CODE_ROOT, env=S.child_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        out = json.loads(p.stdout)
        self.assertEqual((out["stored"], out["unchanged"]), (0, 125))

    def test_TST_HUB_STG20_S15_flags_of_produced_traces_and_unmatched_items(self):
        """S15 (DW-08, AC-GATE-18/19, RTD-69): override of a produced trace's flag -> OVERRIDE_RECORDED on the case, original result unchanged,
        empty reason refused; a flag action on an unmatched intake item (no case) is retrievable as a trail with its audit record."""
        st = self.store()
        st.load_rules()
        cases = producer.load_case_inputs(S.LEGACY_ROOT, S.tmpdir("s20s15-"))[:3]
        rep = producer.produce(st.con, st.s, st.clock, st.anchor, st.pol, cases, "PRIORITY", "as-found-python@1")
        tid = rep["trace_ids"][0]
        fid, case_id, result = st.con.execute("SELECT flag_id, case_id, result FROM rule_trace WHERE trace_id = ?", (tid,)).fetchone()
        from hub.gate.disposition_errors import GateReasonRequired
        with self.assertRaises(GateReasonRequired):
            st.disp.act_on_flag(st.sess("rev"), fid, "override", "  ")
        out = st.disp.act_on_flag(st.sess("rev"), fid, "override", "not applicable (synthetic)")
        self.assertTrue(out["original_output_retained"])
        self.assertEqual(st.con.execute("SELECT result FROM rule_trace WHERE trace_id = ?", (tid,)).fetchone()[0], result)
        self.assertEqual(st.con.execute("SELECT event_type FROM decision_events WHERE event_id = ?", (out["event_id"],)).fetchone()[0],
                         "OVERRIDE_RECORDED")
        st.isvc.ingest("partner_feed", [I.feed(900001, ref_id="C99999999")], "s20s15", "s20s15")
        raw, seq = st.con.execute("SELECT raw_id, outcome_seq FROM intake_current WHERE queue = 'unmatched' ORDER BY raw_id DESC LIMIT 1").fetchone()
        iq = "FLG-IQ-%s-%d" % (raw, seq)
        res = st.disp.act_on_flag(st.sess("rev"), iq, "dismiss", "synthetic: no such case")
        trail = producer.flag_trail(st.con, iq)
        self.assertEqual(len(trail), 1)
        self.assertEqual((trail[0]["action_id"], trail[0]["case_id"], trail[0]["case_event_id"]), (res["action_id"], None, None))
        self.assertIsNotNone(trail[0]["audit_seq"])
        self.assertEqual(trail[0]["reason"], {"text": "synthetic: no such case", "trust": "untrusted"})


if __name__ == "__main__":
    unittest.main()
