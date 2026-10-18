"""CrosswalkService: explicit identity links (C7, F05, ADR-009, FR-ID-01/02).

* Rule links ONLY by an exact registered key: equality of the strings after Unicode NFC + trim, and the target resolves to
  exactly one entity. There is no prefix, case-folding, edit-distance, token or similarity matching anywhere in this package.
* Orphans stay orphans: an item with no registered-key match is reported (UNMATCHED_REF / NO_KEY) and counted, never repaired.
* Links are append-only. Removal is a LINK_RETRACTED event; the current link set is the set of non-retracted links. A link
  that a human retracted is not silently re-created by a later rule run (counted `skipped_retracted`).
* Human links: roles reviewer / quality_lead / compliance (human principals only), a registered type pair, a non-empty reason,
  no duplicate active link, no self-link. Every write is one transaction with its hash-chained audit record.
"""
import json

from hub.core.untrusted import require_trusted
from hub.crosswalk.registry import Registry, normalise
from hub.decision import schema
from hub.decision.errors import (AmbiguousType, IdNotFound, IdReasonRequired, LinkExists, LinkNotFound, PairNotRegistered,
                                 SelfLink)
from hub.security import audit
from hub.security.errors import AuthForbidden, AuthUnauthenticated

WRITE_ROLES = ("reviewer", "quality_lead", "compliance")
READ_ROLES = WRITE_ROLES + ("dispositioner",)
RULE_ACTOR = "crosswalk-matcher"
COLS = ("link_id", "from_type", "from_id", "to_type", "to_id", "key_used", "creator_kind", "creator", "created_at", "reason", "run_id")
OUTCOMES = ("LINKED", "NOOP_ALREADY_LINKED", "UNMATCHED_REF", "AMBIGUOUS_MATCH", "NO_KEY", "SKIPPED_RETRACTED")


def _pair(ft, fi, tt, ti):
    return tuple(sorted([(ft, fi), (tt, ti)]))


def identity_targets(ids):
    """{normalised key: [entity ids]} for entities whose registered key IS their id."""
    out = {}
    for i in ids:
        k = normalise(i)
        if k is not None:
            out.setdefault(k, []).append(i)
    return out


