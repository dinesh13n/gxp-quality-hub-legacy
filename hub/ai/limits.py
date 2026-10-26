"""Rate limit and budget for the AI path (Stage 44, OD-40), counted FROM THE AUDIT LOG so that no other store is written and the limits hold across processes.

  rate    AI_QA_REQUESTED records in the last 60 s >= ai.rate_limit.max_requests_per_minute  -> E-AI-RATE-LIMITED (no model call)
  budget  units booked today (UTC) by AI_QA_ANSWERED / AI_QA_PROVIDER_ERROR + the estimate of this request > ai.budget.daily_token_budget, or the estimate
          alone > ai.budget.max_request_tokens -> E-AI-BUDGET-EXCEEDED (no model call)
Best effort for ONE operator: two simultaneous processes can both pass the check (documented residual risk). The limits protect cost, not safety.
"""
import datetime
import json

from hub.core.ai_errors import AiBudgetExceeded, AiRateLimited
from hub.security.canonical import fmt, parse


def requests_last_minute(con, now):
    cutoff = fmt(parse(now) - datetime.timedelta(seconds=60))
    return con.execute("SELECT count(*) FROM audit_log WHERE action = 'AI_QA_REQUESTED' AND occurred_at >= ?", (cutoff,)).fetchone()[0]


def units_today(con, now):
    day = now[:10] + "T00:00:00.000000Z"
    total = 0
    for (details,) in con.execute("SELECT details FROM audit_log WHERE action IN ('AI_QA_ANSWERED', 'AI_QA_PROVIDER_ERROR') AND occurred_at >= ?", (day,)):
        try:
            total += int(json.loads(details).get("usage_total", 0))
        except (ValueError, TypeError, AttributeError):
            continue
    return total


def snapshot(con, now, s):
    used = units_today(con, now)
    return {"requests_last_minute": requests_last_minute(con, now), "max_requests_per_minute": s["rate_limit"]["max_requests_per_minute"],
            "units_today": used, "daily_token_budget": s["budget"]["daily_token_budget"],
            "units_left_today": max(0, s["budget"]["daily_token_budget"] - used)}


def check(con, now, s, estimate):
    n = requests_last_minute(con, now)
    if n >= s["rate_limit"]["max_requests_per_minute"]:
        raise AiRateLimited({"requests_last_minute": n, "limit": s["rate_limit"]["max_requests_per_minute"], "retry_after_seconds": 60})
    if estimate > s["budget"]["max_request_tokens"]:
        raise AiBudgetExceeded({"scope": "request", "estimate": estimate, "limit": s["budget"]["max_request_tokens"]})
    used = units_today(con, now)
    if used + estimate > s["budget"]["daily_token_budget"]:
        raise AiBudgetExceeded({"scope": "day", "used": used, "estimate": estimate, "limit": s["budget"]["daily_token_budget"]})
    return {"requests_last_minute": n, "units_today": used}
