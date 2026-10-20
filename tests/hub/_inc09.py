"""Shared helpers for the Stage 15 INC-09 hub tests (R2: FTS5 search behind `search.fts`, derived corpus, R2 reports, templates; M007).
Synthetic, unvalidated.

Everything lives under HUB_SANDBOX_ROOT (S.tmpdir) - never inside the repository working tree (OD-03a). The store is the INC-08 template
(M001..M006, the 125 backfilled legacy cases) with M007 applied and one extra synthetic user `fin` (finance_read) created once per process; a
second template variant also holds the shipped corpus (1,200 documents + 420 archive items) loaded from the hash-gated FX-BASE125 sandbox copy of
data/ (read-only; the corpus loader never reads the working tree). Each test gets a private byte copy. The Zone H holders (holder-1, holder-2) are
SYNTHETIC TEST DATA: the shipped config keeps zone_h.holders EMPTY.

INC-09 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER, frozen group C keeps its size) and are run under the
egress guard by test_inc09_egress_guard.py (recursion guard HUB_EGRESS_INNER9). The planned tests are named `test_I9_<FAMILY>_<NN>_...` so no earlier
group selector (-k TST_ID, -k TST_REV, -k TST_SEC, -k I8_, ...) selects them; the INC-09 group selects `-k I9_ -k INC09_S`.
"""
import os
import shutil
import unittest

import _support as S
import _inc05 as D
import _inc08 as W
from hub.r2 import facts as rfacts
from hub.r2.web import R2WebApp
from hub.search import corpus, schema as sschema
from hub.security.canonical import fmt

LABEL = "synthetic, unvalidated"
_TPL9 = {}
_FACTS = {}


def no_fts(con):
    """Probe override: an FTS-less runtime (AC-REV-16 style)."""
    return {"fts5": False, "trigram": False, "sqlite": "test-disabled"}


def skip_in_inner_egress_run():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("INC-09 module: covered by test_inc09_egress_guard.py (inc09-design-notes D-12)")
    S.require_sandbox()


def shipped_corpus():
    """(documents, archive_items, inputs) read once per process from the sandbox copy of data/ (pinned JSONL)."""
    if "c" not in _FACTS:
        _FACTS["c"] = corpus.read_shipped(S.LEGACY_ROOT)
    return _FACTS["c"]


def legacy_facts():
    if "f" not in _FACTS:
        _FACTS["f"] = rfacts.load(S.LEGACY_ROOT, S.tmpdir("p9facts-"))
    return _FACTS["f"]


def _template9(loaded, with_corpus):
    key = (loaded, with_corpus)
    if key in _TPL9:
        return _TPL9[key]
    if with_corpus:
        t = _template9(loaded, False)
        dst = S.tmpdir("p9tplC-")
        shutil.copytree(t["base"], dst, dirs_exist_ok=True)
        ds = D.DStore(_base=dst, _tpl=t)
        docs, arch, inputs = shipped_corpus()
        corpus.build(ds.con, ds.clock, ds.anchor, "host-operator", docs, arch, inputs, "shipped")
        ds.close()
        _TPL9[key] = dict(t, base=dst, clock=fmt(ds.clock._t))
        return _TPL9[key]
    t8 = W._template8(loaded)
    dst = S.tmpdir("p9tpl-")
    shutil.copytree(t8["base"], dst, dirs_exist_ok=True)
    ds = D.DStore(_base=dst, _tpl=t8)
    tokens = dict(t8["tokens"])
    ds.authn.create_user("fin", t8["pw"], ["finance_read"], "op")
    tokens["fin"] = ds.authn.login("fin", t8["pw"], "tpl9")
    ds.close()
    res = sschema.apply(ds.data, os.path.join(dst, "backups-m007"), ds.anchor_path, ds.clock)
    assert res["applied"], res
    _TPL9[key] = {"base": dst, "tokens": tokens, "pw": t8["pw"], "clock": fmt(ds.clock._t)}
    return _TPL9[key]


class R2Store(W.WStore):
    """A private M001..M007 hub store plus an in-process R2WebApp. corpus=True holds the shipped derived corpus."""

    def __init__(self, loaded=True, corpus=False, extra=None, app_kw=None):
        D.DStore.__init__(self, loaded, extra, _tpl=_template9(loaded, corpus))
        from hub.intake.service import IntakeService
        from hub.metrics.service import MetricsService
        from hub.review.service import ReviewService
        from hub.runs.service import RunService
        from hub.gate.dispositions import DispositionService
        self.isvc = IntakeService(self.con, self.s, self.clock, self.anchor)
        self.runs = RunService(self.con, self.s, self.clock, self.anchor, self.cfg)
        self.met = MetricsService(self.con, self.s, self.clock, self.anchor, self.cfg)
        self.rev = ReviewService(self.con, self.s, self.clock, self.anchor)
        self.disp = DispositionService(self.con, self.s, self.clock, self.anchor, self.d)
        self.app_kw = dict(app_kw or {})
        self._app = None

    @property
    def app(self):
        if self._app is None:
            self._app = R2WebApp(self.data, self.cfg, self.clock, **self.app_kw)
        return self._app

    def reset_app(self):
        self._app = None

    def build(self, documents, archive=(), origin="synthetic", probe_fn=None):
        return corpus.build(self.con, self.clock, self.anchor, "host-operator", documents, archive, {"fixture": LABEL}, origin, probe_fn=probe_fn)

    def search(self, q, name, **params):
        import urllib.parse as up
        p = dict(params, q=q)
        return self.get("/api/v2/search?" + up.urlencode(p), name)

    def run_rules(self, *codes):
        """Crosswalk rule links from the read-only legacy snapshot (LT-01..LT-04) and the document JSONL (LT-05)."""
        from hub.crosswalk import sources
        from hub.crosswalk.service import identity_targets
        out = {}
        with D.legacy_handle("p9leg-") as h:
            inputs, cases = sources.legacy_inputs(h)
        for c in codes:
            if c == "LT-05":
                items, _ = sources.document_items(S.LEGACY_ROOT)
                out[c] = self.cw.run_rule(c, items, identity_targets(cases), "t-" + c)
            else:
                items, targets = inputs[c]
                out[c] = self.cw.run_rule(c, items, targets, "t-" + c)
        return out


def doc(i, body, level="quality", eff="2025-01-01", locale="en-US", ref=None, version="v1"):
    return {"doc_id": "DOC-9%07d" % i, "version": version, "effective_at": eff, "source": "synthetic", "locale": locale, "access_level": level,
            "reference": ref, "body": body, "ocr_confidence": None}


def walk_keys(o, out=None):
    out = [] if out is None else out
    if isinstance(o, dict):
        for k, v in o.items():
            out.append(k)
            walk_keys(v, out)
    elif isinstance(o, list):
        for v in o:
            walk_keys(v, out)
    return out
