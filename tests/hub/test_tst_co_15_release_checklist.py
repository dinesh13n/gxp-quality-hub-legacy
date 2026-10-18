"""TST-CO-15 (AC-CO-15, FR-CO-03, PNFR-19) - generating the pre-release checklist records G1-G10, each with a
pass/fail(/not_run) result and an evidence path; any non-pass blocks. G3/G5/G6/G7 are evaluated by
`python -m hub.admin release-checklist`; G1 is supplied from golden-compare (exit 6 by design, OD-S12-13 open);
G2/G4/G8/G9/G10 have no INC-03 evaluator and are recorded not_run (never assumed pass)."""
import json
import os
import sqlite3
import unittest

import _support as S
import _inc03 as H
from hub.ops import release


def setUpModule():
    S.require_sandbox()


class TST_CO_15_ReleaseChecklist(unittest.TestCase):

    def test_TST_CO_15_a_checklist_every_gate_recorded_and_blocking(self):
        """TST-CO-15 / AC-CO-15: 10 gates recorded with result + evidence path; G3/G5/G6/G7 pass with evidence files; --mark-ready -> exit 20."""
        base = S.tmpdir("co15-")
        cfg = H.write_config(base)
        d = os.path.join(base, "data")
        self.assertEqual(H.admin(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg).returncode, 0)
        gc_dir = os.path.join(base, "gc")
        gc = S.golden_compare(gc_dir)
        self.assertEqual(gc.returncode, 6)  # DV-01..09 UNAPPROVED by design (OD-15)
        gc_path = os.path.join(base, "golden-compare.json")
        with open(gc_path, "w") as f:
            f.write(gc.stdout)
        ev = os.path.join(base, "evidence")
        args = ["release-checklist", "--data-dir", d, "--release", "R1-inc03-dryrun", "--evidence-dir", ev,
                "--scratch-root", os.path.join(base, "scratch"), "--gate", "G1=fail:%s:golden-compare exit 6" % gc_path]
        p = H.admin(args, cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = H.out_json(p)
        self.assertEqual([g["gate"] for g in out["gates"]], list(release.GATE_IDS))
        for g in out["gates"]:
            with self.subTest(gate=g["gate"]):
                self.assertIn(g["result"], ("pass", "fail", "not_run"))
                self.assertTrue(g["evidence_path"].strip())
        res = {g["gate"]: g["result"] for g in out["gates"]}
        self.assertEqual({k: res[k] for k in ("G3", "G5", "G6", "G7")}, {"G3": "pass", "G5": "pass", "G6": "pass", "G7": "pass"})
        self.assertEqual(res["G1"], "fail")
        self.assertEqual({res[k] for k in ("G2", "G4", "G8", "G9", "G10")}, {"not_run"})
        for gate in ("G3", "G5", "G6", "G7"):
            path = [g for g in out["gates"] if g["gate"] == gate][0]["evidence_path"]
            self.assertTrue(os.path.isfile(path), path)
            json.load(open(path))
        self.assertTrue(os.path.isfile(os.path.join(ev, "checklist-R1-inc03-dryrun.json")))
        con = sqlite3.connect(os.path.join(d, "hub.sqlite3"))
        try:
            self.assertEqual(con.execute("SELECT count(*) FROM release_gate_result WHERE release_id='R1-inc03-dryrun'").fetchone()[0], 10)
        finally:
            con.close()
        p2 = H.admin(args[:3] + ["--release", "R1-inc03-dryrun-2"] + args[5:] + ["--mark-ready"], cfg)
        self.assertEqual(p2.returncode, 20, p2.stderr)
        self.assertEqual(json.loads(p2.stderr)["code"], "E-CO-RELEASE-BLOCKED")


if __name__ == "__main__":
    unittest.main()
