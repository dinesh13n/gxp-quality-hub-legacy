"""Shared helpers for the Stage 23 hub tests (HITL/HOTL and deterministic control boundaries; DW-13..DW-18). Synthetic, unvalidated.

Stage 23 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER) and run under the egress guard in
test_tst_hub_stg23_egress_guard.py (E23EGRESS) instead (same split as Stage 20 / 21). Evidence JSON is written under HUB_SANDBOX_ROOT/s23-evidence and
copied into docs/23-human-control/evidence/ by the build agent. Nothing here changes hub behaviour, a binding, a legacy path or the working tree (OD-03a).
No helper in this directory imports a deny-listed module (hub.guards.no_ai rule R2): the wire tests use the raw-socket client of _http8.py (loopback).

  control()     run `python -m hub.control --config CFG ...` in the sandbox copy
  read_cfg() / write_cfg()    the config FILE of an _inc03.Store (operator edit, out of band)
  SYNTHETIC_REF   an approval-reference STRING for tests - a test marker, never a human approval (zone_h.holders stays empty in shipped config)
"""
import json
import os
import subprocess
import sys
import unittest

import _support as S

LABEL = "synthetic, unvalidated"
SYNTHETIC_REF = "SYNTHETIC-TEST-REF-S23 (a test marker, not a human approval)"
EVIDENCE_REL = os.path.join("docs", "23-human-control", "evidence")


def skip_in_inner_egress_run():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("Stage 23 module: covered by test_tst_hub_stg23_egress_guard.py (E23EGRESS)")
    S.require_sandbox()


def write_evidence(name, doc):
    d = os.path.join(S.SANDBOX_ROOT, "s23-evidence")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    return p


def module_cli(module, args, cfg_path, env=None, timeout=150):
    return subprocess.run([sys.executable, "-B", "-m", module, "--config", cfg_path] + list(args), cwd=S.CODE_ROOT, env=S.child_env(env),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)


def control(args, cfg_path, env=None, timeout=150):
    return module_cli("hub.control", args, cfg_path, env, timeout)


def code_of(proc):
    try:
        return json.loads(proc.stderr)["code"]
    except ValueError:
        return None


def read_cfg(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_cfg(path, doc):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, sort_keys=True)


def audit_changes(store):
    """[(audit_seq, details dict)] of the CONFIG_CHANGED records of an _inc03.Store."""
    return [(r["audit_seq"], json.loads(r["details"])) for r in store.audit_rows() if r["action"] == "CONFIG_CHANGED"]


# ------------------------------------------------------------------------------------------------ DW-16 contract objects
import base64  # noqa: E402

import _inc05 as D  # noqa: E402
import _inc06 as I  # noqa: E402
import _inc08 as W  # noqa: E402
import _schema_lite as L  # noqa: E402

BOOL = {"exception", "is_default", "affects_state", "counts_toward_totals", "partial", "read_only", "authoritative", "involves_definition", "defaulted"}
V02_DIR = os.path.join("docs", "23-human-control", "stage12-v0.2", "schemas")
V01_DIR = os.path.join("docs", "12-specs", "contracts", "schemas")
SCHEMA_NAMES = ("audit-record", "crosswalk-link", "decision-event", "error-envelope", "evidence-record", "hub-config", "intake-outcome", "metric-definition",
                "metric-value", "partner-feed-envelope", "partner-feed-payload", "policy-object", "raw-intake", "rule-result", "rule-set", "run-record")
CUTOFF = "2030-01-01T00:00:00.000000Z"


def load_schema(name, v02=True):
    with open(os.path.join(S.CODE_ROOT, V02_DIR if v02 else V01_DIR, name + ".schema.json"), encoding="utf-8") as f:
        return json.load(f)


def _maybe_json(v):
    if isinstance(v, str) and v[:1] in "[{":
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def rows(con, table, transform=None):
    """Every row of a store table as a schema-shaped object (storage forms mapped as the addendum IC-7 says: 0/1 -> boolean, JSON text -> object,
    BLOB -> base64). `table` is always a fixed literal from this module."""
    cur = con.execute("SELECT * FROM %s" % table)
    cols = [d[0] for d in cur.description]
    out = []
    for r in cur:
        o = {}
        for c, v in zip(cols, r):
            v = _maybe_json(v)
            if c in BOOL and v in (0, 1):
                v = bool(v)
            o[c] = v
        out.append(transform(o) if transform else o)
    return out


def _raw_intake(o):
    b = o.pop("raw_bytes", None)
    o["raw_bytes_b64"] = base64.b64encode(b if isinstance(b, bytes) else str(b).encode()).decode()
    return o


def effective_config(cfg):
    """The effective configuration (defaults applied by every settings resolver) - what hub-config.schema.json v0.2 describes."""
    from hub.decision import settings as dsettings
    from hub.gate import modes
    from hub.runs import settings as rsettings
    from hub.search import settings as ssettings
    from hub.security import settings as sec
    s = sec.resolve(cfg)
    d = dsettings.resolve(cfg)
    r = rsettings.resolve(cfg)
    out = {"data_origin": cfg["data_origin"], "hub": dict(cfg["hub"]), "runtime": dict(cfg["runtime"]), "capability_authority": dict(cfg["capability_authority"]),
           "approval_refs": dict(cfg.get("approval_refs") or {}), "zone_h": s["zone_h"], "network": s["network"], "audit": s["audit"], "auth": s["auth"],
           "closure": d["closure"], "workflow": d["workflow"], "facts": d["facts"], "case_creation": d["case_creation"],
           "disposition": modes.resolve(cfg), "schedule": r["schedule"], "runs": r["runs"], "site": r["site"],
           "search": ssettings.resolve(cfg), "templates": {"enabled": ssettings.templates_enabled(cfg)},
           "gateway": {"retries": (cfg.get("gateway") or {}).get("retries", 3)}}
    return out


