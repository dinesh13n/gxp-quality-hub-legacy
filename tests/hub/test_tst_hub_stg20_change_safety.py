"""Stage 20 DI-02 change-safety tests (DW-02, DW-03, DW-04, DW-05; FAC-05, FAC-06; S16-D01, S16-D02, S16-D10; RG-03). Synthetic, unvalidated.

  S01-S02  regression group manifest selects every hub test method exactly once (TST-CO-03 included); TST-CO-12 shard partition
  S03-S06  golden-compare observes the built modules: no declared value; observed values equal the Stage 16 observation
           (docs/16-repo-validation/evidence/obs-laptop.json); stale / foreign records refused; inline = record; legacy copy unchanged
  S07-S08  deviation register DV-01..DV-11 proposed (DV-07a text, DV-09 label, DV-10, DV-11); safe refresh of INC-02 rows only
"""
import json
import os
import sqlite3
import unittest

import _groups
import _stg20 as T
import _support as S
from hub.coexistence import register
from hub.golden import compare, observe, run as grun

OBS16 = os.path.join(S.CODE_ROOT, "docs", "16-repo-validation", "evidence", "obs-laptop.json")
DV_IDS = ["DV-%02d" % i for i in range(1, 12)]


def setUpModule():
    T.skip_in_inner_egress_run()


def _record():
    with open(T.observation(), encoding="utf-8") as f:
        return json.load(f)


