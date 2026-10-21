"""Policy withdrawal (Stage 20 DW-07; FR-POL-01, BEH-POL-05, DEV-36, RTD-39; proposed criterion FAC-13).

A withdrawal is NOT a new policy_object row and not a status change of a stored row (policy_object is immutable and its status CHECK
has no 'withdrawn' value - M002): it is one immutable `POLICY_WITHDRAWN` policy_events row (event type already allowed by M002) for an
ADOPTED version, written with its hash-chained audit record through the Zone H gate (ZH-10, hub.policy.service.PolicyService.withdraw /
hub.gate.actions op `withdraw_policy`). From `withdrawn_from` (YYYY-MM-DD, inclusive) the version stops applying:
  * PolicyService.list_policies / get_policy add a `withdrawal` object to a version whose withdrawal is in effect (the stored `status`
    stays 'adopted', so every row keeps its recorded history); status_report lists it under 'withdrawn';
  * clock verdicts are produced only for an adopted clock WITHOUT a withdrawal in effect (hub.policy.clocks);
  * the overlap rule ends a withdrawn window at `withdrawn_from`, so a new adoption of the same (kind, definition_tag) may start then;
  * closure (hub.decision.service.closing_set) and consistency rules (hub.r2.consistency) skip a withdrawn version;
  * metric values computed from a policy whose withdrawal is in effect at their computed_at carry `detail.policy_withdrawal`
    (metric_value.policy_status CHECK has no 'withdrawn' value - M005 - so the marker lives in `detail`).
"In effect at T" = the event was recorded at or before T and `withdrawn_from` <= the date of T: a later withdrawal never rewrites an earlier
stored value, so `reproduce` stays exact. Pure SQL reads; no clock of its own (the caller passes T).
"""
import json
import re

EVENT = "POLICY_WITHDRAWN"
_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


def valid_date(value):
    return isinstance(value, str) and bool(_DATE.match(value))


def recorded(con, policy_ref):
    """The withdrawal event of `policy_ref` ('ID@version') regardless of time, or None."""
    row = con.execute("SELECT event_id, occurred_at, new_value, authority_ref, actor FROM policy_events WHERE policy_ref = ? AND event_type = ?"
                      " ORDER BY event_id LIMIT 1", (policy_ref, EVENT)).fetchone()
    if row is None:
        return None
    v = json.loads(row[2])
    return {"event_id": row[0], "recorded_at": row[1], "withdrawn_from": v["withdrawn_from"], "reason": v.get("reason"),
            "authority_ref": row[3], "actor": row[4]}


def effective(con, policy_ref, as_of):
    """The withdrawal of `policy_ref` if it is in effect at timestamp `as_of` (ISO, 'Z'), else None."""
    w = recorded(con, policy_ref)
    if w is None or not isinstance(as_of, str) or len(as_of) < 10:
        return None
    if w["recorded_at"] > as_of or w["withdrawn_from"] > as_of[:10]:
        return None
    return w


def overlay(con, policy, as_of):
    """Return `policy` (dict) with a `withdrawal` key added when one is in effect at `as_of`; the input is not modified."""
    w = effective(con, "%s@%d" % (policy["policy_id"], policy["version"]), as_of)
    return dict(policy, withdrawal=w) if w else policy
