"""Stage 30 tests, part 1: defect F-29-01 (S30-DEV-01). Synthetic, unvalidated.

Stage 29 found that a malformed line in the audit anchor file made `verify-audit` print the right tamper envelope and then crash with a KeyError in the
end-of-run anchor write: exit 1 and a traceback instead of exit 17. The fix is in hub/admin/cli.py (_Run.close): for verify-audit only, an unreadable anchor
file no longer aborts the close, and the anchor file is NOT appended to (fail closed). Every other command keeps its old behaviour.

  F01  four malformed-anchor shapes -> exit 17, stderr is exactly one E-SEC-AUDIT-TAMPER-DETECTED envelope (no traceback), kind anchor_unreadable,
       the anchor file is byte-identical afterwards
  F02  a clean store still exits 0 and appends nothing new beyond the usual end-of-run anchor; a well-formed head mismatch still exits 17
  F03  other commands are unchanged: `anchor` on a malformed file still fails (exit != 0) and does not write to the file
"""
import json
import os
import unittest

import _stg30 as T


def setUpModule():
    T.skip_in_inner_egress_run()


MALFORMED = (
    ("missing-key", '{"seq": 9, "hash": "x"}\n'),
    ("not-json", "this is not json\n"),
    ("json-list", "[1, 2, 3]\n"),
    ("non-numeric-seq", '{"audit_seq": "abc", "hash": "x"}\n'),
)


class TST_HUB_STG30_F2901(unittest.TestCase):

    def _rig_with_line(self, prefix, line):
        rig = T.Rig(prefix)
        rig.migrate()
        self.assertEqual(rig.admin("verify-audit", "--data-dir", rig.data).returncode, 0)
        with open(rig.anchor, "a", encoding="utf-8") as f:
            f.write(line)
        return rig

    def test_TST_HUB_STG30_F01_malformed_anchor_gives_exit_17_not_a_traceback(self):
        """F01: each malformed shape -> rc 17, one JSON envelope on stderr, kind anchor_unreadable, anchor file unchanged."""
        seen = {}
        for name, line in MALFORMED:
            rig = self._rig_with_line("f01-" + name + "-", line)
            before = rig.anchor_bytes()
            p = rig.admin("verify-audit", "--data-dir", rig.data)
            self.assertEqual(p.returncode, 17, (name, p.stderr[-600:]))
            env = json.loads(p.stderr)  # strict: a traceback after the envelope would not parse
            self.assertEqual(env["code"], "E-SEC-AUDIT-TAMPER-DETECTED", name)
            self.assertEqual((env["details"]["status"], env["details"]["kind"]), ("broken", "anchor_unreadable"), name)
            self.assertNotIn("Traceback", p.stderr)
            self.assertEqual(rig.anchor_bytes(), before, "the unreadable anchor file must not be appended to (%s)" % name)
            self.assertEqual(json.loads(p.stdout)["kind"], "anchor_unreadable")
            seen[name] = p.returncode
        T.write_evidence("f01.json", seen)

    def test_TST_HUB_STG30_F02_clean_and_well_formed_mismatch_unchanged(self):
        """F02: clean store -> rc 0; a well-formed anchor line with a wrong hash -> rc 17 (head_mismatch) as before."""
        rig = T.Rig("f02-")
        rig.migrate()
        self.assertEqual(rig.admin("verify-audit", "--data-dir", rig.data).returncode, 0)
        with open(rig.anchor, "a", encoding="utf-8") as f:
            f.write(json.dumps({"audit_seq": 1, "hash": "0" * 64}) + "\n")
        p = rig.admin("verify-audit", "--data-dir", rig.data)
        self.assertEqual(p.returncode, 17)
        self.assertEqual(json.loads(p.stderr)["details"]["kind"], "head_mismatch")

    def test_TST_HUB_STG30_F03_other_commands_keep_their_behaviour(self):
        """F03: `anchor` on a malformed file still fails (non-zero) and writes nothing; the fix is limited to verify-audit."""
        rig = self._rig_with_line("f03-", '{"seq": 9, "hash": "x"}\n')
        before = rig.anchor_bytes()
        p = rig.admin("anchor", "--data-dir", rig.data)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(rig.anchor_bytes(), before)
        self.assertTrue(os.path.exists(os.path.join(rig.data, "hub.sqlite3")))


if __name__ == "__main__":
    unittest.main()
