"""AD-06 policy-source importer: the three as-found legacy approval rule sets, transcribed into data (A-14-07).

Sources are read as TEXT / DATA only - the legacy code is never imported or executed (adapter-strategy AD-06):
  app/legacy_logic.py                       -> as-found-python  (PRIORITY, MANUAL_REVIEW); constants taken from the AST
  legacy_js/legacy_policy.js                -> as-found-js      (AMOUNT_LIMIT) tolerance factor / fallback from the text
  contracts/decision-policies-archive.json  -> as-found-js      15 historical rows (data file)
  data/enterprise_legacy.sqlite3 (policy_register, operational_objects.status) -> as-found-batch (SHIFT_FLAG), read
                                            through the INC-02 read-only snapshot adapter (sha256 pinned).
Each text source is sha256-pinned in hub/policy/as_found_pins.json; a mismatch, or a constant that is not what the
transcription expects, raises E-POL-ASFOUND-DRIFT (fail closed). Version 1, origin 'as-found', read_only true.
Nothing here activates anything.
"""
import ast
import hashlib
import json
import os
import re

from hub.adapters import legacy_sqlite
from hub.policy.errors import AsFoundDrift
from hub.policy.rulesets import validate

PINS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "as_found_pins.json")
IDS = ("as-found-python", "as-found-js", "as-found-batch")
PY_DOMAINS = {"status": ["OPEN", "UNDER_REVIEW", "CLOSED", "ESCALATED", "REOPENED"],
              "severity": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]}


def _read_pinned(legacy_root, rel):
    with open(os.path.join(legacy_root, rel), "rb") as f:
        body = f.read()
    with open(PINS_PATH, encoding="utf-8") as f:
        want = json.load(f)["sources"][rel]
    got = hashlib.sha256(body).hexdigest()
    if got != want:
        raise AsFoundDrift({"source": rel, "sha256": got, "expected": want})
    return body


def _consts(fn):
    nums = sorted(n.value for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
                  and not isinstance(n.value, bool))
    strs = sorted(set(n.value for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str)))
    return nums, strs


def _row(row_id, ordinal, conditions, function, kind, is_default=0, **outcome):
    o = {"function": function, "kind": kind}
    o.update(outcome)
    return {"row_id": row_id, "ordinal": ordinal, "conditions": conditions, "outcome": o, "effective_from": None,
            "effective_to": None, "owner": None, "is_default": is_default}


def _domain_rows(function, domains, start):
    return [_row("%s-DOM-%s" % (function, f.upper()), start + i, [], function, "domain", field=f, values=list(v))
            for i, (f, v) in enumerate(sorted(domains.items()))]


def build_python(legacy_root):
    body = _read_pinned(legacy_root, "app/legacy_logic.py")
    tree = ast.parse(body.decode("utf-8"))
    fns = dict((n.name, n) for n in tree.body if isinstance(n, ast.FunctionDef))
    p_nums, p_strs = _consts(fns["priority"])
    m_nums, m_strs = _consts(fns["manual_review_required"])
    if p_nums != [50000] or p_strs != ["CLOSED", "CRITICAL", "ESCALATED", "HIGH", "archive", "queue", "review", "urgent"] \
            or m_nums != [] or m_strs != ["CRITICAL", "ESCALATED", "HIGH", "REOPENED"]:
        raise AsFoundDrift({"source": "app/legacy_logic.py", "reason": "constants differ from the transcription",
                            "priority": [p_nums, p_strs], "manual_review_required": [m_nums, m_strs]})
    limit = p_nums[0]
    P, M = "PRIORITY", "MANUAL_REVIEW"
    rows = [
        _row("PY-P1", 1, [{"field": "status", "op": "eq", "value": "CLOSED"}], P, "rule", value="archive"),
        _row("PY-P2", 2, [{"field": "severity", "op": "eq", "value": "CRITICAL"}], P, "rule", value="urgent"),
        _row("PY-P3", 3, [{"field": "amount", "op": "gt", "value": limit}], P, "rule", value="urgent"),
        _row("PY-P4", 4, [{"field": "severity", "op": "eq", "value": "HIGH"}], P, "rule", value="review"),
        _row("PY-P5", 5, [{"field": "status", "op": "eq", "value": "ESCALATED"}], P, "rule", value="review"),
        _row("PY-P6", 6, [], P, "rule", value="queue"),
        _row("PY-M1", 11, [{"field": "severity", "op": "in", "value": ["HIGH", "CRITICAL"]}], M, "rule", value=True),
        _row("PY-M2", 12, [{"field": "status", "op": "in", "value": ["ESCALATED", "REOPENED"]}], M, "rule", value=True),
        _row("PY-M3", 13, [], M, "rule", value=False),
    ] + _domain_rows(P, PY_DOMAINS, 21) + _domain_rows(M, PY_DOMAINS, 31)
    return validate({"ruleset_id": "as-found-python", "version": 1,
                     "name": "As-found Python rules (app/legacy_logic.py: priority > %d, manual review)" % limit,
                     "origin": "as-found", "read_only": True, "functions": [P, M], "rows": rows})


