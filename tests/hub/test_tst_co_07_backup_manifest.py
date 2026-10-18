"""TST-CO-07 (AC-CO-07, OD-03a, FR-CO-01) - after a sandbox run completes, `sha256sum -c --quiet` on the
backup manifest, executed from the repo root, exits 0 and covers all 1,512 baseline files.
"""
import os
import subprocess
import unittest

import _support as S
from hub.guards import sandbox


def setUpModule():
    S.require_sandbox()


class TST_CO_07_BackupManifestAfterRun(unittest.TestCase):

    def test_TST_CO_07_a_sha256sum_rc0_after_sandbox_run(self):
        """TST-CO-07 / AC-CO-07: sandbox golden-compare run, then sha256sum -c --quiet from the repo root -> rc 0, 1,512 entries."""
        p = S.golden_compare(S.tmpdir("co07-"))
        self.assertEqual(p.returncode, 6)  # the run completed (DV rows proposed -> 6 by design)
        c = subprocess.run(["sha256sum", "-c", "--quiet", S.BACKUP_MANIFEST_REL], cwd=S.WORKTREE,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=300)
        self.assertEqual(c.returncode, 0, c.stdout[-500:])
        with open(os.path.join(S.WORKTREE, S.BACKUP_MANIFEST_REL), encoding="utf-8") as f:
            entries = [l for l in f if l.strip()]
        self.assertEqual(len(entries), 1512)

    def test_TST_CO_07_b_python_verifier_agrees(self):
        """TST-CO-07: hub.guards.sandbox.verify_backup_manifest (read-only hashing) -> 1,512 entries, 0 failures."""
        n, failures = sandbox.verify_backup_manifest(S.WORKTREE)
        self.assertEqual((n, failures), (1512, []))


if __name__ == "__main__":
    unittest.main()
