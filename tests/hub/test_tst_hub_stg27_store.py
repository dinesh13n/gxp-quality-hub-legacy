"""Stage 27 tests, part 3: store hardening and the contract-schema gap (DW-26; FAC-09, DQ-S24-09 / RS-12; assumption A-27-05). Synthetic, unvalidated.

  H01  H001: schema_migrations is insert-only (UPDATE and DELETE abort with E-SEC-RETAINED, INSERT of a new version still works), the ledger row carries the file sha256
  H02  H001 is idempotent, applied to a store that was created without it, and drift of the applied file is E-STORE-MIGRATION-DRIFT; its own ledger is insert-only too
  H04  the store file is 0600, a newly created data directory 0700, a new anchor file 0600 (S27-DEV-14)
  H03  the hardening tables are in the retained-table register and the data map (a new table without a decision fails there)
  C01  FAC-09: the 23 committed store-table schemas equal the live DDL, use only validator-supported keywords, accept the real rows of a full scenario, reject drift
  C02  the 17th schema (OP-INT-01 intake envelope): equals the handler's field table, accepts what the endpoint accepts, rejects what it refuses
  R01  the regenerated error registry only ADDS to the Stage 12 v0.2 registry (exactly the three Stage 27 codes), and every code has a status and an exit code
"""
import copy
import glob
import json
import os
import sqlite3
import unittest

import _inc06 as I
import _inc08 as W
import _schema_lite as L
import _stg23 as T23
import _stg27 as T
from hub.core.errors import MigrationDrift
from hub.security import datamap, tables
from hub.store import db, hardening


def setUpModule():
    T.skip_in_inner_egress_run()


class _Base(unittest.TestCase):
    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def wstore(self, *a, **kw):
        st = W.WStore(*a, **kw)
        self.stores.append(st)
        return st


