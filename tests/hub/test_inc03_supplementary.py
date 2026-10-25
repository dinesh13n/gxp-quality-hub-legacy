"""Stage 15 INC-03 supplementary tests (no Stage 13 ID; TST-HUB-INC03-Sxx): migration runner, backup/restore,
INC-02 forward compatibility, anchor-path configuration, Zone H holder / re-auth checks."""
import json
import os
import shutil
import sqlite3
import unittest

import _support as S
import _inc03 as H
from hub import config
from hub.core.errors import ConfigInvalid, MigrationDrift, NotSandbox
from hub.ops import backup
from hub.security import audit, authz, settings
from hub.security.errors import AuthForbidden, BackupInvalid
from hub.store import migrate


def setUpModule():
    S.require_sandbox()


class TST_HUB_INC03_Supplementary(unittest.TestCase):

    def test_TST_HUB_INC03_S01_migration_runner(self):
        """S01: migrate = backup-before-migrate (M000-only snapshot, checksummed) then M001; idempotent; unknown/changed versions refused (exit 15)."""
        base = S.tmpdir("s01-")
        cfg = H.write_config(base)
        d = os.path.join(base, "data")
        self.assertEqual(S.run_hub(["init", "--data-dir", d]).returncode, 0)  # INC-02 store (M000)
        p = H.admin(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = H.out_json(p)
        self.assertEqual((out["from"], out["to"], out["applied"]), ("M000", "M001", ["M001"]))
        m = backup.verify_backup(out["backup"]["path"])
        self.assertEqual(m["schema_versions"], ["M000"])
        p = H.admin(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg)
        self.assertEqual(H.out_json(p)["applied"], [])
        self.assertEqual(H.out_json(H.admin(["status", "--data-dir", d], cfg))["pending"], [])
        con = sqlite3.connect(os.path.join(d, "hub.sqlite3"))
        try:
            mig = [r for r in con.execute("SELECT action, details FROM audit_log") if r[0] == "SCHEMA_MIGRATED"]
            self.assertEqual(len(mig), 1)
            self.assertEqual(json.loads(mig[0][1])["pre_migration_backup"], out["backup"]["label"])
        finally:
            con.close()
        for sql, key in (("INSERT INTO schema_migrations VALUES ('M999', 'x', 't')", "unknown_versions"),
                         ("UPDATE schema_migrations SET sha256 = 'tampered' WHERE version = 'M001'", "changed_versions")):
            d2 = os.path.join(S.tmpdir("s01b-"), "data")
            shutil.copytree(d, d2)
            con = sqlite3.connect(os.path.join(d2, "hub.sqlite3"))
            with con:
                con.execute("DROP TRIGGER IF EXISTS schema_migrations_no_update")  # Stage 27 H001: the ledger is insert-only; a host-level tamper has to remove the trigger first (as for the other ledgers)
                con.execute(sql)
            con.close()
            with self.assertRaises(MigrationDrift) as cm:
                migrate.status(d2)
            self.assertIn(key, cm.exception.details)
            p = H.admin(["status", "--data-dir", d2], cfg)
            self.assertEqual(p.returncode, 15, p.stderr)

    def test_TST_HUB_INC03_S02_backup_restore_roundtrip(self):
        """S02: backup -> more writes -> restore: checksums match, chain verifies, newer store set aside (not deleted); corrupt backup refused (exit 21) untouched."""
        st = H.Store("s02-")
        try:
            st.authn.create_user("u1", H.password(), ["reviewer"], "op")
            audit.write_anchor(st.con, st.anchor_path)
            bk = backup.backup(st.data, st.anchor_path, os.path.join(st.base, "bk"), "b1", st.clock)
            st.authn.create_user("u2", H.password(), ["reviewer"], "op")
            audit.write_anchor(st.con, st.anchor_path)
        finally:
            st.close()
        rep = backup.restore(bk["path"], st.data, st.anchor_path, st.clock)
        self.assertTrue(rep["checksum_match"])
        self.assertEqual(sorted(rep["set_aside"]), ["audit-anchor.jsonl", "hub.sqlite3"])
        con = sqlite3.connect(st.db_path)
        try:
            self.assertEqual([r[0] for r in con.execute("SELECT principal_id FROM principal")], ["u1"])
            self.assertEqual(audit.verify(con, st.anchor_path)["status"], "ok")
        finally:
            con.close()
        aside = sqlite3.connect(os.path.join(rep["set_aside_dir"], "hub.sqlite3"))
        self.assertEqual(aside.execute("SELECT count(*) FROM principal").fetchone()[0], 2)
        aside.close()
        with open(os.path.join(bk["path"], "hub.sqlite3"), "r+b") as f:
            f.seek(200)
            f.write(b"\x00corrupt")
        before = backup.sha256_file(st.db_path)
        with self.assertRaises(BackupInvalid):
            backup.restore(bk["path"], st.data, st.anchor_path, st.clock)
        self.assertEqual(backup.sha256_file(st.db_path), before)
        p = H.admin(["restore", "--data-dir", st.data, "--backup", bk["path"]], st.cfg_path)
        self.assertEqual((p.returncode, json.loads(p.stderr)["code"]), (21, "E-STORE-BACKUP-INVALID"))

    def test_TST_HUB_INC03_S03_inc02_commands_on_m001_store(self):
        """S03: INC-02 `python -m hub init/deviations` keep working on an M001 store (forward compatible); register unchanged."""
        base = S.tmpdir("s03-")
        cfg = H.write_config(base)
        d = os.path.join(base, "data")
        H.admin(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg)
        self.assertEqual(S.run_hub(["init", "--data-dir", d]).returncode, 0)
        p = S.run_hub(["deviations", "--data-dir", d])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(json.loads(p.stdout)["deviation_register"]), 11)  # Stage 20 DW-05: DV-10, DV-11 registered

    def test_TST_HUB_INC03_S04_anchor_path_configuration(self):
        """S04: audit.anchor_path must be set (E-CFG-INVALID), absolute, outside the DB dir, and sandbox-safe (E-CO-NOT-SANDBOX)."""
        base = S.tmpdir("s04-")
        d = os.path.join(base, "data")
        cases = ((None, ConfigInvalid), ("relative/anchor.jsonl", ConfigInvalid), (os.path.join(d, "a.jsonl"), ConfigInvalid),
                 (os.path.join(S.WORKTREE, "hub-anchor-must-not-exist", "a.jsonl"), NotSandbox))
        for path, exc in cases:
            with self.subTest(path=path):
                s = settings.resolve(config.load(overrides={"audit": {"anchor_path": path}}))
                with self.assertRaises(exc):
                    settings.anchor_path(s, d)
        self.assertFalse(os.path.exists(os.path.join(S.WORKTREE, "hub-anchor-must-not-exist")))
        p = H.admin(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")],
                    H.write_config(base, {"audit": {"anchor_path": None}}))
        self.assertEqual((p.returncode, json.loads(p.stderr)["code"]), (2, "E-CFG-INVALID"))
        self.assertFalse(os.path.exists(d))

    def test_TST_HUB_INC03_S05_zone_h_holder_and_reauth(self):
        """S05: Zone H needs role dispositioner AND holder AND re-auth within 300 s; service principals never; every attempt audited."""
        st = H.Store("s05-", extra={"zone_h": {"holders": ["disp"], "reauth_window_seconds": 300}})
        try:
            pw = H.password()
            st.authn.create_user("disp", pw, ["dispositioner"], "op")
            st.authn.create_user("disp2", pw, ["dispositioner"], "op")
            st.authn.create_user("svc", None, ["integration"], "op", kind="service")
            az = authz.Authorizer(st.con, st.s, st.clock, st.authn, st.anchor)
            t1, t2 = st.authn.login("disp", pw, "c"), st.authn.login("disp2", pw, "c")
            self.assertEqual(az.authorize("POST", "/api/v2/zone-h/actions", t1, "zh-ok").principal.principal_id, "disp")
            with self.assertRaises(AuthForbidden) as cm:
                az.authorize("POST", "/api/v2/zone-h/actions", t2, "zh-notholder")
            self.assertEqual(cm.exception.details["reason"], "not_a_holder")
            st.clock.advance(301)
            with self.assertRaises(AuthForbidden) as cm:
                az.authorize("POST", "/api/v2/zone-h/actions", t1, "zh-stale")
            self.assertEqual(cm.exception.details["reason"], "reauth_required")
            st.authn.reauthenticate(t1, pw, "zh-reauth")
            az.authorize("POST", "/api/v2/zone-h/actions", t1, "zh-ok2")
            with self.assertRaises(Exception):
                st.authn.login("svc", pw, "c")  # service principals cannot start interactive sessions
            zh = [(r["correlation_id"], r["outcome"]) for r in st.audit_rows() if r["action"] == "ZONE_H_ATTEMPT"]
            self.assertEqual(zh, [("zh-ok", "success"), ("zh-notholder", "denied"), ("zh-stale", "denied"), ("zh-ok2", "success")])
        finally:
            st.close()


if __name__ == "__main__":
    unittest.main()
