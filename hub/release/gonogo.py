"""Go / no-go evaluation (Stage 30). Pure functions over two JSON documents; no clock, no store, no network, no write.

  results document     {"schema": "hub-release-results/v1", "results": {"<criterion id>": {"result": pass|fail|not_run, "evidence_path": "...", "note": "..."}}}
  approvals document   {"schema": "hub-release-approvals/v1", "records": [{"id", "status": OPEN|APPROVED|REJECTED, "approver", "approval_ref", "approved_on", "evidence_ref"}]}

A criterion that has no result counts as not_run. An approval counts only when its record is APPROVED *and* valid: a named human approver (never an agent,
orchestrator or system name), a non-empty approval reference, an ISO date and a pointer to where the decision is recorded. The hub cannot verify that the
reference exists or that the approver is who they say (the same limit as hub.control.flags): this is a gate against an EMPTY or machine-written approval,
not a proof of identity. The decision is GO only when no technical criterion blocks and every required approval counts; anything else is NO-GO.
"""
import re

from hub.control import flags
from hub.release import register
from hub.security import settings

RESULTS = ("pass", "fail", "not_run")
STATUSES = ("OPEN", "APPROVED", "REJECTED")
DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
NOT_A_HUMAN = frozenset(("claude", "agent", "orchestrator", "assistant", "bot", "system", "ai", "llm", "anthropic", "automation", "pipeline", "ci", "hub"))
RESULTS_SCHEMA = "hub-release-results/v1"
APPROVALS_SCHEMA = "hub-release-approvals/v1"


class RegisterInvalid(ValueError):
    """A results or approvals document that cannot be evaluated (unknown id, duplicate id, bad schema, bad status)."""


def _tokens(text):
    return set(t for t in re.split(r"[^a-z0-9]+", str(text).lower()) if t)


def _date_ok(text):
    m = DATE_RE.match(text) if isinstance(text, str) else None
    return bool(m) and 1 <= int(m.group(2)) <= 12 and 1 <= int(m.group(3)) <= 31


def approval_problems(rec):
    """Reasons an APPROVED record does not count ([] = it counts). Other statuses never count and need no reasons."""
    out = []
    who = rec.get("approver")
    if not isinstance(who, str) or not who.strip():
        out.append("no approver")
    elif _tokens(who) & NOT_A_HUMAN:
        out.append("approver is not a named human")
    if not flags.valid_ref(rec.get("approval_ref")):
        out.append("no approval reference")
    if not _date_ok(rec.get("approved_on")):
        out.append("no ISO approval date")
    if not flags.valid_ref(rec.get("evidence_ref")):
        out.append("no pointer to where the decision is recorded")
    return out


def check_approvals_doc(doc):
    if not isinstance(doc, dict) or doc.get("schema") != APPROVALS_SCHEMA or not isinstance(doc.get("records"), list):
        raise RegisterInvalid("approvals document: wrong schema or no records list")
    ids = [r.get("id") if isinstance(r, dict) else None for r in doc["records"]]
    if len(set(ids)) != len(ids):
        raise RegisterInvalid("approvals document: duplicate id")
    unknown = sorted(str(i) for i in ids if i not in register.approval_ids())
    if unknown:
        raise RegisterInvalid("approvals document: unknown id %s" % unknown[:3])
    for r in doc["records"]:
        if r.get("status") not in STATUSES:
            raise RegisterInvalid("approvals document: bad status for %s" % r["id"])
    return {r["id"]: r for r in doc["records"]}


def check_results_doc(doc):
    if not isinstance(doc, dict) or doc.get("schema") != RESULTS_SCHEMA or not isinstance(doc.get("results"), dict):
        raise RegisterInvalid("results document: wrong schema or no results object")
    for k, v in doc["results"].items():
        if k not in register.TECHNICAL_IDS:
            raise RegisterInvalid("results document: unknown criterion %r" % str(k)[:40])
        if not isinstance(v, dict) or v.get("result") not in RESULTS:
            raise RegisterInvalid("results document: bad result for %s" % k)
    return doc["results"]


def technical(results):
    rows = []
    for cid in register.TECHNICAL_IDS:
        r = results.get(cid) or {}
        res = r.get("result", "not_run")
        rows.append({"id": cid, "result": res, "evidence_path": r.get("evidence_path"), "blocking": res != "pass"})
    return rows


def approval_state(by_id, ids):
    """For each id: counts (APPROVED and valid), or why it does not."""
    rows = []
    for aid in ids:
        rec = by_id.get(aid) or {"status": "OPEN"}
        problems = approval_problems(rec) if rec["status"] == "APPROVED" else []
        counts = rec["status"] == "APPROVED" and not problems
        rows.append({"id": aid, "status": rec["status"], "counts": counts, "problems": problems})
    return rows


def evaluate(results_doc, approvals_doc):
    results, by_id = check_results_doc(results_doc), check_approvals_doc(approvals_doc)
    tech = technical(results)
    tech_blocking = [t["id"] for t in tech if t["blocking"]]
    rel = approval_state(by_id, register.required_for_release())
    rel_missing = [a["id"] for a in rel if not a["counts"]]
    release_go = not tech_blocking and not rel_missing
    steps = {}
    for cid in register.CUT_IDS:
        need = approval_state(by_id, register.required_for_step(cid))
        miss = [a["id"] for a in need if not a["counts"]]
        steps[cid] = {"decision": "GO" if release_go and not miss else "NO-GO", "approvals_missing": miss, "release_go": release_go}
    invalid = [a["id"] for a in approval_state(by_id, sorted(by_id)) if a["status"] == "APPROVED" and not a["counts"]]
    return {"decision": "GO" if release_go else "NO-GO", "technical_blocking": tech_blocking, "technical": tech,
            "release_approvals_missing": rel_missing, "steps": steps, "invalid_approved_records": invalid,
            "counts": {"technical": len(tech), "technical_pass": len(tech) - len(tech_blocking),
                       "approvals": len(register.approval_ids()), "approvals_counting": sum(1 for a in approval_state(by_id, register.approval_ids()) if a["counts"])}}


def posture(cfg):
    """Posture checks over a LOADED hub config (hub.config.load). -> list of violations ([] = shadow, empty Zone H holders, loopback, schedule off, synthetic)."""
    sec = settings.resolve(cfg)
    out = ["non-default decision flag: %s" % p for p, _, _ in flags.nondefault(cfg)]
    checks = (
        (sec["zone_h"]["holders"] != [], "zone_h.holders is not empty"),
        (sec["network"]["exposure_approved"] is not False, "network exposure approved"),
        (sec["network"]["bind"] not in ("127.0.0.1", "localhost", "::1"), "bind is not loopback"),
        (flags.get(cfg, "schedule.enabled", False) is not False, "schedule enabled"),
        (cfg.get("data_origin", "synthetic") != "synthetic", "data_origin is not synthetic"),
        (flags.get(cfg, "hub.kill", False) is not False, "kill switch set"),
        (bool(cfg.get(flags.APPROVALS_KEY)), "approval_refs present"),
    )
    return out + [msg for bad, msg in checks if bad]
