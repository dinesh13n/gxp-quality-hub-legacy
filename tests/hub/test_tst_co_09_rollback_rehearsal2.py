"""TST-CO-09 (AC-CO-09, FR-CO-03, PNFR-19; nfr-measurement; moved to INC-06 because it needs the replay-safety suite): rollback rehearsal 2 in
the sandbox, executed from the written procedure docs/15-modernization/rollback-rehearsal-inc06.md - store restored from the pre-M004 backup,
checksum matches the manifest, the audit chain verifies, and the replay-safety suite passes again after rolling forward. Rehearsal 1 (M001)
is test_inc03_supplementary S02. Synthetic, unvalidated.
"""
import json
import os
import sqlite3
import unittest

import _support as S
import _inc03 as H
import _inc05 as D
import _inc06 as I
from hub.intake import replay, schema as ischema
from hub.intake.service import IntakeService
from hub.ops import backup
from hub.security import audit
from hub.store import db


def setUpModule():
    I.skip_in_inner_egress_run()


def connect(ds):
    con = sqlite3.connect(os.path.join(ds.data, db.HUB_DB_NAME))
    con.execute("PRAGMA foreign_keys = ON")
    return con


class TST_CO_09_RollbackRehearsal2(unittest.TestCase):

    def test_TST_CO_09_rollback_rehearsal_m004(self):
        """TST-CO-09 / AC-CO-09: pre-M004 backup -> apply M004 -> intake run + replay-safety -> restore (L2) -> checksum matches, audit chain
        verifies, intake tables gone, decision record unchanged -> roll forward -> same intake result, replay-safety suite passes."""
        ds = D.DStore(loaded=True)
        base_events = ds.con.execute("SELECT count(*) FROM decision_events").fetchone()[0]
        ds.close()
        bk_root = os.path.join(ds.base, "rehearsal-backups")
        # 1. forward step with its pre-migration backup (the rollback point)
        res = ischema.apply(ds.data, bk_root, ds.anchor_path, ds.clock, "co09-apply")
        self.assertTrue(res["applied"])
        bk = res["backup"]
        pre = backup.verify_backup(bk["path"])
        self.assertNotIn("raw_intake", json.dumps(pre["schema_versions"]))
        items = I.batch(300) + [I.feed(1, payload={"quantity": 55.5}, source_key="FEED-REV-1"), I.feed(900, payload={"quantity": -2})]
        con = connect(ds)
        svc = IntakeService(con, ds.s, ds.clock, ds.anchor)
        r1 = svc.ingest("partner_feed", items, "co09-run1", "co09")
        self.assertEqual((r1["stored"], r1["outcomes"]["VALIDATED"], r1["revised_conflict"]), (302, 300, 1))
        g2 = replay.replay_safety(svc, "partner_feed", items, "co09-replay", ds.clock(), "co09")
        self.assertTrue(g2["ok"], g2["checks"])
        audit.write_anchor(con, ds.anchor_path)
        self.assertEqual(audit.verify(con, ds.anchor_path)["status"], "ok")
        head_after = audit.head(con)
        con.close()
        # 2. rollback L2: restore the pre-migration backup
        rest = backup.restore(bk["path"], ds.data, ds.anchor_path, ds.clock)
        self.assertTrue(rest["checksum_match"])
        self.assertEqual(rest["restored"], pre["files"])                                        # restored files == manifest checksums
        self.assertIn("hub.sqlite3", rest["set_aside"])                                          # hold-all: the newer store is set aside, not deleted
        self.assertTrue(os.path.isfile(os.path.join(rest["set_aside_dir"], "hub.sqlite3")))
        con = connect(ds)
        try:
            names = set(r[0] for r in con.execute("SELECT name FROM sqlite_master"))
            self.assertFalse(names & {"raw_intake", "intake_outcome", "intake_item_attr", "intake_run_event", "intake_schema_migrations"})
            self.assertEqual(con.execute("SELECT count(*) FROM decision_events").fetchone()[0], base_events)
            v = audit.verify(con, ds.anchor_path)
            self.assertEqual(v["status"], "ok")
            self.assertEqual(rest["audit_head"]["audit_seq"], audit.head(con)[0])
            self.assertLess(audit.head(con)[0], head_after[0])
        finally:
            con.close()
        # 3. roll forward again and re-run the replay-safety suite
        res2 = ischema.apply(ds.data, bk_root, ds.anchor_path, ds.clock, "co09-apply2")
        self.assertTrue(res2["applied"])
        con = connect(ds)
        try:
            svc = IntakeService(con, ds.s, ds.clock, ds.anchor)
            r2 = svc.ingest("partner_feed", items, "co09-run2", "co09")
            self.assertEqual(r2["outcomes_digest"], r1["outcomes_digest"])                        # the same input gives the same result
            self.assertEqual(r2["outcomes"], r1["outcomes"])
            g2b = replay.replay_safety(svc, "partner_feed", items, "co09-replay2", ds.clock(), "co09")
            self.assertTrue(g2b["ok"], g2b["checks"])
            idem = svc.ingest("partner_feed", items, "co09-backfill", "co09", idempotent_backfill=True)
            self.assertEqual((idem["stored"], idem["skipped_existing"]), (0, 302))
            self.assertEqual(svc.counts()["raw"], 302 * 2)
            audit.write_anchor(con, ds.anchor_path)
            self.assertEqual(audit.verify(con, ds.anchor_path)["status"], "ok")
        finally:
            con.close()


if __name__ == "__main__":
    unittest.main()
