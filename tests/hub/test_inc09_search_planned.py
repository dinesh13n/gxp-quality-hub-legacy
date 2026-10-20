"""INC-09 planned tests, reviewer search and data protection (R2): TST-REV-09, -11, -12, -13, -15, -18, TST-SEC-19, -20, TST-NFR-12.
Named test_I9_<FAMILY>_<NN> so the frozen earlier selectors (-k TST_REV, -k TST_SEC, -k TST_NFR) keep their counts (inc09-design-notes D-12).
Every search test runs on BOTH engines: FTS5 (`search.fts = auto`, the device runtime offers FTS5 + trigram) and the fallback (probe override =
FTS-less runtime) and asserts identical results. Corpus = the shipped JSONL + archive items from the hash-gated sandbox copy, or labelled synthetic
fixtures. Synthetic, unvalidated.
"""
import ast
import json
import os
import urllib.parse as up
import unittest

import _support as S
import _inc09 as N
from hub.decision import access
from hub.r2 import protection
from hub.search import text

ON = {"search": {"enabled": True, "fts": "auto"}}
REASON = "synthetic reason: INC-09 test of a C3 read"


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

    def both(self, corpus=True, extra=None):
        """(fts5 store, fallback store) over the same corpus."""
        a = self.store(corpus=corpus, extra=extra or ON)
        b = self.store(corpus=corpus, extra=extra or ON, app_kw={"probe_fn": N.no_fts})
        return a, b

    def ids(self, r):
        self.assertEqual(r.status, 200, r.text[:300])
        return [h["doc_id"] for h in r.json()["items"]]


