"""TST-CO-05 (AC-CO-05, FR-CO-01, ADR-003, BEH-CO-03) - after the build, `git diff` on the legacy source paths
is empty. Read-only git queries against the original working tree (HUB_WORKTREE_ROOT) with
--no-optional-locks; compared with the tag `baseline-as-found` (OD-06) and with the current HEAD/worktree.
"""
import json
import os
import subprocess
import unittest

import _support as S

LEGACY_PATHS = [
    "app", "services", "legacy_batch", "legacy_java", "legacy_js", "sql", "scripts", "ops", "integration",
    "contracts", "environments", "data", ".github", "Dockerfile", "compose.yaml", "pyproject.toml", "run.sh",
    "domain.json", "domain-profile.json", "README.md", "DATA_READINESS.md", "PRELOADED_DATA.md",
    ":(glob)tests/*.py", ":(glob)docs/*.md", "docs/correspondence", "docs/decisions",
]


def setUpModule():
    S.require_sandbox()


def git(*args):
    return subprocess.run(["git", "--no-optional-locks", "-C", S.WORKTREE] + list(args), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True, timeout=120)


class TST_CO_05_LegacyPathsUnchanged(unittest.TestCase):

    def test_TST_CO_05_a_no_diff_vs_baseline_as_found(self):
        """TST-CO-05 / AC-CO-05: git diff baseline-as-found (committed + working tree) on legacy paths is empty."""
        p = git("diff", "--name-status", "baseline-as-found", "--", *LEGACY_PATHS)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout.strip(), "")

    def test_TST_CO_05_b_no_untracked_files_in_legacy_paths(self):
        """TST-CO-05: no new untracked (non-ignored) files appear under the legacy paths."""
        p = git("ls-files", "--others", "--exclude-standard", "--", *LEGACY_PATHS)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout.strip(), "")

    def test_TST_CO_05_c_branch_only_adds_files_outside_stage15_docs(self):
        """TST-CO-05: on this branch every change vs main is an added file, except Stage 15's own docs and (Stage 20, OD-26) a
        modification listed in tests/hub/non_add_edits.json with its work item and reason. Deletions / renames are never accepted;
        an allow-list entry may not name a legacy path."""
        with open(os.path.join(S.CODE_ROOT, "tests", "hub", "non_add_edits.json"), encoding="utf-8") as f:
            edits = json.load(f)["edits"]
        allowed = set()
        for e in edits:
            self.assertTrue(str(e.get("work_item", "")).strip() and str(e.get("reason", "")).strip(), e)
            self.assertTrue(e["path"].startswith(("hub/", "tests/hub/")), e["path"])
            allowed.add(e["path"])
        p = git("diff", "--name-status", "main", "--")
        self.assertEqual(p.returncode, 0, p.stderr)
        offending = [l for l in p.stdout.splitlines()
                     if l and not l.startswith("A\t") and not l.split("\t")[-1].startswith("docs/15-modernization/")
                     and not (l.startswith("M\t") and l.split("\t")[-1] in allowed)]
        self.assertEqual(offending, [])
        if allowed:
            lp = git("diff", "--name-status", "baseline-as-found", "--", *sorted(allowed))
            self.assertEqual(lp.returncode, 0, lp.stderr)
            self.assertFalse(any(l.startswith(("D\t", "R")) for l in lp.stdout.splitlines()), lp.stdout)


if __name__ == "__main__":
    unittest.main()
