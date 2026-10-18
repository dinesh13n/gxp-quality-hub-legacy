"""TST-ID-01..12 (AC-ID-01..12; FR-ID-01, FR-ID-02; class A) - the explicit identity crosswalk: rule links only by exact registered
keys over the shipped legacy data (42 deviation->batch, 21 capa->deviation, 173 feed->case with 8,394 feed rows left as orphans),
orphans stay orphans, no case folding / fuzzy / similarity code, human links need a reviewer-class human and a reason, duplicates,
unregistered pairs, retraction as an event, and ambiguous identifiers are never guessed. TST-ID-13..17 are R2 (INC-09).
Fixture: FX-BASE125 (hash-gated sandbox copy, read through the read-only snapshot adapter). Synthetic, unvalidated.
"""
import ast
import os
import unittest

import _support as S
import _inc05 as D
from hub.core.errors import UntrustedUse  # noqa: F401
from hub.crosswalk import sources
from hub.crosswalk.registry import Registry
from hub.crosswalk.service import identity_targets
from hub.decision import errors as E
from hub.security.errors import AuthForbidden


def setUpModule():
    D.skip_in_inner_egress_run()


class TST_ID_01_12_Crosswalk(unittest.TestCase):

    def setUp(self):
        self.ds = None

    def tearDown(self):
        if self.ds is not None:
            self.ds.close()

    def store(self, **kw):
        self.ds = D.DStore(**kw)
        return self.ds

    def legacy_runs(self, ds, codes):
        h = D.legacy_handle()
        try:
            inputs, cases = sources.legacy_inputs(h)
        finally:
            h.close()
        out = {}
        for c in codes:
            items, targets = inputs[c]
            out[c] = ds.cw.run_rule(c, items, targets, "run-test", "t-cw")
        return out

    def test_TST_ID_01_rule_links_deviation_batch_capa_deviation(self):
        """TST-ID-01 / AC-ID-01: after rule matching of the shipped data, 42 deviation->batch (LT-01) and 21 capa->deviation (LT-02) links exist,
        each with key_used, creator_kind = rule, created_at."""
        ds = self.store()
        runs = self.legacy_runs(ds, ["LT-01", "LT-02"])
        self.assertEqual((runs["LT-01"]["items"], runs["LT-01"]["counts"]["LINKED"], runs["LT-01"]["orphans"]), (42, 42, 0))
        self.assertEqual((runs["LT-02"]["items"], runs["LT-02"]["counts"]["LINKED"], runs["LT-02"]["orphans"]), (21, 21, 0))
        links = ds.cw.active_links()
        self.assertEqual(len(links), 63)
        for lk in links:
            self.assertEqual(lk["creator_kind"], "rule")
            self.assertTrue(lk["key_used"] and lk["created_at"] and lk["run_id"] == "run-test")
        self.assertEqual((ds.cw.count_active("LT-01"), ds.cw.count_active("LT-02")), (42, 21))
        l1 = [lk for lk in links if lk["creator"] == "LT-01"][0]
        self.assertEqual((l1["from_type"], l1["to_type"], l1["key_used"]), ("deviation", "batch", "deviations.batch_id = batch_records.batch_id"))
        self.assertEqual([e["event_type"] for e in l1["events"]], ["LINK_CREATED_RULE"])

    def test_TST_ID_02_feed_to_case_173_links_8394_orphans(self):
        """TST-ID-02 / AC-ID-02: the 173 feed rows whose ref_id equals a case id give 173 LT-04 links; 8,394 feed items remain unlinked (orphans, reported)."""
        ds = self.store()
        r = self.legacy_runs(ds, ["LT-04"])["LT-04"]
        self.assertEqual(r["items"], 8567)
        self.assertEqual((r["counts"]["LINKED"], r["counts"]["UNMATCHED_REF"], r["orphans"]), (173, 8394, 8394))
        self.assertEqual(ds.cw.count_active("LT-04"), 173)
        self.assertEqual(ds.cw.orphan_report()["LT-04"]["orphans"], 8394)
        again = self.legacy_runs(ds, ["LT-04"])["LT-04"]
        self.assertEqual((again["counts"]["LINKED"], again["counts"]["NOOP_ALREADY_LINKED"]), (0, 173))
        self.assertEqual(ds.cw.count_active("LT-04"), 173)

    def test_TST_ID_03_orphans_stay_orphans(self):
        """TST-ID-03 / AC-ID-03: an orphan fixture (feed ref_id C99999999) stays unlinked after 3 matcher runs with other data added."""
        ds = self.store()
        items = [("FEED-000000001", "C99999999")]
        targets = identity_targets(["C00000001"])
        for extra in range(3):
            items.append(("FEED-00000010%d" % extra, "C00000001"))
            targets = identity_targets(["C00000001", "C0000010%d" % extra])
            r = ds.cw.run_rule("LT-04", items, targets, "run-%d" % extra, "t-cw", return_outcomes=True)
            self.assertEqual(dict(r["outcomes"])["FEED-000000001"], "UNMATCHED_REF")
        self.assertEqual(ds.cw.count_active("LT-04"), 3)
        lk = ds.cw.lookup(ds.sess("rev"), "FEED-000000001")
        self.assertEqual(lk["links"], [])

    def test_TST_ID_04_no_case_folding_no_fuzzy(self):
        """TST-ID-04 / AC-ID-04: feed ref_id 'c00000001' (case differs) and 'C0000000 1' (inner space) create no link (UNMATCHED_REF); the only
        normalisation is Unicode NFC + trim (' C00000001 ' links)."""
        ds = self.store()
        items = [("FEED-000000001", "c00000001"), ("FEED-000000002", "C0000000 1"), ("FEED-000000003", "C0000000"),
                 ("FEED-000000004", "C000000011"), ("FEED-000000005", " C00000001 ")]
        r = ds.cw.run_rule("LT-04", items, identity_targets(["C00000001"]), "run-x", "t-cw", return_outcomes=True)
        out = dict(r["outcomes"])
        self.assertEqual([out["FEED-00000000%d" % i] for i in (1, 2, 3, 4)], ["UNMATCHED_REF"] * 4)
        self.assertEqual(out["FEED-000000005"], "LINKED")
        self.assertEqual(ds.cw.count_active(), 1)

    def test_TST_ID_05_static_no_similarity_code(self):
        """TST-ID-05 / AC-ID-05: the crosswalk package imports no difflib / fuzzy / levenshtein / similarity library and applies no case folding."""
        root = os.path.join(S.CODE_ROOT, "hub", "crosswalk")
        files = [f for f in os.listdir(root) if f.endswith(".py")]
        self.assertIn("service.py", files)
        bad_import, bad_call = [], []
        for fn in files:
            tree = ast.parse(open(os.path.join(root, fn), encoding="utf-8").read())
            for n in ast.walk(tree):
                mods = []
                if isinstance(n, ast.Import):
                    mods = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom) and n.module:
                    mods = [n.module]
                for m in mods:
                    if any(w in m.lower() for w in ("difflib", "fuzz", "leven", "simil", "jellyfish", "rapidfuzz", "soundex", "metaphone", "jaro")):
                        bad_import.append((fn, m))
                if isinstance(n, ast.Attribute) and n.attr in ("lower", "upper", "casefold", "title", "swapcase"):
                    bad_call.append((fn, n.attr))
        self.assertEqual((bad_import, bad_call), ([], []))

    def test_TST_ID_06_human_link_with_reason(self):
        """TST-ID-06 / AC-ID-06: a reviewer links case C00000001 to batch BT00000000 with a reason: stored with creator_kind human and a
        LINK_CREATED_HUMAN event carrying actor, time and reason (also in the audit chain)."""
        ds = self.store()
        lk = ds.cw.create_human_link(ds.sess("rev"), "case", "C00000001", "batch", "BT00000000", "same lot per site log (synthetic)",
                                     correlation_id="t-hl")
        self.assertEqual((lk["creator_kind"], lk["creator"], lk["reason"], lk["from_type"], lk["to_type"]),
                         ("human", "rev", "same lot per site log (synthetic)", "case", "batch"))
        self.assertTrue(lk["active"])
        ev = lk["events"][0]
        self.assertEqual((ev["event_type"], ev["actor"], ev["reason"]), ("LINK_CREATED_HUMAN", "rev", "same lot per site log (synthetic)"))
        self.assertTrue(ev["occurred_at"].endswith("Z"))
        a = [x for x in ds.audit_actions("LINK_CREATED_HUMAN")]
        self.assertEqual([(x["actor"], x["outcome"]) for x in a], [("rev", "success")])
        look = ds.cw.lookup(ds.sess("ql"), "BT00000000")
        self.assertEqual(look["id_type"], "batch")
        self.assertEqual([x["link_id"] for x in look["links"]], [lk["link_id"]])

    def test_TST_ID_07_reason_required(self):
        """TST-ID-07 / AC-ID-07: the same request without a reason (missing, empty or blank) -> E-ID-REASON-REQUIRED, nothing stored."""
        ds = self.store()
        for reason in (None, "", "   "):
            with self.assertRaises(E.IdReasonRequired):
                ds.cw.create_human_link(ds.sess("rev"), "case", "C00000001", "batch", "BT00000000", reason, correlation_id="t-hl")
        self.assertEqual(ds.counts()["crosswalk_link"], 0)
        self.assertEqual(ds.counts()["crosswalk_link_event"], 0)

    def test_TST_ID_08_service_account_forbidden_and_audited(self):
        """TST-ID-08 / AC-ID-08: a service account calling OP-ID-02 is rejected E-AUTH-FORBIDDEN and the rejection is audited."""
        ds = self.store()
        with self.assertRaises(AuthForbidden):
            ds.cw.create_human_link(ds.service_session(), "case", "C00000001", "batch", "BT00000000", "r", correlation_id="t-svc")
        with self.assertRaises(AuthForbidden):  # a finance_read style human without a reviewer-class role is refused as well
            ds.cw.create_human_link(ds.sess("holder-1"), "case", "C00000001", "batch", "BT00000000", "r", correlation_id="t-disp")
        self.assertEqual(ds.counts()["crosswalk_link"], 0)
        rows = ds.audit_actions("AUTHZ_DENIED")
        self.assertEqual([(a["actor"], a["actor_kind"], a["object_ref"], a["outcome"]) for a in rows],
                         [("svc-integration", "service", "OP-ID-02", "denied"), ("holder-1", "human", "OP-ID-02", "denied")])

    def test_TST_ID_09_duplicate_active_link(self):
        """TST-ID-09 / AC-ID-09: posting an existing active link again (also in the reverse direction) -> E-ID-LINK-EXISTS; a self-link -> E-ID-SELF-LINK."""
        ds = self.store()
        ds.cw.create_human_link(ds.sess("rev"), "case", "C00000001", "batch", "BT00000000", "first", correlation_id="t-hl")
        with self.assertRaises(E.LinkExists):
            ds.cw.create_human_link(ds.sess("ql"), "case", "C00000001", "batch", "BT00000000", "again", correlation_id="t-hl")
        with self.assertRaises(E.LinkExists):
            ds.cw.create_human_link(ds.sess("ql"), "batch", "BT00000000", "case", "C00000001", "reverse", correlation_id="t-hl")
        with self.assertRaises(E.SelfLink):
            ds.cw.create_human_link(ds.sess("ql"), "case", "C00000001", "case", "C00000001", "self", correlation_id="t-hl")
        self.assertEqual(ds.counts()["crosswalk_link"], 1)

    def test_TST_ID_10_unregistered_pair(self):
        """TST-ID-10 / AC-ID-10: a link between an unregistered type pair -> E-ID-PAIR-NOT-REGISTERED (LT-06 pairs are the only human-only pairs)."""
        ds = self.store()
        for ft, fi, tt, ti in (("case", "C00000001", "lab_result", "LAB00000001"), ("document", "DOC-00000001", "batch", "BT00000001"),
                               ("lab_result", "LAB00000001", "document", "DOC-00000001")):
            with self.assertRaises(E.PairNotRegistered):
                ds.cw.create_human_link(ds.sess("rev"), ft, fi, tt, ti, "r", correlation_id="t-hl")
        with self.assertRaises(E.PairNotRegistered):
            ds.cw.run_rule("LT-06", [], {}, "run-x", "t-cw")  # human-only: no rule may create it
        for tt, ti in (("deviation", "DEV00000001"), ("capa", "CAPA00000001")):
            ds.cw.create_human_link(ds.sess("rev"), "case", "C00000001", tt, ti, "human pair", correlation_id="t-hl")
        self.assertEqual(ds.counts()["crosswalk_link"], 2)

    def test_TST_ID_11_retraction_is_an_event(self):
        """TST-ID-11 / AC-ID-11: a link retracted with a reason is no longer active; the original row and its LINK_RETRACTED event are both present;
        a retraction without a reason or of an unknown / already retracted link is refused."""
        ds = self.store()
        lk = ds.cw.create_human_link(ds.sess("rev"), "case", "C00000001", "batch", "BT00000000", "first", correlation_id="t-hl")
        with self.assertRaises(E.IdReasonRequired):
            ds.cw.retract(ds.sess("rev"), lk["link_id"], "", correlation_id="t-rt")
        with self.assertRaises(E.LinkNotFound):
            ds.cw.retract(ds.sess("rev"), "LNK-99999999", "r", correlation_id="t-rt")
        done = ds.cw.retract(ds.sess("ql"), lk["link_id"], "wrong lot (synthetic)", correlation_id="t-rt")
        self.assertFalse(done["active"])
        self.assertEqual([e["event_type"] for e in done["events"]], ["LINK_CREATED_HUMAN", "LINK_RETRACTED"])
        self.assertEqual(done["events"][1]["reason"], "wrong lot (synthetic)")
        self.assertEqual(ds.counts()["crosswalk_link"], 1)
        self.assertEqual(ds.cw.active_links(), [])
        self.assertEqual(ds.cw.lookup(ds.sess("rev"), "C00000001")["links"], [])
        with self.assertRaises(E.LinkNotFound):
            ds.cw.retract(ds.sess("ql"), lk["link_id"], "again", correlation_id="t-rt")
        again = ds.cw.create_human_link(ds.sess("rev"), "case", "C00000001", "batch", "BT00000000", "re-linked on new evidence", correlation_id="t-hl")
        self.assertNotEqual(again["link_id"], lk["link_id"])

    def test_TST_ID_12_ambiguous_identifier_not_guessed(self):
        """TST-ID-12 / AC-ID-12: an id string matching two registered patterns, looked up without id_type -> E-ID-AMBIGUOUS-TYPE with the candidate
        types and no data; with id_type it resolves; an id matching none is E-ID-NOT-FOUND."""
        ds = self.store()
        ds.cw.registry = Registry().with_id_type("legacy_case", "^C[0-9]{8}$")
        ds.cw.create_human_link(ds.sess("rev"), "case", "C00000001", "batch", "BT00000000", "r", correlation_id="t-hl")
        with self.assertRaises(E.AmbiguousType) as cm:
            ds.cw.lookup(ds.sess("rev"), "C00000001")
        self.assertEqual(cm.exception.details["candidates"], ["case", "legacy_case"])
        self.assertNotIn("links", cm.exception.details)
        ok = ds.cw.lookup(ds.sess("rev"), "C00000001", id_type="case")
        self.assertEqual(len(ok["links"]), 1)
        with self.assertRaises(E.IdNotFound):
            ds.cw.lookup(ds.sess("rev"), "not-an-id")
        with self.assertRaises(E.IdNotFound):
            ds.cw.lookup(ds.sess("rev"), "C00000001", id_type="batch")


if __name__ == "__main__":
    unittest.main()
