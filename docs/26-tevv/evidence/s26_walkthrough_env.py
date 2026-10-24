"""Stage 26 DW-22: builds a SANDBOX walkthrough environment for the human walkthroughs TST-REV-03 / 04 / 08 (docs/26-tevv/walkthrough-records.md).

    python3 -B docs/26-tevv/evidence/s26_walkthrough_env.py --sandbox-root ~/fde_sbx/s26-walk

What it makes (everything under --sandbox-root, never in the working tree, never on data/): a hash-gated sandbox copy of the code and the legacy fixture, and a
private hub store with the 125 backfilled cases, the whole shipped partner feed ingested (8,567 deliveries -> the exception backlog), one case with `<script>` text in a
note field, rule traces for three flags on one case, and synthetic users. The configuration lists TWO TEST-ONLY holder ids (holder-1, holder-2) because the sandbox
store was built by the test helpers; that list exists ONLY in this sandbox copy and is never shipped (OD-17 / OD-31: shipped holders stay empty). The three walkthroughs
use the reviewer role only; no Zone H action is part of them.

It prints the serve command, the reviewer login name and a one-time synthetic password. It does not start the server. Synthetic data, unvalidated.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.realpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tests", "characterization"))
os.environ.setdefault("CHAR_WORKTREE_ROOT", REPO)
import harness  # noqa: E402

BUILD = r'''
import json, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "tests", "hub"))
import _support as S
import _inc06 as I
import _inc08 as W
st = W.WStore()
by, _ = I.legacy_deliveries()
st.isvc.ingest("partner_feed", by["partner_feed"], "walk-full", "t-walk-full")
st.isvc.ingest("partner_feed", [I.feed(1, payload={"notes": "<script>alert(1)</script>"}, ref_id="C00009999")], "walk-script", "t-walk-script")
st.load_rules()
case = st.new_case()
for fn, ref, inp in (("PRIORITY", "as-found-python@1", {"status": "OPEN", "severity": "HIGH", "amount": 10}),
                     ("MANUAL_REVIEW", "as-found-python@1", {"status": "CLOSED", "severity": "HIGH"}),
                     ("AMOUNT_LIMIT", "as-found-js@1", {"amount": 1000, "region": "MARS", "year": 2026})):
    st.add_trace(case, fn, inp, ref)
st.con.commit()
out = {"config": st.cfg_path, "data": st.data, "reviewer_login": "rev", "password": st.pw, "trace_case": case,
       "backlog_total": st.count("intake_current", "queue IS NOT NULL")}
st.con.close()
print("WALK-JSON " + json.dumps(out))
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox-root", required=True)
    a = ap.parse_args()
    root = harness.assert_safe_sandbox(os.path.expanduser(a.sandbox_root))
    os.makedirs(root, exist_ok=True)
    label = os.path.join(root, "walk")
    os.makedirs(label, exist_ok=True)
    pristine = harness.build_pristine(label, "c_pristine")
    scratch = os.path.join(label, "scratch")
    os.makedirs(scratch, exist_ok=True)
    env = harness.child_env({"HUB_WORKTREE_ROOT": REPO, "HUB_SANDBOX_ROOT": scratch, "HUB_LEGACY_ROOT": pristine, "PYTHONHASHSEED": "0"})
    p = subprocess.run([sys.executable, "-B", "-c", BUILD], cwd=pristine, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=170)
    line = [l for l in p.stdout.splitlines() if l.startswith("WALK-JSON ")]
    if p.returncode != 0 or not line:
        print(p.stdout[-3000:])
        return 1
    info = json.loads(line[-1][len("WALK-JSON "):])
    print("Walkthrough environment ready (sandbox only).")
    print("  serve : cd %s && python3 -B -m hub.web --config %s serve --data-dir %s --port 8081" % (pristine, info["config"], info["data"]))
    print("  open  : http://127.0.0.1:8081/ui/queue   (log in first at /ui/login)")
    print("  login : %s  /  %s   (synthetic, one-time; reviewer role)" % (info["reviewer_login"], info["password"]))
    print("  trace page for TST-REV-08: http://127.0.0.1:8081/ui/cases/%s/trace" % info["trace_case"])
    print("  backlog total (TST-REV-03): %d" % info["backlog_total"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