class R2SearchPlanned(_Base):

    def test_I9_REV_09_ref_filter_returns_the_case_documents(self):
        """AC-REV-09 (TST-REV-09): `ref:<case>` returns the documents whose reference equals the case id; 30 documents reference a case across the
        corpus; per-case counts come from the fixture (C00000038: 2 open documents, C00000001: none, C00000002: 2 restricted)."""
        docs, _, _ = N.shipped_corpus()
        expected = {}
        cases = ["C%08d" % i for i in range(1, 126)]
        for d in docs:
            if d["reference"] in cases:
                expected.setdefault(d["reference"], set()).add(d["doc_id"])
        self.assertEqual(sum(len(v) for v in expected.values()), 30)
        a, b = self.both()
        for st in (a, b):
            r = st.search("ref:C00000038", "rev")
            self.assertEqual(sorted(self.ids(r)), sorted(expected["C00000038"]))
            self.assertEqual(r.json()["engine"], "fts5" if st is a else "fallback")
            self.assertEqual(st.search("ref:C00000001", "rev").json()["total"], 0)
            self.assertEqual(st.search("ref:C00000002", "rev").json()["total"], 0)  # both restricted: not readable by a reviewer
            r2 = st.search("ref:C00000002", "ql", reason=REASON)
            self.assertEqual(sorted(self.ids(r2)), sorted(expected["C00000002"]))
            total = 0
            sess = st.sess("ql")
            for c in cases:
                total += st.app.search.search(sess, "ref:" + c, con=st.con, reason=REASON, limit=100)["total"]
            self.assertEqual(total, 30)
        self.assertEqual(a.search("ref:C00000038", "rev").json()["items"], b.search("ref:C00000038", "rev").json()["items"])
        # the linked case comes from the crosswalk (LT-05), else 'no linked case'
        self.assertEqual(set(h["linked_case"] for h in a.search("ref:C00000038", "rev").json()["items"]), {"no linked case"})
        a.run_rules("LT-05")
        self.assertEqual(set(h["linked_case"] for h in a.search("ref:C00000038", "rev").json()["items"]), {"C00000038"})
        print("\n[TST-REV-09] documents referencing a case: 30 (synthetic, unvalidated); C00000038 -> %s" % sorted(expected["C00000038"]))

    def test_I9_REV_11_operator_and_sql_text_is_literal(self):
        """AC-REV-11 (TST-REV-11): `foo OR NOT bar* NEAR(x y) col:evil` -> E-REV-QUERY-INVALID for the unknown field `col`; without it every token is
        literal (OR / NOT / NEAR / * have no effect), no FTS syntax error leaks, no SQL fragment executes."""
        for st in self.both():
            r = st.search("foo OR NOT bar* NEAR(x y) col:evil", "rev")
            self.assertEqual((r.status, r.code), (422, "E-REV-QUERY-INVALID"))
            for leak in ("fts5", "syntax", "MATCH", "sqlite", "near \""):
                self.assertNotIn(leak, r.text)
            r = st.search("foo OR NOT bar* NEAR(x y)", "rev")
            self.assertEqual((r.status, r.json()["total"]), (200, 0))
            # OR is a literal token: an FTS OR would return every 'discrepancy' document
            self.assertEqual(st.search("discrepancy OR nosuchword", "rev").json()["total"], 0)
            self.assertGreater(st.search("discrepancy", "rev").json()["total"], 0)
            n = st.count("search_doc")
            for q in ("'; DROP TABLE search_doc; --", "\") OR 1=1 --", "genealogy\" OR \"x", "*", "NEAR(", "^batch", "batch:"):
                r = st.search(q, "rev")
                self.assertIn(r.status, (200, 422), (q, r.text[:200]))
                if r.status == 422:
                    self.assertIn(r.code, ("E-REV-QUERY-INVALID", "E-REV-QUERY-TOO-LONG"))
                self.assertNotIn("Traceback", r.text)
            self.assertEqual(st.count("search_doc"), n)

    def test_I9_REV_12_restricted_rows_are_neither_returned_nor_counted(self):
        """AC-REV-12 (TST-REV-12): a caller without access to restricted documents (328 + the 420 archive items with no access level) searches a
        term present in restricted and open documents -> restricted hits absent and not counted; counts equal the permitted subset."""
        docs, arch, _ = N.shipped_corpus()
        self.assertEqual(sum(1 for d in docs if d["access_level"] == "restricted"), 328)
        allrows = [(d["doc_id"], d["access_level"], d["body"]) for d in docs] + [(x["doc_id"], "restricted", x["body"]) for x in arch]
        hits = [(i, lv) for i, lv, body in allrows if "genealogy" in text.tokens(body)]
        permitted = sorted(i for i, lv in hits if access.can_read(("reviewer",), lv))
        restricted = set(i for i, lv in hits if lv == "restricted")
        self.assertTrue(restricted and permitted)
        for st in self.both():
            seen, cursor = [], None
            while True:
                q = {"limit": 100}
                if cursor:
                    q["cursor"] = cursor
                r = st.search("genealogy", "rev", **q)
                self.assertEqual(r.status, 200, r.text[:200])
                out = r.json()
                self.assertEqual(out["total"], len(permitted))
                seen += [h["doc_id"] for h in out["items"]]
                cursor = out["next"]
                if not cursor:
                    break
            self.assertEqual(sorted(seen), permitted)
            self.assertFalse(set(seen) & restricted)
            q = st.search("genealogy", "ql", reason=REASON, limit=100).json()
            self.assertEqual(q["total"], len(hits))

    def test_I9_REV_13_trigram_substring_and_diacritics(self):
        """AC-REV-13 (TST-REV-13): ja-JP text -> a substring query finds the document (trigram index for >= 3 characters, substring for shorter);
        es / de text with diacritics matches a query without them. Same result on both engines. Fixture: synthetic, unvalidated."""
        fixture = [N.doc(1, u"品質逸脱の調査報告書", locale="ja-JP"),          # 品質逸脱の調査報告書
                   N.doc(2, u"製造記録の確認", locale="ja-JP"),                            # 製造記録の確認
                   N.doc(3, u"investigación de desviación en el lote", locale="es-MX"),
                   N.doc(4, u"Überprüfung der Qualität abgeschlossen", locale="de-DE"),
                   N.doc(5, "plain english control text", locale="en-US")]
        res = []
        for st in self.both(corpus=False):
            st.build(fixture)
            got = {}
            for q in (u"逸脱の調", u"逸脱", u"記録", "investigacion", "desviacion", "uberprufung", "qualitat",
                      u"Qualität", u"\"調査報告\"", "locale:ja-JP"):
                got[q] = self.ids(st.search(q, "rev"))
            res.append(got)
            self.assertEqual(got[u"逸脱の調"], ["DOC-90000001"])
            self.assertEqual(got[u"逸脱"], ["DOC-90000001"])
            self.assertEqual(got[u"記録"], ["DOC-90000002"])
            self.assertEqual((got["investigacion"], got["desviacion"]), (["DOC-90000003"], ["DOC-90000003"]))
            self.assertEqual((got["uberprufung"], got["qualitat"], got[u"Qualität"]), (["DOC-90000004"],) * 3)
            self.assertEqual(got[u"\"調査報告\""], ["DOC-90000001"])
            self.assertEqual(sorted(got["locale:ja-JP"]), ["DOC-90000001", "DOC-90000002"])
        self.assertEqual(res[0], res[1])
        self.assertEqual(self.stores[0].search("x", "rev").json()["engine"], "fts5")

    def test_I9_REV_15_labelled_recall_is_a_reported_baseline(self):
        """AC-REV-15 (TST-REV-15, class C): a labelled set of >= 50 queries -> top-5 recall is measured and REPORTED as a baseline; no threshold is
        enforced. The label set is generated from corpus metadata (OPD-12 proposal, not a human judgement) and the shipped corpus has 3 base
        sentences, so ranking quality cannot be assessed: the number is printed with that note."""
        docs, _, _ = N.shipped_corpus()
        locales = sorted(set(d["locale"] for d in docs))
        sentences = sorted(set(d["body"].split("\n")[0] for d in docs))
        keyword = {s: s.split()[1] if s.split()[0].lower() in ("batch", "draft") else s.split()[0] for s in sentences}
        labelled = []
        for s in sentences:
            for lv in ("engineering", "quality", "operations"):
                for loc in locales:
                    rel = sorted(d["doc_id"] for d in docs if d["body"].split("\n")[0] == s and d["locale"] == loc and d["access_level"] == lv)
                    labelled.append(("%s locale:%s" % (keyword[s], loc), lv, rel))
        for d in sorted(docs, key=lambda d: d["doc_id"])[:20]:
            if d["access_level"] != "restricted":
                labelled.append(("doc:%s %s" % (d["doc_id"], text.tokens(d["body"])[0]), d["access_level"], [d["doc_id"]]))
        self.assertGreaterEqual(len(labelled), 50)
        out = []
        for st in self.both():
            got, rel_n = 0, 0
            for q, lv, rel in labelled:
                ids = st.app.search.search(st.sess("rev"), q, limit=5, con=st.con)["items"]
                top = set(h["doc_id"] for h in ids if h["access_label"] == lv) | set(h["doc_id"] for h in ids if q.startswith("doc:"))
                rel = set(rel)
                got += len(top & rel)
                rel_n += min(len(rel), 5)
            out.append(round(float(got) / rel_n, 4) if rel_n else None)
        self.assertEqual(out[0], out[1])
        print("\n[TST-REV-15] top-5 recall (capped at 5 relevant per query) over %d labelled queries: %s on fts5 and fallback - BASELINE ONLY, "
              "no threshold (OPD-12); ranking quality cannot be assessed on the shipped corpus (3 base sentences). synthetic, unvalidated"
              % (len(labelled), out[0]))

    def test_I9_REV_18_template_drafts_are_never_prefilled(self):
        """AC-REV-18 (TST-REV-18): template feature enabled -> a draft is created with no pre-filled field and no Zone H action reachable from it;
        disabled (default) -> E-REV-DRAFTS-DISABLED."""
        st0 = self.store(extra={})
        r = st0.post("/api/v2/drafts", {"template_id": "deviation_narrative"}, "rev")
        self.assertEqual((r.status, r.code), (501, "E-REV-DRAFTS-DISABLED"))
        st = self.store(extra={"templates": {"enabled": True}})
        zh = st.zh_counts()
        r = st.post("/api/v2/drafts", {"template_id": "deviation_narrative"}, "rev")
        self.assertEqual(r.status, 201, r.text[:300])
        d = r.json()
        self.assertEqual((d["fields"], d["prefilled"], d["owner"]), ({}, False, "rev"))
        r = st.post("/api/v2/drafts", {"template_id": "capa_narrative", "fields": {"root_cause": "typed by the author"}}, "ql")
        self.assertEqual((r.status, r.json()["fields"]), (201, {"root_cause": "typed by the author"}))
        for bad in ({"template_id": "nope"}, {"template_id": "capa_narrative", "fields": {"verdict": "x"}},
                    {"template_id": "capa_narrative", "fields": {"root_cause": "x" * 2001}}, {"template_id": "capa_narrative", "fields": {"root_cause": 5}}):
            r = st.post("/api/v2/drafts", bad, "rev")
            self.assertEqual((r.status, r.code), (422, "E-REV-TEMPLATE-INVALID"), bad)
        self.assertEqual(st.post("/api/v2/drafts", {"template_id": "capa_narrative"}, "holder-1").status, 403)
        self.assertEqual(st.post("/api/v2/drafts", {"template_id": "capa_narrative"}, "fin").status, 403)
        rows = st.con.execute("SELECT template_id, fields, owner FROM review_draft ORDER BY draft_id").fetchall()
        self.assertEqual(rows, [("deviation_narrative", "{}", "rev"), ("capa_narrative", json.dumps({"root_cause": "typed by the author"}), "ql")])
        self.assertEqual(st.zh_counts(), zh)
        keys = set(N.walk_keys(d))
        self.assertFalse(keys & {"action", "actions", "links", "href", "pack_hash", "reauth_token", "disposition"})
        from hub.r2 import drafts
        form = drafts.form("deviation_narrative")
        self.assertTrue(all(f["value"] is None for f in form["fields"]) and form["prefilled"] is False)
        tree = ast.parse(open(drafts.__file__, encoding="utf-8").read())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods.update(a.name for a in n.names)
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module or "")
        self.assertFalse([m for m in mods if m.startswith(("hub.gate", "hub.decision.service", "hub.policy", "hub.intake", "hub.search.engine"))], mods)


