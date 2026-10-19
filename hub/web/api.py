"""Handlers of the 48 OpenAPI operations (INC-08). Each `op_<OP_ID>(ctx)` returns (status, document) or a Response.

A handler only translates: it parses the (already authenticated, CSRF-checked and authorised) request into service calls and shapes the result. All
business rules, role checks of the owning service and audit records stay in the services (INC-02..07, frozen). Operations whose backing service is
R2 / not built answer 501 E-REQ-NOT-IMPLEMENTED (OP-POL-07, OP-INT-04, OP-ID-04, OP-ID-05, OP-MET-06) or their own 501 (OP-REV-04, OP-MET-05).
"""
import hashlib
import json
import os

from hub.crosswalk.service import CrosswalkService
from hub.decision import errors as derr
from hub.decision.service import DecisionService
from hub.gate import pack as gpack
from hub.gate import reauth
from hub.gate.actions import ZoneHActions
from hub.gate.dispositions import DispositionService
from hub.intake.service import IntakeService
from hub.metrics import values as V
from hub.metrics.errors import MetNotAvailable, MetSourceRefused
from hub.metrics.service import MetricsService
from hub.policy.service import PolicyService
from hub.review import errors as rerr
from hub.review.service import ReviewService
from hub.runs.service import RunService
from hub.security import audit
from hub.security.auth import LocalAuthenticator
from hub.security.errors import AuthBadCredentials, AuthLocked
from hub.web import wire
from hub.web.errors import NotImplementedYet, ReqInvalid
from hub.web.tokens import CompositeAuthenticator

S, I, B, D, L = str, int, bool, dict, list
_OPT = (S, type(None))


def _int(ctx, name, default, lo, hi):
    v = ctx.q(name)
    if v is None:
        return default
    try:
        n = int(v)
    except ValueError:
        raise ReqInvalid({"pointer": "?" + name, "reason": "integer expected"})
    return max(lo, min(hi, n))


def _page(ctx, rows, default=50):
    limit, off = _int(ctx, "limit", default, 1, 100), _int(ctx, "cursor", 0, 0, 10 ** 9)
    chunk = rows[off:off + limit]
    return {"items": chunk, "next": str(off + limit) if off + limit < len(rows) else None}


# ---- service factories (one per request connection)
def dec(ctx):
    return ctx.svc("dec", lambda c: DecisionService(c.con, c.s, c.clock, c.anchor, c.app.d))


def pol(ctx):
    return ctx.svc("pol", lambda c: PolicyService(c.con, c.s, c.clock, c.anchor))


def disp(ctx):
    return ctx.svc("disp", lambda c: DispositionService(c.con, c.s, c.clock, c.anchor, c.app.d, c.app.disp))


def xw(ctx):
    return ctx.svc("xw", lambda c: CrosswalkService(c.con, c.s, c.clock, c.anchor))


def intake(ctx):
    return ctx.svc("intake", lambda c: IntakeService(c.con, c.s, c.clock, c.anchor))


def horizon(con):
    """The newest record time the metrics read (decision events, intake receipts, intake outcomes). GET metric values are computed AS OF this instant, not
    as of the wall clock, so two identical GETs give identical JSON until the data change (AC-MET-21); `computed_at` of a GET value is this data instant.
    Values stored by the metrics_snapshot job carry the real time."""
    rows = con.execute("SELECT max(x) FROM (SELECT max(recorded_at) AS x FROM decision_events UNION ALL SELECT max(receipt_time) FROM raw_intake"
                       " UNION ALL SELECT max(decided_at) FROM intake_outcome)").fetchone()
    return rows[0] or "1970-01-01T00:00:00.000000Z"


def met(ctx):
    def make(c):
        h = horizon(c.con)
        return MetricsService(c.con, c.s, lambda: h, c.anchor, c.app.cfg)
    return ctx.svc("met", make)


def rev(ctx):
    return ctx.svc("rev", lambda c: ReviewService(c.con, c.s, c.clock, c.anchor))


def authn(ctx):
    return CompositeAuthenticator(LocalAuthenticator(ctx.con, ctx.s, ctx.clock, ctx.anchor), ctx.con, ctx.clock)


def cookie(token, max_age):
    return ("Set-Cookie", "hub_session=%s; HttpOnly; SameSite=Strict; Path=/; Max-Age=%d" % (token, max_age))


# ---------------------------------------------------------------------------------------------------- system / security
def op_OP_SYS_01(ctx):
    return 200, {"status": "ok"}


