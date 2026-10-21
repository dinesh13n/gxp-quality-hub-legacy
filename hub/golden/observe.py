"""Observed new-side values for golden-compare (Stage 20 DW-04 / FAC-05 / S16-D01 / RTD-15).

The INC-02 probe catalogue used *declared* F10-2 target values for the probes whose owning module did not exist yet. Those modules are
built (INC-04 rule service, INC-06 intake), so this module OBSERVES them instead: it builds a private scratch hub store under
<data_dir>/runs/golden-observe (guarded path, recreated each run, deleted afterwards), runs the built services in-process on the
read-only FX-BASE125 snapshot of --legacy-root, and returns one value per observation id. It never writes the legacy copy (snapshots are
`mode=ro&immutable=1`; the legacy DB sha256 is checked before and after) and never touches the caller's own hub.sqlite3.

The result is an observation record bound to (a) the baseline it was taken on (legacy DB and vendor CSV sha256) and (b) a digest of the
hub code that produced it. `golden-compare` accepts a record only when both still match, so a stale record cannot hide a module
regression (`run.py`). No clock value, run id or path enters the record: it is deterministic for a given code + baseline.
Synthetic, unvalidated - method validation only. No model call, no network.
"""
import hashlib
import json
import os
import shutil

from hub.guards import sandbox

SCHEMA = "golden-observation/v1"
OBS_IDS = ("intake.missing_envelope_field", "intake.partner_replay", "intake.partner_negative_quantity", "intake.partner_outcomes",
           "intake.partner_ref_match", "intake.vendor_tiny", "policy.js_invalid_amount", "policy.js_unknown_year", "policy.js_partial_year")
CT07_EVENT = {"message_id": "bad"}  # the CT-07 scenario input (tests/characterization/capture/lib.py `missing_field`)
JS_SET = "as-found-js@1"
CSV_TIER = "tiny"


def code_digest(root=None):
    """sha256 over every .py / .json / .sql file of the hub package (relative path + bytes, sorted)."""
    root = root or sandbox.PACKAGE_ROOT
    h = hashlib.sha256()
    for d, dirs, fns in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x != "__pycache__")
        for fn in sorted(fns):
            if fn.endswith((".py", ".json", ".sql")):
                p = os.path.join(d, fn)
                h.update(os.path.relpath(p, root).replace(os.sep, "/").encode("utf-8") + b"\0")
                with open(p, "rb") as f:
                    h.update(f.read())
                h.update(b"\0")
    return h.hexdigest()


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _rm(path, base):
    if os.path.exists(path):
        sandbox.assert_safe_path(path, "golden-observe scratch")
        if not sandbox.inside(sandbox.real(path), sandbox.real(base)):
            raise ValueError("refusing to delete outside the observe directory")
        for d, _, fns in os.walk(path):
            for fn in fns:
                os.chmod(os.path.join(d, fn), 0o644)
        shutil.rmtree(path)


def _policy_values(pol):
    from hub.core.errors import HubError

    def ev(inp):
        try:
            r = pol.evaluate("AMOUNT_LIMIT", inp, JS_SET)
            return {"allowed": r["outcome"].get("allowed"), "defaulted": r["defaulted"], "threshold": r["outcome"].get("threshold")}
        except HubError as e:
            return e.code

    invalid = {}
    for label, amount in (("abc", "abc"), ("null", None)):
        v = ev({"amount": amount, "region": "APAC", "year": 2026})
        invalid[label] = v if isinstance(v, str) else "OUTCOME"
    y = ev({"amount": 0, "region": "APAC", "year": 2019})
    unknown_year = y if isinstance(y, str) else {"defaulted": y["defaulted"], "region": "APAC", "threshold": y["threshold"], "year": 2019}
    partial = {}
    for year in ("202", "2", ""):
        v = ev({"amount": 0, "region": "APAC", "year": year})
        partial[year] = v if isinstance(v, str) else {"defaulted": v["defaulted"], "threshold": v["threshold"]}
    return {"policy.js_invalid_amount": invalid, "policy.js_unknown_year": unknown_year, "policy.js_partial_year": partial}


