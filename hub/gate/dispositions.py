"""DispositionService: the INC-08 additive subclass of DecisionService (hub/decision/service.py is frozen, TST-CO-05 c).

* status()             OP-GATE-03: mode, values_set, holders_configured, available (never reveals a secret).
* record_disposition() ZH-01 / ZH-02 / ZH-03 AFTER the Zone H eligibility check (hub.gate.actions calls GateService first; this method never
                       decides eligibility). `none` -> E-GATE-MODE-NONE; `event` needs disposition.values (E-GATE-VALUES-UNSET), a decision from
                       the values, a basis and the CURRENT pack_hash (E-GATE-PACK-STALE) and stores DISPOSITION_RECORDED / QA_RELEASE_RECORDED /
                       ESIGNATURE_RECORDED with mode_at_write 'event'; `external_ref` stores only DISPOSITION_REFERENCED {system, reference, ...,
                       verified: false} with NO decision content. The database trigger independently refuses these event types unless the
                       actor is human and a holder_check_ref is present (AC-GATE-12).
* act_on_flag()        OP-GATE-04: override / dismiss / refuse (BEH-GATE-08). Reviewer, quality_lead or compliance (human); not a Zone H action.
                       The original rule output is never changed; an OVERRIDE_RECORDED event (affects_state false) is appended to the case when
                       the flag belongs to a case, and the action is also kept in the insert-only `flag_action` table.
A recorded decision is only ever typed by a human: nothing here has a default value, a suggestion or a recommended choice.
"""
import json
import re

from hub.core.untrusted import Untrusted, require_trusted
from hub.decision.errors import CaseNotFound, EvidenceUnresolved, FieldTooLong
from hub.decision.service import DecisionService
from hub.gate import flags, modes, pack
from hub.gate.disposition_errors import (GateExtrefInvalid, GateModeNone, GatePackStale, GatePayloadInvalid, GateReasonRequired,
                                         GateValuesUnset)
from hub.security import audit
from hub.security.canonical import canonical
from hub.security.errors import AuthUnauthenticated
from hub.store import m006 as web_schema  # Stage 20 DW-06: no hub.web import

TEXT_MAX = 2000
EVENT_TYPE = {"ZH-01": "DISPOSITION_RECORDED", "ZH-02": "QA_RELEASE_RECORDED", "ZH-03": "ESIGNATURE_RECORDED"}
FLAG_ROLES = ("reviewer", "quality_lead", "compliance")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _text(value, field, limit, required=False):
    if isinstance(value, Untrusted):
        value = value.for_storage()
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise GatePayloadInvalid({"field": field, "reason": "must be text"})
    value = value.strip()
    if len(value) > limit:
        raise FieldTooLong({"field": field, "length": len(value), "limit": limit})
    if required and not value:
        raise GatePayloadInvalid({"field": field, "reason": "required"})
    return value


