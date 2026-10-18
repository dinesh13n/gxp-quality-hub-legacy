"""Stage 15 INC-02 hub test runner - executes tests/hub only inside a sandbox copy (OD-03a, BEH-CO-04).

  python3 -B tests/hub/run_hub_tests.py                 # all INC-02 tests (default sandbox ~/fde_sbx/s15-inc02)
  python3 -B tests/hub/run_hub_tests.py -k TST_CO_04    # subset (unittest -k pattern)

Steps: (1) backup manifest check from the repo root (sha256sum -c --quiet, STOP-01) - refuse if not rc 0;
(2) build a pristine, hash-gated FX-BASE125 sandbox copy with the INC-01 harness (code from the working tree
read-only, data/ from the Stage 0A backup); (3) run `python -m unittest discover -s tests/hub` INSIDE that
copy with HUB_WORKTREE_ROOT / HUB_SANDBOX_ROOT / HUB_LEGACY_ROOT set; (4) re-check the backup manifest;
(5) write <sandbox-root>/<label>/report.json. Exit 0 = all tests pass and checksums rc 0 before and after,
1 = a test failed, 2 = refused (unsafe sandbox, checksum failure, fixture mismatch).
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
sys.path.insert(0, os.path.join(REPO, "tests", "characterization"))
os.environ.setdefault("CHAR_WORKTREE_ROOT", REPO)
import harness  # noqa: E402  (INC-01 sandbox + FX-BASE125 fixture gate; imports no legacy code)

DEFAULT_ROOT = os.path.expanduser("~/fde_sbx/s15-inc02")
MANIFEST = os.path.join("..", "_data-backup-2026-10-17", "SHA256SUMS.txt")


def checksums():
    p = subprocess.run(["sha256sum", "-c", "--quiet", MANIFEST], cwd=REPO, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, universal_newlines=True)
    return p.returncode, p.stdout[-2000:]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sandbox-root", default=os.environ.get("HUB_SANDBOX_ROOT_DEFAULT", DEFAULT_ROOT))
    ap.add_argument("--label", default="run")
    ap.add_argument("-k", dest="pattern", action="append", default=[])
    args = ap.parse_args(argv)
    t0 = time.time()
    try:
        root = harness.assert_safe_sandbox(args.sandbox_root)
    except harness.SandboxGuardError as e:
        print("REFUSED %s" % e)
        return 2
    rc_pre, out_pre = checksums()
    print("pre-run checksum rc=%d" % rc_pre)
    if rc_pre != 0:
        print("REFUSED: backup manifest check failed before the run (STOP-01)\n" + out_pre)
        return 2
    label_dir = os.path.join(root, args.label)
    os.makedirs(label_dir, exist_ok=True)
    try:
        pristine = harness.build_pristine(label_dir, "c_pristine")
    except (harness.SandboxGuardError, harness.FixtureError) as e:
        print("REFUSED %s" % e)
        return 2
    scratch = os.path.join(label_dir, "scratch")
    if os.path.exists(scratch):
        harness.safe_rmtree(scratch, label_dir)
    os.makedirs(scratch)
    env = harness.child_env({"HUB_WORKTREE_ROOT": REPO, "HUB_SANDBOX_ROOT": scratch, "HUB_LEGACY_ROOT": pristine,
                             "PYTHONHASHSEED": "0"})
    env.pop("HUB_EGRESS_INNER", None)
    result_path = os.path.join(label_dir, "unittest-result.json")
    if os.path.exists(result_path):
        os.remove(result_path)
    cmd = [sys.executable, "-B", "tests/hub/_driver.py", "--out", result_path]
    for k in args.pattern:
        cmd += ["-k", k]
    print("running tests/hub/_driver.py (unittest discover tests/hub) in <sandbox>/%s/c_pristine" % args.label)
    p = subprocess.run(cmd, cwd=pristine, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       universal_newlines=True, timeout=900)
    out = p.stdout
    try:
        with open(result_path, encoding="utf-8") as f:
            res = json.load(f)
    except (OSError, ValueError):
        res = {"records": [{"id": "driver.crash", "status": "ERROR", "detail": out[-1500:]}]}
    results = [{"test": r["id"].split(".")[-1], "case": ".".join(r["id"].split(".")[:-1]), "status": r["status"],
                "detail": r["detail"]} for r in res["records"]]
    rc_post, out_post = checksums()
    tst_ids = sorted(set(m.group(1).replace("_", "-") for m in
                         (re.match(r"^test_(TST_[A-Z]+_\d+|TST_HUB_INC02_S\d+)", r["test"]) for r in results) if m))
    report = {
        "schema": "hub-test-run/v1", "label": args.label, "unittest_rc": p.returncode,
        "checksum_rc_pre": rc_pre, "checksum_rc_post": rc_post,
        "tests": results, "test_ids": tst_ids,
        "counts": {s: sum(1 for r in results if r["status"] == s) for s in ("ok", "FAIL", "ERROR", "skipped")},
        "tail": out[-1500:], "seconds": round(time.time() - t0, 1),
        "python": sys.version.split()[0],
    }
    with open(os.path.join(label_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, sort_keys=True)
    print(out[-6000:])
    print("post-run checksum rc=%d" % rc_post)
    print("summary: unittest_rc=%d counts=%s ids=%s seconds=%.1f report=%s" % (
        p.returncode, report["counts"], ",".join(tst_ids), report["seconds"], os.path.join(label_dir, "report.json")))
    if rc_post != 0:
        print("STOP-01: backup manifest check FAILED after the run\n" + out_post)
        return 2
    return 0 if p.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