def _intake_values(con, runs, ct07):
    pf = runs["partner_feed"]
    cur = {}
    for outcome, reason, n in con.execute(
            "SELECT o.outcome, o.primary_reason, count(*) FROM intake_current o JOIN raw_intake r ON r.raw_id = o.raw_id"
            " WHERE r.source = 'partner_feed' GROUP BY 1, 2 ORDER BY 1, 2"):
        cur[outcome if reason is None else "%s/%s" % (outcome, reason)] = n
    trig = set(r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'trigger' AND tbl_name = 'intake_outcome'"))
    append_only = {"intake_outcome_no_update", "intake_outcome_no_delete"} <= trig
    vc = runs["vendor_csv"]
    unparsable = con.execute(
        "SELECT count(*) FROM intake_current o JOIN raw_intake r ON r.raw_id = o.raw_id WHERE r.source = 'vendor_csv'"
        " AND o.outcome = 'QUARANTINED' AND o.primary_reason = 'UNPARSABLE_AMOUNT'").fetchone()[0]
    quarantined = vc["outcomes"].get("QUARANTINED", 0)
    return {
        "intake.missing_envelope_field": {"quarantined": ct07["outcomes"].get("QUARANTINED", 0), "reason": ct07["primary_reason"],
                                          "received": ct07["received"]},
        "intake.partner_replay": {"NOOP_DUPLICATE": pf["noop_duplicate"], "REVISED_CONFLICT": pf["revised_conflict"]},
        "intake.partner_negative_quantity": {"NEGATIVE_VALUE_items": pf["reasons"].get("NEGATIVE_VALUE", 0),
                                             "flagged_value_queue": pf["queues"].get("flagged_value", 0)},
        "intake.partner_outcomes": {"outcome_store": "append-only" if append_only else "MUTABLE", "outcomes": dict(pf["outcomes"])},
        "intake.partner_ref_match": {"linked": pf["linked"], "unmatched_ref": cur.get("EXCEPTION/UNMATCHED_REF", 0),
                                     "no_business_key": cur.get("EXCEPTION/NO_BUSINESS_KEY", 0)},
        "intake.vendor_tiny": {"UNPARSABLE_AMOUNT": unparsable, "kept_rows": vc["received"] - quarantined},
    }


def observe(data_dir, legacy_root):
    """Run the built modules on the baseline and return the observation record (dict). Raises HubError / ValueError on refusal."""
    from hub import config
    from hub.adapters import intake_sources, legacy_sqlite
    from hub.decision import backfill, schema as dschema, settings as dsettings
    from hub.decision.service import DecisionService
    from hub.intake import schema as ischema
    from hub.intake.service import IntakeService
    from hub.policy import schema as pschema
    from hub.policy.service import PolicyService
    from hub.security import audit, canonical, settings
    from hub.store import db, migrate

    data_dir = sandbox.assert_safe_path(data_dir, "hub data directory")
    legacy_root = sandbox.assert_safe_path(legacy_root, "legacy source root")
    base = os.path.join(data_dir, "runs", "golden-observe")
    work = os.path.join(base, "work")
    _rm(work, base)
    os.makedirs(work)
    store, bk, snap = os.path.join(work, "store"), os.path.join(work, "backups"), os.path.join(work, "snap")
    anchor_path = os.path.join(work, "anchor", "audit-anchor.json")
    for p in (store, bk, snap, os.path.dirname(anchor_path)):
        os.makedirs(p)
    legacy_db = os.path.join(legacy_root, "data", "legacy.sqlite3")
    csv_file = intake_sources.csv_path(legacy_root, CSV_TIER)
    sha_before = _sha(legacy_db)
    cfg = config.load(None)
    s = settings.resolve({"audit": {"anchor_path": anchor_path, "anchor_every": 100}})
    clock, cid = canonical.utc_now, "golden-observe"
    try:
        migrate.migrate(store, bk, anchor_path, clock)
        pschema.apply(store, bk, anchor_path, clock, cid)
        dschema.apply(store, bk, anchor_path, clock, cid)
        ischema.apply(store, bk, anchor_path, clock, cid)
        con = db.open_hub(store)
        try:
            anchor = audit.Anchor(anchor_path, s["audit"]["anchor_every"])
            pol = PolicyService(con, s, clock, anchor)
            pol.load_as_found(legacy_root, snap, cid)
            values = _policy_values(pol)
            backfill.run(DecisionService(con, s, clock, anchor, dsettings.resolve(cfg)), legacy_root, snap, cid)
            isvc = IntakeService(con, s, clock, anchor)
            h = legacy_sqlite.open_snapshot(legacy_root, "legacy.sqlite3", snap, pinned=True)
            try:
                by_source = {"partner_feed": intake_sources.partner_feed_deliveries(h),
                             "source_message": intake_sources.source_message_deliveries(h),
                             "gateway": intake_sources.gateway_inbox_deliveries(h)}
            finally:
                h.close()
            runs = {}
            for source in ("partner_feed", "source_message", "gateway"):
                runs[source] = isvc.ingest(source, by_source[source], "observe-%s" % source, cid, idempotent_backfill=True)
            rows, csv_sha = intake_sources.vendor_csv_deliveries(csv_file)
            runs["vendor_csv"] = isvc.ingest("vendor_csv", rows, "observe-vendor_csv", cid, idempotent_backfill=True)
            ct07 = isvc.ingest("gateway", intake_sources.gateway_event_deliveries([dict(CT07_EVENT)]), "observe-ct07", cid)
            row = con.execute("SELECT primary_reason FROM intake_current WHERE raw_id = ?", (ct07["first_raw_id"],)).fetchone()
            ct07["primary_reason"] = row[0] if row else None
            values.update(_intake_values(con, runs, ct07))
        finally:
            con.close()
    finally:
        _rm(work, base)
    sha_after = _sha(legacy_db)
    values["intake.partner_outcomes"]["legacy_table"] = "untouched" if sha_after == sha_before else "CHANGED"
    return {"schema": SCHEMA, "code_digest": code_digest(), "label": "synthetic, unvalidated",
            "baseline": {"legacy.sqlite3": sha_before, "partner_export.csv(%s)" % CSV_TIER: csv_sha},
            "observations": dict((k, values[k]) for k in OBS_IDS)}


def baseline_shas(legacy_root):
    from hub.adapters import intake_sources
    legacy_root = sandbox.assert_safe_path(legacy_root, "legacy source root")
    return {"legacy.sqlite3": _sha(os.path.join(legacy_root, "data", "legacy.sqlite3")),
            "partner_export.csv(%s)" % CSV_TIER: _sha(intake_sources.csv_path(legacy_root, CSV_TIER))}


def check_record(rec, legacy_root):
    """Return None if `rec` is usable for this code + baseline, else the reason text (the probes become NOT-RUN)."""
    if not isinstance(rec, dict) or rec.get("schema") != SCHEMA or not isinstance(rec.get("observations"), dict):
        return "observation record has an unknown schema"
    if rec.get("code_digest") != code_digest():
        return "observation record is stale: hub code changed since it was taken (re-run golden-observe)"
    if not legacy_root:
        return "--legacy-root is required to verify the observation baseline"
    if rec.get("baseline") != baseline_shas(legacy_root):
        return "observation record was taken on a different baseline"
    return None


def load_record(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