def build_js(legacy_root):
    js = _read_pinned(legacy_root, "legacy_js/legacy_policy.js").decode("utf-8")
    data = json.loads(_read_pinned(legacy_root, "contracts/decision-policies-archive.json").decode("utf-8"))
    m_fb = re.search(r"\?\s*r\.limit\s*:\s*([0-9]+)\s*;", js)
    m_fac = re.search(r"threshold\(region,year\)\*([0-9]+\.[0-9]+)", js)
    if not m_fb or not m_fac or "startsWith(String(year))" not in js or "p.region===region" not in js:
        raise AsFoundDrift({"source": "legacy_js/legacy_policy.js", "reason": "expected threshold/legacyAllows shape not found"})
    A = "AMOUNT_LIMIT"
    rows = []
    for i, v in enumerate(data["historical_versions"], 1):
        r = _row("JS-%02d" % i, i, [{"field": "region", "op": "eq", "value": v["region"]},
                                    {"field": "year", "op": "eq", "value": v["effective_from"][:4]}],
                 A, "rule", value=v["limit"], currency=v["currency"], approval_roles=list(v["approval_roles"]),
                 rule=v["rule"])
        r["effective_from"], r["effective_to"] = v["effective_from"], v["effective_to"]
        rows.append(r)
    rows.append(_row("JS-default", 99, [], A, "rule", is_default=1, value=int(m_fb.group(1)),
                     defaulted_reason="NO_MATCH_REGION_YEAR"))
    rows.append(_row("JS-param-tolerance", 100, [], A, "param", name="tolerance_factor", value=m_fac.group(1)))
    return validate({"ruleset_id": "as-found-js", "version": 1,
                     "name": "As-found JS rules (legacy_js/legacy_policy.js: regional limit x%s, fallback %s)" % (
                         m_fac.group(1), m_fb.group(1)),
                     "origin": "as-found", "read_only": True, "functions": [A], "rows": rows})


def build_batch(legacy_root, run_dir):
    S = "SHIFT_FLAG"
    with legacy_sqlite.open_snapshot(legacy_root, "enterprise_legacy.sqlite3", run_dir, pinned=True) as lg:
        reg = lg.execute("SELECT policy_id, region, policy_code, active, valid_from, valid_to, threshold, owner_team"
                         " FROM policy_register ORDER BY policy_id")
        statuses = [r[0] for r in lg.execute("SELECT DISTINCT status FROM operational_objects ORDER BY status")]
    rows = [
        _row("BATCH-1", 1, [{"field": "status", "op": "in", "value": ["HOLD", "REVIEW"]}], S, "rule", value=True),
        _row("BATCH-2", 2, [{"field": "threshold", "op": "not_null", "value": None},
                            {"field": "value", "op": "gt", "value": {"$input": "threshold"}}], S, "rule", value=True),
        _row("BATCH-3", 3, [], S, "rule", value=False),
    ] + _domain_rows(S, {"status": statuses}, 11)
    for i, (pid, region, code, active, vfrom, vto, thr, owner) in enumerate(reg):
        r = _row(pid, 101 + i, [], S, "register", region=region, policy_code=code, active=int(active), threshold=thr)
        r["effective_from"], r["effective_to"], r["owner"] = vfrom, vto, owner
        rows.append(r)
    return validate({"ruleset_id": "as-found-batch", "version": 1,
                     "name": "As-found night-shift rules (legacy_batch/shift_reconciliation.py: status HOLD/REVIEW or value > "
                             "policy_register threshold)",
                     "origin": "as-found", "read_only": True, "functions": [S], "rows": rows})


def build_all(legacy_root, run_dir):
    """The three as-found documents, in a fixed order. `legacy_root` must be a sandbox copy (the adapter guards it)."""
    return [build_python(legacy_root), build_js(legacy_root), build_batch(legacy_root, run_dir)]
