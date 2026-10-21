"""M006 presence / drift check for domain services (Stage 20 DW-06; S16-D06 / AC-04).

hub.gate.dispositions, hub.review.service and hub.search.schema only need "is M006 applied and unchanged?". They imported hub.web.schema
for it - a domain -> HTTP-layer dependency. This module holds that check without importing hub.web (or any domain package); hub.web.schema
keeps the migration (apply / status) and delegates migration() / applied() / require() here, so there is one implementation. The SQL file
stays where it was applied from (hub/web/migrations/, its sha256 is what web_schema_migrations recorded); only its path is referenced here.
"""
import hashlib
import os

from hub.core.errors import MigrationDrift
from hub.security.errors import StoreNotMigrated

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "migrations")
VERSION = "M006"
TABLE = "web_schema_migrations"


def migration():
    fn = [f for f in sorted(os.listdir(MIGRATIONS_DIR)) if f.startswith(VERSION + "_") and f.endswith(".sql")][0]
    with open(os.path.join(MIGRATIONS_DIR, fn), "rb") as f:
        body = f.read()
    return hashlib.sha256(body).hexdigest(), body.decode("utf-8")


def applied(con):
    if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (TABLE,)).fetchone() is None:
        return None
    row = con.execute("SELECT sha256 FROM web_schema_migrations WHERE version = ?", (VERSION,)).fetchone()
    return row[0] if row else None


def require(con):
    """Return normally when M006 is applied and unchanged; else raise (used by every INC-08 service entry)."""
    digest, _ = migration()
    have = applied(con)
    if have is None:
        raise StoreNotMigrated({"needs": VERSION, "hint": "python -m hub.web migrate"})
    if have != digest:
        raise MigrationDrift({"changed_versions": [VERSION]})
