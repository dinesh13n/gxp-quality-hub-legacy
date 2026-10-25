"""GateService: Zone H eligibility (BEH-GATE-01, BEH-GATE-05, BEH-GATE-07) for the closed action list ZH-01..ZH-10.

A Zone H action is executable only when ALL hold (there is no flag, environment variable, debug mode or CLI path that
skips a check - AC-GATE-21):
  (a) the session exists and its principal is a human (actor_kind human; service / scheduler / importer / integration
      identities are rejected)                                          -> E-AUTH-UNAUTHENTICATED / E-GATE-NOT-AUTHORISED
  (b) the principal has role dispositioner and is listed in zone_h.holders; an EMPTY list (ships empty, OD-S12-06)
      -> E-GATE-NO-HOLDERS; not listed -> E-GATE-NOT-AUTHORISED
  (c) the last step-up re-authentication is within zone_h.reauth_window_seconds -> E-GATE-REAUTH-REQUIRED
Every attempt, accepted or rejected, is written to the audit chain (action ZONE_H_ATTEMPT, actor, zone-H code,
correlation id) in its own transaction, so a refusal leaves a trace. The accepted record's audit_seq is the
`holder_check_ref` stored on Zone H events ("audit:<seq>"; the DB trigger refuses Zone H event types without one).
This module never reads free text and imports nothing from intake, runs, metrics, reviewer support or rules (BEH-GATE-02).
"""
from hub.gate.errors import GateNoHolders, GateNotAuthorised, GateReauthRequired, GateUnknownAction
from hub.security import audit, zone_h
from hub.security.errors import AuthUnauthenticated

ZONE_H_ACTIONS = {
    "ZH-01": "BATCH_DISPOSITION", "ZH-02": "QA_RELEASE", "ZH-03": "ESIGNATURE_RECORD", "ZH-04": "CLOSE_EXCEPTION",
    "ZH-05": "POLICY_ADOPT", "ZH-06": "RULESET_ACTIVATE", "ZH-07": "EXCEPTION_RULE_ACCEPT",
    "ZH-08": "DISPOSITION_MODE_CHANGE", "ZH-09": "SCHEDULE_ENABLE_DISABLE", "ZH-10": "POLICY_CHANGE",
}


class GateService(object):
    def __init__(self, con, settings, clock, anchor=None):
        self.con, self.s, self.clock, self.anchor = con, settings, clock, anchor

    def available(self):
        """OP-GATE-03 eligibility part: holders_configured count and availability (never reveals secrets)."""
        n = len(self.s["zone_h"]["holders"])
        return {"holders_configured": n, "available": n > 0}

    def require_holder(self, sess, zh, correlation_id, object_ref):
        """Return the audit_seq of the accepted ZONE_H_ATTEMPT record (the holder_check_ref) or raise."""
        holders = self.s["zone_h"]["holders"]
        if sess is None:  # Stage 27 S26-F-01 (ER-1): authenticate BEFORE the action name is looked at, so an anonymous caller learns nothing about valid names
            audit.append(self.con, self.clock, anchor=self.anchor, actor="anonymous", actor_kind="system",
                         action="ZONE_H_ATTEMPT", outcome="denied", correlation_id=correlation_id, object_ref=object_ref,
                         reason="unauthenticated", details={"zh": zh if zh in ZONE_H_ACTIONS else "unrecognised",
                                                            "zone_h_action": ZONE_H_ACTIONS.get(zh, "unrecognised"),
                                                            "reason": "unauthenticated", "holders_configured": len(holders)})
            raise AuthUnauthenticated()
        if zh not in ZONE_H_ACTIONS:
            audit.append(self.con, self.clock, anchor=self.anchor, actor=sess.principal.principal_id,
                         actor_kind=sess.principal.actor_kind, action="ZONE_H_ATTEMPT", outcome="denied",
                         correlation_id=correlation_id, object_ref=object_ref, reason="unknown_action",
                         details={"zh": str(zh)[:16], "reason": "unknown_action"})
            raise GateUnknownAction({"zh": str(zh)[:16]})
        p = sess.principal
        reason = zone_h.refusal(p, sess.reauth_at, self.clock, self.s["zone_h"], reject_integration=True)  # Stage 20 DW-06: the one rule
        err = {None: None, zone_h.NO_HOLDERS: GateNoHolders, zone_h.REAUTH: GateReauthRequired}.get(reason, GateNotAuthorised)
        rec = audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                           action="ZONE_H_ATTEMPT", outcome="denied" if err else "success", correlation_id=correlation_id,
                           object_ref=object_ref, reason=reason,
                           details={"zh": zh, "zone_h_action": ZONE_H_ACTIONS[zh], "reason": reason or "accepted",
                                    "holders_configured": len(holders)})
        if err:
            raise err({"zh": zh, "reason": reason})
        return rec["audit_seq"]
