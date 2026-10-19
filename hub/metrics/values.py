"""Metric values and the ONLY arithmetic / comparison entry points (BEH-MET-02, BEH-MET-03, BEH-MET-04; INC-07). Pure: Decimal only, no clock.

`combine(values, op)` and `compare(a, b)` raise E-MET-TAG-MIX when the inputs carry different definition tags or different policy versions of the
same tag; `side_by_side` shows one labelled column per tag and derives nothing across columns; `trend` flags FAIL-02-conflict and never makes a
cross-definition 'improved' headline. median: mean of the two middle values for even n; p90: nearest rank, ceil(0.9 x n)-th smallest; both are spec
choices (A-12-F07-1). n = 0 gives value None with a reason, never 0.
"""
import csv
import decimal
import io
import json

from hub.metrics.errors import MetNotAvailable, MetTagMix

D = decimal.Decimal
LABEL = "synthetic, unvalidated"
MIX_NOTE = "different definitions - not comparable"
OPS = ("sum", "min", "max")
FIELDS = ("value_id", "metric_id", "metric_version", "definition_tag", "policy_version", "policy_status", "value", "null_reason", "n", "partial",
          "errors", "window_start", "window_end", "denominator", "exclusions", "basis", "data_origin", "label", "inputs_hash", "code_version",
          "computed_at")
METHOD = {"median": "arithmetic mean of the two middle values for even n", "p90": "nearest rank: ceil(0.9 x n)-th smallest value"}


def dtext(d):
    """Canonical text of a Decimal: no exponent, no trailing zeros ('3', '2.5', '100')."""
    s = format(d.normalize(), "f")
    return "0" if s in ("-0", "") else s


def median(values):
    v = sorted(values)
    n = len(v)
    if n == 0:
        return None
    mid = n // 2
    return v[mid] if n % 2 else (v[mid - 1] + v[mid]) / D(2)


