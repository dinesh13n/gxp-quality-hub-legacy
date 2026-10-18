"""`hub golden-compare` engine (BEH-CO-01, AC-CO-01, AC-CO-02, gate G1, TG-4).

For every probe: legacy value (AD-08, active goldens) vs new value (baseline_ro over read-only snapshots, or
the declared F10-2 target until the owning module exists). Each line is {golden_ref, legacy, new, disposition}:
  identical | approved_deviation(<dev_id>, <approval_ref>) | UNAPPROVED | NOT-RUN
A difference is an approved deviation only if a register row for that golden_ref has status 'approved', a
non-empty approval_ref, AND its legacy_value / new_value equal the observed values (canonical JSON).
Any UNAPPROVED or NOT-RUN line -> exit 6 (E-CO-UNAPPROVED-DEVIATION). Pure and deterministic: no clock,
no randomness, no absolute paths in the report, stable ordering.
"""
import json
import os

from hub.adapters.legacy_captures import CaptureMissing
from hub.coexistence.register import is_approved
from hub.core.errors import UnapprovedDeviation

PROBES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probes_inc02.json")
IDENTICAL, UNAPPROVED, NOT_RUN = "identical", "UNAPPROVED", "NOT-RUN"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load_probes(path=PROBES_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["probes"]


def compare(probes, captures, new_values, register_rows):
    """probes: list; captures: CaptureSet; new_values: {golden_ref: (value, source) or Exception};
    register_rows: list of register dicts. Returns the report dict (exit_code included)."""
    by_ref = {}
    for r in register_rows:
        by_ref.setdefault(r["golden_ref"], []).append(r)
    entries = []
    for p in sorted(probes, key=lambda x: x["golden_ref"]):
        ref = p["golden_ref"]
        e = {"golden_ref": ref}
        try:
            legacy = captures.extract(p["legacy"]["source"], p["legacy"]["path"])
            e["legacy"] = legacy
        except CaptureMissing as ex:
            e.update({"legacy": None, "new": None, "disposition": NOT_RUN, "reason": "legacy capture missing: %s" % ex})
            entries.append(e)
            continue
        nv = new_values.get(ref)
        if nv is None or isinstance(nv, Exception):
            e.update({"new": None, "disposition": NOT_RUN,
                      "reason": "new-side observation unavailable%s" % (": %s" % nv if nv is not None else "")})
            entries.append(e)
            continue
        new, source = nv
        e["new"] = new
        e["new_source"] = source
        rows = sorted(by_ref.get(ref, []), key=lambda r: r["dev_id"])
        if rows:
            e["register"] = [{"dev_id": r["dev_id"], "status": r["status"]} for r in rows]
        if canonical(legacy) == canonical(new):
            e["disposition"] = IDENTICAL
        else:
            match = [r for r in rows if is_approved(r) and r["legacy_value"] == canonical(legacy)
                     and r["new_value"] == canonical(new)]
            if match:
                r = match[0]
                e["disposition"] = "approved_deviation(%s, %s)" % (r["dev_id"], r["approval_ref"])
            else:
                e["disposition"] = UNAPPROVED
        entries.append(e)
    summary = {"identical": 0, "approved_deviation": 0, UNAPPROVED: 0, NOT_RUN: 0, "probes": len(entries)}
    for e in entries:
        d = e["disposition"]
        summary["approved_deviation" if d.startswith("approved_deviation") else d] += 1
    exit_code = 0 if summary[UNAPPROVED] == 0 and summary[NOT_RUN] == 0 else UnapprovedDeviation.exit_code
    return {"schema": "golden-compare/v1", "entries": entries, "summary": summary, "exit_code": exit_code,
            "error": None if exit_code == 0 else UnapprovedDeviation.code}


def render_text(report):
    lines = []
    for e in report["entries"]:
        lines.append("%-40s %s\n    legacy=%s\n    new=%s%s" % (
            e["disposition"], e["golden_ref"], canonical(e.get("legacy")), canonical(e.get("new")),
            ("\n    reason=%s" % e["reason"]) if e.get("reason") else ""))
    s = report["summary"]
    lines.append("summary: probes=%d identical=%d approved_deviation=%d UNAPPROVED=%d NOT-RUN=%d exit=%d" % (
        s["probes"], s["identical"], s["approved_deviation"], s["UNAPPROVED"], s["NOT-RUN"], report["exit_code"]))
    return "\n".join(lines)
