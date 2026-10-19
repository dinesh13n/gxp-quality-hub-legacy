"""Shared helpers for the Stage 15 INC-07 hub tests (runs, metrics, observability; M005). Synthetic, unvalidated.

Everything lives under HUB_SANDBOX_ROOT (S.tmpdir) - never inside the repository working tree (OD-03a). The store is the INC-06 template (M001..M004,
6 users, the 125 backfilled legacy cases, the 5 seeded candidate policies) with M005 applied once per process; each test gets a private byte copy.
The Zone H holders are SYNTHETIC TEST DATA: the shipped config keeps zone_h.holders EMPTY (OD-17..OD-19). Synthetic deliveries are labelled
'synthetic, unvalidated'; the shipped-data checks read the hash-gated FX-BASE125 sandbox copy (OD-09) through the read-only snapshot adapter.

INC-07 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER, frozen group C keeps its size) and are run under the egress
guard by test_inc07_egress_guard.py instead (inc07-design-notes D-14, same split as INC-05 / INC-06).
"""
import json
import os
import shutil
import sqlite3
import unittest

import _support as S
import _inc05 as D
import _inc06 as I
from hub.intake.service import IntakeService
from hub.metrics.service import MetricsService
from hub.runs import schema as rschema
from hub.runs import sources as rsources
from hub.runs.schedule import ScheduleService
from hub.runs.service import RunService
from hub.security.canonical import fmt, parse

LABEL = "synthetic, unvalidated"
AUTH = "TEST-AUTH-07 (synthetic)"
_TPL7 = {}


class SimulatedKill(BaseException):
    """A process that dies without cleanup (not an Exception, so the runner records nothing - like SIGKILL)."""


def skip_in_inner_egress_run():
    """Call from setUpModule: INC-07 modules are exercised under the egress guard by test_inc07_egress_guard.py."""
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("INC-07 module: covered by test_inc07_egress_guard.py (design note D-14)")
    S.require_sandbox()


def _template7(loaded):
    if loaded in _TPL7:
        return _TPL7[loaded]
    t6 = I._template6(loaded)
    dst = S.tmpdir("p7tpl-")
    shutil.copytree(t6["base"], dst, dirs_exist_ok=True)
    ds = D.DStore(_base=dst, _tpl=t6)
    ds.pol.seed()  # 3 DEFINITION + 2 CLOCK candidates (INC-04 seed); none adopted
    ds.close()
    res = rschema.apply(ds.data, os.path.join(dst, "backups-m005"), ds.anchor_path, ds.clock)
    assert res["applied"], res
    _TPL7[loaded] = {"base": dst, "tokens": t6["tokens"], "pw": t6["pw"], "clock": fmt(ds.clock._t)}
    return _TPL7[loaded]


