"""Backup / restore of the hub store together with the audit anchor file (BEH-CO-06, gate G7, ADR-015, TB-11).

backup(): consistent copy via VACUUM INTO on the hub-store connection (hub.store.db.open_hub), plus the anchor file,
          plus MANIFEST.json and SHA256SUMS (`sha256sum -c` compatible). Destination must be sandbox-safe.
restore(): verifies the backup's checksums FIRST (E-STORE-BACKUP-INVALID, nothing touched), then sets the current
           hub.sqlite3 and anchor file ASIDE under <data_dir>/pre-restore/<stamp>/ (hold-all, OD-S12-09: nothing is
           deleted), copies the backup in and re-verifies the restored checksums. The caller then runs verify-audit.
"""
import hashlib
import json
import os
import shutil

from hub.guards import sandbox
from hub.security.errors import BackupInvalid
from hub.store import db

ANCHOR_NAME = "audit-anchor.jsonl"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _stamp(ts):
    return ts.replace(":", "").replace("-", "").replace(".", "")


def _store_facts(con):
    versions = [r[0] for r in con.execute("SELECT version FROM schema_migrations ORDER BY version")]
    head = None
    if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='audit_log'").fetchone():
        r = con.execute("SELECT audit_seq, hash FROM audit_log ORDER BY audit_seq DESC LIMIT 1").fetchone()
        head = {"audit_seq": r[0], "hash": r[1]} if r else {"audit_seq": 0, "hash": None}
    return versions, head


def backup(data_dir, anchor_path, dest_root, label, clock):
    data_dir = sandbox.assert_safe_path(data_dir, "hub data directory")
    dest_root = sandbox.assert_safe_path(dest_root, "backup root")
    src_path = os.path.join(data_dir, db.HUB_DB_NAME)
    if not os.path.isfile(src_path):
        raise BackupInvalid({"reason": "no hub store to back up", "data_dir": data_dir})
    dest = os.path.join(dest_root, label)
    if os.path.exists(dest):
        raise BackupInvalid({"reason": "backup label already exists (backups are never overwritten)", "label": label})
    os.makedirs(dest)
    # All hub-store connections go through hub.store.db.open_hub (TST-CO-04 d); the copy is made with
    # VACUUM INTO (SQLite >= 3.27, floor 3.37) from that connection: a transactionally consistent snapshot.
    con = db.open_hub(data_dir)
    try:
        before = _store_facts(con)
        con.execute("VACUUM INTO ?", (os.path.join(dest, db.HUB_DB_NAME),))
        after = _store_facts(con)
    finally:
        con.close()
    if before != after:
        raise BackupInvalid({"reason": "store changed while the backup was taken; retry", "label": label})
    versions, head = after
    files = {db.HUB_DB_NAME: sha256_file(os.path.join(dest, db.HUB_DB_NAME))}
    if anchor_path and os.path.isfile(anchor_path):
        shutil.copy2(anchor_path, os.path.join(dest, ANCHOR_NAME))
        files[ANCHOR_NAME] = sha256_file(os.path.join(dest, ANCHOR_NAME))
    manifest = {"schema": "hub-backup/v1", "label": label, "created_at": clock(), "files": files,
                "schema_versions": versions, "audit_head": head, "anchor_included": ANCHOR_NAME in files}
    with open(os.path.join(dest, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    with open(os.path.join(dest, "SHA256SUMS"), "w", encoding="utf-8") as f:
        for name in sorted(files):
            f.write("%s  %s\n" % (files[name], name))
    manifest["path"] = dest
    return manifest


def verify_backup(backup_dir):
    mpath = os.path.join(backup_dir, "MANIFEST.json")
    if not os.path.isfile(mpath):
        raise BackupInvalid({"reason": "MANIFEST.json missing", "backup": backup_dir})
    with open(mpath, encoding="utf-8") as f:
        manifest = json.load(f)
    bad = [n for n, d in sorted(manifest["files"].items())
           if not os.path.isfile(os.path.join(backup_dir, n)) or sha256_file(os.path.join(backup_dir, n)) != d]
    if bad:
        raise BackupInvalid({"reason": "checksum mismatch", "files": bad})
    return manifest


def restore(backup_dir, data_dir, anchor_path, clock):
    backup_dir = sandbox.assert_safe_path(backup_dir, "backup directory")
    data_dir = sandbox.assert_safe_path(data_dir, "hub data directory")
    manifest = verify_backup(backup_dir)
    os.makedirs(data_dir, exist_ok=True)
    target = os.path.join(data_dir, db.HUB_DB_NAME)
    aside = os.path.join(data_dir, "pre-restore", _stamp(clock()))
    set_aside = []
    for p in (target, target + "-journal", target + "-wal", target + "-shm", anchor_path):
        if p and os.path.isfile(p):
            os.makedirs(aside, exist_ok=True)
            name = os.path.basename(p) if p != anchor_path else ANCHOR_NAME
            shutil.move(p, os.path.join(aside, name))
            set_aside.append(name)
    tmp = target + ".restore-tmp"
    shutil.copy2(os.path.join(backup_dir, db.HUB_DB_NAME), tmp)
    os.replace(tmp, target)
    restored = {db.HUB_DB_NAME: sha256_file(target)}
    if manifest["files"].get(ANCHOR_NAME):
        os.makedirs(os.path.dirname(anchor_path), exist_ok=True)
        shutil.copy2(os.path.join(backup_dir, ANCHOR_NAME), anchor_path)
        restored[ANCHOR_NAME] = sha256_file(anchor_path)
    match = restored == manifest["files"]
    if not match:
        raise BackupInvalid({"reason": "restored files differ from the manifest", "restored": restored})
    return {"backup": manifest["label"], "checksum_match": match, "restored": restored,
            "schema_versions": manifest["schema_versions"], "audit_head": manifest["audit_head"],
            "set_aside": set_aside, "set_aside_dir": aside if set_aside else None}
