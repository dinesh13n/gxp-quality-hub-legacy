"""Evidence pack (OP-GATE-01, BEH-GATE-03/04, AC-GATE-15/16/17; INC-08): a READ-ONLY, deterministic assembly for one case.

Contents: case header, full state history, linked objects by class (a class with no link is listed as 'none found'), evidence records with
their source, stored rule traces with the status of their flag, open findings, overrides, current policy versions and the active rule sets.
`pack_hash` = sha256 over the canonical JSON of everything else, so two packs of unchanged data are byte-identical, and any new event, evidence,
trace, finding, override, policy or activation changes it (a disposition carrying the old hash is refused: E-GATE-PACK-STALE).

The pack NEVER summarises, scores or recommends: there is no field named decision / disposition / release / recommendation, nothing is pre-selected
and free text is typed {text, trust: untrusted}. No clock, randomness or network is read. This module has no write method and never writes.
"""
import json

from hub.core.untrusted import Untrusted
from hub.decision.errors import CaseNotFound
from hub.security.canonical import canonical, sha256_hex

PACK_VERSION = "pack/1"
LINK_CLASSES = ("batch", "deviation", "capa", "lab_result", "feed_item", "document")
NONE_FOUND = "none found"
_EV_COLS = ("event_id", "case_id", "seq", "event_type", "from_state", "to_state", "affects_state", "actor", "actor_kind", "occurred_at",
            "recorded_at", "basis", "evidence_refs", "cycle", "exception", "closure_check", "mode_at_write", "policy_version",
            "holder_check_ref", "payload", "prev_hash", "hash")


def _t(text, source):
    return Untrusted("" if text is None else text, source).to_wire()


def _history(con, case_id):
    rows = con.execute("SELECT " + ", ".join(_EV_COLS) + " FROM decision_events WHERE case_id = ? ORDER BY seq", (case_id,)).fetchall()
    out = []
    for r in rows:
        e = dict(zip(_EV_COLS, r))
        e["affects_state"], e["exception"] = bool(e["affects_state"]), bool(e["exception"])
        e["evidence_refs"], e["payload"] = json.loads(e["evidence_refs"]), json.loads(e["payload"])
        e["basis"] = _t(e["basis"], "decision_events.basis")
        out.append(e)
    return out


def _linked(con, case_id):
    out = dict((c, []) for c in LINK_CLASSES)
    rows = con.execute("SELECT link_id, from_type, from_id, to_type, to_id, key_used, creator_kind, creator, created_at FROM crosswalk_link"
                       " WHERE (from_type = 'case' AND from_id = ?) OR (to_type = 'case' AND to_id = ?) ORDER BY link_id",
                       (case_id, case_id)).fetchall()
    for lid, ft, fi, tt, ti, key, kind, creator, at in rows:
        if con.execute("SELECT 1 FROM crosswalk_link_event WHERE link_id = ? AND event_type = 'LINK_RETRACTED'", (lid,)).fetchone():
            continue
        other_t, other_i = (tt, ti) if (ft, fi) == ("case", case_id) else (ft, fi)
        if other_t in out:
            out[other_t].append({"link_id": lid, "object_type": other_t, "object_id": other_i, "key_used": key,
                                 "creator_kind": kind, "creator": creator, "created_at": at})
    return dict((c, v if v else NONE_FOUND) for c, v in sorted(out.items()))


def _evidence(con, history):
    ids = []
    for e in history:
        for r in e["evidence_refs"] + ([e["payload"]["ev_id"]] if e["event_type"] == "EVIDENCE_ATTACHED" and "ev_id" in e["payload"] else []):
            if r not in ids:
                ids.append(r)
    out = []
    for ev_id in sorted(ids):
        row = con.execute("SELECT ev_id, kind, source, source_ref, source_hash, access_level, attached_by, attached_at FROM evidence_record"
                          " WHERE ev_id = ?", (ev_id,)).fetchone()
        if row is None:
            out.append({"ev_id": ev_id, "unresolvable": True})
        else:
            out.append({"ev_id": row[0], "kind": row[1], "source": _t(row[2], "evidence_record.source"),
                        "source_ref": _t(row[3], "evidence_record.source_ref"), "source_hash": row[4], "access_level": row[5],
                        "attached_by": row[6], "attached_at": row[7]})
    return out


