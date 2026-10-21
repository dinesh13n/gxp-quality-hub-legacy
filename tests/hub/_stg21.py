"""Shared helpers for the Stage 21 hub tests (Enterprise Integration; DW-10, DW-11, DW-12). Synthetic, unvalidated.

Stage 21 is evidence-only (Stage 18 DI-05): these helpers READ the shipped sources through the existing adapters and the existing intake
service, start the repo's own loopback source-gateway stub from the sandbox copy, and write evidence JSON under HUB_SANDBOX_ROOT. Nothing
here changes hub behaviour, a binding, a legacy path or the working tree (OD-03a). Stage 21 modules skip themselves inside the TST-CO-12
inner egress run (HUB_EGRESS_INNER) and run under the egress guard in test_tst_hub_stg21_egress_guard.py (E21EGRESS) instead.

  contract_pack()   DW-10: source-contract-v1 over the four shipped sources (per-source pass / fail, failing fields, payload key profile,
                    the effect enforce would have, and the Stage 12 partner-feed-payload schema as an alternative candidate)
  consumer_scan()   DW-11: static scan of the repository copy for readers of each legacy output (LO-01..LO-13), classified by path
  GatewayStub       the shipped services/source_gateway/server.py on a free loopback port over a scratch copy of the FX-BASE125 database
  hanging_server()  a loopback socket that accepts and never answers (timeout semantics)
"""
import collections
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import unittest
import urllib.parse

import _support as S

LABEL = "synthetic, unvalidated"
SOURCES = ("partner_feed", "source_message", "gateway", "vendor_csv")
EVIDENCE_REL = os.path.join("docs", "21-integration", "evidence")
STAGE12_PAYLOAD_SCHEMA = os.path.join("docs", "12-specs", "contracts", "schemas", "partner-feed-payload.schema.json")


def skip_in_inner_egress_run():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("Stage 21 module: covered by test_tst_hub_stg21_egress_guard.py (E21EGRESS)")
    S.require_sandbox()


