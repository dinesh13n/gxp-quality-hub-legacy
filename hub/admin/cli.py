"""`python -m hub.admin [--config FILE] <command>` (stdlib argparse). Host-operator only; no web bootstrap.

  status          schema versions applied / pending (read-only)
  migrate         backup-before-migrate, then apply forward migrations (M001: audit_log, principals, releases)
  user create     create a principal offline (password from $HUB_NEW_USER_PASSWORD or stdin; never echoed)
  user list       list principals and roles (no credential material)
  verify-audit    recompute the audit chain and check anchors (exit 17 on tamper)
  anchor          append the current audit head to audit.anchor_path
  backup          hub.sqlite3 + anchor file -> <dest-root>/<label> with MANIFEST.json + SHA256SUMS
  restore         verify a backup, set the current store aside, restore, verify checksums + audit chain
  release-checklist  record G1-G10 for a release (G3/G5/G6/G7 evaluated here; others from --gate or not_run)
  scan            secret scan + deletion-path grep (+ retention triggers with --data-dir) (exit 16)
  startup-check   network exposure guard (exit 9 E-SEC-EXPOSURE-NOT-APPROVED)

Every command installs the egress guard, checks the runtime floor and honours hub.kill. Every command that opens
a migrated store appends CONFIG_LOADED (config sha256) first and anchors the audit head at the end of the run.
"""
import argparse
import json
import os
import sqlite3
import sys

from hub.core.errors import HubError, HubKilled, RuntimeUnsupported
from hub.security.errors import AuditTamperDetected, StoreNotMigrated


def _dump(obj):
    return json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False, default=str)


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.admin", description=__doc__,
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
    p.add_argument("--target", default=None)
    p = sub.add_parser("user")
    usub = p.add_subparsers(dest="ucmd")
    u = usub.add_parser("create")
    u.add_argument("--data-dir", required=True)
    u.add_argument("--principal", required=True)
    u.add_argument("--role", action="append", default=[])
    u.add_argument("--kind", choices=["human", "service"], default="human")
    u = usub.add_parser("list")
    u.add_argument("--data-dir", required=True)
    store("verify-audit")
    store("anchor")
    p = store("backup")
    p.add_argument("--dest-root", required=True)
    p.add_argument("--label", required=True)
    p = store("restore")
    p.add_argument("--backup", required=True)
    p = store("release-checklist")
    p.add_argument("--release", required=True)
    p.add_argument("--evidence-dir", required=True)
    p.add_argument("--scratch-root", required=True)
    p.add_argument("--gate", action="append", default=[], help="Gn=pass|fail|not_run:<evidence path>[:note]")
    p.add_argument("--mark-ready", action="store_true")
    p = sub.add_parser("scan")
    p.add_argument("--data-dir", default=None)
    sub.add_parser("startup-check")
    return ap


class _Run(object):
    def __init__(self, args):
        from hub import config, runtime
        from hub.security import canonical, settings
        self.args = args
        self.cfg = config.load(args.config)
        runtime.check(None, None, self.cfg["runtime"]["floor"])
        if self.cfg["hub"]["kill"]:
            raise HubKilled()
        self.s = settings.resolve(self.cfg)
        self.clock = canonical.utc_now
        self.operator = os.environ.get("HUB_OPERATOR", "host-operator")
        self.cid = args.correlation_id or ("cli-" + os.urandom(8).hex())
        self.con = None
        self.anchor = None

    def open_store(self, need_audit=True, config_loaded=True):
        from hub.security import audit, settings
        from hub.store import db, migrate
        data_dir = os.path.abspath(self.args.data_dir)
        self.anchor_path = settings.anchor_path(self.s, data_dir)
        self.anchor = audit.Anchor(self.anchor_path, self.s["audit"]["anchor_every"])
        self.con = db.open_hub(data_dir)
        migrate.check(self.con)
        if need_audit and not migrate.has_audit(self.con):
            raise StoreNotMigrated({"needs": "M001", "hint": "python -m hub.admin migrate"})
        if config_loaded and migrate.has_audit(self.con):
            self.config_loaded()
        return self.con

    def config_loaded(self):
        from hub.security import audit, settings
        audit.append(self.con, self.clock, anchor=self.anchor, actor="hub", actor_kind="system", action="CONFIG_LOADED",
                     outcome="success", correlation_id=self.cid, object_ref="config",
                     details={"config_hash": settings.config_hash(self.cfg), "command": self.args.cmd,
                              "zone_h_holders": list(self.s["zone_h"]["holders"]),
                              "anchor_every": self.s["audit"]["anchor_every"]})
        from hub.control import switch  # Stage 23 DW-17 (FF-2 rule 4): an authority value changed in the config file is audited CONFIG_CHANGED
        switch.record_authority_changes(self.con, self.clock, self.anchor, self.cfg, self.cid, self.args.cmd)

    def close(self):
        if self.con is not None:
            from hub.security import audit
            from hub.store import migrate
            try:
                if migrate.has_audit(self.con):
                    audit.write_anchor(self.con, self.anchor_path)  # end of every run (BEH-SEC-06)
            except (KeyError, ValueError, TypeError, AttributeError):
                # S30-DEV-01 (F-29-01): verify-audit on a malformed anchor line must still end with its tamper exit code (17), not a traceback (exit 1).
                # The anchor is NOT appended to (fail closed); every other command keeps the old behaviour (the error propagates).
                if getattr(self.args, "cmd", None) != "verify-audit":
                    raise
            finally:
                self.con.close()
                self.con = None


