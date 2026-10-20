"""Stage 16 data-contract check: validate objects the BUILT hub produced (a store written by s16_observe.py in a
sandbox) against the Stage 12 JSON schemas in docs/12-specs/contracts/schemas (draft-07).

Evaluation tooling only: needs the third-party `jsonschema` package, which is NOT a product dependency (OD-08 /
stdlib-only hub). Read-only: the store is opened with sqlite `mode=ro`. Run where jsonschema is installed:
    python3 -B docs/16-repo-validation/evidence/s16_contracts.py --store <sandbox>/work/data/hub.sqlite3 \
        --obs <observation json> --out <result json>
Synthetic data, unvalidated - method validation only.
"""
import argparse
import base64
import collections
import json
import os
import sqlite3

import jsonschema

REPO = os.path.realpath(os.environ.get("S16_REPO") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SCHEMAS = os.path.join(REPO, "docs", "12-specs", "contracts", "schemas")
BOOL = {"exception", "is_default", "affects_state", "counts_toward_totals", "partial", "read_only", "authoritative", "involves_definition", "defaulted"}


def load(name):
    with open(os.path.join(SCHEMAS, name + ".schema.json"), encoding="utf-8") as f:
        return json.load(f)


def maybe_json(v):
    if isinstance(v, str) and v[:1] in "[{":
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def rows(con, table, transform=None):
    cur = con.execute("SELECT * FROM %s" % table)  # fixed table names below
    cols = [d[0] for d in cur.description]
    for r in cur:
        o = {}
        for c, v in zip(cols, r):
            v = maybe_json(v)
            if c in BOOL and v in (0, 1):
                v = bool(v)
            o[c] = v
        yield transform(o) if transform else o


def check(schema_name, objs, limit_examples=3):
    schema = load(schema_name)
    v = jsonschema.Draft7Validator(schema)
    n, bad, msgs = 0, 0, collections.Counter()
    examples = []
    for o in objs:
        n += 1
        errs = sorted(v.iter_errors(o), key=lambda e: list(e.path))
        if errs:
            bad += 1
            for e in errs:
                key = "%s: %s" % ("/".join(str(p) for p in e.path) or "(root)", e.message[:160])
                msgs[key] += 1
            if len(examples) < limit_examples:
                examples.append({k: (str(o[k])[:80] if k in o else None) for k in list(o)[:4]})
    return {"schema": schema_name, "objects": n, "valid": n - bad, "invalid": bad,
            "top_errors": msgs.most_common(8), "invalid_examples_head": examples}


def raw_intake(o):
    b = o.pop("raw_bytes", None)
    o["raw_bytes_b64"] = base64.b64encode(b if isinstance(b, bytes) else str(b).encode()).decode()
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--obs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    con = sqlite3.connect("file:%s?mode=ro" % a.store, uri=True)
    con.text_factory = str
    res = []
    try:
        res.append(check("audit-record", rows(con, "audit_log")))
        res.append(check("crosswalk-link", rows(con, "crosswalk_link")))
        res.append(check("decision-event", rows(con, "decision_events")))
        res.append(check("intake-outcome", rows(con, "intake_outcome")))
        res.append(check("raw-intake", rows(con, "raw_intake", raw_intake)))
        res.append(check("metric-definition", rows(con, "metric_definition")))
        res.append(check("policy-object", rows(con, "policy_object")))
        sets = []
        for rs in rows(con, "rule_set"):
            rs["rows"] = [r for r in rows(con, "rule_row") if r["ruleset_id"] == rs["ruleset_id"] and r["version"] == rs["version"]]
            for r in rs["rows"]:
                r.pop("ruleset_id", None)
                r.pop("version", None)
            sets.append(rs)
        res.append(check("rule-set", sets))
    finally:
        con.close()
    with open(a.obs, encoding="utf-8") as f:
        obs = json.load(f)
    rr = [v["out"] for v in obs["policy_evaluate"].values() if v["rc"] == 0 and isinstance(v["out"], dict)]
    res.append(check("rule-result", rr))
    mv = obs["month_end"]["out"]["value"] if isinstance(obs["month_end"]["out"], dict) else None
    res.append(check("metric-value", [mv] if mv else []))
    out = {"label": "synthetic, unvalidated - method validation only", "jsonschema": __import__("importlib.metadata").metadata.version("jsonschema"),
           "results": res}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    for r in res:
        print("%-18s objects=%-6d valid=%-6d invalid=%d %s" % (r["schema"], r["objects"], r["valid"], r["invalid"], r["top_errors"][:3]))


if __name__ == "__main__":
    main()
