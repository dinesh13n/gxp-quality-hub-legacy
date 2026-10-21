"""Orchestrates one golden-compare run: guarded data dir, hub store (M000 + register), read-only snapshots,
new-side observations, comparison. The run directory is <data_dir>/runs/golden-compare (recreated each run,
deleted only inside the guarded data directory).

Stage 20 (DW-04, FAC-05): the shipped probe catalogue is `probes_s20.json`. Its module probes use provider `observed`: the value
comes from an observation record of the BUILT modules (hub.golden.observe) - taken inline with `observe=True`, or read from
`observed_path` (written by `python -m hub golden-observe`) and accepted only if its code digest and baseline hashes still match.
Without a usable record those probes are NOT-RUN (gate fails); no declared target value is used. A probe whose legacy side has no
golden (DV-11, DEV-29) reads the legacy value documented in its register row and is labelled `legacy_source: register:<dev_id>`.
"""
import json
import os
import shutil

from hub.adapters import legacy_sqlite
from hub.adapters.legacy_captures import CaptureMissing, CaptureSet, DEFAULT_GOLDEN_DIR
from hub.coexistence import register
from hub.golden import baseline_probes, compare, observe as observe_mod
from hub.guards import sandbox
from hub.store import db

PROBES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probes_s20.json")


class _Captures(object):
    """CaptureSet plus the `register` legacy source (the documented legacy value of a DV row that has no golden)."""

    def __init__(self, captures, rows):
        self.captures, self.rows = captures, dict((r["dev_id"], r) for r in rows)

    def extract(self, source, path):
        if source != "register":
            return self.captures.extract(source, path)
        row = self.rows.get(path[0] if path else None)
        if row is None:
            raise CaptureMissing("register row %s missing" % (path[0] if path else None))
        return json.loads(row["legacy_value"])


def _fresh_run_dir(data_dir):
    run_dir = os.path.join(data_dir, "runs", "golden-compare")
    if os.path.exists(run_dir):
        sandbox.assert_safe_path(run_dir, "run directory")
        for d, _, fns in os.walk(run_dir):
            for fn in fns:
                os.chmod(os.path.join(d, fn), 0o644)
        shutil.rmtree(run_dir)
    os.makedirs(run_dir)
    return run_dir


def _baseline_values(probes, data_dir, legacy_root, new_values):
    """baseline_ro probes over read-only snapshots; returns the snapshot provenance."""
    ro = [p for p in probes if p["new"]["provider"] == "baseline_ro"]
    if not ro:
        return {}
    if not legacy_root:
        err = ValueError("--legacy-root is required for baseline_ro probes")
        for p in ro:
            new_values[p["golden_ref"]] = err
        return {}
    run_dir = _fresh_run_dir(data_dir)
    handles, baseline = {}, {}
    try:
        for store in baseline_probes.stores_needed(sorted(set(p["new"]["query"] for p in ro))):
            handles[store] = legacy_sqlite.open_snapshot(legacy_root, store, run_dir, pinned=True)
            baseline[store] = handles[store].provenance
        for p in ro:
            new_values[p["golden_ref"]] = (baseline_probes.run(p["new"]["query"], handles),
                                           "baseline_ro:%s (read-only snapshot)" % p["new"]["query"])
    finally:
        for h in handles.values():
            h.close()
    return baseline


def _observation(probes, data_dir, legacy_root, observe, observed_path):
    """Return (record or None, status dict) for the `observed` probes."""
    if not any(p["new"]["provider"] == "observed" for p in probes):
        return None, {"status": "not needed"}
    if observe:
        if not legacy_root:
            return None, {"status": "refused", "reason": "--legacy-root is required to observe the built modules"}
        rec = observe_mod.observe(data_dir, legacy_root)
    elif observed_path:
        rec = observe_mod.load_record(observed_path)
    else:
        return None, {"status": "not supplied",
                      "reason": "module observation not supplied: pass --observe or --observed <record from `python -m hub golden-observe`>"}
    why = observe_mod.check_record(rec, legacy_root)
    if why:
        return None, {"status": "refused", "reason": why}
    return rec, {"status": "used", "code_digest": rec["code_digest"], "baseline": rec["baseline"],
                 "taken": "inline" if observe else "record"}


def _observed_values(probes, rec, status, new_values):
    for p in probes:
        spec = p["new"]
        if spec["provider"] == "declared":
            new_values[p["golden_ref"]] = (spec["value"], "declared:%s (target; owning module not built yet)" % spec.get("basis", "F10-2"))
        elif spec["provider"] == "observed":
            oid = spec["observation"]
            if rec is None:
                new_values[p["golden_ref"]] = ValueError(status["reason"])
            elif oid not in rec["observations"]:
                new_values[p["golden_ref"]] = ValueError("observation %s missing from the record" % oid)
            else:
                new_values[p["golden_ref"]] = (rec["observations"][oid], "observed:%s (built module; code %s)" % (oid, rec["code_digest"][:12]))


def run(data_dir, legacy_root=None, probes_path=None, golden_dir=None, observations_path=None, observe=False, observed_path=None):
    data_dir = sandbox.assert_safe_path(data_dir, "hub data directory")
    if legacy_root:
        sandbox.assert_safe_path(legacy_root, "legacy source root")
    probes = compare.load_probes(probes_path or PROBES_PATH)
    con = db.open_hub(data_dir)
    try:
        rows = register.rows(con)
    finally:
        con.close()
    captures = _Captures(CaptureSet.from_golden_dir(golden_dir or DEFAULT_GOLDEN_DIR), rows)
    new_values = {}
    baseline = _baseline_values(probes, data_dir, legacy_root, new_values)
    rec, obs_status = _observation(probes, data_dir, legacy_root, observe, observed_path)
    _observed_values(probes, rec, obs_status, new_values)
    if observations_path:  # test seam: substitute new-side observations (simulates a changed new module)
        with open(observations_path, encoding="utf-8") as f:
            for ref, value in sorted(json.load(f).items()):
                new_values[ref] = (value, "observation-override")
    report = compare.compare(probes, captures, new_values, rows)
    reg_src = dict((p["golden_ref"], p["legacy"]["path"][0]) for p in probes if p["legacy"]["source"] == "register")
    for e in report["entries"]:
        if e["golden_ref"] in reg_src:
            e["legacy_source"] = "register:%s (no golden; documented legacy value)" % reg_src[e["golden_ref"]]
    report["baseline"] = baseline
    report["observation"] = obs_status
    return report
