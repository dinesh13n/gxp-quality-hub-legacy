"""`python -m hub.obs <command>` - offline observability tools over a JSON file of samples (Stage 31). Reads files, writes stdout; opens no store, no
network, takes no clock, writes no audit record, and changes no hub state.

  catalog                         the metric catalogue, the SLO candidates and invariants, and the alert rules (JSON)
  evaluate --samples FILE [--previous FILE] [--availability FILE] [--timeliness FILE]
                                  lint + SLO positions + alerts for a list of samples (as stored by `obs-snapshot`, JSON list of
                                  {name, kind, labels, value}); exit 0 = nothing firing and lint clean, 1 = an alert fires or lint finds
                                  something, 2 = unreadable input
  expo --samples FILE             Prometheus text exposition of the samples
  traces --log FILE               trace summaries rebuilt from a file of JSON log lines (correlation id = trace id)
"""
import argparse
import json
import sys

from hub.obs import alerts, catalog, expo, report, slo, trace


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _out(doc):
    sys.stdout.write(json.dumps(doc, sort_keys=True, indent=1) + "\n")


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.obs", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("catalog")
    p = sub.add_parser("evaluate")
    for f in ("samples", "previous", "availability", "timeliness"):
        p.add_argument("--" + f, default=None, required=(f == "samples"))
    sub.add_parser("expo").add_argument("--samples", required=True)
    sub.add_parser("traces").add_argument("--log", required=True)
    return ap


def _run(a):
    if a.cmd == "catalog":
        _out({"metrics": catalog.CATALOG, "slos": slo.SLOS, "invariants": slo.INVARIANTS, "alert_rules": alerts.RULES, "label": report.LABEL})
        return 0
    if a.cmd == "expo":
        sys.stdout.write(expo.render(_load(a.samples)))
        return 0
    if a.cmd == "traces":
        with open(a.log, encoding="utf-8") as f:
            res = trace.build_traces(f.read().splitlines())
        for t in res["traces"].values():
            t.pop("span_list")
        _out(res)
        return 0
    opt = dict((k, _load(getattr(a, k))) for k in ("previous", "availability", "timeliness") if getattr(a, k))
    res = report.evaluate(_load(a.samples), **opt)
    _out(res)
    return 1 if res["lint"] or res["alerts"]["firing"] else 0


def main(argv=None):
    a = _parser().parse_args(argv)
    if not a.cmd:
        _parser().print_help()
        return 2
    try:
        return _run(a)
    except (OSError, ValueError, KeyError, TypeError) as e:
        sys.stderr.write("hub.obs: unreadable or invalid input (%s)\n" % type(e).__name__)
        return 2