def scenario(tc):
    """Populate a WStore with every kind of object the hub writes (synthetic, unvalidated) and return {schema name: [objects]}.
    Ingest: valid, replayed, revised-conflict, unmatched, negative, unparsable and unsupported-revision deliveries; the three as-found rule sets are loaded and
    evaluated; evidence is attached; a decision event is appended; a metric value is computed; a run is executed; error envelopes come from real refusals."""
    st = tc.wstore(loaded=True)
    ingest = []
    ingest += I.batch(12)
    ingest += I.batch(4)  # replay of the first 4
    ingest.append(I.feed(5, payload={"quantity": 77.5}))  # same natural key, different payload -> REVISED_CONFLICT
    ingest.append(I.feed(300, ref_id="NO-SUCH-CASE"))
    ingest.append(I.feed(301, payload={"quantity": -2}))
    ingest.append(I.feed(302, payload_text="{not json"))
    ingest.append(I.feed(303, schema_rev="9.9"))
    rep = st.isvc.ingest("partner_feed", ingest, "s23-ingest", "s23-ingest")
    case = I.case_id(3)
    st.evidence(case)
    st.move(case, "UNDER_REVIEW")
    rdir = tempfile_dir("s23rs-")
    st.pol.load_as_found(S.LEGACY_ROOT, rdir, "s23-asfound")
    results = [st.pol.evaluate("PRIORITY", {"status": "OPEN", "severity": "HIGH", "amount": 60000}, "as-found-python@1"),
               st.pol.evaluate("PRIORITY", {"status": "CLOSED", "severity": "LOW", "amount": 10}, "as-found-python@1"),
               st.pol.evaluate("AMOUNT_LIMIT", {"amount": 1000, "region": "APAC", "year": 2026}, "as-found-js@1"),
               st.pol.evaluate("AMOUNT_LIMIT", {"amount": 1000, "region": "APAC", "year": 2019}, "as-found-js@1"),
               st.pol.evaluate("SHIFT_FLAG", {"value": 3000, "threshold": 2500}, "as-found-batch@1")]
    from hub.metrics.sources import CasesAmountSource
    leg = D.legacy_handle("s23leg-")
    try:
        st.met.month_end_total(CUTOFF, "cases:125 (FX-BASE125)", CasesAmountSource(leg))
    finally:
        leg.close()
    run = st.runs.run("verify_audit", st.service_session(), resources={"anchor_path": st.anchor_path}, correlation_id="s23-run")
    from hub.runs.service import RunService
    from hub.web import wire
    errs = []
    for path in ("/api/v2/cases", "/no/such/route"):
        errs.append(st.get(path).json())
    from hub.core.errors import ConfigInvalid, HubError
    errs.append(wire.envelope(ConfigInvalid({"x": 1}), "s23-corr-0001"))
    errs.append(wire.envelope(HubError(), "s23-corr-0002"))
    by, _sha = I.legacy_deliveries()
    rulesets = []
    for rs in rows(st.con, "rule_set"):
        rs["rows"] = [r for r in rows(st.con, "rule_row") if r["ruleset_id"] == rs["ruleset_id"] and r["version"] == rs["version"]]
        for r in rs["rows"]:
            r.pop("ruleset_id", None)
            r.pop("version", None)
        rulesets.append(rs)
    objs = {
        "audit-record": rows(st.con, "audit_log"), "crosswalk-link": rows(st.con, "crosswalk_link"), "decision-event": rows(st.con, "decision_events"),
        "evidence-record": rows(st.con, "evidence_record"), "intake-outcome": rows(st.con, "intake_outcome"),
        "raw-intake": rows(st.con, "raw_intake", _raw_intake), "metric-definition": rows(st.con, "metric_definition"),
        "metric-value": rows(st.con, "metric_value"), "policy-object": rows(st.con, "policy_object"), "rule-set": rulesets, "rule-result": results,
        "run-record": [RunService.to_schema(run)], "error-envelope": errs, "hub-config": [effective_config(st.cfg)],
        "partner-feed-envelope": [d["raw"] for d in by["partner_feed"]],
        "partner-feed-payload": [json.loads(d["raw"]["raw_json"]) for d in by["partner_feed"]],
    }
    return st, objs, {"ingest": rep}


def tempfile_dir(prefix):
    return S.tmpdir(prefix)


def check_objects(name, objs, v02=True):
    """{schema, objects, valid, invalid, top_errors[:6]} for one schema."""
    sch = load_schema(name, v02)
    bad, msgs = 0, {}
    for o in objs:
        es = L.errors(sch, o)
        if es:
            bad += 1
            for e in es:
                key = e.split(": ", 1)[0].rsplit(".", 1)[-1] + ": " + e.split(": ", 1)[-1][:90]
                msgs[key] = msgs.get(key, 0) + 1
    return {"schema": name, "objects": len(objs), "valid": len(objs) - bad, "invalid": bad,
            "top_errors": sorted(msgs.items(), key=lambda kv: -kv[1])[:6]}
