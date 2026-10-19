"""TST-INT-01, 03, 04, 05, 06, 07, 08 (AC-INT-01, 03..08; FR-INT-01/02/03; PNFR-11; class A except TST-INT-06 = B (OD-S12-17, decided OD-18)
and TST-INT-07 = C (synthetic corrected-replay fixture, FND-INT-1)): append-only raw store, never an update of a status column, replay
safety, the natural-key pairs of the shipped data, business_key is not an identity, corrected replay -> REVISED_CONFLICT, human resolution.
Shipped-data checks read the hash-gated FX-BASE125 sandbox copy. Synthetic, unvalidated.
"""
import os
import re
import unittest

import _support as S
import _inc06 as I
from hub.core.errors import LegacyWriteRefused
from hub.intake import errors as E, replay
from hub.security.errors import AuthForbidden


def setUpModule():
    I.skip_in_inner_egress_run()


def rawid(n):
    return "RAW-%010d" % n


class TST_INT_01_08_Core(unittest.TestCase):

    def setUp(self):
        self.st = None

    def tearDown(self):
        if self.st is not None:
            self.st.close()

    def store(self, **kw):
        self.st = I.IStore(**kw)
        return self.st

    def test_TST_INT_01_every_delivery_stored_raw_rows_unchanged(self):
        """TST-INT-01 / AC-INT-01: 100 valid items, job run twice -> 200 raw rows, the original 100 byte-unchanged, outcomes of both runs kept."""
        st = self.store()
        items = I.batch(100)
        r1 = st.isvc.ingest("partner_feed", items, "t01-run1", "t01")
        self.assertEqual((r1["stored"], r1["outcomes"]), (100, {"VALIDATED": 100}))
        self.assertEqual(r1["linked"], 100)
        before = st.con.execute("SELECT * FROM raw_intake ORDER BY raw_id").fetchall()
        r2 = st.isvc.ingest("partner_feed", items, "t01-run2", "t01")
        self.assertEqual((r2["stored"], r2["outcomes"]), (100, {"NOOP_DUPLICATE": 100}))
        rows = st.con.execute("SELECT * FROM raw_intake ORDER BY raw_id").fetchall()
        self.assertEqual(len(rows), 200)
        self.assertEqual(rows[:100], before)
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_outcome").fetchone()[0], 200)
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_outcome WHERE run_id = 't01-run2' AND outcome = 'NOOP_DUPLICATE'").fetchone()[0], 100)
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_outcome WHERE run_id = 't01-run1' AND outcome = 'VALIDATED'").fetchone()[0], 100)

    def test_TST_INT_03_no_status_update_and_legacy_read_only(self):
        """TST-INT-03 / AC-INT-03: no statement in the intake code updates an intake table or the legacy processing_status, and the legacy
        partner feed is reachable only through the mode=ro&immutable=1 snapshot handle (a write is refused)."""
        files = []
        for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub", "intake")):
            files += [os.path.join(d, f) for f in fns if f.endswith((".py", ".sql"))]
        files += [os.path.join(S.CODE_ROOT, "hub", "adapters", f) for f in ("intake_sources.py", "gateway_client.py")]
        self.assertGreaterEqual(len(files), 12)
        bad = re.compile(r"(?i)\bUPDATE\s+(raw_intake|intake_\w+|partner_feeds|source_messages|gateway_inbox)\b|processing_status|\bsqlite3\.connect\b"
                         r"|\b(INSERT\s+INTO|DELETE\s+FROM|REPLACE\s+INTO|ALTER\s+TABLE|DROP\s+TABLE)\s+(partner_feeds|source_messages|gateway_inbox)\b")
        hits = []
        for f in files:
            with open(f, encoding="utf-8") as fh:
                for n, line in enumerate(fh, 1):
                    if f.endswith(".py") and bad.search(line):
                        hits.append((os.path.relpath(f, S.CODE_ROOT), n))
        self.assertEqual(hits, [])
        h = I.D.legacy_handle("t03-")
        try:
            self.assertEqual(h.provenance["access"], "mode=ro&immutable=1")
            with self.assertRaises(LegacyWriteRefused):
                h.execute("UPDATE partner_feeds SET processing_status = 'X'")
            with self.assertRaises(LegacyWriteRefused):
                h.execute("DELETE FROM partner_feeds")
        finally:
            h.close()

    def test_TST_INT_04_redelivery_changes_nothing(self):
        """TST-INT-04 / AC-INT-04 / PNFR-11: 100 processed items (a mix of clean and defective), snapshot, the same 100 re-delivered -> queue
        sizes, ages, per-reason counts and totals identical; 100 NOOP_DUPLICATE with counts_toward_totals = 0."""
        st = self.store()
        items = I.batch(70) + [I.feed(i, payload={"quantity": -1.5}) for i in range(70, 80)] + \
            [I.feed(i, ref_id="C0000%04d" % (9000 + i)) for i in range(80, 90)] + \
            [I.feed(i, schema_rev="unsupported") for i in range(90, 100)]
        st.isvc.ingest("partner_feed", items, "t04-run1", "t04")
        snap = st.isvc.queue_snapshot(st.now())
        self.assertGreater(sum(snap["queues"].values()), 0)
        self.assertEqual(sorted(snap["queues"]), ["flagged_value", "quarantine_invalid", "unmatched"])
        res = replay.replay_safety(st.isvc, "partner_feed", items, "t04-run2", st.now(), "t04")
        self.assertTrue(res["ok"], res["checks"])
        self.assertEqual(st.isvc.queue_snapshot(st.now())["queues"], snap["queues"])
        rows = st.con.execute("SELECT outcome, counts_toward_totals FROM intake_outcome WHERE run_id = 't04-run2'").fetchall()
        self.assertEqual(rows, [("NOOP_DUPLICATE", 0)] * 100)

    def test_TST_INT_05_67_replay_pairs_are_noop_duplicates(self):
        """TST-INT-05 / AC-INT-05: the 134 shipped rows forming 67 natural-key pairs -> 67 originals + 67 NOOP_DUPLICATE, none a revision conflict."""
        by, _ = I.legacy_deliveries()
        groups = {}
        for d in by["partner_feed"]:
            groups.setdefault((d["partner"], d["record_kind"], d["ref_id"], d["source_ts"]), []).append(d)
        pairs = [g for g in groups.values() if len(g) > 1]
        self.assertEqual((len(pairs), sorted(set(len(g) for g in pairs))), (67, [2]))
        keep = set(d["source_key"] for g in pairs for d in g)
        subset = [d for d in by["partner_feed"] if d["source_key"] in keep]
        self.assertEqual(len(subset), 134)
        st = self.store()
        rep = st.isvc.ingest("partner_feed", subset, "t05", "t05")
        self.assertEqual((rep["noop_duplicate"], rep["revised_conflict"], rep["stored"]), (67, 0, 134))
        rows = st.con.execute("SELECT r.raw_id, r.duplicate_of, o.outcome, r.source_key FROM raw_intake r JOIN intake_outcome o ON o.raw_id = r.raw_id"
                              " ORDER BY r.raw_id").fetchall()
        noop = [r for r in rows if r[2] == "NOOP_DUPLICATE"]
        self.assertEqual(len(noop), 67)
        orig = dict((r[0], r) for r in rows if r[2] != "NOOP_DUPLICATE")
        self.assertEqual(len(orig), 67)
        for r in noop:
            self.assertIn(r[1], orig)                       # the duplicate points at its original
            self.assertTrue(r[3].startswith("REPLAY-") and orig[r[1]][3].startswith("FEED-"))
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_outcome WHERE all_reasons LIKE '%REVISED_CONFLICT%'").fetchone()[0], 0)

    def test_TST_INT_06_business_key_is_not_an_identity(self):
        """TST-INT-06 / AC-INT-06 / OD-S12-17 (decided OD-18): across the whole shipped feed only the 67 replay pairs are duplicates; rows that share a
        business_key but have different natural keys are never duplicates or revision conflicts. The rejected key (partner, business_key) is
        measured for contrast."""
        st, rep = I.full_store("record_only")
        by, _ = I.legacy_deliveries()
        feeds = by["partner_feed"]
        self.assertEqual(rep["received"], 8567)
        self.assertEqual((rep["noop_duplicate"], rep["revised_conflict"]), (67, 0))
        import json
        nat, biz = {}, {}
        for n, d in enumerate(feeds, 1):
            nat.setdefault((d["partner"], d["record_kind"], d["ref_id"], d["source_ts"]), []).append(n)
            p = json.loads(d["payload_text"])
            if p.get("business_key"):
                biz.setdefault((d["partner"], p["business_key"]), []).append((n, d["payload_text"]))
        outcome = dict(st.con.execute("SELECT raw_id, outcome FROM intake_current UNION ALL SELECT raw_id, outcome FROM intake_outcome WHERE outcome = 'NOOP_DUPLICATE'"))
        singles = [g[0] for g in nat.values() if len(g) == 1]
        self.assertEqual(len(singles), 8567 - 134)
        self.assertEqual([n for n in singles if outcome[rawid(n)] == "NOOP_DUPLICATE"], [])
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_outcome WHERE conflicts_with IS NOT NULL").fetchone()[0], 0)
        shared = [g for g in biz.values() if len(g) > 1 and len(set(t for _, t in g)) > 1]
        self.assertGreater(len(shared), 0)
        wrong_key_collisions = sum(len(g) - 1 for g in shared)
        self.assertGreater(wrong_key_collisions, 500)       # the rejected key would have mis-classified these as revisions of one another

    def test_TST_INT_07_corrected_replay_is_quarantined_not_duplicate(self):
        """TST-INT-07 / AC-INT-07 (class C: synthetic fixture, FND-INT-1): same natural key, changed quantity -> QUARANTINED REVISED_CONFLICT in
        queue revision_review; both versions retrievable and linked; not marked duplicate; later re-deliveries of either version are NOOP."""
        st = self.store()
        orig = I.feed(1)
        rev = I.feed(1, payload={"quantity": 99.5}, source_key="FEED-REVISED-01")
        self.assertEqual(rev["source_ts"], orig["source_ts"])
        st.isvc.ingest("partner_feed", [orig], "t07a", "t07")
        rep = st.isvc.ingest("partner_feed", [rev], "t07b", "t07")
        self.assertEqual((rep["revised_conflict"], rep["outcomes"]), (1, {"QUARANTINED": 1}))
        it = st.isvc.get_item(rawid(2))
        cur = it["current"]
        self.assertEqual((cur["outcome"], cur["primary_reason"], cur["queue"], cur["conflicts_with"]),
                         ("QUARANTINED", "REVISED_CONFLICT", "revision_review", rawid(1)))
        self.assertIsNone(it["duplicate_of"])
        self.assertEqual(st.isvc.versions(rawid(2)), [rawid(1), rawid(2)])
        self.assertNotEqual(st.isvc.raw_bytes(rawid(1)), st.isvc.raw_bytes(rawid(2)))
        self.assertIn(b"99.5", st.isvc.raw_bytes(rawid(2)))
        self.assertEqual(st.isvc.queue_snapshot(st.now())["queues"], {"revision_review": 1})
        rep = st.isvc.ingest("partner_feed", [rev, orig], "t07c", "t07")
        self.assertEqual(rep["outcomes"], {"NOOP_DUPLICATE": 2})
        self.assertEqual(st.isvc.queue_snapshot(st.now())["queues"], {"revision_review": 1})

    def test_TST_INT_08_human_resolution_needs_reason_and_changes_no_case(self):
        """TST-INT-08 / AC-INT-08: a reviewer resolves accept_revision with a reason -> CONFLICT_RESOLVED stored, no decision event / case state /
        gate event written; no reason -> E-INT-RESOLUTION-REASON-REQUIRED; second resolution refused; wrong role, unknown or non-conflict items refused."""
        st = self.store()
        st.isvc.ingest("partner_feed", [I.feed(1), I.feed(1, payload={"quantity": 7.25}, source_key="FEED-REV"), I.feed(2)], "t08", "t08")
        conflict, plain = rawid(2), rawid(3)
        before = (st.con.execute("SELECT count(*) FROM decision_events").fetchone()[0], st.table_digest(["case_state", "decision_events"]))
        n_out = st.con.execute("SELECT count(*) FROM intake_outcome").fetchone()[0]
        for bad in (None, "", "   ", "x" * 2001):
            with self.assertRaises(E.ResolutionReasonRequired):
                st.isvc.resolve_conflict(st.sess("rev"), conflict, "accept_revision", bad, "t08")
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_outcome").fetchone()[0], n_out)
        with self.assertRaises(AuthForbidden):
            st.isvc.resolve_conflict(st.sess("holder-1"), conflict, "accept_revision", "ok", "t08")      # dispositioner is not a resolver
        with self.assertRaises(AuthForbidden):
            st.isvc.resolve_conflict(st.service_session(), conflict, "accept_revision", "ok", "t08")
        with self.assertRaises(E.ItemNotFound):
            st.isvc.resolve_conflict(st.sess("rev"), "RAW-9999999999", "accept_revision", "ok", "t08")
        with self.assertRaises(E.ItemNotFound):
            st.isvc.resolve_conflict(st.sess("rev"), plain, "accept_revision", "ok", "t08")             # not a revision conflict
        with self.assertRaises(E.EnvelopeInvalid):
            st.isvc.resolve_conflict(st.sess("rev"), conflict, "merge_both", "ok", "t08")
        it = st.isvc.resolve_conflict(st.sess("rev"), conflict, "accept_revision", "reviewed the corrected quantity (synthetic)", "t08")
        cur = it["current"]
        self.assertEqual((cur["outcome"], cur["resolution"], cur["resolved_by"], cur["queue"], cur["conflicts_with"]),
                         ("CONFLICT_RESOLVED", "accept_revision", "rev", None, rawid(1)))
        self.assertEqual([o["outcome_seq"] for o in it["outcomes"]], [1, 2])
        self.assertEqual(it["outcomes"][0]["outcome"], "QUARANTINED")                                      # history kept
        self.assertEqual(st.isvc.queue_snapshot(st.now())["queues"], {})                                  # left revision_review
        after = (st.con.execute("SELECT count(*) FROM decision_events").fetchone()[0], st.table_digest(["case_state", "decision_events"]))
        self.assertEqual(before, after)
        self.assertEqual(st.audit_actions("ZONE_H_ATTEMPT"), [])
        with self.assertRaises(E.ConflictAlreadyResolved):
            st.isvc.resolve_conflict(st.sess("ql"), conflict, "keep_original", "again", "t08")
        a = st.audit_actions("INTAKE_CONFLICT_RESOLVED")
        self.assertEqual((len(a), a[0]["actor"], a[0]["details"]["resolution"]), (1, "rev", "accept_revision"))


if __name__ == "__main__":
    unittest.main()
