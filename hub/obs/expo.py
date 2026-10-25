"""Text exposition of samples in the Prometheus text format (Stage 31; docs/31-observability/metrics-spec.md MS-5). Pure and deterministic.

Nothing serves this over HTTP: the route registry is frozen (TST-SEC-01) and a `/metrics` route is decision D-31-04. The text can be written to a file
by `python -m hub.obs expo` for a collector that reads files. Counters get no `_total` rewriting (the catalogue names already end in `_total`);
a histogram sample (closed JSON shape) becomes `<name>_count`, `<name>_sum` and `<name>_max` lines. Label values are escaped per the format.
"""
import json

from hub.obs import catalog


def _esc(v):
    return str(v).replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def _labels(labels):
    return "{%s}" % ",".join('%s="%s"' % (k, _esc(labels[k])) for k in sorted(labels)) if labels else ""


def _lines(s):
    if s["kind"] != "histogram":
        return [("%s%s %s" % (s["name"], _labels(s["labels"]), s["value"]))]
    try:
        d = json.loads(s["value"])
    except ValueError:
        return []
    names = {"count": "_count", "sum_ms": "_sum", "sum_s": "_sum", "max_ms": "_max", "max_s": "_max"}
    return ["%s%s%s %s" % (s["name"], names[k], _labels(s["labels"]), d[k]) for k in sorted(d) if k in names]


def render(samples):
    out, seen = [], set()
    for s in sorted(samples, key=lambda s: (s["name"], json.dumps(s["labels"], sort_keys=True))):
        if s["name"] not in seen:
            seen.add(s["name"])
            kind = "histogram" if s["kind"] == "histogram" else s["kind"]
            purpose = catalog.CATALOG.get(s["name"], {}).get("purpose", "")
            out += ["# HELP %s %s" % (s["name"], _esc(purpose)), "# TYPE %s %s" % (s["name"], "summary" if kind == "histogram" else kind)]
        out += _lines(s)
    return "\n".join(out) + ("\n" if out else "")
