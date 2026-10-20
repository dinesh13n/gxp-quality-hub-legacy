"""TST-CO-08 (AC-CO-08, FR-CO-02; api, class A; INC-08 override rule C1: the HTTP surface exists now): the coexistence inventory is readable, lists CO-WF-01
with owner 'Unknown', and no API route, UI route or job named update / retire / disable for it exists. Synthetic, unvalidated."""
import re
import unittest

import _support as S
import _inc08 as W
from hub.runs import jobs
from hub.web.routes import Table


def setUpModule():
    W.skip_in_inner_egress_run()


class TST_CO_08_Inventory(unittest.TestCase):

    def test_TST_CO_08_co_wf_01_present_and_unchangeable(self):
        """TST-CO-08 / AC-CO-08: CO-WF-01 is in the inventory with owner 'Unknown' and status 'protected'; no route (API or UI) and no job offers to update,
        retire or disable it; the rows cannot be changed through SQL either (insert-only / protected)."""
        st = W.WStore(loaded=False)
        try:
            row = st.con.execute("SELECT item_id, owner, status FROM coexistence_inventory WHERE item_id = 'CO-WF-01'").fetchone()
            self.assertEqual(row, ("CO-WF-01", "Unknown", "protected"))
            t = Table()
            bad = re.compile(r"update|retire|disable|coexist|co-wf|inventory", re.I)
            hits = [(r["op_id"], r["method"], r["path"]) for r in t.api + t.ui if bad.search(r["path"]) or bad.search(r["op_id"])]
            self.assertEqual(hits, [])
            names = [j for j in dir(jobs) if not j.startswith("_")] + list(getattr(jobs, "JOBS", {}))
            self.assertEqual([n for n in names if bad.search(n) and "inventory" not in n.lower()], [])
            for method in ("PUT", "PATCH", "DELETE", "POST"):
                for path in ("/api/v2/coexistence/CO-WF-01", "/api/v2/coexistence/inventory/CO-WF-01", "/api/v2/inventory/CO-WF-01/retire",
                             "/api/v2/inventory/CO-WF-01/disable"):
                    r = st.call(method, path, {} if method != "DELETE" else None, token=st.tokens["ql"])
                    self.assertEqual((r.status, r.code), (403, "E-AUTH-FORBIDDEN"), (method, path, r.text))
            for sql in ("UPDATE coexistence_inventory SET status = 'retired' WHERE item_id = 'CO-WF-01'",
                        "DELETE FROM coexistence_inventory WHERE item_id = 'CO-WF-01'"):
                with self.assertRaises(Exception):
                    st.con.execute(sql)
            self.assertEqual(st.con.execute("SELECT owner, status FROM coexistence_inventory WHERE item_id = 'CO-WF-01'").fetchone(), ("Unknown", "protected"))
        finally:
            st.close()


if __name__ == "__main__":
    unittest.main()
