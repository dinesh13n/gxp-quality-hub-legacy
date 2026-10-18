"""AD-01 (legacy.sqlite3) / AD-02 (enterprise_legacy.sqlite3) read-only adapters (BEH-CO-03, AC-CO-04).

Snapshot first (AS-2 rule 3): the legacy file is copied into the run's sandbox directory, its sha256 recorded
(and checked against the OD-09 pin when `pinned=True`), then opened ONLY as
`file:<snapshot>?mode=ro&immutable=1` with an SQLite authorizer that denies every write/DDL/ATTACH/PRAGMA-set.
Any write attempt raises E-CO-LEGACY-WRITE-REFUSED. The legacy schema is checked against the pin and drift
fails closed (AS-2 rule 4). The legacy source itself is never opened by SQLite, so the legacy file cannot be
locked or modified (TR-09). The source must not be in the original working tree or the backup (sandbox guard).
"""
import hashlib
import json
import os
import shutil
import sqlite3
from urllib.parse import quote

from hub.core.errors import FixtureMismatch, LegacySchemaDrift, LegacyWriteRefused
from hub.guards import sandbox

PINS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline_pins.json")

_ALLOWED_ACTIONS = set([sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
                        getattr(sqlite3, "SQLITE_RECURSIVE", 33)])
_READ_PRAGMAS = set(["table_info", "table_xinfo", "index_list", "index_info", "foreign_key_list"])


def _authorizer(action, arg1, arg2, dbname, source):
    if action in _ALLOWED_ACTIONS:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_PRAGMA and arg1 in _READ_PRAGMAS:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def load_pins():
    with open(PINS_PATH, encoding="utf-8") as f:
        return json.load(f)["stores"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class ReadOnlyLegacy(object):
    """Query-only handle on a snapshot. `execute` returns a list of rows."""

    def __init__(self, con, store, provenance):
        self._con = con
        self.store = store
        self.provenance = provenance

    def execute(self, sql, params=()):
        try:
            return self._con.execute(sql, params).fetchall()
        except sqlite3.DatabaseError as e:
            msg = str(e).lower()
            if "authoriz" in msg or "readonly" in msg or "read-only" in msg:
                raise LegacyWriteRefused({"store": self.store, "sqlite": str(e)})
            raise

    def executescript(self, script):
        raise LegacyWriteRefused({"store": self.store, "reason": "executescript is not available on a legacy store"})

    def commit(self):
        raise LegacyWriteRefused({"store": self.store, "reason": "commit is not available on a legacy store"})

    def close(self):
        self._con.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def open_snapshot(legacy_root, store, run_dir, pinned=True):
    """Copy <legacy_root>/<rel_path> into <run_dir>/snapshots/, verify, open read-only."""
    pins = load_pins()
    if store not in pins:
        raise LegacySchemaDrift({"store": store, "reason": "unknown legacy store"})
    pin = pins[store]
    src = os.path.join(legacy_root, pin["rel_path"])
    sandbox.assert_safe_path(legacy_root, "legacy source root")
    sandbox.assert_safe_path(run_dir, "run directory")
    snap_dir = os.path.join(run_dir, "snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    snap = os.path.join(snap_dir, store)
    if os.path.exists(snap):  # previous snapshot in this guarded run dir (read-only file): replace it
        os.chmod(snap, 0o644)
        os.remove(snap)
    shutil.copyfile(src, snap)
    os.chmod(snap, 0o444)
    digest = sha256_file(snap)
    if pinned and digest != pin["sha256"]:
        raise FixtureMismatch({"store": store, "sha256": digest, "expected": pin["sha256"]})
    uri = "file:%s?mode=ro&immutable=1" % quote(os.path.abspath(snap))
    con = sqlite3.connect(uri, uri=True)
    con.set_authorizer(_authorizer)
    handle = ReadOnlyLegacy(con, store, {"source": store, "adapter": pin["adapter"], "source_sha256": digest,
                                         "access": "mode=ro&immutable=1"})
    tables = dict((n, [r[1] for r in con.execute('PRAGMA table_info("%s")' % n.replace('"', '""'))])
                  for (n,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1"))
    if tables != pin["tables"]:
        con.close()
        raise LegacySchemaDrift({"store": store,
                                 "missing": sorted(set(pin["tables"]) - set(tables)),
                                 "extra": sorted(set(tables) - set(pin["tables"])),
                                 "changed": sorted(t for t in set(tables) & set(pin["tables"]) if tables[t] != pin["tables"][t])})
    return handle
