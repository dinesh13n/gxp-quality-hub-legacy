"""Open the hub store inside a sandboxed data directory and apply migrations (forward-only, checksummed)."""
import datetime
import hashlib
import os
import sqlite3

from hub.core.errors import MigrationDrift
from hub.guards import sandbox

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
HUB_DB_NAME = "hub.sqlite3"


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def migrations():
    out = []
    for fn in sorted(os.listdir(MIGRATIONS_DIR)):
        if fn.endswith(".sql"):
            with open(os.path.join(MIGRATIONS_DIR, fn), "rb") as f:
                body = f.read()
            out.append((fn.split("_", 1)[0], hashlib.sha256(body).hexdigest(), body.decode("utf-8")))
    return out


def open_hub(data_dir, clock=_utc_now):
    """Return a connection to <data_dir>/hub.sqlite3 with all migrations applied (data_dir is guarded)."""
    data_dir = sandbox.assert_safe_path(data_dir, "hub data directory")
    os.makedirs(data_dir, mode=0o700, exist_ok=True)  # Stage 27 S27-DEV-14: a newly created data directory is owner-only
    con = sqlite3.connect(os.path.join(data_dir, HUB_DB_NAME))
    try:  # the store holds password hashes and session digests: drop the group / other bits, never ADD a bit (a deliberately read-only 0444 file stays read-only)
        mode = os.stat(os.path.join(data_dir, HUB_DB_NAME)).st_mode & 0o777
        if mode & 0o077:
            os.chmod(os.path.join(data_dir, HUB_DB_NAME), mode & 0o700)
    except OSError:
        pass  # best effort: a file owned by someone else keeps its mode
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, sha256 TEXT NOT NULL, applied_at TEXT NOT NULL)")
    applied = dict(con.execute("SELECT version, sha256 FROM schema_migrations"))
    for version, digest, sql in migrations():
        if version in applied:
            if applied[version] != digest:
                con.close()
                raise MigrationDrift({"version": version})
            continue
        with con:
            con.executescript(sql)
            con.execute("INSERT INTO schema_migrations(version, sha256, applied_at) VALUES (?,?,?)",
                        (version, digest, clock()))
    from hub.store import hardening  # Stage 27 H001: insert-only triggers on schema_migrations
    hardening.apply(con, clock)
    from hub.coexistence import register
    register.seed(con)
    return con
