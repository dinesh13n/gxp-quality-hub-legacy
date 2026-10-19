"""`python -m hub.intake [--config FILE] <command>` - host-operator commands for the INC-06 intake (shadow mode over sandbox copies, C6).

  status          M004 state, raw / outcome / run counts and the queue snapshot (read-only)
  migrate         backup-before-migrate, then apply M004 (requires M001, M002 and M003)
  ingest-legacy   shadow intake of the legacy partner_feeds / source_messages / gateway_inbox (+ the vendor CSV with --csv-tier) read from the
                  SANDBOX copy --legacy-root through the hash-gated read-only snapshot adapter; idempotent by (source, key, content hash)
  gateway-pull    pull one page of events from a loopback gateway URL (http/https, loopback only); an unreachable source is a failed run
  verify-replay   re-deliver the legacy partner feeds as a normal run and prove nothing changed (replay safety, gate G2)
  report          queue snapshot (sizes, ages, per-reason counts, totals)

Contract bindings and conflict resolutions need an authenticated human session (Zone H ZH-10 / reviewer) and are service calls
(hub.intake.service); this CLI records no decision and cannot switch a source to `enforce`. Same guards as hub.admin: egress guard,
runtime floor, hub.kill, CONFIG_LOADED audit record, anchor at the end. No model call, no network beyond loopback.
"""
import argparse
import os
import sqlite3
import sys

from hub.admin.cli import _Run, _dump
from hub.core.errors import HubError, RuntimeUnsupported

LEGACY_SOURCES = ("partner_feed", "source_message", "gateway")


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.intake", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
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
    p = store("ingest-legacy")
    p.add_argument("--legacy-root", required=True)
    p.add_argument("--run-dir", required=True)
    p.add_argument("--csv-tier", default=None, choices=["tiny"])
    p = store("gateway-pull")
    p.add_argument("--url", required=True)
    p.add_argument("--limit", type=int, default=50)
    p = store("verify-replay")
    p.add_argument("--legacy-root", required=True)
    p.add_argument("--run-dir", required=True)
    store("report")
    return ap


def _svc(r):
    from hub.intake.service import IntakeService
    return IntakeService(r.con, r.s, r.clock, r.anchor)


def _legacy(a):
    from hub.adapters import intake_sources, legacy_sqlite
    handle = legacy_sqlite.open_snapshot(os.path.abspath(a.legacy_root), "legacy.sqlite3", os.path.abspath(a.run_dir), pinned=True)
    try:
        return {"partner_feed": intake_sources.partner_feed_deliveries(handle),
                "source_message": intake_sources.source_message_deliveries(handle),
                "gateway": intake_sources.gateway_inbox_deliveries(handle)}, handle.provenance["source_sha256"]
    finally:
        handle.close()


def _cmd(r, a):
    from hub.intake import schema
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
            svc = _svc(r)
            st.update(svc.counts(), queue_snapshot=svc.queue_snapshot(r.clock()))
        return st, 0
    svc = _svc(r)
    if a.cmd == "report":
        return svc.queue_snapshot(r.clock()), 0
    if a.cmd == "ingest-legacy":
        from hub.adapters import intake_sources
        by_source, sha = _legacy(a)
        runs = {}
        for source in LEGACY_SOURCES:
            runs[source] = svc.ingest(source, by_source[source], "legacy-%s-%s" % (source, r.cid), r.cid, idempotent_backfill=True)
        csv_sha = None
        if a.csv_tier:
            rows, csv_sha = intake_sources.vendor_csv_deliveries(intake_sources.csv_path(os.path.abspath(a.legacy_root), a.csv_tier))
            runs["vendor_csv"] = svc.ingest("vendor_csv", rows, "legacy-vendor_csv-%s" % r.cid, r.cid, idempotent_backfill=True)
        return {"legacy_db_sha256": sha, "vendor_csv_sha256": csv_sha, "runs": runs, "counts": svc.counts(),
                "queue_snapshot": svc.queue_snapshot(r.clock())}, 0
    if a.cmd == "gateway-pull":
        from hub.adapters import gateway_client, intake_sources
        retries = int(r.cfg.get("gateway", {}).get("retries", 3))
        cp = svc.last_checkpoint("gateway")
        offset = cp["next_offset"] if cp else 0
        run_id = "gateway-%s" % r.cid
        try:
            page = gateway_client.fetch_events(a.url, offset, a.limit, retries)
        except HubError as e:
            if e.code == "E-INT-SOURCE-UNREACHABLE":
                svc.fail_run("gateway", run_id, "SOURCE_UNREACHABLE", e.details, r.cid)
                return {"status": "failed", "error": "SOURCE_UNREACHABLE", "details": e.details}, e.exit_code
            raise
        rep = svc.ingest("gateway", intake_sources.gateway_event_deliveries(page["items"]), run_id, r.cid,
                         checkpoint={"next_offset": page["next_offset"], "attempts": page["attempts"]})
        return {"report": rep, "next_offset": page["next_offset"]}, 0
    if a.cmd == "verify-replay":
        from hub.intake import replay
        by_source, _ = _legacy(a)
        res = replay.replay_safety(svc, "partner_feed", by_source["partner_feed"], "replay-%s" % r.cid, r.clock(), r.cid)
        res["report"] = {k: res["report"][k] for k in ("received", "stored", "outcomes", "noop_duplicate")}
        return res, (0 if res["ok"] else 28)
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
