"""TST-CO-06 (AC-CO-06, OD-03a, BEH-CO-04) - a working data directory inside the original repository root
(or the backup, or an ancestor of either) -> E-CO-NOT-SANDBOX (exit 7) and no run (nothing created).
"""
import os
import shutil
import subprocess
import sys
import unittest

import _support as S


def setUpModule():
    S.require_sandbox()


class TST_CO_06_SandboxGuard(unittest.TestCase):

    def _refused(self, data_dir, legacy_root=None):
        existed = os.path.exists(data_dir)
        args = ["golden-compare", "--json", "--data-dir", data_dir, "--legacy-root", legacy_root or S.LEGACY_ROOT]
        p = S.run_hub(args)
        self.assertEqual(p.returncode, 7, (data_dir, p.stdout[-300:], p.stderr[-300:]))
        self.assertEqual(S.error_code(p), "E-CO-NOT-SANDBOX")
        self.assertEqual(p.stdout, "")
        self.assertEqual(os.path.exists(data_dir), existed, "guard must refuse before creating anything")

    def test_TST_CO_06_a_data_dir_inside_repo_refused(self):
        """TST-CO-06 / AC-CO-06: data dir inside the original repo (root, data/, a new subdir) -> exit 7, no run."""
        for d in (S.WORKTREE, os.path.join(S.WORKTREE, "data"), os.path.join(S.WORKTREE, "data", "hub-inc02-must-not-exist"),
                  os.path.join(S.WORKTREE, "hub", "x-must-not-exist")):
            with self.subTest(d=d):
                self._refused(d)

    def test_TST_CO_06_b_backup_ancestor_home_root_refused(self):
        """TST-CO-06: the Stage 0A backup, an ancestor of the repo, $HOME and / are refused."""
        backup = os.path.join(os.path.dirname(S.WORKTREE), "_data-backup-2026-10-17", "hub-must-not-exist")
        for d in (backup, os.path.dirname(S.WORKTREE), os.path.expanduser("~"), "/"):
            with self.subTest(d=d):
                self._refused(d)

    def test_TST_CO_06_c_legacy_root_in_worktree_refused(self):
        """TST-CO-06: --legacy-root pointing at the working tree (its data/) is refused before any snapshot."""
        d = os.path.join(S.tmpdir("co06c-"), "hubdata")
        self._refused(d, legacy_root=S.WORKTREE)

    def test_TST_CO_06_d_any_git_worktree_refused(self):
        """TST-CO-06: a data dir inside any directory holding .git is refused, and hub code loaded from such a
        tree refuses to run its tests (assert_running_in_sandbox)."""
        fake = S.tmpdir("co06d-")
        os.makedirs(os.path.join(fake, ".git"))
        shutil.copytree(os.path.join(S.CODE_ROOT, "hub"), os.path.join(fake, "hub"))
        env = S.child_env()
        env.pop("HUB_WORKTREE_ROOT", None)
        p = subprocess.run([sys.executable, "-B", "-m", "hub", "init", "--data-dir", os.path.join(fake, "d")],
                           cwd=fake, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(p.returncode, 7, p.stderr)
        self.assertFalse(os.path.exists(os.path.join(fake, "d")))
        p = subprocess.run([sys.executable, "-B", "-c", "from hub.guards import sandbox; sandbox.assert_running_in_sandbox()"],
                           cwd=fake, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("E-CO-NOT-SANDBOX", p.stderr)

    def test_TST_CO_06_e_sandbox_data_dir_accepted(self):
        """TST-CO-06 control: a data dir in the sandbox scratch area is accepted (init exit 0)."""
        d = os.path.join(S.tmpdir("co06e-"), "hubdata")
        p = S.run_hub(["init", "--data-dir", d])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(os.path.isfile(os.path.join(d, "hub.sqlite3")))


if __name__ == "__main__":
    unittest.main()
