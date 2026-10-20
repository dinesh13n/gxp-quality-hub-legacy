"""Stage 16 RTD-42 probe: exact-Decimal hub rule engine vs legacy JS IEEE-double comparison at the x1.05 tolerance
boundary, for every as-found regional limit (contracts/decision-policies-archive.json, 15 rows).

Run INSIDE a sandbox copy (cwd = the hash-gated copy made by s16_observe.py, HUB_WORKTREE_ROOT set) after
s16_observe.py has loaded the as-found rule sets into <store>:
    python3 -B <this file> --store <sandbox>/work/data/hub.sqlite3 --out <json>
Legacy side: `node -e` requiring legacy_js/legacy_policy.js from the sandbox copy (read-only; no legacy file is written).
Synthetic data, unvalidated - method validation only.
"""
import argparse
import decimal
import json
import sqlite3
import os
import subprocess
import sys

sys.path.insert(0, os.getcwd())  # the sandbox copy (cwd) provides the hub package
from hub.policy import engine
from hub.policy.service import PolicyService


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open("contracts/decision-policies-archive.json", encoding="utf-8") as f:
        rows = json.load(f)["historical_versions"]
    con = sqlite3.connect("file:%s?mode=ro" % a.store, uri=True)
    con.row_factory = sqlite3.Row
    doc = PolicyService(con, {}, lambda: "2026-10-20T00:00:00.000000Z").get_ruleset("as-found-js@1")
    cases = []
    for r in rows:
        exact = decimal.Decimal(r["limit"]) * decimal.Decimal("1.05")
        for delta in ("0", "0.01", "-0.01", "0.000001", "-0.000001", "0.0000000001", "-0.0000000001"):
            amt = exact + decimal.Decimal(delta)
            cases.append([format(amt, "f"), r["region"], int(r["effective_from"][:4])])
    js = ("const p=require('./legacy_js/legacy_policy.js');const c=JSON.parse(require('fs').readFileSync(0,'utf8'));"
          "console.log(JSON.stringify(c.map(x=>[p.threshold(x[1],x[2]),p.legacyAllows(x[0],x[1],x[2]),p.threshold(x[1],x[2])*1.05])))")
    out = subprocess.run(["node", "-e", js], input=json.dumps(cases), stdout=subprocess.PIPE, universal_newlines=True, check=True).stdout
    legacy = json.loads(out)
    diffs, same = [], 0
    for c, l in zip(cases, legacy):
        h = engine.evaluate(doc, "AMOUNT_LIMIT", {"amount": c[0], "region": c[1], "year": str(c[2])})["outcome"]
        if (h["threshold"], h["allowed"]) == (l[0], l[1]):
            same += 1
        else:
            diffs.append({"amount": c[0], "region": c[1], "year": c[2], "legacy": {"threshold": l[0], "allowed": l[1], "limit_x105_double": l[2]},
                          "hub": h})
    res = {"label": "synthetic, unvalidated - method validation only", "cases": len(cases), "identical": same, "different": len(diffs),
           "diffs": diffs}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: res[k] for k in ("cases", "identical", "different")}))
    for d in diffs[:20]:
        print(d)


if __name__ == "__main__":
    main()
