"""TST-CO-01 (AC-CO-01, FR-CO-01, BEH-CO-01/02) - golden-compare on the 125-case baseline (sandbox copy, FX-BASE125).

Given all deviation_register rows `proposed`, every difference from DV-01..DV-11 is listed UNAPPROVED and the
exit code is non-zero (6); with matching approved rows the exit code is 0.
Stage 20 (DW-04 / DW-05, FAC-05 / FAC-06): the module probes are OBSERVED from the built modules (one `golden-observe` record per
module run, passed with --observed); the register holds DV-01..DV-11. Without an observation the module probes are NOT-RUN
(no declared value is ever used) and the gate still fails (exit 6).
NOTE: the "approved" rows below are TEST FIXTURES written into a throw-away sandbox hub DB. They are not
HAR-06 approvals and the product has no command that approves a deviation (BEH-CO-02).
"""
import json
import os
import sqlite3
import unittest

import _support as S
from hub.adapters.legacy_sqlite import load_pins
from hub.golden.compare import canonical

DV_IDS = ["DV-%02d" % i for i in range(1, 12)]
_OBS = {}


def setUpModule():
    S.require_sandbox()


def observed():
    """One observation record of the built modules for this module run (Stage 20 DW-04)."""
    if "path" not in _OBS:
        d = S.tmpdir("co01obs-")
        p = S.run_hub(["golden-observe", "--data-dir", d, "--legacy-root", S.LEGACY_ROOT])
        assert p.returncode == 0, p.stderr[-2000:]
        _OBS["path"] = os.path.join(d, "runs", "golden-observe", "observation.json")
    return _OBS["path"]


def _gc(d):
    return S.golden_compare(d, "--observed", observed())


def _approve_all(data_dir, tweak=None):
    con = sqlite3.connect(os.path.join(data_dir, "hub.sqlite3"))
    with con:
        con.execute("UPDATE deviation_register SET status='approved', "
                    "approval_ref='TEST-FIXTURE-NOT-A-HAR06-APPROVAL-' || dev_id")
        if tweak:
            con.execute(tweak)
    con.close()


