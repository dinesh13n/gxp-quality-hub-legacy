"""INC-09 supplementary tests (TST-HUB-INC09-S01..S13): engine parity, flag / fallback selection, derived-index rollback, M007, corpus pin and
sandbox guard, operator CLIs, static guards (no time / random / network / AI imports), R2WebApp delegation, shipped defaults, archive parsing, M007 rollback rehearsal.
Not planned test ids (the plan has 20 INC-09 tests); they guard the INC-09 design decisions (inc09-design-notes). Synthetic, unvalidated.
"""
import ast
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import unittest

import _support as S
import _inc08 as W
import _inc09 as N
from hub.search import corpus, fts, text

ON = {"search": {"enabled": True, "fts": "auto"}}
REASON = "synthetic reason: INC-09 supplementary"
NEW_DIRS = (os.path.join("hub", "search"), os.path.join("hub", "r2"))


def setUpModule():
    N.skip_in_inner_egress_run()


class _Base(unittest.TestCase):
    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def store(self, **kw):
        kw.setdefault("extra", ON)
        st = N.R2Store(**kw)
        self.stores.append(st)
        return st


def _py_files():
    for d in NEW_DIRS:
        for root, _, files in os.walk(os.path.join(S.CODE_ROOT, d)):
            for f in sorted(files):
                if f.endswith(".py"):
                    yield os.path.join(root, f)


