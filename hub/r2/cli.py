"""`python -m hub.r2 [--config FILE] <command>` - R2 reports and the R2 loopback server (INC-09). Host-operator commands.

  consistency-check --data-dir D --legacy-root L [--run-id ID]   run the adopted CONSISTENCY rules (none ship adopted -> zero findings + statement)
  divergence --data-dir D --legacy-root L                        amount_over_limit divergence of the loaded rule sets over the shipped cases
  delays --data-dir D --source S                                 intake delay / missing / revised report of one source
  freshness --data-dir D [--as-of TS]                            age of the newest accepted item per source
  serve --data-dir D [--port N] [--legacy-root L]                the loopback HTTP surface with the R2 handlers (R2WebApp); self-check first
Results on stdout, JSON log lines on stderr. Same guards as hub.admin. No model call, no network beyond loopback.
"""
import argparse
import json
import sys

from hub.admin.cli import _Run, _dump
from hub.core.errors import HubError, RuntimeUnsupported


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.r2", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--correlation-id", default=None)
    sub = ap.add_subparsers(dest="cmd")
    for name in ("consistency-check", "divergence", "delays", "freshness", "serve"):
        p = sub.add_parser(name)
        p.add_argument("--data-dir", required=True)
        if name in ("consistency-check", "divergence"):
            p.add_argument("--legacy-root", required=True)
        if name == "serve":
            p.add_argument("--legacy-root", default=None)
            p.add_argument("--port", type=int, default=8081)
        if name == "consistency-check":
            p.add_argument("--run-id", default=None)
        if name == "delays":
            p.add_argument("--source", required=True)
        if name == "freshness":
            p.add_argument("--as-of", default=None)
    return ap


def _run_dir(r):
    import os
    import tempfile
    from hub.guards import sandbox
    base = os.path.join(os.path.abspath(r.args.data_dir), "r2-runs")
    sandbox.assert_safe_path(base, "run directory")
    os.makedirs(base, exist_ok=True)
    return tempfile.mkdtemp(prefix="r2-", dir=base)


def _cmd(r, a):
    import os
    from hub.r2 import consistency, divergence, facts as rfacts, intake_reports
    data_dir = os.path.abspath(a.data_dir)
    if a.cmd == "serve":
        from hub.r2.web import R2WebApp
        from hub.web import server
        fx, cases = (None, None)
        if a.legacy_root:
            fx, cases = rfacts.load(os.path.abspath(a.legacy_root), _run_dir(r))
        app = R2WebApp(data_dir, r.cfg, r.clock, case_inputs=cases, facts=fx, log_sink=lambda line: sys.stderr.write(line + "\n"))
        srv = server.make_server(app, a.port)
        sys.stderr.write(json.dumps({"event": "listening", "address": "%s:%d" % srv.server_address[:2], "label": "synthetic, unvalidated"}) + "\n")
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            srv.server_close()
            app.flush_metrics()
        return {"stopped": True}, 0
    con = r.open_store()
    if a.cmd == "consistency-check":
        fx, _ = rfacts.load(os.path.abspath(a.legacy_root), _run_dir(r))
        return consistency.run(con, r.clock, r.anchor, r.operator, fx, a.run_id or ("CONS-" + r.cid[-12:]), r.cid), 0
    if a.cmd == "divergence":
        from hub.policy.service import PolicyService
        from hub.security import audit
        _, cases = rfacts.load(os.path.abspath(a.legacy_root), _run_dir(r))
        rep = divergence.report(PolicyService(con, r.s, r.clock, r.anchor), cases)
        audit.append(con, r.clock, anchor=r.anchor, actor=r.operator, actor_kind="human", action="RULE_DIVERGENCE_REPORTED", outcome="success",
                     correlation_id=r.cid, object_ref="OP-POL-07",
                     details={"compared_sets": rep["compared_sets"], "inputs": rep["inputs"], "divergent": rep["count"], "null_outputs": rep["null_outputs"]})
        return rep, 0
    st = intake_reports.settings(r.cfg)
    if a.cmd == "delays":
        return intake_reports.delay_report(con, a.source, st["delay_threshold_hours"]), 0
    if a.cmd == "freshness":
        return intake_reports.freshness_report(con, a.as_of or r.clock(), st["freshness_hours"]), 0
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
    try:
        r = _Run(args)
        cid = r.cid
        out, rc = _cmd(r, args)
        r.close()
        print(_dump(out))
    except RuntimeUnsupported as e:
        sys.stderr.write(_dump(hublog.envelope_with_correlation(e, cid)) + "\n")
        return e.exit_code
    except HubError as e:
        if r is not None:
            try:
                r.close()
            except Exception:  # noqa: BLE001
                pass
        sys.stderr.write(_dump(hublog.envelope_with_correlation(e, cid)) + "\n")
        rc = e.exit_code
    try:
        metrics.check_tripwires()
    except HubError as e:
        sys.stderr.write(_dump(e.envelope()) + "\n")
        rc = rc or e.exit_code
    return rc
