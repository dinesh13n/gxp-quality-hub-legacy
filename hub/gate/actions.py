"""Zone H choke point (OP-GATE-02, BEH-GATE-01/05/06/07, AC-GATE-02/09/10/21; INC-08).

EVERY Zone H action ZH-01..ZH-10 enters here, and this module calls GateService.require_holder exactly once per request BEFORE any payload is read:
  human interactive session -> dispositioner role in zone_h.holders (empty list ships: E-GATE-NO-HOLDERS) -> step-up re-authentication window.
There is no flag, environment variable, debug mode, header or CLI path that skips it (AC-GATE-21). The accepted attempt's audit_seq is handed to the
service that stores the result (`_Preapproved`, fail-closed, one-shot) so the delegate does not write a second ZONE_H_ATTEMPT record.

  ZH-01/02/03  DispositionService.record_disposition   (mode none -> E-GATE-MODE-NONE; event needs disposition.values + current pack_hash)
  ZH-04        DecisionService.transition(close_exception) via DispositionService
  ZH-05        GatedPolicyService.adopt / accept_open
  ZH-06        GatedPolicyService.record_activation_decision + activate / deactivate
  ZH-07        EXCEPTION_RULE_ACCEPTED policy event (record only; semantics undefined in the spec: Stage 12 gap, RTD-67)
  ZH-08        DISPOSITION_MODE_CHANGED policy event (latest wins; modes.current)
  ZH-09        schedule flag (SCHEDULE_CHANGED), same event as hub.runs.schedule
  ZH-10        GatedPolicyService.edit_rule_row; op withdraw_policy -> PolicyService.withdraw (Stage 20 DW-07, POLICY_WITHDRAWN)
Nothing in this module reads free text to choose an action, and no automated caller (intake, runs, metrics, reviewer support, rules) imports it.
"""
from hub.core.errors import ConfigInvalid
from hub.gate import modes, reauth
from hub.gate.disposition_errors import GatePayloadInvalid
from hub.gate.dispositions import DispositionService
from hub.gate.errors import GateReauthRequired, GateUnknownAction
from hub.gate.policy_binding import GatedPolicyService
from hub.gate.service import GateService
from hub.policy.errors import AuthorityRequired
from hub.security import audit
from hub.core.req_errors import ReqInvalid

REQUEST_KEYS = ("action", "case_id", "payload", "pack_hash", "authority_ref", "reauth_token")
OPS_05 = ("adopt", "accept_open")
OPS_06 = ("activate", "deactivate")


class _Preapproved(object):
    """Hands the already-audited holder check of THIS request to a delegate exactly `uses` times, for that one action only (fail closed)."""

    def __init__(self, seq, zh, uses=1):
        self.seq, self.zh, self.uses = seq, zh, uses

    def require_holder(self, sess, zh, correlation_id, object_ref):
        if zh != self.zh or self.uses <= 0:
            raise GateUnknownAction({"zh": str(zh)[:16], "reason": "no pre-approved holder check for this call"})
        self.uses -= 1
        return self.seq


class _ActionPolicy(GatedPolicyService):
    """GatedPolicyService whose Zone H hook consumes the choke point's accepted check; also writes the ZH-07 / ZH-08 policy events."""

    def bind(self, pre):
        self.pre = pre
        return self

    def _zone_h(self, sess, zh, cid, object_ref):
        return self.pre.require_holder(sess, zh, cid, object_ref)

    def record_exception_rule(self, sess, ref, row_id, reason, authority_ref, hcr_seq, correlation_id):
        self._need_authority(authority_ref)
        self.get_ruleset(ref)
        actor, akind = self._actor(sess)
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="EXCEPTION_RULE_ACCEPTED",
                          outcome="success", correlation_id=correlation_id, object_ref="ruleset:" + ref,
                          details={"ruleset_ref": ref, "row_id": row_id, "authority_ref": authority_ref}) as ctx:
            eid = self._event_row(ref, "EXCEPTION_RULE_ACCEPTED", actor, None, {"ruleset_ref": ref, "row_id": row_id, "reason": reason},
                                  authority_ref, "audit:%d" % hcr_seq)
            ctx.fields["details"]["event_id"] = eid
        return eid

    def change_disposition_mode(self, sess, mode, values, old, authority_ref, hcr_seq, correlation_id):
        self._need_authority(authority_ref)
        actor, akind = self._actor(sess)
        new = {"mode": mode, "values": values}
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="DISPOSITION_MODE_CHANGED",
                          outcome="success", correlation_id=correlation_id, object_ref="disposition",
                          details={"from_mode": old["mode"], "to_mode": mode, "values_count": len(values), "authority_ref": authority_ref}) as ctx:
            eid = self._event_row("disposition", "DISPOSITION_MODE_CHANGED", actor, {"mode": old["mode"], "values": old["values"]}, new,
                                  authority_ref, "audit:%d" % hcr_seq)
            ctx.fields["details"]["event_id"] = eid
        return eid

    def set_schedule(self, sess, enabled, authority_ref, hcr_seq, correlation_id):
        self._need_authority(authority_ref)
        from hub.runs.flag import schedule_state  # function-level since Stage 27: breaks the gate <-> runs package cycle (OD-27 debt)
        old = schedule_state(self.con)
        actor, akind = self._actor(sess)
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="SCHEDULE_CHANGED",
                          outcome="success", correlation_id=correlation_id, object_ref="schedule",
                          details={"from_enabled": old["enabled"], "to_enabled": enabled}) as ctx:
            eid = self._event_row("schedule", "SCHEDULE_CHANGED", actor, {"enabled": old["enabled"]}, {"enabled": enabled}, authority_ref,
                                  "audit:%d" % hcr_seq)
            ctx.fields["details"]["event_id"] = eid
        return eid


