"""`python -m hub.policy [--config FILE] <command>` - host-operator commands for the INC-04 policy & rule service.

  status          M002 state (applied / absent / drift), seeded policies, rule sets and the active pointers (read-only)
  migrate         backup-before-migrate, then apply M002 (requires M001: `python -m hub.admin migrate` first)
  seed            idempotent seed: 3 DEFINITION + 2 CLOCK candidates (none adopted)
  load-as-found   load the 3 as-found rule sets from --legacy-root (a SANDBOX copy) as inactive, read-only candidates
  rulesets        list rule sets (+ which function each is active for; empty on a fresh install)
  policies        list policy objects (all versions)
  evaluate        evaluate --function F --input JSON [--ruleset-ref R]  (no ref + no active set -> E-POL-NO-ACTIVE-RULESET)

Adoption, activation and rule edits are Zone H actions: they need an authenticated human holder session and are
available through hub.policy.service.PolicyService (the HTTP layer arrives with INC-05+); this CLI never activates anything.
Same guards as hub.admin: egress guard, runtime floor, hub.kill, CONFIG_LOADED audit record, anchor at the end.
"""
import argparse
import json
import os
import sqlite3
import sys

from hub.admin.cli import _Run, _dump
from hub.core.errors import HubError, RuntimeUnsupported


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.policy", description=__doc__,
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
    store("seed")
    p = store("load-as-found")
    p.add_argument("--legacy-root", required=True)
    p.add_argument("--run-dir", required=True)
    store("rulesets")
    store("policies")
    p = store("evaluate")
    p.add_argument("--function", required=True)
    p.add_argument("--input", required=True, help="JSON object")
    p.add_argument("--ruleset-ref", default=None)
    return ap


def _cmd(r, a):
    from hub.policy import schema
    from hub.policy.service import PolicyService
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
            svc = PolicyService(con, r.s, r.clock, r.anchor)
            st.update(policies=len(svc.list_policies()), rulesets=[x["ruleset_ref"] for x in svc.list_rulesets()],
                      active=svc.active())
        return st, 0
    svc = PolicyService(con, r.s, r.clock, r.anchor)
    if a.cmd == "seed":
        return {"seeded": svc.seed(r.cid)}, 0
    if a.cmd == "load-as-found":
        return {"rulesets": svc.load_as_found(os.path.abspath(a.legacy_root), os.path.abspath(a.run_dir), r.cid), "active": svc.active()}, 0
    if a.cmd == "rulesets":
        return {"rulesets": svc.list_rulesets(), "active": svc.active()}, 0
    if a.cmd == "policies":
        return {"policies": svc.list_policies()}, 0
    if a.cmd == "evaluate":
        try:
            inputs = json.loads(a.input)
        except ValueError:
            raise SystemExit(2)
        if not isinstance(inputs, dict):
            raise SystemExit(2)
        return svc.evaluate(a.function, inputs, a.ruleset_ref), 0
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