class TST_HUB_STG27_Hardening(_Base):

    def test_TST_HUB_STG27_H01_schema_migrations_is_insert_only(self):
        """H01: UPDATE and DELETE on schema_migrations abort with E-SEC-RETAINED; an INSERT (a new migration) still works; the H001 ledger row has the sha256 of the SQL file."""
        st = self.wstore(loaded=False)
        con = st.con
        n = con.execute("SELECT count(*) FROM schema_migrations").fetchone()[0]
        self.assertGreaterEqual(n, 1)
        for sql in ("UPDATE schema_migrations SET sha256 = 'x'", "DELETE FROM schema_migrations", "DELETE FROM schema_migrations WHERE version = 'M001'",
                    "UPDATE schema_migrations SET applied_at = applied_at WHERE version = 'M000'"):
            with self.assertRaises(sqlite3.DatabaseError, msg=sql) as cm:
                con.execute(sql)
            self.assertIn("E-SEC-RETAINED", str(cm.exception))
        self.assertEqual(con.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], n)
        con.execute("INSERT INTO schema_migrations(version, sha256, applied_at) VALUES ('M999-TEST', 'abc', '2026-01-01T00:00:00Z')")
        self.assertEqual(con.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], n + 1)
        digest, _sql = hardening.migration()
        self.assertEqual(con.execute("SELECT sha256 FROM hardening_schema_migrations WHERE version = 'H001'").fetchone()[0], digest)
        trig = sorted(r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'trigger' AND tbl_name = 'schema_migrations'"))
        self.assertEqual(trig, ["schema_migrations_no_delete", "schema_migrations_no_update"])

    def test_TST_HUB_STG27_H02_h001_is_idempotent_retrofitted_and_drift_checked(self):
        """H02: apply() on an up-to-date store changes nothing and returns False; on a store that has the migrations but not H001 it adds the triggers and the ledger row (True);
        a changed ledger digest -> MigrationDrift; the H001 ledger is itself insert-only; reopening the store directory through db.open_hub keeps everything."""
        st = self.wstore(loaded=False)
        con, clock = st.con, st.clock
        self.assertFalse(hardening.apply(con, clock))
        before = con.execute("SELECT version, sha256, applied_at FROM hardening_schema_migrations").fetchall()
        self.assertFalse(hardening.apply(con, clock))
        self.assertEqual(con.execute("SELECT version, sha256, applied_at FROM hardening_schema_migrations").fetchall(), before)
        # simulate a store from before Stage 27: no H001 ledger, no triggers
        for t in ("hardening_schema_migrations_no_update", "hardening_schema_migrations_no_delete", "schema_migrations_no_update", "schema_migrations_no_delete"):
            con.execute('DROP TRIGGER "%s"' % t)
        con.execute("DROP TABLE hardening_schema_migrations")
        con.commit()
        self.assertIsNone(hardening.applied(con))
        con.execute("UPDATE schema_migrations SET applied_at = applied_at")  # allowed again: this is the pre-H001 state
        self.assertTrue(hardening.apply(con, clock))
        self.assertEqual(hardening.applied(con), hardening.migration()[0])
        with self.assertRaises(sqlite3.DatabaseError):
            con.execute("DELETE FROM schema_migrations")
        for sql in ("UPDATE hardening_schema_migrations SET sha256 = 'x'", "DELETE FROM hardening_schema_migrations"):
            with self.assertRaises(sqlite3.DatabaseError, msg=sql) as cm:
                con.execute(sql)
            self.assertIn("E-SEC-RETAINED", str(cm.exception))
        # drift: a ledger row that does not match the file
        con.execute('DROP TRIGGER "hardening_schema_migrations_no_update"')
        con.execute("UPDATE hardening_schema_migrations SET sha256 = 'f' WHERE version = 'H001'")
        con.commit()
        with self.assertRaises(MigrationDrift):
            hardening.apply(con, clock)
        # a real reopen of the data directory through open_hub applies / keeps H001 and seeds the rest as before
        d = T.S.tmpdir("s27-h02-")
        c1 = db.open_hub(d)
        c1.close()
        c2 = db.open_hub(d)
        self.assertEqual(c2.execute("SELECT count(*) FROM hardening_schema_migrations").fetchone()[0], 1)
        self.assertEqual(sorted(r[0] for r in c2.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='schema_migrations'")),
                         ["schema_migrations_no_delete", "schema_migrations_no_update"])
        c2.close()

    def test_TST_HUB_STG27_H04_store_files_are_owner_only(self):
        """H04 (S27-DEV-14): a data directory created by open_hub is 0700, the store file is 0600 even under a permissive umask and after a reopen of a file that was group / world
        readable (only group / other bits are removed: a read-only 0444 file becomes 0400, never writable), and an audit anchor file created by write_anchor is 0600 (an existing anchor file keeps its mode)."""
        from hub.security import audit
        old = os.umask(0)
        try:
            base = T.S.tmpdir("s27-h04-")
            d = os.path.join(base, "newdir")
            con = db.open_hub(d)
            self.assertEqual(os.stat(d).st_mode & 0o777, 0o700)
            dbp = os.path.join(d, db.HUB_DB_NAME)
            self.assertEqual(os.stat(dbp).st_mode & 0o777, 0o600)
            con.close()
            os.chmod(dbp, 0o666)
            db.open_hub(d).close()
            self.assertEqual(os.stat(dbp).st_mode & 0o777, 0o600)
            os.chmod(dbp, 0o444)  # a deliberately read-only store is NOT made writable by the open (S26 C01); only the group / other bits go
            try:
                db.open_hub(d).close()
            except sqlite3.DatabaseError:
                pass
            self.assertEqual(os.stat(dbp).st_mode & 0o777, 0o400)
            os.chmod(dbp, 0o600)
            st = self.wstore(loaded=False)
            con = st.con
            audit.append(con, st.clock, actor="a", actor_kind="human", action="LOGIN", outcome="success", correlation_id="t-h04")
            con.commit()
            fresh = os.path.join(base, "anchors", "a.log")
            audit.write_anchor(con, fresh)
            self.assertEqual(os.stat(fresh).st_mode & 0o777, 0o600)
            old_anchor = os.path.join(base, "old.log")
            with open(old_anchor, "w") as f:
                f.write("")
            os.chmod(old_anchor, 0o640)
            audit.append(con, st.clock, actor="a", actor_kind="human", action="LOGIN", outcome="success", correlation_id="t-h04b")
            con.commit()
            audit.write_anchor(con, old_anchor)
            self.assertEqual(os.stat(old_anchor).st_mode & 0o777, 0o640)
        finally:
            os.umask(old)

    def test_TST_HUB_STG27_H03_registers_know_the_hardening_tables(self):
        """H03: schema_migrations and hardening_schema_migrations are RETAINED in the table register and have a data class in the data map."""
        self.assertEqual(tables.disposition("schema_migrations"), tables.RETAINED)
        self.assertEqual(tables.disposition("hardening_schema_migrations"), tables.RETAINED)
        self.assertIn("hardening_schema_migrations", tables.RETAINED_TABLES)
        self.assertEqual(datamap.TABLE_CLASS["hardening_schema_migrations"], "C1")


class TST_HUB_STG27_Schemas(_Base):
    _cache = {}

    def scenario(self):
        if "s" not in TST_HUB_STG27_Schemas._cache:
            st, objs, info = T23.scenario(self)
            st.set_mode("event")  # a Zone H write: policy_events / audit rows by a synthetic holder
            st.con.commit()
            rows = {}
            for t in T.NO_SCHEMA_23:
                cur = st.con.execute("SELECT * FROM %s" % t)
                cols = [c[0] for c in cur.description]
                rows[t] = [dict(zip(cols, r)) for r in cur.fetchall()]
            TST_HUB_STG27_Schemas._cache["s"] = (st, rows, dict((t, table_schema_of(st, t)) for t in T.NO_SCHEMA_23))
        return TST_HUB_STG27_Schemas._cache["s"]

    def test_TST_HUB_STG27_C01_store_table_schemas_match_the_ddl_and_the_real_rows(self):
        """C01 (FAC-09): 23 committed schemas (docs/27-hardening/schemas/store-tables/) are exactly what the live DDL yields (so a column change fails here until the schema is
        regenerated and reviewed); they use only keywords the stdlib validator supports; every real row of the scenario validates; a planted extra column, a missing required
        column, a wrong type and an out-of-vocabulary enum value are each rejected; at least 12 of the 23 tables hold rows (14 today) (the rest are schema-checked only)."""
        st, rows, live = self.scenario()
        files = sorted(glob.glob(os.path.join(T.SCHEMA_DIR, "*.schema.json")))
        self.assertEqual([os.path.basename(f) for f in files], sorted(t.replace("_", "-") + ".schema.json" for t in T.NO_SCHEMA_23))
        report, with_rows = [], 0
        for t in T.NO_SCHEMA_23:
            with open(os.path.join(T.SCHEMA_DIR, t.replace("_", "-") + ".schema.json"), encoding="utf-8") as f:
                committed = json.load(f)
            self.assertEqual(committed, live[t], t)
            self.assertEqual(L.unsupported(committed), [], t)
            bad = 0
            for row in rows[t]:
                es = L.errors(committed, row)
                self.assertEqual(es, [], (t, es[:3]))
            if rows[t]:
                with_rows += 1
                good = rows[t][0]
                x = copy.deepcopy(good)
                x["surprise_column"] = 1
                self.assertNotEqual(L.errors(committed, x), [], t)
                if committed["required"]:
                    y = copy.deepcopy(good)
                    y.pop(committed["required"][0])
                    self.assertNotEqual(L.errors(committed, y), [], t)
                for col, prop in committed["properties"].items():
                    ty = prop["type"] if isinstance(prop["type"], str) else prop["type"][0]
                    z = copy.deepcopy(good)
                    z[col] = [1] if ty != "object" else 1  # a list is never a valid column value
                    self.assertNotEqual(L.errors(committed, z), [], (t, col))
                    if "enum" in prop and good[col] is not None:
                        z = copy.deepcopy(good)
                        z[col] = "NOT_IN_VOCABULARY"
                        self.assertNotEqual(L.errors(committed, z), [], (t, col, "enum"))
            report.append({"table": t, "columns": len(committed["properties"]), "rows_validated": len(rows[t]), "enum_columns": sorted(k for k, v in committed["properties"].items() if "enum" in v)})
        self.assertGreaterEqual(with_rows, 12)
        T.write_evidence("store-table-schemas.json", {"label": T.LABEL, "tables": 23, "tables_with_rows": with_rows, "per_table": report,
                                                      "tables_without_rows": sorted(t for t in T.NO_SCHEMA_23 if not rows[t])})

    def test_TST_HUB_STG27_C02_intake_envelope_schema_matches_the_endpoint(self):
        """C02 (FAC-09, the 17th schema): the schema's envelope properties equal the handler's field table (hub.web.api._ENV) and its required list equals the mandatory
        fields; the request bodies the endpoint accepts as well-formed (201) validate; the ones it refuses with E-REQ-INVALID (unknown field, missing envelope, wrong container type) do not; a missing or mistyped envelope FIELD is rejected by the schema while the transport accepts it and the intake rules quarantine the item."""
        from hub.web import api
        with open(T.ENVELOPE_PATH, encoding="utf-8") as f:
            sch = json.load(f)
        self.assertEqual(L.unsupported(sch), [])
        env = sch["properties"]["envelope"]
        self.assertEqual(sorted(env["properties"]), sorted(api._ENV))
        self.assertEqual(sorted(env["required"]), sorted(k for k, (_t, req) in api._ENV.items() if req))
        st = self.wstore(loaded=False)
        from hub.web import tokens as wtokens
        st.authn.create_user("svc-int", st.pw, ["integration"], "op", kind="service")
        tok = wtokens.issue(st.con, st.clock, st.anchor, "svc-int", "s27 synthetic service token", "op")
        st.con.commit()
        good = {"source_key": "S27-1", "partner": "north", "schema_rev": "1.0", "source_ts": "2025-01-01T00:00:00+00:00", "ref_id": "C1", "record_kind": "OOS_RESULT",
                "payload_text": json.dumps({"business_key": "C1"})}
        no_rev = dict(good)
        del no_rev["schema_rev"]
        null_rev = dict(good, schema_rev=None)
        for env_doc in (good, no_rev, null_rev):
            body = {"source": "partner_feed", "envelope": env_doc}
            self.assertEqual(L.errors(sch, body), [], env_doc)
            r = st.call("POST", "/api/v2/intake/items", body, token=tok)
            self.assertEqual(r.status, 201, r.text)
        body = {"source": "partner_feed", "envelope": good, "idempotency_key": "k-1"}
        self.assertEqual(L.errors(sch, body), [])
        self.assertEqual(st.call("POST", "/api/v2/intake/items", body, token=tok).status, 201)
        refused = []
        for name, b in (("unknown envelope field", {"source": "partner_feed", "envelope": dict(good, extra=1)}),
                        ("unknown top-level", {"source": "partner_feed", "envelope": good, "mode": "x"}),
                        ("no envelope", {"source": "partner_feed"}), ("envelope not object", {"source": "partner_feed", "envelope": "x"}),
                        ("source not string", {"source": 3, "envelope": good})):
            self.assertNotEqual(L.errors(sch, b), [], name)
            r = st.call("POST", "/api/v2/intake/items", b, token=tok)
            self.assertEqual((r.status, r.code), (400, "E-REQ-INVALID"), name)
            refused.append(name)
        # the transport accepts a missing / mistyped envelope field and the intake rules quarantine the item: the schema is the stricter INPUT contract (not a second validator)
        for name, b in (("missing ref_id", {"source": "partner_feed", "envelope": dict((k, v) for k, v in good.items() if k != "ref_id")}),
                        ("partner wrong type", {"source": "partner_feed", "envelope": dict(good, partner=5)})):
            self.assertNotEqual(L.errors(sch, b), [], name)
            r = st.call("POST", "/api/v2/intake/items", b, token=tok)
            self.assertEqual(r.status, 201, (name, r.text))
            self.assertNotEqual(r.json()["outcome"], "ACCEPTED", name)
        self.assertEqual(len(refused), 5)

    def test_TST_HUB_STG27_R01_error_registry_only_adds_to_the_stage_12_registry(self):
        """R01: every code of the Stage 12 v0.2 registry is present in the Stage 27 registry with the same area, class, HTTP status and exit code; the new codes are exactly
        E-REQ-TIMEOUT, E-REQ-RATE-LIMITED and E-STORE-UNAVAILABLE (spec addenda pending, S27-DEV-10); no exit-code problem."""
        base = os.path.join(T.S.CODE_ROOT, "docs", "23-human-control", "stage12-v0.2", "error-code-registry.json")
        new = os.path.join(T.S.CODE_ROOT, "docs", "27-hardening", "error-registry", "error-code-registry.json")
        with open(base, encoding="utf-8") as f:
            old = json.load(f)
        with open(new, encoding="utf-8") as f:
            cur = json.load(f)
        o = dict((c["code"], c) for c in old["codes"])
        n = dict((c["code"], c) for c in cur["codes"])
        for code, c in o.items():
            self.assertIn(code, n, code)
            for k in ("area", "classes", "exit_code", "http", "in_stage12_spec", "module"):
                self.assertEqual(n[code][k], c[k], (code, k))
        self.assertEqual(sorted(set(n) - set(o)), ["E-REQ-RATE-LIMITED", "E-REQ-TIMEOUT", "E-STORE-UNAVAILABLE"])
        self.assertEqual((n["E-REQ-TIMEOUT"]["http"], n["E-REQ-RATE-LIMITED"]["http"], n["E-STORE-UNAVAILABLE"]["http"]), (408, 429, 503))
        self.assertEqual(cur["exit_code_problems"], [])
        self.assertEqual(cur["count"], old["count"] + 3)


def table_schema_of(st, t):
    return T.table_schema(st.con, t)


if __name__ == "__main__":
    unittest.main()