class TST_CO_01_GoldenCompareBaseline(unittest.TestCase):

    def test_TST_CO_01_a_all_proposed_dv01_dv11_unapproved_exit6(self):
        """TST-CO-01 / AC-CO-01 positive: register all proposed -> 11 UNAPPROVED (DV-01..DV-11), exit 6."""
        d = S.tmpdir("co01a-")
        p = _gc(d)
        self.assertEqual(p.returncode, 6, p.stderr)
        rep = json.loads(p.stdout)
        self.assertEqual(rep["error"], "E-CO-UNAPPROVED-DEVIATION")
        unapproved = [e for e in rep["entries"] if e["disposition"] == "UNAPPROVED"]
        self.assertEqual(len(unapproved), 11)
        devs = sorted(r["dev_id"] for e in unapproved for r in e.get("register", []))
        self.assertEqual(devs, DV_IDS)
        for e in unapproved:
            self.assertEqual([r["status"] for r in e["register"]], ["proposed"])
        self.assertEqual(rep["summary"]["identical"], 2)
        self.assertEqual(rep["summary"]["NOT-RUN"], 0)
        self.assertEqual(rep["observation"]["status"], "used")
        # evidence that the run used the OD-09 baseline through read-only snapshots
        pins = load_pins()
        self.assertEqual(rep["baseline"]["legacy.sqlite3"]["source_sha256"], pins["legacy.sqlite3"]["sha256"])
        self.assertTrue(rep["baseline"]["legacy.sqlite3"]["source_sha256"].startswith("c254649f57e2"))
        self.assertEqual(rep["baseline"]["enterprise_legacy.sqlite3"]["access"], "mode=ro&immutable=1")
        self.assertEqual(rep["tripwires"], {"egress_attempts_total": 0, "model_calls_total": 0})
        # DV-01 is computed live on the baseline: 742,956.61 (legacy) vs 622,826.44 (new)
        dv01 = [e for e in rep["entries"] if e["golden_ref"] == "CT-12:batch.sql_report_1_total_gross"][0]
        self.assertEqual((dv01["legacy"], dv01["new"]), (742956.61, 622826.44))
        # FAC-05: no new-side value is declared
        self.assertEqual([e["golden_ref"] for e in rep["entries"] if str(e.get("new_source", "")).startswith("declared:")], [])

    def test_TST_CO_01_b_register_describes_the_actual_goldens(self):
        """TST-CO-01: each DV row's legacy_value/new_value equals the observed legacy/new value (canonical JSON)."""
        d = S.tmpdir("co01b-")
        rep = json.loads(_gc(d).stdout)
        dv = json.loads(S.run_hub(["deviations", "--data-dir", d]).stdout)["deviation_register"]
        by_ref = dict((e["golden_ref"], e) for e in rep["entries"])
        self.assertEqual(sorted(r["dev_id"] for r in dv), DV_IDS)
        for r in dv:
            e = by_ref[r["golden_ref"]]
            self.assertEqual(r["legacy_value"], canonical(e["legacy"]), r["dev_id"])
            self.assertEqual(r["new_value"], canonical(e["new"]), r["dev_id"])
            self.assertEqual(r["status"], "proposed")
            self.assertIsNone(r["approval_ref"])

    def test_TST_CO_01_c_matching_approved_rows_exit0(self):
        """TST-CO-01 / AC-CO-01: with matching approved rows (test fixture) -> every DV approved_deviation, exit 0."""
        d = S.tmpdir("co01c-")
        self.assertEqual(S.run_hub(["init", "--data-dir", d]).returncode, 0)
        _approve_all(d)
        p = _gc(d)
        self.assertEqual(p.returncode, 0, p.stdout[-2000:])
        rep = json.loads(p.stdout)
        self.assertEqual(rep["summary"]["approved_deviation"], 11)
        self.assertEqual(rep["summary"]["UNAPPROVED"], 0)
        for e in rep["entries"]:
            if e["disposition"] != "identical":
                self.assertRegex(e["disposition"], r"^approved_deviation\(DV-(0[1-9]|1[01]), TEST-FIXTURE-NOT-A-HAR06-APPROVAL-DV-(0[1-9]|1[01])\)$")

    def test_TST_CO_01_d_approval_must_match_observed_values(self):
        """TST-CO-01: an approved row whose new_value differs from the observed value does not cover the diff."""
        d = S.tmpdir("co01d-")
        S.run_hub(["init", "--data-dir", d])
        _approve_all(d, "UPDATE deviation_register SET new_value='622826.45' WHERE dev_id='DV-01'")
        p = _gc(d)
        self.assertEqual(p.returncode, 6)
        rep = json.loads(p.stdout)
        self.assertEqual(rep["summary"]["UNAPPROVED"], 1)
        self.assertEqual([e["golden_ref"] for e in rep["entries"] if e["disposition"] == "UNAPPROVED"],
                         ["CT-12:batch.sql_report_1_total_gross"])

    def test_TST_CO_01_e_approved_requires_approval_ref(self):
        """TST-CO-01 / BEH-CO-02: status 'approved' with an empty approval_ref is rejected by the store."""
        d = S.tmpdir("co01e-")
        S.run_hub(["init", "--data-dir", d])
        con = sqlite3.connect(os.path.join(d, "hub.sqlite3"))
        with self.assertRaises(sqlite3.IntegrityError):
            with con:
                con.execute("UPDATE deviation_register SET status='approved', approval_ref='  ' WHERE dev_id='DV-01'")
        con.close()

    def test_TST_CO_01_f_without_observation_module_probes_not_run(self):
        """TST-CO-01 / FAC-05 (Stage 20): no observation supplied -> the 9 module probes are NOT-RUN (never declared), DV-01 / DV-08
        (baseline_ro) UNAPPROVED, exit 6 even with every row approved."""
        d = S.tmpdir("co01f-")
        S.run_hub(["init", "--data-dir", d])
        _approve_all(d)
        p = S.golden_compare(d)
        self.assertEqual(p.returncode, 6)
        rep = json.loads(p.stdout)
        self.assertEqual((rep["summary"]["NOT-RUN"], rep["observation"]["status"]), (9, "not supplied"))
        for e in rep["entries"]:
            self.assertFalse(str(e.get("new_source", "")).startswith("declared:"), e["golden_ref"])
            if e["disposition"] == "NOT-RUN":
                self.assertIn("module observation not supplied", e["reason"])


if __name__ == "__main__":
    unittest.main()
