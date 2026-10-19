"""TST-INT-09..16 (AC-INT-09..16; FR-INT-04/05/06; class A except TST-INT-12/13/14 = B (OD-S12-11, default record_only) and TST-INT-15 = B
(OD-S12-13, legacy rejected negatives)): quarantine of the unsupported revisions, one reason code per defect, the 210 rows without
business_key, the per-source contract binding (record_only default vs enforce) over the shipped feeds, negative quantities flagged not
rejected, unit / currency vocabularies. Shipped-data checks read the hash-gated FX-BASE125 sandbox copy. Synthetic, unvalidated.
"""
import json
import unittest

import _support as S
import _inc06 as I
from hub.gate import errors as GE
from hub.intake.service import IntakeService


def setUpModule():
    I.skip_in_inner_egress_run()


def rawid(n):
    return "RAW-%010d" % n


class TST_INT_09_16_Validation(unittest.TestCase):

    def setUp(self):
        self.st = None

    def tearDown(self):
        if self.st is not None:
            self.st.close()

    def store(self, **kw):
        self.st = I.IStore(**kw)
        return self.st

    def current(self, st, raw_id):
        return st.isvc.get_item(raw_id)["current"]

    def test_TST_INT_09_unsupported_revisions_are_quarantined(self):
        """TST-INT-09 / AC-INT-09 / DQ-02: the 224 shipped rows with schema_rev 'unsupported' -> raw rows = 224, every non-replay row is
        QUARANTINED UNSUPPORTED_REVISION in queue quarantine_invalid; quarantine rows = UNSUPPORTED outcomes; a replay of a quarantined original
        is a NOOP_DUPLICATE (SBR-INT-04: identity comparison precedes validation)."""
        by, _ = I.legacy_deliveries()
        subset = [d for d in by["partner_feed"] if d["schema_rev"] == "unsupported"]
        self.assertEqual(len(subset), 224)
        st = self.store()
        rep = st.isvc.ingest("partner_feed", subset, "t09", "t09")
        self.assertEqual(st.isvc.counts()["raw"], 224)
        self.assertEqual(st.isvc.counts()["outcomes"], 224)
        unsupported = st.con.execute("SELECT count(*) FROM intake_outcome WHERE primary_reason = 'UNSUPPORTED_REVISION' AND outcome = 'QUARANTINED'"
                                     " AND queue = 'quarantine_invalid'").fetchone()[0]
        noop = rep["noop_duplicate"]
        self.assertEqual(unsupported + noop, 224)
        self.assertEqual(rep["outcomes"], {"QUARANTINED": unsupported, "NOOP_DUPLICATE": noop})
        self.assertEqual(st.isvc.queue_snapshot(st.now())["queues"], {"quarantine_invalid": unsupported})
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_current WHERE queue = 'quarantine_invalid'").fetchone()[0], unsupported)
        self.assertEqual(st.con.execute("SELECT count(*) FROM crosswalk_link").fetchone()[0], 0)       # quarantined items are never linked
        self.assertGreater(unsupported, 200)

    def test_TST_INT_10_each_defect_gets_its_reason_code(self):
        """TST-INT-10 / AC-INT-10: invalid JSON, a missing envelope field, an unknown record_kind and a missing payload field each land in
        quarantine with INVALID_JSON / MISSING_ENVELOPE_FIELD / UNKNOWN_RECORD_KIND / MISSING_PAYLOAD_FIELD; reason counts = quarantine rows."""
        st = self.store()
        items = [I.feed(1, payload_text="{not valid json"), I.feed(2, ref_id=None), I.feed(3, record_kind="FOO"),
                 I.feed(4, payload={"object_type": ...})]
        rep = st.isvc.ingest("partner_feed", items, "t10", "t10")
        self.assertEqual(rep["outcomes"], {"QUARANTINED": 4})
        got = [self.current(st, rawid(i)) for i in (1, 2, 3, 4)]
        self.assertEqual([g["primary_reason"] for g in got], ["INVALID_JSON", "MISSING_ENVELOPE_FIELD", "UNKNOWN_RECORD_KIND", "MISSING_PAYLOAD_FIELD"])
        self.assertEqual([g["queue"] for g in got], ["quarantine_invalid"] * 4)
        self.assertEqual(got[1]["reason_detail"]["MISSING_ENVELOPE_FIELD"], ["ref_id"])
        self.assertEqual(got[3]["reason_detail"]["MISSING_PAYLOAD_FIELD"], ["object_type"])
        snap = st.isvc.queue_snapshot(st.now())
        self.assertEqual(snap["reasons"], {"INVALID_JSON": 1, "MISSING_ENVELOPE_FIELD": 1, "MISSING_PAYLOAD_FIELD": 1, "UNKNOWN_RECORD_KIND": 1})
        self.assertEqual(snap["queues"], {"quarantine_invalid": 4})
        self.assertEqual(st.isvc.counts()["raw"], 4)                                       # stored, not merely counted
        for i in (1, 2, 3, 4):
            self.assertTrue(len(st.isvc.raw_bytes(rawid(i))) > 10)

    def test_TST_INT_11_rows_without_business_key(self):
        """TST-INT-11 / AC-INT-11 / DQ-01: the 210 shipped rows without business_key -> NO_BUSINESS_KEY in every non-duplicate outcome (the 2
        replay copies are NOOP), queue unmatched when it is the primary reason, none linked."""
        st, _ = I.full_store("record_only")
        by, _sha = I.legacy_deliveries()
        nb = [n for n, d in enumerate(by["partner_feed"], 1) if "business_key" not in json.loads(d["payload_text"])]
        self.assertEqual(len(nb), 210)
        noop = set(r[0] for r in st.con.execute("SELECT raw_id FROM intake_outcome WHERE outcome = 'NOOP_DUPLICATE'"))
        self.assertTrue(set(rawid(n) for n in nb) & noop)                                 # some of the 210 are replay copies
        flagged, primary = 0, 0
        for n in nb:
            cur = st.isvc.outcomes(rawid(n))[-1]
            if cur["outcome"] == "NOOP_DUPLICATE":
                continue
            self.assertIn("NO_BUSINESS_KEY", cur["all_reasons"])
            flagged += 1
            if cur["primary_reason"] == "NO_BUSINESS_KEY":
                primary += 1
                self.assertEqual((cur["queue"], cur["outcome"], cur["matched_link"]), ("unmatched", "EXCEPTION", None))
            self.assertIsNone(cur["matched_link"])
        self.assertEqual(flagged, 210 - len(set(rawid(n) for n in nb) & noop))
        self.assertGreater(primary, 150)
        feed_ids = [by["partner_feed"][n - 1]["source_key"] for n in nb]
        q = "SELECT count(*) FROM crosswalk_link WHERE from_id IN (%s)" % ",".join("?" * len(feed_ids))
        self.assertEqual(st.con.execute(q, feed_ids).fetchone()[0], 0)

    def test_TST_INT_12_record_only_is_the_default(self):
        """TST-INT-12 / AC-INT-12 / OD-S12-11: binding partner_feed = record_only (default) -> every one of the 8,567 outcomes carries
        contract_check = fail, none is quarantined by the contract alone."""
        st, rep = I.full_store("record_only")
        self.assertEqual(rep["binding"], {"source": "partner_feed", "mode": "record_only", "contract_file": "source-contract-v1", "origin": "default"})
        self.assertEqual(rep["contract_check"], {"fail": 8567})
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_outcome WHERE contract_check = 'fail'").fetchone()[0], 8567)
        self.assertEqual(st.con.execute("SELECT count(*) FROM intake_outcome WHERE all_reasons LIKE '%CONTRACT_VIOLATION%'").fetchone()[0], 0)
        self.assertEqual(json.loads(st.con.execute("SELECT contract_missing FROM intake_outcome WHERE raw_id = ?", (rawid(1),)).fetchone()[0]),
                         ["ref", "schema_version", "status"])
        quarantined = st.con.execute("SELECT count(*) FROM intake_outcome WHERE outcome = 'QUARANTINED'").fetchone()[0]
        reasons = st.isvc.queue_snapshot(st.now())["reasons"]
        self.assertEqual(quarantined, reasons["UNSUPPORTED_REVISION"] if "UNSUPPORTED_REVISION" in reasons else 0)  # only the revision rule quarantines
        self.assertEqual(st.con.execute("SELECT count(*) FROM raw_intake").fetchone()[0], 8567)

    def test_TST_INT_13_enforce_quarantines_everything_nothing_dropped(self):
        """TST-INT-13 / AC-INT-13: binding partner_feed = enforce (set by a synthetic Zone H holder) -> every non-duplicate outcome carries
        CONTRACT_VIOLATION and is QUARANTINED (8,500) and the 67 replay copies are NOOP_DUPLICATE (all 8,567 fail the contract); nothing dropped."""
        st, rep = I.full_store("enforce")
        self.assertEqual(rep["binding"]["mode"], "enforce")
        self.assertTrue(rep["binding"]["origin"].startswith("PE-"))
        self.assertEqual(rep["contract_check"], {"fail": 8567})
        self.assertEqual(rep["outcomes"], {"QUARANTINED": 8500, "NOOP_DUPLICATE": 67})
        n = st.con.execute("SELECT count(*) FROM intake_outcome WHERE all_reasons LIKE '%CONTRACT_VIOLATION%' AND outcome = 'QUARANTINED'").fetchone()[0]
        self.assertEqual(n, 8500)
        self.assertEqual(n + rep["noop_duplicate"], 8567)
        self.assertEqual((st.isvc.counts()["raw"], st.isvc.counts()["outcomes"]), (8567, 8567))
        self.assertEqual(st.con.execute("SELECT count(*) FROM crosswalk_link").fetchone()[0], 0)
        a = st.audit_actions("CONTRACT_BINDING_CHANGED")
        self.assertEqual((len(a), a[0]["actor"], a[0]["details"]["to_mode"]), (1, "holder-1", "enforce"))

    def test_TST_INT_14_source_messages_conform_to_the_contract(self):
        """TST-INT-14 / AC-INT-14 / FND-INT-3: binding source_message = enforce -> the 15 shipped messages: 15 contract_check = pass, 0 quarantined;
        the single gateway_inbox row fails the contract (enforce -> CONTRACT_VIOLATION, record_only -> kept, not quarantined)."""
        by, _ = I.legacy_deliveries()
        st = self.store()
        st.bind("source_message", "enforce")
        rep = st.isvc.ingest("source_message", by["source_message"], "t14a", "t14")
        self.assertEqual((rep["contract_check"], rep["outcomes"]), ({"pass": 15}, {"VALIDATED": 15}))
        self.assertEqual(st.isvc.queue_snapshot(st.now())["queues"], {})
        rep = st.isvc.ingest("gateway", by["gateway"], "t14b", "t14")
        self.assertEqual((rep["contract_check"], rep["outcomes"]), ({"fail": 1}, {"VALIDATED": 1}))   # gateway still record_only
        st.bind("gateway", "enforce")
        rep = st.isvc.ingest("gateway", [dict(by["gateway"][0], source_key="GW-COPY-1", ref_id="BT00000001", source_ts="2025-01-02T00:00:00Z")], "t14c", "t14")
        self.assertEqual(rep["outcomes"], {"QUARANTINED": 1})
        self.assertEqual(self.current(st, rawid(17))["primary_reason"], "CONTRACT_VIOLATION")

    def test_TST_INT_15_negative_quantity_is_flagged_not_rejected(self):
        """TST-INT-15 / AC-INT-15 / OD-S12-13: quantity -4.942 -> flag NEGATIVE_VALUE, queue flagged_value, value kept verbatim. The legacy
        reconcile REJECTED it ('quantity out of range'): a recorded difference to be decided at Stage 30 (DV-ref in the transformation log)."""
        st = self.store()
        rep = st.isvc.ingest("partner_feed", [I.feed(1, payload={"quantity": -4.942})], "t15", "t15")
        self.assertEqual(rep["outcomes"], {"VALIDATED_WITH_FLAGS": 1})
        it = st.isvc.get_item(rawid(1))
        cur = it["current"]
        self.assertEqual((cur["primary_reason"], cur["queue"], cur["all_reasons"]), ("NEGATIVE_VALUE", "flagged_value", ["NEGATIVE_VALUE"]))
        self.assertEqual(it["attributes"]["amount_text"], "-4.942")
        self.assertEqual(json.loads(json.loads(st.isvc.raw_bytes(rawid(1)))["raw_json"])["quantity"], -4.942)
        self.assertIsNotNone(cur["matched_link"])                                       # a flagged value is still matched, not rejected
        rep = st.isvc.ingest("partner_feed", [I.feed(2, payload={"quantity": "abc"}), I.feed(3, payload={"quantity": True}),
                                              I.feed(4, payload={"quantity": None})], "t15b", "t15")
        self.assertEqual(rep["reasons"], {"UNPARSABLE_AMOUNT": 3})

    def test_TST_INT_16_unit_and_currency_vocabularies(self):
        """TST-INT-16 / AC-INT-16: unit 'pct' -> UNKNOWN_UNIT, 'percent' clean; currency 'XXX' and 'usd' -> UNKNOWN_CURRENCY; raw values preserved."""
        st = self.store()
        items = [I.feed(1, payload={"unit": "pct"}), I.feed(2, payload={"unit": "percent"}), I.feed(3, payload={"currency": "XXX"}),
                 I.feed(4, payload={"currency": "usd"})]
        st.isvc.ingest("partner_feed", items, "t16", "t16")
        got = [self.current(st, rawid(i)) for i in (1, 2, 3, 4)]
        self.assertEqual([g["primary_reason"] for g in got], ["UNKNOWN_UNIT", None, "UNKNOWN_CURRENCY", "UNKNOWN_CURRENCY"])
        self.assertEqual([g["outcome"] for g in got], ["VALIDATED_WITH_FLAGS", "VALIDATED", "VALIDATED_WITH_FLAGS", "VALIDATED_WITH_FLAGS"])
        self.assertEqual([g["queue"] for g in got], ["flagged_value", None, "flagged_value", "flagged_value"])
        raws = [json.loads(json.loads(st.isvc.raw_bytes(rawid(i)))["raw_json"]) for i in (1, 2, 3, 4)]
        self.assertEqual((raws[0]["unit"], raws[1]["unit"], raws[2]["currency"], raws[3]["currency"]), ("pct", "percent", "XXX", "usd"))


if __name__ == "__main__":
    unittest.main()
