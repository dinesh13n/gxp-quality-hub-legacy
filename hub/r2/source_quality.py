"""Per-source data quality: unmatched reference rate and reconciliation delay (OP-MET-06, BEH-MET-10, FR-MET-07, AC-MET-19; INC-09).

  unmatched_reference_rate  = items whose current reasons contain UNMATCHED_REF or NO_BUSINESS_KEY / validated items (current outcome VALIDATED,
                              VALIDATED_WITH_FLAGS or EXCEPTION - quarantined items never reached matching), per source
  reconciliation_delay      = distribution (n, min, p50, p95, max; nearest-rank, hours, exact decimal) of RUN_FINISHED.occurred_at of the run that
                              produced the item's FIRST outcome minus the item's receipt_time, per source
Optional period: receipt_time in [window_start, window_end). Read-only, computed AS OF a data instant passed by the caller (the HTTP surface uses the
newest record time, INC-08 D-10), so two identical calls give identical JSON (reproducible: `inputs_hash` covers every input row). Not stored.
"""
import decimal
import hashlib
import json
import math

import hub
from hub.r2.intake_reports import hours_between, parse_ts

METRIC_ID, METRIC_VERSION = "source_quality", 1
VALIDATED = ("VALIDATED", "VALIDATED_WITH_FLAGS", "EXCEPTION")
UNMATCHED = ("UNMATCHED_REF", "NO_BUSINESS_KEY")
CODE_VERSION = "%s+inc09" % hub.__version__


def _pct(sorted_vals, p):
    if not sorted_vals:
        return None
    k = max(1, int(math.ceil(p / 100.0 * len(sorted_vals))))
    return str(sorted_vals[k - 1])


def _rate(num, den):
    return None if den == 0 else str((decimal.Decimal(num) / decimal.Decimal(den)).quantize(decimal.Decimal("0.0001")))


def compute(con, as_of, window_start=None, window_end=None, source=None):
    q = ("SELECT r.raw_id, r.source, r.receipt_time, c.outcome, c.all_reasons,"
         " (SELECT max(e.occurred_at) FROM intake_outcome o1 JOIN intake_run_event e ON e.run_id = o1.run_id AND e.event_type = 'RUN_FINISHED'"
         "   WHERE o1.raw_id = r.raw_id AND o1.outcome_seq = 1)"
         " FROM raw_intake r JOIN intake_current c ON c.raw_id = r.raw_id WHERE 1=1")
    args = []
    if source:
        q += " AND r.source = ?"
        args.append(source)
    if window_start:
        q += " AND r.receipt_time >= ?"
        args.append(window_start)
    if window_end:
        q += " AND r.receipt_time < ?"
        args.append(window_end)
    rows = con.execute(q + " ORDER BY r.source, r.raw_id", args).fetchall()
    per, h = {}, hashlib.sha256()
    for raw_id, src, receipt, outcome, reasons, ended in rows:
        h.update(("%s|%s|%s|%s|%s|%s\n" % (raw_id, src, receipt, outcome, reasons, ended)).encode("utf-8"))
        s = per.setdefault(src, {"validated": 0, "unmatched": 0, "delays": [], "no_run_end": 0})
        if outcome in VALIDATED:
            s["validated"] += 1
            if set(json.loads(reasons or "[]")) & set(UNMATCHED):
                s["unmatched"] += 1
        rt, et = parse_ts(receipt), parse_ts(ended)
        if rt is None or et is None:
            s["no_run_end"] += 1
        else:
            s["delays"].append(hours_between(rt, et))
    detail, tot_v, tot_u = {}, 0, 0
    for src in sorted(per):
        s = per[src]
        d = sorted(s["delays"])
        tot_v, tot_u = tot_v + s["validated"], tot_u + s["unmatched"]
        detail[src] = {"validated_items": s["validated"], "unmatched_items": s["unmatched"], "unmatched_reference_rate": _rate(s["unmatched"], s["validated"]),
                       "reconciliation_delay_hours": {"n": len(d), "min": str(d[0]) if d else None, "p50": _pct(d, 50), "p95": _pct(d, 95),
                                                      "max": str(d[-1]) if d else None, "method": "nearest-rank"},
                       "items_without_run_end": s["no_run_end"]}
    ih = h.hexdigest()
    value = _rate(tot_u, tot_v)
    return {"value_id": "MV-R2-%s" % hashlib.sha256((ih + "|" + str(as_of) + "|" + str(window_start) + "|" + str(window_end)).encode()).hexdigest()[:16],
            "metric_id": METRIC_ID, "metric_version": METRIC_VERSION, "definition_tag": None, "policy_version": None, "policy_status": None,
            "value": value, "null_reason": None if value is not None else "no validated items in scope", "n": tot_v, "partial": False, "errors": [],
            "window_start": window_start, "window_end": window_end or as_of,
            "denominator": "validated items (current outcome VALIDATED, VALIDATED_WITH_FLAGS or EXCEPTION)",
            "exclusions": "quarantined and duplicate (NOOP_DUPLICATE) deliveries", "basis": "event_derived", "data_origin": "synthetic",
            "label": "synthetic, unvalidated", "inputs_hash": ih, "code_version": CODE_VERSION, "computed_at": as_of,
            "detail": {"per_source": detail, "rows": len(rows)}}
