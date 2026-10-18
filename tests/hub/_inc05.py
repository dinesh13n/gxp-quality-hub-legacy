"""Shared helpers for the Stage 15 INC-05 hub tests (decision record, crosswalk, shared gate, backfill; M003).

Everything lives under HUB_SANDBOX_ROOT (S.tmpdir) - never inside the repository working tree (OD-03a). Users and sessions
are created ONCE per process in a template store (PBKDF2 at the INC-03 floor is slow); each test gets a private byte copy of
the template, reopened with a deterministic clock that continues where the template stopped. Passwords are generated at run
time (no credential literals, AC-SEC-18). The Zone H holders below are SYNTHETIC TEST DATA: the shipped config keeps
zone_h.holders EMPTY (OD-17). Case creation through the service is enabled only in these test configs (OD-S12-19 default off).

INC-05 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER, group C stays at its size) and are
run under the egress guard by test_inc05_egress_guard.py instead (inc05-design-notes D-16).
"""
import json
import os
import shutil
import sqlite3
import unittest

import _support as S
import _inc03 as H
from hub import config
from hub.crosswalk.service import CrosswalkService
from hub.decision import backfill, schema as dschema, settings as dsettings
from hub.decision.service import DecisionService
from hub.gate.policy_binding import GatedPolicyService
from hub.policy import schema as pschema
from hub.security import audit, auth, settings
from hub.security.canonical import FixedClock, fmt, parse
from hub.store import db

HOLDERS = ["holder-1", "holder-2"]  # synthetic test holders - NOT shipped configuration
USERS = {"holder-1": ["dispositioner"], "holder-2": ["dispositioner"], "nonholder": ["dispositioner"],
         "ql": ["quality_lead"], "comp": ["compliance"], "rev": ["reviewer"]}
TABLES = ("decision_events", "evidence_record", "case_state", "crosswalk_link", "crosswalk_link_event", "decision_idempotency",
          "audit_log")
_TPL = {}


def skip_in_inner_egress_run():
    """Call from setUpModule: INC-05 modules are exercised under the egress guard by test_inc05_egress_guard.py."""
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("INC-05 module: covered by test_inc05_egress_guard.py (design note D-16)")
    S.require_sandbox()


def _template(loaded):
    if loaded in _TPL:
        return _TPL[loaded]
    if not loaded:
        st = H.Store("p5tpl-", extra={"zone_h": {"holders": HOLDERS}})
        pschema.apply(st.data, os.path.join(st.base, "backups-m002"), st.anchor_path, st.clock)
        dschema.apply(st.data, os.path.join(st.base, "backups-m003"), st.anchor_path, st.clock)
        pw = H.password()
        tokens = {}
        for name, roles in sorted(USERS.items()):
            st.authn.create_user(name, pw, roles, "op")
            tokens[name] = st.authn.login(name, pw, "tpl")
        st.close()
        _TPL[False] = {"base": st.base, "tokens": tokens, "pw": pw, "clock": fmt(st.clock._t)}
    else:
        base = _template(False)
        dst = S.tmpdir("p5tplL-")
        shutil.copytree(base["base"], dst, dirs_exist_ok=True)
        ds = DStore(_base=dst, _tpl=base)
        res = backfill.run(ds.svc, S.LEGACY_ROOT, S.tmpdir("p5run-"), "tpl-backfill")
        assert res["imported_now"] == 125, res
        ds.close()
        _TPL[True] = {"base": dst, "tokens": base["tokens"], "pw": base["pw"], "clock": fmt(ds.clock._t)}
    return _TPL[loaded]


