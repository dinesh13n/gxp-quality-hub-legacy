"""The closed job catalogue implementations (F06-2). A job is `fn(ctx) -> result dict`; the runner (hub.runs.service) owns the run record, the
lock, the checkpoint rows and the reconciliation.

Result keys: inputs_seen, outcomes_by_type, errors, limit_reached, backlog_remaining, checkpoint, reconcile_intake.

Jobs never touch Zone H: this module imports nothing from hub.gate and calls only the read / pipeline methods listed in
SERVICE_CALLS (AC-RUN-12; the AST test in tests/hub/test_tst_run_01_15_runs.py compares every attribute call here with ZONE_H_METHODS).
There is no capacity constant in this file: the cap is `ctx.batch_size` (configuration or --batch-size), printed in the run record.
"""
from hub.decision import settings as dsettings
from hub.decision.service import DecisionService
from hub.intake.errors import SourceUnreachable
from hub.intake.service import IntakeService
from hub.runs.catalogue import INTAKE_JOBS
from hub.security import audit
from hub.security.errors import AuditTamperDetected

SERVICE_CALLS = ("ingest", "verify_projection", "rebuild_projection", "verify_chain", "snapshot", "items_after", "verify")


def _result(inputs=0, outcomes=None, errors=None, limit=False, backlog=0, checkpoint=None, reconcile=False):
    return {"inputs_seen": inputs, "outcomes_by_type": dict(sorted((outcomes or {}).items())), "errors": list(errors or []),
            "limit_reached": limit, "backlog_remaining": backlog, "checkpoint": checkpoint, "reconcile_intake": reconcile}


def run_ordered(ctx, names):
    readers = ctx.res.get("readers", {})
    svc = IntakeService(ctx.con, ctx.s, ctx.clock, ctx.anchor)
    keys = dict((ctx.checkpoint or {}).get("order_keys", {}))
    errors, plan = [], []
    for name in names:
        r = readers.get(name)
        if r is None:
            errors.append({"code": "SOURCE_NOT_CONFIGURED", "detail": name})
            continue
        try:
            plan.append((name, r.items_after(keys.get(name))))
        except SourceUnreachable:
            errors.append({"code": "SOURCE_UNREACHABLE", "detail": name})
    if errors and not plan:
        return _result(errors=errors, checkpoint=ctx.checkpoint, reconcile=True)
    total = sum(len(items) for _, items in plan)
    budget = None if ctx.until_empty else ctx.batch_size
    outcomes, inputs, k, skipped, stop = {}, 0, 0, 0, False
    for name, items in plan:
        pos = 0
        while pos < len(items):
            if budget is not None and budget <= 0:
                stop = True
                break
            n = ctx.batch_size if budget is None else min(ctx.batch_size, budget)
            chunk = items[pos:pos + n]
            k += 1
            rep = svc.ingest(name, [d for _, d in chunk], "%s.b%04d" % (ctx.run_id, k), ctx.cid, idempotent_backfill=True)
            for oc, c in rep["outcomes"].items():
                outcomes[oc] = outcomes.get(oc, 0) + c
            skipped += rep["skipped_existing"]
            inputs += len(chunk)
            pos += len(chunk)
            if budget is not None:
                budget -= len(chunk)
            keys[name] = chunk[-1][0]
            ctx.checkpoint_save({"order_keys": dict(keys)}, inputs, outcomes, total - inputs)
        if stop:
            break
    backlog = total - inputs
    res = _result(inputs, outcomes, errors, backlog > 0, backlog, {"order_keys": keys} if keys else ctx.checkpoint, True)
    res["extras"] = {"skipped_existing": skipped, "batches": k}
    return res


def make_intake_job(job):
    names = INTAKE_JOBS[job]
    return lambda ctx: run_ordered(ctx, names)


def verify_audit(ctx):
    rep = audit.verify(ctx.con, ctx.res.get("anchor_path"))
    if rep["status"] != "ok":
        raise AuditTamperDetected(rep)
    return _result(1, {"audit_chain_ok": 1})


def verify_projection(ctx):
    rep = DecisionService(ctx.con, ctx.s, ctx.clock, ctx.anchor, dsettings.resolve(ctx.cfg)).verify_projection()
    key = "projection_consistent" if rep["mismatches"] == 0 else "projection_mismatch"
    return _result(rep["cases"], {key: rep["mismatches"] or rep["cases"]}, [] if rep["mismatches"] == 0 else
                   [{"code": "PROJECTION_MISMATCH", "detail": "%d case(s)" % rep["mismatches"]}])


def rebuild_projection(ctx):
    svc = DecisionService(ctx.con, ctx.s, ctx.clock, ctx.anchor, dsettings.resolve(ctx.cfg))
    rep = svc.rebuild_projection(ctx.cid)
    return _result(rep["cases"], {"projection_rebuilt": rep["cases"]})


def metrics_snapshot(ctx):
    from hub.metrics.service import MetricsService
    rows = MetricsService(ctx.con, ctx.s, ctx.clock, ctx.anchor, ctx.cfg).snapshot(ctx.cid, site_of=ctx.res.get("site_of"))
    return _result(len(rows), dict((r["metric_id"], 1) for r in rows))


IMPLEMENTATIONS = dict((j, make_intake_job(j)) for j in INTAKE_JOBS)
IMPLEMENTATIONS.update({"verify_audit": verify_audit, "verify_projection": verify_projection, "rebuild_projection": rebuild_projection,
                        "metrics_snapshot": metrics_snapshot})
