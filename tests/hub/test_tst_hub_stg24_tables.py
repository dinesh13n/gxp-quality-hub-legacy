"""Stage 24 table-disposition tests (DW-19 'RETAINED_TABLES gap'; RF-02, GC-02). Synthetic, unvalidated.

  S01  the register (hub/security/tables.py) equals the live fully migrated store (M000..M007): every table has a disposition, every `retained`
       table has an aborting BEFORE DELETE trigger, no other table has one
  S02  scan.RETAINED_TABLES is the register's retained set and contains the Stage 15 list; the deletion-path grep catches a planted delete of each
       newly covered table; the real hub/ tree and a migrated store are clean
  S03  the delete / drop-table statements in product code are exactly the reviewed sites
  S04  a delete on every populated retained table is refused by the store
"""
import os
import re
import unittest

import _support as S
import _inc09 as N
import _stg23 as T23
import _stg24 as T
from hub.security import scan, tables

OLD_STAGE15 = ("audit_log", "principal", "principal_role", "session", "login_attempt", "release_record", "release_gate_result", "deviation_register",
               "coexistence_inventory", "decision_events", "policy_object", "policy_events", "raw_intake", "intake_outcome", "crosswalk_link",
               "crosswalk_link_event", "run_event", "evidence_record")


def setUpModule():
    T.skip_in_inner_egress_run()


def _aborting_delete_triggers(con):
    out = set()
    for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
        if tables.ignored(name):
            continue
        for (sql,) in con.execute("SELECT sql FROM sqlite_master WHERE type = 'trigger' AND tbl_name = ?", (name,)):
            if re.search(r"(?is)BEFORE\s+DELETE\s+ON\s+%s\b.*RAISE\s*\(\s*ABORT" % name, sql or ""):
                out.add(name)
    return out


class TST_HUB_STG24_Tables(unittest.TestCase):
    def setUp(self):
        self.st = N.R2Store(loaded=False)

    def tearDown(self):
        self.st.close()

    def live(self):
        return set(r[0] for r in self.st.con.execute("SELECT name FROM sqlite_master WHERE type = 'table'") if not tables.ignored(r[0]))

    def test_TST_HUB_STG24_S01_register_equals_the_live_store(self):
        """S01 (DW-19): 44 tables in the M000..M007 store = 44 in the register; retained <=> aborting BEFORE DELETE trigger."""
        live = self.live()
        self.assertEqual(live - set(tables.TABLES), set(), "table without a disposition")
        self.assertEqual(set(tables.TABLES) - live, set(), "register entry for a table that does not exist")
        trig = _aborting_delete_triggers(self.st.con)
        retained = set(tables.RETAINED_TABLES)
        self.assertEqual(retained - trig, set(), "retained table without an aborting delete trigger")
        self.assertEqual(trig - retained, set(), "table with an aborting delete trigger that the register does not call retained")
        for t, (d, reason) in tables.TABLES.items():
            self.assertIn(d, (tables.RETAINED, tables.MUTABLE, tables.DERIVED), t)
            self.assertTrue(reason.strip(), t)
        T.write_evidence("store-table-dispositions.json", {
            "label": T.LABEL, "tables": len(live), "retained": sorted(retained),
            "mutable": sorted(t for t, (d, _) in tables.TABLES.items() if d == tables.MUTABLE),
            "derived": sorted(t for t, (d, _) in tables.TABLES.items() if d == tables.DERIVED),
            "stage15_list_size": len(OLD_STAGE15), "added_by_stage24": sorted(retained - set(OLD_STAGE15)),
            "tst_nfr_10_names_zone_h_action_which_is_not_a_table": "zone_h_action" not in live})

    def test_TST_HUB_STG24_S02_scan_list_is_the_register_and_the_grep_catches_every_new_table(self):
        """S02 (DW-19): RETAINED_TABLES = register; Stage 15's 18 names are inside; a planted delete / drop of each of the newly covered tables (21 in Stage 24, 23 since Stage 27 H001) is found."""
        self.assertEqual(tuple(scan.RETAINED_TABLES), tuple(tables.RETAINED_TABLES))
        self.assertTrue(set(OLD_STAGE15) <= set(scan.RETAINED_TABLES))
        added = sorted(set(scan.RETAINED_TABLES) - set(OLD_STAGE15))
        self.assertEqual(len(added), 23)  # Stage 27 H001: schema_migrations (now insert-only) and hardening_schema_migrations
        d = S.tmpdir("s24-grep-")
        p = os.path.join(d, "planted.py")
        with open(p, "w", encoding="utf-8") as f:
            for t in added:
                f.write('con.execute("DEL' + 'ETE FROM %s")\ncon.execute("DR' % t + 'OP TABLE %s")\n' % t)
        hits = scan.deletion_grep([d])
        self.assertEqual(sorted(set(h["table"] for h in hits)), added)
        self.assertEqual(len(hits), 2 * len(added))
        rep = scan.run(S.CODE_ROOT, self.st.con)
        self.assertEqual(rep["tables_without_delete_trigger"], [])
        self.assertEqual(rep["deletion_findings"], [])
        self.assertEqual(rep["secret_findings"], [])

    def test_TST_HUB_STG24_S03_product_delete_sites_are_the_reviewed_ones(self):
        """S03 (DW-19): every delete / drop-table statement in hub/**/*.py|.sql, by (file, table), equals REVIEWED_DELETE_SITES; a new site is a finding."""
        found = {}
        rx = (scan._DELETE, scan._DROP)
        base = os.path.join(S.CODE_ROOT, "hub")
        for d, dirs, fns in os.walk(base):
            dirs[:] = sorted(x for x in dirs if x != "__pycache__")
            for fn in fns:
                if fn.endswith((".py", ".sql")):
                    rel = os.path.relpath(os.path.join(d, fn), base).replace(os.sep, "/")
                    with open(os.path.join(d, fn), encoding="utf-8") as f:
                        for line in f:
                            for r in rx:
                                for m in r.finditer(line):
                                    t = m.group(1)
                                    if not tables.ignored(t) and t.lower() != "temp":
                                        found[(rel, t)] = found.get((rel, t), 0) + 1
        self.assertEqual(found, tables.REVIEWED_DELETE_SITES)
        for (_f, t) in found:
            self.assertNotEqual(tables.disposition(t), tables.RETAINED, t)

    def test_TST_HUB_STG24_S04_delete_is_refused_on_populated_retained_tables(self):
        """S04 (DW-19): with a populated store, a bulk delete on each retained table that has rows raises; tables with no rows are listed, not claimed."""
        import sqlite3
        st, _objs, _extra = T23.scenario(self)  # populates the M001..M006 tables through the real services
        try:
            refused, empty = [], []
            for t in tables.RETAINED_TABLES:
                if not st.con.execute("SELECT 1 FROM sqlite_master WHERE name = ?", (t,)).fetchone():
                    continue
                if st.con.execute("SELECT count(*) FROM %s" % t).fetchone()[0] == 0:
                    empty.append(t)
                    continue
                with self.assertRaises(sqlite3.DatabaseError, msg=t):
                    st.con.execute("DELETE FROM %s" % t)
                refused.append(t)
            self.assertGreaterEqual(len(refused), 20)
            T.write_evidence("delete-refusal.json", {"label": T.LABEL, "refused": refused, "retained_but_empty_in_this_scenario": empty})
        finally:
            st.close()

    def wstore(self, *a, **kw):
        import _inc08 as W
        return W.WStore(*a, **kw)


if __name__ == "__main__":
    unittest.main()
