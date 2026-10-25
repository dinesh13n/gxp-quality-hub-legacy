"""DecisionService: the append-only decision and evidence record (C3, F01, ADR-004, ADR-005, DR-22).

* Every state change, fact and evidence attachment is ONE new row in `decision_events` (per-case gapless `seq`, per-case
  hash chain). The service has no update or delete method; SQLite triggers reject UPDATE / DELETE (E-DEC-IMMUTABLE).
* Each append is one transaction with its `case_state` projection row and its hash-chained audit record
  (`audit.change`): if the audit insert fails the event is rolled back (BEH-DEC-11, AC-DEC-24).
* Humans decide: no method judges evidence sufficiency (OD-S12-07) or labels a case 'closed' from a fact event. A closing
  transition needs >= 1 existing evidence reference OR a close_exception, which is the Zone H action ZH-04 and goes through
  the shared gate (hub.gate). Free text (basis, notes) is typed Untrusted: stored verbatim, escaped on output, never parsed.
"""
import datetime
import html
import json
import re
import sqlite3

from hub.core.untrusted import Untrusted, require_trusted
from hub.decision import access, schema, settings as dsettings
from hub.decision.errors import (CaseExists, CaseIdInvalid, CaseNotFound, ChainBroken, CreationDisabled, EvidenceRequired,
                                 EvidenceUnresolved, FactInvalid, FieldTooLong, IdempotencyMismatch, Immutable, NoOp,
                                 NotYetExists, ReopenExplicit, SeqConflict, StateUnknown, TimeOrder, TransitionNotAllowed)
from hub.policy import withdrawal
from hub.security import audit
from hub.security.canonical import GENESIS, canonical, fmt, parse, sha256_hex
from hub.security.errors import AuthForbidden, AuthUnauthenticated

BASIS_MAX = 2000
TEXT_MAX = 1000
STATE_ROLES = ("reviewer", "quality_lead", "compliance")
READ_ROLES = STATE_ROLES + ("dispositioner",)
FACT_TYPES = ("FACT_OPS_CLOSED", "FACT_EVIDENCE_COMPLETE")
EVIDENCE_KINDS = ("document", "intake_item", "crosswalk_object", "external_ref")
LEGACY_REOPEN_MARKER = "LEGACY_UNEVIDENCED_REOPEN"
WITHHELD_BASIS = "[withheld: the note of restricted evidence is not readable with your role]"  # Stage 27 S26-F-02
_CASE_ID = re.compile(r"^C[0-9]{8}$")
_REF = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")
COLS = ("event_id", "case_id", "seq", "event_type", "from_state", "to_state", "affects_state", "actor", "actor_kind",
        "occurred_at", "recorded_at", "basis", "evidence_refs", "cycle", "exception", "closure_check", "mode_at_write",
        "policy_version", "holder_check_ref", "payload", "prev_hash", "hash")
_HASHED = tuple(c for c in COLS if c not in ("prev_hash", "hash"))
_TS_FORMATS = ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z")


def norm_ts(value, field="occurred_at"):
    """Normalise an ISO-8601 UTC timestamp to the canonical hub form; anything else -> E-DEC-TIME-ORDER."""
    if not isinstance(value, str):
        raise TimeOrder({"field": field, "reason": "not a string"})
    for f in _TS_FORMATS:
        try:
            dt = datetime.datetime.strptime(value, f)
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return fmt(dt)
    raise TimeOrder({"field": field, "reason": "not an ISO-8601 UTC timestamp"})


def _decode(row):
    e = dict(zip(COLS, row))
    e["affects_state"] = bool(e["affects_state"])
    e["exception"] = bool(e["exception"])
    e["evidence_refs"] = json.loads(e["evidence_refs"])
    e["payload"] = json.loads(e["payload"])
    return e


def event_hash(prev_hash, ev):
    return sha256_hex(prev_hash + canonical({k: ev[k] for k in _HASHED}))


def fold(events):
    """Pure fold of one case's events (ordered by seq): {state, cycle, last_seq, updated_from_event} or None."""
    state, cycle, last = None, 1, None
    for e in events:
        if e["affects_state"]:
            state = e["to_state"]
        if e["event_type"] == "REOPEN":
            cycle += 1
        last = e
    if last is None:
        return None
    return {"state": state, "cycle": cycle, "last_seq": last["seq"], "updated_from_event": last["event_id"]}


def view(event):
    """Wire/display form of an event: free text positions carry {text, trust: untrusted} plus an escaped copy (BEH-DEC-12)."""
    out = dict(event)
    out["basis"] = Untrusted(event["basis"], source="decision_events.basis").to_wire()
    out["basis_escaped"] = html.escape(event["basis"], quote=True)
    out["payload_escaped"] = html.escape(canonical(event["payload"]), quote=True)
    return out


