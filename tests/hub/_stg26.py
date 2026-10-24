"""Shared helpers for the Stage 26 TEVV tests (independent TEVV and adversarial testing of the deterministic controls; DW-21..DW-24). Synthetic, unvalidated.

Stage 26 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER) and run under the egress guard in
test_tst_hub_stg26_egress_guard.py (E26EGRESS) instead (same split as Stages 20, 21, 23 and 24). Evidence JSON is written under
HUB_SANDBOX_ROOT/s26-evidence and copied into docs/26-tevv/evidence/ by the TEVV agent. Nothing here changes hub behaviour, a binding, a legacy path or the
working tree (OD-03a). No helper in this directory imports a deny-listed module (hub.guards.no_ai rule R2): wire tests use the raw-socket client of _http8.py.

The thresholds these tests enforce are declared in docs/26-tevv/release-thresholds.md and the dataset in docs/26-tevv/adversarial-dataset-spec.md BEFORE any
test ran. A test never edits a threshold or the corpus: S26-B01 pins the corpus by sha256.

  corpus()            the hash-pinned adversarial corpus v1.0 (tests/hub/data_s26/adversarial_corpus_v1.json)
  strings()           [(class, index, text)] of the 114 hostile strings
  snapshot(st)        per-table (row count, content digest) of a WStore, minus the tables that legitimately change on a refused request
  diff(a, b)          sorted table names whose snapshot differs
  write_evidence()    JSON under HUB_SANDBOX_ROOT/s26-evidence
"""
import hashlib
import json
import os
import unittest

import _support as S

LABEL = "synthetic, unvalidated"
CORPUS_REL = os.path.join("tests", "hub", "data_s26", "adversarial_corpus_v1.json")
CORPUS_SHA256 = "1806bd77cb2c69619bd074515bf497049c1288dd0c957dac6a84d90b9a556f7b"  # declared in adversarial-dataset-spec.md AD-1 before any result
CORPUS_STRINGS = 114
EVIDENCE_REL = os.path.join("docs", "26-tevv", "evidence")
# Tables that change on a refused / read-only request by design: the audit trail (checked separately), session last-seen, failed-login counters, HTTP metrics.
VOLATILE = ("audit_log", "session", "login_attempt", "obs_metric", "sqlite_sequence")
ZH_ALL = ["ZH-%02d" % i for i in range(1, 11)]
TAG = None


def skip_in_inner_egress_run():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("Stage 26 module: covered by test_tst_hub_stg26_egress_guard.py (E26EGRESS)")
    S.require_sandbox()


def write_evidence(name, doc):
    d = os.path.join(S.SANDBOX_ROOT, "s26-evidence")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    return p


def corpus_bytes():
    with open(os.path.join(S.CODE_ROOT, CORPUS_REL), "rb") as f:
        return f.read()


_C = {}


def corpus():
    if "c" not in _C:
        _C["c"] = json.loads(corpus_bytes().decode("utf-8"))
    return _C["c"]


def strings(classes=None):
    out = []
    for cls, items in sorted(corpus()["classes"].items()):
        if classes and cls not in classes:
            continue
        for i, s in enumerate(items):
            out.append((cls, i, s))
    return out


def jsonable(s):
    """True when the text can be encoded as UTF-8 (a lone surrogate can not; it travels as a JSON \\u escape instead)."""
    try:
        s.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False


def snapshot(st, ignore=VOLATILE):
    """{table: (rows, sha256 of all rows in rowid order)} for every table of the store's SQLite file except `ignore`. Table names come from sqlite_master."""
    out = {}
    names = [r[0] for r in st.con.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
    for t in names:
        if t in ignore:
            continue
        h = hashlib.sha256()
        n = 0
        try:
            cur = st.con.execute('SELECT * FROM "%s" ORDER BY rowid' % t.replace('"', '""'))
        except Exception:  # noqa: BLE001  WITHOUT ROWID table
            cur = st.con.execute('SELECT * FROM "%s"' % t.replace('"', '""'))
        for row in cur:
            h.update(repr(row).encode("utf-8", "surrogatepass"))
            n += 1
        out[t] = (n, h.hexdigest())
    return out


def diff(a, b):
    return sorted(t for t in set(a) | set(b) if a.get(t) != b.get(t))


def audit_n(st):
    return st.count("audit_log")


def verify_chain(st):
    """The audit chain verification report of the store (hub.security.audit.verify)."""
    from hub.security import audit
    return audit.verify(st.con, st.anchor_path)
