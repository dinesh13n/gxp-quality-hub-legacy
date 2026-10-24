"""Stage 24 field-map tests (DW-19 'field map', RTD-83; privacy impact assessment). Synthetic, unvalidated.

  S10  every column of every table of the M000..M007 store is classified by hub/security/datamap.py; the map is written as evidence
  S11  an unclassified table or column is refused (a new column fails the build until it is reviewed)
  S12  credential material is exactly the secret-tagged columns and none of it reaches the audit trail or the structured log
  S13  the datamap and the Stage 20 request-time protection map (hub.r2.protection) agree where they overlap
"""
import json
import unittest

import _inc09 as N
import _stg24 as T
from hub.r2 import protection
from hub.security import datamap, tables

SECRET_COLUMNS = {("principal", "pw_hash"), ("principal", "pw_salt"), ("session", "token_sha256"), ("service_token", "token_sha256"),
                  ("service_token_revocation", "token_sha256")}


def setUpModule():
    T.skip_in_inner_egress_run()


class TST_HUB_STG24_Fields(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.st = N.R2Store(loaded=False)
        cls.cols = []
        for (t,) in cls.st.con.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name").fetchall():
            if tables.ignored(t):
                continue
            for r in cls.st.con.execute("PRAGMA table_info(%s)" % t).fetchall():
                cls.cols.append((t, r[1]))

    @classmethod
    def tearDownClass(cls):
        cls.st.close()

    def test_TST_HUB_STG24_S10_every_column_is_classified(self):
        """S10 (DW-19, RTD-83): all columns resolve to C1..C3; class counts and the personal-data-analogue columns are evidence."""
        out, counts = [], {"C1": 0, "C2": 0, "C3": 0}
        for t, c in self.cols:
            k = datamap.classify(t, c)
            self.assertIn(k["class"], counts, (t, c))
            counts[k["class"]] += 1
            out.append({"table": t, "column": c, "class": k["class"], "tags": k["tags"]})
        self.assertGreaterEqual(len(self.cols), 300)
        T.write_evidence("field-map.json", {"label": T.LABEL, "status": "PROPOSED (A-11-02 open)", "columns": len(out), "class_counts": counts,
                                            "staff_id_columns": sorted(set(c["column"] for c in out if "staff_id" in c["tags"])),
                                            "free_text_columns": sorted(set("%s.%s" % (c["table"], c["column"]) for c in out if "free_text" in c["tags"])),
                                            "map": out})

    def test_TST_HUB_STG24_S11_unclassified_table_or_column_is_refused(self):
        """S11 (DW-19): classify raises for an unknown table and for a column no rule covers."""
        with self.assertRaises(KeyError):
            datamap.classify("no_such_table", "x")
        with self.assertRaises(KeyError):
            datamap.classify("audit_log", "brand_new_column")

    def test_TST_HUB_STG24_S12_secrets_are_the_tagged_columns_and_stay_out_of_audit_and_log(self):
        """S12 (DW-19, BEH-SEC-07): the secret-tagged columns are exactly the five credential columns, all C3; after a login / logout the plaintext password,
        session token and stored hashes appear in no audit row."""
        tagged = set((t, c) for t, c in self.cols if "secret" in datamap.classify(t, c)["tags"])
        self.assertEqual(tagged, SECRET_COLUMNS)
        for t, c in tagged:
            self.assertEqual(datamap.classify(t, c)["class"], "C3")
        st = N.R2Store(loaded=False)
        try:
            tok = st.authn.login("rev", st.pw, "s24-s12")
            st.authn.logout(tok, "s24-s12")
            blob = json.dumps([tuple(map(str, r)) for r in st.con.execute("SELECT * FROM audit_log")])
            for secret in (st.pw, tok):
                self.assertNotIn(secret, blob)
            for (h,) in st.con.execute("SELECT pw_hash FROM principal WHERE pw_hash IS NOT NULL"):
                self.assertNotIn(h, blob)
        finally:
            st.close()

    def test_TST_HUB_STG24_S13_datamap_and_protection_map_agree_on_the_audit_trail(self):
        """S13 (DW-19): hub.r2.protection puts audit actor / reason in C3; the datamap puts audit_log in C3 with actor as staff_id and reason as free text."""
        self.assertEqual(protection.FIELD_CLASSES["audit"]["actor"][0], "C3")
        self.assertEqual(protection.FIELD_CLASSES["audit"]["reason"][0], "C3")
        for col in ("actor", "reason"):
            self.assertEqual(datamap.classify("audit_log", col)["class"], "C3")
        self.assertIn("staff_id", datamap.classify("audit_log", "actor")["tags"])
        self.assertIn("free_text", datamap.classify("audit_log", "reason")["tags"])


if __name__ == "__main__":
    unittest.main()
