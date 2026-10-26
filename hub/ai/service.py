"""Orchestration of one advisory question (Stage 44, OD-40). Retrieve -> limits -> audit REQUESTED -> model -> grounding -> audit ANSWERED.

Refusals that happen after the store is open are audited (AI_QA_REFUSED); nothing but the audit log is ever written. The model client is injected
(hub.ai.gate.client in production, never anything else), so no function here can reach the network by itself.
"""
import time

from hub.ai import DATA_LABEL, LABEL, grounding, limits, prompt, retrieve, trail
from hub.core.ai_errors import AiNonSynthetic, AiNoRetrieval, AiPrincipalRefused, AiQuestionInvalid, AiUngrounded
from hub.core.errors import HubError
from hub.review import search as rsearch
from hub.search import schema as sschema
from hub.security import auth

SYNTHETIC_ORIGINS = frozenset(("shipped", "shipped-archive", "synthetic", "synthetic-archive", "fixture", "fixture-archive"))
CHARGED_ON_ERROR = ("E-AI-PROVIDER-TIMEOUT", "E-AI-PROVIDER-UNAVAILABLE", "E-AI-PROVIDER-BAD-RESPONSE")


class Ctx(object):
    """con, cfg, sec (security settings), ai (ai settings), client, clock, anchor, cid, actor, actor_kind (filled by principal())."""

    def __init__(self, con, cfg, sec, ai, client, clock, anchor, cid):
        self.con, self.cfg, self.sec, self.ai, self.client, self.clock, self.anchor, self.cid = con, cfg, sec, ai, client, clock, anchor, cid
        self.actor, self.actor_kind = "unknown", "human"


def check_question(question, max_chars):
    q = question.strip() if isinstance(question, str) else ""
    if len(q) < 3 or len(q) > max_chars or "\x00" in q:
        raise AiQuestionInvalid({"length": len(q), "limit": max_chars})
    return q


def synthetic_corpus_or_refuse(con):
    """The corpus must be flagged synthetic (load record AND every row's origin). Anything else is refused (OD-40: synthetic data only)."""
    sschema.require(con)
    origins = set(r[0] for r in con.execute("SELECT DISTINCT origin FROM search_doc"))
    last = con.execute("SELECT origin FROM search_corpus_load ORDER BY load_id DESC LIMIT 1").fetchone()
    bad = sorted(o for o in origins | ({last[0]} if last else set()) if o not in SYNTHETIC_ORIGINS)
    if bad:
        raise AiNonSynthetic({"corpus_origins_not_synthetic": [str(b)[:30] for b in bad[:5]]})
    return sorted(origins)


def principal_session(ctx, principal_id):
    authn = auth.LocalAuthenticator(ctx.con, ctx.sec, ctx.clock, ctx.anchor)
    p = authn.principal(principal_id) if isinstance(principal_id, str) and principal_id else None
    if p is None or p.status != "active" or not any(r in p.roles for r in rsearch.ROLES):
        raise AiPrincipalRefused({"principal": str(principal_id)[:60]})
    ctx.actor, ctx.actor_kind = p.principal_id, p.actor_kind
    now = ctx.clock()
    return auth.Session(p, "0" * 64, now, now, now)


def _refuse(ctx, err, extra=None):
    d = {"code": err.code}
    d.update(extra or {})
    trail.write(ctx, trail.REFUSED, "denied", d, reason=err.code)
    return err


def _cite(sources, ids):
    by = dict((s["id"], s) for s in sources)
    return [{"id": i, "doc_id": by[i]["doc_id"], "version": by[i]["version"], "hash_prefix": by[i]["hash_prefix"], "source": by[i]["source"],
             "effective_at": by[i]["effective_at"], "linked_case": by[i]["linked_case"]} for i in ids if i in by]


