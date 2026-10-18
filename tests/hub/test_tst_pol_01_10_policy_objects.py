"""TST-POL-01..10 (AC-POL-01..10, FR-POL-01/02/03, BEH-POL-01..05; class A; fixtures FX-UNIT-SYNTHETIC temp store) -
versioned policy objects, adoption through Zone H, overlap refusal, accepted-open, clocks and verdicts, authority_ref
and change events. Every policy used here is an explicitly synthetic TEST policy in a private sandbox store; none ships adopted.
"""
import json
import unittest

import _support as S
import _inc04 as P
from hub.policy.errors import (AuthorityRequired, ClockCalendarRequired, GateNotAuthorised, Overlap, PolicyInvalid,
                               ReadonlySet)
from hub.security.errors import AuthForbidden

T0 = "2026-03-01T00:00:00Z"
AUTH = "TEST-AUTH-1 (synthetic)"


def setUpModule():
    S.require_sandbox()


class TST_POL_PolicyObjects(unittest.TestCase):

    def setUp(self):
        self.st = P.PStore()
        self.svc = self.st.svc

    def tearDown(self):
        self.st.close()

    # ---- AC-POL-01
    def test_TST_POL_01_fresh_install_five_candidates_none_adopted(self):
        """TST-POL-01 / AC-POL-01: exactly three DEFINITION and two CLOCK objects, all candidate, owner unassigned; adopted = 0."""
        pols = self.svc.list_policies()
        self.assertEqual(sorted((p["kind"], p["policy_id"]) for p in pols),
                         [("CLOCK", "C-EVID"), ("CLOCK", "C-OPS"), ("DEFINITION", "D-EVID"), ("DEFINITION", "D-FIN"), ("DEFINITION", "D-OPS")])
        self.assertEqual({(p["status"], p["owner"], p["version"], p["created_by"]) for p in pols}, {("candidate", "unassigned", 1, "seed")})
        self.assertEqual(self.svc.list_policies(status="adopted"), [])
        self.assertEqual(self.svc.active(), {})
        self.assertEqual(self.svc.list_rulesets(), [])
        self.assertEqual([e["event_type"] for e in self.svc.events()], ["POLICY_VERSION_CREATED"] * 5)
        self.assertEqual(self.svc.seed(), [])  # idempotent
        self.assertEqual(self.st.verify()["status"], "ok")

    # ---- AC-POL-02
    def test_TST_POL_02_service_actor_cannot_adopt(self):
        """TST-POL-02 / AC-POL-02: a service-actor request to adopt D-OPS is rejected E-GATE-NOT-AUTHORISED, audited; still candidate."""
        before = self.st.counts()
        for who in (self.st.service_session(), self.st.sess("nonholder"), self.st.sess("rev")):
            with self.assertRaises(GateNotAuthorised) as cm:
                self.svc.adopt(who, "D-OPS", 1, "2026-01-01", "ops-owner", AUTH)
            self.assertEqual(cm.exception.code, "E-GATE-NOT-AUTHORISED")
        self.assertEqual(self.svc.get_policy("D-OPS")["status"], "candidate")
        after = self.st.counts()
        for t in ("policy_object", "policy_events"):
            self.assertEqual(after[t], before[t])
        att = [a for a in self.st.audit_actions("ZONE_H_ATTEMPT") if a["outcome"] == "denied"]
        self.assertEqual([(a["actor"], a["actor_kind"]) for a in att], [("svc-integration", "service"), ("nonholder", "human"), ("rev", "human")])
        self.assertEqual({a["details"]["zh"] for a in att}, {"ZH-05"})

    # ---- AC-POL-03
    def test_TST_POL_03_holder_adopts_with_authority(self):
        """TST-POL-03 / AC-POL-03: a holder adopts D-OPS -> new version adopted; POLICY_ADOPTED event with old/new and authority_ref."""
        p = self.svc.adopt(self.st.sess("holder-1"), "D-OPS", 1, "2026-01-01", "ops-owner", AUTH, effective_to="2026-12-31")
        self.assertEqual((p["version"], p["status"], p["owner"], p["effective_from"], p["effective_to"]),
                         (2, "adopted", "ops-owner", "2026-01-01", "2026-12-31"))
        self.assertEqual(self.svc.get_policy("D-OPS", 1)["status"], "candidate")  # old version untouched
        ev = self.svc.events("D-OPS@2")
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["event_type"], e["actor"], e["authority_ref"]), ("POLICY_ADOPTED", "holder-1", AUTH))
        self.assertEqual(e["old_value"]["status"], "candidate")
        self.assertEqual(e["new_value"]["status"], "adopted")
        self.assertTrue(e["holder_check_ref"].startswith("audit:"))
        rec = [a for a in self.st.audit_actions("POLICY_ADOPTED")]
        self.assertEqual((len(rec), rec[0]["outcome"], rec[0]["details"]["event_id"]), (1, "success", e["event_id"]))
        self.assertEqual(self.st.verify()["status"], "ok")

    # ---- AC-POL-04
    def test_TST_POL_04_overlapping_adoption_refused(self):
        """TST-POL-04 / AC-POL-04: a second adoption with an overlapping window for the same tag -> E-POL-OVERLAP; disjoint window succeeds."""
        h = self.st.sess("holder-1")
        self.svc.adopt(h, "D-OPS", 1, "2026-01-01", "ops-owner", AUTH, effective_to="2026-12-31")
        before = self.st.counts()
        for frm, to in (("2026-06-01", "2027-06-30"), ("2026-12-31", None), ("2025-01-01", "2026-01-01"), ("2026-02-01", "2026-03-01")):
            with self.assertRaises(Overlap) as cm:
                self.svc.adopt(h, "D-OPS", 1, frm, "ops-owner", AUTH, effective_to=to)
            self.assertEqual(cm.exception.code, "E-POL-OVERLAP")
        self.assertEqual(self.st.counts()["policy_object"], before["policy_object"])
        self.assertEqual(self.st.counts()["policy_events"], before["policy_events"])
        ok = self.svc.adopt(h, "D-OPS", 1, "2027-01-01", "ops-owner", AUTH)
        self.assertEqual((ok["version"], ok["status"]), (3, "adopted"))
        self.svc.adopt(h, "D-EVID", 1, "2026-01-01", "evid-owner", AUTH)  # another tag: no clash with D-OPS

    # ---- AC-POL-05
    def test_TST_POL_05_accepted_open_is_not_adopted(self):
        """TST-POL-05 / AC-POL-05: 'accepted-open' for D-FIN with a reason: dated event; the report lists it as accepted-open, not adopted."""
        h = self.st.sess("holder-1")
        with self.assertRaises(PolicyInvalid):
            self.svc.accept_open(h, "D-FIN", 1, "  ", AUTH)
        p = self.svc.accept_open(h, "D-FIN", 1, "Finance has not defined 'resolved'; decision deferred (synthetic)", AUTH)
        self.assertEqual((p["status"], p["version"]), ("accepted-open", 2))
        self.assertEqual(p["body"]["accepted_open"]["reason"], "Finance has not defined 'resolved'; decision deferred (synthetic)")
        e = self.svc.events("D-FIN@2")[0]
        self.assertEqual((e["event_type"], e["authority_ref"]), ("POLICY_ACCEPTED_OPEN", AUTH))
        self.assertTrue(e["new_value"]["dated"].endswith("Z"))
        rep = self.svc.status_report()
        self.assertEqual([x["policy_ref"] for x in rep["accepted-open"]], ["D-FIN@2"])
        self.assertNotIn("D-FIN", " ".join(x["policy_ref"] for x in rep["adopted"]))
        self.assertEqual(self.svc.list_policies(status="adopted"), [])

    # ---- AC-POL-06
    def test_TST_POL_06_elapsed_under_both_clocks_no_verdict(self):
        """TST-POL-06 / AC-POL-06: two cases: elapsed under C-OPS and C-EVID side by side; verdict not_available_no_adopted_policy; no pass/fail."""
        cases = [{"case_id": "CASE-1", "events": {"FACT_RECEIVED": T0, "FACT_OPS_CLOSED": "2026-03-01T10:00:00Z",
                                                  "FACT_EVIDENCE_COMPLETE": "2026-03-03T02:00:00Z"}},
                 {"case_id": "CASE-2", "events": {"FACT_RECEIVED": T0, "FACT_OPS_CLOSED": "2026-03-01T01:30:00Z"}}]
        rep = self.svc.clock_report(cases)
        self.assertEqual([c["case_id"] for c in rep], ["CASE-1", "CASE-2"])
        by = {c["case_id"]: {x["policy_ref"]: x for x in c["clocks"]} for c in rep}
        self.assertEqual(sorted(by["CASE-1"]), ["C-EVID@1", "C-OPS@1"])
        self.assertEqual((by["CASE-1"]["C-OPS@1"]["elapsed_hours"], by["CASE-1"]["C-EVID@1"]["elapsed_hours"]), ("10", "50"))
        self.assertEqual((by["CASE-2"]["C-OPS@1"]["elapsed_hours"], by["CASE-2"]["C-EVID@1"]["elapsed_hours"]), ("1.5", None))
        for c in rep:
            for x in c["clocks"]:
                self.assertEqual((x["verdict"], x["status"], x["boundary_rule"]), ("not_available_no_adopted_policy", "candidate", None))
        text = json.dumps(rep)
        self.assertNotIn("within", text.replace("not_available_no_adopted_policy", ""))

    # ---- AC-POL-07
    def test_TST_POL_07_business_calendar_needs_calendar_ref(self):
        """TST-POL-07 / AC-POL-07: CLOCK with calendar_basis business_calendar and no calendar_ref -> E-POL-CLOCK-CALENDAR-REQUIRED; nothing stored."""
        ql = self.st.sess("ql")
        body = {"clock_start_event": "FACT_RECEIVED", "clock_stop_event": "FACT_OPS_CLOSED", "duration_hours": None,
                "calendar_basis": "business_calendar"}
        before = self.st.counts()
        for ref in (None, "", "   "):
            with self.assertRaises(ClockCalendarRequired) as cm:
                self.svc.create_candidate(ql, "C-BIZ", "CLOCK", "business-hours clock (test)", dict(body, calendar_ref=ref), AUTH)
            self.assertEqual(cm.exception.code, "E-POL-CLOCK-CALENDAR-REQUIRED")
        self.assertEqual(self.st.counts()["policy_object"], before["policy_object"])
        self.assertEqual(self.st.counts()["policy_events"], before["policy_events"])
        p = self.svc.create_candidate(ql, "C-BIZ", "CLOCK", "business-hours clock (test)", dict(body, calendar_ref="CAL-TEST"), AUTH)
        self.assertEqual((p["version"], p["status"], p["created_by"]), (1, "candidate", "ql"))

    # ---- AC-POL-08
    def test_TST_POL_08_adopted_clock_verdicts_at_the_boundary(self):
        """TST-POL-08 / AC-POL-08: adopted clock with duration 48: 47.9 h within, 48.0 h within (inclusive), 48.1 h not within; boundary rule stated."""
        h = self.st.sess("holder-1")
        p = self.svc.adopt(h, "C-OPS", 1, "2026-01-01", "ops-owner", AUTH, body_updates={"duration_hours": 48})
        self.assertEqual((p["status"], p["body"]["duration_hours"]), ("adopted", 48))
        def case(cid, stop):
            return {"case_id": cid, "events": {"FACT_RECEIVED": T0, "FACT_OPS_CLOSED": stop, "FACT_EVIDENCE_COMPLETE": stop}}
        rep = self.svc.clock_report([case("A", "2026-03-02T23:54:00Z"), case("B", "2026-03-03T00:00:00Z"), case("C", "2026-03-03T00:06:00Z")])
        ops = {c["case_id"]: [x for x in c["clocks"] if x["policy_ref"].startswith("C-OPS")][0] for c in rep}
        self.assertEqual([(ops[k]["elapsed_hours"], ops[k]["verdict"]) for k in "ABC"],
                         [("47.9", "within"), ("48", "within"), ("48.1", "not_within")])
        self.assertEqual({ops[k]["boundary_rule"] for k in "ABC"}, {"elapsed_hours <= duration_hours (inclusive)"})
        evid = [x for x in rep[0]["clocks"] if x["policy_ref"].startswith("C-EVID")][0]
        self.assertEqual(evid["verdict"], "not_available_no_adopted_policy")  # the other clock is still a candidate

    # ---- AC-POL-09
    def test_TST_POL_09_empty_authority_ref_stores_nothing(self):
        """TST-POL-09 / AC-POL-09: every policy / rule-row edit with an empty authority_ref -> E-POL-AUTHORITY-REQUIRED; no row is stored."""
        st = P.PStore(loaded=True)
        try:
            svc, h, ql = st.svc, st.sess("holder-1"), st.sess("ql")
            custom = svc.fork_as_custom(ql, "as-found-js@1", "custom-js", AUTH)
            dec = svc.record_activation_decision(h, "PRIORITY", "as-found-python@1", AUTH, "test decision (synthetic)")["decision_seq"]
            actions = [
                lambda a: svc.create_candidate(ql, "D-NEW", "DEFINITION", "n", {"text": "t"}, a),
                lambda a: svc.adopt(h, "D-OPS", 1, "2026-01-01", "ops-owner", a),
                lambda a: svc.accept_open(h, "D-FIN", 1, "reason", a),
                lambda a: svc.edit_rule_row(h, custom, "JS-13", a, outcome_updates={"value": 26000}),
                lambda a: svc.fork_as_custom(ql, "as-found-python@1", "custom-py", a),
                lambda a: svc.record_activation_decision(h, "AMOUNT_LIMIT", "as-found-js@1", a, "r"),
                lambda a: svc.activate(h, "PRIORITY", "as-found-python@1", a, dec),
                lambda a: svc.deactivate(h, "PRIORITY", a),
            ]
            for i, act in enumerate(actions):
                for empty in ("", "   ", None):
                    before = {k: v for k, v in st.counts().items() if k != "audit_log"}
                    with self.assertRaises(AuthorityRequired, msg=(i, empty)) as cm:
                        act(empty)
                    self.assertEqual(cm.exception.code, "E-POL-AUTHORITY-REQUIRED")
                    self.assertEqual({k: v for k, v in st.counts().items() if k != "audit_log"}, before, (i, empty))
            self.assertEqual(st.svc.active(), {})
        finally:
            st.close()

    # ---- AC-POL-10
    def test_TST_POL_10_threshold_edit_event_and_service_actor_rejected(self):
        """TST-POL-10 / AC-POL-10: a holder's threshold edit leaves ONE event (who, when, old, new, authority_ref); a service actor is rejected and logged."""
        st = P.PStore(loaded=True)
        try:
            svc = st.svc
            custom = svc.fork_as_custom(st.sess("ql"), "as-found-js@1", "custom-js", AUTH)
            self.assertEqual(custom, "custom-js@1")
            rows = [r for r in svc.get_ruleset(custom)["rows"] if r["conditions"] == [{"field": "region", "op": "eq", "value": "APAC"},
                                                                                      {"field": "year", "op": "eq", "value": "2026"}]]
            self.assertEqual(len(rows), 1)
            rid = rows[0]["row_id"]
            self.assertEqual(rows[0]["outcome"]["value"], 25000)
            sv = st.service_session()
            n_events = st.counts()["policy_events"]
            with self.assertRaises(GateNotAuthorised):
                svc.edit_rule_row(sv, custom, rid, AUTH, outcome_updates={"value": 26000})
            self.assertEqual(st.counts()["policy_events"], n_events)
            self.assertEqual([a["actor"] for a in st.audit_actions("ZONE_H_ATTEMPT") if a["outcome"] == "denied" and a["details"]["zh"] == "ZH-10"],
                             ["svc-integration"])
            new_ref = svc.edit_rule_row(st.sess("holder-1"), custom, rid, "CHG-TEST-7 (synthetic)", outcome_updates={"value": 26000})
            self.assertEqual(new_ref, "custom-js@2")
            ev = svc.events(new_ref, "RULE_ROW_CHANGED")
            self.assertEqual(len(ev), 1)
            e = ev[0]
            self.assertEqual((e["actor"], e["authority_ref"], e["old_value"]["outcome"]["value"], e["new_value"]["outcome"]["value"]),
                             ("holder-1", "CHG-TEST-7 (synthetic)", 25000, 26000))
            self.assertTrue(e["occurred_at"].endswith("Z"))
            self.assertEqual(svc.get_ruleset(custom)["rows"][int(rid.split("-")[1]) - 1]["outcome"]["value"], 25000)  # v1 immutable
            self.assertEqual(svc.evaluate("AMOUNT_LIMIT", {"amount": 27300, "region": "APAC", "year": 2026}, "custom-js@2")["outcome"]["allowed"], True)
            self.assertEqual(svc.evaluate("AMOUNT_LIMIT", {"amount": 27300.01, "region": "APAC", "year": 2026}, "custom-js@2")["outcome"]["allowed"], False)
            self.assertEqual(svc.evaluate("AMOUNT_LIMIT", {"amount": 27300, "region": "APAC", "year": 2026}, "custom-js@1")["outcome"]["allowed"], False)
            self.assertEqual(st.verify()["status"], "ok")
        finally:
            st.close()


if __name__ == "__main__":
    unittest.main()
