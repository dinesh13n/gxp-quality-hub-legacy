"""ReviewService (C10, F08; INC-08): exception queue (BEH-REV-01), stored rule-trace explanations (BEH-REV-02).

Reads only. The one write is `record_trace` (an insert-only rule_trace row + one audit record) which stores a rule evaluation that someone else
computed; it decides nothing. This module imports nothing from hub.gate or hub.decision.service, so no reviewer-support call can reach a Zone H write
(AC-GATE-11). Free text (intake notes) is returned as {text, trust: untrusted} plus an escaped copy and the label 'untrusted source text'.
"""
import datetime
import html
import json
import re

from hub.core.untrusted import Untrusted
from hub.decision.errors import CaseNotFound
from hub.policy.errors import NoActiveRuleset
from hub.review import templates
from hub.review.errors import QueryInvalid, ReviewNotFound
from hub.security import audit
from hub.security.canonical import canonical, fmt, parse
from hub.security.errors import AuthForbidden, AuthUnauthenticated
from hub.store import m006 as web_schema  # Stage 20 DW-06: no hub.web import

QUEUE_ROLES = ("reviewer", "quality_lead", "compliance", "integration")
TRACE_ROLES = ("reviewer", "quality_lead", "compliance", "dispositioner")
QUEUES = ("quarantine_invalid", "revision_review", "unmatched", "ambiguous_match", "flagged_value")
LIMIT_DEFAULT, LIMIT_MAX = 50, 100
NOTE_MAX = 200
UNTRUSTED_LABEL = "untrusted source text"
_CURSOR = re.compile(r"^[0-9T:.Z-]{20,32}\|RAW-[0-9]{10}$")
_REASON = re.compile(r"^[A-Z_]{3,40}$")
_SOURCE = re.compile(r"^[A-Za-z0-9._:-]{1,60}$")