def _call(ctx, built, req_details):
    """The model call with its audit records. -> (reply, latency_ms). A provider failure is audited and re-raised."""
    t0 = time.monotonic()
    try:
        reply = ctx.client.complete(built["messages"], ctx.ai["answer"]["max_output_tokens"])
    except HubError as e:
        charged = req_details["estimate_units"] if e.code in CHARGED_ON_ERROR else 0
        trail.write(ctx, trail.PROVIDER_ERROR, "error", {"code": e.code, "detail": e.details, "usage_total": charged,
                                                         "latency_ms": int((time.monotonic() - t0) * 1000)}, reason=e.code)
        raise
    return reply, int((time.monotonic() - t0) * 1000)


def ask(ctx, principal_id, question, query=None):
    """-> the advisory result dict. Raises HubError subclasses (E-AI-*, E-REV-*). The audit log is the only store written."""
    q = check_question(question, ctx.ai["retrieval"]["max_question_chars"])
    session = principal_session(ctx, principal_id)
    origins = synthetic_corpus_or_refuse(ctx.con)
    try:
        got = retrieve.retrieve(ctx.con, ctx.cfg, session, q, query, ctx.ai, ctx.cid, ctx.clock, ctx.anchor)
    except AiNoRetrieval as e:
        raise _refuse(ctx, e, {"question_sha256": trail.sha(q), "detail": e.details})
    built = prompt.build(q, got["sources"], ctx.ai["retrieval"]["max_question_chars"])
    estimate = prompt.estimate_units(built["chars"], ctx.ai["answer"]["max_output_tokens"])
    try:
        limits.check(ctx.con, ctx.clock(), ctx.ai, estimate)
    except HubError as e:
        raise _refuse(ctx, e, {"question_sha256": trail.sha(q), "estimate_units": estimate, "detail": e.details})
    req = {"question": q[:500], "question_sha256": trail.sha(q), "query_used": got["query_used"], "searches": got["searches"],
           "sources": [{"id": s["id"], "doc_id": s["doc_id"], "version": s["version"], "hash_prefix": s["hash_prefix"],
                        "instruction_like": s["instruction_like"]} for s in got["sources"]],
           "excluded": got["excluded"], "prompt_version": built["version"], "prompt_chars": built["chars"], "estimate_units": estimate,
           "provider": "azure_openai", "corpus_origins": origins}
    rec = trail.write(ctx, trail.REQUESTED, "success", req)
    reply, latency = _call(ctx, built, req)
    verdict = grounding.check(reply["text"], got["sources"])
    usage = reply["usage"] if reply["usage"]["total"] > 0 else {"prompt": estimate, "completion": 0, "total": estimate}
    if not verdict["ok"]:
        err = AiUngrounded({"checks": verdict["reasons"]})
        _refuse(ctx, err, {"answer_preview": reply["text"][:500], "answer_sha256": trail.sha(reply["text"]), "checks": verdict["reasons"],
                           "usage_total": usage["total"], "request_audit_seq": rec["audit_seq"]})
        raise err
    citations = _cite(got["sources"], verdict["cited"])
    answer = None if verdict["no_answer"] else reply["text"].strip()
    done = trail.write(ctx, trail.ANSWERED, "success", {
        "status": "insufficient_context" if verdict["no_answer"] else "answered", "answer": (answer or "")[:4000], "answer_sha256": trail.sha(reply["text"]),
        "citations": citations, "grounding": {"sentences": verdict["sentences"], "overlap_min": verdict["overlap_min"]},
        "usage_prompt": usage["prompt"], "usage_completion": usage["completion"], "usage_total": usage["total"], "model": reply["model"],
        "finish_reason": reply["finish_reason"], "latency_ms": latency, "request_audit_seq": rec["audit_seq"], "prompt_version": built["version"]})
    return {"label": LABEL, "data_label": DATA_LABEL, "status": "insufficient_context" if verdict["no_answer"] else "answered", "answer": answer,
            "citations": citations, "query_used": got["query_used"], "sources_considered": len(got["sources"]), "excluded": got["excluded"],
            "grounding": {"checked": True, "sentences": verdict["sentences"], "overlap_min": verdict["overlap_min"],
                          "note": "lexical check only; it does not prove the answer is true or complete"},
            "usage": usage, "latency_ms": latency, "model": reply["model"], "audit_seq": done["audit_seq"], "request_audit_seq": rec["audit_seq"]}
