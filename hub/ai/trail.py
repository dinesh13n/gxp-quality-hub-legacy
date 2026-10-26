"""The audit trail of the AI path - the ONLY thing hub.ai writes (Stage 44, OD-40). Four actions, all in the hash-chained audit_log:

  AI_QA_REQUESTED       written BEFORE the model call (question text <= 500 chars + sha256, query, source ids / hashes, prompt version, size estimate).
                        The per-minute rate limit counts these.
  AI_QA_ANSWERED        the shown answer (<= 4000 chars + sha256), citations, grounding result, provider usage (prompt / completion / total units), model,
                        finish reason, latency. The daily budget sums these.
  AI_QA_PROVIDER_ERROR  provider failure (code, HTTP status, retry-after) and the units charged against the budget (estimate for timeout / 5xx / bad response).
  AI_QA_REFUSED         refusal by the hub before or after the call (reason code; for an ungrounded answer a <= 500 char preview + sha256 + failed checks).
Detail keys never contain credential-like words (hub.security.audit refuses them): usage is stored as usage_prompt / usage_completion / usage_total.
The API key is never an input of this module.
"""
import hashlib

from hub.security import audit

REQUESTED, ANSWERED, PROVIDER_ERROR, REFUSED = "AI_QA_REQUESTED", "AI_QA_ANSWERED", "AI_QA_PROVIDER_ERROR", "AI_QA_REFUSED"


def sha(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def write(ctx, action, outcome, details, reason=None):
    """-> the audit record (dict with audit_seq). ctx supplies con, clock, anchor, actor, actor_kind, cid."""
    return audit.append(ctx.con, ctx.clock, anchor=ctx.anchor, actor=ctx.actor, actor_kind=ctx.actor_kind, action=action, outcome=outcome,
                        correlation_id=ctx.cid, object_ref="ai:qa", reason=reason, details=details)