class DecisionService(object):
    def __init__(self, con, s, clock, anchor=None, d=None):
        """s = security settings (hub.security.settings.resolve), d = decision settings (hub.decision.settings.resolve)."""
        self.con, self.s, self.clock, self.anchor = con, s, clock, anchor
        self.d = d if d is not None else dsettings.resolve({})
        schema.require(con)
        from hub.gate.service import GateService  # function-level since Stage 27: breaks the decision <-> gate package cycle (OD-27 debt)
        self.gate = GateService(con, s, clock, anchor)

    # ------------------------------------------------------------------ helpers
    def _deny(self, sess, op, cid, roles):
        p = sess.principal
        audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                     action="AUTHZ_DENIED", outcome="denied", correlation_id=cid, object_ref=op,
                     details={"reason": "role", "needs_one_of": list(roles)})
        raise AuthForbidden({"reason": "role"})

    def _need_roles(self, sess, roles, cid, op):
        if sess is None:
            raise AuthUnauthenticated()
        p = sess.principal
        if p.kind == "human" and any(r in p.roles for r in roles):
            return p
        self._deny(sess, op, cid, roles)

    @staticmethod
    def _text(value, field, limit):
        if isinstance(value, Untrusted):
            value = value.for_storage()
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise FieldTooLong({"field": field, "reason": "not text"})
        if len(value) > limit:
            raise FieldTooLong({"field": field, "length": len(value), "limit": limit})
        return value

    def _refs(self, refs):
        refs = [] if refs is None else refs
        if not isinstance(refs, (list, tuple)) or len(refs) > 100:
            raise EvidenceUnresolved({"reason": "evidence_refs must be a list of at most 100 ids"})
        out = []
        for r in refs:
            if not isinstance(r, str) or not _REF.match(r):
                raise EvidenceUnresolved({"reason": "malformed evidence id", "ev_id": str(r)[:80]})
            if r not in out:
                out.append(r)
        return out

    def _existing_refs(self, refs):
        if not refs:
            return set()
        q = "SELECT ev_id FROM evidence_record WHERE ev_id IN (%s)" % ",".join("?" * len(refs))
        return set(r[0] for r in self.con.execute(q, refs))

    def _head(self, case_id):
        """(seq, hash, event_id, occurred_at, cycle) of the case's last event, or None."""
        return self.con.execute("SELECT seq, hash, event_id, occurred_at, cycle FROM decision_events WHERE case_id = ?"
                                " ORDER BY seq DESC LIMIT 1", (case_id,)).fetchone()

    def _state_of(self, case_id):
        r = self.con.execute("SELECT to_state FROM decision_events WHERE case_id = ? AND affects_state = 1 ORDER BY seq DESC LIMIT 1",
                             (case_id,)).fetchone()
        return r[0] if r else None

    def _next_event_id(self):
        return "EV-%08d" % (self.con.execute("SELECT count(*) FROM decision_events").fetchone()[0] + 1)

    def _insert_event(self, case_id, event_type, actor, actor_kind, occurred_at, recorded_at, basis, to_state=None, from_state=None,
                      affects_state=False, evidence_refs=None, cycle=1, exception=False, closure_check=None, mode_at_write=None,
                      policy_version=None, holder_check_ref=None, payload=None):
        """Insert one event (must run inside an open transaction): seq, hash chain, row, projection. Returns the decoded event."""
        head = self._head(case_id)
        seq = 1 if head is None else head[0] + 1
        prev = GENESIS if head is None else head[1]
        ev = {"event_id": self._next_event_id(), "case_id": case_id, "seq": seq, "event_type": event_type, "from_state": from_state,
              "to_state": to_state, "affects_state": bool(affects_state), "actor": actor, "actor_kind": actor_kind,
              "occurred_at": occurred_at, "recorded_at": recorded_at, "basis": basis, "evidence_refs": list(evidence_refs or []),
              "cycle": cycle, "exception": bool(exception), "closure_check": closure_check, "mode_at_write": mode_at_write,
              "policy_version": policy_version, "holder_check_ref": holder_check_ref, "payload": payload or {}}
        h = event_hash(prev, ev)
        try:
            self.con.execute("INSERT INTO decision_events(" + ", ".join(COLS) + ") VALUES (" + ",".join("?" * len(COLS)) + ")",
                             (ev["event_id"], case_id, seq, event_type, from_state, to_state, int(ev["affects_state"]), actor,
                              actor_kind, occurred_at, recorded_at, basis, canonical(ev["evidence_refs"]), cycle,
                              int(ev["exception"]), closure_check, mode_at_write, policy_version, holder_check_ref,
                              canonical(ev["payload"]), prev, h))
        except sqlite3.IntegrityError as e:
            self._map_integrity(e)
            raise
        ev["prev_hash"], ev["hash"] = prev, h
        state = to_state if affects_state else self._state_of(case_id)
        self.con.execute("INSERT OR REPLACE INTO case_state(case_id, state, cycle, last_seq, updated_from_event) VALUES (?,?,?,?,?)",
                         (case_id, state, cycle, seq, ev["event_id"]))
        return ev

    @staticmethod
    def _map_integrity(e):
        msg = str(e)
        if "E-DEC-SEQ-CONFLICT" in msg:
            raise SeqConflict({"reason": "seq is not the next gapless value"})
        if "E-DEC-IMMUTABLE" in msg:
            raise Immutable()
        if "E-GATE-NOT-AUTHORISED" in msg:
            from hub.gate.errors import GateNotAuthorised  # function-level (cycle debt, Stage 27)
            raise GateNotAuthorised({"reason": "database trigger: Zone H event needs a human actor and a holder_check_ref"})

    def _idem_replay(self, key, body_hash):
        if key is None:
            return None
        if not isinstance(key, str) or not _REF.match(key):
            raise IdempotencyMismatch({"reason": "malformed Idempotency-Key"})
        row = self.con.execute("SELECT body_hash, event_id FROM decision_idempotency WHERE idem_key = ?", (key,)).fetchone()
        if row is None:
            return None
        if row[0] != body_hash:
            raise IdempotencyMismatch({"idempotency_key": key})
        ev = self._get_event(row[1])
        ev["replayed"] = True
        return ev

    def _idem_store(self, key, body_hash, event_id):
        if key is not None:
            self.con.execute("INSERT INTO decision_idempotency(idem_key, body_hash, event_id, created_at) VALUES (?,?,?,?)",
                             (key, body_hash, event_id, self.clock()))

    def _get_event(self, event_id):
        row = self.con.execute("SELECT " + ", ".join(COLS) + " FROM decision_events WHERE event_id = ?", (event_id,)).fetchone()
        return None if row is None else _decode(row)

    def _check_time(self, occurred_at, recorded_at, head):
        occ = recorded_at if occurred_at is None else norm_ts(occurred_at)
        if occ > recorded_at:
            raise TimeOrder({"reason": "occurred_at is after recorded_at"})
        if head is not None and occ < head[3]:
            raise TimeOrder({"reason": "occurred_at is before the previous event of the case"})
        return occ

    # ------------------------------------------------------------------ closing-state set (SBR-DEC-03)
    def closing_set(self):
        """({closing states}, mode, policy_ref): mode 'policy' | 'label' | 'none'."""
        today = self.clock()[:10]
        rows = self.con.execute(
            "SELECT policy_id, version, body, effective_from, effective_to FROM policy_object WHERE kind = 'CLOSURE'"
            " AND status IN ('adopted','accepted-open') ORDER BY created_at DESC, version DESC").fetchall()
        for pid, ver, body, ef, et in rows:
            if (ef is not None and ef > today) or (et is not None and et < today):
                continue
            if withdrawal.effective(self.con, "%s@%d" % (pid, ver), self.clock()):  # Stage 20 DW-07
                continue
            cs = json.loads(body).get("closing_states")
            if isinstance(cs, list) and cs and all(x in dsettings.VOCAB for x in cs):
                return set(cs), "policy", "%s@%d" % (pid, ver)
        if self.d["closure"]["unconfigured_behaviour"] == "treat_label_CLOSED_as_closing":
            return set([dsettings.CLOSING_LABEL]), "label", None
        return set(), "none", None

    # ------------------------------------------------------------------ writes
    def create_case(self, sess, case_id, to_state="OPEN", basis="", occurred_at=None, received_at=None, correlation_id="decision"):
        """CASE_CREATED (+ FACT_RECEIVED when received_at is given). R1 creation path = legacy backfill only (OD-S12-19):
        refused unless case_creation.enabled."""
        require_trusted([case_id, to_state], "create_case")
        if not self.d["case_creation"]["enabled"]:
            raise CreationDisabled()
        p = self._need_roles(sess, STATE_ROLES, correlation_id, "OP-DEC-CREATE")
        if not isinstance(case_id, str) or not _CASE_ID.match(case_id):
            raise CaseIdInvalid({"case_id": str(case_id)[:40]})
        if to_state not in dsettings.VOCAB:
            raise StateUnknown({"state": str(to_state)[:40], "vocabulary": list(dsettings.VOCAB)})
        basis = self._text(basis, "basis", BASIS_MAX)
        out = []
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                          action="DECISION_APPENDED", outcome="success", correlation_id=correlation_id,
                          object_ref="case:" + case_id, details={}) as ctx:
            if self._head(case_id) is not None:
                raise CaseExists({"case_id": case_id})
            now = self.clock()
            occ = self._check_time(occurred_at, now, None)
            out.append(self._insert_event(case_id, "CASE_CREATED", p.principal_id, "human", occ, now, basis, to_state=to_state,
                                          from_state=None, affects_state=True))
            if received_at is not None:
                rec = norm_ts(received_at, "received_at")
                if rec > now:
                    raise TimeOrder({"reason": "received_at is after recorded_at"})
                if rec < occ:
                    raise TimeOrder({"reason": "received_at is before the creation event"})
                out.append(self._insert_event(case_id, "FACT_RECEIVED", p.principal_id, "human", rec, now, "", cycle=1))
            ctx.fields["details"] = {"case_id": case_id, "events": [e["event_id"] for e in out], "event_type": "CASE_CREATED",
                                     "to_state": to_state, "event_hash": out[-1]["hash"]}
        return out[0]

    def transition(self, sess, case_id, to_state=None, basis="", event_type="STATUS_CHANGE", evidence_refs=None, expected_seq=None,
                   idempotency_key=None, occurred_at=None, close_exception=None, correlation_id="decision"):
        """OP-DEC-01. Append a state-changing event. With `close_exception` ({actor?, authority, reason}) the call is the Zone H
        action ZH-04 (human holder, step-up re-authentication); otherwise roles reviewer / quality_lead / compliance."""
        require_trusted([case_id, to_state, event_type, expected_seq, idempotency_key], "transition")
        if event_type not in ("STATUS_CHANGE", "REOPEN"):
            raise StateUnknown({"event_type": str(event_type)[:40], "allowed": ["STATUS_CHANGE", "REOPEN"]})
        if event_type == "REOPEN" and to_state is None:
            to_state = dsettings.REOPENED_LABEL
        basis = self._text(basis, "basis", BASIS_MAX)
        refs = self._refs(evidence_refs)
        exc = None
        if close_exception is not None:
            if not isinstance(close_exception, dict):
                raise EvidenceRequired({"reason": "close_exception must be an object {actor, authority, reason}"})
            exc = {"authority": self._text(close_exception.get("authority"), "authority", TEXT_MAX).strip(),
                   "reason": self._text(close_exception.get("reason"), "reason", TEXT_MAX).strip()}
            if not exc["authority"] or not exc["reason"]:
                raise EvidenceRequired({"reason": "close_exception needs a non-empty authority and reason"})
            if event_type != "STATUS_CHANGE":
                raise TransitionNotAllowed({"reason": "close_exception applies to a STATUS_CHANGE only"})
        body_hash = sha256_hex(canonical({"op": "transition", "case_id": case_id, "to_state": to_state, "event_type": event_type,
                                          "basis": basis, "evidence_refs": refs, "occurred_at": occurred_at,
                                          "close_exception": exc, "actor": sess.principal.principal_id if sess else None}))
        hcr, p = None, None
        if exc is not None:
            hcr = "audit:%d" % self.gate.require_holder(sess, "ZH-04", correlation_id, "case:%s" % case_id)
            p = sess.principal
            declared = close_exception.get("actor")
            if declared is not None and declared != p.principal_id:
                from hub.gate.errors import GateNotAuthorised  # function-level (cycle debt, Stage 27)
                raise GateNotAuthorised({"reason": "close_exception actor differs from the authenticated holder"})
            exc["actor"] = p.principal_id
        else:
            p = self._need_roles(sess, STATE_ROLES, correlation_id, "OP-DEC-01")
        replay = self._idem_replay(idempotency_key, body_hash)
        if replay is not None:
            return replay
        out = []
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                          action="DECISION_APPENDED", outcome="success", correlation_id=correlation_id,
                          object_ref="case:%s" % case_id, details={}) as ctx:
            head = self._head(case_id)
            if head is None:
                raise CaseNotFound({"case_id": str(case_id)[:40]})
            if expected_seq is not None and (isinstance(expected_seq, bool) or expected_seq != head[0]):
                raise SeqConflict({"expected_seq": expected_seq, "current_seq": head[0]})
            if to_state not in dsettings.VOCAB:
                raise StateUnknown({"state": str(to_state)[:40], "vocabulary": list(dsettings.VOCAB)})
            cur = self._state_of(case_id)
            if event_type == "REOPEN":
                if to_state != dsettings.REOPENED_LABEL or not basis.strip():
                    raise ReopenExplicit({"reason": "REOPEN needs to_state REOPENED and a non-empty basis"})
            elif to_state == dsettings.REOPENED_LABEL:
                raise ReopenExplicit({"reason": "use event_type REOPEN with a basis"})
            if to_state == cur:
                raise NoOp({"state": cur})
            if self.d["workflow"]["transition_table"] == "strict" and to_state not in self.d["workflow"]["transitions"].get(cur, []):
                raise TransitionNotAllowed({"from": cur, "to": to_state})
            now = self.clock()
            occ = self._check_time(occurred_at, now, head)
            closing, mode, pol = self.closing_set()
            closure_check, ev_type, exception = None, event_type, False
            if to_state in closing:
                if refs:
                    have = self._existing_refs(refs)
                    missing = [r for r in refs if r not in have]
                    if missing:
                        raise EvidenceUnresolved({"missing": missing[:20]})
                if exc is not None:
                    closure_check, ev_type, exception = "exception", "CLOSE_EXCEPTION", True
                elif refs:
                    closure_check = "passed"
                else:
                    raise EvidenceRequired({"to_state": to_state, "closing_set_mode": mode})
            elif exc is not None:
                raise TransitionNotAllowed({"reason": "close_exception applies to a transition into a closing state only",
                                            "to_state": to_state})
            elif mode == "none" and to_state == dsettings.CLOSING_LABEL:
                closure_check = "not_configured"
            cycle = head[4] + (1 if event_type == "REOPEN" else 0)
            payload = {"authority": exc["authority"], "reason": exc["reason"], "actor": exc["actor"]} if exc is not None else {}
            ev = self._insert_event(case_id, ev_type, p.principal_id, "human", occ, now, basis, to_state=to_state, from_state=cur,
                                    affects_state=True, evidence_refs=refs, cycle=cycle, exception=exception,
                                    closure_check=closure_check, policy_version=pol if to_state in closing else None,
                                    holder_check_ref=hcr, payload=payload)
            self._idem_store(idempotency_key, body_hash, ev["event_id"])
            out.append(ev)
            ctx.fields["details"] = {"case_id": case_id, "event_id": ev["event_id"], "seq": ev["seq"], "event_type": ev_type,
                                     "from_state": cur, "to_state": to_state, "closure_check": closure_check,
                                     "exception": exception, "event_hash": ev["hash"]}
        return out[0]

    def record_fact(self, sess, case_id, fact_type, occurred_at=None, note="", expected_seq=None, idempotency_key=None,
                    correlation_id="decision"):
        """OP-DEC-05. FACT_OPS_CLOSED / FACT_EVIDENCE_COMPLETE: human roles only (OD-S12-15 default). Never changes state."""
        require_trusted([case_id, fact_type, expected_seq, idempotency_key], "record_fact")
        if fact_type not in FACT_TYPES:
            raise FactInvalid({"fact_type": str(fact_type)[:40], "allowed": list(FACT_TYPES)})
        note = self._text(note, "note", BASIS_MAX)
        p = self._need_roles(sess, STATE_ROLES, correlation_id, "OP-DEC-05")
        body_hash = sha256_hex(canonical({"op": "fact", "case_id": case_id, "fact_type": fact_type, "note": note,
                                          "occurred_at": occurred_at, "actor": p.principal_id}))
        replay = self._idem_replay(idempotency_key, body_hash)
        if replay is not None:
            return replay
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                          action="DECISION_APPENDED", outcome="success", correlation_id=correlation_id,
                          object_ref="case:%s" % case_id, details={}) as ctx:
            head = self._head(case_id)
            if head is None:
                raise CaseNotFound({"case_id": str(case_id)[:40]})
            if expected_seq is not None and (isinstance(expected_seq, bool) or expected_seq != head[0]):
                raise SeqConflict({"expected_seq": expected_seq, "current_seq": head[0]})
            now = self.clock()
            occ = self._check_time(occurred_at, now, head)
            ev = self._insert_event(case_id, fact_type, p.principal_id, "human", occ, now, note, cycle=head[4])
            self._idem_store(idempotency_key, body_hash, ev["event_id"])
            ctx.fields["details"] = {"case_id": case_id, "event_id": ev["event_id"], "seq": ev["seq"], "event_type": fact_type,
                                     "event_hash": ev["hash"]}
        return ev

    def attach_evidence(self, sess, case_id, kind, source, source_ref, source_hash=None, access_level="restricted", note="",
                        idempotency_key=None, correlation_id="decision"):
        """OP-DEC-06. Creates an immutable evidence record and its EVIDENCE_ATTACHED event (affects_state false)."""
        require_trusted([case_id, kind, access_level, idempotency_key], "attach_evidence")
        if kind not in EVIDENCE_KINDS or access_level not in access.LEVELS:
            raise FieldTooLong({"reason": "kind or access_level not in the allowed set", "kinds": list(EVIDENCE_KINDS),
                                "levels": list(access.LEVELS)})
        source = self._text(source, "source", TEXT_MAX)
        source_ref = self._text(source_ref, "source_ref", TEXT_MAX)
        if not source or not source_ref:
            raise FieldTooLong({"reason": "source and source_ref are required"})
        if source_hash is not None and not (isinstance(source_hash, str) and re.match(r"^[0-9a-f]{64}$", source_hash)):
            raise FieldTooLong({"reason": "source_hash must be a sha256 hex string"})
        note = self._text(note, "note", BASIS_MAX)
        p = self._need_roles(sess, STATE_ROLES, correlation_id, "OP-DEC-06")
        body_hash = sha256_hex(canonical({"op": "evidence", "case_id": case_id, "kind": kind, "source": source,
                                          "source_ref": source_ref, "source_hash": source_hash, "access_level": access_level,
                                          "note": note, "actor": p.principal_id}))
        replay = self._idem_replay(idempotency_key, body_hash)
        if replay is not None:
            return replay
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                          action="DECISION_APPENDED", outcome="success", correlation_id=correlation_id,
                          object_ref="case:%s" % case_id, details={}) as ctx:
            head = self._head(case_id)
            if head is None:
                raise CaseNotFound({"case_id": str(case_id)[:40]})
            now = self.clock()
            ev_id = "EVD-%08d" % (self.con.execute("SELECT count(*) FROM evidence_record").fetchone()[0] + 1)
            self.con.execute("INSERT INTO evidence_record(ev_id, kind, source, source_ref, source_hash, access_level, attached_by,"
                             " attached_at) VALUES (?,?,?,?,?,?,?,?)", (ev_id, kind, source, source_ref, source_hash, access_level,
                                                                     p.principal_id, now))
            occ = self._check_time(None, now, head)
            ev = self._insert_event(case_id, "EVIDENCE_ATTACHED", p.principal_id, "human", occ, now, note, cycle=head[4],
                                    payload={"ev_id": ev_id})
            self._idem_store(idempotency_key, body_hash, ev["event_id"])
            ev["evidence"] = {"ev_id": ev_id, "kind": kind, "access_level": access_level}
            ctx.fields["details"] = {"case_id": case_id, "event_id": ev["event_id"], "seq": ev["seq"],
                                     "event_type": "EVIDENCE_ATTACHED", "ev_id": ev_id, "event_hash": ev["hash"]}
        return ev

    # ------------------------------------------------------------------ reads
    def events(self, sess, case_id, after_seq=0, limit=100, correlation_id="decision"):
        """OP-DEC-02: events of a case in seq order (cursor = after_seq, limit <= 100)."""
        self._need_roles(sess, READ_ROLES, correlation_id, "OP-DEC-02")
        limit = max(1, min(int(limit), 100))
        if self._head(case_id) is None:
            raise CaseNotFound({"case_id": str(case_id)[:40]})
        rows = self.con.execute("SELECT " + ", ".join(COLS) + " FROM decision_events WHERE case_id = ? AND seq > ? ORDER BY seq LIMIT ?",
                                (case_id, int(after_seq), limit)).fetchall()
        return [self._withhold_note(sess, _decode(r)) for r in rows]

    def _withhold_note(self, sess, ev):
        """Stage 27 S26-F-02 (assumption A-27-02, safest default): the free-text note of an EVIDENCE_ATTACHED event is the `basis` of that event, so the
        access rule of the evidence record (AC-DEC-13) must also cover it. A reader whose roles may not read the record's level gets the fixed placeholder
        and basis_withheld = true; the stored row, its hash and the chain are unchanged (verify_chain still passes). An event whose record can not be
        resolved is withheld too (fail closed). Every other event type is returned as stored."""
        if ev["event_type"] != "EVIDENCE_ATTACHED":
            return ev
        row = self.con.execute("SELECT access_level FROM evidence_record WHERE ev_id = ?", (ev["payload"].get("ev_id"),)).fetchone()
        if row is not None and access.can_read(sess.principal.roles, row[0]):
            return ev
        return dict(ev, basis=WITHHELD_BASIS, basis_withheld=True)

    def all_events(self, case_id):
        """Internal / report use: every event of a case, ordered (no role check)."""
        rows = self.con.execute("SELECT " + ", ".join(COLS) + " FROM decision_events WHERE case_id = ? ORDER BY seq", (case_id,)).fetchall()
        return [_decode(r) for r in rows]

    def state(self, sess, case_id, as_of=None, correlation_id="decision"):
        """OP-DEC-03: current state, or the state from the last state-affecting event with occurred_at <= as_of (ties by seq)."""
        self._need_roles(sess, READ_ROLES, correlation_id, "OP-DEC-03")
        if self._head(case_id) is None:
            raise CaseNotFound({"case_id": str(case_id)[:40]})
        if as_of is None:
            r = self.con.execute("SELECT state, cycle, last_seq, updated_from_event FROM case_state WHERE case_id = ?", (case_id,)).fetchone()
            ev = self._get_event(r[3])
            src = self.con.execute("SELECT event_id, event_type FROM decision_events WHERE case_id = ? AND affects_state = 1"
                                   " ORDER BY seq DESC LIMIT 1", (case_id,)).fetchone()
            return {"case_id": case_id, "state": r[0], "cycle": r[1], "last_seq": r[2], "as_of": None,
                    "source_event": src[0], "source_event_type": src[1], "last_event": ev["event_id"]}
        t = norm_ts(as_of, "as_of")
        row = self.con.execute("SELECT event_id, event_type, to_state, seq, cycle FROM decision_events WHERE case_id = ? AND"
                               " affects_state = 1 AND occurred_at <= ? ORDER BY occurred_at DESC, seq DESC LIMIT 1",
                               (case_id, t)).fetchone()
        if row is None:
            raise NotYetExists({"case_id": case_id, "as_of": t})
        cyc = 1 + self.con.execute("SELECT count(*) FROM decision_events WHERE case_id = ? AND event_type = 'REOPEN' AND seq <= ?",
                                   (case_id, row[3])).fetchone()[0]
        return {"case_id": case_id, "state": row[2], "cycle": cyc, "last_seq": row[3], "as_of": t, "source_event": row[0],
                "source_event_type": row[1]}

    def event_with_evidence(self, sess, event_id, correlation_id="decision"):
        """OP-DEC-04: one event + each referenced evidence record resolved. A reference that cannot be resolved is flagged
        `unresolvable` (never omitted); evidence the caller may not read is the placeholder {ev_id, access: denied}."""
        self._need_roles(sess, READ_ROLES, correlation_id, "OP-DEC-04")
        ev = self._get_event(event_id)
        if ev is None:
            raise CaseNotFound({"event_id": str(event_id)[:40]})
        ev = self._withhold_note(sess, ev)  # Stage 27 S26-F-02
        refs = list(ev["evidence_refs"])
        if ev["event_type"] == "EVIDENCE_ATTACHED" and ev["payload"].get("ev_id") not in refs:
            refs.append(ev["payload"]["ev_id"])
        out = []
        for r in refs:
            row = self.con.execute("SELECT ev_id, kind, source, source_ref, source_hash, access_level, attached_by, attached_at"
                                   " FROM evidence_record WHERE ev_id = ?", (r,)).fetchone()
            if row is None:
                out.append({"ev_id": r, "unresolvable": True})
            elif not access.can_read(sess.principal.roles, row[5]):
                out.append({"ev_id": r, "access": "denied"})
            else:
                out.append({"ev_id": row[0], "kind": row[1], "source": Untrusted(row[2], "evidence").to_wire(),
                            "source_ref": Untrusted(row[3], "evidence").to_wire(), "source_hash": row[4],
                            "access_level": row[5], "attached_by": row[6], "attached_at": row[7]})
        return {"event": view(ev), "evidence": out}

    def exception_report(self, sess, correlation_id="decision"):
        """Cases closed through an accepted close_exception (AC-DEC-18)."""
        self._need_roles(sess, READ_ROLES, correlation_id, "OP-DEC-EXCEPTIONS")
        rows = self.con.execute("SELECT event_id, case_id, seq, actor, occurred_at, payload, holder_check_ref FROM decision_events"
                                " WHERE exception = 1 ORDER BY event_id").fetchall()
        return [{"event_id": r[0], "case_id": r[1], "seq": r[2], "actor": r[3], "occurred_at": r[4],
                 "authority": json.loads(r[5]).get("authority"), "reason": json.loads(r[5]).get("reason"),
                 "holder_check_ref": r[6]} for r in rows]

    def evidence_coverage(self, sess, event_ids=None, correlation_id="decision"):
        """AC-DEC-14: for decision events that entered a closing state (closure_check passed / exception): evidence AND source
        retrievable, or an explicit exception marker. Events checked: `event_ids` or all of them."""
        self._need_roles(sess, READ_ROLES, correlation_id, "OP-DEC-COVERAGE")
        q = "SELECT event_id FROM decision_events WHERE closure_check IN ('passed','exception')"
        ids = [r[0] for r in self.con.execute(q + " ORDER BY event_id")]
        if event_ids is not None:
            ids = [i for i in ids if i in set(event_ids)]
        covered, exception, uncovered = [], [], []
        for i in ids:
            ev = self._get_event(i)
            if ev["exception"]:
                exception.append(i)
                continue
            ok = bool(ev["evidence_refs"]) and all(
                self.con.execute("SELECT source, source_ref FROM evidence_record WHERE ev_id = ?", (r,)).fetchone() is not None
                for r in ev["evidence_refs"])
            (covered if ok else uncovered).append(i)
        n = len(ids)
        return {"events": n, "covered": covered, "exception_marked": exception, "uncovered": uncovered,
                "coverage_pct": 100.0 if n == 0 else round(100.0 * (len(covered) + len(exception)) / n, 2)}

    def fact_timeline(self, sess, case_id, correlation_id="decision"):
        """FR-DEC-06: the three facts per cycle and the two elapsed times they allow (hours). Facts never change state and
        nothing here says a case is 'closed'."""
        self._need_roles(sess, READ_ROLES, correlation_id, "OP-DEC-FACTS")
        evs = self.all_events(case_id)
        if not evs:
            raise CaseNotFound({"case_id": str(case_id)[:40]})
        cycles = {}
        for e in evs:
            if e["event_type"] in ("FACT_RECEIVED",) + FACT_TYPES:
                cycles.setdefault(e["cycle"], {})[e["event_type"]] = e["occurred_at"]
        out = []
        for c in sorted(cycles):
            f = cycles[c]
            row = {"cycle": c, "received_at": f.get("FACT_RECEIVED"), "ops_fact_at": f.get("FACT_OPS_CLOSED"),
                   "evidence_fact_at": f.get("FACT_EVIDENCE_COMPLETE")}
            for key, src in (("elapsed_hours_to_ops_fact", "FACT_OPS_CLOSED"), ("elapsed_hours_to_evidence_fact", "FACT_EVIDENCE_COMPLETE")):
                row[key] = None
                if "FACT_RECEIVED" in f and src in f:
                    row[key] = round((parse(f[src]).timestamp() - parse(f["FACT_RECEIVED"]).timestamp()) / 3600.0, 6)
            out.append(row)
        return {"case_id": case_id, "state": self._state_of(case_id), "cycles": out,
                "note": "facts are recorded events only; no closure policy is adopted by this service"}

    def status_report(self, sess, correlation_id="decision"):
        """A report that lists each case's recorded state and which facts exist. It derives no 'closed' label from a fact."""
        self._need_roles(sess, READ_ROLES, correlation_id, "OP-DEC-REPORT")
        rows = self.con.execute("SELECT s.case_id, s.state, s.cycle, (SELECT group_concat(DISTINCT event_type) FROM decision_events d"
                                " WHERE d.case_id = s.case_id AND d.event_type LIKE 'FACT_%') FROM case_state s ORDER BY s.case_id").fetchall()
        cases = [{"case_id": r[0], "recorded_state": r[1], "cycle": r[2],
                  "facts_recorded": sorted(r[3].split(",")) if r[3] else []} for r in rows]
        closing, mode, pol = self.closing_set()
        return {"cases": cases, "closing_set_mode": mode, "closure_policy": pol,
                "note": "states are the recorded states; a fact event is not a closure"}

    def reopen_invariant(self, sess, correlation_id="decision"):
        """AC-DEC-11 / SBR-DEC-05: REOPENED cases with no REOPEN event, split into violations (must be empty) and the
        legacy-imported cases carrying LEGACY_UNEVIDENCED_REOPEN (listed, not hidden)."""
        self._need_roles(sess, READ_ROLES, correlation_id, "OP-DEC-INVARIANT")
        return self.reopen_invariant_internal()

    def reopen_invariant_internal(self):
        violations, marked = [], []
        for (cid,) in self.con.execute("SELECT case_id FROM case_state WHERE state = 'REOPENED' ORDER BY case_id").fetchall():
            has = self.con.execute("SELECT 1 FROM decision_events WHERE case_id = ? AND event_type = 'REOPEN'", (cid,)).fetchone()
            if has:
                continue
            imp = self.con.execute("SELECT payload FROM decision_events WHERE case_id = ? AND event_type = 'CASE_IMPORTED'", (cid,)).fetchone()
            if imp and json.loads(imp[0]).get("marker") == LEGACY_REOPEN_MARKER:
                marked.append(cid)
            else:
                violations.append(cid)
        return {"violations": violations, "violation_count": len(violations), "marked_legacy": marked, "marked_count": len(marked)}

    # ------------------------------------------------------------------ verification (read-only unless stated)
    def verify_chain(self):
        """Recompute every per-case hash chain (first prev_hash = 64 zeros)."""
        cases = events = 0
        prev_case, prev_hash, expect = None, GENESIS, 1
        for row in self.con.execute("SELECT " + ", ".join(COLS) + " FROM decision_events ORDER BY case_id, seq"):
            e = _decode(row)
            if e["case_id"] != prev_case:
                cases += 1
                prev_case, prev_hash, expect = e["case_id"], GENESIS, 1
            events += 1
            if e["seq"] != expect:
                return {"status": "broken", "kind": "seq_gap", "case_id": e["case_id"], "seq": e["seq"], "cases": cases, "events": events}
            if e["prev_hash"] != prev_hash or event_hash(prev_hash, e) != e["hash"]:
                return {"status": "broken", "kind": "hash_mismatch", "case_id": e["case_id"], "seq": e["seq"], "cases": cases,
                        "events": events}
            prev_hash, expect = e["hash"], expect + 1
        return {"status": "ok", "cases": cases, "events": events}

    def require_chain(self):
        r = self.verify_chain()
        if r["status"] != "ok":
            raise ChainBroken(r)
        return r

    def _folded(self):
        out, cur, buf = {}, None, []
        for row in self.con.execute("SELECT " + ", ".join(COLS) + " FROM decision_events ORDER BY case_id, seq"):
            e = _decode(row)
            if e["case_id"] != cur:
                if cur is not None:
                    out[cur] = fold(buf)
                cur, buf = e["case_id"], []
            buf.append(e)
        if cur is not None:
            out[cur] = fold(buf)
        return out

    def verify_projection(self):
        """AC-DEC-05: recompute every case from its events and compare with `case_state` (mismatches must be 0)."""
        folded = self._folded()
        have = dict((r[0], {"state": r[1], "cycle": r[2], "last_seq": r[3], "updated_from_event": r[4]})
                    for r in self.con.execute("SELECT case_id, state, cycle, last_seq, updated_from_event FROM case_state"))
        mismatches = []
        for cid in sorted(set(folded) | set(have)):
            if folded.get(cid) != have.get(cid):
                mismatches.append({"case_id": cid, "folded": folded.get(cid), "projection": have.get(cid)})
        return {"status": "ok" if not mismatches else "mismatch", "cases": len(folded), "projection_rows": len(have),
                "mismatches": len(mismatches), "detail": mismatches[:20]}

    def rebuild_projection(self, correlation_id="decision-rebuild"):
        """Rollback L1/L2 helper: rebuild `case_state` from the events (audited, one transaction)."""
        folded = self._folded()
        with audit.change(self.con, self.clock, anchor=self.anchor, actor="hub", actor_kind="system", action="PROJECTION_REBUILT",
                          outcome="success", correlation_id=correlation_id, object_ref="projection:case_state", details={}) as ctx:
            self.con.execute("DELETE FROM case_state")
            for cid in sorted(folded):
                f = folded[cid]
                self.con.execute("INSERT INTO case_state(case_id, state, cycle, last_seq, updated_from_event) VALUES (?,?,?,?,?)",
                                 (cid, f["state"], f["cycle"], f["last_seq"], f["updated_from_event"]))
            ctx.fields["details"] = {"cases": len(folded)}
        return {"cases": len(folded)}
