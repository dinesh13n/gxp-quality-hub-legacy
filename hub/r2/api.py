"""INC-09 handlers for the R2 operations that answered 501 in INC-08 (DEV-82): OP-POL-07, OP-INT-04, OP-ID-04, OP-ID-05, OP-MET-06, plus the R2
versions of OP-REV-03 (FTS5 / fallback over the derived corpus) and OP-REV-04 (template drafts). Every other operation is the frozen INC-08
handler (module-level __getattr__ delegates to hub.web.api). OP-MET-05 stays E-MET-NOT-AVAILABLE (FR-MET-08: no cost input exists).
Handlers only translate; the rules live in hub.r2.* and hub.search.* services. Route roles come from the frozen registry (TST-SEC-01).
"""
from hub.intake.errors import ItemNotFound
from hub.r2 import consistency, divergence, drafts, intake_reports, joined, source_quality
from hub.r2.errors import R2InputInvalid
from hub.web import api as _r1
from hub.web import wire
from hub.web.errors import ReqInvalid

S, D = str, dict


def __getattr__(name):  # PEP 562: every handler not defined here is the INC-08 one
    return getattr(_r1, name)


def op_OP_POL_07(ctx):
    if ctx.app.case_inputs is None:
        raise R2InputInvalid({"reason": "no case input source configured for the divergence report"})
    inputs = ctx.app.case_inputs() if callable(ctx.app.case_inputs) else list(ctx.app.case_inputs)
    return 200, divergence.run(ctx.con, ctx.clock, ctx.anchor, ctx.sess, _r1.pol(ctx), inputs, ctx.cid)


def op_OP_INT_04(ctx):
    src = ctx.params["source"]
    st = intake_reports.settings(ctx.app.cfg)
    if ctx.q("view") == "freshness":
        rep = intake_reports.freshness_report(ctx.con, ctx.q("as_of") or ctx.clock(), st["freshness_hours"])
        rows = [x for x in rep["sources"] if x["source"] == src]
        if not rows:
            raise ItemNotFound({"source": src[:40], "reason": "no intake item for this source"})
        return 200, dict(rep, sources=rows, stale=[x["source"] for x in rows if x["older_than_threshold"]])
    rep = intake_reports.delay_report(ctx.con, src, st["delay_threshold_hours"])
    if not rep["items"]:
        raise ItemNotFound({"source": src[:40], "reason": "no intake item for this source"})
    page = _r1._page(ctx, rep["items"])
    return 200, dict(rep, items=page["items"], next=page["next"])


def op_OP_ID_04(ctx):
    i = ctx.q("id")
    if not i:
        raise ReqInvalid({"pointer": "?id", "reason": "required"})
    return 200, joined.view(ctx.con, ctx.s, ctx.clock, ctx.anchor, ctx.sess, i, ctx.q("id_type"), ctx.app.cfg, ctx.q("reason"), ctx.app.facts, ctx.cid)


def op_OP_ID_05(ctx):
    return 200, consistency.list_findings(ctx.con, ctx.sess)


def op_OP_MET_06(ctx):
    return 200, source_quality.compute(ctx.con, _r1.horizon(ctx.con), ctx.q("window_start"), ctx.q("window_end"), ctx.q("source"))


def op_OP_REV_03(ctx):
    q = ctx.q("q")
    if q is None:
        raise ReqInvalid({"pointer": "?q", "reason": "required"})
    return 200, ctx.app.search.search(ctx.sess, q, ctx.q("limit"), ctx.q("cursor"), ctx.q("latest_only") in ("1", "true"), con=ctx.con,
                                      reason=ctx.q("reason"), correlation_id=ctx.cid)


def op_OP_REV_04(ctx):
    b = wire.check(ctx.body, {"template_id": (S, True), "fields": (D, False)})
    return 201, drafts.create(ctx.con, ctx.clock, ctx.anchor, ctx.app.cfg, ctx.sess, b["template_id"], b.get("fields"), ctx.cid)
