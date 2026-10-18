"""`python -m hub.decision [--config FILE] <command>` - host-operator commands for the INC-05 decision record, crosswalk and backfill.

  status             M003 state, event / case / link counts (read-only)
  migrate            backup-before-migrate, then apply M003 (requires M001 and M002)
  backfill           import the shipped legacy cases from --legacy-root (a SANDBOX copy) as CASE_IMPORTED + FACT_RECEIVED events;
                     --priority-check also reports the CT-02 priority distribution through the as-found Python rule set (inactive)
  verify-projection  recompute every case from its events and compare with case_state (exit 27 if a mismatch)
  verify-chain       recompute every per-case hash chain (exit 25 E-DEC-CHAIN-BROKEN if broken)
  crosswalk-run      run the registered rule matchers LT-01..LT-05 over the legacy snapshot (exact keys only) and print orphan counts
  reopen-invariant   REOPENED cases lacking a REOPEN event: violations and the marked legacy cases

Decisions, human links and evidence need an authenticated human session and are service calls (hub.decision.service,
hub.crosswalk.service); this CLI records no decision. Same guards as hub.admin: egress guard, runtime floor, hub.kill,
CONFIG_LOADED audit record, anchor at the end.
"""
import argparse
import os
import sqlite3
import sys

from hub.admin.cli import _Run, _dump
from hub.core.errors import HubError, RuntimeUnsupported


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.decision", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--correlation-id", default=None)
    sub = ap.add_subparsers(dest="cmd")

    def store(name):
        p = sub.add_parser(name)
        p.add_argument("--data-dir", required=True)
        return p

    store("status")
    p = store("migrate")
    p.add_argument("--backup-root", required=True)
    p = store("backfill")
    p.add_argument("--legacy-root", required=True)
    p.add_argument("--run-dir", required=True)
    p.add_argument("--priority-check", action="store_true")
    store("verify-projection")
    store("verify-chain")
    p = store("crosswalk-run")
    p.add_argument("--legacy-root", required=True)
    p.add_argument("--run-dir", required=True)
    store("reopen-invariant")
    return ap


def _services(r):
    from hub.decision import settings as dsettings
    from hub.decision.service import DecisionService
    return DecisionService(r.con, r.s, r.clock, r.anchor, dsettings.resolve(r.cfg))


def _cmd(r, a):
    from hub.decision import schema
    from hub.security import settings
    data_dir = os.path.abspath(a.data_dir)
    if a.cmd == "migrate":
        anchor_path = settings.anchor_path(r.s, data_dir)
        res = schema.apply(data_dir, os.path.abspath(a.backup_root), anchor_path, r.clock, r.cid)
        res["backup"] = res["backup"] and {k: res["backup"][k] for k in ("label", "path", "files", "schema_versions")}
        return res, 0
    con = r.open_store()
    if a.cmd == "status":
        st = schema.status(con)
        if st["state"] == "drift":
            schema.require(con)  # raises E-STORE-MIGRATION-DRIFT (exit 15)
        if st["state"] == "applied":
            st.update(events=con.execute("SELECT count(*) FROM decision_events").fetchone()[0],
                      cases=con.execute("SELECT count(*) FROM case_state").fetchone()[0],
                      links=con.execute("SELECT count(*) FROM crosswalk_link").fetchone()[0])
        return st, 0
    svc = _services(r)
    if a.cmd == "backfill":
        from hub.decision import backfill
        from hub.gate.policy_binding import GatedPolicyService
        pol = None
        if a.priority_check:
            pol = GatedPolicyService(con, r.s, r.clock, r.anchor)
            if backfill.PRIORITY_RULESET not in [x["ruleset_ref"] for x in pol.list_rulesets()]:
                pol.load_as_found(os.path.abspath(a.legacy_root), os.path.abspath(a.run_dir), r.cid)
        return backfill.run(svc, os.path.abspath(a.legacy_root), os.path.abspath(a.run_dir), r.cid, policy_service=pol), 0
    if a.cmd == "verify-projection":
        res = svc.verify_projection()
        return res, (0 if res["mismatches"] == 0 else 27)
    if a.cmd == "verify-chain":
        return svc.require_chain(), 0
    if a.cmd == "reopen-invariant":
        res = svc.reopen_invariant_internal()
        return res, (0 if res["violation_count"] == 0 else 27)
    if a.cmd == "crosswalk-run":
        from hub.adapters import legacy_sqlite
        from hub.crosswalk import sources
        from hub.crosswalk.service import CrosswalkService, identity_targets
        cw = CrosswalkService(con, r.s, r.clock, r.anchor)
        handle = legacy_sqlite.open_snapshot(os.path.abspath(a.legacy_root), "legacy.sqlite3", os.path.abspath(a.run_dir), pinned=True)
        try:
            inputs, cases = sources.legacy_inputs(handle)
        finally:
            handle.close()
        runs = {}
        for code in sorted(inputs):
            items, targets = inputs[code]
            runs[code] = cw.run_rule(code, items, targets, "run-" + r.cid, r.cid)
        docs, dsha = sources.document_items(os.path.abspath(a.legacy_root))
        if docs is not None:
            runs["LT-05"] = cw.run_rule("LT-05", docs, identity_targets(cases), "run-" + r.cid, r.cid)
        return {"runs": runs, "documents_sha256": dsha, "active_links": cw.count_active(), "orphans": cw.orphan_report()}, 0
    raise SystemExit(2)


def main(argv=None):
    from hub.guards import egress
    from hub.obs import metrics
    egress.install()
    metrics.reset()
    ap = _parser()
    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_help()
        return 2
    r, rc = None, 0
    try:
        r = _Run(args)
        out, rc = _cmd(r, args)
        r.close()
        print(_dump(out))
    except RuntimeUnsupported as e:
        sys.stderr.write(_dump(e.envelope()) + "\n")
        return e.exit_code
    except HubError as e:
        if r is not None:
            try:
                r.close()
            except (HubError, sqlite3.Error):
                pass
        sys.stderr.write(_dump(e.envelope()) + "\n")
        rc = e.exit_code
    try:
        metrics.check_tripwires()
    except HubError as e:
        sys.stderr.write(_dump(e.envelope()) + "\n")
        rc = rc or e.exit_code
    return rc
