"""Clock policies (BEH-POL-04, AC-POL-06/07/08): elapsed time is computable under every configured clock whatever its
status; a pass/fail verdict exists only for a clock with status `adopted` and a non-null `duration_hours`; otherwise
`verdict = not_available_no_adopted_policy`. Boundary rule stated in the response: elapsed_hours <= duration_hours.
Timestamps: YYYY-MM-DDTHH:MM:SS[.ffffff]Z (UTC). No clock is read here: the caller supplies the timestamps.
"""
import datetime
import decimal

from hub.policy import inputs as _in
from hub.policy.errors import ClockCalendarRequired, PolicyInvalid

BOUNDARY_RULE = "elapsed_hours <= duration_hours (inclusive)"
NO_POLICY = "not_available_no_adopted_policy"
_FORMATS = ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ")


def validate_body(kind, body):
    """Body validation by kind (policy-object.schema.json). CLOCK needs events, basis and calendar_ref iff business."""
    if not isinstance(body, dict):
        raise PolicyInvalid({"reason": "body must be an object"})
    if kind != "CLOCK":
        return body
    for k in ("clock_start_event", "clock_stop_event", "calendar_basis"):
        if not body.get(k) or not isinstance(body[k], str):
            raise PolicyInvalid({"reason": "CLOCK body needs " + k})
    if body["calendar_basis"] not in ("wall_clock", "business_calendar"):
        raise PolicyInvalid({"reason": "calendar_basis", "value": body["calendar_basis"]})
    if body["calendar_basis"] == "business_calendar" and not (isinstance(body.get("calendar_ref"), str) and body["calendar_ref"].strip()):
        raise ClockCalendarRequired({"calendar_basis": "business_calendar"})
    d = body.get("duration_hours")
    if d is not None and (isinstance(d, bool) or not isinstance(d, (int, float)) or d <= 0):
        raise PolicyInvalid({"reason": "duration_hours must be a positive number or null"})
    return body


def _ts(value):
    for f in _FORMATS:
        try:
            return datetime.datetime.strptime(value, f)
        except (ValueError, TypeError):
            continue
    raise PolicyInvalid({"reason": "timestamp must be YYYY-MM-DDTHH:MM:SS[.ffffff]Z", "value": str(value)[:40]})


def elapsed_hours(start_ts, stop_ts):
    td = _ts(stop_ts) - _ts(start_ts)
    micro = decimal.Decimal(td.days * 86400 * 10 ** 6 + td.seconds * 10 ** 6 + td.microseconds)
    return (micro / decimal.Decimal(3600 * 10 ** 6)).quantize(decimal.Decimal("0.0001"))


def clock_entry(policy, events):
    """One clock's result for one case. `policy` is a policy_object dict (latest version); `events` {event_name: ts}."""
    body = policy["body"]
    start, stop = events.get(body["clock_start_event"]), events.get(body["clock_stop_event"])
    elapsed = None if start is None or stop is None else elapsed_hours(start, stop)
    dur = body.get("duration_hours")
    if policy["status"] == "adopted" and not policy.get("withdrawal") and dur is not None:  # Stage 20 DW-07: no verdict once withdrawn
        verdict = "not_available_event_missing" if elapsed is None else (
            "within" if elapsed <= _in.to_decimal(dur, "duration_hours") else "not_within")
        rule = BOUNDARY_RULE
    else:
        verdict, rule = NO_POLICY, None
    return {"policy_ref": "%s@%d" % (policy["policy_id"], policy["version"]), "status": policy["status"],
            "elapsed_hours": None if elapsed is None else _in.text(elapsed), "verdict": verdict, "boundary_rule": rule}