def op_OP_SEC_01(ctx):
    b = wire.check(ctx.body, {"username": (S, True), "password": (S, True)})
    a = authn(ctx)
    try:
        token = a.login(b["username"], b["password"], ctx.cid)
    except AuthBadCredentials:
        ctx.app.metrics.auth_failure("bad_credentials")
        raise
    except AuthLocked:
        ctx.app.metrics.auth_failure("locked")
        raise
    sess = a.authenticate(token, ctx.cid, touch=False)
    from hub.web import csrf
    au = ctx.s["auth"]
    ctx.extra_headers.append(cookie(token, au["session_absolute_seconds"]))
    return 201, {"user": sess.principal.principal_id, "roles": list(sess.principal.roles), "token": token, "csrf_token": csrf.csrf_token(sess),
                 "idle_timeout_seconds": au["session_idle_seconds"], "absolute_timeout_seconds": au["session_absolute_seconds"]}


def op_OP_SEC_02(ctx):
    authn(ctx).logout(ctx.token, ctx.cid)
    ctx.extra_headers.append(cookie("", 0))
    return 201, {}


def op_OP_SEC_05(ctx):
    b = wire.check(ctx.body, {"password": (S, True)})
    sess = authn(ctx).reauthenticate(ctx.token, b["password"], ctx.cid)
    return 201, {"reauth_token": reauth.token_for(sess), "expires_in_seconds": ctx.s["zone_h"]["reauth_window_seconds"]}


def op_OP_SEC_03(ctx):
    after, limit = _int(ctx, "cursor", 0, 0, 10 ** 12), _int(ctx, "limit", 50, 1, 100)
    rows = ctx.con.execute("SELECT " + ", ".join(audit.FIELDS) + " FROM audit_log WHERE audit_seq > ? ORDER BY audit_seq LIMIT ?",
                           (after, limit + 1)).fetchall()
    items = []
    for r in rows[:limit]:
        d = dict(zip(audit.FIELDS, r))
        d["details"] = json.loads(d["details"]) if isinstance(d["details"], str) else d["details"]
        items.append(d)
    return 200, {"items": items, "next": str(items[-1]["audit_seq"]) if len(rows) > limit else None}


def op_OP_SEC_04(ctx):
    rep = audit.verify(ctx.con, ctx.app.anchor_path)
    ok = rep["status"] == "ok"
    kind = {"altered_record": "altered", "missing_record": "missing"}.get(rep.get("kind"), rep.get("kind"))
    return 201, {"ok": ok, "checked": rep.get("records", 0), "first_broken_seq": rep.get("first_broken_seq"), "failure_kind": None if ok else kind}


# ---------------------------------------------------------------------------------------------------- decision
def op_OP_DEC_01(ctx):
    b = wire.check(ctx.body, {"to_state": (S, True), "event_type": (S, True), "basis": (S, True), "evidence_refs": (L, False),
                              "expected_seq": (I, True), "occurred_at": (_OPT, False)})
    ev = dec(ctx).transition(ctx.sess, ctx.params["case_id"], to_state=b["to_state"], basis=b["basis"], event_type=b["event_type"],
                             evidence_refs=b.get("evidence_refs"), expected_seq=b["expected_seq"],
                             idempotency_key=ctx.req.headers.get("idempotency-key"), occurred_at=b.get("occurred_at"), correlation_id=ctx.cid)
    return 201, ev


def op_OP_DEC_02(ctx):
    after, limit = _int(ctx, "cursor", 0, 0, 10 ** 12), _int(ctx, "limit", 100, 1, 100)
    items = dec(ctx).events(ctx.sess, ctx.params["case_id"], after, limit, ctx.cid)
    return 200, {"items": items, "next": str(items[-1]["seq"]) if len(items) == limit else None}


def op_OP_DEC_03(ctx):
    return 200, dec(ctx).state(ctx.sess, ctx.params["case_id"], ctx.q("as_of"), ctx.cid)


def op_OP_DEC_04(ctx):
    return 200, dec(ctx).event_with_evidence(ctx.sess, ctx.params["event_id"], ctx.cid)


def op_OP_DEC_05(ctx):
    b = wire.check(ctx.body, {"fact_type": (S, True), "occurred_at": (_OPT, False), "basis": (S, False), "expected_seq": (I, True)})
    return 201, dec(ctx).record_fact(ctx.sess, ctx.params["case_id"], b["fact_type"], b.get("occurred_at"), b.get("basis") or "", b["expected_seq"],
                                     ctx.req.headers.get("idempotency-key"), ctx.cid)