class R2ProtectionPlanned(_Base):

    ROLES = {"rev": ("reviewer",), "ql": ("quality_lead",), "comp": ("compliance",), "holder-1": ("dispositioner",), "fin": ("finance_read",)}

    def test_I9_SEC_19_field_class_handling_by_role(self):
        """AC-SEC-19 (TST-SEC-19): one fixture record per field class and each role -> handling matches metadata-model M3/M4 (finance_read masked
        account_id, restricted denied, missing access_level treated restricted). Read through the API where a route exists for the role; the
        finance masking is checked at the protection layer because no registered route serves case fields to finance_read (DEV-91)."""
        facts, _ = N.legacy_facts()
        case = facts("case", "C00000002")
        for name, roles in sorted(self.ROLES.items()):
            p = protection.project("case", case, roles)
            if name == "fin":
                self.assertEqual(p["account_id"], protection.mask(case["account_id"]))
                self.assertNotEqual(p["account_id"], case["account_id"])
            else:
                self.assertEqual(p["account_id"], case["account_id"])
            self.assertEqual(protection.project("batch", facts("batch", "BT00000000"), roles)["qa_status"], "REVIEW")
            for lv in ("engineering", "quality", "operations", "restricted", None, "bogus"):
                d = protection.project("document", {"doc_id": "DOC-1", "access_level": lv}, roles)
                eff = lv if lv in access.LEVELS else "restricted"
                if access.can_read(roles, eff):
                    self.assertEqual((d["access_level"], d["field_class"]), (eff, protection.document_class(eff)))
                else:
                    self.assertEqual(d, {"type": "document", "access": "denied"})
            self.assertEqual(protection.project("audit", {"actor": "x"}, roles)["actor"] == "x", any(r in protection.CLASS_READERS["C3"] for r in roles))
        # through the API: search over a fixture with one document per class (C2 levels, C3 restricted, missing level -> restricted)
        st = self.store(corpus=False)
        st.build([N.doc(1, "classword engineering", "engineering"), N.doc(2, "classword quality", "quality"),
                  N.doc(3, "classword operations", "operations"), N.doc(4, "classword restricted", "restricted"),
                  dict(N.doc(5, "classword missing level"), access_level=None)])
        want = {"rev": ["DOC-90000001", "DOC-90000002", "DOC-90000003"]}
        for name in ("ql", "comp", "holder-1"):
            want[name] = ["DOC-90000001", "DOC-90000002", "DOC-90000003", "DOC-90000004", "DOC-90000005"]
        for name, ids in sorted(want.items()):
            r = st.search("classword", name, reason=REASON, limit=100)
            self.assertEqual(sorted(self.ids(r)), ids, name)
            labels = dict((h["doc_id"], h["access_label"]) for h in r.json()["items"])
            if "DOC-90000005" in labels:
                self.assertEqual(labels["DOC-90000005"], "restricted")
        r = st.search("classword", "fin")
        self.assertEqual((r.status, r.code), (403, "E-AUTH-FORBIDDEN"))
        # joined view fields through the API (case account_id shown to the roles that may read C2)
        st.app_kw["facts"] = facts
        st.reset_app()
        st.cw.create_human_link(st.sess("rev"), "case", "C00000002", "batch", "BT00000000", "synthetic link for TST-SEC-19")
        v = st.get("/api/v2/crosswalk/view?id=BT00000000", "rev").json()
        cs = [e for e in v["entities"] if e.get("type") == "case"][0]
        self.assertEqual(cs["fields"]["account_id"], case["account_id"])

    def test_I9_SEC_20_c3_read_needs_a_reason_and_is_audited(self):
        """AC-SEC-20 (TST-SEC-20): a C3 read without reason -> E-SEC-REASON-REQUIRED (nothing returned); with a reason it succeeds and the reason is
        audited (non-empty). Covered for search (OP-REV-03) and the joined view (OP-ID-04)."""
        st = self.store(corpus=True)
        st.run_rules("LT-05")
        for path in ("/api/v2/search?q=ref:C00000002", "/api/v2/crosswalk/view?id=C00000002"):
            for reason in (None, "", "   "):
                r = st.get(path + ("" if reason is None else "&reason=" + up.quote(reason)), "ql")
                self.assertEqual((r.status, r.code), (422, "E-SEC-REASON-REQUIRED"), (path, reason))
                self.assertNotIn("DOC-0000", r.text)
            n = st.count("audit_log", "action = 'C3_READ'")
            r = st.get(path + "&reason=" + up.quote(REASON), "comp")
            self.assertEqual(r.status, 200, r.text[:200])
            rows = st.con.execute("SELECT actor, reason, details FROM audit_log WHERE action = 'C3_READ' ORDER BY audit_seq").fetchall()
            self.assertEqual(len(rows), n + 1)
            self.assertEqual((rows[-1][0], rows[-1][1]), ("comp", REASON))
            self.assertTrue(rows[-1][1].strip())
        # a reviewer sees no C3 row, so no reason is asked of him
        self.assertEqual(st.get("/api/v2/search?q=ref:C00000002", "rev").status, 200)

    def test_I9_NFR_12_every_field_class_has_an_access_fixture(self):
        """AC-NFR-12 (TST-NFR-12): one fixture per field class -> the access tests cover 100% of the field classes present in the estate (C1, C2, C3;
        C0 public has no data in the estate, metadata-model M2)."""
        fixtures = {"C1": ("batch", {"batch_id": "BT00000000", "qa_status": "REVIEW"}, "qa_status"),
                    "C2": ("case", {"case_id": "C00000002", "account_id": "ACCT-000028"}, "account_id"),
                    "C3": ("audit", {"actor": "holder-1"}, "actor")}
        covered = set()
        for cls, (t, rec, field) in sorted(fixtures.items()):
            self.assertEqual(protection.FIELD_CLASSES[t][field][0], cls)
            for roles in self.ROLES.values():
                out = protection.project(t, rec, roles)
                readable = any(r in protection.CLASS_READERS[cls] for r in roles)
                if not readable:
                    self.assertEqual(out[field], {"access": "denied"})
                elif cls == "C2" and roles == ("finance_read",):
                    self.assertTrue(out[field].startswith(protection.MASK))
                else:
                    self.assertEqual(out[field], rec[field])
            covered.add(cls)
        for lv in access.LEVELS:
            covered.add(protection.document_class(lv))
        estate = set(protection.coverage())
        self.assertEqual(covered, estate)
        self.assertEqual(sorted(estate), ["C1", "C2", "C3"])
        print("\n[TST-NFR-12] field classes covered: %s of %s (100%%); C0 has no data in the estate. synthetic, unvalidated"
              % (sorted(covered), sorted(estate)))


if __name__ == "__main__":
    unittest.main()
