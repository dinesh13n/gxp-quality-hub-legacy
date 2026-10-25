"""Metric catalogue and telemetry lint (Stage 31; observability-spec OBS-4; privacy-safe telemetry).

The catalogue is DATA: every metric the hub can export, its kind, its closed set of label names and where it comes from
(`implemented` = exported today by hub.obs.collect / hub.web.obs_http, `built_unwired` = produced by a Stage 31 function nobody calls by default,
`gap` = specified in OBS-4 but not exported yet). `lint_samples` is the privacy and schema check for a list of samples (the dicts produced by
hub.obs.collect): unknown metric, wrong kind, label names outside the closed set, label values that are not identifier-shaped, values that are not
numbers (or the closed histogram shape), prohibited content (the AC-OBS-04 patterns) and label cardinality. A finding names the sample position and
the kind of problem; the offending text is never echoed, so a lint report cannot itself leak what it found. Pure functions: no clock, no I/O.
"""
import json
import re

from hub.obs import log as obslog
from hub.security.canonical import canonical

MAX_SERIES_PER_METRIC = 500     # Assumption A-31-05: a label set that grows past this is a cardinality defect, not data
LABEL_VALUE = re.compile(r"^[A-Za-z0-9._:@#=-]{1,80}$")
NUMBER = re.compile(r"^-?[0-9]{1,18}(\.[0-9]{1,9})?$")
HISTOGRAM_KEYS = ("count", "max_ms", "max_s", "sum_ms", "sum_s")

IMPLEMENTED, BUILT_UNWIRED, GAP = "implemented", "built_unwired", "gap"


def _m(kind, labels, source, purpose, kinds=None):
    return {"kinds": tuple(kinds or (kind,)), "labels": tuple(labels), "source": source, "purpose": purpose}


CATALOG = {
    # exported today by hub.obs.collect (INC-07)
    "intake_items_total": _m("counter", ("source", "outcome"), IMPLEMENTED, "PNFR-11 intake volume by outcome"),
    "intake_noop_duplicate_total": _m("counter", ("source",), IMPLEMENTED, "FR-INT-02 replay evidence"),
    "quarantine_depth": _m("gauge", ("queue",), IMPLEMENTED, "FR-REV-02 quarantine depth"),
    "exception_queue_depth": _m("gauge", ("queue",), IMPLEMENTED, "BR-12 exception queue depth"),
    "decision_events_total": _m("counter", ("event_type",), IMPLEMENTED, "decision volume"),
    "zone_h_attempts_total": _m("counter", ("action", "outcome"), IMPLEMENTED, "FR-GATE-01 Zone H attempts"),
    "zone_h_service_actor_rejections_total": _m("counter", ("action",), IMPLEMENTED, "AC-GATE-09 evidence"),
    "zone_h_service_actor_accepted": _m("counter", (), IMPLEMENTED, "tripwire, must be 0 (FR-GATE-03)"),
    "run_duration_seconds": _m("histogram", ("job",), IMPLEMENTED, "PNFR-02 run duration", kinds=("histogram", "gauge")),
    "run_backlog_remaining": _m("gauge", ("job",), IMPLEMENTED, "FR-RUN-03 backlog"),
    "run_missed_total": _m("counter", ("job",), IMPLEMENTED, "PNFR-14 missed runs (schedule enabled only)"),
    "model_calls_total": _m("counter", (), IMPLEMENTED, "tripwire, must be 0 (PNFR-18, OD-08)"),
    "egress_attempts_total": _m("counter", (), IMPLEMENTED, "tripwire, must be 0 (FR-CO-04)"),
    "search_engine": _m("gauge", ("engine",), IMPLEMENTED, "OD-S12-12 search engine in use"),
    # exported today by hub.web.obs_http (INC-08)
    "http_requests_total": _m("counter", ("op_id", "status"), IMPLEMENTED, "PNFR-01 availability proxy"),
    "http_request_duration_ms": _m("histogram", ("op_id",), IMPLEMENTED, "PNFR-06 latency (measure-only)"),
    "auth_failures_total": _m("counter", ("reason",), IMPLEMENTED, "PNFR-07 authentication failures"),
    "override_total": _m("counter", ("action",), IMPLEMENTED, "PNFR-15 override rate"),
    "defaulted_outputs_total": _m("counter", ("function",), IMPLEMENTED, "FR-POL-06 defaulted outputs"),
    # Stage 31: resilience telemetry (hub.obs.resilience_samples; not called by any shipped command, S31-DEV-01)
    "resilience_breaker_state": _m("gauge", ("dependency",), BUILT_UNWIRED, "0 closed, 1 open, 2 half-open"),
    "resilience_breaker_opened_total": _m("counter", ("dependency",), BUILT_UNWIRED, "times the breaker tripped"),
    "resilience_breaker_rejected_total": _m("counter", ("dependency",), BUILT_UNWIRED, "calls refused by an open breaker"),
    "resilience_retry_budget_tokens": _m("gauge", ("dependency",), BUILT_UNWIRED, "whole retry tokens left"),
    "resilience_retries_granted_total": _m("counter", ("dependency",), BUILT_UNWIRED, "retries paid from the budget"),
    "resilience_retries_denied_total": _m("counter", ("dependency",), BUILT_UNWIRED, "retries refused: storm prevented"),
    "resilience_bulkhead_rejected_total": _m("counter", ("dependency",), BUILT_UNWIRED, "calls refused by the concurrency cap"),
    "resilience_bulkhead_in_flight": _m("gauge", ("dependency",), BUILT_UNWIRED, "calls in flight now"),
    "resilience_calls_total": _m("counter", ("dependency",), BUILT_UNWIRED, "guarded calls"),
    "resilience_attempts_total": _m("counter", ("dependency",), BUILT_UNWIRED, "attempts sent to the dependency"),
    # Stage 31: computed by `python -m hub.obs evaluate`, not stored
    "telemetry_lint_findings_total": _m("counter", (), BUILT_UNWIRED, "privacy / schema findings in the evaluated samples"),
    # specified in observability-spec OBS-4, not exported yet (registered gaps, docs/31-observability/metrics-spec.md MS-4)
    "audit_chain_verify_ok": _m("gauge", (), GAP, "PNFR-09 audit chain verified (needs the F-29-01 fix first)"),
    "projection_mismatch_count": _m("gauge", (), GAP, "FR-DEC-02 projection mismatches"),
    "exception_age_hours_p90": _m("gauge", ("queue",), GAP, "FR-MET-05 exception age"),
    "unmatched_reference_rate": _m("gauge", ("source",), GAP, "FR-MET-07 unmatched references"),
    "run_finished_before_0600_local": _m("gauge", ("job",), GAP, "PNFR-02 (reported by hub.runs.detector, not stored)"),
    "db_busy_total": _m("counter", (), GAP, "CT-17 / H-14 busy evidence"),
}


