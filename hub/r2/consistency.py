"""Consistency findings (OP-ID-05, BEH-ID-07/08, FR-ID-03, AC-ID-15/16; INC-09).

Rules are ADOPTED `CONSISTENCY` policy objects (F03; adoption is Zone H ZH-05 - none ships adopted, so a fresh install yields zero findings and the
statement 'no consistency policy adopted'). Body:
  {"left":  {"type": "case",  "field": "state",     "in": ["X", ...]},
   "right": {"type": "batch", "field": "qa_status", "in": ["Y", ...]}}
A finding is raised for every pair of entities connected by an ACTIVE crosswalk link whose left value is in left.in AND right value in right.in.
Vocabularies are never mapped (BEH-ID-08): values are compared as stored, per vocabulary. `case.state` comes from the decision projection
(case_state); every other field from the injected read-only `facts(type, id)` provider (the legacy snapshot).
The check writes `consistency_finding` rows idempotently (UNIQUE rule_ref + object_refs + policy_version, INSERT OR IGNORE: running twice gives one
open finding), changes no other state, never auto-corrects, and is audited once per run (CONSISTENCY_CHECK_RUN).
"""
import json

from hub.policy import withdrawal
from hub.r2.errors import R2InputInvalid
from hub.search import schema
from hub.security import audit
from hub.security.errors import AuthForbidden, AuthUnauthenticated

ROLES = ("quality_lead", "compliance")
NONE_ADOPTED = "no consistency policy adopted"
COLS = ("finding_id", "rule_ref", "object_refs", "policy_version", "detected_at", "status", "run_id", "detail")


def adopted_rules(con, as_of=None):
    """Adopted CONSISTENCY rules; with `as_of` (ISO timestamp) a version whose withdrawal is in effect is skipped (Stage 20 DW-07)."""
    rows = con.execute("SELECT policy_id, version, body FROM policy_object WHERE kind = 'CONSISTENCY' AND status = 'adopted' ORDER BY policy_id, version")
    return [{"policy_id": r[0], "version": r[1], "body": json.loads(r[2])} for r in rows
            if as_of is None or not withdrawal.effective(con, "%s@%d" % (r[0], r[1]), as_of)]


def _side(body, name):
    s = body.get(name)
    if not isinstance(s, dict) or not isinstance(s.get("type"), str) or not isinstance(s.get("field"), str) or not isinstance(s.get("in"), list):
        raise R2InputInvalid({"reason": "CONSISTENCY body needs %s {type, field, in[]}" % name})
    return s


def _value(con, facts, t, i, field):
    if t == "case" and field == "state":
        r = con.execute("SELECT state FROM case_state WHERE case_id = ?", (i,)).fetchone()
        return r[0] if r else None
    rec = facts(t, i) if facts else None
    return None if not rec else rec.get(field)


def _pairs(con, lt, rt):
    q = ("SELECT l.from_type, l.from_id, l.to_type, l.to_id FROM crosswalk_link l WHERE ((l.from_type = ? AND l.to_type = ?) OR (l.from_type = ? AND"
         " l.to_type = ?)) AND NOT EXISTS (SELECT 1 FROM crosswalk_link_event e WHERE e.link_id = l.link_id AND e.event_type = 'LINK_RETRACTED')"
         " ORDER BY l.link_id")
    out = []
    for ft, fi, tt, ti in con.execute(q, (lt, rt, rt, lt)):
        out.append((fi, ti) if ft == lt else (ti, fi))
    return sorted(set(out))


def run(con, clock, anchor, actor, facts=None, run_id="consistency", correlation_id="consistency"):
    """Operator / job entry (host operator, like the INC-07 jobs). Returns {rules, findings_new, findings_open, statement?}."""
    schema.require(con)
    rules = adopted_rules(con, clock())
    if not rules:
        audit.append(con, clock, anchor=anchor, actor=actor, actor_kind="system" if actor == "hub" else "human", action="CONSISTENCY_CHECK_RUN",
                     outcome="success", correlation_id=correlation_id, object_ref="OP-ID-05", details={"rules": 0, "new": 0, "statement": NONE_ADOPTED})
        return {"rules": 0, "findings_new": 0, "findings_open": open_count(con), "statement": NONE_ADOPTED, "run_id": run_id}
    new = 0
    with audit.change(con, clock, anchor=anchor, actor=actor, actor_kind="system" if actor == "hub" else "human", action="CONSISTENCY_CHECK_RUN",
                      outcome="success", correlation_id=correlation_id, object_ref="OP-ID-05", details={}) as ctx:
        now = clock()
        for r in rules:
            left, right = _side(r["body"], "left"), _side(r["body"], "right")
            ref = "%s@%d" % (r["policy_id"], r["version"])
            for li, ri in _pairs(con, left["type"], right["type"]):
                lv, rv = _value(con, facts, left["type"], li, left["field"]), _value(con, facts, right["type"], ri, right["field"])
                if lv in left["in"] and rv in right["in"]:
                    objs = json.dumps(sorted(["%s:%s" % (left["type"], li), "%s:%s" % (right["type"], ri)]), separators=(",", ":"))
                    fid = "FND-%08d" % (con.execute("SELECT count(*) FROM consistency_finding").fetchone()[0] + 1)
                    cur = con.execute("INSERT OR IGNORE INTO consistency_finding(" + ", ".join(COLS) + ") VALUES (?,?,?,?,?,?,?,?)",
                                      (fid, ref, objs, str(r["version"]), now, "open", run_id,
                                       json.dumps({left["type"] + "." + left["field"]: lv, right["type"] + "." + right["field"]: rv}, sort_keys=True)))
                    new += cur.rowcount
        ctx.fields["details"] = {"rules": len(rules), "new": new, "run_id": run_id}
    return {"rules": len(rules), "findings_new": new, "findings_open": open_count(con), "run_id": run_id}


def open_count(con):
    return con.execute("SELECT count(*) FROM consistency_finding WHERE status = 'open'").fetchone()[0]


def list_findings(con, sess):
    """OP-ID-05 (FindingPage)."""
    if sess is None:
        raise AuthUnauthenticated()
    if not any(r in sess.principal.roles for r in ROLES):
        raise AuthForbidden({"reason": "role"})
    schema.require(con)
    rows = con.execute("SELECT " + ", ".join(COLS) + " FROM consistency_finding ORDER BY finding_id").fetchall()
    items = []
    for row in rows:
        d = dict(zip(COLS, row))
        d["object_refs"], d["detail"] = json.loads(d["object_refs"]), json.loads(d["detail"])
        items.append(d)
    out = {"items": items, "label": "synthetic, unvalidated"}
    if not adopted_rules(con):
        out["statement"] = NONE_ADOPTED
    return out
