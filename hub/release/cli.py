"""`python -m hub.release <command>` - offline release-readiness tools (Stage 30). Reads files, writes stdout; opens no store, no network, writes nothing.

  register                                          the criteria, the approvals each step needs, and the ids (JSON)
  evaluate --results FILE --approvals FILE          go / no-go over the evidence results and the approval records; exit 0 = GO, 1 = NO-GO, 2 = unreadable or invalid input
  posture [--config FILE]                           shipped-configuration posture (shadow, empty Zone H holders, loopback, schedule off); exit 0 = clean, 1 = violations

A GO is only possible when every technical criterion passes and every required approval is a valid APPROVED record by a named human. This tool never records an
approval and never changes a flag.
"""
import argparse
import json
import sys

from hub.release import gonogo, register


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _out(doc):
    sys.stdout.write(json.dumps(doc, sort_keys=True, indent=1) + "\n")


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.release", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("register")
    p = sub.add_parser("evaluate")
    p.add_argument("--results", required=True)
    p.add_argument("--approvals", required=True)
    sub.add_parser("posture").add_argument("--config", default=None)
    return ap


def _run(a):
    if a.cmd == "register":
        _out({"gates": list(register.GATE_IDS), "technical": [list(t) for t in register.TECHNICAL], "cut_steps": list(register.CUT_STEPS),
              "dv": list(register.DV_IDS), "ops_approvals": [list(o) for o in register.OPS_APPROVALS],
              "required_for_release": list(register.required_for_release()),
              "required_for_step": dict((c, list(register.required_for_step(c))) for c in register.CUT_IDS)})
        return 0
    if a.cmd == "posture":
        from hub import config
        bad = gonogo.posture(config.load(a.config))
        _out({"violations": bad})
        return 1 if bad else 0
    res = gonogo.evaluate(_load(a.results), _load(a.approvals))
    _out(res)
    return 0 if res["decision"] == "GO" else 1


def main(argv=None):
    a = _parser().parse_args(argv)
    if not a.cmd:
        _parser().print_help()
        return 2
    try:
        return _run(a)
    except (OSError, ValueError, KeyError, TypeError) as e:
        sys.stderr.write("hub.release: unreadable or invalid input (%s)\n" % type(e).__name__)
        return 2