def _need(d, key, kind=str):
    v = d.get(key)
    if not isinstance(v, kind) or (kind is str and not v.strip()):
        raise GatePayloadInvalid({"field": key, "reason": "required %s" % kind.__name__})
    return v


class ZoneHActions(object):
    def __init__(self, con, s, clock, anchor=None, d=None, disposition=None, cfg=None):
        self.con, self.s, self.clock, self.anchor = con, s, clock, anchor
        self.gate = GateService(con, s, clock, anchor)
        self.disp = DispositionService(con, s, clock, anchor, d, disposition)
        self.pol = _ActionPolicy(con, s, clock, anchor)

    def execute(self, sess, request, correlation_id="zone-h"):
        """The single entry for ZH-01..ZH-10. Returns ZoneHResult {action, event_ref, mode_at_write, audit_seq, holder_check_ref}."""
        req = request if isinstance(request, dict) else {}
        zh = req.get("action")
        hseq = self.gate.require_holder(sess, zh if isinstance(zh, str) else "", correlation_id, "zone-h:%s" % str(zh)[:16])
        if not isinstance(request, dict):
            raise ReqInvalid({"pointer": "", "reason": "the request must be a JSON object"})
        unknown = sorted(k for k in req if k not in REQUEST_KEYS)
        if unknown:
            raise ReqInvalid({"unknown_fields": ["/" + k for k in unknown]})
        authority_ref = req.get("authority_ref")
        if not isinstance(authority_ref, str) or not authority_ref.strip():
            raise AuthorityRequired()
        if not reauth.matches(sess, req.get("reauth_token")):
            raise GateReauthRequired({"zh": zh, "reason": "reauth_token missing or not from the latest step-up re-authentication"})
        payload = req.get("payload", {})
        if not isinstance(payload, dict):
            raise ReqInvalid({"pointer": "/payload", "reason": "must be an object"})
        case_id = req.get("case_id")
        authority_ref = authority_ref.strip()
        out = getattr(self, "_" + zh.lower().replace("-", "_"))(sess, case_id, payload, req.get("pack_hash"), authority_ref, hseq, correlation_id)
        out.setdefault("action", zh)
        out.setdefault("mode_at_write", None)
        out["holder_check_ref"] = "audit:%d" % hseq
        if "audit_seq" not in out:
            row = self.con.execute("SELECT max(audit_seq) FROM audit_log WHERE correlation_id = ? AND outcome = 'success'"
                                   " AND action <> 'ZONE_H_ATTEMPT'", (correlation_id,)).fetchone()
            out["audit_seq"] = row[0] if row and row[0] else hseq
        return out

    # ---- ZH-01..03
    def _disposition(self, zh, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        return self.disp.record_disposition(sess, zh, case_id, dict(payload, authority_ref=authority_ref), pack_hash, hseq, cid)

    def _zh_01(self, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        return self._disposition("ZH-01", sess, case_id, payload, pack_hash, authority_ref, hseq, cid)

    def _zh_02(self, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        return self._disposition("ZH-02", sess, case_id, payload, pack_hash, authority_ref, hseq, cid)

    def _zh_03(self, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        return self._disposition("ZH-03", sess, case_id, payload, pack_hash, authority_ref, hseq, cid)

    # ---- ZH-04
    def _zh_04(self, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        _need({"case_id": case_id}, "case_id")
        svc = self.disp
        svc.gate = _Preapproved(hseq, "ZH-04")
        try:
            ev = svc.transition(sess, case_id, _need(payload, "to_state"), payload.get("basis", ""), "STATUS_CHANGE", payload.get("evidence_refs"),
                                payload.get("expected_seq"), None, payload.get("occurred_at"),
                                {"authority": payload.get("authority", authority_ref), "reason": payload.get("reason")}, cid)
        finally:
            svc.gate = GateService(self.con, self.s, self.clock, self.anchor)
        return {"event_ref": ev["event_id"]}

    # ---- ZH-05
    def _zh_05(self, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        pol = self.pol.bind(_Preapproved(hseq, "ZH-05"))
        op = payload.get("op")
        if op not in OPS_05:
            raise GatePayloadInvalid({"field": "payload.op", "allowed": list(OPS_05)})
        pid, ver = _need(payload, "policy_id"), _need(payload, "from_version", int)
        if op == "adopt":
            p = pol.adopt(sess, pid, ver, payload.get("effective_from"), payload.get("owner"), authority_ref, payload.get("effective_to"),
                          payload.get("body_updates"), cid)
        else:
            p = pol.accept_open(sess, pid, ver, payload.get("reason"), authority_ref, cid)
        ref = "%s@%d" % (pid, p["version"])
        return {"event_ref": pol.events(policy_ref=ref)[-1]["event_id"]}

    # ---- ZH-06
    def _zh_06(self, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        op = payload.get("op")
        if op not in OPS_06:
            raise GatePayloadInvalid({"field": "payload.op", "allowed": list(OPS_06)})
        fn = _need(payload, "function")
        if op == "deactivate":
            return {"event_ref": self.pol.bind(_Preapproved(hseq, "ZH-06")).deactivate(sess, fn, authority_ref, cid)["event_id"]}
        pol = self.pol.bind(_Preapproved(hseq, "ZH-06", 2))
        ref = _need(payload, "ruleset_ref")
        dec = pol.record_activation_decision(sess, fn, ref, authority_ref, payload.get("reason"), cid)
        return {"event_ref": pol.activate(sess, fn, ref, authority_ref, dec["decision_seq"], cid)["event_id"]}

    # ---- ZH-07
    def _zh_07(self, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        ref, reason = _need(payload, "ruleset_ref"), _need(payload, "reason")
        row_id = payload.get("row_id")
        if row_id is not None and not isinstance(row_id, str):
            raise GatePayloadInvalid({"field": "payload.row_id"})
        return {"event_ref": self.pol.record_exception_rule(sess, ref, row_id, reason, authority_ref, hseq, cid)}

    # ---- ZH-08
    def _zh_08(self, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        mode = payload.get("mode")
        if mode not in modes.MODES:
            raise GatePayloadInvalid({"field": "payload.mode", "allowed": list(modes.MODES)})
        old = modes.current(self.con, self.disp.disp)
        try:
            values = modes.check_values(payload["values"]) if "values" in payload else list(old["values"])
        except ConfigInvalid as e:
            raise GatePayloadInvalid(e.details)
        return {"event_ref": self.pol.change_disposition_mode(sess, mode, values, old, authority_ref, hseq, cid)}

    @property
    def disp_cfg(self):
        return self.disp.disp

    # ---- ZH-09
    def _zh_09(self, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        enabled = payload.get("enabled")
        if not isinstance(enabled, bool):
            raise GatePayloadInvalid({"field": "payload.enabled", "reason": "boolean required"})
        return {"event_ref": self.pol.set_schedule(sess, enabled, authority_ref, hseq, cid)}

    # ---- ZH-10
    def _zh_10(self, sess, case_id, payload, pack_hash, authority_ref, hseq, cid):
        if payload.get("op") not in ("edit_rule_row", "withdraw_policy"):
            raise GatePayloadInvalid({"field": "payload.op", "allowed": ["edit_rule_row", "withdraw_policy"]})
        pol = self.pol.bind(_Preapproved(hseq, "ZH-10"))
        if payload["op"] == "withdraw_policy":  # Stage 20 DW-07
            w = pol.withdraw(sess, _need(payload, "policy_id"), _need(payload, "version", int), payload.get("withdrawn_from"),
                             payload.get("reason"), authority_ref, cid)
            return {"event_ref": w["event_id"]}
        nref = pol.edit_rule_row(sess, _need(payload, "ruleset_ref"), _need(payload, "row_id"), authority_ref, payload.get("outcome_updates"),
                                 payload.get("conditions"), cid)
        evs = pol.events(policy_ref=nref, event_type="RULE_ROW_CHANGED")
        return {"event_ref": evs[-1]["event_id"]}