def committed(name):
    """The committed evidence file of the same name (docs/21-integration/evidence/<name>) in the sandbox code copy, or None."""
    p = os.path.join(S.CODE_ROOT, EVIDENCE_REL, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def write_evidence(name, doc):
    """Write <HUB_SANDBOX_ROOT>/s21-evidence/<name> (copied into docs/21-integration/evidence/ by the build agent); returns the path."""
    d = os.path.join(S.SANDBOX_ROOT, "s21-evidence")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    return p


def _inc(d, k, n=1):
    d[k] = d.get(k, 0) + n


# ------------------------------------------------------------------------------------------------ DW-10 contract pack
_TYPES = {"string": str, "number": (int, float), "integer": int, "object": dict, "array": list, "boolean": bool}


def _type_ok(spec_type, v):
    import decimal
    types = spec_type if isinstance(spec_type, list) else [spec_type]
    for t in types:
        py = _TYPES.get(t)
        if py is None:
            return True
        if t == "number" and isinstance(v, decimal.Decimal):
            return True
        if isinstance(v, py) and not (t != "boolean" and isinstance(v, bool)):
            return True
    return False


def subset_schema_check(schema, payload):
    """Stdlib subset of draft-07 used by the Stage 12 partner-feed-payload schema: object, required, per-property type / enum.
    Returns the sorted failing field names (empty = pass). Evaluation tooling only; not a hub binding."""
    if not isinstance(payload, dict):
        return sorted(schema.get("required", [])) or ["<not an object>"]
    bad = set(k for k in schema.get("required", []) if k not in payload)
    for k, spec in schema.get("properties", {}).items():
        if k not in payload:
            continue
        v = payload[k]
        if "enum" in spec and v not in spec["enum"]:
            bad.add(k)
        elif "type" in spec and not _type_ok(spec["type"], v):
            bad.add(k)
    return sorted(bad)


def _deliveries():
    import _inc06 as I
    from hub.adapters import intake_sources
    by, db_sha = I.legacy_deliveries()
    rows, csv_sha = intake_sources.vendor_csv_deliveries(intake_sources.csv_path(S.LEGACY_ROOT, "tiny"))
    return dict(by, vendor_csv=rows), db_sha, csv_sha


def static_contract_profile(contract, deliveries, profile):
    """Per-source profile of one declared contract over the deliveries, through the hub's own L2 parse (validate) and L3 check (contracts)."""
    from hub.intake import contracts, validate
    req = list(contract.get("required", []))
    st = {"items": 0, "pass": 0, "fail": 0, "absent": dict((k, 0) for k in req), "wrong_type": dict((k, 0) for k in req),
          "fail_signatures": {}, "payload_not_object": 0, "payload_keys": {}}
    for d in deliveries:
        _, _, facts = validate.validate(profile, d)
        p = facts["payload"]
        res, missing = contracts.check(contract, p)
        st["items"] += 1
        st[res] += 1
        if res == "fail":
            _inc(st["fail_signatures"], ",".join(missing))
        if not isinstance(p, dict):
            st["payload_not_object"] += 1
            continue
        for k in p:
            _inc(st["payload_keys"], k)
        for k in req:
            if k not in p:
                st["absent"][k] += 1
            elif k in missing:
                st["wrong_type"][k] += 1
    st["payload_keys"] = dict(sorted(st["payload_keys"].items()))
    st["fail_signatures"] = dict(sorted(st["fail_signatures"].items()))
    return st


def store_effect(store, by):
    """Ingest every source once under the shipped default binding (record_only) and read back, per source: the run's contract_check
    counts and, for contract-failing items, the CURRENT outcome - i.e. what `enforce` would add (CONTRACT_VIOLATION) to items not already
    quarantined or duplicate. Pure read after the ingest; no binding is changed."""
    out = {}
    for src in SOURCES:
        rep = store.isvc.ingest(src, by[src], "s21-pack-" + src, "s21-pack")
        cur = collections.OrderedDict()
        for outcome, n in store.con.execute(
                "SELECT o.outcome, count(*) FROM intake_outcome o JOIN raw_intake r ON r.raw_id = o.raw_id WHERE r.source = ?"
                " AND o.contract_check = 'fail' AND o.outcome_seq = (SELECT max(x.outcome_seq) FROM intake_outcome x WHERE x.raw_id = o.raw_id)"
                " GROUP BY o.outcome ORDER BY o.outcome", (src,)):
            cur[outcome] = n
        newly = sum(n for o, n in cur.items() if o not in ("QUARANTINED", "NOOP_DUPLICATE"))
        out[src] = {"binding": rep["binding"]["mode"], "binding_origin": rep["binding"]["origin"], "received": rep["received"],
                    "stored": rep["stored"], "contract_check": dict(sorted(rep["contract_check"].items())), "outcomes": dict(sorted(rep["outcomes"].items())),
                    "contract_fail_current_outcomes": dict(cur), "enforce_would_newly_quarantine": newly,
                    "enforce_would_keep_noop_duplicate": cur.get("NOOP_DUPLICATE", 0), "outcomes_digest": rep["outcomes_digest"]}
    return out


def contract_pack(store):
    from hub.intake import contracts
    from hub.intake.profiles import PROFILES
    by, db_sha, csv_sha = _deliveries()
    contract = contracts.load("source-contract-v1")
    with open(os.path.join(contracts.DIR, "source-contract-v1.json"), "rb") as f:
        bundled = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(S.CODE_ROOT, "integration", "source-contract-v1.json"), "rb") as f:
        shipped = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(S.CODE_ROOT, STAGE12_PAYLOAD_SCHEMA), encoding="utf-8") as f:
        p_schema = json.load(f)
    from hub.intake import validate
    alt = {"items": 0, "pass": 0, "fail": 0, "fail_fields": {}}
    for d in by["partner_feed"]:
        _, _, facts = validate.validate(PROFILES["partner_feed"], d)
        bad = subset_schema_check(p_schema, facts["payload"])
        alt["items"] += 1
        alt["fail" if bad else "pass"] += 1
        for k in bad:
            _inc(alt["fail_fields"], k)
    alt["fail_fields"] = dict(sorted(alt["fail_fields"].items()))
    return {
        "schema": "s21-contract-pack/v1", "label": LABEL, "stage": "21", "work_item": "DW-10",
        "decision_supported": "OD-S12-11 (per-source contract binding record_only | enforce); U-17-IP-2 / U-16-DC-1 (contract owner; contract or data wrong)",
        "contract": {"name": "source-contract-v1", "required": contract.get("required"), "bundled_sha256": bundled,
                     "integration_sha256": shipped, "byte_identical": bundled == shipped},
        "inputs": {"legacy_db_sha256": db_sha, "vendor_csv_tier": "tiny", "vendor_csv_sha256": csv_sha},
        "static": dict((src, static_contract_profile(contract, by[src], PROFILES[src])) for src in SOURCES),
        "store": store_effect(store, by),
        "alternative_candidate": {"partner_feed": dict(alt, schema=STAGE12_PAYLOAD_SCHEMA.replace(os.sep, "/"),
                                                       note="Stage 12 v0.1 DRAFT schema; stdlib subset check (required, type, enum)")},
        "reproduce": "python3 -B tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s21-pack --label pack -k TST_HUB_STG21_S01 "
                     "(writes <sandbox>/pack/scratch/s21-evidence/contract-pack.json)",
    }


