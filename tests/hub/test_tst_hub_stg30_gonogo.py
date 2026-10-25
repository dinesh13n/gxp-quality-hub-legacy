"""Stage 30 tests, part 2: the go / no-go evaluator and the shipped release register. Synthetic, unvalidated.

  G01  the register is consistent: unique ids, every DV row belongs to exactly one cutover step, the gate ids are the hub release gates
  G02  the SHIPPED approvals register has every record OPEN with no approver, reference or date; against the shipped results the decision is NO-GO
  G03  APPROVED records that are not valid (agent or system approver, no reference, bad date, no pointer) do not count; REJECTED never counts
  G04  control (test-only, synthetic names): all criteria pass and all required approvals valid -> GO; one failing criterion or one missing approval -> NO-GO
  G05  malformed documents are refused (unknown id, duplicate id, bad status, wrong schema) and the CLI exits 2
  G06  the CLI: shipped inputs -> exit 1 NO-GO; register -> 0; posture of the shipped defaults -> 0; a non-default flag, Zone H holders, a bind or a schedule -> 1
  G07  the shipped gate-results.json is valid, every pass has an evidence file, and G1 is not a pass while the DV rows are open
"""
import copy
import json
import os
import subprocess
import sys
import unittest

import _stg30 as T
import _support as S
from hub import config
from hub.ops import release as ops_release
from hub.release import gonogo, register

HUMAN = "Synthetic Approver Example"


def setUpModule():
    T.skip_in_inner_egress_run()


def shipped():
    return T.read_json(os.path.join(T.EVID, "gate-results.json")), T.read_json(os.path.join(T.EVID, "approvals-register.json"))


def all_pass():
    return {"schema": gonogo.RESULTS_SCHEMA, "results": dict((c, {"result": "pass", "evidence_path": "synthetic/%s.json" % c}) for c in register.TECHNICAL_IDS)}


def approvals(ids, **over):
    recs = []
    for i in register.approval_ids():
        r = {"id": i, "status": "OPEN", "approver": None, "approval_ref": None, "approved_on": None, "evidence_ref": None}
        if i in ids:
            r.update(status="APPROVED", approver=HUMAN, approval_ref="SYNTHETIC-REF-%s" % i, approved_on="2026-01-02", evidence_ref="synthetic/decisions.md")
            r.update(over)
        recs.append(r)
    return {"schema": gonogo.APPROVALS_SCHEMA, "records": recs}


def cli(*args):
    return subprocess.run([sys.executable, "-B", "-m", "hub.release"] + list(args), cwd=S.CODE_ROOT, env=S.child_env(), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True, timeout=120)


