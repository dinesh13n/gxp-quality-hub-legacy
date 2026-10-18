"""TST-CO-10 (AC-CO-10, FR-CO-03, BEH-CO-06) - a release attempted with G2 (replay-safety) failing cannot be marked
ready: the code path refuses (E-CO-RELEASE-BLOCKED, audited) and the DB trigger refuses a direct UPDATE too.
The all-pass control uses SYNTHETIC gate results (test-only) to prove the path to 'ready' exists."""
import sqlite3
import unittest

import _support as S
import _inc03 as H
from hub.ops import release
from hub.security import audit
from hub.security.errors import ReleaseBlocked


def setUpModule():
    S.require_sandbox()


def _all(result="pass"):
    return {g: {"result": result, "evidence_path": "synthetic/%s.json" % g} for g in release.GATE_IDS}


class TST_CO_10_ReleaseBlocked(unittest.TestCase):

    def test_TST_CO_10_a_g2_failing_blocks_ready(self):
        """TST-CO-10 / AC-CO-10: G1,G3-G10 pass, G2 fail -> mark_ready raises E-CO-RELEASE-BLOCKED; status stays candidate."""
        st = H.Store("co10a-")
        try:
            res = _all()
            res["G2"] = {"result": "fail", "evidence_path": "synthetic/G2-replay-safety.json", "note": "replay suite failed"}
            out = release.record_checklist(st.con, st.clock, "R-co10", res, "op", "c1", anchor=st.anchor)
            self.assertEqual((out["blocking"], out["ready_allowed"]), (["G2"], False))
            with self.assertRaises(ReleaseBlocked) as cm:
                release.mark_ready(st.con, st.clock, "R-co10", "op", "c2", anchor=st.anchor)
            self.assertEqual(cm.exception.details["blocking"], ["G2"])
            self.assertEqual(release.checklist(st.con, "R-co10")["status"], "candidate")
            with self.assertRaises(sqlite3.IntegrityError) as cm2:
                with st.con:
                    st.con.execute("UPDATE release_record SET status = 'ready' WHERE release_id = 'R-co10'")
            self.assertIn("E-CO-RELEASE-BLOCKED", str(cm2.exception))
            with self.assertRaises(sqlite3.IntegrityError):
                with st.con:
                    st.con.execute("UPDATE release_gate_result SET result = 'pass' WHERE gate = 'G2'")
            last = st.audit_rows()[-1]
            self.assertEqual((last["action"], last["outcome"]), ("RELEASE_READY", "denied"))
            self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")
        finally:
            st.close()

    def test_TST_CO_10_b_not_run_also_blocks_and_all_pass_control(self):
        """TST-CO-10: a gate left not_run blocks as well; control - all 10 synthetic 'pass' -> ready (one way only)."""
        st = H.Store("co10b-")
        try:
            res = _all()
            del res["G2"]
            release.record_checklist(st.con, st.clock, "R-notrun", res, "op", "c1")
            with self.assertRaises(ReleaseBlocked):
                release.mark_ready(st.con, st.clock, "R-notrun", "op", "c2")
            release.record_checklist(st.con, st.clock, "R-synthetic-allpass", _all(), "op", "c3")
            self.assertEqual(release.mark_ready(st.con, st.clock, "R-synthetic-allpass", "op", "c4")["status"], "ready")
            with self.assertRaises(sqlite3.IntegrityError):
                with st.con:
                    st.con.execute("UPDATE release_record SET status = 'candidate' WHERE release_id = 'R-synthetic-allpass'")
        finally:
            st.close()


if __name__ == "__main__":
    unittest.main()
