"""`python -m hub.web [--config FILE] <command>` - the loopback HTTP surface and its operator commands (INC-08).

  status                       M006 state (read-only)
  migrate                      backup-before-migrate, then apply M006 (requires M001..M005)
  serve [--port N]             serve on the configured loopback address (default 127.0.0.1:8081) until interrupted; self-check first
  token issue PRINCIPAL --label TEXT [--expires-at ISO]   issue a service token (shown ONCE); token revoke TOKEN-OR-DIGEST-PREFIX
  record-trace                 store a rule evaluation for a case (reads the JSON request on stdin; operator command, audited)
  produce-traces               evaluate one rule function for every case and store the traces (Stage 20 DW-08; active set, or a named
                               --ruleset-ref as a what-if; case attributes from the read-only legacy snapshot of --legacy-root; idempotent)
Logs are JSON lines on stderr (stdout carries the result). Same guards as hub.admin: egress guard, runtime floor, hub.kill, anchor at the end.
No model call, no network beyond loopback. Shipped zone_h.holders is EMPTY: no Zone H action can be accepted until a holder is configured.
"""
import argparse
import json
import sys

from hub.admin.cli import _Run, _dump
from hub.core.errors import ConfigInvalid, HubError, RuntimeUnsupported


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.web", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
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
    p = store("serve")
    p.add_argument("--port", type=int, default=8081)
    p = store("token")
    p.add_argument("action", choices=["issue", "revoke"])
    p.add_argument("subject")
    p.add_argument("--label", default=None)
    p.add_argument("--expires-at", default=None)
    store("record-trace")
    p = store("produce-traces")
    p.add_argument("--legacy-root", required=True)
    p.add_argument("--function", required=True)
    p.add_argument("--ruleset-ref", default=None)
    return ap


def _cmd(r, a):
    import os
    from hub.security import settings
    from hub.web import schema, tokens
    data_dir = os.path.abspath(a.data_dir)
    if a.cmd == "migrate":
        res = schema.apply(data_dir, os.path.abspath(a.backup_root), settings.anchor_path(r.s, data_dir), r.clock, r.cid)
        res["backup"] = res["backup"] and {k: res["backup"][k] for k in ("label", "path", "files", "schema_versions")}
        return res, 0
    if a.cmd == "serve":
        from hub.web import server
        from hub.web.app import WebApp
        app = WebApp(data_dir, r.cfg, r.clock, log_sink=lambda line: sys.stderr.write(line + "\n"))
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
    if a.cmd == "status":
        return schema.status(con), 0
    if a.cmd == "token":
        if a.action == "issue":
            if not a.label:
                raise ConfigInvalid({"token issue": "needs --label"})
            tok = tokens.issue(con, r.clock, r.anchor, a.subject, a.label, r.operator, a.expires_at, r.cid)
            return {"token": tok, "shown_once": True, "digest_prefix": __import__("hashlib").sha256(tok.encode()).hexdigest()[:8]}, 0
        return tokens.revoke(con, r.clock, r.anchor, a.subject, r.operator, r.cid), 0
    if a.cmd == "record-trace":
        from hub.review.service import ReviewService
        req = json.loads(sys.stdin.read())
        svc = ReviewService(con, r.s, r.clock, r.anchor)
        return svc.record_trace(r.operator, "human", req["case_id"], req["function"], req["ruleset_ref"], req["inputs"], req["result"], r.cid), 0
    if a.cmd == "produce-traces":  # Stage 20 DW-08
        import tempfile
        from hub.guards import sandbox
        from hub.policy.service import PolicyService
        from hub.review import producer
        base = os.path.join(data_dir, "trace-runs")
        sandbox.assert_safe_path(base, "run directory")
        os.makedirs(base, exist_ok=True)
        cases = producer.load_case_inputs(sandbox.assert_safe_path(os.path.abspath(a.legacy_root), "legacy source root"),
                                          tempfile.mkdtemp(prefix="tr-", dir=base))
        rep = producer.produce(con, r.s, r.clock, r.anchor, PolicyService(con, r.s, r.clock, r.anchor), cases, a.function, a.ruleset_ref, r.cid)
        rep["trace_ids"] = rep["trace_ids"][:5] + (["..."] if len(rep["trace_ids"]) > 5 else [])
        return rep, 0
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