def _password():
    pw = os.environ.get("HUB_NEW_USER_PASSWORD")
    if pw is not None:
        return pw
    if sys.stdin.isatty():
        import getpass
        return getpass.getpass("password: ")
    return sys.stdin.readline().rstrip("\n")


def _gate_args(items):
    out = {}
    for it in items:
        gate, _, rest = it.partition("=")
        result, _, tail = rest.partition(":")
        path, _, note = tail.partition(":")
        out[gate.strip()] = {"result": result.strip(), "evidence_path": path.strip(), "note": note.strip() or None}
    return out


def _cmd(r, a):
    from hub.security import audit
    if a.cmd == "status":
        from hub.store import migrate
        return migrate.status(os.path.abspath(a.data_dir)), 0
    if a.cmd == "migrate":
        from hub.security import settings
        from hub.store import migrate
        data_dir = os.path.abspath(a.data_dir)
        anchor_path = settings.anchor_path(r.s, data_dir)
        res = migrate.migrate(data_dir, os.path.abspath(a.backup_root), anchor_path, r.clock, a.target)
        r.open_store(need_audit=False, config_loaded=False)
        if migrate.has_audit(r.con):
            if res["applied"]:
                audit.append(r.con, r.clock, anchor=r.anchor, actor=r.operator, actor_kind="human",
                             action="SCHEMA_MIGRATED", outcome="success", correlation_id=r.cid, object_ref="hub.sqlite3",
                             details={"from": res["from"], "to": res["to"], "applied": res["applied"],
                                      "pre_migration_backup": res["backup"]["label"],
                                      "backup_files": res["backup"]["files"]})
            r.config_loaded()
        res["backup"] = res["backup"] and {k: res["backup"][k] for k in ("label", "path", "files", "schema_versions")}
        return res, 0
    if a.cmd == "user":
        from hub.security import auth
        r.open_store()
        authn = auth.LocalAuthenticator(r.con, r.s, r.clock, r.anchor)
        if a.ucmd == "create":
            p = authn.create_user(a.principal, _password() if a.kind == "human" else None, a.role, r.operator,
                                  kind=a.kind, correlation_id=r.cid)
            return {"created": p.as_dict()}, 0
        rows = [authn.principal(x[0]).as_dict() for x in r.con.execute("SELECT principal_id FROM principal ORDER BY 1")]
        return {"principals": rows}, 0
    if a.cmd == "verify-audit":
        r.open_store(config_loaded=False)
        rep = audit.verify(r.con, r.anchor_path)
        audit.append(r.con, r.clock, anchor=r.anchor, actor=r.operator, actor_kind="human", action="AUDIT_VERIFIED",
                     outcome="success" if rep["status"] == "ok" else "error", correlation_id=r.cid,
                     details={k: rep.get(k) for k in ("status", "first_broken_seq", "kind", "records")})
        if rep["status"] != "ok":
            sys.stderr.write(_dump(AuditTamperDetected(rep).envelope()) + "\n")
            return rep, AuditTamperDetected.exit_code
        return rep, 0
    if a.cmd == "anchor":
        r.open_store()
        return {"anchored": audit.write_anchor(r.con, r.anchor_path)}, 0
    if a.cmd == "backup":
        from hub.ops import backup
        r.open_store()
        audit.append(r.con, r.clock, anchor=r.anchor, actor=r.operator, actor_kind="human", action="BACKUP",
                     outcome="success", correlation_id=r.cid, object_ref="hub.sqlite3", details={"label": a.label})
        audit.write_anchor(r.con, r.anchor_path)
        r.con.close()
        r.con = None
        m = backup.backup(os.path.abspath(a.data_dir), r.anchor_path, os.path.abspath(a.dest_root), a.label, r.clock)
        return m, 0
    if a.cmd == "restore":
        from hub.ops import backup
        from hub.security import settings
        data_dir = os.path.abspath(a.data_dir)
        r.anchor_path = settings.anchor_path(r.s, data_dir)
        rep = backup.restore(os.path.abspath(a.backup), data_dir, r.anchor_path, r.clock)
        r.open_store(need_audit=False, config_loaded=False)
        from hub.store import migrate
        rep["schema_after_restore"] = sorted(migrate.applied(r.con))
        if migrate.has_audit(r.con):
            rep["verify_audit"] = audit.verify(r.con, r.anchor_path)
            audit.append(r.con, r.clock, anchor=r.anchor, actor=r.operator, actor_kind="human", action="STORE_RESTORED",
                         outcome="success" if rep["verify_audit"]["status"] == "ok" else "error", correlation_id=r.cid,
                         object_ref="hub.sqlite3", details={"backup": rep["backup"], "checksum_match": rep["checksum_match"]})
            r.config_loaded()
            if rep["verify_audit"]["status"] != "ok":
                return rep, AuditTamperDetected.exit_code
        else:
            rep["verify_audit"] = {"status": "not_applicable", "reason": "restored store is below M001 (no audit_log)"}
        return rep, 0
    if a.cmd == "release-checklist":
        from hub.ops import gates, release
        r.open_store()
        ev = os.path.abspath(a.evidence_dir)
        os.makedirs(ev, exist_ok=True)
        results = _gate_args(a.gate)
        evals = {"G3": lambda: gates.g3_verify_audit(r.con, r.anchor_path), "G5": gates.g5_no_ai,
                 "G6": lambda: gates.g6_scan(r.con),
                 "G7": lambda: gates.g7_backup_restore(os.path.abspath(a.data_dir), r.anchor_path,
                                                       os.path.abspath(a.scratch_root), r.clock)}
        for gate, fn in sorted(evals.items()):
            if gate in results:
                continue
            res = fn()
            path = os.path.join(ev, "%s.json" % gate)
            with open(path, "w", encoding="utf-8") as f:
                f.write(_dump(res["evidence"]) + "\n")
            results[gate] = {"result": res["result"], "evidence_path": path, "note": "evaluated by hub.admin"}
        out = release.record_checklist(r.con, r.clock, a.release, results, r.operator, r.cid, anchor=r.anchor)
        with open(os.path.join(ev, "checklist-%s.json" % a.release), "w", encoding="utf-8") as f:
            f.write(_dump(out) + "\n")
        if a.mark_ready:
            out["final"] = release.mark_ready(r.con, r.clock, a.release, r.operator, r.cid, anchor=r.anchor)
        return out, 0
    if a.cmd == "scan":
        from hub.guards import sandbox
        from hub.security import scan
        con = r.open_store() if a.data_dir else None
        rep = scan.run(sandbox.PACKAGE_ROOT, con)
        if not rep["clean"]:
            from hub.security.errors import ScanFindings
            sys.stderr.write(_dump(ScanFindings({"secret": len(rep["secret_findings"]),
                                                 "deletion": len(rep["deletion_findings"])}).envelope()) + "\n")
            return rep, 16
        return rep, 0
    if a.cmd == "startup-check":
        from hub.security import exposure
        return exposure.check_startup(r.s), 0
    raise SystemExit(2)


def main(argv=None):
    from hub.guards import egress
    from hub.obs import metrics
    egress.install()
    metrics.reset()
    ap = _parser()
    args = ap.parse_args(argv)
    if not args.cmd or (args.cmd == "user" and not getattr(args, "ucmd", None)):
        ap.print_help()
        return 2
    r = None
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
