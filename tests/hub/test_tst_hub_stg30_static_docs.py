"""Stage 30 tests, part 4: static guarantees and the document set. Synthetic, unvalidated.

  D01  hub/release imports no clock, random, socket, HTTP client, subprocess or web layer; it defines no error code; nothing outside hub/release and the tests
       imports it (not wired); the non-add allow-list is the Stage 30 one
  D02  the 11 required artifacts exist with the front matter and the eight sections, a status that is not APPROVED, and the synthetic label
  D03  docs agree with the register: every approval id is in release-approvals.md, every criterion id in go-no-go-criteria.md, every carried decision
       (D-27-nn, D-28-nn, D-31-nn) is listed, and the outcome document says the release was not executed
  D04  shipped state: the hub-hardening workflow is not installed under .github, no config file sets an authority switch, the shipped posture is clean, zone_h.holders is empty, no real holder is named
  D05  the evidence folder's SHA256SUMS verifies and covers every file in it
"""
import ast
import json
import os
import re
import subprocess
import unittest

import _stg30 as T
import _support as S
from hub import config
from hub.release import gonogo, register

PKG = os.path.join(S.CODE_ROOT, "hub", "release")
ARTIFACTS = ("release-plan", "environment-promotion-plan", "deployment-strategy", "feature-flag-plan", "cutover-checklist", "go-no-go-criteria", "rollback-plan",
             "backup-validation", "release-approvals", "deployment-evidence", "release-outcome")
SECTIONS = ("## Summary", "## Findings", "## Evidence References", "## Assumptions", "## Unknowns", "## Unresolved Issues", "## Residual Risks", "## Change History")
FORBIDDEN = ("time", "datetime", "random", "secrets", "socket", "subprocess", "urllib", "http")
EXPECTED_EDITS = ["hub/admin/cli.py", "hub/security/audit.py", "tests/hub/non_add_edits.json", "tests/hub/regression_groups.json",
                  "tests/hub/test_tst_hub_stg31_static_docs.py"]


def setUpModule():
    T.skip_in_inner_egress_run()