class CrosswalkService(object):
    def __init__(self, con, s, clock, anchor=None, registry=None):
        self.con, self.s, self.clock, self.anchor = con, s, clock, anchor
        self.registry = registry or Registry()
        schema.require(con)

    # ------------------------------------------------------------------ helpers
    def _need_roles(self, sess, roles, cid, op):
        if sess is None:
            raise AuthUnauthenticated()
        p = sess.principal
        if p.kind == "human" and any(r in p.roles for r in roles):
            return p
        audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                     action="AUTHZ_DENIED", outcome="denied", correlation_id=cid, object_ref=op,
                     details={"reason": "role", "needs_one_of": list(roles)})
        raise AuthForbidden({"reason": "role"})

    def _next(self, table, prefix):
        return "%s%08d" % (prefix, self.con.execute("SELECT count(*) FROM %s" % table).fetchone()[0] + 1)

    def _states(self, pairs_types):
        """(active pair set, ever-retracted pair set) over the given (type, type) pairs."""
        active, retracted = set(), set()
        seen = set()
        for a, b in pairs_types:
            for ft, tt in ((a, b), (b, a)):
                if (ft, tt) in seen:
                    continue
                seen.add((ft, tt))
                q = ("SELECT l.from_type, l.from_id, l.to_type, l.to_id,"
                     " EXISTS(SELECT 1 FROM crosswalk_link_event e WHERE e.link_id = l.link_id AND e.event_type = 'LINK_RETRACTED')"
                     " FROM crosswalk_link l WHERE l.from_type = ? AND l.to_type = ?")
                for r in self.con.execute(q, (ft, tt)):
                    (retracted if r[4] else active).add(_pair(r[0], r[1], r[2], r[3]))
        return active, retracted

    def _insert_link(self, n, from_type, from_id, to_type, to_id, key_used, kind, creator, now, reason, run_id, actor, event_type):
        link_id = "LNK-%08d" % n
        self.con.execute("INSERT INTO crosswalk_link(" + ", ".join(COLS) + ") VALUES (" + ",".join("?" * len(COLS)) + ")",
                         (link_id, from_type, from_id, to_type, to_id, key_used, kind, creator, now, reason, run_id))
        m = self.con.execute("SELECT count(*) FROM crosswalk_link_event").fetchone()[0] + 1
        self.con.execute("INSERT INTO crosswalk_link_event(event_id, link_id, event_type, actor, occurred_at, reason) VALUES (?,?,?,?,?,?)",
                         ("LE-%08d" % m, link_id, event_type, actor, now, reason))
        return link_id

    # ------------------------------------------------------------------ rule links
    def run_rule(self, code, items, targets, run_id, correlation_id="crosswalk", return_outcomes=False):
        """Match `items` [(from_id, key_value)] against `targets` {normalised key: [to_id, ...]} for registered rule link type `code`.
        Returns counts per outcome (+ per-item outcomes on request). One transaction, one audit record (CROSSWALK_RUN)."""
        lt = self.registry.link_type(code)
        if lt is None or lt["creator_kind"] != "rule":
            raise PairNotRegistered({"link_type": str(code)[:20], "reason": "not a registered rule link type"})
        ft, tt = lt["from_type"], lt["to_type"]
        counts = dict((o, 0) for o in OUTCOMES)
        outcomes = []
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=RULE_ACTOR, actor_kind="rule", action="CROSSWALK_RUN",
                          outcome="success", correlation_id=correlation_id, object_ref="crosswalk:" + code, details={}) as ctx:
            active, retracted = self._states([(ft, tt)])
            now = self.clock()
            n = self.con.execute("SELECT count(*) FROM crosswalk_link").fetchone()[0]
            for from_id, key in items:
                k = normalise(key)
                if not k:
                    res = "NO_KEY"
                else:
                    cands = targets.get(k, [])
                    if len(cands) == 0:
                        res = "UNMATCHED_REF"
                    elif len(cands) > 1:
                        res = "AMBIGUOUS_MATCH"
                    else:
                        to_id = cands[0]
                        pk = _pair(ft, from_id, tt, to_id)
                        if pk in active:
                            res = "NOOP_ALREADY_LINKED"
                        elif pk in retracted:
                            res = "SKIPPED_RETRACTED"
                        else:
                            n += 1
                            self._insert_link(n, ft, from_id, tt, to_id, lt["key_used"], "rule", code, now, None, run_id,
                                              RULE_ACTOR, "LINK_CREATED_RULE")
                            active.add(pk)
                            res = "LINKED"
                counts[res] += 1
                if return_outcomes:
                    outcomes.append((from_id, res))
            total = len(items)
            ctx.fields["details"] = {"link_type": code, "run_id": run_id, "items": total, "counts": counts,
                                     "orphans": counts["UNMATCHED_REF"] + counts["NO_KEY"] + counts["AMBIGUOUS_MATCH"]}
        out = {"link_type": code, "run_id": run_id, "items": len(items), "counts": counts,
               "orphans": counts["UNMATCHED_REF"] + counts["NO_KEY"] + counts["AMBIGUOUS_MATCH"]}
        if return_outcomes:
            out["outcomes"] = outcomes
        return out

    # ------------------------------------------------------------------ human links
    def create_human_link(self, sess, from_type, from_id, to_type, to_id, reason, correlation_id="crosswalk"):
        """OP-ID-02."""
        require_trusted([from_type, from_id, to_type, to_id], "create_human_link")
        p = self._need_roles(sess, WRITE_ROLES, correlation_id, "OP-ID-02")
        from_id, to_id = normalise(from_id), normalise(to_id)
        if from_id is None or to_id is None or from_type not in self.registry.patterns or to_type not in self.registry.patterns:
            raise IdNotFound({"reason": "unknown object type or identifier"})
        if (from_type, from_id) == (to_type, to_id):
            raise SelfLink({"type": from_type})
        reason = reason.strip() if isinstance(reason, str) else ""
        if not reason or len(reason) > 2000:
            raise IdReasonRequired({"reason": "a non-empty reason of at most 2000 characters is required"})
        if not self.registry.pair_registered(from_type, to_type):
            raise PairNotRegistered({"from_type": from_type, "to_type": to_type})
        for t, i in ((from_type, from_id), (to_type, to_id)):
            if not self.registry.matches(t, i):
                raise IdNotFound({"type": t, "reason": "identifier does not match the registered pattern"})
        key_used, code = self.registry.pair_key_used(from_type, to_type)
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                          action="LINK_CREATED_HUMAN", outcome="success", correlation_id=correlation_id,
                          object_ref="link:%s:%s-%s:%s" % (from_type, from_id, to_type, to_id), details={}) as ctx:
            active, _ = self._states([(from_type, to_type)])
            if _pair(from_type, from_id, to_type, to_id) in active:
                raise LinkExists({"from": "%s:%s" % (from_type, from_id), "to": "%s:%s" % (to_type, to_id)})
            now = self.clock()
            n = self.con.execute("SELECT count(*) FROM crosswalk_link").fetchone()[0] + 1
            link_id = self._insert_link(n, from_type, from_id, to_type, to_id, key_used, "human", p.principal_id, now, reason, None,
                                        p.principal_id, "LINK_CREATED_HUMAN")
            ctx.fields["details"] = {"link_id": link_id, "link_type": code, "from": "%s:%s" % (from_type, from_id),
                                     "to": "%s:%s" % (to_type, to_id)}
        return self.get_link(link_id)

    def retract(self, sess, link_id, reason, correlation_id="crosswalk"):
        """OP-ID-03: LINK_RETRACTED event with a reason; the link row and its creation event stay."""
        require_trusted([link_id], "retract")
        p = self._need_roles(sess, WRITE_ROLES, correlation_id, "OP-ID-03")
        reason = reason.strip() if isinstance(reason, str) else ""
        if not reason or len(reason) > 2000:
            raise IdReasonRequired({"reason": "a non-empty reason of at most 2000 characters is required"})
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                          action="LINK_RETRACTED", outcome="success", correlation_id=correlation_id,
                          object_ref="link:%s" % str(link_id)[:40], details={}) as ctx:
            row = self.con.execute("SELECT link_id FROM crosswalk_link WHERE link_id = ?", (link_id,)).fetchone()
            if row is None:
                raise LinkNotFound({"link_id": str(link_id)[:40]})
            if self.con.execute("SELECT 1 FROM crosswalk_link_event WHERE link_id = ? AND event_type = 'LINK_RETRACTED'", (link_id,)).fetchone():
                raise LinkNotFound({"link_id": link_id, "reason": "already retracted"})
            m = self.con.execute("SELECT count(*) FROM crosswalk_link_event").fetchone()[0] + 1
            self.con.execute("INSERT INTO crosswalk_link_event(event_id, link_id, event_type, actor, occurred_at, reason) VALUES (?,?,?,?,?,?)",
                             ("LE-%08d" % m, link_id, "LINK_RETRACTED", p.principal_id, self.clock(), reason))
            ctx.fields["details"] = {"link_id": link_id}
        return self.get_link(link_id)

    # ------------------------------------------------------------------ reads
    def get_link(self, link_id):
        row = self.con.execute("SELECT " + ", ".join(COLS) + " FROM crosswalk_link WHERE link_id = ?", (link_id,)).fetchone()
        if row is None:
            raise LinkNotFound({"link_id": str(link_id)[:40]})
        d = dict(zip(COLS, row))
        ev = self.con.execute("SELECT event_id, event_type, actor, occurred_at, reason FROM crosswalk_link_event WHERE link_id = ?"
                              " ORDER BY event_id", (link_id,)).fetchall()
        d["events"] = [dict(zip(("event_id", "event_type", "actor", "occurred_at", "reason"), e)) for e in ev]
        d["active"] = not any(e["event_type"] == "LINK_RETRACTED" for e in d["events"])
        return d

    def active_links(self, link_type=None):
        """Current link set (non-retracted), ordered by link_id."""
        out = []
        for (lid,) in self.con.execute("SELECT link_id FROM crosswalk_link ORDER BY link_id").fetchall():
            d = self.get_link(lid)
            if d["active"] and (link_type is None or d["creator"] == link_type or d["key_used"] == link_type):
                out.append(d)
        return out

    def count_active(self, creator=None):
        """Count of non-retracted links, optionally by creator (rule id such as LT-04, or a user id)."""
        q = ("SELECT count(*) FROM crosswalk_link l WHERE NOT EXISTS (SELECT 1 FROM crosswalk_link_event e WHERE e.link_id = l.link_id"
             " AND e.event_type = 'LINK_RETRACTED')")
        if creator:
            return self.con.execute(q + " AND l.creator = ?", (creator,)).fetchone()[0]
        return self.con.execute(q).fetchone()[0]

    def lookup(self, sess, id_value, id_type=None, correlation_id="crosswalk"):
        """OP-ID-01: direct active links for an identifier. Without id_type the id is compared with the registered id patterns; a
        string that matches several returns E-ID-AMBIGUOUS-TYPE with the candidates and NO data (no guessing)."""
        require_trusted([id_value, id_type], "lookup")
        self._need_roles(sess, READ_ROLES, correlation_id, "OP-ID-01")
        v = normalise(id_value)
        if v is None:
            raise IdNotFound({"reason": "identifier must be a string"})
        if id_type is None:
            cands = self.registry.candidates(v)
            if not cands:
                raise IdNotFound({"id": v[:80], "reason": "matches no registered id pattern"})
            if len(cands) > 1:
                raise AmbiguousType({"id": v[:80], "candidates": cands})
            id_type = cands[0]
        elif not self.registry.matches(id_type, v):
            raise IdNotFound({"id": v[:80], "id_type": str(id_type)[:40], "reason": "does not match the registered pattern"})
        rows = self.con.execute("SELECT link_id FROM crosswalk_link WHERE (from_type = ? AND from_id = ?) OR (to_type = ? AND to_id = ?)"
                                " ORDER BY created_at, link_id", (id_type, v, id_type, v)).fetchall()
        links = [d for d in (self.get_link(r[0]) for r in rows) if d["active"]]
        return {"id": v, "id_type": id_type, "links": [{k: d[k] for k in COLS} for d in links]}

    def history(self, link_id):
        return self.get_link(link_id)["events"]

    def orphan_report(self):
        """Orphan accounting from the audit chain: the latest CROSSWALK_RUN per link type (DQ-24)."""
        out = {}
        for (det,) in self.con.execute("SELECT details FROM audit_log WHERE action = 'CROSSWALK_RUN' ORDER BY audit_seq").fetchall():
            d = json.loads(det)
            out[d["link_type"]] = {"run_id": d["run_id"], "items": d["items"], "linked_now": d["counts"]["LINKED"],
                                   "already_linked": d["counts"]["NOOP_ALREADY_LINKED"], "orphans": d["orphans"]}
        return out
