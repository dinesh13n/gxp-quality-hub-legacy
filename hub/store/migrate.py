"""Forward-only migration runner with backup-before-migrate (TB-09, schema-migration-plan M001, rollback L2).

Baseline M000 stays in hub/store/migrations/ and is applied by hub.store.db.open_hub (INC-02, unchanged).
Forward migrations (M001+) live in hub/store/forward/ and are applied ONLY here, after a pre-migration backup of
hub.sqlite3 + the audit anchor file. Each forward migration runs in one transaction together with its
schema_migrations row. Refusals (E-STORE-MIGRATION-DRIFT, exit 15):
  * an applied migration's file changed (checksum drift);
  * the store records a version this code does not know (store newer than code -> restore the pre-migration
    backup, i.e. rollback L2, or roll the code forward).
"""
import hashlib
import os
import re
import sqlite3

from hub.core.errors import MigrationDrift
from hub.store import db

FORWARD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forward")
_VERSION = re.compile(r"^M\d{3}$")
_HEX = re.compile(r"^[0-9a-f]{64}$")
_TS = re.compile(r"^[0-9T:.\-Z]+$")


def forward_migrations():
    out = []
    for fn in sorted(os.listdir(FORWARD_DIR)):
        if fn.endswith(".sql"):
            with open(os.path.join(FORWARD_DIR, fn), "rb") as f:
                body = f.read()
            out.append((fn.split("_", 1)[0], hashlib.sha256(body).hexdigest(), body.decode("utf-8")))
    return out


def known_versions():
    return [(v, d) for v, d, _ in db.migrations()] + [(v, d) for v, d, _ in forward_migrations()]


def head_version():
    return known_versions()[-1][0]


def applied(con):
    return dict(con.execute("SELECT version, sha256 FROM schema_migrations"))


def check(con):
    """Raise MigrationDrift on unknown or changed applied versions; return (applied, pending forward)."""
    known = dict(known_versions())
    app = applied(con)
    unknown = sorted(v for v in app if v not in known)
    if unknown:
        raise MigrationDrift({"unknown_versions": unknown, "code_head": head_version(),
                              "reason": "store is newer than this code: restore the pre-migration backup (rollback L2) "
                                        "or roll the code forward"})
    changed = sorted(v for v, d in app.items() if known[v] != d)
    if changed:
        raise MigrationDrift({"changed_versions": changed})
    pending = [(v, d, sql) for v, d, sql in forward_migrations() if v not in app]
    return app, pending


def status(data_dir):
    path = os.path.join(data_dir, db.HUB_DB_NAME)
    if not os.path.isfile(path):
        return {"store": "absent", "applied": [], "pending": [v for v, _ in known_versions()], "code_head": head_version()}
    con = db.open_hub(data_dir)  # existing store only (checked above); M000 + seed are idempotent
    try:
        app, pending = check(con)
    finally:
        con.close()
    return {"store": "present", "applied": sorted(app), "pending": [v for v, _, _ in pending], "code_head": head_version()}


def has_audit(con):
    return con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='audit_log'").fetchone() is not None


def migrate(data_dir, backup_root, anchor_path, clock, target=None):
    """Bring the store to `target` (default: code head). Returns {from, to, applied, backup}."""
    con = db.open_hub(data_dir)  # guarded path; applies/validates baseline M000 (INC-02)
    try:
        app, pending = check(con)
    finally:
        con.close()
    if target is not None:
        pending = [m for m in pending if m[0] <= target]
    frm = sorted(app)[-1] if app else None
    if not pending:
        return {"from": frm, "to": frm, "applied": [], "backup": None}
    from hub.ops import backup as backup_mod  # function-level since Stage 27: breaks the ops <-> store package cycle (OD-27 debt)
    label = "pre-migrate-%s-to-%s-%s" % (frm, pending[-1][0], backup_mod._stamp(clock()))
    bk = backup_mod.backup(data_dir, anchor_path, backup_root, label, clock)
    con = db.open_hub(data_dir)
    done = []
    try:
        for version, digest, sql in pending:
            ts = clock()
            if not (_VERSION.match(version) and _HEX.match(digest) and _TS.match(ts)):
                raise MigrationDrift({"version": version, "reason": "malformed migration metadata"})
            script = "BEGIN;\n%s\nINSERT INTO schema_migrations(version, sha256, applied_at) VALUES ('%s','%s','%s');\nCOMMIT;\n" % (
                sql, version, digest, ts)
            try:
                con.executescript(script)
            except sqlite3.Error:
                if con.in_transaction:
                    con.execute("ROLLBACK")
                raise
            done.append(version)
    finally:
        con.close()
    return {"from": frm, "to": done[-1], "applied": done, "backup": bk}