class RStore(D.DStore):
    """A private M001..M005 hub store; loaded=True (default) holds the 125 backfilled legacy cases."""

    def __init__(self, loaded=True, extra=None, hooks=None):
        D.DStore.__init__(self, loaded, extra, _tpl=_template7(loaded))
        self.isvc = IntakeService(self.con, self.s, self.clock, self.anchor)
        self.runs = RunService(self.con, self.s, self.clock, self.anchor, self.cfg, hooks)
        self.met = MetricsService(self.con, self.s, self.clock, self.anchor, self.cfg)
        self.sched = ScheduleService(self.con, self.s, self.clock, self.anchor)

    def enable_schedule(self, who="holder-1"):
        tok = self.authn.login(who, self.pw, "t-sched-login")  # fresh session: the test clock may have moved since the template tokens were issued
        return self.sched.set_enabled(self.authn.reauthenticate(tok, self.pw, "t-sched-reauth"), True, AUTH, "t-sched")

    def fresh(self, name):
        """A new session at the CURRENT test-clock time (the template tokens idle out when a test moves the clock)."""
        tok = self.authn.login(name, self.pw, "t-fresh-login")
        return self.authn.authenticate(tok, "t-fresh")

    def run_service(self, hooks=None, con=None):
        return RunService(con or self.con, self.s, self.clock, self.anchor, self.cfg, hooks)

    def raw_digest(self):
        return self.con.execute("SELECT count(*), count(DISTINCT identity_key) FROM raw_intake").fetchone()

    def outcome_rows(self):
        """Outcome rows without run_id / decided_at (which differ between a resumed and an uninterrupted run)."""
        return self.con.execute("SELECT raw_id, outcome_seq, outcome, primary_reason, all_reasons, queue, contract_check, counts_toward_totals,"
                                " matched_link FROM intake_outcome ORDER BY raw_id, outcome_seq").fetchall()

    def run_events(self, run_id=None):
        q = "SELECT run_id, run_seq, event_type, job, trigger, triggered_by, occurred_at, body FROM run_event"
        rows = self.con.execute(q + (" WHERE run_id = ?" if run_id else "") + " ORDER BY run_id, run_seq", (run_id,) if run_id else ()).fetchall()
        return [dict(zip(("run_id", "run_seq", "event_type", "job", "trigger", "triggered_by", "occurred_at", "body"), r[:7] + (json.loads(r[7]),)))
                for r in rows]

    def digest(self):
        """Row counts of the data tables a run must not touch when it is refused."""
        return dict((t, self.con.execute("SELECT count(*) FROM %s" % t).fetchone()[0])
                    for t in ("raw_intake", "intake_outcome", "case_state", "decision_events", "crosswalk_link", "metric_value"))


def source(n, start=0, name="partner_feed"):
    """An OrderedSource of n distinct synthetic partner-feed deliveries (label 'synthetic, unvalidated')."""
    return rsources.OrderedSource(name, I.batch(n, start))


def readers(n, start=0):
    return {"readers": {"partner_feed": source(n, start)}}


def cases_db(rows, events):
    """An in-memory legacy-shaped fixture: cases(id, amount, created_at, site) + events(case_id)."""
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE cases(id TEXT PRIMARY KEY, amount REAL NOT NULL, created_at TEXT NOT NULL, site TEXT NOT NULL)")
    con.execute("CREATE TABLE events(id INTEGER PRIMARY KEY, case_id TEXT NOT NULL)")
    con.executemany("INSERT INTO cases VALUES (?,?,?,?)", rows)
    con.executemany("INSERT INTO events(case_id) VALUES (?)", [(e,) for e in events])
    return con


class RO(object):
    """Adapter giving a sqlite3 connection the `.execute(sql, params) -> list` shape of the read-only legacy handle."""

    def __init__(self, con):
        self.con = con

    def execute(self, sql, params=()):
        return self.con.execute(sql, params).fetchall()


def schema_problems(rec, schema_path):
    """Minimal check of a run record against run-record.schema.json: required keys, enums, basic types, timestamp pattern, no extra keys."""
    import re
    with open(schema_path, encoding="utf-8") as f:
        sch = json.load(f)
    bad = []
    for k in sch["required"]:
        if k not in rec:
            bad.append("missing " + k)
    for k, v in rec.items():
        p = sch["properties"].get(k)
        if p is None:
            bad.append("extra " + k)
            continue
        if "enum" in p and v not in p["enum"]:
            bad.append("enum " + k)
        t = p.get("type")
        if t in ("string", "integer", "boolean", "object") or isinstance(t, list):
            names = t if isinstance(t, list) else [t]
            ok = any({"string": isinstance(v, str), "integer": isinstance(v, int) and not isinstance(v, bool), "boolean": isinstance(v, bool),
                      "object": isinstance(v, dict), "null": v is None}[n] for n in names)
            if not ok:
                bad.append("type " + k)
        if p.get("type") == "integer" and isinstance(v, int) and v < p.get("minimum", v):
            bad.append("minimum " + k)
        if k in ("started_at", "ended_at") and isinstance(v, str) and not re.match(p.get("pattern", p.get("anyOf", [{}])[0].get("pattern", ".*")), v):
            bad.append("pattern " + k)
    return bad
