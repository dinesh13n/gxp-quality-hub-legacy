"""`python -m hub.runs [--config FILE] <command>` - run orchestration, run records and reports (INC-07, C8). THE SCHEDULER IS OFF: nothing here
starts a run by itself; every run is an operator invocation of `run` (OD-19).

  status            M005 state and the run / metric counts (read-only)
  migrate           backup-before-migrate, then apply M005 (requires M001..M004)
  run JOB           start one run (--trigger manual|scheduled, --batch-size N, --until-empty); needs a session of a principal with role
                    quality_lead / compliance / integration: --principal NAME and the password in $HUB_RUN_PASSWORD (or stdin)
                    sources: --legacy-root/--run-dir (sandbox copy; partner_feed / source_message / gateway snapshot), --csv-tier tiny
  list [--job J]    run records;  show RUN_ID  one record with its events;  reap  close stale runs (writes RUN_ABANDONED)
  schedule          show the schedule flag (read-only); `schedule set --enabled true|false --authority-ref REF` is Zone H ZH-09 and needs a
                    holder session (shipped zone_h.holders is empty: E-GATE-NO-HOLDERS)
  detect-missing    missing-run detector as of now (or --as-of);  timeliness  'finished before 06:00' per scheduled run
  report health|latency|kpi-coverage|queues   read-only reports;  selfcheck  Python / SQLite / FTS5 / config hash / gate status
  obs-snapshot      store the observability samples in obs_metric
Logs are JSON lines on stderr (stdout carries the result, DEV-70); error envelopes carry the correlation id. Same guards as hub.admin:
egress guard, runtime floor, hub.kill, CONFIG_LOADED audit record, anchor at the end. No model call, no network beyond loopback.
"""
import argparse
import os
import sqlite3
import sys

from hub.admin.cli import _Run, _dump
from hub.core.errors import ConfigInvalid, HubError, RuntimeUnsupported
from hub.runs import CODE_VERSION, catalogue


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.runs", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
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
    p = store("run")
    p.add_argument("job")
    p.add_argument("--principal", required=True)
    p.add_argument("--trigger", default="manual", choices=list(catalogue.TRIGGERS))
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--until-empty", action="store_true")
    p.add_argument("--legacy-root", default=None)
    p.add_argument("--run-dir", default=None)
    p.add_argument("--csv-tier", default=None, choices=["tiny"])
    p = store("list")
    p.add_argument("--job", default=None)
    p = store("show")
    p.add_argument("run_id")
    store("reap")
    p = store("schedule")
    p.add_argument("action", nargs="?", default="show", choices=["show", "set"])
    p.add_argument("--enabled", default=None, choices=["true", "false"])
    p.add_argument("--authority-ref", default=None)
    p.add_argument("--principal", default=None)
    p = store("detect-missing")
    p.add_argument("--as-of", default=None)
    p = store("timeliness")
    p.add_argument("--deadline", default="06:00")
    p = store("report")
    p.add_argument("which", choices=["health", "latency", "kpi-coverage", "queues"])
    p.add_argument("--calls", type=int, default=20)
    store("selfcheck")
    store("obs-snapshot")
    return ap


def _session(r, name):
    from hub.security import auth
    pw = os.environ.get("HUB_RUN_PASSWORD")
    if pw is None:
        pw = sys.stdin.readline().rstrip("\n")
    authn = auth.LocalAuthenticator(r.con, r.s, r.clock, r.anchor)
    token = authn.login(name, pw, r.cid)
    return authn.authenticate(token, r.cid), authn, token, pw


def _resources(a, r):
    res = {"anchor_path": r.anchor_path}
    if a.legacy_root:
        from hub.adapters import legacy_sqlite
        from hub.metrics import sources as msources
        from hub.runs import sources
        handle = legacy_sqlite.open_snapshot(os.path.abspath(a.legacy_root), "legacy.sqlite3", os.path.abspath(a.run_dir), pinned=True)
        try:
            res["readers"] = sources.legacy_sources(handle)
            res["site_of"] = msources.case_sites(handle)
            if a.csv_tier:
                res["readers"]["vendor_csv"], _ = sources.vendor_csv_source(__import__("hub.adapters.intake_sources", fromlist=["x"]).csv_path(
                    os.path.abspath(a.legacy_root), a.csv_tier))
        finally:
            handle.close()
    return res


