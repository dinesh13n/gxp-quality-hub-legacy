"""Stage 30 tests, part 3: release, cutover and rollback rehearsals on PRIVATE sandbox copies. Synthetic, unvalidated.

Nothing here touches the working tree or its data/, flips a shipped switch, or records an approval. The authority flip in R02 is a rehearsal on a throwaway
config file with an explicit marker that is NOT an approval (REHEARSAL-SANDBOX-NOT-AN-APPROVAL); it shows that the switch is refused without a reference
and that the L3 rollback returns the capability to shadow and leaves both changes in the audit chain.

  R01  rollout + L2: migrate, backup (manifest verifies), more audit records, restore -> checksum match, chain verifies, the later records are set aside
       (not merged); a corrupted copy of the backup is refused (exit 21) and the live store is unchanged
  R02  cutover dry-run + L3: authority flip refused without a reference (exit 2); with the rehearsal marker it holds; posture sees it; flip-to-shadow returns
       the config to a clean posture; the chain holds two CONFIG_CHANGED records (to_non_default, then to_default with rollback L3); verify-audit ok
  R03  the release record refuses `ready` while any gate is not 'pass' (exit 20, RELEASE_READY denied); the checklist can be recorded with real automated gates
       and nothing is marked ready
  R04  L1: a merge reverted with `git revert -m 1` in a throwaway repository restores the pre-merge tree exactly, history only grows, nothing is force-pushed
"""
import json
import os
import shutil
import sqlite3
import subprocess
import unittest

import _stg30 as T
import _support as S
from hub import config
from hub.release import gonogo


def setUpModule():
    T.skip_in_inner_egress_run()


def head_seq(rig):
    con = sqlite3.connect(os.path.join(rig.data, "hub.sqlite3"))
    try:
        return con.execute("SELECT MAX(audit_seq) FROM audit_log").fetchone()[0]
    finally:
        con.close()


