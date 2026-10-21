"""M006 (service_token, service_token_revocation, rule_trace, flag_action) - applied here, not by hub.store.migrate (same reason as
M002..M005, inc08-design-notes D-02).

Recorded with its sha256 in the insert-only table `web_schema_migrations`. Refusals: store below M001 (no audit_log) or M002..M005
-> E-STORE-NOT-MIGRATED; applied M006 whose file changed -> E-STORE-MIGRATION-DRIFT. Backup-before-migrate with the same backup routine as
M001..M005 (rollback L2).
"""
import os

from hub.core.errors import MigrationDrift
from hub.decision import schema as decision_schema
from hub.intake import schema as intake_schema
from hub.ops import backup as backup_mod
from hub.policy import schema as policy_schema
from hub.runs import schema as runs_schema
from hub.security import audit
from hub.security.errors import StoreNotMigrated
from hub.store import db, m006, migrate

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
VERSION = "M006"
TABLE = "web_schema_migrations"
_TABLE_DDL = ("CREATE TABLE IF NOT EXISTS web_schema_migrations(version TEXT PRIMARY KEY, sha256 TEXT NOT NULL,"
              " applied_at TEXT NOT NULL);\n"
              "CREATE TRIGGER IF NOT EXISTS web_schema_migrations_no_update BEFORE UPDATE ON web_schema_migrations"
              " BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;\n"
              "CREATE TRIGGER IF NOT EXISTS web_schema_migrations_no_delete BEFORE DELETE ON web_schema_migrations"
              " BEGIN SELECT RAISE(ABORT,'E-SEC-RETAINED'); END;\n")
_NEEDS = (("M002", policy_schema, "python -m hub.policy migrate"), ("M003", decision_schema, "python -m hub.decision migrate"),
          ("M004", intake_schema, "python -m hub.intake migrate"), ("M005", runs_schema, "python -m hub.runs migrate"))


def migration():
    return m006.migration()  # Stage 20 DW-06: one implementation in hub.store.m006 (domain services import that, not hub.web)


def applied(con):
    return m006.applied(con)


def require(con):
    """Return normally when M006 is applied and unchanged; else raise (used by every INC-08 service entry). Same logic as hub.store.m006.require,
    kept on this module's own migration() / applied() so the HTTP layer's start-up check behaves exactly as before (and stays patchable)."""
    digest, _ = migration()
    have = applied(con)
    if have is None:
        raise StoreNotMigrated({"needs": VERSION, "hint": "python -m hub.web migrate"})
    if have != digest:
        raise MigrationDrift({"changed_versions": [VERSION]})


def status(con):
    digest, _ = migration()
    have = applied(con)
    return {"version": VERSION, "state": "absent" if have is None else ("applied" if have == digest else "drift"),
            "audit_present": migrate.has_audit(con), "policy_m002": policy_schema.applied(con) is not None,
            "decision_m003": decision_schema.applied(con) is not None, "intake_m004": intake_schema.applied(con) is not None,
            "runs_m005": runs_schema.applied(con) is not None}


def apply(data_dir, backup_root, anchor_path, clock, correlation_id="web-migrate"):
    """Apply M006 after a backup. Returns {"applied": bool, "backup": dict|None}."""
    digest, sql = migration()
    con = db.open_hub(data_dir)
    try:
        migrate.check(con)
        if not migrate.has_audit(con):
            raise StoreNotMigrated({"needs": "M001", "hint": "python -m hub.admin migrate"})
        for needs, mod, hint in _NEEDS:
            if mod.applied(con) is None:
                raise StoreNotMigrated({"needs": needs, "hint": hint})
        have = applied(con)
        if have is not None:
            if have != digest:
                raise MigrationDrift({"changed_versions": [VERSION]})
            return {"applied": False, "backup": None}
    finally:
        con.close()
    label = "pre-web-%s-%s" % (VERSION, backup_mod._stamp(clock()))
    bk = backup_mod.backup(data_dir, anchor_path, backup_root, label, clock)
    con = db.open_hub(data_dir)
    try:
        ts = clock()
        script = "BEGIN;\n%s\n%s\nINSERT INTO web_schema_migrations(version, sha256, applied_at) VALUES ('%s','%s','%s');\nCOMMIT;\n" % (
            _TABLE_DDL, sql, VERSION, digest, ts)
        try:
            con.executescript(script)
        except Exception:
            if con.in_transaction:
                con.execute("ROLLBACK")
            raise
        audit.append(con, clock, anchor=audit.Anchor(anchor_path, 100), actor="hub", actor_kind="system",
                     action="WEB_SCHEMA_APPLIED", outcome="success", correlation_id=correlation_id,
                     object_ref="schema:" + VERSION,
                     details={"version": VERSION, "sha256": digest, "pre_migration_backup": bk["label"]})
        audit.write_anchor(con, anchor_path)
    finally:
        con.close()
    return {"applied": True, "backup": bk}