class DStore(object):
    """A private M001+M002+M003 hub store with 6 users (3 role classes + 2 synthetic holders + 1 non-holder dispositioner);
    loaded=True additionally holds the 125 backfilled legacy cases."""

    def __init__(self, loaded=False, extra=None, _base=None, _tpl=None):
        tpl = _tpl or _template(loaded)
        if _base is None:
            self.base = S.tmpdir("p5-")
            shutil.copytree(tpl["base"], self.base, dirs_exist_ok=True)
        else:
            self.base = _base
        self.data = os.path.join(self.base, "data")
        ex = {"zone_h": {"holders": HOLDERS}, "case_creation": {"enabled": True}}
        for k, v in (extra or {}).items():
            ex.setdefault(k, {}).update(v) if isinstance(v, dict) else ex.__setitem__(k, v)
        self.cfg_path = H.write_config(self.base, ex)
        self.cfg = config.load(self.cfg_path)
        self.s = settings.resolve(self.cfg)
        self.d = dsettings.resolve(self.cfg)
        self.anchor_path = settings.anchor_path(self.s, self.data)
        self.anchor = audit.Anchor(self.anchor_path, 100)
        self.clock = FixedClock(start=tpl["clock"])
        self.tokens, self.pw = tpl["tokens"], tpl["pw"]
        self.con = sqlite3.connect(os.path.join(self.data, db.HUB_DB_NAME))
        self.con.execute("PRAGMA foreign_keys = ON")
        self.authn = auth.LocalAuthenticator(self.con, self.s, self.clock, self.anchor)
        self.svc = DecisionService(self.con, self.s, self.clock, self.anchor, self.d)
        self.cw = CrosswalkService(self.con, self.s, self.clock, self.anchor)
        self.pol = GatedPolicyService(self.con, self.s, self.clock, self.anchor)

    # ---- sessions
    def sess(self, name):
        return self.authn.authenticate(self.tokens[name], "t-" + name)

    def reauth(self, name):
        return self.authn.reauthenticate(self.tokens[name], self.pw, "t-reauth-" + name)

    def service_session(self):
        now = self.clock()
        return auth.Session(auth.Principal("svc-integration", "service", ["integration"], "active"), "0" * 64, now, now, now)

    # ---- time
    def now(self):
        return self.clock()

    def ago(self, hours=0.0, minutes=0.0):
        import datetime
        return fmt(parse(self.clock()) - datetime.timedelta(hours=hours, minutes=minutes))

    # ---- fixtures
    def mk(self, case_id, state="OPEN", occurred_at=None, received_at=None, who="rev"):
        return self.svc.create_case(self.sess(who), case_id, state, "synthetic case", occurred_at, received_at, "t-mk")

    def evidence(self, case_id, level="quality", who="rev", ref="synthetic evidence"):
        ev = self.svc.attach_evidence(self.sess(who), case_id, "document", "synthetic-source", ref, access_level=level,
                                      correlation_id="t-ev")
        return ev["evidence"]["ev_id"]

    def move(self, case_id, to_state, who="rev", **kw):
        return self.svc.transition(self.sess(who), case_id, to_state, kw.pop("basis", "synthetic"), correlation_id="t-mv", **kw)

    def close_with_evidence(self, case_id, who="rev"):
        ev = self.evidence(case_id, who=who)
        return self.move(case_id, "CLOSED", who=who, evidence_refs=[ev])

    def closure_policy(self, states=("CLOSED",), pid="CL-1"):
        """Adopt a CLOSURE policy through the shared gate (ZH-05): create_candidate by quality_lead, adopt by a synthetic holder."""
        ql = self.sess("ql")
        self.pol.create_candidate(ql, pid, "CLOSURE", "closing states", {"closing_states": list(states)}, "TEST-AUTH (synthetic)")
        return self.pol.adopt(self.sess("holder-1"), pid, 1, self.clock()[:10], "qa-owner-synthetic", "TEST-AUTH (synthetic)")

    # ---- inspection
    def counts(self):
        return dict((t, self.con.execute("SELECT count(*) FROM %s" % t).fetchone()[0]) for t in TABLES)

    def event_rows(self, case_id=None):
        q = "SELECT * FROM decision_events" + (" WHERE case_id = ?" if case_id else "") + " ORDER BY case_id, seq"
        return self.con.execute(q, (case_id,) if case_id else ()).fetchall()

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

    def close(self):
        audit.write_anchor(self.con, self.anchor_path)
        self.con.close()


def legacy_handle(run_prefix="p5leg-"):
    from hub.adapters import legacy_sqlite
    return legacy_sqlite.open_snapshot(S.LEGACY_ROOT, "legacy.sqlite3", S.tmpdir(run_prefix), pinned=True)