def read(rel):
    with open(os.path.join(S.CODE_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def imports(text):
    mods = []
    for n in ast.walk(ast.parse(text)):
        if isinstance(n, ast.Import):
            mods += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            mods += [n.module or ""] + [(n.module or "") + "." + a.name for a in n.names]
    return mods


class TST_HUB_STG30_Static(unittest.TestCase):

    def test_TST_HUB_STG30_D01_package_is_pure_and_not_wired(self):
        """D01: no forbidden import in hub/release; no E-* code literal; no other hub module imports it; the non-add list is exactly the Stage 30 list."""
        for fn in sorted(os.listdir(PKG)):
            if not fn.endswith(".py"):
                continue
            text = read("hub/release/" + fn)
            for m in imports(text):
                self.assertNotIn(m.split(".")[0], FORBIDDEN, (fn, m))
                self.assertFalse(m.startswith("hub.web"), (fn, m))
            self.assertNotRegex(text, r"[\"']E-[A-Z]")
        users = []
        for d, dirs, fns in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for fn in fns:
                rel = os.path.relpath(os.path.join(d, fn), S.CODE_ROOT).replace(os.sep, "/")
                if fn.endswith(".py") and not rel.startswith("hub/release/") and any(m.startswith("hub.release") for m in imports(read(rel))):
                    users.append(rel)
        self.assertEqual(users, [], "hub.release is a stand-alone tool: nothing in the product imports it (S30-DEV-03)")
        edits = T.read_json(os.path.join(S.CODE_ROOT, "tests", "hub", "non_add_edits.json"))
        self.assertEqual(edits["stage"], "30")
        self.assertEqual(sorted(e["path"] for e in edits["edits"]), EXPECTED_EDITS)

    def test_TST_HUB_STG30_D02_artifacts_exist_with_structure(self):
        """D02: 11 artifacts, front matter keys, eight sections, status not APPROVED, synthetic label, stage 30."""
        for a in ARTIFACTS:
            text = read("docs/30-release/%s.md" % a)
            head = text.split("---")[1]
            for k in ("stage:", "artifact:", "version:", "date:", "author_agent:", "status:", "evidence_sources:", "supersedes:"):
                self.assertIn(k, head, (a, k))
            self.assertIn('artifact: "%s.md"' % a, head)
            self.assertIn("30", re.search(r'stage: "([^"]*)"', head).group(1))
            self.assertNotIn("APPROVED", re.search(r'status: "([^"]*)"', head).group(1), a)
            for sec in SECTIONS:
                self.assertIn(sec, text, (a, sec))
            self.assertIn("synthetic, unvalidated", text, a)
        self.assertEqual(len(ARTIFACTS), 11)

    def test_TST_HUB_STG30_D03_docs_agree_with_the_register(self):
        """D03: all 40 approval ids, 20 criterion ids and the 29 carried decisions are in the documents; release-outcome says NOT RELEASED and records no approval."""
        appr = read("docs/30-release/release-approvals.md")
        for i in register.approval_ids():
            self.assertIn(i, appr, i)
        for pre, n in (("D-27-", 9), ("D-28-", 10), ("D-31-", 10)):
            for k in range(1, n + 1):
                self.assertIn("%s%02d" % (pre, k), appr, (pre, k))
        crit = read("docs/30-release/go-no-go-criteria.md")
        for c in register.TECHNICAL_IDS:
            self.assertIn(c, crit, c)
        out = read("docs/30-release/release-outcome.md")
        self.assertIn("NOT RELEASED", out)
        self.assertIn("cutover were not executed", out.replace("\n", " "))
        for a in ARTIFACTS:
            text = read("docs/30-release/%s.md" % a)
            self.assertNotRegex(text, r"(?i)approved by dinesh", a)
        rb = read("docs/30-release/rollback-plan.md")
        for lvl in ("L1", "L2", "L3"):
            self.assertIn(lvl, rb)

    def test_TST_HUB_STG30_D04_shipped_state_is_unchanged_and_safe(self):
        """D04: the hub-hardening workflow is not installed under .github; no repo config file sets an authority switch; shipped defaults pass the posture check; Zone H holders empty; no holder named."""
        self.assertFalse(os.path.exists(os.path.join(S.CODE_ROOT, ".github", "workflows", "hub-hardening.yml")))  # D-27-03 / HAR-07: not installed
        offenders = []
        for rel in ("domain.json", "domain-profile.json", "compose.yaml", "Dockerfile", "pyproject.toml", "run.sh"):
            p = os.path.join(S.CODE_ROOT, rel)
            if os.path.exists(p) and "capability_authority" in read(rel):
                offenders.append(rel)
        for d in ("environments", "ci", "ops", "operations"):
            base = os.path.join(S.CODE_ROOT, d)
            for root, dirs, fns in os.walk(base):
                for fn in fns:
                    if "capability_authority" in read(os.path.relpath(os.path.join(root, fn), S.CODE_ROOT)):
                        offenders.append(os.path.join(d, fn))
        self.assertEqual(offenders, [])
        cfg = config.load(None)
        self.assertEqual(gonogo.posture(cfg), [])
        self.assertEqual(cfg["capability_authority"], {})
        from hub.security import settings
        self.assertEqual(settings.resolve(cfg)["zone_h"]["holders"], [])
        appr = T.read_json(os.path.join(T.EVID, "approvals-register.json"))
        self.assertEqual([r["id"] for r in appr["records"] if r["status"] != "OPEN"], [])

    def test_TST_HUB_STG30_D05_evidence_checksums_verify(self):
        """D05: evidence/SHA256SUMS.txt verifies (sha256sum -c) and lists every other file of the folder."""
        listed = []
        with open(os.path.join(T.EVID, "SHA256SUMS.txt"), encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    listed.append(line.split(None, 1)[1].strip().lstrip("*"))
        on_disk = sorted(x for x in os.listdir(T.EVID) if x != "SHA256SUMS.txt")
        self.assertEqual(sorted(listed), on_disk)
        p = subprocess.run(["sha256sum", "-c", "--quiet", "SHA256SUMS.txt"], cwd=T.EVID, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        self.assertEqual(p.returncode, 0, p.stdout)


if __name__ == "__main__":
    unittest.main()
