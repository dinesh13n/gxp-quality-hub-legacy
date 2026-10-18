"""TST-DEC-01..14 (AC-DEC-01..14; FR-DEC-01..04; class A) - the append-only decision and evidence record: gapless immutable
events, trigger-enforced immutability, introspection (no update / delete method), projection = fold of events over the 125
backfilled legacy cases, as-of reads, creation event semantics, time order, explicit REOPEN, the REOPEN invariant with the
8 marked legacy cases, evidence resolution (dangling flagged, never omitted), access redaction and evidence coverage.
Synthetic cases and holders, unvalidated. Fixtures: FX-BASE125 (hash-gated sandbox copy) for DEC-05 / DEC-11.
"""
import datetime
import os
import re
import sqlite3
import unittest

import _support as S
import _inc05 as D
from hub.decision import errors as E
from hub.decision.service import DecisionService
from hub.security.canonical import fmt, parse


def setUpModule():
    D.skip_in_inner_egress_run()


def plus(ts, **kw):
    return fmt(parse(ts) + datetime.timedelta(**kw))


class TST_DEC_01_14_Record(unittest.TestCase):

    def setUp(self):
        self.ds = None

    def tearDown(self):
        if self.ds is not None:
            self.ds.close()

    def store(self, **kw):
        self.ds = D.DStore(**kw)
        return self.ds

    def test_TST_DEC_01_gapless_seq_no_row_modified(self):
        """TST-DEC-01 / AC-DEC-01: 5 successful transitions -> creation + 5 state events, seq 1..6 gapless, row hashes unchanged between reads."""
        ds = self.store()
        ds.mk("C00000001")
        for to in ("UNDER_REVIEW", "ESCALATED", "OPEN", "UNDER_REVIEW", "ESCALATED"):
            ds.move("C00000001", to)
        evs = ds.svc.events(ds.sess("rev"), "C00000001")
        self.assertEqual([e["seq"] for e in evs], [1, 2, 3, 4, 5, 6])
        self.assertEqual([e["event_type"] for e in evs], ["CASE_CREATED"] + ["STATUS_CHANGE"] * 5)
        first = ds.event_rows("C00000001")
        ds.mk("C00000002")
        ds.move("C00000002", "UNDER_REVIEW")
        self.assertEqual(ds.event_rows("C00000001"), first)
        self.assertEqual(ds.svc.verify_chain(), {"status": "ok", "cases": 2, "events": 8})

    def test_TST_DEC_02_raw_update_rejected(self):
        """TST-DEC-02 / AC-DEC-02: a raw UPDATE of decision_events fails with E-DEC-IMMUTABLE and the row is unchanged."""
        ds = self.store()
        ds.mk("C00000001")
        before = ds.event_rows("C00000001")
        with self.assertRaises(sqlite3.DatabaseError) as cm:
            ds.con.execute("UPDATE decision_events SET basis = 'x' WHERE case_id = 'C00000001'")
        ds.con.rollback()
        self.assertIn("E-DEC-IMMUTABLE", str(cm.exception))
        self.assertEqual(ds.event_rows("C00000001"), before)

    def test_TST_DEC_03_raw_delete_rejected(self):
        """TST-DEC-03 / AC-DEC-03 (PNFR-10): a raw DELETE FROM decision_events fails with E-DEC-IMMUTABLE; hold-all, nothing removed."""
        ds = self.store()
        ds.mk("C00000001")
        n = ds.counts()["decision_events"]
        with self.assertRaises(sqlite3.DatabaseError) as cm:
            ds.con.execute("DELETE FROM decision_events")
        ds.con.rollback()
        self.assertIn("E-DEC-IMMUTABLE", str(cm.exception))
        self.assertEqual(ds.counts()["decision_events"], n)

    def test_TST_DEC_04_no_update_or_delete_method(self):
        """TST-DEC-04 / AC-DEC-04: introspection - no public method of DecisionService is named or behaves as update/delete of an
        event, and the product code contains exactly one INSERT into decision_events and no UPDATE / DELETE of it."""
        names = [n for n in dir(DecisionService) if not n.startswith("_") and callable(getattr(DecisionService, n))]
        self.assertIn("transition", names)
        bad = [n for n in names if re.search(r"update|delete|remove|edit|modify|overwrite|erase|purge|drop|amend|rewrite", n)]
        self.assertEqual(bad, [])
        inserts, mutating = [], []
        for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            for fn in fns:
                if not fn.endswith(".py"):
                    continue
                text = open(os.path.join(d, fn), encoding="utf-8").read()
                inserts += [fn for _ in re.finditer(r"INSERT\s+(?:OR\s+\w+\s+)?INTO\s+decision_events\b", text)]
                mutating += [fn for _ in re.finditer(r"(?i)(UPDATE\s+decision_events\b|DELETE\s+FROM\s+decision_events\b)", text)]
        self.assertEqual(inserts, ["service.py"])
        self.assertEqual(mutating, [])

    def test_TST_DEC_05_projection_equals_fold_125_cases(self):
        """TST-DEC-05 / AC-DEC-05 (PNFR-17): over the 125 imported legacy cases plus later transitions verify-projection finds 0 mismatches."""
        ds = self.store(loaded=True)
        rep = ds.svc.verify_projection()
        self.assertEqual((rep["cases"], rep["projection_rows"], rep["mismatches"]), (125, 125, 0))
        ds.move("C00000003", "UNDER_REVIEW")
        ds.svc.transition(ds.sess("ql"), "C00000001", "REOPENED", "synthetic reopening basis", event_type="REOPEN", correlation_id="t-ro")
        rep = ds.svc.verify_projection()
        self.assertEqual((rep["cases"], rep["mismatches"]), (125, 0))
        c1 = ds.svc.state(ds.sess("rev"), "C00000001")
        self.assertEqual((c1["state"], c1["cycle"]), ("REOPENED", 2))
        self.assertEqual(ds.svc.state(ds.sess("rev"), "C00000003")["state"], "UNDER_REVIEW")
        self.assertEqual(ds.svc.verify_chain()["status"], "ok")

    def test_TST_DEC_06_as_of(self):
        """TST-DEC-06 / AC-DEC-06: events at t1<t2<t3 with states A,B,C: as_of t2 and t2+epsilon -> B; just before t1 -> E-DEC-NOT-YET-EXISTS."""
        ds = self.store()
        t1, t2, t3 = ds.ago(hours=3), ds.ago(hours=2), ds.ago(hours=1)
        ds.mk("C00000001", state="OPEN", occurred_at=t1)
        ds.move("C00000001", "UNDER_REVIEW", occurred_at=t2)
        ds.move("C00000001", "ESCALATED", occurred_at=t3)
        rev = ds.sess("rev")
        st = lambda t: ds.svc.state(rev, "C00000001", as_of=t)["state"]
        self.assertEqual(st(t2), "UNDER_REVIEW")
        self.assertEqual(st(plus(t2, microseconds=1)), "UNDER_REVIEW")
        self.assertEqual(st(t1), "OPEN")
        self.assertEqual(st(t3), "ESCALATED")
        self.assertEqual(st(plus(t3, hours=5)), "ESCALATED")
        with self.assertRaises(E.NotYetExists):
            st(plus(t1, microseconds=-1))
        self.assertEqual(ds.svc.state(rev, "C00000001")["state"], "ESCALATED")

    def test_TST_DEC_07_creation_event_keeps_creation_state(self):
        """TST-DEC-07 / AC-DEC-07: after the case moved to CLOSED the CASE_CREATED event still has from_state null, to_state = creation state."""
        ds = self.store()
        ds.mk("C00000001", state="OPEN")
        ds.close_with_evidence("C00000001")
        self.assertEqual(ds.svc.state(ds.sess("rev"), "C00000001")["state"], "CLOSED")
        first = ds.svc.events(ds.sess("rev"), "C00000001")[0]
        self.assertEqual((first["event_type"], first["from_state"], first["to_state"]), ("CASE_CREATED", None, "OPEN"))

    def test_TST_DEC_08_time_order(self):
        """TST-DEC-08 / AC-DEC-08: occurred_at in the future, or earlier than the previous event -> E-DEC-TIME-ORDER, nothing stored."""
        ds = self.store()
        ds.mk("C00000001")
        n = ds.counts()["decision_events"]
        with self.assertRaises(E.TimeOrder):
            ds.move("C00000001", "UNDER_REVIEW", occurred_at=plus(ds.now(), hours=1))
        with self.assertRaises(E.TimeOrder):
            ds.move("C00000001", "UNDER_REVIEW", occurred_at=ds.ago(hours=5))
        with self.assertRaises(E.TimeOrder):
            ds.move("C00000001", "UNDER_REVIEW", occurred_at="yesterday")
        self.assertEqual(ds.counts()["decision_events"], n)
        self.assertEqual(ds.svc.state(ds.sess("rev"), "C00000001")["state"], "OPEN")

    def test_TST_DEC_09_reopen_needs_reopen_event(self):
        """TST-DEC-09 / AC-DEC-09: CLOSED -> REOPENED posted as STATUS_CHANGE is refused E-DEC-REOPEN-EXPLICIT."""
        ds = self.store()
        ds.mk("C00000001")
        ds.close_with_evidence("C00000001")
        n = ds.counts()["decision_events"]
        with self.assertRaises(E.ReopenExplicit):
            ds.move("C00000001", "REOPENED", event_type="STATUS_CHANGE")
        self.assertEqual(ds.counts()["decision_events"], n)
        self.assertEqual(ds.svc.state(ds.sess("rev"), "C00000001")["state"], "CLOSED")

    def test_TST_DEC_10_reopen_increments_cycle(self):
        """TST-DEC-10 / AC-DEC-10: a REOPEN event with a non-empty basis is accepted: state REOPENED, cycle 1 -> 2; an empty basis is refused."""
        ds = self.store()
        ds.mk("C00000001")
        ds.close_with_evidence("C00000001")
        self.assertEqual(ds.svc.state(ds.sess("rev"), "C00000001")["cycle"], 1)
        with self.assertRaises(E.ReopenExplicit):
            ds.svc.transition(ds.sess("rev"), "C00000001", "REOPENED", "   ", event_type="REOPEN", correlation_id="t-ro")
        ev = ds.svc.transition(ds.sess("rev"), "C00000001", "REOPENED", "new finding after closure (synthetic)", event_type="REOPEN",
                               correlation_id="t-ro")
        self.assertEqual((ev["event_type"], ev["to_state"], ev["cycle"]), ("REOPEN", "REOPENED", 2))
        st = ds.svc.state(ds.sess("rev"), "C00000001")
        self.assertEqual((st["state"], st["cycle"]), ("REOPENED", 2))

    def test_TST_DEC_11_reopen_invariant_lists_marked_legacy_cases(self):
        """TST-DEC-11 / AC-DEC-11: REOPENED cases lacking a REOPEN event, excluding LEGACY_UNEVIDENCED_REOPEN-marked legacy imports: 0;
        the 8 marked legacy cases are listed separately; a planted violation IS reported (control)."""
        ds = self.store(loaded=True)
        ql = ds.sess("ql")
        inv = ds.svc.reopen_invariant(ql)
        self.assertEqual(inv["violation_count"], 0)
        self.assertEqual(inv["marked_count"], 8)
        self.assertEqual(len(inv["marked_legacy"]), 8)
        self.assertEqual(len(set(inv["marked_legacy"])), 8)
        ds.svc.transition(ds.sess("rev"), "C00000001", "REOPENED", "synthetic reopening basis", event_type="REOPEN", correlation_id="t-ro")
        self.assertEqual(ds.svc.reopen_invariant(ql)["violation_count"], 0)
        ds.con.execute("UPDATE case_state SET state = 'REOPENED' WHERE case_id = 'C00000003'")  # projection only: planted defect
        ds.con.commit()
        inv = ds.svc.reopen_invariant(ql)
        self.assertEqual(inv["violations"], ["C00000003"])
        self.assertEqual(inv["marked_count"], 8)
        self.assertEqual(ds.svc.verify_projection()["mismatches"], 1)

    def test_TST_DEC_12_dangling_evidence_flagged_not_omitted(self):
        """TST-DEC-12 / AC-DEC-12: an event with two evidence refs (one resolvable, one dangling): OP-DEC-04 returns the event, the resolved
        evidence with its source, and the dangling one flagged `unresolvable`."""
        ds = self.store()
        ds.mk("C00000001")
        ev1 = ds.evidence("C00000001", level="quality")
        ev = ds.move("C00000001", "UNDER_REVIEW", evidence_refs=[ev1, "EVD-99999999"])
        got = ds.svc.event_with_evidence(ds.sess("rev"), ev["event_id"])
        self.assertEqual(got["event"]["event_id"], ev["event_id"])
        self.assertEqual([x["ev_id"] for x in got["evidence"]], [ev1, "EVD-99999999"])
        self.assertEqual(got["evidence"][0]["source"], {"text": "synthetic-source", "trust": "untrusted"})
        self.assertEqual(got["evidence"][0]["kind"], "document")
        self.assertEqual(got["evidence"][1], {"ev_id": "EVD-99999999", "unresolvable": True})

    def test_TST_DEC_13_restricted_evidence_redacted(self):
        """TST-DEC-13 / AC-DEC-13: restricted evidence for a caller without access appears as {ev_id, access: denied} with no body or source text."""
        ds = self.store()
        ds.mk("C00000001")
        ev1 = ds.evidence("C00000001", level="restricted", ref="confidential synthetic reference")
        ev = ds.move("C00000001", "UNDER_REVIEW", evidence_refs=[ev1])
        denied = ds.svc.event_with_evidence(ds.sess("rev"), ev["event_id"])["evidence"]
        self.assertEqual(denied, [{"ev_id": ev1, "access": "denied"}])
        self.assertNotIn("confidential", repr(denied))
        allowed = ds.svc.event_with_evidence(ds.sess("ql"), ev["event_id"])["evidence"][0]
        self.assertEqual((allowed["ev_id"], allowed["access_level"]), (ev1, "restricted"))
        self.assertEqual(allowed["source_ref"]["text"], "confidential synthetic reference")

    def test_TST_DEC_14_closing_events_have_evidence_or_exception_marker(self):
        """TST-DEC-14 / AC-DEC-14: a sample of 20 closing decision events (10 with evidence, 10 via holder exceptions): 100% have evidence and
        source retrievable or an explicit exception marker."""
        ds = self.store()
        ids = []
        for i in range(1, 21):
            cid = "C%08d" % i
            ds.mk(cid)
            if i <= 10:
                ev = ds.evidence(cid)
                ids.append(ds.move(cid, "CLOSED", evidence_refs=[ev])["event_id"])
            else:
                ids.append(ds.svc.transition(ds.sess("holder-1"), cid, "CLOSED", "closure by exception (synthetic)",
                                             close_exception={"authority": "TEST-AUTH-14 (synthetic)", "reason": "synthetic exception"},
                                             correlation_id="t-exc")["event_id"])
        rep = ds.svc.evidence_coverage(ds.sess("ql"), ids)
        self.assertEqual(rep["events"], 20)
        self.assertEqual((len(rep["covered"]), len(rep["exception_marked"]), rep["uncovered"]), (10, 10, []))
        self.assertEqual(rep["coverage_pct"], 100.0)
        for eid in rep["covered"]:
            got = ds.svc.event_with_evidence(ds.sess("ql"), eid)
            self.assertTrue(got["evidence"] and "source" in got["evidence"][0])


if __name__ == "__main__":
    unittest.main()