class TST_HUB_STG30_Rehearsal(unittest.TestCase):

    def test_TST_HUB_STG30_R01_backup_restore_and_corrupt_backup(self):
        """R01: backup verifies; restore returns to the backup head, chain ok, later records set aside; a corrupted backup copy is refused with exit 21."""
        rig = T.Rig("r01-")
        rig.migrate()
        self.assertEqual(rig.admin("verify-audit", "--data-dir", rig.data).returncode, 0)
        dest = os.path.join(rig.root, "backups")
        p = rig.admin("backup", "--data-dir", rig.data, "--dest-root", dest, "--label", "pre")
        self.assertEqual(p.returncode, 0, p.stderr)
        bk = os.path.join(dest, "pre")
        self.assertEqual(subprocess.run(["sha256sum", "-c", "--quiet", "SHA256SUMS"], cwd=bk).returncode, 0)
        at_backup = head_seq(rig)
        for _ in range(2):  # each verify-audit appends an AUDIT_VERIFIED record: these are the 'later records'
            self.assertEqual(rig.admin("verify-audit", "--data-dir", rig.data).returncode, 0)
        self.assertGreater(head_seq(rig), at_backup)
        bad = os.path.join(dest, "bad")
        shutil.copytree(bk, bad)
        with open(os.path.join(bad, "hub.sqlite3"), "r+b") as f:
            f.seek(100)
            f.write(b"X")
        before = head_seq(rig)
        p = rig.admin("restore", "--data-dir", rig.data, "--backup", bad)
        self.assertEqual(p.returncode, 21, p.stderr)
        self.assertEqual(json.loads(p.stderr)["code"], "E-STORE-BACKUP-INVALID")
        self.assertEqual(head_seq(rig), before)
        p = rig.admin("restore", "--data-dir", rig.data, "--backup", bk)
        self.assertEqual(p.returncode, 0, p.stderr)
        rep = json.loads(p.stdout)
        self.assertTrue(rep["checksum_match"])
        self.assertEqual(rep["verify_audit"]["status"], "ok")
        self.assertIn("hub.sqlite3", rep["set_aside"])
        self.assertTrue(os.path.isdir(rep["set_aside_dir"]))
        self.assertEqual(rep["audit_head"]["audit_seq"], at_backup)
        self.assertEqual(rig.admin("verify-audit", "--data-dir", rig.data).returncode, 0)
        T.write_evidence("r01.json", {"head_at_backup": at_backup, "head_before_restore": before, "restored_head": rep["audit_head"]["audit_seq"]})

    def test_TST_HUB_STG30_R02_authority_flip_is_refused_without_reference_and_rolls_back(self):
        """R02: no reference -> exit 2; rehearsal marker -> held, posture violation; flip-to-shadow -> clean posture; two CONFIG_CHANGED records; chain ok."""
        rig = T.Rig("r02-")
        rig.migrate()
        flag = "capability_authority.CUT-2"
        p = rig.control("set-flag", "--flag", flag, "--value", '"authoritative"', "--data-dir", rig.data)
        self.assertEqual(p.returncode, 2, p.stderr)
        self.assertEqual(json.loads(p.stderr)["code"], "E-CFG-INVALID")
        self.assertEqual(gonogo.posture(config.load(rig.cfg_path)), [])
        p = rig.control("set-flag", "--flag", flag, "--value", '"authoritative"', "--approval-ref", T.SANDBOX_REF, "--data-dir", rig.data)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["direction"], "to_non_default")
        viol = gonogo.posture(config.load(rig.cfg_path))
        self.assertTrue(any("capability_authority.CUT-2" in v for v in viol), viol)
        self.assertEqual(rig.admin("verify-audit", "--data-dir", rig.data).returncode, 0)
        p = rig.control("flip-to-shadow", "--capability", "CUT-2", "--reason", "Stage 30 rehearsal L3", "--data-dir", rig.data)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["direction"], "to_default")
        self.assertEqual(gonogo.posture(config.load(rig.cfg_path)), [])
        changed = [(o, json.loads(d)) for a, o, d in rig.audit_actions() if a == "CONFIG_CHANGED"]
        self.assertEqual([(o, d["new"], d["direction"]) for o, d in changed],
                         [("flag:" + flag, "authoritative", "to_non_default"), ("flag:" + flag, "shadow", "to_default")])
        self.assertEqual(changed[0][1]["approval_ref"], T.SANDBOX_REF)
        self.assertIsNone(changed[1][1]["approval_ref"])
        self.assertEqual(changed[1][1]["rollback"], "L3")
        self.assertEqual(rig.admin("verify-audit", "--data-dir", rig.data).returncode, 0)

    def test_TST_HUB_STG30_R03_release_record_refuses_ready_while_a_gate_is_not_pass(self):
        """R03: release-checklist with --mark-ready and six gates not run -> exit 20 E-CO-RELEASE-BLOCKED naming them; without --mark-ready the record stays a candidate."""
        rig = T.Rig("r03-")
        rig.migrate()
        args = ["--data-dir", rig.data, "--evidence-dir", os.path.join(rig.root, "ev"), "--scratch-root", os.path.join(rig.root, "g7")]
        p = rig.admin("release-checklist", "--release", "R-S30-T1", "--mark-ready", *args)
        self.assertEqual(p.returncode, 20, p.stderr)
        env = json.loads(p.stderr)
        self.assertEqual(env["code"], "E-CO-RELEASE-BLOCKED")
        self.assertEqual(env["details"]["blocking"], ["G1", "G2", "G4", "G8", "G9", "G10"])
        p = rig.admin("release-checklist", "--release", "R-S30-T2", *args)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertFalse(out["ready_allowed"])
        res = dict((g["gate"], g["result"]) for g in out["gates"])
        self.assertEqual([g for g, r in sorted(res.items()) if r == "pass"], ["G3", "G5", "G6", "G7"])
        con = sqlite3.connect(os.path.join(rig.data, "hub.sqlite3"))
        try:
            self.assertEqual(sorted(r[0] for r in con.execute("SELECT status FROM release_record")), ["candidate", "candidate"])
        finally:
            con.close()

    def test_TST_HUB_STG30_R04_l1_revert_of_a_merge_restores_the_tree(self):
        """R04: throwaway repo: base -> feature merged with --no-ff -> `git revert -m 1` -> tree equals base; history grew by one commit; nothing rewritten."""
        if shutil.which("git") is None:
            self.skipTest("git not available")
        repo = os.path.join(S.tmpdir("r04-"), "r")
        os.makedirs(repo)
        env = dict(S.child_env(), GIT_AUTHOR_NAME="Rehearsal", GIT_AUTHOR_EMAIL="r@example.invalid", GIT_COMMITTER_NAME="Rehearsal", GIT_COMMITTER_EMAIL="r@example.invalid",
                   GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)

        def git(*a):
            p = subprocess.run(["git"] + list(a), cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=60)
            self.assertEqual(p.returncode, 0, (a, p.stdout))
            return p.stdout.strip()

        git("init", "-q", "-b", "main")
        with open(os.path.join(repo, "a.txt"), "w") as f:
            f.write("base\n")
        git("add", "-A")
        git("commit", "-q", "-m", "base")
        base_tree = git("rev-parse", "HEAD^{tree}")
        git("checkout", "-q", "-b", "feature")
        with open(os.path.join(repo, "b.txt"), "w") as f:
            f.write("feature\n")
        with open(os.path.join(repo, "a.txt"), "a") as f:
            f.write("changed\n")
        git("add", "-A")
        git("commit", "-q", "-m", "feature work")
        git("checkout", "-q", "main")
        git("merge", "-q", "--no-ff", "-m", "merge feature", "feature")
        merged = git("rev-parse", "HEAD")
        self.assertNotEqual(git("rev-parse", "HEAD^{tree}"), base_tree)
        git("revert", "--no-edit", "-m", "1", merged)
        self.assertEqual(git("rev-parse", "HEAD^{tree}"), base_tree)
        self.assertEqual(git("rev-list", "--count", "HEAD"), "4")  # base, feature work, merge, revert: history only grows
        self.assertEqual(git("merge-base", "--is-ancestor", merged, "HEAD") or "", "")
        self.assertFalse(os.path.exists(os.path.join(repo, "b.txt")))


if __name__ == "__main__":
    unittest.main()
