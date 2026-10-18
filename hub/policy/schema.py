"""M002 (policy_object, policy_events, rule_set, rule_row, active_ruleset) - applied here, not by hub.store.migrate.

Why (design notes D-02 / DEV-28): a file in hub/store/forward/ joins `migrate.known_versions()` and would break the
INC-03 test S01 (`applied == ["M001"]`), and migrate.py / that test are frozen by the add-only rule (TST-CO-05 c).
So M002 lives in hub/policy/migrations/, is applied after a backup-before-migrate (same backup routine, rollback L2)
and is recorded, with its sha256, in the insert-only table `policy_schema_migrations`.
Refusals: store below M001 (no audit_log) -> E-STORE-NOT-MIGRATED; applied M002 whose file changed -> E-STORE-MIGRATION-DRIFT.
"""
import hashlib
import os

from hub.core.errors import MigrationDrift
from hub.ops import backup as backup_mod
from hub.security import audit
from hub.security.errors import StoreNotMigrated
from hub.store import db, migrate

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
VERSION = "M002"
TABLE = "policy_schema_migrations"
_TABLE_DDL = ("CREATE TABLE IF NOT EXISTS policy_schema_migrations(version TEXT PRIMARY KEY, sha256 TEXT NOT NULL,"
              " applied_at TEXT NOT NULL);\n"
              "CREATE TRIGGER IF NOT EXISTS policy_schema_migrations_no_update BEFORE UPDATE ON policy_schema_migrations"
              " BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;\n"
              "CREATE TRIGGER IF NOT EXISTS policy_schema_migrations_no_delete BEFORE DELETE ON policy_schema_migrations"
              " BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;\n")


def migration():
    fn = [f for f in sorted(os.listdir(MIGRATIONS_DIR)) if f.startswith(VERSION + "_") and f.endswith(".sql")][0]
    with open(os.path.join(MIGRATIONS_DIR, fn), "rb") as f:
        body = f.read()
    return hashlib.sha256(body).hexdigest(), body.decode("utf-8")


def applied(con):
    if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (TABLE,)).fetchone() is None:
        return None
    row = con.execute("SELECT sha256 FROM policy_schema_migrations WHERE version = ?", (VERSION,)).fetchone()
    return row[0] if row else None


def require(con):
    """Return normally when M002 is applied and unchanged; else raise (used by every PolicyService entry)."""
    digest, _ = migration()
    have = applied(con)
    if have is None:
        raise StoreNotMigrated({"needs": VERSION, "hint": "python -m hub.policy migrate"})
    if have != digest:
        raise MigrationDrift({"changed_versions": [VERSION]})


def status(con):
    digest, _ = migration()
    have = applied(con)
    return {"version": VERSION, "state": "absent" if have is None else ("applied" if have == digest else "drift"),
            "audit_present": migrate.has_audit(con)}


def apply(data_dir, backup_root, anchor_path, clock, correlation_id="policy-migrate"):
    """Apply M002 after a backup. Returns {"applied": bool, "backup": dict|None}."""
    digest, sql = migration()
    con = db.open_hub(data_dir)
    try:
        migrate.check(con)
        if not migrate.has_audit(con):
            raise StoreNotMigrated({"needs": "M001", "hint": "python -m hub.admin migrate"})
        have = applied(con)
        if have is not None:
            if have != digest:
                raise MigrationDrift({"changed_versions": [VERSION]})
            return {"applied": False, "backup": None}
    finally:
        con.close()
    label = "pre-policy-%s-%s" % (VERSION, backup_mod._stamp(clock()))
    bk = backup_mod.backup(data_dir, anchor_path, backup_root, label, clock)
    con = db.open_hub(data_dir)
    try:
        ts = clock()
        script = "BEGIN;\n%s\n%s\nINSERT INTO policy_schema_migrations(version, sha256, applied_at) VALUES ('%s','%s','%s');\nCOMMIT;\n" % (
            _TABLE_DDL, sql, VERSION, digest, ts)
        try:
            con.executescript(script)
        except Exception:
            if con.in_transaction:
                con.execute("ROLLBACK")
            raise
        audit.append(con, clock, anchor=audit.Anchor(anchor_path, 100), actor="hub", actor_kind="system",
                     action="POLICY_SCHEMA_APPLIED", outcome="success", correlation_id=correlation_id,
                     object_ref="schema:" + VERSION,
                     details={"version": VERSION, "sha256": digest, "pre_migration_backup": bk["label"]})
        audit.write_anchor(con, anchor_path)
    finally:
        con.close()
    return {"applied": True, "backup": bk}
