"""PolicyService: policy objects, rule sets as data, activation with a recorded human decision (F03, ADR-007).

Every state change is ONE transaction with its hash-chained audit record (hub.security.audit.change): if the audit
insert fails the change is rolled back. Every policy change also writes an immutable `policy_events` row with a
non-empty authority_ref. Actors are `Session` objects from the INC-03 authenticator (human or service).
Rules: nothing ships adopted or active; activation is refused without a valid recorded human decision (D-10).
"""
import json
import re

from hub.policy import asfound, clocks, engine, rulesets, schema
from hub.policy import gate
from hub.policy import withdrawal
from hub.policy.errors import (AsFoundDrift, AuthorityRequired, DecisionRequired, NoActiveRuleset, NotFound, Overlap,
                               PolicyInvalid, ReadonlySet, UnknownFunction)
from hub.security import audit
from hub.security.canonical import canonical
from hub.security.errors import AuthForbidden

KINDS = ("DEFINITION", "CLOCK", "CLOSURE", "CONSISTENCY", "CUTOFF")
CANDIDATE_ROLES = ("quality_lead", "compliance")
SEED_AUTHORITY = "seed: candidate wording of docs/03-problem-value/success-criteria.md (not policy)"
SEEDS = [
    ("D-OPS", "DEFINITION", "D-OPS", "D-OPS", {"text": "Operations marks the case closed"}),
    ("D-EVID", "DEFINITION", "D-EVID", "D-EVID", {"text": "Closed, and verifiable evidence and an authorised approver are recorded"}),
    ("D-FIN", "DEFINITION", "D-FIN", "D-FIN", {"text": "Successfully resolved for cost purposes (undefined)"}),
    ("C-OPS", "CLOCK", "receipt to ops-closed", "C-OPS",
     {"clock_start_event": "FACT_RECEIVED", "clock_stop_event": "FACT_OPS_CLOSED", "candidate_duration_hours": 48,
      "duration_hours": None, "calendar_basis": "wall_clock"}),
    ("C-EVID", "CLOCK", "receipt to evidence-complete", "C-EVID",
     {"clock_start_event": "FACT_RECEIVED", "clock_stop_event": "FACT_EVIDENCE_COMPLETE", "candidate_duration_hours": 48,
      "duration_hours": None, "calendar_basis": "wall_clock"}),
]
_POLICY_COLS = "policy_id, version, kind, name, definition_tag, body, owner, effective_from, effective_to, status, created_by, created_at"
_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


def _policy(row):
    return {"policy_id": row[0], "version": row[1], "kind": row[2], "name": row[3], "definition_tag": row[4],
            "body": json.loads(row[5]), "owner": row[6], "effective_from": row[7], "effective_to": row[8],
            "status": row[9], "created_by": row[10], "created_at": row[11]}


def _brief(p):
    return None if p is None else {"policy_ref": "%s@%d" % (p["policy_id"], p["version"]), "status": p["status"],
                                   "owner": p["owner"], "effective_from": p["effective_from"], "effective_to": p["effective_to"]}