class TST_HUB_INC09_Supplementary(_Base):

    def test_TST_HUB_INC09_S01_fts5_and_fallback_return_identical_pages(self):
        """S01: the same query on the FTS5 engine and on the fallback engine returns identical items, order, scores and totals (shipped corpus)."""
        a = self.store(corpus=True)
        b = self.store(corpus=True, app_kw={"probe_fn": N.no_fts})
        queries = ["genealogy", "\"batch genealogy\"", "oos signature", "draft procedure superseded", "locale:de-DE genealogy", "from:2024-01-01 to:2024-12-31 oos",
                   "version:v2 procedure", "doc:DOC-00000001", "ignore", "\"ignore previous instructions\"", "archive note", "exception case 00001",
                   "status reopened", "genealogy genealogy", "qa", "mes lims", "nomatch", "ref:C00000038"]
        for name in ("rev", "ql"):
            for q in queries:
                for extra in ({}, {"limit": 7, "cursor": 7}, {"latest_only": "true"}):
                    ra, rb = a.search(q, name, reason=REASON, **extra), b.search(q, name, reason=REASON, **extra)
                    self.assertEqual((ra.status, rb.status), (200, 200), (q, ra.text[:200], rb.text[:200]))
                    ja, jb = ra.json(), rb.json()
                    self.assertEqual((ja["engine"], jb["engine"]), ("fts5", "fallback"))
                    self.assertEqual((ja["items"], ja["total"], ja["next"]), (jb["items"], jb["total"], jb["next"]), (name, q, extra))
        self.assertEqual(a.search("genealogy", "rev").raw, a.search("genealogy", "rev").raw)

    def test_TST_HUB_INC09_S02_rev_10_14_16_on_the_fts5_engine(self):
        """S02: the INC-08 R2 checks TST-REV-10 / 14 / 16 repeated on the FTS5 engine over the derived corpus."""
        st = self.store(corpus=True)
        r = st.search("\"ignore previous\"", "ql", reason=REASON, limit=100).json()
        self.assertEqual((r["engine"], r["total"]), ("fts5", 22))
        self.assertTrue(all(h["trust"] == "untrusted" and h["label"] == "untrusted source text" and "<" not in h["snippet"] for h in r["items"]))
        self.assertEqual(st.search("\"ignore previous\"", "rev", limit=100).json()["total"], 17)
        docs = [N.doc(i, "batch genealogy discrepancy", eff=ea) for i, ea in ((3, "2025-01-01"), (1, "2025-01-01"), (2, "2026-01-01"), (5, "2024-01-01"),
                                                                              (4, "2025-01-01"))]
        for probe in (None, N.no_fts):
            s2 = self.store(app_kw={"probe_fn": probe} if probe else None)
            s2.build(docs)
            o1, o2 = s2.search("genealogy", "rev"), s2.search("genealogy", "rev")
            self.assertEqual(o1.raw, o2.raw)
            self.assertEqual([h["doc_id"] for h in o1.json()["items"]], ["DOC-90000002", "DOC-90000001", "DOC-90000003", "DOC-90000004", "DOC-90000005"])

    def test_TST_HUB_INC09_S03_engine_selection_and_startup_log(self):
        """S03: search.fts off (default) -> fallback/flag_off; FTS5 missing -> fallback/fts5_unavailable; index built without FTS -> fallback/
        fts_index_not_built; auto + FTS5 + index -> fts5. start() logs fts_engine_selected with the engine. search.enabled false -> 501."""
        cases = [({"search": {"enabled": True}}, None, None, ("fallback", "flag_off")),
                 (ON, N.no_fts, None, ("fallback", "fts5_unavailable")),
                 (ON, None, N.no_fts, ("fallback", "fts_index_not_built")),
                 (ON, None, None, ("fts5", "auto"))]
        for extra, app_probe, build_probe, want in cases:
            lines = []
            st = self.store(extra=extra, app_kw=dict({"log_sink": lines.append}, **({"probe_fn": app_probe} if app_probe else {})))
            st.build([N.doc(1, "alpha beta")], probe_fn=build_probe)
            rep = st.app.start("t-start9")
            self.assertEqual((rep["search_engine"]["engine"], rep["search_engine"]["reason"]), want)
            ev = [json.loads(l) for l in lines if '"fts_engine_selected"' in l]
            self.assertEqual(ev[-1]["object_ref"], "search-engine:%s:%s" % want)
            r = st.search("alpha", "rev").json()
            self.assertEqual((r["engine"], r["engine_reason"], r["total"]), want + (1,))
        r = self.store(extra={}).search("alpha", "rev")
        self.assertEqual((r.status, r.code), (501, "E-REV-SEARCH-DISABLED"))

    def test_TST_HUB_INC09_S04_drop_index_is_the_rollback(self):
        """S04: drop-index removes the FTS tables and the derived rows (audited, provenance kept); search answers E-REV-INDEX-ABSENT; a rebuild from
        the same inputs gives byte-identical search responses."""
        st = self.store(corpus=True)
        before = st.search("genealogy", "ql", reason=REASON, limit=50).raw
        self.assertTrue(fts.index_present(st.con))
        res = corpus.drop(st.con, st.clock, st.anchor, "host-operator")
        self.assertEqual(res["rows_dropped"], 1620)
        self.assertFalse(fts.index_present(st.con))
        self.assertEqual(st.count("search_doc"), 0)
        r = st.search("genealogy", "ql", reason=REASON)
        self.assertEqual((r.status, r.code), (409, "E-REV-INDEX-ABSENT"))
        docs, arch, inputs = N.shipped_corpus()
        corpus.build(st.con, st.clock, st.anchor, "host-operator", docs, arch, inputs, "shipped")
        self.assertEqual(st.search("genealogy", "ql", reason=REASON, limit=50).raw, before)
        ev = [r[0] for r in st.con.execute("SELECT event FROM search_corpus_load ORDER BY load_id")]
        self.assertEqual(ev[-2:], ["DROPPED", "LOADED"])
        self.assertEqual(st.count("audit_log", "action IN ('SEARCH_CORPUS_DROPPED','SEARCH_CORPUS_LOADED')") >= 2, True)

    def test_TST_HUB_INC09_S05_m007_requires_m006_is_idempotent_and_insert_only(self):
        """S05: M007 on an INC-08 store: absent -> E-STORE-NOT-MIGRATED from the R2 services; applied once (a second apply is a no-op); the record
        tables are insert-only (E-SEC-RETAINED)."""
        from hub.search import schema
        st8 = W.WStore()
        self.stores.append(st8)
        self.assertEqual(schema.status(st8.con)["state"], "absent")
        app = N.R2WebApp(st8.data, dict(st8.cfg, **ON), st8.clock)
        st8._app = app
        r = st8.get("/api/v2/search?q=x", "rev")
        self.assertEqual(r.code, "E-STORE-NOT-MIGRATED")
        st = self.store()
        st.close()
        self.stores.remove(st)
        self.assertEqual(schema.apply(st.data, os.path.join(st.base, "bk2"), st.anchor_path, st.clock)["applied"], False)
        st = self.store(extra={"templates": {"enabled": True}})
        st.post("/api/v2/drafts", {"template_id": "capa_narrative"}, "rev")
        st.build([N.doc(1, "x")])
        st.con.execute("INSERT INTO consistency_finding VALUES ('F1','r','[]','1','t','open','run','{}')")
        st.con.commit()
        for sql in ("UPDATE review_draft SET owner = 'x'", "DELETE FROM review_draft", "UPDATE search_corpus_load SET actor = 'x'",
                    "DELETE FROM search_corpus_load", "UPDATE consistency_finding SET status = 'open'", "DELETE FROM consistency_finding",
                    "DELETE FROM search_schema_migrations"):
            with self.assertRaises(sqlite3.DatabaseError) as cm:
                st.con.execute(sql)
            self.assertIn("E-SEC-RETAINED", str(cm.exception))
            st.con.rollback()

    def test_TST_HUB_INC09_S06_corpus_pin_and_sandbox_guard(self):
        """S06: the JSONL is pinned (a changed byte -> E-FX-HASH, fail closed); the loader refuses the working tree (E-CO-NOT-SANDBOX); the sandbox copy
        of data/ is byte-identical after every load."""
        from hub.core.errors import FixtureMismatch, NotSandbox
        before = S.sha256_file(os.path.join(S.LEGACY_ROOT, corpus.DOC_REL))
        self.assertEqual(before, corpus.JSONL_SHA256)
        tmp = S.tmpdir("p9pin-")
        os.makedirs(os.path.join(tmp, "data", "documents"))
        with open(os.path.join(S.LEGACY_ROOT, corpus.DOC_REL), "rb") as f:
            raw = f.read()
        with open(os.path.join(tmp, corpus.DOC_REL), "wb") as f:
            f.write(raw.replace(b"genealogy", b"genea1ogy", 1))
        with self.assertRaises(FixtureMismatch):
            corpus.read_shipped(tmp)
        docs, arch, inputs = corpus.read_shipped(tmp, pinned=False)
        self.assertEqual((len(docs), len(arch), inputs["archive"]), (1200, 0, None))
        with self.assertRaises(NotSandbox):
            corpus.read_shipped(S.WORKTREE)
        N.shipped_corpus()
        self.assertEqual(S.sha256_file(os.path.join(S.LEGACY_ROOT, corpus.DOC_REL)), before)

    def test_TST_HUB_INC09_S07_operator_clis(self):
        """S07: python -m hub.search status / build-index / drop-index and python -m hub.r2 consistency-check / divergence / delays / freshness on a
        store copy (subprocesses, egress guard installed by the CLIs)."""
        st = self.store(extra=ON)
        st.close()
        self.stores.remove(st)

        def run(mod, *args):
            p = subprocess.run([sys.executable, "-B", "-m", mod, "--config", st.cfg_path] + list(args), cwd=S.CODE_ROOT, env=S.child_env(),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)
            return p.returncode, (json.loads(p.stdout) if p.stdout.strip() else None), p.stderr
        rc, out, err = run("hub.search", "build-index", "--data-dir", st.data, "--legacy-root", S.LEGACY_ROOT)
        self.assertEqual(rc, 0, err[-500:])
        self.assertEqual((out["documents"], out["archive_items"]), (1200, 420))
        rc, out, err = run("hub.search", "status", "--data-dir", st.data)
        self.assertEqual((rc, out["state"], out["engine"], out["corpus"]["event"]), (0, "applied", "fts5", "LOADED"), err[-300:])
        rc, out, err = run("hub.r2", "consistency-check", "--data-dir", st.data, "--legacy-root", S.LEGACY_ROOT)
        self.assertEqual((rc, out["findings_new"], out.get("statement")), (0, 0, "no consistency policy adopted"), err[-300:])
        rc, out, err = run("hub.r2", "divergence", "--data-dir", st.data, "--legacy-root", S.LEGACY_ROOT)
        self.assertEqual((rc, out["inputs"], out["compared_sets"]), (0, 125, []), err[-300:])  # no rule set loaded in this store
        rc, out, err = run("hub.r2", "freshness", "--data-dir", st.data, "--as-of", "2026-10-20T00:00:00.000000Z")
        self.assertEqual((rc, out["sources"]), (0, []), err[-300:])
        rc, out, err = run("hub.r2", "delays", "--data-dir", st.data, "--source", "partner_feed")
        self.assertEqual((rc, out["items"]), (0, []), err[-300:])
        rc, out, err = run("hub.search", "drop-index", "--data-dir", st.data)
        self.assertEqual((rc, out["rows_dropped"]), (0, 1620), err[-300:])
        rc, out, err = run("hub.search", "status", "--data-dir", st.data)
        self.assertEqual((out["corpus"]["event"], out["engine_reason"]), ("DROPPED", "fts_index_not_built"))

    def test_TST_HUB_INC09_S08_static_guards_on_the_new_modules(self):
        """S08: hub/search and hub/r2 import no time / random / secrets, call no wall clock, import no HTTP client and no AI package (deny-list scan
        green), and never build SQL from the query text (MATCH / LIKE arguments are bound parameters)."""
        from hub.guards import no_ai
        bad = []
        for path in _py_files():
            tree = ast.parse(open(path, encoding="utf-8").read())
            for n in ast.walk(tree):
                mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module or ""] if isinstance(n, ast.ImportFrom) else [])
                for m in mods:
                    if m.split(".")[0] in ("time", "random", "secrets", "socket", "urllib", "requests", "httpx") or m.startswith("http.client"):
                        bad.append((path, m))
                if isinstance(n, ast.Attribute) and n.attr in ("now", "utcnow", "today") and isinstance(n.value, (ast.Name, ast.Attribute)):
                    bad.append((path, "wall clock ." + n.attr))
        self.assertEqual(bad, [])
        self.assertEqual(no_ai.scan([os.path.join(S.CODE_ROOT, d) for d in NEW_DIRS] + [os.path.join(S.CODE_ROOT, "tests", "hub", f) for f in
                                    ("_inc09.py", "test_inc09_search_planned.py", "test_inc09_reports_planned.py", "test_inc09_supplementary.py")]), [])
        src = open(os.path.join(S.CODE_ROOT, "hub", "search", "engine.py"), encoding="utf-8").read()
        self.assertNotIn("% q", src)
        self.assertNotIn("+ query", src)

    def test_TST_HUB_INC09_S09_r2_app_delegates_the_r1_operations(self):
        """S09: R2WebApp serves every one of the 48 registry operations (R2 handler or the frozen INC-08 one); R1 behaviour is unchanged for the
        operations INC-09 does not own (health, OP-MET-05 501, audit list role rules)."""
        from hub.r2 import api as r2api
        from hub.security import authz
        for r in authz.load_registry():
            self.assertTrue(callable(getattr(r2api, "op_" + r["op_id"].replace("-", "_"))), r["op_id"])
        st = self.store()
        self.assertEqual(st.get("/healthz").status, 200)
        self.assertEqual(st.get("/api/v2/metrics/case-cost", "ql").code, "E-MET-NOT-AVAILABLE")
        self.assertEqual(st.get("/api/v2/audit/records", "rev").status, 403)
        self.assertEqual(st.get("/api/v2/rules/divergence", "ql").code, "E-R2-INPUT-INVALID")

    def test_TST_HUB_INC09_S10_shipped_defaults_are_off_and_holders_empty(self):
        """S10: shipped defaults: search.enabled false, search.fts off, templates.enabled false, zone_h.holders EMPTY; the flag rejects other values."""
        from hub import config
        from hub.core.errors import ConfigInvalid
        from hub.search import settings as ss
        from hub.security import settings
        cfg = config.load(None)
        s = ss.resolve(cfg)
        self.assertEqual((s["enabled"], s["fts"], ss.templates_enabled(cfg)), (False, "off", False))
        self.assertEqual(settings.resolve(cfg)["zone_h"]["holders"], [])
        with self.assertRaises(ConfigInvalid):
            ss.resolve({"search": {"fts": "on"}})

    def test_TST_HUB_INC09_S11_archive_items_are_parsed_as_untrusted_restricted_text(self):
        """S11: archive .eml (quoted-printable) and .html items become restricted rows (no access level given, MA-1) with the decoded visible text;
        the planted instruction stays ordinary text; effective_at comes from the 'Source date' in the text."""
        _, arch, inputs = N.shipped_corpus()
        self.assertEqual((len(arch), inputs["archive"]["files"]), (420, 420))
        a0 = [x for x in arch if x["doc_id"] == "ARC-00000"][0]
        self.assertIn("Source date 2021-01-01", a0["body"])
        self.assertIn("ignore prior instructions", a0["body"])
        self.assertNotIn("=\n", a0["body"])
        self.assertEqual((a0["effective_at"], a0["source"]), ("2021-01-01", "archive-eml"))
        a1 = [x for x in arch if x["doc_id"] == "ARC-00001"][0]
        self.assertEqual(a1["body"].count("Pharma Quality exception case 00001"), 2)  # h1 + paragraph; <title> excluded
        st = self.store(corpus=True)
        self.assertEqual(st.con.execute("SELECT count(*), min(access_level), max(access_level), max(access_level_given) FROM search_doc"
                                        " WHERE origin = 'shipped-archive'").fetchone(), (420, "restricted", "restricted", 0))
        self.assertEqual(st.search("\"ignore prior instructions\"", "rev").json()["total"], 0)
        self.assertGreater(st.search("\"ignore prior instructions\"", "comp", reason=REASON).json()["total"], 0)

    def test_TST_HUB_INC09_S12_text_rules_match_the_fts5_tokenizer(self):
        """S12: the shared text rules: fold removes diacritics and case; tokens split on '_' like unicode61; CJK terms are substring terms; the bm25
        helper reproduces SQLite's bm25() for a small table (to 1e-9)."""
        self.assertEqual(text.fold(u"ÜBER Straße"), "uber strasse")
        self.assertEqual(text.tokens("foo_bar baz-9"), ["foo", "bar", "baz", "9"])
        self.assertTrue(text.is_cjk(u"逸脱") and not text.is_cjk("abc"))
        st = self.store()
        st.build([N.doc(1, "alpha beta beta"), N.doc(2, "alpha gamma"), N.doc(3, "beta beta beta delta epsilon"), N.doc(4, "zeta")])
        got = dict(st.con.execute("SELECT d.doc_id, bm25(search_fts) FROM search_fts JOIN search_doc d ON d.rowid = search_fts.rowid"
                                  " WHERE search_fts MATCH '\"beta\"'").fetchall())
        rows = [text.tokens(b) for b in ("alpha beta beta", "alpha gamma", "beta beta beta delta epsilon", "zeta")]
        avg = sum(len(r) for r in rows) / 4.0
        w = [text.idf(4, 2)]
        for i, r in ((1, rows[0]), (3, rows[2])):
            self.assertAlmostEqual(got["DOC-9%07d" % i], text.bm25(w, [r.count("beta")], float(len(r)), avg), places=9)

    def test_TST_HUB_INC09_S13_m007_rollback_rehearsal(self):
        """S13 (rollback-rehearsal-inc09.md): an INC-08 store (M001..M006) -> `python -m hub.search migrate` takes a `pre-search-M007-` backup and
        applies M007 -> corpus built, a draft written -> restore of that backup gives the M006 store back (M007 absent, audit chain verifies) ->
        migrate again works. Level L1 (flag off / drop-index) needs no restore; this is L2."""
        from hub.ops import backup
        from hub.search import schema
        from hub.security import audit
        st8 = W.WStore(extra={"templates": {"enabled": True}})
        st8.close()
        bk_root = S.tmpdir("p9bk-")
        p = subprocess.run([sys.executable, "-B", "-m", "hub.search", "--config", st8.cfg_path, "migrate", "--data-dir", st8.data, "--backup-root", bk_root],
                           cwd=S.CODE_ROOT, env=S.child_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr[-500:])
        res = json.loads(p.stdout)
        self.assertTrue(res["applied"] and res["backup"]["label"].startswith("pre-search-M007-"))
        con = sqlite3.connect(os.path.join(st8.data, "hub.sqlite3"))
        try:
            self.assertEqual(schema.status(con)["state"], "applied")
            corpus.build(con, st8.clock, st8.anchor, "host-operator", [N.doc(1, "rehearsal text")], (), {"fixture": "synthetic"}, "synthetic")
        finally:
            con.close()
        backup.restore(res["backup"]["path"], st8.data, st8.anchor_path, st8.clock)
        con = sqlite3.connect(os.path.join(st8.data, "hub.sqlite3"))
        try:
            self.assertEqual(schema.status(con)["state"], "absent")
            self.assertEqual(audit.verify(con, st8.anchor_path)["status"], "ok")
            self.assertIsNone(con.execute("SELECT 1 FROM sqlite_master WHERE name = 'search_doc'").fetchone())
        finally:
            con.close()
        again = schema.apply(st8.data, S.tmpdir("p9bk2-"), st8.anchor_path, st8.clock)
        self.assertTrue(again["applied"])


if __name__ == "__main__":
    unittest.main()