def op_OP_DEC_06(ctx):
    b = wire.check(ctx.body, {"kind": (S, True), "source": (S, True), "source_ref": (S, True), "source_hash": (_OPT, False),
                              "access_level": (S, True), "note": (S, False)})
    return 201, dec(ctx).attach_evidence(ctx.sess, ctx.params["case_id"], b["kind"], b["source"], b["source_ref"], b.get("source_hash"),
                                         b["access_level"], b.get("note") or "", ctx.req.headers.get("idempotency-key"), ctx.cid)


# ---------------------------------------------------------------------------------------------------- gate
def op_OP_GATE_01(ctx):
    cid = ctx.params["case_id"]
    if dec(ctx)._head(cid) is None:
        raise derr.CaseNotFound({"case_id": cid[:40]})
    return 200, gpack.build(ctx.con, cid)


def op_OP_GATE_02(ctx):
    body = ctx.body
    za = ZoneHActions(ctx.con, ctx.s, ctx.clock, ctx.anchor, ctx.app.d, ctx.app.disp, ctx.app.cfg)
    return 201, za.execute(ctx.sess, body, ctx.cid)


def op_OP_GATE_03(ctx):
    return 200, disp(ctx).status()


def op_OP_GATE_04(ctx):
    b = wire.check(ctx.body, {"action": (S, True), "reason": (S, True), "replacement": ((S, I, D, L, B, float, type(None)), False)})
    r = disp(ctx).act_on_flag(ctx.sess, ctx.params["flag_id"], b["action"], b["reason"], b.get("replacement"), ctx.cid)
    return 201, r


# ---------------------------------------------------------------------------------------------------- policy
def op_OP_POL_01(ctx):
    rows = pol(ctx).list_policies(ctx.q("kind"), ctx.q("status"), ctx.q("latest_only") in ("1", "true"))
    return 200, _page(ctx, rows)


def op_OP_POL_02(ctx):
    b = wire.check(ctx.body, {"policy_id": (S, True), "kind": (S, True), "name": (S, True), "definition_tag": (_OPT, False), "body": (D, True),
                              "owner": (S, False), "authority_ref": (S, True)})
    return 201, pol(ctx).create_candidate(ctx.sess, b["policy_id"], b["kind"], b["name"], b["body"], b["authority_ref"], b.get("definition_tag"),
                                          b.get("owner") or "unassigned", ctx.cid)


def op_OP_POL_03(ctx):
    try:
        v = int(ctx.params["version"])
    except ValueError:
        raise ReqInvalid({"pointer": "version", "reason": "integer expected"})
    return 200, pol(ctx).get_policy(ctx.params["policy_id"], v)


def op_OP_POL_04(ctx):
    p = pol(ctx)
    return 200, {"items": p.list_rulesets(), "active": p.active()}


def op_OP_POL_05(ctx):
    return 200, pol(ctx).get_ruleset("%s@%s" % (ctx.params["ruleset_id"], ctx.params["version"]))


def op_OP_POL_06(ctx):
    b = wire.check(ctx.body, {"function": (S, True), "ruleset_ref": (_OPT, False), "inputs": (D, True)})
    return 201, pol(ctx).evaluate(b["function"], b["inputs"], b.get("ruleset_ref"))


def op_OP_POL_07(ctx):
    raise NotImplementedYet({"op": "OP-POL-07", "release": "R2"})


def op_OP_POL_08(ctx):
    cid = ctx.params["case_id"]
    d = dec(ctx)
    d.state(ctx.sess, cid, None, ctx.cid)  # existence + read role of the decision service
    events = {}
    for e in d.all_events(cid):
        events.setdefault(e["event_type"], e["occurred_at"])  # the first occurrence of each clock event
    return 200, pol(ctx).clock_report([{"case_id": cid, "events": events}])[0]


# ---------------------------------------------------------------------------------------------------- intake
_SOURCE_ALIAS = {"source_messages": "source_message"}
_ENV = {"source_key": (S, True), "partner": (S, True), "schema_rev": (_OPT, False), "source_ts": (S, True), "ref_id": (S, True),
        "record_kind": (S, True), "payload_text": (S, True)}