def _cmd(r, a, log):
    from hub.runs import detector, reports, schema
    from hub.runs.schedule import ScheduleService
    from hub.runs.service import RunService
    from hub.security import settings
    data_dir = os.path.abspath(a.data_dir)
    if a.cmd == "migrate":
        res = schema.apply(data_dir, os.path.abspath(a.backup_root), settings.anchor_path(r.s, data_dir), r.clock, r.cid)
        res["backup"] = res["backup"] and {k: res["backup"][k] for k in ("label", "path", "files", "schema_versions")}
        return res, 0
    con = r.open_store()
    if a.cmd == "status":
        st = schema.status(con)
        if st["state"] == "drift":
            schema.require(con)
        if st["state"] == "applied":
            st.update(runs=con.execute("SELECT count(DISTINCT run_id) FROM run_event").fetchone()[0],
                      metric_values=con.execute("SELECT count(*) FROM metric_value").fetchone()[0],
                      metric_definitions=con.execute("SELECT count(*) FROM metric_definition").fetchone()[0])
        return st, 0
    svc = RunService(con, r.s, r.clock, r.anchor, r.cfg)
    if a.cmd == "run":
        sess, _, _, _ = _session(r, a.principal)
        with log.step("OP-RUN-01", r.cid, actor=sess.principal.principal_id, actor_kind=sess.principal.actor_kind, object_ref="job:" + a.job) as info:
            rec = svc.run(a.job, sess, a.trigger, a.batch_size, a.until_empty, _resources(a, r), r.cid)
            info["run_id"] = rec["run_id"]
        return rec, 0
    if a.cmd == "list":
        return {"runs": svc.list_runs(a.job), "schedule": svc.schedule()}, 0
    if a.cmd == "show":
        return svc.get_run(a.run_id, with_events=True), 0
    if a.cmd == "reap":
        return {"abandoned": svc.reap_stale(r.cid)}, 0
    if a.cmd == "schedule":
        sch = ScheduleService(con, r.s, r.clock, r.anchor)
        if a.action == "show":
            return sch.state(), 0
        if a.enabled is None or not a.principal:
            raise ConfigInvalid({"schedule set": "needs --enabled true|false, --authority-ref and --principal"})
        sess, authn, token, pw = _session(r, a.principal)
        sess = authn.reauthenticate(token, pw, r.cid)
        return sch.set_enabled(sess, a.enabled == "true", a.authority_ref, r.cid), 0
    if a.cmd == "detect-missing":
        return detector.missing(con, svc.rs, a.as_of or r.clock()), 0
    if a.cmd == "timeliness":
        return detector.timeliness(svc.list_runs(), svc.rs, a.deadline), 0
    if a.cmd == "selfcheck":
        out = reports.selfcheck(r.cfg, r.s, con)
        log.emit("startup_selfcheck", correlation_id=r.cid, outcome="success", op_id="OP-OBS-SELFCHECK")
        return out, 0
    if a.cmd == "obs-snapshot":
        from hub.obs import collect
        rs = svc.list_runs()
        n = collect.snapshot(con, r.clock, collect.samples(con, rs, detector.missing(con, svc.rs, r.clock())["by_job"] if svc.schedule()["enabled"] else None))
        return {"samples_stored": n}, 0
    if a.cmd == "report":
        if a.which == "health":
            return reports.health(svc, r.clock(), r.anchor_path), 0
        if a.which == "queues":
            from hub.intake.service import IntakeService
            return IntakeService(con, r.s, r.clock, r.anchor).queue_snapshot(r.clock()), 0
        from hub.metrics.service import MetricsService
        m = MetricsService(con, r.s, r.clock, r.anchor, r.cfg)
        if a.which == "kpi-coverage":
            m.registry.seed_builtin()
            return {"kpis": m.kpi_coverage()}, 0
        from hub.intake.service import IntakeService
        isvc = IntakeService(con, r.s, r.clock, r.anchor)
        ops = {"intake.queue_snapshot": lambda: isvc.queue_snapshot(r.clock()), "metrics.time_to_close": lambda: m.time_to_close(store=False),
               "metrics.backlog_d_ops": lambda: m.backlog_by_site("D-OPS", r.clock(), store=False),
               "runs.list_runs": svc.list_runs, "policy.status_report": m.policy.status_report}
        return reports.latency(ops, a.calls, r.clock), 0
    raise SystemExit(2)


def main(argv=None):
    from hub.guards import egress
    from hub.obs import log as hublog, metrics
    egress.install()
    metrics.reset()
    ap = _parser()
    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_help()
        return 2
    r, rc, cid = None, 0, args.correlation_id
    log = None
    try:
        r = _Run(args)
        cid = r.cid
        log = hublog.Logger(r.clock, lambda line: sys.stderr.write(line + "\n"), CODE_VERSION)
        out, rc = _cmd(r, args, log)
        r.close()
        print(_dump(out))
    except RuntimeUnsupported as e:
        sys.stderr.write(_dump(hublog.envelope_with_correlation(e, cid)) + "\n")
        return e.exit_code
    except HubError as e:
        if r is not None:
            try:
                r.close()
            except (HubError, sqlite3.Error):
                pass
        sys.stderr.write(_dump(hublog.envelope_with_correlation(e, cid)) + "\n")
        rc = e.exit_code
    try:
        metrics.check_tripwires()
    except HubError as e:
        sys.stderr.write(_dump(e.envelope()) + "\n")
        rc = rc or e.exit_code
    return rc
