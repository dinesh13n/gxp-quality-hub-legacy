"""TST-CO-04 (AC-CO-04, FR-CO-01, BEH-CO-03, ADR-003) - legacy DBs are opened only via `mode=ro` (on a
per-run snapshot of the FX-BASE125 sandbox copy); every write attempt raises E-CO-LEGACY-WRITE-REFUSED.
"""
import ast
import os
import shutil
import sqlite3
import unittest

import _support as S
from hub.adapters import legacy_sqlite
from hub.core.errors import FixtureMismatch, LegacySchemaDrift, LegacyWriteRefused, NotSandbox

WRITES = [
    "INSERT INTO cases(id) VALUES ('X')",
    "UPDATE cases SET status = 'CLOSED'",
    "DELETE FROM cases",
    "CREATE TABLE hub_probe(x)",
    "CREATE TEMP TABLE hub_probe(x)",
    "DROP TABLE cases",
    "ALTER TABLE cases ADD COLUMN y",
    "ATTACH DATABASE ':memory:' AS other",
    "PRAGMA journal_mode = WAL",
    "PRAGMA user_version = 7",
    "REINDEX",
    "ANALYZE",
    "VACUUM",
]


def setUpModule():
    S.require_sandbox()


class TST_CO_04_ReadOnlyAdapters(unittest.TestCase):

    def setUp(self):
        self.run_dir = S.tmpdir("co04-")
        self.pins = legacy_sqlite.load_pins()

    def test_TST_CO_04_a_each_legacy_db_opened_read_only(self):
        """TST-CO-04: AD-01 and AD-02 open a snapshot with mode=ro&immutable=1; pinned schema and sha256 verified."""
        for store in sorted(self.pins):
            with legacy_sqlite.open_snapshot(S.LEGACY_ROOT, store, self.run_dir) as h:
                self.assertEqual(h.provenance["access"], "mode=ro&immutable=1")
                self.assertEqual(h.provenance["source_sha256"], self.pins[store]["sha256"])
                self.assertEqual(h.provenance["adapter"], {"legacy.sqlite3": "AD-01",
                                                           "enterprise_legacy.sqlite3": "AD-02"}[store])
        with legacy_sqlite.open_snapshot(S.LEGACY_ROOT, "legacy.sqlite3", self.run_dir) as h:
            self.assertEqual(h.execute("SELECT count(*) FROM cases"), [(125,)])

    def test_TST_CO_04_b_every_write_attempt_refused(self):
        """TST-CO-04 / AC-CO-04 negative: INSERT/UPDATE/DELETE/DDL/ATTACH/PRAGMA-set/VACUUM/commit -> E-CO-LEGACY-WRITE-REFUSED."""
        for store, table in (("legacy.sqlite3", "cases"), ("enterprise_legacy.sqlite3", "operational_objects")):
            with legacy_sqlite.open_snapshot(S.LEGACY_ROOT, store, self.run_dir) as h:
                for sql in WRITES:
                    with self.subTest(store=store, sql=sql):
                        with self.assertRaises(LegacyWriteRefused) as cm:
                            h.execute(sql.replace("cases", table))
                        self.assertEqual(cm.exception.code, "E-CO-LEGACY-WRITE-REFUSED")
                with self.assertRaises(LegacyWriteRefused):
                    h.executescript("DELETE FROM %s;" % table)
                with self.assertRaises(LegacyWriteRefused):
                    h.commit()

    def test_TST_CO_04_c_legacy_files_byte_identical_after_attempts(self):
        """TST-CO-04: the sandbox legacy source and the snapshot keep their pinned sha256 after all attempts."""
        for store, table in (("legacy.sqlite3", "cases"), ("enterprise_legacy.sqlite3", "operational_objects")):
            with legacy_sqlite.open_snapshot(S.LEGACY_ROOT, store, self.run_dir) as h:
                for sql in WRITES[:3]:
                    with self.assertRaises(LegacyWriteRefused):
                        h.execute(sql.replace("cases", table))
            self.assertEqual(S.sha256_file(os.path.join(S.LEGACY_ROOT, self.pins[store]["rel_path"])), self.pins[store]["sha256"])
            self.assertEqual(S.sha256_file(os.path.join(self.run_dir, "snapshots", store)), self.pins[store]["sha256"])

    def test_TST_CO_04_d_only_ro_uri_connections_to_legacy(self):
        """TST-CO-04 static: sqlite3.connect appears only in the store, the runtime check (:memory:) and the
        RO adapter, and the adapter connects with uri=True to a mode=ro&immutable=1 URI."""
        allowed = {os.path.join("hub", "store", "db.py"), os.path.join("hub", "runtime.py"),
                   os.path.join("hub", "adapters", "legacy_sqlite.py")}
        found = {}
        for d, _, fns in os.walk(os.path.join(S.CODE_ROOT, "hub")):
            for fn in fns:
                if fn.endswith(".py"):
                    p = os.path.join(d, fn)
                    tree = ast.parse(open(p, encoding="utf-8").read())
                    for n in ast.walk(tree):
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "connect" \
                                and isinstance(n.func.value, ast.Name) and n.func.value.id == "sqlite3":
                            found.setdefault(os.path.relpath(p, S.CODE_ROOT), []).append(n)
        self.assertTrue(set(found) <= allowed, sorted(found))
        calls = found[os.path.join("hub", "adapters", "legacy_sqlite.py")]
        self.assertEqual(len(calls), 1)
        self.assertTrue(any(k.arg == "uri" and getattr(k.value, "value", None) is True for k in calls[0].keywords))
        src = open(os.path.join(S.CODE_ROOT, "hub", "adapters", "legacy_sqlite.py"), encoding="utf-8").read()
        self.assertIn('"file:%s?mode=ro&immutable=1"', src)

    def test_TST_CO_04_e_schema_drift_and_hash_mismatch_fail_closed(self):
        """TST-CO-04 / AS-2 rule 4: a drifted copy fails closed (E-CO-LEGACY-SCHEMA-DRIFT unpinned, E-FX-HASH pinned)."""
        fake_root = S.tmpdir("co04e-root-")
        os.makedirs(os.path.join(fake_root, "data"))
        dst = os.path.join(fake_root, "data", "legacy.sqlite3")
        shutil.copyfile(os.path.join(S.LEGACY_ROOT, "data", "legacy.sqlite3"), dst)  # sandbox-to-sandbox copy
        con = sqlite3.connect(dst)
        con.execute("CREATE TABLE drift(x)")
        con.commit()
        con.close()
        with self.assertRaises(FixtureMismatch):
            legacy_sqlite.open_snapshot(fake_root, "legacy.sqlite3", self.run_dir, pinned=True)
        with self.assertRaises(LegacySchemaDrift) as cm:
            legacy_sqlite.open_snapshot(fake_root, "legacy.sqlite3", self.run_dir, pinned=False)
        self.assertEqual(cm.exception.details["extra"], ["drift"])

    def test_TST_CO_04_f_working_tree_source_refused(self):
        """TST-CO-04 + OD-03a: the adapter refuses a legacy source inside the original working tree (nothing copied)."""
        before = set(os.listdir(self.run_dir))
        with self.assertRaises(NotSandbox):
            legacy_sqlite.open_snapshot(S.WORKTREE, "legacy.sqlite3", self.run_dir)
        self.assertEqual(set(os.listdir(self.run_dir)), before)


if __name__ == "__main__":
    unittest.main()
