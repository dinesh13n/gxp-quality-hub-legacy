"""`python -m hub.search [--config FILE] <command>` - R2 search corpus operator commands (INC-09).

  status --data-dir D                          M007 state, FTS5 / trigram probe, selected engine and reason, latest corpus load (read-only)
  migrate --data-dir D --backup-root B         backup-before-migrate, then apply M007 (requires M001..M006)
  build-index --data-dir D --legacy-root L     (re)build the DERIVED corpus from a sandbox copy of the legacy tree (JSONL pinned; archive hashed)
  drop-index --data-dir D                      rollback: drop the FTS tables and empty search_doc (audited); search then answers E-REV-INDEX-ABSENT
Same guards as hub.admin (egress guard, runtime floor, hub.kill, CONFIG_LOADED audit, anchor at the end). No model call, no network.
"""
import argparse
import sys

from hub.admin.cli import _Run, _dump
from hub.core.errors import HubError, RuntimeUnsupported


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.search", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--correlation-id", default=None)
    sub = ap.add_subparsers(dest="cmd")
    for name in ("status", "migrate", "build-index", "drop-index"):
        p = sub.add_parser(name)
        p.add_argument("--data-dir", required=True)
        if name == "migrate":
            p.add_argument("--backup-root", required=True)
        if name == "build-index":
            p.add_argument("--legacy-root", required=True)
    return ap


def _cmd(r, a):
    import os
    from hub.search import corpus, fts, schema, settings as ssettings
    from hub.security import settings
    data_dir = os.path.abspath(a.data_dir)
    if a.cmd == "migrate":
        res = schema.apply(data_dir, os.path.abspath(a.backup_root), settings.anchor_path(r.s, data_dir), r.clock, r.cid)
        res["backup"] = res["backup"] and {k: res["backup"][k] for k in ("label", "path", "files", "schema_versions")}
        return res, 0
    con = r.open_store()
    st = ssettings.resolve(r.cfg)
    if a.cmd == "status":
        out = schema.status(con)
        if out["state"] == "applied":
            eng, why, pr = fts.select(con, st)
            out.update(engine=eng, engine_reason=why, probe=pr, corpus=corpus.current(con), search_enabled=st["enabled"], fts_flag=st["fts"])
        return out, 0
    if a.cmd == "build-index":
        docs, arch, inputs = corpus.read_shipped(os.path.abspath(a.legacy_root))
        rec = corpus.build(con, r.clock, r.anchor, r.operator, docs, arch, inputs, "shipped", st["max_doc_chars"], correlation_id=r.cid)
        return rec, 0
    if a.cmd == "drop-index":
        return corpus.drop(con, r.clock, r.anchor, r.operator, r.cid), 0
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