# ------------------------------------------------------------------------------------------------ DW-11 consumer scan
# Legacy outputs of the CUT-2..CUT-4 counterparts (docs/14-transformation/cutover-plan.md CO-1) and the regexes that identify a reader.
OUTPUTS = [
    ("LO-01", "CUT-2", "priority() / manual_review_required() rule results", ["app/legacy_logic.py"],
     [r"legacy_logic", r"manual_review_required", r"\bpriority\("]),
    ("LO-02", "CUT-2", "legacy API /api/cases (priority, manual_review_required fields)", ["app/server.py"], [r"/api/cases"]),
    ("LO-03", "CUT-2", "JS threshold() / legacyAllows() output", ["legacy_js/legacy_policy.js"], [r"legacy_policy", r"legacyAllows"]),
    ("LO-04", "CUT-3", "partner_feeds.processing_status after in-place reconcile", ["app/partner_feeds.py"],
     [r"processing_status", r"partner_feeds\s+--reconcile", r"/api/partners"]),
    ("LO-05", "CUT-3", "gateway_inbox / gateway_checkpoints rows", ["app/gateway_bridge.py"], [r"gateway_inbox", r"gateway_checkpoints"]),
    ("LO-06", "CUT-3", "vendor_file_rows / vendor_file_imports rows", ["app/historical_estate.py"], [r"vendor_file_rows", r"vendor_file_imports"]),
    ("LO-07", "CUT-3", "consume_source_messages() output", ["app/integration.py"], [r"consume_source_messages", r"app\.integration\b"]),
    ("LO-08", "CUT-4", "app.baseline metrics JSON", ["app/baseline.py"], [r"app\.baseline", r"from \.baseline", r"\bbaseline\(\)"]),
    ("LO-09", "CUT-4", "Java month-end total (stdout)", ["legacy_java/ReconcileLegacy.java"], [r"ReconcileLegacy"]),
    ("LO-10", "CUT-4", "SQL month-end report", ["sql/legacy_reports.sql"], [r"legacy_reports"]),
    ("LO-11", "CUT-4", "night-shift reconciliation output", ["legacy_batch/shift_reconciliation.py"], [r"shift_reconciliation", r"flagged_count"]),
    ("LO-12", "CUT-4", "legacy API /api/metrics", ["app/server.py"], [r"/api/metrics"]),
    ("LO-13", "CUT-3/4", "operational correlation report", ["app/operational_report.py"], [r"operational_report"]),
]
_STAGE_DOC = re.compile(r"^docs/\d\d-")
_SKIP_TOP = {".git", "data", ".fde", "__pycache__"}


def path_class(rel):
    """Reader class of a repository-relative path; None = out of scan scope (FDE stage docs, hub tests, data, .fde)."""
    if _STAGE_DOC.match(rel) or rel.startswith(("tests/hub/", ".fde/", "data/")):
        return None
    if rel.startswith("hub/"):
        return "hub"
    if rel.startswith("tests/characterization/"):
        return "characterization_harness"
    if rel.startswith(".github/"):
        return "legacy_ci"
    if rel.startswith("tests/"):
        return "legacy_tests"
    if rel.startswith(("app/", "services/", "legacy_batch/", "legacy_java/", "legacy_js/", "sql/", "ops/", "scripts/")) \
            or rel in ("compose.yaml", "Dockerfile", "run.sh"):
        return "legacy_runtime"
    if rel.endswith(".md") or rel.startswith(("docs/", "environments/")):
        return "legacy_docs"
    return "other"


def _files(root):
    for d, dirs, fns in os.walk(root):
        rel_d = os.path.relpath(d, root).replace(os.sep, "/")
        dirs[:] = sorted(x for x in dirs if not (rel_d == "." and x in _SKIP_TOP) and x != "__pycache__")
        for fn in sorted(fns):
            rel = (fn if rel_d == "." else rel_d + "/" + fn)
            if fn.endswith((".pyc", ".class", ".sqlite3")):
                continue
            yield rel, os.path.join(d, fn)