def sample(name, kind, labels, value):
    """A sample dict in the shape hub.obs.collect produces: value is always a string."""
    return {"name": name, "kind": kind, "labels": dict(labels), "value": str(value)}


def names(source=None):
    return sorted(n for n, m in CATALOG.items() if source is None or m["source"] == source)


def _value_ok(kind, value):
    if kind == "histogram":
        try:
            d = json.loads(value)
        except (TypeError, ValueError):
            return False
        return isinstance(d, dict) and bool(d) and all(k in HISTOGRAM_KEYS and isinstance(v, (int, float)) and not isinstance(v, bool)
                                                       for k, v in d.items())
    return isinstance(value, str) and bool(NUMBER.match(value))


def _check(i, s, entry):
    out = []
    labels = s.get("labels")
    if s.get("kind") not in entry["kinds"]:
        out.append((i, s.get("name"), "bad_kind"))
    if not isinstance(labels, dict):
        return out + [(i, s.get("name"), "bad_labels")]
    if any(k not in entry["labels"] for k in labels):
        out.append((i, s.get("name"), "unknown_label"))
    if any(not (isinstance(v, str) and LABEL_VALUE.match(v)) for v in labels.values()):
        out.append((i, s.get("name"), "bad_label_value"))
    if not _value_ok(s.get("kind"), s.get("value")):
        out.append((i, s.get("name"), "bad_value"))
    return out


def lint_samples(samples):
    """-> [{index, metric, problem}] (empty = clean). The metric name is reported only when it is a catalogue name; otherwise 'unknown'."""
    found, series = [], {}
    for i, s in enumerate(samples):
        name = s.get("name") if isinstance(s, dict) else None
        if name not in CATALOG:
            found.append((i, None, "unknown_metric"))
            continue
        found += _check(i, s, CATALOG[name])
        series.setdefault(name, set()).add(canonical(s.get("labels")) if isinstance(s.get("labels"), dict) else "")
        if obslog.prohibited_findings([json.dumps(s, sort_keys=True, default=str)]):
            found.append((i, name, "prohibited_content"))
    for name, keys in sorted(series.items()):
        if len(keys) > MAX_SERIES_PER_METRIC:
            found.append((-1, name, "cardinality"))
    return [{"index": i, "metric": (m if m in CATALOG else "unknown"), "problem": p} for i, m, p in found]