class DispositionService(DecisionService):
    def __init__(self, con, s, clock, anchor=None, d=None, disposition=None):
        DecisionService.__init__(self, con, s, clock, anchor, d)
        web_schema.require(con)
        self.disp = disposition if disposition is not None else modes.resolve({})

    # ------------------------------------------------------------------ OP-GATE-03
    def mode(self):
        return modes.current(self.con, self.disp)

    def status(self):
        m = self.mode()
        g = self.gate.available()
        return {"mode": m["mode"], "values_set": bool(m["values"]), "holders_configured": g["holders_configured"], "available": g["available"]}

    # ------------------------------------------------------------------ ZH-01..03
    def _refuse(self, sess, zh, case_id, err, cid):
        p = sess.principal
        audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="ZONE_H_REFUSED",
                     outcome="denied", correlation_id=cid, object_ref="case:%s" % str(case_id)[:40], reason=err.code,
                     details={"zh": zh, "reason": err.code})
        raise err

    def record_disposition(self, sess, zh, case_id, payload, pack_hash, holder_audit_seq, correlation_id="gate"):
        """Store the human's disposition (ZH-01), QA release (ZH-02) or e-signature record (ZH-03). `holder_audit_seq` is the accepted
        ZONE_H_ATTEMPT record returned by GateService.require_holder for this very call."""
        if zh not in EVENT_TYPE:
            raise GatePayloadInvalid({"zh": str(zh)[:16]})
        require_trusted([case_id, pack_hash], "record_disposition")
        if not isinstance(payload, dict):
            raise GatePayloadInvalid({"field": "payload", "reason": "must be an object"})
        m = self.mode()
        if m["mode"] == "none":
            self._refuse(sess, zh, case_id, GateModeNone({"zh": zh}), correlation_id)
        if m["mode"] == "event" and not m["values"]:
            self._refuse(sess, zh, case_id, GateValuesUnset({"zh": zh}), correlation_id)
        if not isinstance(case_id, str) or not case_id:
            raise GatePayloadInvalid({"field": "case_id", "reason": "required"})
        refs = self._refs(payload.get("evidence_refs"))
        body = {}
        if m["mode"] == "event":
            basis = _text(payload.get("basis"), "basis", TEXT_MAX, required=True)
            if zh in ("ZH-01", "ZH-02"):
                decision = payload.get("decision")
                if not isinstance(decision, str) or decision not in m["values"]:
                    raise GatePayloadInvalid({"field": "decision", "allowed": list(m["values"])})
                body["decision"] = decision
            else:
                body["statement"] = _text(payload.get("statement"), "statement", TEXT_MAX, required=True)
                body["not_a_cryptographic_signature"] = True
            if not isinstance(pack_hash, str) or not _HEX64.match(pack_hash):
                raise GatePayloadInvalid({"field": "pack_hash", "reason": "the sha256 pack_hash of the pack that was read is required"})
            ev_type = EVENT_TYPE[zh]
        else:
            system = _text(payload.get("system"), "system", 200)
            reference = _text(payload.get("reference"), "reference", 500)
            if not system or not reference:
                raise GateExtrefInvalid({"missing": [k for k, v in (("system", system), ("reference", reference)) if not v]})
            body = {"zone_h_action": zh, "system": system, "reference": reference,
                    "uri": _text(payload.get("uri"), "uri", 1000) or None,
                    "decided_at": _text(payload.get("decided_at"), "decided_at", 64) or None,
                    "decided_by_declared": _text(payload.get("decided_by_declared"), "decided_by_declared", 200) or None,
                    "entered_by": sess.principal.principal_id, "verified": False}
            basis, ev_type = "", "DISPOSITION_REFERENCED"
            if pack_hash is not None and (not isinstance(pack_hash, str) or not _HEX64.match(pack_hash)):
                raise GatePayloadInvalid({"field": "pack_hash", "reason": "must be a sha256 hex string when given"})
        p = sess.principal
        try:
            return self._store_disposition(sess, p, zh, case_id, ev_type, basis, refs, body, m, pack_hash, holder_audit_seq, correlation_id, payload)
        except GatePackStale as e:
            self._refuse(sess, zh, case_id, e, correlation_id)

    def _store_disposition(self, sess, p, zh, case_id, ev_type, basis, refs, body, m, pack_hash, holder_audit_seq, correlation_id, payload):
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind, action=ev_type,
                          outcome="success", correlation_id=correlation_id, object_ref="case:%s" % case_id[:40], details={}) as ctx:
            head = self._head(case_id)
            if head is None:
                raise CaseNotFound({"case_id": case_id[:40]})
            if pack_hash is not None and pack.current_hash(self.con, case_id) != pack_hash:
                raise GatePackStale({"case_id": case_id, "hint": "GET the evidence pack again"})
            if refs:
                have = self._existing_refs(refs)
                missing = [r for r in refs if r not in have]
                if missing:
                    raise EvidenceUnresolved({"missing": missing[:20]})
            now = self.clock()
            occ = self._check_time(None, now, head)
            body["pack_hash"] = pack_hash
            body["authority_ref"] = _text(payload.get("authority_ref"), "authority_ref", 500) or None
            ev = self._insert_event(case_id, ev_type, p.principal_id, "human", occ, now, basis, evidence_refs=refs, cycle=head[4],
                                    mode_at_write=m["mode"], holder_check_ref="audit:%d" % holder_audit_seq, payload=body)
            ctx.fields["details"] = {"case_id": case_id, "event_id": ev["event_id"], "seq": ev["seq"], "event_type": ev_type, "zh": zh,
                                     "mode_at_write": m["mode"], "event_hash": ev["hash"]}
        return {"action": zh, "event_ref": ev["event_id"], "mode_at_write": m["mode"], "audit_seq": ctx.record["audit_seq"]}

    # ------------------------------------------------------------------ OP-GATE-04
    def act_on_flag(self, sess, flag_id, action, reason, replacement=None, correlation_id="gate"):
        """Override, dismiss or refuse a rule-generated item. The system never blocks it except for a missing reason or authentication."""
        require_trusted([flag_id, action], "act_on_flag")
        if sess is None:
            raise AuthUnauthenticated()
        p = self._need_roles(sess, FLAG_ROLES, correlation_id, "OP-GATE-04")
        if action not in flags.ACTIONS:
            raise GatePayloadInvalid({"field": "action", "allowed": list(flags.ACTIONS)})
        text = reason.for_storage() if isinstance(reason, Untrusted) else reason
        text = text.strip() if isinstance(text, str) else ""
        if not text:
            raise GateReasonRequired({"field": "reason"})
        if len(text) > TEXT_MAX:
            raise FieldTooLong({"field": "reason", "length": len(text), "limit": TEXT_MAX})
        repl = None
        if replacement is not None:
            repl = canonical(replacement)
            if len(repl) > TEXT_MAX:
                raise FieldTooLong({"field": "replacement", "length": len(repl), "limit": TEXT_MAX})
        f = flags.resolve(self.con, flag_id)
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                          action="FLAG_" + action.upper(), outcome="success", correlation_id=correlation_id,
                          object_ref="flag:" + flag_id, details={}) as ctx:
            now = self.clock()
            event_id, case_id = None, f.get("case_id")
            if case_id is not None:
                head = self._head(case_id)
                if head is not None:
                    occ = self._check_time(None, now, head)
                    ev = self._insert_event(case_id, "OVERRIDE_RECORDED", p.principal_id, "human", occ, now, text, cycle=head[4],
                                            payload={"flag_id": flag_id, "action": action, "flag_kind": f["flag_kind"],
                                                     "replacement": None if replacement is None else json.loads(repl)})
                    event_id = ev["event_id"]
                else:
                    case_id = None
            aid = "FA-%08d" % (self.con.execute("SELECT count(*) FROM flag_action").fetchone()[0] + 1)
            self.con.execute("INSERT INTO flag_action(action_id, flag_id, flag_kind, action, reason, replacement, actor, actor_kind, acted_at,"
                             " case_id, event_id) VALUES (?,?,?,?,?,?,?,'human',?,?,?)",
                             (aid, flag_id, f["flag_kind"], action, text, repl, p.principal_id, now, case_id, event_id))
            ctx.fields["details"] = {"flag_id": flag_id, "action_id": aid, "flag_action": action, "event_id": event_id, "case_id": case_id}
        return {"event_id": event_id or aid, "action_id": aid, "flag_id": flag_id, "action": action, "original_output_retained": True,
                "flag_status": pack.flag_status(self.con, flag_id)}