class PolicyService(object):
    def __init__(self, con, settings, clock, anchor=None):
        self.con, self.s, self.clock, self.anchor = con, settings, clock, anchor
        schema.require(con)

    # ---------------------------------------------------------------- helpers
    def _actor(self, sess):
        if sess is None:
            return "hub", "system"
        return sess.principal.principal_id, sess.principal.actor_kind

    def _need_authority(self, authority_ref):
        if not isinstance(authority_ref, str) or not authority_ref.strip():
            raise AuthorityRequired()
        return authority_ref

    def _need_role(self, sess, roles, cid, op):
        p = sess.principal
        if any(r in p.roles for r in roles):
            return
        audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                     action="AUTHZ_DENIED", outcome="denied", correlation_id=cid, object_ref=op,
                     details={"reason": "role", "needs_one_of": list(roles)})
        raise AuthForbidden({"reason": "role"})

    def _zone_h(self, sess, zh, cid, object_ref):
        return gate.require_holder(self.con, self.s, self.clock, self.anchor, sess, zh, cid, object_ref)

    def _event_row(self, policy_ref, event_type, actor, old, new, authority_ref, holder_check_ref=None):
        n = self.con.execute("SELECT count(*) FROM policy_events").fetchone()[0] + 1
        eid = "PE-%08d" % n
        self.con.execute("INSERT INTO policy_events(event_id, policy_ref, event_type, actor, occurred_at, old_value, new_value,"
                         " authority_ref, holder_check_ref) VALUES (?,?,?,?,?,?,?,?,?)",
                         (eid, policy_ref, event_type, actor, self.clock(),
                          None if old is None else canonical(old), None if new is None else canonical(new),
                          self._need_authority(authority_ref), holder_check_ref))
        return eid

    # ---------------------------------------------------------------- policy objects
    def seed(self, correlation_id="seed"):
        """Idempotent. Fresh install: exactly 3 DEFINITION + 2 CLOCK candidates, owner 'unassigned', none adopted (BEH-POL-02)."""
        todo = [x for x in SEEDS if self.con.execute("SELECT 1 FROM policy_object WHERE policy_id = ?", (x[0],)).fetchone() is None]
        if not todo:
            return []
        with audit.change(self.con, self.clock, anchor=self.anchor, actor="hub", actor_kind="system", action="POLICY_SEEDED",
                          outcome="success", correlation_id=correlation_id, object_ref="policy:seed",
                          details={"policies": [x[0] for x in todo], "status": "candidate", "owner": "unassigned"}):
            for pid, kind, name, tag, body in todo:
                self.con.execute("INSERT INTO policy_object(" + _POLICY_COLS + ") VALUES (?,?,?,?,?,?,'unassigned',NULL,NULL,'candidate',?,?)",
                                 (pid, 1, kind, name, tag, canonical(body), "seed", self.clock()))
                self._event_row("%s@1" % pid, "POLICY_VERSION_CREATED", "seed", None,
                                {"policy_ref": "%s@1" % pid, "status": "candidate"}, SEED_AUTHORITY)
        return [x[0] for x in todo]

    def list_policies(self, kind=None, status=None, latest_only=False):
        q, a = "SELECT " + _POLICY_COLS + " FROM policy_object", []
        w = []
        if kind:
            w.append("kind = ?")
            a.append(kind)
        if status:
            w.append("status = ?")
            a.append(status)
        if latest_only:
            w.append("version = (SELECT max(version) FROM policy_object p2 WHERE p2.policy_id = policy_object.policy_id)")
        rows = self.con.execute(q + (" WHERE " + " AND ".join(w) if w else "") + " ORDER BY policy_id, version", a).fetchall()
        now = self.clock()
        return [withdrawal.overlay(self.con, _policy(r), now) for r in rows]  # Stage 20 DW-07: `withdrawal` key when in effect

    def get_policy(self, policy_id, version=None):
        if version is None:
            row = self.con.execute("SELECT " + _POLICY_COLS + " FROM policy_object WHERE policy_id = ? ORDER BY version DESC LIMIT 1",
                                   (policy_id,)).fetchone()
        else:
            row = self.con.execute("SELECT " + _POLICY_COLS + " FROM policy_object WHERE policy_id = ? AND version = ?",
                                   (policy_id, version)).fetchone()
        if row is None:
            raise NotFound({"policy_id": policy_id, "version": version})
        return withdrawal.overlay(self.con, _policy(row), self.clock())  # Stage 20 DW-07

    def events(self, policy_ref=None, event_type=None):
        q, a, w = "SELECT event_id, policy_ref, event_type, actor, occurred_at, old_value, new_value, authority_ref, holder_check_ref FROM policy_events", [], []
        if policy_ref:
            w.append("policy_ref = ?")
            a.append(policy_ref)
        if event_type:
            w.append("event_type = ?")
            a.append(event_type)
        rows = self.con.execute(q + (" WHERE " + " AND ".join(w) if w else "") + " ORDER BY event_id", a).fetchall()
        keys = ("event_id", "policy_ref", "event_type", "actor", "occurred_at", "old_value", "new_value", "authority_ref", "holder_check_ref")
        out = []
        for r in rows:
            e = dict(zip(keys, r))
            for k in ("old_value", "new_value"):
                e[k] = None if e[k] is None else json.loads(e[k])
            out.append(e)
        return out

    def _insert_policy(self, p):
        self.con.execute("INSERT INTO policy_object(" + _POLICY_COLS + ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         (p["policy_id"], p["version"], p["kind"], p["name"], p["definition_tag"], canonical(p["body"]),
                          p["owner"], p["effective_from"], p["effective_to"], p["status"], p["created_by"], p["created_at"]))

    def create_candidate(self, sess, policy_id, kind, name, body, authority_ref, definition_tag=None, owner="unassigned",
                         correlation_id="policy"):
        """New candidate policy or new candidate version (roles quality_lead / compliance, audited). Changing a policy that
        already has an adopted version is an edit of adopted content: Zone H (ZH-10)."""
        if kind not in KINDS:
            raise PolicyInvalid({"kind": kind})
        prior = self.con.execute("SELECT status FROM policy_object WHERE policy_id = ? AND status = 'adopted' LIMIT 1", (policy_id,)).fetchone()
        ref = "policy:" + str(policy_id)
        hcr = None
        if prior is not None:
            hcr = "audit:%d" % self._zone_h(sess, "ZH-10", correlation_id, ref)
        else:
            self._need_role(sess, CANDIDATE_ROLES, correlation_id, ref)
        self._need_authority(authority_ref)
        if not policy_id or not name:
            raise PolicyInvalid({"reason": "policy_id and name are required"})
        clocks.validate_body(kind, body)
        actor, akind = self._actor(sess)
        last = self.con.execute("SELECT version, kind FROM policy_object WHERE policy_id = ? ORDER BY version DESC LIMIT 1", (policy_id,)).fetchone()
        if last is not None and last[1] != kind:
            raise PolicyInvalid({"reason": "kind of an existing policy cannot change", "policy_id": policy_id})
        version = 1 if last is None else last[0] + 1
        p = {"policy_id": policy_id, "version": version, "kind": kind, "name": name, "definition_tag": definition_tag,
             "body": body, "owner": owner or "unassigned", "effective_from": None, "effective_to": None, "status": "candidate",
             "created_by": actor, "created_at": None}
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind,
                          action="POLICY_VERSION_CREATED", outcome="success", correlation_id=correlation_id, object_ref=ref,
                          details={"policy_ref": "%s@%d" % (policy_id, version), "status": "candidate"}) as ctx:
            p["created_at"] = self.clock()
            self._insert_policy(p)
            ctx.fields["details"]["event_id"] = self._event_row(
                "%s@%d" % (policy_id, version), "POLICY_VERSION_CREATED", actor, None if last is None else {"policy_ref": "%s@%d" % (policy_id, last[0])},
                _brief(p), authority_ref, hcr)
        return p

    def _overlaps(self, kind, tag, policy_id, a_from, a_to):
        hi = "9999-12-31"
        rows = self.con.execute("SELECT policy_id, version, effective_from, effective_to FROM policy_object WHERE status = 'adopted'"
                                " AND kind = ? AND COALESCE(definition_tag, policy_id) = ?", (kind, tag or policy_id)).fetchall()
        out = []
        for r in rows:
            w = withdrawal.recorded(self.con, "%s@%d" % (r[0], r[1]))  # Stage 20 DW-07: a withdrawn window ends at withdrawn_from
            if w is not None and (a_from or "") >= w["withdrawn_from"]:
                continue
            if (r[2] or "") <= (a_to or hi) and (a_from or "") <= (r[3] or hi):
                out.append((r[0], r[1]))
        return out

    def adopt(self, sess, policy_id, from_version, effective_from, owner, authority_ref, effective_to=None, body_updates=None,
              correlation_id="policy"):
        """ZH-05. candidate / accepted-open -> a NEW version with status adopted (BEH-POL-03); overlap with another adopted
        version of the same (kind, definition_tag) is refused."""
        ref = "policy:%s@%s" % (policy_id, from_version)
        hcr = "audit:%d" % self._zone_h(sess, "ZH-05", correlation_id, ref)
        self._need_authority(authority_ref)
        src = self.get_policy(policy_id, from_version)
        if src["status"] == "adopted":
            raise PolicyInvalid({"reason": "already adopted", "policy_ref": "%s@%d" % (policy_id, src["version"])})
        if not (isinstance(effective_from, str) and _DATE.match(effective_from)) or \
                (effective_to is not None and not (isinstance(effective_to, str) and _DATE.match(effective_to) and effective_to >= effective_from)):
            raise PolicyInvalid({"reason": "effective_from / effective_to must be YYYY-MM-DD with to >= from"})
        if not owner or owner == "unassigned":
            raise PolicyInvalid({"reason": "an adopted policy needs a named owner"})
        body = dict(src["body"])
        body.update(body_updates or {})
        body.pop("accepted_open", None)
        clocks.validate_body(src["kind"], body)
        clash = self._overlaps(src["kind"], src["definition_tag"], policy_id, effective_from, effective_to)
        if clash:
            raise Overlap({"with": ["%s@%d" % c for c in clash], "kind": src["kind"], "definition_tag": src["definition_tag"]})
        actor, akind = self._actor(sess)
        last = self.con.execute("SELECT max(version) FROM policy_object WHERE policy_id = ?", (policy_id,)).fetchone()[0]
        p = dict(src, version=last + 1, body=body, owner=owner, effective_from=effective_from, effective_to=effective_to,
                 status="adopted", created_by=actor, created_at=None)
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="POLICY_ADOPTED",
                          outcome="success", correlation_id=correlation_id, object_ref="policy:%s@%d" % (policy_id, p["version"]),
                          details={"from": _brief(src), "to_version": p["version"], "authority_ref": authority_ref}) as ctx:
            p["created_at"] = self.clock()
            self._insert_policy(p)
            ctx.fields["details"]["event_id"] = self._event_row("%s@%d" % (policy_id, p["version"]), "POLICY_ADOPTED", actor,
                                                                _brief(src), _brief(p), authority_ref, hcr)
        return p

    def accept_open(self, sess, policy_id, from_version, reason, authority_ref, correlation_id="policy"):
        """ZH-05. Record 'accepted-open' (explicit, dated, with reason and authority_ref): a NEW version, never 'adopted'."""
        ref = "policy:%s@%s" % (policy_id, from_version)
        hcr = "audit:%d" % self._zone_h(sess, "ZH-05", correlation_id, ref)
        self._need_authority(authority_ref)
        if not isinstance(reason, str) or not reason.strip():
            raise PolicyInvalid({"reason": "a reason is required to record accepted-open"})
        src = self.get_policy(policy_id, from_version)
        actor, akind = self._actor(sess)
        last = self.con.execute("SELECT max(version) FROM policy_object WHERE policy_id = ?", (policy_id,)).fetchone()[0]
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="POLICY_ACCEPTED_OPEN",
                          outcome="success", correlation_id=correlation_id, object_ref="policy:%s@%d" % (policy_id, last + 1),
                          details={"from": _brief(src), "authority_ref": authority_ref}) as ctx:
            now = self.clock()
            body = dict(src["body"], accepted_open={"reason": reason, "recorded_at": now, "recorded_by": actor,
                                                    "authority_ref": authority_ref})
            p = dict(src, version=last + 1, body=body, status="accepted-open", created_by=actor, created_at=now,
                     effective_from=None, effective_to=None)
            self._insert_policy(p)
            ctx.fields["details"]["event_id"] = self._event_row("%s@%d" % (policy_id, p["version"]), "POLICY_ACCEPTED_OPEN", actor,
                                                                _brief(src), dict(_brief(p), reason=reason, dated=now), authority_ref, hcr)
        return p

    def withdraw(self, sess, policy_id, version, withdrawn_from, reason, authority_ref, correlation_id="policy"):
        """ZH-10 (Stage 20 DW-07, BEH-POL-05, FAC-13 proposed). Withdraw an ADOPTED version from `withdrawn_from` (YYYY-MM-DD, inclusive):
        one POLICY_WITHDRAWN policy event + its audit record in one transaction. Refused without a Zone H holder (E-GATE-*), without an
        authority_ref (E-POL-AUTHORITY-REQUIRED) or reason, for a version that is not adopted, already withdrawn, or a date before its
        effective_from. Nothing else changes: the stored version keeps status 'adopted' (history), its use stops from withdrawn_from."""
        ref = "policy:%s@%s" % (policy_id, version)
        hcr = "audit:%d" % self._zone_h(sess, "ZH-10", correlation_id, ref)
        self._need_authority(authority_ref)
        if not isinstance(reason, str) or not reason.strip():
            raise PolicyInvalid({"reason": "a reason is required to withdraw a policy"})
        if not isinstance(version, int) or isinstance(version, bool):
            raise PolicyInvalid({"reason": "version must be an integer"})
        row = self.con.execute("SELECT " + _POLICY_COLS + " FROM policy_object WHERE policy_id = ? AND version = ?", (policy_id, version)).fetchone()
        if row is None:
            raise NotFound({"policy_id": policy_id, "version": version})
        src = _policy(row)
        pref = "%s@%d" % (policy_id, version)
        if src["status"] != "adopted":
            raise PolicyInvalid({"reason": "only an adopted version can be withdrawn", "policy_ref": pref, "status": src["status"]})
        if withdrawal.recorded(self.con, pref) is not None:
            raise PolicyInvalid({"reason": "already withdrawn", "policy_ref": pref})
        if not withdrawal.valid_date(withdrawn_from) or (src["effective_from"] and withdrawn_from < src["effective_from"]):
            raise PolicyInvalid({"reason": "withdrawn_from must be YYYY-MM-DD and not before effective_from", "effective_from": src["effective_from"]})
        actor, akind = self._actor(sess)
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action=withdrawal.EVENT,
                          outcome="success", correlation_id=correlation_id, object_ref="policy:" + pref,
                          details={"policy_ref": pref, "withdrawn_from": withdrawn_from, "authority_ref": authority_ref}) as ctx:
            ctx.fields["details"]["event_id"] = self._event_row(
                pref, withdrawal.EVENT, actor, _brief(src),
                {"policy_ref": pref, "withdrawn_from": withdrawn_from, "reason": reason, "prior_effective_to": src["effective_to"]},
                authority_ref, hcr)
        return withdrawal.recorded(self.con, pref)

    def status_report(self):
        """Latest version of every policy, grouped by status: accepted-open is never shown as adopted (AC-POL-05); an adopted version
        whose withdrawal is in effect is listed under 'withdrawn' (Stage 20 DW-07)."""
        out = {"adopted": [], "accepted-open": [], "candidate": [], "withdrawn": []}
        for p in self.list_policies(latest_only=True):
            b = dict(_brief(p), kind=p["kind"], definition_tag=p["definition_tag"])
            if p.get("withdrawal"):
                out["withdrawn"].append(dict(b, withdrawn_from=p["withdrawal"]["withdrawn_from"]))
            else:
                out[p["status"]].append(b)
        return out

    def clock_report(self, cases):
        """Elapsed time under EVERY configured clock, side by side (latest version of each CLOCK policy), per case."""
        clk = self.list_policies(kind="CLOCK", latest_only=True)
        return [{"case_id": c["case_id"], "clocks": [clocks.clock_entry(p, c["events"]) for p in clk]} for c in cases]

    # ---------------------------------------------------------------- rule sets
    def _insert_ruleset(self, doc):
        self.con.execute("INSERT INTO rule_set(ruleset_id, version, name, origin, read_only, functions) VALUES (?,?,?,?,?,?)",
                         (doc["ruleset_id"], doc["version"], doc["name"], doc["origin"], 1 if doc["read_only"] else 0,
                          canonical(sorted(doc["functions"]))))
        for r in doc["rows"]:
            self.con.execute("INSERT INTO rule_row(ruleset_id, version, row_id, ordinal, conditions, outcome, effective_from,"
                             " effective_to, owner, is_default) VALUES (?,?,?,?,?,?,?,?,?,?)",
                             (doc["ruleset_id"], doc["version"], r["row_id"], r["ordinal"], canonical(r["conditions"]),
                              canonical(r["outcome"]), r.get("effective_from"), r.get("effective_to"), r.get("owner"),
                              1 if r.get("is_default") else 0))

    def get_ruleset(self, ref):
        rid, ver = rulesets.parse_ref(ref)
        h = self.con.execute("SELECT name, origin, read_only, functions FROM rule_set WHERE ruleset_id = ? AND version = ?", (rid, ver)).fetchone()
        if h is None:
            raise NotFound({"ruleset_ref": ref})
        rows = self.con.execute("SELECT row_id, ordinal, conditions, outcome, effective_from, effective_to, owner, is_default FROM rule_row"
                                " WHERE ruleset_id = ? AND version = ? ORDER BY ordinal, row_id", (rid, ver)).fetchall()
        return {"ruleset_id": rid, "version": ver, "name": h[0], "origin": h[1], "read_only": bool(h[2]), "functions": json.loads(h[3]),
                "rows": [{"row_id": r[0], "ordinal": r[1], "conditions": json.loads(r[2]), "outcome": json.loads(r[3]),
                          "effective_from": r[4], "effective_to": r[5], "owner": r[6], "is_default": r[7]} for r in rows]}

    def active(self):
        return {r[0]: "%s@%d" % (r[1], r[2]) for r in self.con.execute("SELECT function, ruleset_id, version FROM active_ruleset ORDER BY function")}

    def list_rulesets(self):
        act = self.active()
        out = []
        for rid, ver, name, origin, ro, fns in self.con.execute("SELECT ruleset_id, version, name, origin, read_only, functions FROM rule_set ORDER BY ruleset_id, version"):
            ref = "%s@%d" % (rid, ver)
            out.append({"ruleset_id": rid, "version": ver, "ruleset_ref": ref, "name": name, "origin": origin, "read_only": bool(ro),
                        "functions": json.loads(fns), "active_for": sorted(f for f, r in act.items() if r == ref)})
        return out

    def load_as_found(self, legacy_root, run_dir, correlation_id="load-as-found"):
        """AD-06: load the three as-found sets (inactive, read-only). Idempotent; legacy drift -> E-POL-ASFOUND-DRIFT. Never activates."""
        report = []
        for doc in asfound.build_all(legacy_root, run_dir):
            ref = rulesets.make_ref(doc["ruleset_id"], doc["version"])
            digest = rulesets.content_hash(doc)
            try:
                have = rulesets.content_hash(self.get_ruleset(ref))
            except NotFound:
                have = None
            if have is not None:
                if have != digest:
                    raise AsFoundDrift({"ruleset_ref": ref, "stored_sha256": have, "legacy_sha256": digest})
                report.append({"ruleset_ref": ref, "loaded": False, "content_sha256": digest})
                continue
            with audit.change(self.con, self.clock, anchor=self.anchor, actor="hub", actor_kind="system", action="RULESET_LOADED",
                              outcome="success", correlation_id=correlation_id, object_ref="ruleset:" + ref,
                              details={"origin": "as-found", "read_only": True, "active": False, "rows": len(doc["rows"]),
                                       "content_sha256": digest, "functions": sorted(doc["functions"])}):
                self._insert_ruleset(doc)
            report.append({"ruleset_ref": ref, "loaded": True, "content_sha256": digest})
        return report

    def fork_as_custom(self, sess, ref, new_id, authority_ref, correlation_id="policy"):
        """A custom (editable) copy of any set, version 1, inactive. Edits never touch an as-found set (BEH-POL-07)."""
        self._need_role(sess, CANDIDATE_ROLES, correlation_id, "ruleset:" + str(ref))
        self._need_authority(authority_ref)
        src = self.get_ruleset(ref)
        doc = dict(src, ruleset_id=new_id, version=1, origin="custom", read_only=False, name="Custom copy of %s" % ref)
        rulesets.validate(doc)
        if self.con.execute("SELECT 1 FROM rule_set WHERE ruleset_id = ?", (new_id,)).fetchone():
            raise PolicyInvalid({"reason": "ruleset_id already exists", "ruleset_id": new_id})
        actor, akind = self._actor(sess)
        nref = rulesets.make_ref(new_id, 1)
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="POLICY_VERSION_CREATED",
                          outcome="success", correlation_id=correlation_id, object_ref="ruleset:" + nref,
                          details={"forked_from": ref, "active": False}) as ctx:
            self._insert_ruleset(doc)
            ctx.fields["details"]["event_id"] = self._event_row(nref, "POLICY_VERSION_CREATED", actor, {"ruleset_ref": ref},
                                                                {"ruleset_ref": nref, "origin": "custom"}, authority_ref)
        return nref

    def edit_rule_row(self, sess, ref, row_id, authority_ref, outcome_updates=None, conditions=None, correlation_id="policy"):
        """ZH-10. Edit one row of a CUSTOM set = new version of the set (old versions untouched); RULE_ROW_CHANGED event with who /
        when / old / new / authority_ref. An as-found set is read-only: E-POL-READONLY-SET (audited)."""
        hcr = "audit:%d" % self._zone_h(sess, "ZH-10", correlation_id, "ruleset:" + str(ref))
        self._need_authority(authority_ref)
        doc = self.get_ruleset(ref)
        actor, akind = self._actor(sess)
        if doc["read_only"] or doc["origin"] == "as-found":
            audit.append(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="RULE_ROW_CHANGED",
                         outcome="denied", correlation_id=correlation_id, object_ref="ruleset:" + ref, reason="read_only_set",
                         details={"row_id": row_id})
            raise ReadonlySet({"ruleset_ref": ref})
        row = [r for r in doc["rows"] if r["row_id"] == row_id]
        if not row:
            raise NotFound({"ruleset_ref": ref, "row_id": row_id})
        old = {"row_id": row_id, "conditions": row[0]["conditions"], "outcome": row[0]["outcome"]}
        new_row = dict(row[0], outcome=dict(row[0]["outcome"], **(outcome_updates or {})),
                       conditions=row[0]["conditions"] if conditions is None else conditions)
        last = self.con.execute("SELECT max(version) FROM rule_set WHERE ruleset_id = ?", (doc["ruleset_id"],)).fetchone()[0]
        new_doc = dict(doc, version=last + 1, rows=[new_row if r["row_id"] == row_id else r for r in doc["rows"]])
        rulesets.validate(new_doc)
        nref = rulesets.make_ref(doc["ruleset_id"], new_doc["version"])
        new = {"row_id": row_id, "conditions": new_row["conditions"], "outcome": new_row["outcome"]}
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="RULE_ROW_CHANGED",
                          outcome="success", correlation_id=correlation_id, object_ref="ruleset:" + nref,
                          details={"from": ref, "row_id": row_id, "authority_ref": authority_ref}) as ctx:
            self._insert_ruleset(new_doc)
            ctx.fields["details"]["event_id"] = self._event_row(nref, "RULE_ROW_CHANGED", actor, dict(old, ruleset_ref=ref),
                                                                dict(new, ruleset_ref=nref), authority_ref, hcr)
        return nref

    # ---------------------------------------------------------------- evaluation
    def evaluate(self, function, inputs, ruleset_ref=None):
        """BEH-POL-06/08. Explicit ruleset_ref always works (what-if, authoritative only if it IS the active set);
        without one an active set is required (E-POL-NO-ACTIVE-RULESET). Read-only: no audit, no write."""
        if function not in engine.FUNCTIONS:
            raise UnknownFunction({"function": function, "catalogue": sorted(engine.FUNCTIONS)})
        act = self.active().get(function)
        if ruleset_ref is None:
            if act is None:
                raise NoActiveRuleset({"function": function})
            ruleset_ref = act
        doc = self.get_ruleset(ruleset_ref)
        res = engine.evaluate(doc, function, inputs)
        res["authoritative"] = (act == ruleset_ref)
        return res

    def evaluate_many(self, function, batch, ruleset_ref=None):
        """One result per input row, in order: the rule service never multiplies rows (AC-POL-15; legacy JOIN defect BB-07)."""
        if ruleset_ref is None and function in engine.FUNCTIONS:
            ruleset_ref = self.active().get(function)
            if ruleset_ref is None:
                raise NoActiveRuleset({"function": function})
        return [self.evaluate(function, i, ruleset_ref) for i in batch]

    # ---------------------------------------------------------------- activation
    def _check_set_serves(self, function, ref):
        if function not in engine.FUNCTIONS:
            raise UnknownFunction({"function": function})
        doc = self.get_ruleset(ref)
        if function not in doc["functions"]:
            raise UnknownFunction({"function": function, "ruleset_ref": ref, "served": doc["functions"]})
        return doc

    @staticmethod
    def decision_object_ref(function, ref):
        return "rule-activation:%s:%s" % (function, ref)

    def record_activation_decision(self, sess, function, ruleset_ref, authority_ref, reason, correlation_id="policy"):
        """Record the human decision to activate `ruleset_ref` for `function` in the hash-chained audit trail (ZH-06).
        Returns {"decision_seq", ...}. It activates nothing."""
        oref = self.decision_object_ref(function, ruleset_ref)
        self._zone_h(sess, "ZH-06", correlation_id, oref)
        self._need_authority(authority_ref)
        if not isinstance(reason, str) or not reason.strip():
            raise PolicyInvalid({"reason": "a reason is required"})
        self._check_set_serves(function, ruleset_ref)
        actor, akind = self._actor(sess)
        rec = audit.append(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="POLICY_DECISION_RECORDED",
                           outcome="success", correlation_id=correlation_id, object_ref=oref,
                           details={"decision": "activate", "function": function, "ruleset_ref": ruleset_ref,
                                    "authority_ref": authority_ref, "reason": reason})
        return {"decision_seq": rec["audit_seq"], "object_ref": oref, "recorded_by": actor}

    def _decision_problem(self, decision_seq, function, ruleset_ref):
        """None when `decision_seq` is a valid recorded human decision for exactly this activation; else the reason."""
        if isinstance(decision_seq, bool) or not isinstance(decision_seq, int):
            return "no decision_seq given"
        row = self.con.execute("SELECT action, outcome, actor, actor_kind, object_ref, details FROM audit_log WHERE audit_seq = ?",
                               (decision_seq,)).fetchone()
        if row is None:
            return "no such audit record"
        d = json.loads(row[5])
        if row[0] != "POLICY_DECISION_RECORDED" or row[1] != "success":
            return "audit record is not a recorded decision"
        if row[3] != "human":
            return "decision was not recorded by a human"
        if row[2] not in self.s["zone_h"]["holders"]:
            return "decision actor is not a configured Zone H holder"
        if row[4] != self.decision_object_ref(function, ruleset_ref) or d.get("decision") != "activate" \
                or d.get("function") != function or d.get("ruleset_ref") != ruleset_ref or not str(d.get("authority_ref", "")).strip():
            return "decision is for a different function or rule set"
        for e in self.events(event_type="RULESET_ACTIVATED"):
            if (e["new_value"] or {}).get("decision_audit_seq") == decision_seq:
                return "decision already consumed by %s" % e["event_id"]
        rep = audit.verify(self.con, self.anchor.path if self.anchor is not None else None)
        if rep["status"] != "ok":
            return "audit chain does not verify (%s)" % rep.get("kind")
        return None

    def activate(self, sess, function, ruleset_ref, authority_ref, decision_seq=None, correlation_id="policy"):
        """ZH-06. Refused (E-POL-DECISION-REQUIRED, audited) unless `decision_seq` is a valid recorded human decision for exactly
        this (function, ruleset). RULESET_ACTIVATED goes to policy_events and the audit chain in one transaction."""
        oref = self.decision_object_ref(function, ruleset_ref)
        hcr = "audit:%d" % self._zone_h(sess, "ZH-06", correlation_id, oref)
        self._need_authority(authority_ref)
        self._check_set_serves(function, ruleset_ref)
        actor, akind = self._actor(sess)
        problem = self._decision_problem(decision_seq, function, ruleset_ref)
        if problem:
            audit.append(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="RULESET_ACTIVATED",
                         outcome="denied", correlation_id=correlation_id, object_ref=oref, reason="decision_required",
                         details={"function": function, "ruleset_ref": ruleset_ref, "problem": problem})
            raise DecisionRequired({"function": function, "ruleset_ref": ruleset_ref, "problem": problem})
        prev = self.active().get(function)
        rid, ver = rulesets.parse_ref(ruleset_ref)
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="RULESET_ACTIVATED",
                          outcome="success", correlation_id=correlation_id, object_ref=oref,
                          details={"function": function, "ruleset_ref": ruleset_ref, "previous": prev,
                                   "decision_audit_seq": decision_seq, "authority_ref": authority_ref}) as ctx:
            eid = self._event_row(ruleset_ref, "RULESET_ACTIVATED", actor, {"function": function, "ruleset_ref": prev},
                                  {"function": function, "ruleset_ref": ruleset_ref, "decision_audit_seq": decision_seq},
                                  authority_ref, hcr)
            self.con.execute("DELETE FROM active_ruleset WHERE function = ?", (function,))
            self.con.execute("INSERT INTO active_ruleset(function, ruleset_id, version, activated_event) VALUES (?,?,?,?)",
                             (function, rid, ver, eid))
            ctx.fields["details"]["event_id"] = eid
        return {"function": function, "ruleset_ref": ruleset_ref, "event_id": eid, "previous": prev}

    def deactivate(self, sess, function, authority_ref, correlation_id="policy"):
        """ZH-06. Back to 'no active set' for `function`. Risk-reducing: holder + authority_ref, no prior decision needed."""
        oref = "rule-deactivation:%s" % function
        hcr = "audit:%d" % self._zone_h(sess, "ZH-06", correlation_id, oref)
        self._need_authority(authority_ref)
        if function not in engine.FUNCTIONS:
            raise UnknownFunction({"function": function})
        prev = self.active().get(function)
        if prev is None:
            raise NotFound({"function": function, "reason": "no active rule set"})
        actor, akind = self._actor(sess)
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=akind, action="RULESET_DEACTIVATED",
                          outcome="success", correlation_id=correlation_id, object_ref=oref,
                          details={"function": function, "previous": prev, "authority_ref": authority_ref}) as ctx:
            eid = self._event_row(prev, "RULESET_DEACTIVATED", actor, {"function": function, "ruleset_ref": prev},
                                  {"function": function, "ruleset_ref": None}, authority_ref, hcr)
            self.con.execute("DELETE FROM active_ruleset WHERE function = ?", (function,))
            ctx.fields["details"]["event_id"] = eid
        return {"function": function, "previous": prev, "event_id": eid}