class TST_HUB_STG20_ChangeSafety(unittest.TestCase):

    def test_TST_HUB_STG20_S01_manifest_selects_every_test_once(self):
        """S01 (DW-02 / DW-03): every test method in tests/hub/test_*.py is selected by exactly one group; TST-CO-03 (3 methods) is
        selected (S16-D10); group ids unique; group C is split into C1 / C2 / C3 (TST-CO-12 a-d + e1 / e2 / e3)."""
        groups = _groups.load()
        ids = _groups.static_ids()
        cov = _groups.coverage(groups, ids)
        self.assertEqual([i for i, g in sorted(cov.items()) if len(g) != 1], [])
        self.assertEqual(len(set(g["id"] for g in groups)), len(groups))
        co03 = [i for i in ids if "TST_CO_03" in i]
        self.assertEqual(len(co03), 3)
        self.assertEqual(set(g for i in co03 for g in cov[i]), {"I45"})
        for k in (2, 3):
            self.assertEqual(_groups.expected("C%d" % k, groups, ids), ["test_tst_co_12_egress_tripwire.TST_CO_12_EgressAndTripwire."
                                                                       "test_TST_CO_12_e%d_full_suite_under_egress_guard_shard%d" % (k, k)])
        self.assertEqual(len(_groups.expected("C1", groups, ids)), 5)
        self.assertGreaterEqual(len(ids), 397)

    def test_TST_HUB_STG20_S02_driver_shards_partition_modules(self):
        """S02 (DW-03): _driver.shard('k/n') keeps whole modules, shards 1..n partition the suite, order is preserved; bad specs refused."""
        import _driver

        def case(mod, name):
            cls = type("C_%s_%s" % (mod, name), (unittest.TestCase,), {name: lambda self: None, "__module__": mod})
            return cls(name)

        suite = unittest.TestSuite([unittest.TestSuite([case("m%d" % (i % 5), "test_%d" % i)]) for i in range(20)])
        parts = [[t.id() for t in _driver.shard(suite, "%d/3" % k)] for k in (1, 2, 3)]
        flat = [t.id() for t in _driver._flat(suite)]
        self.assertEqual(sorted(sum(parts, [])), sorted(flat))
        self.assertEqual(sum(len(p) for p in parts), len(flat))
        for p in parts:
            self.assertEqual(p, [x for x in flat if x in p])
            mods = set(x.split(".")[0] for x in p)
            for other in parts:
                if other is not p:
                    self.assertFalse(mods & set(x.split(".")[0] for x in other))
        for bad in ("0/2", "3/2", "x"):
            with self.assertRaises(ValueError):
                _driver.shard(suite, bad)

    def test_TST_HUB_STG20_S03_catalogue_has_no_declared_value(self):
        """S03 (FAC-05): the shipped probe catalogue has no `declared` provider; every register row has a probe; module probes are
        `observed`; the catalogue still covers the 11 INC-02 golden refs."""
        probes = compare.load_probes(grun.PROBES_PATH)
        self.assertEqual([p["golden_ref"] for p in probes if p["new"]["provider"] == "declared"], [])
        self.assertEqual(sorted(set(p["new"]["provider"] for p in probes)), ["baseline_ro", "observed"])
        refs = set(p["golden_ref"] for p in probes)
        seed = register.load_seed()
        self.assertEqual(sorted(r["dev_id"] for r in seed["deviations"]), DV_IDS)
        self.assertEqual(sorted(r["dev_id"] for r in seed["deviations"] if r["golden_ref"] not in refs), [])
        old = set(p["golden_ref"] for p in compare.load_probes(compare.PROBES_PATH))
        self.assertEqual(sorted(old - refs), [])
        self.assertEqual(sorted(p["new"]["observation"] for p in probes if p["new"]["provider"] == "observed"), sorted(observe.OBS_IDS))

    def test_TST_HUB_STG20_S04_observed_values_equal_stage16_observation(self):
        """S04 (DW-04 acceptance): every observed value equals the Stage 16 s16_observe.py observation of the same build
        (obs-laptop.json); golden-compare --observed lists every module probe with an `observed:` source."""
        with open(OBS16, encoding="utf-8") as f:
            o16 = json.load(f)
        obs = _record()["observations"]
        runs = o16["ingest"]["runs"]
        pf, vc = runs["partner_feed"], runs["vendor_csv"]
        cur = dict(("%s/%s/%s" % (s, o, r), n) for s, o, r, n in o16["intake_current_outcomes"])
        self.assertEqual(obs["intake.partner_replay"], {"NOOP_DUPLICATE": pf["noop_duplicate"], "REVISED_CONFLICT": pf["revised_conflict"]})
        self.assertEqual(obs["intake.partner_negative_quantity"], {"NEGATIVE_VALUE_items": pf["reasons"]["NEGATIVE_VALUE"],
                                                                   "flagged_value_queue": pf["queues"]["flagged_value"]})
        self.assertEqual(obs["intake.partner_outcomes"]["outcomes"], pf["outcomes"])
        self.assertEqual(obs["intake.partner_outcomes"]["legacy_table"], "untouched")
        self.assertEqual(obs["intake.partner_ref_match"], {"linked": pf["linked"], "unmatched_ref": cur["partner_feed/EXCEPTION/UNMATCHED_REF"],
                                                           "no_business_key": cur["partner_feed/EXCEPTION/NO_BUSINESS_KEY"]})
        self.assertEqual(obs["intake.vendor_tiny"], {"UNPARSABLE_AMOUNT": cur["vendor_csv/QUARANTINED/UNPARSABLE_AMOUNT"],
                                                     "kept_rows": vc["received"] - vc["outcomes"]["QUARANTINED"]})
        ev = o16["policy_evaluate"]
        self.assertEqual((ev["APAC_2026_abc"]["rc"], ev["APAC_2026_null"]["rc"]), (23, 23))
        self.assertEqual(obs["policy.js_invalid_amount"], {"abc": "E-POL-INPUT-INVALID", "null": "E-POL-INPUT-INVALID"})
        y = ev["APAC_2019"]["out"]
        self.assertEqual(obs["policy.js_unknown_year"], {"defaulted": y["defaulted"], "region": "APAC", "threshold": y["outcome"]["threshold"],
                                                         "year": 2019})
        y = ev["APAC_202_partial"]["out"]
        self.assertEqual(obs["policy.js_partial_year"]["202"], {"defaulted": y["defaulted"], "threshold": y["outcome"]["threshold"]})
        self.assertEqual(obs["intake.missing_envelope_field"], {"quarantined": 1, "reason": "MISSING_ENVELOPE_FIELD", "received": 1})
        p = S.golden_compare(S.tmpdir("s20s04-"), "--observed", T.observation())
        rep = json.loads(p.stdout)
        srcs = dict((e["golden_ref"], e["new_source"]) for e in rep["entries"])
        self.assertEqual(sorted(r for r, s in srcs.items() if not s.startswith(("observed:", "baseline_ro:"))), [])
        self.assertEqual(sum(1 for s in srcs.values() if s.startswith("observed:")), 9)
        dv11 = [e for e in rep["entries"] if e["golden_ref"].startswith("DEV-29")][0]
        self.assertEqual((dv11["legacy_source"][:14], dv11["legacy"]["202"]), ("register:DV-11", 15000))

    def test_TST_HUB_STG20_S05_stale_or_foreign_record_refused(self):
        """S05 (FAC-05): a record whose code digest or baseline does not match is refused -> module probes NOT-RUN, exit 6; a record
        is deterministic (second observation identical) and taking it leaves the FX-BASE125 copy byte-identical."""
        rec = _record()
        base = S.tmpdir("s20s05-")
        legacy_db = os.path.join(S.LEGACY_ROOT, "data", "legacy.sqlite3")
        before = S.sha256_file(legacy_db)
        p = S.run_hub(["golden-observe", "--data-dir", os.path.join(base, "o2"), "--legacy-root", S.LEGACY_ROOT, "--out",
                       os.path.join(base, "second.json")])
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        with open(os.path.join(base, "second.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f), rec)
        self.assertEqual(S.sha256_file(legacy_db), before)
        for name, change, why in (("stale", {"code_digest": "0" * 64}, "stale"),
                                  ("foreign", {"baseline": dict(rec["baseline"], **{"legacy.sqlite3": "1" * 64})}, "different baseline"),
                                  ("schema", {"schema": "x"}, "unknown schema")):
            path = os.path.join(base, name + ".json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dict(rec, **change), f)
            p = S.golden_compare(os.path.join(base, "d-" + name), "--observed", path)
            self.assertEqual(p.returncode, 6)
            r = json.loads(p.stdout)
            self.assertEqual((r["observation"]["status"], r["summary"]["NOT-RUN"]), ("refused", 9), name)
            self.assertIn(why, r["observation"]["reason"])

    def test_TST_HUB_STG20_S06_inline_observation_equals_record(self):
        """S06: `golden-compare --observe` (inline) reports the same entries as --observed <record>; without --legacy-root the
        observation is refused (NOT-RUN), not guessed."""
        a = json.loads(S.golden_compare(S.tmpdir("s20s06a-"), "--observe").stdout)
        b = json.loads(S.golden_compare(S.tmpdir("s20s06b-"), "--observed", T.observation()).stdout)
        self.assertEqual(a["entries"], b["entries"])
        self.assertEqual((a["observation"]["taken"], b["observation"]["taken"]), ("inline", "record"))
        c = json.loads(S.golden_compare(S.tmpdir("s20s06c-"), "--observe", legacy=False).stdout)
        self.assertEqual(c["observation"]["status"], "refused")
        self.assertEqual(c["exit_code"], 6)

    def test_TST_HUB_STG20_S07_register_dv01_dv11_proposed(self):
        """S07 (DW-05 / FAC-06): DV-01..DV-11 present, all `proposed`, approval_ref empty; DV-07a text; DV-09 label MISSING_ENVELOPE_FIELD;
        DV-10 (exact ref_id matching) and DV-11 (DEV-29 partial year) registered."""
        d = S.tmpdir("s20s07-")
        rows = json.loads(S.run_hub(["deviations", "--data-dir", d]).stdout)["deviation_register"]
        self.assertEqual([r["dev_id"] for r in rows], DV_IDS)
        self.assertEqual(set((r["status"], r["approval_ref"]) for r in rows), {("proposed", None)})
        by = dict((r["dev_id"], r) for r in rows)
        self.assertIn("MISSING_ENVELOPE_FIELD", by["DV-09"]["new_value"])
        self.assertNotIn("envelope_invalid", by["DV-09"]["new_value"])
        self.assertIn("DV-07a", by["DV-07"]["justification"])
        self.assertIn("UNMATCHED_REF 7,903", by["DV-07"]["justification"])
        self.assertEqual(by["DV-10"]["golden_ref"], "CT-08:batch.partner_status_after_all[ref_id match]")
        self.assertEqual(by["DV-10"]["legacy_value"], by["DV-07"]["legacy_value"])
        self.assertEqual(json.loads(by["DV-11"]["legacy_value"]), {"": 15000, "2": 15000, "202": 15000})
        self.assertTrue(all(v["defaulted"] and v["threshold"] == 999999 for v in json.loads(by["DV-11"]["new_value"]).values()))

    def test_TST_HUB_STG20_S08_refresh_touches_only_unchanged_inc02_rows(self):
        """S08 (DW-05): on an existing store, a row still byte-identical to the INC-02 seed and proposed is refreshed to the Stage 20
        text; a row a human changed (here: a TEST-FIXTURE approval, not a HAR-06 approval) is never touched; missing rows are added."""
        d = S.tmpdir("s20s08-")
        self.assertEqual(S.run_hub(["init", "--data-dir", d]).returncode, 0)
        old = dict((r["dev_id"], r) for r in register.load_seed(register.SEED_INC02_PATH)["deviations"])
        con = sqlite3.connect(os.path.join(d, "hub.sqlite3"))
        with con:
            for dv in ("DV-03", "DV-07", "DV-09"):
                o = old[dv]
                con.execute("UPDATE deviation_register SET golden_ref=?, legacy_value=?, new_value=?, justification=? WHERE dev_id=?",
                            (o["golden_ref"], o["legacy_value"], o["new_value"], o["justification"], dv))
            con.execute("UPDATE deviation_register SET status='approved', approval_ref='TEST-FIXTURE-NOT-A-HAR06-APPROVAL' WHERE dev_id='DV-03'")
            con.execute("DELETE FROM deviation_register WHERE dev_id IN ('DV-10', 'DV-11')")  # M000-only store: no delete guard yet
        con.close()
        rows = dict((r["dev_id"], r) for r in json.loads(S.run_hub(["deviations", "--data-dir", d]).stdout)["deviation_register"])
        new = dict((r["dev_id"], r) for r in register.load_seed()["deviations"])
        self.assertEqual(sorted(rows), DV_IDS)
        for dv in ("DV-07", "DV-09", "DV-10", "DV-11"):
            self.assertEqual((rows[dv]["new_value"], rows[dv]["status"]), (new[dv]["new_value"], "proposed"), dv)
        self.assertEqual((rows["DV-03"]["new_value"], rows["DV-03"]["status"]), (old["DV-03"]["new_value"], "approved"))


if __name__ == "__main__":
    unittest.main()