def consumer_scan(root):
    texts = {}
    for rel, p in _files(root):
        cls = path_class(rel)
        if cls is None:
            continue
        try:
            with open(p, encoding="utf-8") as f:
                texts[rel] = (cls, f.read())
        except (UnicodeDecodeError, OSError):
            continue
    outs = []
    for lo, cut, what, producers, pats in OUTPUTS:
        rx = re.compile("|".join(pats))
        readers = {}
        for rel, (cls, t) in sorted(texts.items()):
            if rel in producers:
                continue
            if rx.search(t):
                readers.setdefault(cls, []).append(rel)
        outs.append({"id": lo, "cut_step": cut, "output": what, "producers": producers, "patterns": pats,
                     "readers": dict(sorted(readers.items())),
                     "legacy_runtime_readers": readers.get("legacy_runtime", []), "legacy_ci_readers": readers.get("legacy_ci", [])})
    return {"schema": "s21-consumer-scan/v1", "label": LABEL, "stage": "21", "work_item": "DW-11", "decision_supported": "DQ-15 / U-14-01; CUT-2..CUT-4 step 4",
            "scope": "every text file of the repository copy except .git, data/, .fde/, docs/NN-* stage documents and tests/hub/ (scanned: %d files)" % len(texts),
            "outputs": outs,
            "reproduce": "python3 -B tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/s21-scan --label scan -k TST_HUB_STG21_S04 "
                         "(writes <sandbox>/scan/scratch/s21-evidence/consumer-scan.json)"}


def frozen_view(scan):
    """The part of the scan that only depends on frozen legacy paths (TST-CO-05): equal across later hub changes."""
    return [{"id": o["id"], "readers": dict((k, v) for k, v in o["readers"].items() if k not in ("hub", "characterization_harness"))}
            for o in scan["outputs"]]


# ------------------------------------------------------------------------------------------------ loopback servers
def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def get_json(url, timeout=5):
    """Plain loopback GET (the stub's catalog / failure endpoints) through the raw-socket client of _http8.py: urllib.request / http.client
    are deny-listed outside hub/adapters by No-AI rule R2, which also scans tests/hub (S21-DEV-02). Loopback hosts only. Returns
    (status, body bytes)."""
    import _http8
    u = urllib.parse.urlsplit(url)
    if u.hostname not in ("127.0.0.1", "localhost"):
        raise ValueError("loopback only")
    path = (u.path or "/") + ("?" + u.query if u.query else "")
    head = "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (path, u.netloc)
    r = _http8.raw(u.hostname, u.port, head.encode("latin-1"), timeout=timeout)
    return r.status, r.body


class GatewayStub(object):
    """services/source_gateway/server.py (legacy, unchanged) run from the SANDBOX code copy on a free loopback port, reading a scratch copy of
    the FX-BASE125 legacy.sqlite3 (LEGACY_DB) - the pinned copy is never opened by the stub."""

    def __init__(self):
        self.dir = S.tmpdir("s21stub-")
        self.db = os.path.join(self.dir, "legacy.sqlite3")
        shutil.copy2(os.path.join(S.LEGACY_ROOT, "data", "legacy.sqlite3"), self.db)
        self.port = free_port()
        self.url = "http://127.0.0.1:%d" % self.port
        env = S.child_env({"LEGACY_DB": self.db, "HOST": "127.0.0.1", "SOURCE_PORT": str(self.port)})
        self.proc = subprocess.Popen([sys.executable, "-B", "-m", "services.source_gateway.server"], cwd=S.CODE_ROOT, env=env,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        ev = threading.Event()
        for _ in range(100):
            try:
                st, _b = get_json(self.url + "/health", timeout=1)
                if st == 200:
                    break
            except OSError:
                pass
            ev.wait(0.1)
        else:
            self.close()
            raise RuntimeError("source-gateway stub did not become healthy")

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        if self.proc.stderr:
            self.proc.stderr.close()


class hanging_server(object):
    """A loopback listener that accepts connections and never sends a byte (records request bytes it received)."""

    def __init__(self):
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(8)
        self.url = "http://127.0.0.1:%d" % self.sock.getsockname()[1]
        self.conns, self.received = [], []
        self._stop = threading.Event()
        self.t = threading.Thread(target=self._run, daemon=True)
        self.t.start()

    def _run(self):
        self.sock.settimeout(0.2)
        while not self._stop.is_set():
            try:
                c, _ = self.sock.accept()
            except OSError:
                continue
            c.settimeout(0.5)
            try:
                self.received.append(c.recv(65536))
            except OSError:
                self.received.append(b"")
            self.conns.append(c)

    def close(self):
        self._stop.set()
        self.t.join(2)
        for c in self.conns:
            c.close()
        self.sock.close()


def tree_digest(root):
    """{relative path: sha256} of every file under root (the FX-BASE125 legacy copy)."""
    out = {}
    for d, dirs, fns in os.walk(root):
        dirs.sort()
        for fn in sorted(fns):
            p = os.path.join(d, fn)
            out[os.path.relpath(p, root).replace(os.sep, "/")] = S.sha256_file(p)
    return out
