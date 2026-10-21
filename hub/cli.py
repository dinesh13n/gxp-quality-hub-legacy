"""`python -m hub` command line (stdlib argparse). Every invocation installs the egress guard first, checks
the runtime floor, honours the kill switch and exports the zero-tripwires at the end.

  selfcheck       print Python / SQLite / FTS5 versions and the floor (AC-CO-14)
  init            create/migrate <data-dir>/hub.sqlite3 (M000) and seed the deviation register
  deviations      list the deviation register and the coexistence inventory (read-only)
  golden-compare  compare legacy goldens with new-side observations (exit 6 on UNAPPROVED / NOT-RUN); module probes need
                  --observe (observe the built modules inline) or --observed <record> (Stage 20 DW-04)
  golden-observe  run the built modules on the read-only baseline and write the observation record (Stage 20 DW-04)
  no-ai-check     dependency / import deny-list scan (exit 9 on findings)
"""
import argparse
import json
import sys

from hub.core.errors import HubError, HubKilled, RuntimeUnsupported


def _dump(obj):
    return json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False, default=str)


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None, help="hub config JSON (defaults are the safe INC-02 flags)")
    ap.add_argument("--floor", default=None, choices=["3.10", "3.12"], help="runtime floor (OD-S12-12)")
    ap.add_argument("--assume-python", default=None, help=argparse.SUPPRESS)  # test seam (AC-CO-14)
    ap.add_argument("--assume-sqlite", default=None, help=argparse.SUPPRESS)  # test seam (AC-CO-14)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("selfcheck")
    p = sub.add_parser("init")
    p.add_argument("--data-dir", required=True)
    p = sub.add_parser("deviations")
    p.add_argument("--data-dir", required=True)
    p = sub.add_parser("golden-compare")
    p.add_argument("--data-dir", required=True)
    p.add_argument("--legacy-root", default=None, help="sandbox copy whose data/ holds the FX-BASE125 baseline")
    p.add_argument("--probes", default=None)
    p.add_argument("--golden-dir", default=None)
    p.add_argument("--observations", default=None, help=argparse.SUPPRESS)  # test seam (AC-CO-02)
    p.add_argument("--observe", action="store_true", help="observe the built modules inline (Stage 20 DW-04)")
    p.add_argument("--observed", default=None, help="observation record written by golden-observe (checked: code digest + baseline)")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("golden-observe")
    p.add_argument("--data-dir", required=True)
    p.add_argument("--legacy-root", required=True, help="sandbox copy whose data/ holds the FX-BASE125 baseline")
    p.add_argument("--out", default=None, help="record path (default <data-dir>/runs/golden-observe/observation.json)")
    p = sub.add_parser("no-ai-check")
    p.add_argument("paths", nargs="*")
    return ap


def main(argv=None):
    from hub.guards import egress
    from hub.obs import metrics
    egress.install()
    metrics.reset()
    args = _parser().parse_args(argv)
    if not args.cmd:
        _parser().print_help()
        return 2
    rc = 0
    try:
        from hub import config, runtime
        cfg = config.load(args.config)
        floor = args.floor or cfg["runtime"]["floor"]
        rt = runtime.check(args.assume_python, args.assume_sqlite, floor)
        if args.cmd != "selfcheck" and cfg["hub"]["kill"]:
            raise HubKilled()
        if args.cmd == "selfcheck":
            print(_dump({"runtime": rt, "data_origin": cfg["data_origin"], "dependencies": "stdlib only (OD-08)",
                         "tripwires": metrics.tripwires()}))
        elif args.cmd == "init":
            from hub.store import db
            con = db.open_hub(args.data_dir)
            n = con.execute("SELECT count(*) FROM deviation_register").fetchone()[0]
            con.close()
            print(_dump({"hub_db": "hub.sqlite3", "deviation_register_rows": n}))
        elif args.cmd == "deviations":
            from hub.coexistence import register
            from hub.store import db
            con = db.open_hub(args.data_dir)
            try:
                rows = [dict(r, justification=r["justification"].escaped()) for r in register.rows(con)]
                inv = register.inventory(con)
            finally:
                con.close()
            print(_dump({"deviation_register": rows, "coexistence_inventory": inv}))
        elif args.cmd == "golden-compare":
            from hub.golden import compare, run
            report = run.run(args.data_dir, args.legacy_root, args.probes, args.golden_dir, args.observations,
                             observe=args.observe, observed_path=args.observed)
            metrics.check_tripwires()
            report["tripwires"] = metrics.tripwires()
            print(_dump(report) if args.json else compare.render_text(report))
            rc = report["exit_code"]
        elif args.cmd == "golden-observe":
            import os
            from hub.golden import observe
            from hub.guards import sandbox
            rec = observe.observe(args.data_dir, args.legacy_root)
            out = args.out or os.path.join(sandbox.assert_safe_path(args.data_dir, "hub data directory"), "runs", "golden-observe",
                                           "observation.json")
            out = sandbox.assert_safe_path(out, "observation record")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                f.write(_dump(rec) + "\n")
            metrics.check_tripwires()
            print(_dump(dict(rec, record=os.path.basename(out))))
        elif args.cmd == "no-ai-check":
            import os
            from hub.guards import no_ai, sandbox
            paths = args.paths or no_ai.default_targets(sandbox.PACKAGE_ROOT)
            no_ai.check(paths)
            print(_dump({"scanned": [os.path.relpath(p, sandbox.PACKAGE_ROOT) for p in paths], "findings": []}))
    except RuntimeUnsupported as e:
        sys.stderr.write(_dump(e.envelope()) + "\n")
        return e.exit_code
    except HubError as e:
        sys.stderr.write(_dump(e.envelope()) + "\n")
        rc = e.exit_code
    try:
        metrics.check_tripwires()
    except HubError as e:
        sys.stderr.write(_dump(e.envelope()) + "\n")
        rc = rc or e.exit_code
    return rc
