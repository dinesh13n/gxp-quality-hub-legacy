"""`python -m hub.metrics [--config FILE] <command>` - metric registry and stored values (INC-07, C9). Read / compute only; no decision is recorded.

  registry                 seed the R1 KPI definitions (idempotent) and list them with their documentation pages (fails when a KPI lacks window /
                           denominator / exclusions / tag, AC-MET-15)
  snapshot                 compute and store the KPIs that need no explicit parameter (time to close per clock, backlog and unresolved-exception
                           rate under D-OPS); --legacy-root/--run-dir adds the per-site mapping from the sandbox legacy copy
  month-end                month-end total: --cutoff and --denominator are REQUIRED (no default); --legacy-root/--run-dir reads cases.amount from the
                           hash-gated read-only snapshot
  values [--metric ID]     stored values;  reproduce VALUE_ID  recompute a stored value (exit 30 + E-MET-NOT-REPRODUCIBLE when it differs)
  kpi-coverage             each registered KPI with its value or the stated reason
Every figure shows definition tag, policy version / status and the label 'synthetic, unvalidated'. Same guards as hub.admin.
"""
import argparse
import os
import sqlite3
import sys

from hub.admin.cli import _Run, _dump
from hub.core.errors import HubError, RuntimeUnsupported


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.metrics", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--correlation-id", default=None)
    sub = ap.add_subparsers(dest="cmd")

    def store(name):
        p = sub.add_parser(name)
        p.add_argument("--data-dir", required=True)
        return p

    store("registry")
    p = store("snapshot")
    p.add_argument("--legacy-root", default=None)
    p.add_argument("--run-dir", default=None)
    p = store("month-end")
    p.add_argument("--cutoff", default=None)
    p.add_argument("--denominator", default=None)
    p.add_argument("--legacy-root", default=None)
    p.add_argument("--run-dir", default=None)
    p.add_argument("--allow-partial", action="store_true")
    p = store("values")
    p.add_argument("--metric", default=None)
    p = store("reproduce")
    p.add_argument("value_id")
    p.add_argument("--legacy-root", default=None)
    p.add_argument("--run-dir", default=None)
    store("kpi-coverage")
    return ap


def _handle(a):
    from hub.adapters import legacy_sqlite
    return legacy_sqlite.open_snapshot(os.path.abspath(a.legacy_root), "legacy.sqlite3", os.path.abspath(a.run_dir), pinned=True)


def _cmd(r, a):
    from hub.metrics import sources, values
    from hub.metrics.service import MetricsService
    con = r.open_store()
    m = MetricsService(con, r.s, r.clock, r.anchor, r.cfg)
    if a.cmd == "registry":
        seeded = m.registry.seed_builtin()
        return {"seeded": seeded, "metrics": m.registry.list(), "documentation": m.registry.documentation_pages()}, 0
    if a.cmd == "snapshot":
        site_of = None
        if a.legacy_root:
            h = _handle(a)
            try:
                site_of = sources.case_sites(h)
            finally:
                h.close()
        return {"values": m.snapshot(r.cid, site_of=site_of)}, 0
    if a.cmd == "month-end":
        if not a.legacy_root:
            from hub.metrics.errors import MetSourceRefused
            raise MetSourceRefused({"reason": "no source given (--legacy-root/--run-dir -> cases.amount)"})
        h = _handle(a)
        try:
            mv = m.month_end_total(a.cutoff, a.denominator, sources.CasesAmountSource(h), a.allow_partial)
        finally:
            h.close()
        return {"value": mv.to_dict(), "text": values.render_text(mv)}, 0
    if a.cmd == "values":
        rows = m.values_for(a.metric) if a.metric else [m.get_value(x[0]) for x in con.execute("SELECT value_id FROM metric_value ORDER BY rowid")]
        return {"values": [v.to_dict() for v in rows]}, 0
    if a.cmd == "reproduce":
        source = site_of = None
        if a.legacy_root:
            h = _handle(a)
            try:
                source = sources.RowsSource("cases.amount", sources.CasesAmountSource(h).read())
                site_of = sources.case_sites(h)
            finally:
                h.close()
        return m.reproduce(a.value_id, source=source, site_of=site_of, strict=True), 0
    if a.cmd == "kpi-coverage":
        m.registry.seed_builtin()
        return {"kpis": m.kpi_coverage()}, 0
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
