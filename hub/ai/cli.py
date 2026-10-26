"""`python -m hub.ai [--config FILE] <command>` - the OPTIONAL advisory Azure OpenAI document Q&A (Stage 44, OD-40). OFF by default.

  ask --data-dir D --principal P [--query Q] [--text] "<question>"
        Retrieve from the hub search as principal P (their own access rights), ask the model to answer only from those passages, check the answer is
        grounded and cited, print it labelled "AI-generated, advisory, not a GxP record, human verification required". Writes ONLY audit records.
  status --data-dir D
        Read-only: is it enabled, which AZURE_OPENAI_* variables are set (booleans, never values), today's usage vs the budget, the rate window. No model call.

Exit codes: 0 ok | 3 hub.kill | 40 refused (E-AI-DISABLED, -NOT-CONFIGURED, -NON-SYNTHETIC, -PRINCIPAL-REFUSED, -QUESTION-INVALID, -NO-RETRIEVAL,
-RATE-LIMITED, -BUDGET-EXCEEDED, -UNGROUNDED) | 41 provider failure (E-AI-PROVIDER-*) | 31/32 search errors | 2 config/usage. Same guards as hub.admin (egress guard,
runtime floor, hub.kill, CONFIG_LOADED audit, anchor at the end). Refusals for disabled / kill / missing settings happen before the store is opened.
"""
import argparse
import sys

from hub.admin.cli import _Run, _dump
from hub.core.errors import HubError, RuntimeUnsupported


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.ai", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--correlation-id", default=None)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("ask")
    p.add_argument("--data-dir", required=True)
    p.add_argument("--principal", required=True)
    p.add_argument("--query", default=None, help="explicit search grammar instead of the keywords derived from the question")
    p.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    p.add_argument("question")
    p = sub.add_parser("status")
    p.add_argument("--data-dir", required=True)
    return ap


def render_text(res):
    lines = ["*** %s ***" % res["label"], "(%s)" % res["data_label"], ""]
    lines.append(res["answer"] if res["answer"] else "The retrieved sources do not contain an answer (INSUFFICIENT_CONTEXT).")
    lines += ["", "Sources:"] + ["  [%s] %s %s (hash %s) %s" % (c["id"], c["doc_id"], c["version"], c["hash_prefix"], c["linked_case"]) for c in res["citations"]]
    lines += ["", "Grounding: %s" % res["grounding"]["note"], "Audit record: %s" % res["audit_seq"]]
    return "\n".join(lines)


def _status(r, a):
    from hub.adapters import azure_openai
    from hub.ai import limits, service, settings
    s = settings.resolve(r.cfg)
    out = {"enabled": s["enabled"], "kill": r.cfg["hub"]["kill"], "data_origin": r.cfg["data_origin"], "provider": s["provider"],
           "environment_variables_set": azure_openai.env_report(), "injection_policy": s["injection_policy"], "model_call_made": False}
    con = r.open_store()
    out["limits"] = limits.snapshot(con, r.clock(), s)
    out["corpus_origins"] = service.synthetic_corpus_or_refuse(con)
    return out


def _ask(r, a):
    from hub.ai import gate, service
    from hub.obs import metrics
    s, provider = gate.check(r.cfg)  # kill / disabled / non-synthetic / not configured: all before the store is opened
    con = r.open_store()
    ctx = service.Ctx(con, r.cfg, r.s, s, gate.client(s, provider), r.clock, r.anchor, r.cid)
    res = service.ask(ctx, a.principal, a.question, a.query)
    res["advisory_model_calls"] = metrics.value("ai_advisory_calls_total")
    return res


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
        out = _ask(r, args) if args.cmd == "ask" else _status(r, args)
        r.close()
        print(render_text(out) if (args.cmd == "ask" and args.text) else _dump(out))
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