def op_OP_INT_01(ctx):
    b = wire.check(ctx.body, {"source": (S, True), "envelope": (D, True), "idempotency_key": (_OPT, False)})
    src = _SOURCE_ALIAS.get(b["source"], b["source"])
    env = b["envelope"]
    bad = [k for k in env if k not in _ENV]
    if bad:
        raise ReqInvalid({"errors": [{"pointer": "/envelope/" + k[:40], "reason": "unknown field"} for k in sorted(bad)]})
    ik = b.get("idempotency_key") or ctx.req.headers.get("idempotency-key")
    run_id = "HTTP-" + (hashlib.sha256((src + "|" + ik).encode("utf-8")).hexdigest()[:20] if ik else os.urandom(8).hex())
    svc = intake(ctx)
    if ik and ctx.con.execute("SELECT 1 FROM intake_run_event WHERE run_id = ?", (run_id,)).fetchone():
        pass  # replay of the same idempotency key: no second ingest, same receipt
    else:
        d = dict((k, env.get(k)) for k in _ENV)
        d["raw"] = dict(env)
        svc.ingest(src, [d], run_id, ctx.cid)
    r = ctx.con.execute("SELECT raw_id FROM raw_intake WHERE run_id = ? ORDER BY rowid LIMIT 1", (run_id,)).fetchone()
    if r is None:
        raise ReqInvalid({"reason": "nothing stored"})
    item = svc.get_item(r[0])
    cur = item["current"] or {}
    return 201, {"raw_id": r[0], "outcome": cur.get("outcome"), "primary_reason": cur.get("primary_reason"), "queue": cur.get("queue"),
                 "contract_check": cur.get("contract_check") or "not_bound", "run_id": run_id}


def _item_view(ctx, raw_id):
    svc = intake(ctx)
    it = svc.get_item(raw_id)
    raw = dict((k, it[k]) for k in ("raw_id", "source", "source_key", "partner", "schema_rev", "receipt_time", "content_hash", "duplicate_of", "run_id"))
    return {"raw": raw, "outcomes": it["outcomes"], "current": it["current"], "attributes": it["attributes"], "notes": it["notes"],
            "conflicts_with": [x for x in svc.versions(raw_id) if x != raw_id]}


def op_OP_INT_02(ctx):
    return 200, _item_view(ctx, ctx.params["raw_id"])


def op_OP_INT_03(ctx):
    b = wire.check(ctx.body, {"resolution": (S, True), "reason": (S, True)})
    intake(ctx).resolve_conflict(ctx.sess, ctx.params["raw_id"], b["resolution"], b["reason"], ctx.cid)
    return 201, _item_view(ctx, ctx.params["raw_id"])


def op_OP_INT_04(ctx):
    raise NotImplementedYet({"op": "OP-INT-04", "release": "R2"})


# ---------------------------------------------------------------------------------------------------- crosswalk
def op_OP_ID_01(ctx):
    i = ctx.q("id")
    if not i:
        raise ReqInvalid({"pointer": "?id", "reason": "required"})
    return 200, xw(ctx).lookup(ctx.sess, i, ctx.q("id_type"), ctx.cid)


def op_OP_ID_02(ctx):
    b = wire.check(ctx.body, {"from_type": (S, True), "from_id": (S, True), "to_type": (S, True), "to_id": (S, True), "reason": (S, True)})
    return 201, xw(ctx).create_human_link(ctx.sess, b["from_type"], b["from_id"], b["to_type"], b["to_id"], b["reason"], ctx.cid)


def op_OP_ID_03(ctx):
    b = wire.check(ctx.body, {"reason": (S, True)})
    return 201, xw(ctx).retract(ctx.sess, ctx.params["link_id"], b["reason"], ctx.cid)


def op_OP_ID_04(ctx):
    raise NotImplementedYet({"op": "OP-ID-04", "release": "R2"})


def op_OP_ID_05(ctx):
    raise NotImplementedYet({"op": "OP-ID-05", "release": "R2"})


# ---------------------------------------------------------------------------------------------------- runs
def op_OP_RUN_01(ctx):
    b = wire.check(ctx.body, {"job": (S, True), "trigger": (S, False), "batch_size": ((I, type(None)), False), "until_empty": (B, False)})
    if b.get("trigger", "manual") != "manual":
        raise ReqInvalid({"pointer": "/trigger", "reason": "only 'manual' is accepted over HTTP (scheduled runs are started by the host scheduler)"})
    res = ctx.app.run_resources() if callable(ctx.app.run_resources) else (ctx.app.run_resources or None)
    rec = RunService(ctx.con, ctx.s, ctx.clock, ctx.anchor, ctx.app.cfg).run(b["job"], ctx.sess, "manual", b.get("batch_size"),
                                                                              bool(b.get("until_empty")), res, ctx.cid)
    return 201, RunService.to_schema(rec)


