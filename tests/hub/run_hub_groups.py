"""Stage 20 DW-02 / DW-03 hub regression runner: runs the groups of tests/hub/regression_groups.json, ONE `run_hub_tests.py` call per
group (sandbox copy, checksum gate before/after - unchanged runner), logs wall time and counts per group, checks that the number of
executed test methods equals the number statically selected for the group (executed = discovered), and deletes each group's sandbox
afterwards (OD-16 housekeeping).

  python3 -B tests/hub/run_hub_groups.py --sandbox-base ~/fde_sbx/<x> --group C1 [--group C2 ...] [--log <json>]
  python3 -B tests/hub/run_hub_groups.py --sandbox-base ~/fde_sbx/<x> --all --log <json>     (cloud workspace, no per-call cap)

Exit 0 = every selected group green and complete; 1 = a test failed or a count differs; 2 = refused (the per-group runner refused).
Never runs code from the working tree: run_hub_tests.py builds the sandbox copy.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.realpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "tests", "characterization"))
os.environ.setdefault("CHAR_WORKTREE_ROOT", REPO)
import _groups  # noqa: E402
import harness  # noqa: E402


def run_group(g, base, ids):
    root = os.path.join(base, g["id"])
    cmd = [sys.executable, "-B", os.path.join(HERE, "run_hub_tests.py"), "--sandbox-root", root, "--label", g["id"]]
    for s in g["selectors"]:
        cmd += ["-k", s]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    wall = round(time.time() - t0, 1)
    rep = {}
    try:
        with open(os.path.join(root, g["id"], "report.json"), encoding="utf-8") as f:
            rep = json.load(f)
    except (OSError, ValueError):
        pass
    exp = _groups.expected(g["id"], ids=ids)
    executed = len(rep.get("tests", []))
    out = {"group": g["id"], "selectors": g["selectors"], "rc": p.returncode, "wall_seconds": wall,
           "runner_seconds": rep.get("seconds"), "counts": rep.get("counts"), "expected_methods": len(exp), "executed_methods": executed,
           "complete": executed == len(exp), "checksum_rc_pre": rep.get("checksum_rc_pre"), "checksum_rc_post": rep.get("checksum_rc_post"),
           "python": rep.get("python"), "summary": [l for l in p.stdout.splitlines() if l.startswith("summary")][-1:]}
    if p.returncode != 0 or not out["complete"]:
        out["tail"] = p.stdout[-2500:]
        out["failed"] = sorted(set(re.findall(r"^(?:FAIL|ERROR): (test\w+)", p.stdout, re.M)))
    if os.path.isdir(root):
        harness.safe_rmtree(root, base)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sandbox-base", required=True)
    ap.add_argument("--group", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--log", default=None)
    a = ap.parse_args(argv)
    base = harness.assert_safe_sandbox(a.sandbox_base)
    os.makedirs(base, exist_ok=True)
    groups = _groups.load()
    known = [g["id"] for g in groups]
    unknown = [x for x in a.group if x not in known]
    if unknown or (not a.all and not a.group):
        print("REFUSED: give --all or --group from %s (unknown: %s)" % (known, unknown))
        return 2
    ids = _groups.static_ids()
    results = [run_group(g, base, ids) for g in groups if a.all or g["id"] in a.group]
    for r in results:
        print("%-4s rc=%s wall=%5.1fs counts=%s expected=%d executed=%d complete=%s" % (
            r["group"], r["rc"], r["wall_seconds"], r["counts"], r["expected_methods"], r["executed_methods"], r["complete"]), flush=True)
    log = {"schema": "hub-regression-log/v1", "label": "synthetic, unvalidated", "results": results,
           "total_executed": sum(r["executed_methods"] for r in results), "total_expected": sum(r["expected_methods"] for r in results)}
    if a.log:
        with open(a.log, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=1, sort_keys=True)
    if any(r["rc"] == 2 for r in results):
        return 2
    return 0 if all(r["rc"] == 0 and r["complete"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
