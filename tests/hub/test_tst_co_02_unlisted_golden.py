"""TST-CO-02 (AC-CO-02, FR-CO-01) - a change that alters an UNLISTED golden (e.g. the priority of one case)
is reported UNAPPROVED and fails (exit 6). Fixture FX-UNIT-SYNTHETIC (temporary synthetic goldens) plus one
check against the real goldens with a substituted new-side observation.
"""
import json
import os
import unittest

import _support as S
from hub.adapters.legacy_captures import CaptureSet
from hub.golden import compare


def setUpModule():
    S.require_sandbox()


def _synthetic_goldens(root):
    os.makedirs(root)
    api = {"api_all_cases_priority": [["C1", "OPEN", "HIGH", 100.0, "queue"], ["C2", "CLOSED", "LOW", 5.0, "archive"]]}
    with open(os.path.join(root, "api.json"), "w") as f:
        json.dump(api, f)
    with open(os.path.join(root, "INDEX.json"), "w") as f:
        json.dump({"schema": "golden-index/v1", "sources": {"api": "api.json"}}, f)
    with open(os.path.join(root, "MANIFEST.sha256"), "w") as f:
        for fn in ("api.json", "INDEX.json"):
            f.write("%s  %s\n" % (S.sha256_file(os.path.join(root, fn)), fn))


PROBE = {"golden_ref": "CT-02:api.api_all_cases_priority[C1].priority",
         "legacy": {"source": "api", "path": ["api_all_cases_priority", 0, 4]},
         "new": {"provider": "declared", "value": "queue", "basis": "synthetic"}}


class TST_CO_02_UnlistedGolden(unittest.TestCase):

    def setUp(self):
        self.base = S.tmpdir("co02-")
        self.golden = os.path.join(self.base, "golden")
        _synthetic_goldens(self.golden)
        self.probes = os.path.join(self.base, "probes.json")
        with open(self.probes, "w") as f:
            json.dump({"probes": [PROBE]}, f)

    def _run(self, observations=None):
        args = ["golden-compare", "--json", "--data-dir", os.path.join(self.base, "hubdata"),
                "--probes", self.probes, "--golden-dir", self.golden]
        if observations is not None:
            obs = os.path.join(self.base, "obs.json")
            with open(obs, "w") as f:
                json.dump(observations, f)
            args += ["--observations", obs]
        return S.run_hub(args)

    def test_TST_CO_02_a_unchanged_priority_is_identical(self):
        """TST-CO-02 control: unchanged priority -> identical, exit 0."""
        p = self._run()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["entries"][0]["disposition"], "identical")

    def test_TST_CO_02_b_changed_priority_of_one_case_unapproved_exit6(self):
        """TST-CO-02 / AC-CO-02 negative: priority of C1 changes queue -> review; no register row -> UNAPPROVED, exit 6."""
        p = self._run({PROBE["golden_ref"]: "review"})
        self.assertEqual(p.returncode, 6)
        rep = json.loads(p.stdout)
        e = rep["entries"][0]
        self.assertEqual((e["legacy"], e["new"], e["disposition"]), ("queue", "review", "UNAPPROVED"))
        self.assertNotIn("register", e)
        self.assertEqual(rep["error"], "E-CO-UNAPPROVED-DEVIATION")

    def test_TST_CO_02_c_approval_for_another_golden_does_not_leak(self):
        """TST-CO-02: an approved DV for a different golden_ref never covers this difference (pure engine)."""
        caps = CaptureSet.from_golden_dir(self.golden)
        rows = [{"dev_id": "DV-99", "golden_ref": "CT-12:other", "legacy_value": '"queue"', "new_value": '"review"',
                 "approval_ref": "TEST-FIXTURE", "status": "approved"}]
        rep = compare.compare([PROBE], caps, {PROBE["golden_ref"]: ("review", "test")}, rows)
        self.assertEqual(rep["entries"][0]["disposition"], "UNAPPROVED")
        self.assertEqual(rep["exit_code"], 6)

    def test_TST_CO_02_d_missing_capture_is_not_run_and_fails(self):
        """TST-CO-02 / AD-08: a probe whose capture is missing is NOT-RUN and the gate fails (exit 6)."""
        caps = CaptureSet.from_golden_dir(self.golden)
        probe = dict(PROBE, legacy={"source": "batch", "path": ["x"]})
        rep = compare.compare([probe], caps, {PROBE["golden_ref"]: ("queue", "test")}, [])
        self.assertEqual(rep["entries"][0]["disposition"], "NOT-RUN")
        self.assertEqual(rep["exit_code"], 6)

    def test_TST_CO_02_e_real_goldens_unlisted_change_fails(self):
        """TST-CO-02 on the real goldens: CT-12 true_total_amount (no DV row) altered by 0.01 -> UNAPPROVED.
        Stage 20 (DW-04): without an observation record the 9 module probes are NOT-RUN, so UNAPPROVED = DV-01 + DV-08 + this one."""
        d = S.tmpdir("co02e-")
        obs = os.path.join(d, "obs.json")
        with open(obs, "w") as f:
            json.dump({"CT-12:batch.true_total_amount": 622826.45}, f)
        p = S.golden_compare(os.path.join(d, "hubdata"), "--observations", obs)
        self.assertEqual(p.returncode, 6)
        rep = json.loads(p.stdout)
        e = [x for x in rep["entries"] if x["golden_ref"] == "CT-12:batch.true_total_amount"][0]
        self.assertEqual(e["disposition"], "UNAPPROVED")
        self.assertNotIn("register", e)
        self.assertEqual((rep["summary"]["UNAPPROVED"], rep["summary"]["NOT-RUN"]), (3, 9))

    def test_TST_CO_02_f_tampered_golden_refused(self):
        """TST-CO-02 / AD-08 integrity: a golden changed outside the reviewed path is refused (E-FX-HASH)."""
        with open(os.path.join(self.golden, "api.json"), "a") as f:
            f.write(" ")
        p = self._run()
        self.assertEqual(p.returncode, 2)
        self.assertEqual(S.error_code(p), "E-FX-HASH")


if __name__ == "__main__":
    unittest.main()
