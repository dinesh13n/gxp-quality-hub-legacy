"""Zone H eligibility check for policy actions ZH-05 (adopt), ZH-06 (activate rule set), ZH-10 (policy change).

There is no gate service until INC-05, so the same rules F02 will apply are enforced here (D-11):
  not a human / lacks role dispositioner / integration actor         -> E-GATE-NOT-AUTHORISED
  zone_h.holders is empty (ships empty, OD-S12-06)                    -> E-GATE-NO-HOLDERS
  principal not in zone_h.holders                                     -> E-GATE-NOT-AUTHORISED
  last re-authentication older than zone_h.reauth_window_seconds      -> E-GATE-NOT-AUTHORISED
Every attempt writes a ZONE_H_ATTEMPT audit record (success or denied) in its own transaction, so a refusal
leaves a trace. Returns the audit_seq of the attempt record (the holder_check_ref).
"""
from hub.policy.errors import GateNoHolders, GateNotAuthorised
from hub.security import audit, zone_h

ZONE_H_ACTIONS = {"ZH-05": "POLICY_ADOPT", "ZH-06": "RULESET_ACTIVATE", "ZH-10": "POLICY_CHANGE"}


def require_holder(con, settings, clock, anchor, sess, zh, correlation_id, object_ref):
    p = sess.principal
    holders = settings["zone_h"]["holders"]
    reason = zone_h.refusal(p, sess.reauth_at, clock, settings["zone_h"])  # Stage 20 DW-06: the one rule (hub.security.zone_h)
    err = None if reason is None else (GateNoHolders if reason == zone_h.NO_HOLDERS else GateNotAuthorised)
    rec = audit.append(con, clock, anchor=anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="ZONE_H_ATTEMPT",
                       outcome="denied" if err else "success", correlation_id=correlation_id, object_ref=object_ref,
                       reason=reason, details={"zh": zh, "zone_h_action": ZONE_H_ACTIONS[zh], "reason": reason or "accepted",
                                               "holders_configured": len(holders)})
    if err:
        raise err({"zh": zh, "reason": reason})
    return rec["audit_seq"]