class ReviewService(object):
    def __init__(self, con, s, clock, anchor=None):
        self.con, self.s, self.clock, self.anchor = con, s, clock, anchor
        web_schema.require(con)

    def _need_roles(self, sess, roles, cid, op):
        if sess is None:
            raise AuthUnauthenticated()
        p = sess.principal
        if any(r in p.roles for r in roles):
            return p
        audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="AUTHZ_DENIED",
                     outcome="denied", correlation_id=cid, object_ref=op, details={"reason": "role", "needs_one_of": list(roles)})
        raise AuthForbidden({"reason": "role"})

    # ------------------------------------------------------------------ OP-REV-01
    def queue(self, sess, queue=None, reason=None, source=None, min_age_hours=None, limit=None, cursor=None, correlation_id="review"):
        """Every item whose CURRENT outcome has a queue (NOOP_DUPLICATE excluded by the intake_current view), once, oldest first."""
        self._need_roles(sess, QUEUE_ROLES, correlation_id, "OP-REV-01")
        if queue is not None and queue not in QUEUES:
            raise QueryInvalid({"field": "queue", "allowed": list(QUEUES)})
        if reason is not None and not _REASON.match(str(reason)):
            raise QueryInvalid({"field": "reason"})
        if source is not None and not _SOURCE.match(str(source)):
            raise QueryInvalid({"field": "source"})
        try:
            limit = LIMIT_DEFAULT if limit is None else int(limit)
        except (TypeError, ValueError):
            raise QueryInvalid({"field": "limit"})
        limit = max(1, min(limit, LIMIT_MAX))
        if min_age_hours is not None:
            try:
                min_age_hours = float(min_age_hours)
            except (TypeError, ValueError):
                raise QueryInvalid({"field": "min_age_hours"})
        if cursor is not None and not _CURSOR.match(str(cursor)):
            raise QueryInvalid({"field": "cursor"})
        now = parse(self.clock()).timestamp()
        where, args = ["o.queue IS NOT NULL"], []
        if queue:
            where.append("o.queue = ?")
            args.append(queue)
        if reason:
            where.append("EXISTS (SELECT 1 FROM json_each(o.all_reasons) j WHERE j.value = ?)")
            args.append(reason)
        if source:
            where.append("r.source = ?")
            args.append(source)
        if min_age_hours is not None:
            cutoff = fmt(parse(self.clock()) - datetime.timedelta(hours=min_age_hours))
            where.append("r.receipt_time <= ?")
            args.append(cutoff)
        base = ("FROM intake_current o JOIN raw_intake r ON r.raw_id = o.raw_id LEFT JOIN intake_item_attr a ON a.raw_id = o.raw_id"
                " WHERE " + " AND ".join(where))
        total = self.con.execute("SELECT count(*) " + base, args).fetchone()[0]
        page_where, page_args = "", list(args)
        if cursor:
            ts, raw = cursor.split("|")
            page_where = " AND (r.receipt_time > ? OR (r.receipt_time = ? AND o.raw_id > ?))"
            page_args += [ts, ts, raw]
        rows = self.con.execute("SELECT o.raw_id, o.outcome_seq, o.primary_reason, o.all_reasons, o.queue, r.source, r.receipt_time, o.matched_link,"
                                " a.notes " + base + page_where + " ORDER BY r.receipt_time ASC, o.raw_id ASC LIMIT ?",
                                page_args + [limit + 1]).fetchall()
        more = len(rows) > limit
        rows = rows[:limit]
        items = [self._queue_item(r, now) for r in rows]
        nxt = "%s|%s" % (rows[-1][6], rows[-1][0]) if more else None
        return {"items": items, "next": nxt, "total": total, "limit": limit, "label": "synthetic, unvalidated"}

    def _queue_item(self, r, now):
        raw_id, seq, primary, reasons, queue, source, receipt, link, notes = r
        case = None
        if link:
            l = self.con.execute("SELECT from_type, from_id, to_type, to_id FROM crosswalk_link WHERE link_id = ?", (link,)).fetchone()
            if l:
                case = l[1] if l[0] == "case" else (l[3] if l[2] == "case" else None)
        item = {"raw_id": raw_id, "primary_reason": primary, "all_reasons": json.loads(reasons), "queue": queue, "source": source,
                "receipt_time": receipt, "age_hours": round((now - parse(receipt).timestamp()) / 3600.0, 6), "matched_case": case,
                "flag_id": "FLG-IQ-%s-%d" % (raw_id, seq)}
        if notes is not None:
            u = Untrusted(notes[:NOTE_MAX], "intake")
            item["notes"] = {"text": u.for_storage(), "trust": "untrusted", "text_escaped": u.escaped(), "label": UNTRUSTED_LABEL,
                             "truncated": len(notes) > NOTE_MAX}
        else:
            item["notes"] = None
        return item

    def all_queue_raw_ids(self):
        """Test / report helper: raw ids of every item whose current outcome has a queue (AC-REV-02 compares this with the view)."""
        return [r[0] for r in self.con.execute("SELECT raw_id FROM intake_current WHERE queue IS NOT NULL ORDER BY raw_id")]

    # ------------------------------------------------------------------ OP-REV-02
    def record_trace(self, actor, actor_kind, case_id, function, ruleset_ref, inputs, result, correlation_id="review"):
        """Store a rule evaluation for a case (insert-only) with a new flag_id. `result` is the rule-result object an evaluator returned."""
        if actor_kind not in ("human", "system", "rule"):
            raise QueryInvalid({"field": "actor_kind"})
        if self.con.execute("SELECT 1 FROM case_state WHERE case_id = ?", (case_id,)).fetchone() is None:
            raise CaseNotFound({"case_id": str(case_id)[:40]})
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind=actor_kind, action="RULE_TRACE_RECORDED",
                          outcome="success", correlation_id=correlation_id, object_ref="case:%s" % case_id, details={}) as ctx:
            n = self.con.execute("SELECT count(*) FROM rule_trace").fetchone()[0] + 1
            tid, fid = "RT-%08d" % n, "FLG-RT-%08d" % n
            self.con.execute('INSERT INTO rule_trace(trace_id, flag_id, case_id, "function", ruleset_ref, authoritative, inputs, result,'
                             " template_version, recorded_at, recorded_by) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                             (tid, fid, case_id, function, ruleset_ref, 1 if result.get("authoritative") else 0, canonical(inputs),
                              canonical(result), templates.TEMPLATE_VERSION, self.clock(), actor))
            ctx.fields["details"] = {"trace_id": tid, "flag_id": fid, "function": function, "ruleset_ref": ruleset_ref}
        return {"trace_id": tid, "flag_id": fid}

    def explanations(self, sess, case_id, correlation_id="review"):
        self._need_roles(sess, TRACE_ROLES, correlation_id, "OP-REV-02")
        if self.con.execute("SELECT 1 FROM case_state WHERE case_id = ?", (case_id,)).fetchone() is None:
            raise CaseNotFound({"case_id": str(case_id)[:40]})
        rows = self.con.execute('SELECT trace_id, flag_id, "function", ruleset_ref, authoritative, inputs, result FROM rule_trace'
                                " WHERE case_id = ? ORDER BY trace_id", (case_id,)).fetchall()
        if not rows and not self.con.execute("SELECT 1 FROM active_ruleset").fetchone():
            raise NoActiveRuleset({"case_id": case_id, "reason": "no stored trace and no active rule set"})
        out = []
        for tid, fid, fn, ref, auth, inputs, result in rows:
            res = json.loads(result)
            text = templates.render(fn, ref, bool(auth), res)
            st = self.con.execute("SELECT action FROM flag_action WHERE flag_id = ? ORDER BY rowid DESC LIMIT 1", (fid,)).fetchone()
            out.append({"trace_id": tid, "function": fn, "ruleset_ref": ref, "text": text, "text_escaped": html.escape(text, quote=True),
                        "template_version": templates.TEMPLATE_VERSION, "defaulted": bool(res.get("defaulted")),
                        "defaulted_reason": res.get("defaulted_reason"), "flag_id": fid,
                        "flag_status": "open" if st is None else {"override": "overridden", "dismiss": "dismissed", "refuse": "refused"}[st[0]],
                        "actions": ["override", "dismiss", "refuse"], "label": "synthetic, unvalidated"})
        return {"case_id": case_id, "explanations": out}

    def trace_flag(self, flag_id):
        r = self.con.execute("SELECT trace_id FROM rule_trace WHERE flag_id = ?", (flag_id,)).fetchone()
        if r is None:
            raise ReviewNotFound({"flag_id": str(flag_id)[:60]})
        return r[0]