def p90(values):
    v = sorted(values)
    n = len(v)
    if n == 0:
        return None
    rank = -(-9 * n // 10)  # ceil(0.9 * n) without floating point
    return v[rank - 1]


def summarise(durations):
    """{'n', 'median', 'p90'} as Decimal / None for a list of Decimal durations."""
    return {"n": len(durations), "median": median(durations), "p90": p90(durations)}


class MetricValue(object):
    def __init__(self, metric_id, metric_version=1, definition_tag=None, policy_version=None, policy_status=None, value=None, null_reason=None, n=0,
                 partial=False, errors=None, window_start=None, window_end=None, denominator="", exclusions="", basis="event_derived",
                 data_origin="synthetic", label=LABEL, inputs_hash="", code_version="", computed_at="", value_id=None, params=None,
                 inputs=None, detail=None):
        self.value_id, self.metric_id, self.metric_version = value_id, metric_id, metric_version
        self.definition_tag, self.policy_version, self.policy_status = definition_tag, policy_version, policy_status
        self.value, self.null_reason, self.n, self.partial = value, null_reason, n, bool(partial)
        self.errors, self.window_start, self.window_end = list(errors or []), window_start, window_end
        self.denominator, self.exclusions, self.basis = denominator, exclusions, basis
        self.data_origin, self.label = data_origin, label
        self.inputs_hash, self.code_version, self.computed_at = inputs_hash, code_version, computed_at
        self.params, self.inputs, self.detail = dict(params or {}), list(inputs or []), dict(detail or {})

    def to_dict(self, with_internals=False):
        d = dict((k, getattr(self, k)) for k in FIELDS)
        if with_internals:
            d.update(params=self.params, inputs=self.inputs, detail=self.detail)
        else:
            d["detail"] = self.detail
        return d

    def decimal(self):
        return None if self.value is None else D(self.value)


def _same_definition(values):
    keys = set((v.definition_tag, v.policy_version) for v in values)
    if len(keys) > 1:
        raise MetTagMix({"definitions": sorted("%s/%s" % k for k in keys), "note": MIX_NOTE})
    return values[0].definition_tag, values[0].policy_version


def combine(values, op="sum"):
    """Arithmetic over values of ONE definition. Different tag or policy version -> E-MET-TAG-MIX. A null input gives a null result."""
    if op not in OPS:
        raise MetNotAvailable({"op": str(op)[:20], "allowed": list(OPS)})
    values = list(values)
    if not values:
        raise MetNotAvailable({"reason": "no values"})
    tag, pol = _same_definition(values)
    first = values[0]
    out = MetricValue("COMBINE-" + op.upper(), 1, tag, pol, first.policy_status, None, None, sum(v.n for v in values),
                      any(v.partial for v in values), [], None, None, "combined: " + "; ".join(sorted(set(v.denominator for v in values))),
                      "; ".join(sorted(set(v.exclusions for v in values))), first.basis, first.data_origin, first.label)
    if any(v.value is None for v in values):
        out.null_reason = "input_null"
        return out
    nums = [v.decimal() for v in values]
    res = sum(nums, D(0)) if op == "sum" else (min(nums) if op == "min" else max(nums))
    out.value = dtext(res)
    return out


def compare(a, b):
    """Comparison of two values of ONE definition: {'relation': '<'|'='|'>', 'difference'}; null input -> relation None."""
    tag, pol = _same_definition([a, b])
    if a.value is None or b.value is None:
        return {"definition_tag": tag, "policy_version": pol, "relation": None, "difference": None, "reason": "input_null"}
    x, y = a.decimal(), b.decimal()
    return {"definition_tag": tag, "policy_version": pol, "relation": "<" if x < y else (">" if x > y else "="),
            "difference": dtext(x - y), "label": a.label}


def side_by_side(values):
    """One labelled column per definition tag; no sum / ratio / difference across columns (AC-MET-04)."""
    cols, seen = [], set()
    for v in values:
        if v.definition_tag in seen:
            raise MetTagMix({"reason": "two columns for the same tag", "tag": v.definition_tag, "note": MIX_NOTE})
        seen.add(v.definition_tag)
        cols.append({"definition_tag": v.definition_tag, "policy_version": v.policy_version, "policy_status": v.policy_status,
                     "value": v.value, "null_reason": v.null_reason, "n": v.n, "label": v.label})
    return {"columns": cols, "note": MIX_NOTE, "derived": None}


def trend(prev_values, curr_values, lower_is_better=True):
    """Per-tag change between two periods. Both improved AND worsened tags -> flag FAIL-02-conflict; there is never a cross-definition headline."""
    prev = dict((v.definition_tag, v) for v in prev_values)
    rows = []
    for c in curr_values:
        p = prev.get(c.definition_tag)
        if p is not None and p.policy_version != c.policy_version:
            direction = "not_comparable_policy_version"
        elif p is None or p.value is None or c.value is None:
            direction = "not_available"
        else:
            x, y = p.decimal(), c.decimal()
            direction = "unchanged" if x == y else ("improved" if (y < x) == lower_is_better else "worsened")
        rows.append({"definition_tag": c.definition_tag, "policy_version": c.policy_version, "previous": None if p is None else p.value,
                     "current": c.value, "direction": direction})
    dirs = set(r["direction"] for r in rows)
    flags = ["FAIL-02-conflict"] if {"improved", "worsened"} <= dirs else []
    headline = None
    if len(rows) == 1 and rows[0]["direction"] in ("improved", "worsened", "unchanged"):
        headline = rows[0]["direction"]  # one definition only: no mixing possible
    return {"rows": rows, "flags": flags, "headline": headline, "note": MIX_NOTE if len(rows) > 1 else None, "label": LABEL}


# ------------------------------------------------------------------------------------------------ renderings (tag, policy version, status, label)
def render_text(v):
    val = v.value if v.value is not None else "null (%s)" % v.null_reason
    return "%s [tag=%s policy=%s status=%s] %s n=%d%s -- %s" % (
        v.metric_id, v.definition_tag, v.policy_version, v.policy_status, val, v.n, " PARTIAL" if v.partial else "", v.label)


def render_json(v, with_computed_at=False):
    d = v.to_dict()
    if not with_computed_at:
        d.pop("computed_at")
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def render_csv(values):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    cols = ("metric_id", "definition_tag", "policy_version", "policy_status", "value", "null_reason", "n", "partial", "label")
    w.writerow(cols)
    for v in values:
        w.writerow([getattr(v, c) if c != "partial" else int(v.partial) for c in cols])
    return buf.getvalue()
