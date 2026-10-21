"""Stage 20 mutation gate (DW-04 / DW-06 evidence): apply ONE mutant to a hash-gated sandbox copy built from the working tree (never the
working tree itself), run the selected hub tests there with the standard in-sandbox driver, record KILLED (a test fails) or SURVIVED,
then delete the sandbox. Same method as docs/16-repo-validation/evidence/s16_hub_mutation_gate.py, without the full repository clone
(the sandbox copy is built by tests/characterization/harness.py exactly as tests/hub/run_hub_tests.py builds it).

    python3 -B docs/20-application/evidence/s20_mutation_gate.py --sandbox-root ~/fde_sbx/<x> --mutant H1S20 --out <json>
Synthetic data, unvalidated - method validation only.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

REPO = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tests", "characterization"))
os.environ.setdefault("CHAR_WORKTREE_ROOT", REPO)
import harness  # noqa: E402

MUTANTS = {
    # DW-06: the one Zone H holder rule (replaces Stage 16 H1, whose anchor moved from hub/gate/service.py to hub/security/zone_h.py)
    "H1S20": ("hub/security/zone_h.py", "    if principal.principal_id not in holders:\n        return NOT_A_HOLDER",
              "    if False:\n        return NOT_A_HOLDER", "Zone H: a non-holder is accepted (all three callers)", ["TST_GATE"]),
    # DW-04 / FAC-05: a regression in a BUILT module (negative quantities no longer flagged) must be caught by the golden-compare tests
    "G1S20": ("hub/intake/validate.py", "        elif dec < 0:\n            reasons.add(\"NEGATIVE_VALUE\")",
              "        elif False:\n            reasons.add(\"NEGATIVE_VALUE\")", "intake stops flagging negative quantities (DV-03 behaviour)",
              ["TST_CO_01", "STG20_S04"]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox-root", required=True)
    ap.add_argument("--mutant", required=True, choices=sorted(MUTANTS))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    path, old, new, what, sel = MUTANTS[a.mutant]
    t0 = time.time()
    root = harness.assert_safe_sandbox(a.sandbox_root)
    label = os.path.join(root, a.mutant)
    os.makedirs(label, exist_ok=True)
    pristine = harness.build_pristine(label, "c_pristine")
    f = os.path.join(pristine, path)
    src = open(f, encoding="utf-8").read()
    res = {"id": a.mutant, "file": path, "mutation": what, "selectors": sel, "label": "synthetic, unvalidated - method validation only"}
    if src.count(old) != 1:
        res.update(status="NOT-APPLIED", reason="anchor found %d times" % src.count(old))
    else:
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(src.replace(old, new))
        scratch = os.path.join(label, "scratch")
        os.makedirs(scratch, exist_ok=True)
        env = harness.child_env({"HUB_WORKTREE_ROOT": REPO, "HUB_SANDBOX_ROOT": scratch, "HUB_LEGACY_ROOT": pristine, "PYTHONHASHSEED": "0"})
        env.pop("HUB_EGRESS_INNER", None)
        out = os.path.join(label, "result.json")
        cmd = [sys.executable, "-B", "tests/hub/_driver.py", "--out", out]
        for k in sel:
            cmd += ["-k", k]
        p = subprocess.run(cmd, cwd=pristine, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=900)
        failed = sorted(set(re.findall(r"^(?:FAIL|ERROR): (test\w+)", p.stdout, re.M)))
        with open(out, encoding="utf-8") as fh:
            r = json.load(fh)
        counts = dict((s, sum(1 for x in r["records"] if x["status"] == s)) for s in ("ok", "FAIL", "ERROR", "skipped"))
        res.update(status="KILLED" if failed else ("SURVIVED" if p.returncode == 0 else "INCONCLUSIVE rc=%d" % p.returncode),
                   rc=p.returncode, counts=counts, killed_by=failed[:12])
    res["seconds"] = round(time.time() - t0, 1)
    harness.safe_rmtree(label, root)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(json.dumps(res, sort_keys=True))


if __name__ == "__main__":
    main()
