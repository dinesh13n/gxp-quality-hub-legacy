"""H001 hardening migration (Stage 27, S24 DQ-S24-09 / RS-12): insert-only triggers on the core ledger `schema_migrations`.

Recorded with its sha256 in the insert-only table `hardening_schema_migrations` (the name ends in `schema_migrations` like the other per-component ledgers).
`hub.store.db.open_hub` calls `apply()` on every open: a store without H001 gets it (two CREATE TRIGGER statements and one ledger row, one transaction, no
data touched - this is why it needs no pre-migration backup; rollback = restore the store from the backup of the previous migration, or DROP the two
triggers by hand, which is deliberately NOT a hub command); an applied H001 whose file changed is E-STORE-MIGRATION-DRIFT.
Assumption A-27-05: applying it on open (not through a separate command) is the safest default - a store can not stay without the ledger protection.
"""
import hashlib
import os

from hub.core.errors import MigrationDrift

HARDENING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hardening")
VERSION = "H001"
TABLE = "hardening_schema_migrations"
_LEDGER_DDL = ("CREATE TABLE IF NOT EXISTS hardening_schema_migrations(version TEXT PRIMARY KEY, sha256 TEXT NOT NULL, applied_at TEXT NOT NULL);\n"
               "CREATE TRIGGER IF NOT EXISTS hardening_schema_migrations_no_update BEFORE UPDATE ON hardening_schema_migrations"
               " BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;\n"
               "CREATE TRIGGER IF NOT EXISTS hardening_schema_migrations_no_delete BEFORE DELETE ON hardening_schema_migrations"
               " BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;\n")


_CACHE = {}


def migration():
    """(sha256, sql) of the H001 file, read once per process (open_hub runs for every web request; the file is part of the code and does not change at run time)."""
    if "m" not in _CACHE:
        fn = [f for f in sorted(os.listdir(HARDENING_DIR)) if f.startswith(VERSION + "_") and f.endswith(".sql")][0]
        with open(os.path.join(HARDENING_DIR, fn), "rb") as f:
            body = f.read()
        _CACHE["m"] = (hashlib.sha256(body).hexdigest(), body.decode("utf-8"))
    return _CACHE["m"]


def applied(con):
    if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (TABLE,)).fetchone() is None:
        return None
    row = con.execute("SELECT sha256 FROM hardening_schema_migrations WHERE version = ?", (VERSION,)).fetchone()
    return row[0] if row else None


def apply(con, clock):
    """Idempotent. Returns True when H001 was applied by this call."""
    digest, sql = migration()
    have = applied(con)
    if have == digest:
        return False
    if have is not None:
        raise MigrationDrift({"changed_versions": [VERSION]})
    # Every statement is idempotent (IF NOT EXISTS) and the ledger row is written LAST: a crash in between leaves a store that simply re-applies on the next open.
    con.executescript(_LEDGER_DDL)
    con.executescript(sql)
    with con:
        con.execute("INSERT OR IGNORE INTO hardening_schema_migrations(version, sha256, applied_at) VALUES (?,?,?)", (VERSION, digest, clock()))
    return True
