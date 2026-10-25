"""Trace reconstruction from the structured log (Stage 31; docs/31-observability/tracing-spec.md).

The hub has no span ids and no tracing library (dependency deny-list, ADR-016): the correlation id that BEH-OBS-01 puts on every log line, audit record and
error envelope IS the trace id, and each log line is a span (event, op_id, duration_ms, outcome, error_code). `build_traces` groups parsed lines by
correlation id, orders them by timestamp (ties keep input order) and summarises each trace. Lines that are not valid JSON objects, carry fields outside
the log whitelist, or contain prohibited content (hub.obs.log.prohibited_findings) are counted and dropped, never reproduced. Pure function.
"""
import json

from hub.obs import log as obslog

SEVERITY = {"success": 0, "denied": 1, "error": 2, None: 0}


def parse_lines(lines):
    """-> (records, rejected) - `rejected` counts lines dropped for any of the reasons above."""
    records, rejected = [], 0
    for line in lines:
        try:
            rec = json.loads(line)
        except (TypeError, ValueError):
            rejected += 1
            continue
        if not isinstance(rec, dict) or set(rec) - set(obslog.FIELDS) or obslog.prohibited_findings([line]):
            rejected += 1
            continue
        records.append(rec)
    return records, rejected


def _summary(spans):
    ms = [s["duration_ms"] for s in spans if isinstance(s.get("duration_ms"), (int, float))]
    worst = max(spans, key=lambda s: SEVERITY.get(s.get("outcome"), 0))
    return {"spans": len(spans), "first_ts": spans[0].get("ts"), "last_ts": spans[-1].get("ts"), "total_span_ms": round(sum(ms), 3),
            "outcome": worst.get("outcome"), "error_codes": sorted(set(s["error_code"] for s in spans if s.get("error_code"))),
            "events": [s.get("event") for s in spans]}


def build_traces(lines):
    """-> {"traces": {correlation_id: summary + spans}, "uncorrelated": n, "rejected": n}."""
    records, rejected = parse_lines(lines)
    groups, loose = {}, 0
    for i, rec in enumerate(records):
        cid = rec.get("correlation_id")
        if not cid or cid == "redacted":
            loose += 1
            continue
        groups.setdefault(cid, []).append((str(rec.get("ts")), i, rec))
    traces = {}
    for cid, items in sorted(groups.items()):
        spans = [r for _, _, r in sorted(items, key=lambda t: (t[0], t[1]))]
        traces[cid] = dict(_summary(spans), span_list=spans)
    return {"traces": traces, "uncorrelated": loose, "rejected": rejected}