class TST_HUB_STG30_GoNoGo(unittest.TestCase):

    def test_TST_HUB_STG30_G01_register_is_consistent(self):
        """G01: ids unique; each of DV-01..DV-11 sits in exactly one cutover step; gates are the hub's G1..G10; step needs include their DV rows."""
        ids = register.approval_ids()
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(register.GATE_IDS, ops_release.GATE_IDS)
        placed = [d for c in register.CUT_STEPS for d in c["dv"]]
        self.assertEqual(sorted(placed), sorted(register.DV_IDS))
        self.assertEqual(len(register.DV_IDS), 11)
        for c in register.CUT_STEPS:
            need = register.required_for_step(c["id"])
            self.assertIn("AP-" + c["id"], need)
            for d in c["dv"]:
                self.assertIn("AP-" + d, need)
        self.assertEqual(len(register.required_for_release()), 1 + 10 + 11)
        self.assertEqual(len(register.TECHNICAL_IDS), 20)
        self.assertEqual(len(register.TECHNICAL_IDS), len(set(register.TECHNICAL_IDS)))

    def test_TST_HUB_STG30_G02_shipped_register_is_open_and_no_go(self):
        """G02: 40 records, all OPEN, every human field empty; evaluating the shipped results + approvals -> NO-GO, 0 approvals counting, every CUT step NO-GO."""
        results, appr = shipped()
        self.assertEqual([r["id"] for r in appr["records"]], list(register.approval_ids()))
        for r in appr["records"]:
            self.assertEqual((r["status"], r["approver"], r["approval_ref"], r["approved_on"], r["evidence_ref"]), ("OPEN", None, None, None, None), r["id"])
            self.assertEqual(r["owner"], "Engagement lead (Dinesh Naik)")
        rep = gonogo.evaluate(results, appr)
        self.assertEqual(rep["decision"], "NO-GO")
        self.assertEqual(rep["counts"]["approvals"], 40)
        self.assertEqual(rep["counts"]["approvals_counting"], 0)
        self.assertEqual(sorted(rep["release_approvals_missing"]), sorted(register.required_for_release()))
        self.assertEqual(rep["invalid_approved_records"], [])
        self.assertEqual([s["decision"] for s in rep["steps"].values()], ["NO-GO"] * 5)
        T.write_evidence("g02-shipped-evaluation.json", {"decision": rep["decision"], "technical_blocking": rep["technical_blocking"], "counts": rep["counts"]})

    def test_TST_HUB_STG30_G03_invalid_or_machine_made_approvals_do_not_count(self):
        """G03: with every criterion passing, a record approved by an agent / system name, without a reference, with a bad date or without a pointer does not count."""
        bad = (
            dict(approver="Claude"), dict(approver="claude-fde-agent"), dict(approver="orchestrator"), dict(approver="hub system"), dict(approver="AI Advisor"),
            dict(approver="  "), dict(approver=None), dict(approval_ref=None), dict(approval_ref="  "), dict(approved_on="today"), dict(approved_on="2026-13-02"),
            dict(approved_on="2026-01-32"), dict(approved_on=None), dict(evidence_ref=None), dict(evidence_ref=""),
        )
        for over in bad:
            doc = approvals(register.required_for_release(), **over)
            rep = gonogo.evaluate(all_pass(), doc)
            self.assertEqual(rep["decision"], "NO-GO", over)
            self.assertEqual(sorted(rep["release_approvals_missing"]), sorted(register.required_for_release()), over)
            self.assertEqual(sorted(rep["invalid_approved_records"]), sorted(register.required_for_release()), over)
        rej = approvals(register.required_for_release(), status="REJECTED")
        self.assertEqual(gonogo.evaluate(all_pass(), rej)["decision"], "NO-GO")
        self.assertEqual(gonogo.approval_problems({"approver": "Naik Example", "approval_ref": "R", "approved_on": "2026-01-02", "evidence_ref": "x"}), [])

    def test_TST_HUB_STG30_G04_control_all_good_is_go_and_one_gap_is_no_go(self):
        """G04 (synthetic control, test-only): release GO needs criteria + release approvals; a step also needs its own; any single gap flips to NO-GO."""
        doc = approvals(register.required_for_release())
        rep = gonogo.evaluate(all_pass(), doc)
        self.assertEqual(rep["decision"], "GO")
        self.assertEqual([s["decision"] for s in rep["steps"].values()], ["NO-GO"] * 5)  # steps need their own approvals
        full = approvals(set(register.approval_ids()))
        rep = gonogo.evaluate(all_pass(), full)
        self.assertEqual([s["decision"] for s in rep["steps"].values()], ["GO"] * 5)
        res = all_pass()
        res["results"]["G7"]["result"] = "fail"
        rep = gonogo.evaluate(res, full)
        self.assertEqual((rep["decision"], rep["technical_blocking"]), ("NO-GO", ["G7"]))
        self.assertEqual([s["decision"] for s in rep["steps"].values()], ["NO-GO"] * 5)
        res = all_pass()
        del res["results"]["T-03"]
        self.assertEqual(gonogo.evaluate(res, full)["technical_blocking"], ["T-03"])  # no result = not_run = blocking
        partial = copy.deepcopy(full)
        for r in partial["records"]:
            if r["id"] == "AP-OPS-04":
                r["status"] = "OPEN"
        rep = gonogo.evaluate(all_pass(), partial)
        self.assertEqual((rep["decision"], rep["release_approvals_missing"]), ("NO-GO", ["AP-OPS-04"]))

    def test_TST_HUB_STG30_G05_malformed_documents_are_refused(self):
        """G05: unknown / duplicate id, bad status, wrong schema, unknown criterion, bad result -> RegisterInvalid; the CLI turns each into exit 2."""
        good = approvals(())
        cases = []
        d = copy.deepcopy(good); d["records"][0]["id"] = "AP-NOPE"; cases.append(("approvals", d))
        d = copy.deepcopy(good); d["records"].append(copy.deepcopy(d["records"][0])); cases.append(("approvals", d))
        d = copy.deepcopy(good); d["records"][0]["status"] = "MAYBE"; cases.append(("approvals", d))
        d = copy.deepcopy(good); d["schema"] = "other/v1"; cases.append(("approvals", d))
        r = all_pass(); r["results"]["T-99"] = {"result": "pass"}; cases.append(("results", r))
        r = all_pass(); r["results"]["G1"]["result"] = "passed"; cases.append(("results", r))
        for kind, d in cases:
            with self.assertRaises(gonogo.RegisterInvalid):
                gonogo.evaluate(d, good) if kind == "results" else gonogo.evaluate(all_pass(), d)
        tmp = S.tmpdir("g05-")
        rp, ap = os.path.join(tmp, "r.json"), os.path.join(tmp, "a.json")
        for kind, d in cases:
            json.dump(d if kind == "results" else all_pass(), open(rp, "w"))
            json.dump(good if kind == "results" else d, open(ap, "w"))
            p = cli("evaluate", "--results", rp, "--approvals", ap)
            self.assertEqual(p.returncode, 2, (kind, p.stderr))
            self.assertIn("unreadable or invalid input", p.stderr)
        self.assertEqual(cli("evaluate", "--results", os.path.join(tmp, "missing.json"), "--approvals", ap).returncode, 2)

    def test_TST_HUB_STG30_G06_cli_exit_codes_and_posture(self):
        """G06: shipped inputs -> rc 1 with decision NO-GO; `register` rc 0; shipped defaults pass the posture check; each unsafe setting is a violation (rc 1)."""
        p = cli("evaluate", "--results", os.path.join(T.EVID, "gate-results.json"), "--approvals", os.path.join(T.EVID, "approvals-register.json"))
        self.assertEqual(p.returncode, 1)
        self.assertEqual(json.loads(p.stdout)["decision"], "NO-GO")
        reg = json.loads(cli("register").stdout)
        self.assertEqual(len(reg["gates"]), 10)
        self.assertEqual(cli("posture").returncode, 0)
        tmp = S.tmpdir("g06-")
        unsafe = {
            "authority": ({"capability_authority": {"CUT-2": "authoritative"}, "approval_refs": {"capability_authority.CUT-2": "SYNTHETIC-REF"}}, "non-default decision flag"),
            "holders": ({"zone_h": {"holders": ["synthetic-holder"]}, "approval_refs": {"zone_h.holders": "SYNTHETIC-REF"}}, "zone_h.holders"),
            "bind": ({"network": {"bind": "0.0.0.0"}}, "bind is not loopback"),
            "kill": ({"hub": {"kill": True}}, "kill switch set"),
        }
        for name, (cfg, expect) in sorted(unsafe.items()):
            path = os.path.join(tmp, name + ".json")
            json.dump(cfg, open(path, "w"))
            p = cli("posture", "--config", path)
            self.assertEqual(p.returncode, 1, (name, p.stdout, p.stderr))
            self.assertTrue(any(expect in v for v in json.loads(p.stdout)["violations"]), (name, p.stdout))
        self.assertEqual(gonogo.posture(config.load(None)), [])

    def test_TST_HUB_STG30_G07_shipped_gate_results_are_honest(self):
        """G07: gate-results.json validates; every 'pass' names an evidence file that exists; G1 is not a pass (DV rows proposed, golden-compare exit 6); no result claims a human approval."""
        results, appr = shipped()
        res = gonogo.check_results_doc(results)
        self.assertEqual(sorted(res), sorted(register.TECHNICAL_IDS))
        for cid, r in sorted(res.items()):
            self.assertIn(r["result"], gonogo.RESULTS)
            if r["result"] == "pass":
                self.assertTrue(r.get("evidence_path"), cid)
                self.assertTrue(os.path.exists(os.path.join(S.CODE_ROOT, r["evidence_path"])), (cid, r["evidence_path"]))
            self.assertNotIn("approved by", json.dumps(r).lower(), cid)
        self.assertNotEqual(res["G1"]["result"], "pass")
        self.assertNotEqual(res["T-09"]["result"], "pass")
        self.assertNotEqual(res["T-10"]["result"], "pass")


if __name__ == "__main__":
    unittest.main()