def op_OP_RUN_02(ctx):
    runs = RunService(ctx.con, ctx.s, ctx.clock, ctx.anchor, ctx.app.cfg).list_runs(ctx.q("job"))
    return 200, _page(ctx, [RunService.to_schema(r) for r in runs])


def op_OP_RUN_03(ctx):
    return 200, RunService.to_schema(RunService(ctx.con, ctx.s, ctx.clock, ctx.anchor, ctx.app.cfg).get_run(ctx.params["run_id"]))


# ---------------------------------------------------------------------------------------------------- metrics
def _source(ctx):
    name = ctx.q("source")
    if not name:
        raise ReqInvalid({"pointer": "?source", "reason": "required"})
    if name not in ctx.app.sources:
        raise MetSourceRefused({"source": name[:40], "reason": "not a configured source"})
    return ctx.app.sources[name]


def op_OP_MET_01(ctx):
    ids = ctx.q("clock_ids")
    vals = met(ctx).time_to_close(ids.split(",") if ids else None, store=False)
    return 200, {"items": [v.to_dict() for v in vals]}


def op_OP_MET_02(ctx):
    v = met(ctx).month_end_total(ctx.q("cutoff_ts"), ctx.q("denominator_ref"), _source(ctx), ctx.q("allow_partial") in ("1", "true"), store=False)
    return 200, v.to_dict()


def op_OP_MET_03(ctx):
    m = met(ctx)
    tag = ctx.q("definition_tag")
    if ctx.q("kind") == "exception_rate":
        return 200, m.unresolved_exception_rate(tag, ctx.app.site_of, store=False).to_dict()
    return 200, m.backlog_by_site(tag, ctx.q("as_of"), ctx.app.site_of, store=False).to_dict()


def op_OP_MET_04(ctx):
    src = _source(ctx) if ctx.q("source") else None
    return 200, met(ctx).reproduce(ctx.params["value_id"], src, ctx.app.site_of)


def op_OP_MET_05(ctx):
    met(ctx).case_cost()


def op_OP_MET_06(ctx):
    raise NotImplementedYet({"op": "OP-MET-06", "release": "R2"})


def op_OP_MET_07(ctx):
    return 200, {"items": met(ctx).registry.list()}


def op_OP_MET_08(ctx):
    b = wire.check(ctx.body, {"values": (L, True), "op": (S, True)})
    if not b["values"] or not all(isinstance(x, str) for x in b["values"]):
        raise ReqInvalid({"pointer": "/values", "reason": "a non-empty list of value ids"})
    m = met(ctx)
    vals = [m.get_value(x) for x in b["values"]]
    op = b["op"]
    if op == "compare":
        if len(vals) != 2:
            raise ReqInvalid({"pointer": "/values", "reason": "compare takes exactly two values"})
        return 201, V.compare(vals[0], vals[1])
    if op in ("ratio", "difference"):
        raise MetNotAvailable({"op": op, "reason": "not implemented (no registered denominator semantics)"})
    return 201, V.combine(vals, op).to_dict()


# ---------------------------------------------------------------------------------------------------- reviewer
def op_OP_REV_01(ctx):
    r = rev(ctx).queue(ctx.sess, ctx.q("queue"), ctx.q("reason"), ctx.q("source"), ctx.q("min_age_hours"), ctx.q("limit"), ctx.q("cursor"), ctx.cid)
    return 200, r


def op_OP_REV_02(ctx):
    return 200, rev(ctx).explanations(ctx.sess, ctx.params["case_id"], ctx.cid)


def op_OP_REV_03(ctx):
    q = ctx.q("q")
    if q is None:
        raise ReqInvalid({"pointer": "?q", "reason": "required"})
    return 200, ctx.app.search.search(ctx.sess, q, ctx.q("limit"), ctx.q("cursor"), ctx.q("latest_only") in ("1", "true"))


def op_OP_REV_04(ctx):
    wire.check(ctx.body, {"template_id": (S, True), "fields": (D, False)})
    raise rerr.DraftsDisabled({"op": "OP-REV-04", "release": "R2"})
