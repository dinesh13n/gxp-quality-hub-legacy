"""Shared helpers for the Stage 15 INC-03 hub tests (C2 access & audit, M001, backup/restore, release checklist).

Everything is created under HUB_SANDBOX_ROOT (S.tmpdir) - never inside the repository working tree (OD-03a).
Passwords are generated at run time (no credential literals in the code base, AC-SEC-18).
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys

import _support as S
from hub import config
from hub.control import flags as control_flags
from hub.security import audit, auth, settings
from hub.security.canonical import FixedClock
from hub.store import db, migrate

ANCHOR = "audit-anchor.jsonl"
TEST_APPROVAL_REF = "TEST-SYNTHETIC-REF (a test marker, not a human approval)"  # Stage 23 DW-17: test configs that set a non-default flag carry it


def password():
    return "pw-" + os.urandom(12).hex()


def write_config(base, extra=None, anchor_every=100):
    cfg = {"audit": {"anchor_path": os.path.join(base, "anchor", ANCHOR), "anchor_every": anchor_every}}
    for k, v in (extra or {}).items():
        cfg.setdefault(k, {}).update(v) if isinstance(v, dict) else cfg.__setitem__(k, v)
    refs = dict((p, TEST_APPROVAL_REF) for p, _, _ in control_flags.nondefault(cfg))  # Stage 23 DW-17 (S23-DEV-02): the approval rule is enforced by config.load
    if refs:
        cfg[control_flags.APPROVALS_KEY] = refs
    path = os.path.join(base, "hub-config.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, sort_keys=True)
    return path


def admin(args, cfg_path, env=None, input_text=None, timeout=150):
    return subprocess.run([sys.executable, "-B", "-m", "hub.admin", "--config", cfg_path] + list(args), cwd=S.CODE_ROOT,
                          env=S.child_env(env), input=input_text, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, timeout=timeout)


def out_json(proc):
    return json.loads(proc.stdout)


class Store(object):
    """An M001 hub store in a fresh sandbox temp dir, opened in-process with a deterministic clock."""

    def __init__(self, prefix, extra=None, anchor_every=100, fast=False):
        self.base = S.tmpdir(prefix)
        self.data = os.path.join(self.base, "data")
        self.cfg_path = write_config(self.base, extra, anchor_every)
        self.cfg = config.load(self.cfg_path)
        self.s = settings.resolve(self.cfg)
        self.anchor_path = settings.anchor_path(self.s, self.data)
        self.anchor = audit.Anchor(self.anchor_path, anchor_every)
        self.clock = FixedClock()
        self.migration = migrate.migrate(self.data, os.path.join(self.base, "backups"), self.anchor_path, self.clock)
        self.con = self.connect()
        if fast:
            self.con.execute("PRAGMA synchronous = OFF")
        self.authn = auth.LocalAuthenticator(self.con, self.s, self.clock, self.anchor)

    @property
    def db_path(self):
        return os.path.join(self.data, db.HUB_DB_NAME)

    def connect(self):
        con = sqlite3.connect(self.db_path)
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def audit_rows(self):
        cur = self.con.execute("SELECT * FROM audit_log ORDER BY audit_seq")
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur]

    def close(self):
        self.con.close()


_CHAIN = {}


def chain_1000(extra_after_anchor=0):
    """A store with exactly 1,000 audit records anchored every 100 (last anchor at seq 1,000), optionally followed
    by `extra_after_anchor` unanchored records. Built once per process; callers get a private copy
    (db_path, anchor_path)."""
    key = extra_after_anchor
    if key not in _CHAIN:
        st = Store("chain-", anchor_every=100, fast=True)
        start = audit.head(st.con)[0]
        for i in range(start + 1, 1001):
            audit.append(st.con, st.clock, anchor=st.anchor, actor="synthetic-actor-%d" % (i % 7), actor_kind="system",
                         action="SYNTHETIC_EVENT", outcome="success", correlation_id="corr-%04d" % i,
                         object_ref="case:%d" % (i % 125), details={"n": i, "note": "synthetic, unvalidated"})
        anchor_every_big = audit.Anchor(st.anchor_path, 10 ** 9)
        for i in range(extra_after_anchor):
            audit.append(st.con, st.clock, anchor=anchor_every_big, actor="late", actor_kind="system",
                         action="SYNTHETIC_EVENT", outcome="success", correlation_id="late-%d" % i)
        st.close()
        _CHAIN[key] = st
    st = _CHAIN[key]
    dst = S.tmpdir("chaincopy-")
    os.makedirs(os.path.join(dst, "data"))
    os.makedirs(os.path.join(dst, "anchor"))
    dbp, anp = os.path.join(dst, "data", db.HUB_DB_NAME), os.path.join(dst, "anchor", ANCHOR)
    shutil.copy2(st.db_path, dbp)
    shutil.copy2(st.anchor_path, anp)
    return dbp, anp


def offline_attacker(db_path):
    """Open the store as an offline attacker would: the insert-only triggers are dropped first (ABU-05)."""
    con = sqlite3.connect(db_path)
    con.execute("DROP TRIGGER audit_log_no_update")
    con.execute("DROP TRIGGER audit_log_no_delete")
    return con