def flag_status(con, flag_id):
    """'open' or the latest flag action (overridden / dismissed / refused). The original rule output is never changed."""
    row = con.execute("SELECT action FROM flag_action WHERE flag_id = ? ORDER BY rowid DESC LIMIT 1", (flag_id,)).fetchone()
    return "open" if row is None else {"override": "overridden", "dismiss": "dismissed", "refuse": "refused"}[row[0]]


def _traces(con, case_id):
    out = []
    for tid, fid, fn, ref, auth, inputs, result, at in con.execute(
            'SELECT trace_id, flag_id, "function", ruleset_ref, authoritative, inputs, result, recorded_at FROM rule_trace WHERE case_id = ?'
            " ORDER BY trace_id", (case_id,)):
        out.append({"trace_id": tid, "flag_id": fid, "function": fn, "ruleset_ref": ref, "authoritative": bool(auth),
                    "inputs": json.loads(inputs), "result": json.loads(result), "recorded_at": at, "flag_status": flag_status(con, fid)})
    return out


def _findings(con, case_id):
    """Intake items that are in an exception queue AND matched to this case by a crosswalk link, with no human action on their flag."""
    out = []
    for raw_id, seq, queue, reason, link in con.execute(
            "SELECT o.raw_id, o.outcome_seq, o.queue, o.primary_reason, o.matched_link FROM intake_current o JOIN crosswalk_link l"
            " ON l.link_id = o.matched_link WHERE o.queue IS NOT NULL AND ((l.from_type = 'case' AND l.from_id = ?)"
            " OR (l.to_type = 'case' AND l.to_id = ?)) ORDER BY o.raw_id", (case_id, case_id)):
        fid = "FLG-IQ-%s-%d" % (raw_id, seq)
        if flag_status(con, fid) == "open":
            out.append({"flag_id": fid, "raw_id": raw_id, "queue": queue, "primary_reason": reason, "matched_link": link})
    return out


def _overrides(con, case_id):
    out = []
    for aid, fid, kind, action, reason, repl, actor, at, ev in con.execute(
            "SELECT action_id, flag_id, flag_kind, action, reason, replacement, actor, acted_at, event_id FROM flag_action WHERE case_id = ?"
            " ORDER BY action_id", (case_id,)):
        out.append({"action_id": aid, "flag_id": fid, "flag_kind": kind, "action": action, "reason": _t(reason, "flag_action.reason"),
                    "replacement": None if repl is None else json.loads(repl), "actor": actor, "acted_at": at, "event_id": ev})
    return out


def _policies(con):
    out = {}
    for pid, ver, kind, status, tag, owner, ef, et in con.execute(
            "SELECT policy_id, version, kind, status, definition_tag, owner, effective_from, effective_to FROM policy_object p WHERE version ="
            " (SELECT max(version) FROM policy_object q WHERE q.policy_id = p.policy_id) ORDER BY policy_id"):
        out[pid] = {"policy_ref": "%s@%d" % (pid, ver), "kind": kind, "status": status, "definition_tag": tag, "owner": owner,
                    "effective_from": ef, "effective_to": et}
    return out


def _active(con):
    return dict((fn, "%s@%d" % (rid, ver)) for fn, rid, ver in con.execute("SELECT function, ruleset_id, version FROM active_ruleset ORDER BY function"))


def build(con, case_id):
    """The evidence pack of one case (E-DEC-CASE-NOT-FOUND for an unknown case). Read-only."""
    head = con.execute("SELECT state, cycle, last_seq FROM case_state WHERE case_id = ?", (case_id,)).fetchone()
    if head is None:
        raise CaseNotFound({"case_id": str(case_id)[:40]})
    history = _history(con, case_id)
    pack = {"pack_version": PACK_VERSION, "label": "synthetic, unvalidated",
            "case": {"case_id": case_id, "state": head[0], "cycle": head[1], "last_seq": head[2],
                     "created_at": history[0]["occurred_at"] if history else None},
            "history": history, "linked_objects": _linked(con, case_id), "evidence": _evidence(con, history),
            "rule_traces": _traces(con, case_id), "open_findings": _findings(con, case_id) or NONE_FOUND,
            "overrides": _overrides(con, case_id) or NONE_FOUND, "policy_versions": _policies(con), "active_rulesets": _active(con)}
    pack["pack_hash"] = sha256_hex(canonical(pack))
    return pack


def current_hash(con, case_id):
    return build(con, case_id)["pack_hash"]
