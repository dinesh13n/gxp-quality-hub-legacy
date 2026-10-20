"""Versioned rule-trace explanation template (BEH-REV-02, AC-REV-05/06/07; INC-08). Pure: no I/O, no clock, no randomness, no network, no model.

`render(trace)` builds the text from the STORED trace fields only (rule set reference, examined rows with the input values compared, which row
matched, the outcome, the defaulted marker and reason). The same stored fields always give byte-identical text (PNFR-17). The text contains no advice.
Input values are shown as stored; callers that put the text in HTML escape it (`html.escape`), and over-long values are cut with a visible marker.
"""
import json

TEMPLATE_VERSION = "trace_template/1"
VALUE_MAX = 120


def _v(value):
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return text if len(text) <= VALUE_MAX else text[:VALUE_MAX] + "...(cut)"


def render(function, ruleset_ref, authoritative, result):
    """result = the stored rule-result object {outcome, trace[], defaulted, defaulted_reason, ruleset_ref, authoritative}."""
    lines = ["Function %s evaluated with rule set %s%s." % (function, ruleset_ref, "" if authoritative else " (not the active set: what-if)")]
    matched = None
    for t in result.get("trace", []):
        used = ", ".join("%s=%s" % (k, _v(t["inputs_used"][k])) for k in sorted(t.get("inputs_used", {})))
        lines.append("  row %s (#%s): %s; inputs compared: %s" % (t["row_id"], t["ordinal"], "MATCHED" if t["matched"] else "no match",
                                                                 used or "none"))
        if t["matched"] and matched is None:
            matched = t["row_id"]
    lines.append("Matched row: %s." % (matched if matched else "none"))
    lines.append("Outcome: %s." % _v(result.get("outcome")))
    if result.get("defaulted"):
        lines.append("defaulted: %s; the retained as-found value is %s." % (result.get("defaulted_reason"), _v(result.get("outcome"))))
    return "\n".join(lines)
