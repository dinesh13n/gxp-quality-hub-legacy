"""Shared helpers for the Stage 15 INC-04 hub tests (policy & rule service, M002).

Everything lives under HUB_SANDBOX_ROOT (S.tmpdir) - never inside the repository working tree (OD-03a). Users and
sessions are created ONCE per process in a template store (PBKDF2 at the INC-03 floor is slow) and each test gets a
private byte copy of the template, reopened with a deterministic clock that continues where the template stopped.
Passwords are generated at run time (no credential literals, AC-SEC-18). Holders are explicit synthetic test data.
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys

import _support as S
import _inc03 as H
from hub import config
from hub.adapters import legacy_captures
from hub.policy import schema
from hub.policy.service import PolicyService
from hub.security import audit, auth, settings
from hub.security.canonical import FixedClock, fmt
from hub.store import db

HOLDERS = ["holder-1", "holder-2"]
USERS = {"holder-1": ["dispositioner"], "holder-2": ["dispositioner"], "nonholder": ["dispositioner"],
         "ql": ["quality_lead"], "comp": ["compliance"], "rev": ["reviewer"]}
TABLES = ("policy_object", "policy_events", "rule_set", "rule_row", "active_ruleset", "audit_log")
_TPL = {}


def _template(loaded):
    if loaded in _TPL:
        return _TPL[loaded]
    if not loaded:
        st = H.Store("p4tpl-", extra={"zone_h": {"holders": HOLDERS}})
        schema.apply(st.data, os.path.join(st.base, "backups-m002"), st.anchor_path, st.clock)
        svc = PolicyService(st.con, st.s, st.clock, st.anchor)
        svc.seed()
        pw = H.password()
        tokens = {}
        for name, roles in sorted(USERS.items()):
            st.authn.create_user(name, pw, roles, "op")
            tokens[name] = st.authn.login(name, pw, "tpl")
        st.close()
        _TPL[False] = {"base": st.base, "tokens": tokens, "clock": fmt(st.clock._t)}
    else:
        base = _template(False)
        dst = S.tmpdir("p4tplL-")
        shutil.copytree(base["base"], dst, dirs_exist_ok=True)
        ps = PStore(loaded=False, _base=dst, _tpl=base)
        ps.svc.load_as_found(S.LEGACY_ROOT, S.tmpdir("p4run-"))
        ps.close()
        _TPL[True] = {"base": dst, "tokens": base["tokens"], "clock": fmt(ps.clock._t)}
    return _TPL[loaded]


class PStore(object):
    """A private M001+M002 hub store with 5 seeded candidate policies, 6 users and (loaded=True) the 3 as-found sets (inactive)."""

    def __init__(self, loaded=False, extra=None, _base=None, _tpl=None):
        tpl = _tpl or _template(loaded)
        if _base is None:
            self.base = S.tmpdir("p4-")
            shutil.copytree(tpl["base"], self.base, dirs_exist_ok=True)
        else:
            self.base = _base
        self.data = os.path.join(self.base, "data")
        ex = {"zone_h": {"holders": HOLDERS}}
        ex.update(extra or {})
        self.cfg_path = H.write_config(self.base, ex)
        self.cfg = config.load(self.cfg_path)
        self.s = settings.resolve(self.cfg)
        self.anchor_path = settings.anchor_path(self.s, self.data)
        self.anchor = audit.Anchor(self.anchor_path, 100)
        self.clock = FixedClock(start=tpl["clock"])
        self.tokens = tpl["tokens"]
        self.con = sqlite3.connect(os.path.join(self.data, db.HUB_DB_NAME))
        self.con.execute("PRAGMA foreign_keys = ON")
        self.authn = auth.LocalAuthenticator(self.con, self.s, self.clock, self.anchor)
        self.svc = PolicyService(self.con, self.s, self.clock, self.anchor)

    def sess(self, name):
        return self.authn.authenticate(self.tokens[name], "t-" + name)

    def service_session(self):
        now = self.clock()
        return auth.Session(auth.Principal("svc-integration", "service", ["integration"], "active"), "0" * 64, now, now, now)

    def counts(self):
        return {t: self.con.execute("SELECT count(*) FROM %s" % t).fetchone()[0] for t in TABLES}

    def audit_actions(self, action=None):
        q = "SELECT audit_seq, actor, actor_kind, action, outcome, object_ref, reason, details FROM audit_log"
        rows = self.con.execute(q + (" WHERE action = ?" if action else "") + " ORDER BY audit_seq", (action,) if action else ()).fetchall()
        keys = ("audit_seq", "actor", "actor_kind", "action", "outcome", "object_ref", "reason", "details")
        out = []
        for r in rows:
            d = dict(zip(keys, r))
            d["details"] = json.loads(d["details"])
            out.append(d)
        return out

    def verify(self):
        return audit.verify(self.con, self.anchor_path)

    def close(self):
        audit.write_anchor(self.con, self.anchor_path)
        self.con.close()


def golden(path):
    cs = legacy_captures.CaptureSet.from_golden_dir()  # integrity-checked against MANIFEST.sha256
    return cs.extract("batch", path)


def _run(cmd, stdin_text):
    p = subprocess.run(cmd, cwd=S.LEGACY_ROOT, env=S.child_env({"PYTHONHASHSEED": "0"}), input=stdin_text,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=150)
    if p.returncode != 0:
        raise RuntimeError("legacy child failed: %s" % p.stderr[-800:])
    return json.loads(p.stdout)


_PY = ("import importlib.util, json, sys\n"
       "spec = importlib.util.spec_from_file_location('legacy_logic', 'app/legacy_logic.py')\n"
       "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
       "rows = json.load(sys.stdin)\n"
       "print(json.dumps([[m.priority(r[0], r[1], r[2]), m.manual_review_required(r[0], r[1])] for r in rows]))\n")
_JS = ("const p = require('./legacy_js/legacy_policy.js');\n"
       "const rows = JSON.parse(require('fs').readFileSync(0, 'utf8'));\n"
       "console.log(JSON.stringify(rows.map(r => [p.threshold(r[1], r[2]), p.legacyAllows(r[0], r[1], r[2])])));\n")


def legacy_python(rows):
    """Run the as-found app/legacy_logic.py (in the SANDBOX legacy copy) over [status, severity, amount] rows."""
    return _run([sys.executable, "-B", "-c", _PY], json.dumps(rows))


def legacy_node(rows):
    """Run the as-found legacy_js/legacy_policy.js (sandbox copy, cwd = copy root) over [amount, region, year] rows."""
    return _run(["node", "-e", _JS], json.dumps(rows))
