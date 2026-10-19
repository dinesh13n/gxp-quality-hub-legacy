"""Shared helpers for the Stage 15 INC-06 hub tests (safe intake & exception handling; M004). Synthetic, unvalidated.

Everything lives under HUB_SANDBOX_ROOT (S.tmpdir) - never inside the repository working tree (OD-03a). The store is the INC-05 template
(M001..M003, 6 users, the 125 backfilled legacy cases) with M004 applied once per process; each test gets a private byte copy. The Zone H
holders are SYNTHETIC TEST DATA: the shipped config keeps zone_h.holders EMPTY (OD-17/OD-18). Synthetic deliveries are labelled 'synthetic,
unvalidated'; the shipped-data checks read the hash-gated FX-BASE125 sandbox copy (OD-09) through the read-only snapshot adapter.

INC-06 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER, frozen group C keeps its size) and are run under
the egress guard by test_inc06_egress_guard.py instead (inc06-design-notes D-14, same split as INC-05 D-16).
"""
import datetime
import json
import os
import shutil
import unittest

import _support as S
import _inc05 as D
from hub.adapters import intake_sources, legacy_sqlite
from hub.intake import schema as ischema
from hub.intake.service import IntakeService
from hub.security.canonical import fmt

LABEL = "synthetic, unvalidated"
AUTH = "TEST-AUTH-06 (synthetic)"
_TPL6 = {}
_LEG = {}
_FULL = {}


def skip_in_inner_egress_run():
    """Call from setUpModule: INC-06 modules are exercised under the egress guard by test_inc06_egress_guard.py."""
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("INC-06 module: covered by test_inc06_egress_guard.py (design note D-14)")
    S.require_sandbox()


def _template6(loaded):
    if loaded in _TPL6:
        return _TPL6[loaded]
    t5 = D._template(loaded)
    dst = S.tmpdir("p6tpl-")
    shutil.copytree(t5["base"], dst, dirs_exist_ok=True)
    ds = D.DStore(_base=dst, _tpl=t5)
    ds.close()
    res = ischema.apply(ds.data, os.path.join(dst, "backups-m004"), ds.anchor_path, ds.clock)
    assert res["applied"], res
    _TPL6[loaded] = {"base": dst, "tokens": t5["tokens"], "pw": t5["pw"], "clock": fmt(ds.clock._t)}
    return _TPL6[loaded]


class IStore(D.DStore):
    """A private M001..M004 hub store; loaded=True (default) holds the 125 backfilled legacy cases (the matcher's targets)."""
    INTAKE_TABLES = ("raw_intake", "intake_outcome", "intake_item_attr", "intake_run_event")

    def __init__(self, loaded=True, extra=None):
        D.DStore.__init__(self, loaded, extra, _tpl=_template6(loaded))
        self.isvc = IntakeService(self.con, self.s, self.clock, self.anchor)

    def reauth_holder(self, name="holder-1"):
        return self.reauth(name)

    def bind(self, source, mode, who="holder-1"):
        return self.isvc.set_binding(self.reauth(who), source, mode, AUTH, "t-bind")

    def outcomes(self, run_id=None):
        q = "SELECT raw_id, outcome, primary_reason, all_reasons, queue, contract_check, counts_toward_totals, matched_link FROM intake_outcome"
        rows = self.con.execute(q + (" WHERE run_id = ?" if run_id else "") + " ORDER BY raw_id, outcome_seq", (run_id,) if run_id else ()).fetchall()
        return [dict(zip(("raw_id", "outcome", "primary_reason", "all_reasons", "queue", "contract_check", "counts", "matched_link"),
                         r[:2] + (r[2], json.loads(r[3])) + r[4:])) for r in rows]

    def table_digest(self, tables):
        import hashlib
        h = hashlib.sha256()
        for t in tables:
            h.update(t.encode())
            for row in self.con.execute("SELECT * FROM %s ORDER BY 1, 2" % t):
                h.update(repr(row).encode())
        return h.hexdigest()


# ---------------------------------------------------------------------------------------------------- synthetic deliveries
def case_id(i):
    return "C%08d" % ((i % 125) + 1)


def feed(i, payload=None, payload_text=None, **env):
    """A synthetic partner-feed delivery (label 'synthetic, unvalidated'); distinct i -> distinct natural key."""
    p = {"business_key": case_id(i), "object_type": "BATCH", "subtype": "BIOLOGIC", "state": "OPEN", "quantity": round(1 + i * 0.5, 3),
         "unit": "kg", "currency": "USD", "policy_version": "2021-A", "quality_flag": "OK", "notes": "synthetic note %d" % i,
         "source_version": "1.0"}
    if payload:
        p.update(payload)
    for k in [k for k, v in p.items() if v is ... ]:
        del p[k]
    text = payload_text if payload_text is not None else json.dumps(p)
    ts = (datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(minutes=i)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    d = {"source_key": "FEED-%09d" % i, "partner": "north", "schema_rev": "1.0", "source_ts": ts, "ref_id": case_id(i),
         "record_kind": "OOS_RESULT", "payload_text": text}
    d.update(env)
    d["raw"] = {"feed_id": d["source_key"], "partner": d["partner"], "schema_rev": d["schema_rev"], "source_ts": d["source_ts"],
                "ingest_ts": ts, "ref_id": d["ref_id"], "record_kind": d["record_kind"], "raw_json": text}
    return d


def batch(n, start=0):
    return [feed(i) for i in range(start, start + n)]


# ---------------------------------------------------------------------------------------------------- shipped (FX-BASE125) data
def legacy_deliveries():
    """{'partner_feed': [...8,567], 'source_message': [...15], 'gateway': [...1]} + the snapshot sha256, cached per process."""
    if not _LEG:
        h = D.legacy_handle("p6leg-")
        try:
            _LEG["by_source"] = {"partner_feed": intake_sources.partner_feed_deliveries(h),
                                 "source_message": intake_sources.source_message_deliveries(h),
                                 "gateway": intake_sources.gateway_inbox_deliveries(h)}
            _LEG["sha256"] = h.provenance["source_sha256"]
        finally:
            h.close()
    return _LEG["by_source"], _LEG["sha256"]


def full_store(mode):
    """Cached store holding the whole shipped partner feed ingested once (mode 'record_only' default or 'enforce'); READ-ONLY for tests."""
    if mode not in _FULL:
        st = IStore()
        if mode == "enforce":
            st.bind("partner_feed", "enforce")
        by, _ = legacy_deliveries()
        rep = st.isvc.ingest("partner_feed", by["partner_feed"], "full-" + mode, "t-full")
        _FULL[mode] = (st, rep)
    return _FULL[mode]
