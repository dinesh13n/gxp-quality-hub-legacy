"""Stage 27 tests, part 4: SBOM, CI additions and the structure ratchet (DW-27; AC-HRD-07 .. AC-HRD-10; deviations S27-DEV-11, S27-DEV-12). Synthetic, unvalidated.

  B01  SBOM: CycloneDX 1.5, deterministic, every hub package listed, stdlib only (no third-party import), file digests change when a file changes, a third-party import is flagged
  B02  the committed SBOM (docs/27-hardening/evidence/sbom.cdx.json) is well-formed and lists no third-party component; the tool itself imports only stdlib and no time / random
  C01  the CI additions (ci/hub-hardening.yml): 3.12 and 3.13, No-AI gate, least privilege, no .github change, no secrets, no unsafe constructs
  S01  structure ratchet from the S20 static checks: 0 two-cycles, 0 three-cycles, 0 domain-to-web imports, at most 9 functions over complexity 15, WebApp._dispatch under 15
"""
import ast
import json
import os
import re
import subprocess
import sys
import unittest

import _stg27 as T
from hub.security import sbom

ROOT = T.S.CODE_ROOT


def setUpModule():
    T.skip_in_inner_egress_run()


class TST_HUB_STG27_Supply(unittest.TestCase):

    def test_TST_HUB_STG27_B01_sbom_is_deterministic_stdlib_only_and_hash_sensitive(self):
        """B01: CycloneDX 1.5 with a content-derived serial number and no timestamp; two builds are identical; one library component per hub package; every import is stdlib
        (third_party() == []); a changed file changes its package digest and the serial number; a planted third-party import is flagged and labelled UNREVIEWED."""
        a, b = sbom.build(ROOT), sbom.build(ROOT)
        self.assertEqual(sbom.dumps(a), sbom.dumps(b))
        self.assertEqual((a["bomFormat"], a["specVersion"]), ("CycloneDX", "1.5"))
        self.assertRegex(a["serialNumber"], r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
        self.assertNotIn("timestamp", json.dumps(a))
        pkgs = sorted(c["name"] for c in a["components"] if c["bom-ref"].startswith("src:"))
        dirs = sorted("hub." + d for d in os.listdir(os.path.join(ROOT, "hub")) if os.path.isdir(os.path.join(ROOT, "hub", d)) and d != "__pycache__")
        for d in dirs:
            self.assertIn(d, pkgs, d)
        self.assertEqual(sbom.third_party(ROOT), [])
        self.assertEqual([c["name"] for c in a["components"] if c["properties"] and {"name": "origin", "value": "third-party-UNREVIEWED"} in c["properties"]], [])
        self.assertIn("sqlite3", [c["name"] for c in a["components"]])
        d = T.S.tmpdir("s27-sbom-")
        os.makedirs(os.path.join(d, "hub", "x"))
        os.makedirs(os.path.join(d, "app"))
        with open(os.path.join(d, "hub", "x", "m.py"), "w") as f:
            f.write("import os\nimport json\n")
        with open(os.path.join(d, "app", "a.py"), "w") as f:
            f.write("import sqlite3\n")
        s1 = sbom.build(d)
        self.assertEqual(sbom.third_party(d), [])
        with open(os.path.join(d, "hub", "x", "m.py"), "w") as f:
            f.write("import os\nimport json\nimport requests\n")
        s2 = sbom.build(d)
        h = lambda doc: [c for c in doc["components"] if c["bom-ref"] == "src:hub.x"][0]["hashes"][0]["content"]
        self.assertNotEqual(h(s1), h(s2))
        self.assertNotEqual(s1["serialNumber"], s2["serialNumber"])
        self.assertEqual(sbom.third_party(d), ["requests"])
        flagged = [c for c in s2["components"] if c["name"] == "requests"][0]
        self.assertIn({"name": "origin", "value": "third-party-UNREVIEWED"}, flagged["properties"])

    def test_TST_HUB_STG27_B02_committed_sbom_is_well_formed_and_the_tool_is_pure(self):
        """B02: the committed SBOM parses, is CycloneDX 1.5, has the application component and the python base image, lists no third-party component; hub/security/sbom.py
        imports only stdlib modules and neither time, datetime, random, uuid, socket nor subprocess (so it can not make the output non-deterministic or reach out)."""
        with open(os.path.join(ROOT, "docs", "27-hardening", "evidence", "sbom.cdx.json"), encoding="utf-8") as f:
            doc = json.load(f)
        self.assertEqual((doc["bomFormat"], doc["specVersion"]), ("CycloneDX", "1.5"))
        self.assertEqual(doc["metadata"]["component"]["name"], "gxp-quality-hub")
        origins = [p["value"] for c in doc["components"] for p in c.get("properties", []) if p["name"] == "origin"]
        self.assertNotIn("third-party-UNREVIEWED", origins)
        self.assertEqual([c["name"] for c in doc["components"] if c["type"] == "container"], ["python"])
        self.assertGreaterEqual(len([c for c in doc["components"] if c["bom-ref"].startswith("src:hub.")]), 20)
        with open(os.path.join(ROOT, "hub", "security", "sbom.py"), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods.update(a.name.split(".")[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom):
                mods.add((n.module or "").split(".")[0])
        self.assertTrue(mods <= set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else True, mods)
        self.assertEqual(mods & {"time", "datetime", "random", "uuid", "socket", "subprocess", "urllib", "http"}, set())

    def test_TST_HUB_STG27_C01_ci_additions_are_least_privilege_and_do_not_touch_github(self):
        """C01 (S27-DEV-12): ci/hub-hardening.yml runs Python 3.12 and 3.13, the No-AI gate, the SBOM reproducibility check and the static checks; it has read-only permissions, no
        secrets, no pull_request_target, no continue-on-error, no download-and-execute, and states that it is not active; .github/workflows holds only the legacy verify.yml."""
        p = os.path.join(ROOT, "ci", "hub-hardening.yml")
        with open(p, encoding="utf-8") as f:
            y = f.read()
        for needle in ('"3.12"', '"3.13"', "hub --floor 3.12 selfcheck", "no-ai-check", "hub.security.sbom", "s20_static_checks.py", "permissions:", "contents: read",
                       "actions/checkout@v4", "actions/setup-python@v5", "NOT ACTIVE", "Dinesh", "scan.run"):
            self.assertIn(needle, y, needle)
        for bad in ("secrets.", "pull_request_target", "continue-on-error", "curl ", "wget ", "| sh", "| bash", "pip install", "sudo ", "write-all", "contents: write", "::set-output"):
            self.assertNotIn(bad, y, bad)
        self.assertEqual(len(re.findall(r"^permissions:", y, re.M)), 1)
        wf = os.path.join(ROOT, ".github", "workflows")
        self.assertEqual(sorted(os.listdir(wf)), ["verify.yml"])
        self.assertFalse(os.path.exists(os.path.join(ROOT, ".github", "workflows", "hub-hardening.yml")))
        with open(os.path.join(wf, "verify.yml"), encoding="utf-8") as f:
            self.assertIn('python-version: "3.12"', f.read())

    def test_TST_HUB_STG27_S01_structure_ratchet(self):
        """S01 (OD-27 debt): the S20 static checks on this tree report 0 two-cycles, 0 three-cycles, 0 domain-to-web imports and at most 9 functions over complexity 15 (10 before
        Stage 27); WebApp._dispatch, _read_body and _session are each at or under 15. The ratchet only goes down: a new cycle or a new complex function fails here."""
        out = os.path.join(T.S.tmpdir("s27-static-"), "static.json")
        script = os.path.join(ROOT, "docs", "20-application", "evidence", "s20_static_checks.py")
        p = subprocess.run([sys.executable, "-B", script, ROOT, "--out", out], cwd=ROOT, env=T.S.child_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           universal_newlines=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stdout[-800:])
        with open(out, encoding="utf-8") as f:
            res = json.load(f)
        c = res["counts"]
        self.assertEqual((c["two_cycles"], c["three_cycles"], c["domain_to_web_files"]), (0, 0, 0), res["graph"]["two_cycles"] + res["graph"]["three_cycles"])
        self.assertLessEqual(c["complexity_over_15"], 9, [(x["file"], x["function"], x["complexity"]) for x in res["complexity_over_15"]])
        worst = dict(((x["file"], x["function"]), x["complexity"]) for x in res["complexity_over_15"])
        for fn in ("_dispatch", "_read_body", "_session"):
            self.assertNotIn(("hub/web/app.py", fn), worst, fn)
        T.write_evidence("structure-ratchet.json", {"label": T.LABEL, "counts": c, "over_15": sorted("%s:%s=%d" % (k[0], k[1], v) for k, v in worst.items())})


if __name__ == "__main__":
    unittest.main()
