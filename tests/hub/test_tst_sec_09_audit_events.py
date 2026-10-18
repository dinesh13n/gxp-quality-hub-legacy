"""TST-SEC-09 (AC-SEC-09, FR-SEC-02, BEH-SEC-05) - a decision event, a policy change, a Zone H attempt, an
authorisation failure and a login failure each produce exactly one audit record with the BEH-SEC-05 fields,
chain-linked.

Zone H attempt, authz failure and login failure are driven through the real C2 code paths. Decision-event and
policy-change PRODUCERS arrive in INC-04/INC-05; here they are exercised through the same C2 API they must use
(`audit.change` = change + audit record in one transaction). Re-run when those producers exist (RTD).
"""
import json
import os
import re
import unittest

import _support as S
import _inc03 as H
from hub.security import audit, authz
from hub.security.canonical import GENESIS, canonical
from hub.security.errors import AuthBadCredentials, AuthForbidden

SCHEMA = os.path.join(S.CODE_ROOT, "docs", "12-specs", "contracts", "schemas", "audit-record.schema.json")


def setUpModule():
    S.require_sandbox()


class TST_SEC_09_AuditEvents(unittest.TestCase):

    def test_TST_SEC_09_a_one_record_per_action_chain_linked(self):
        """TST-SEC-09 / AC-SEC-09: 5 actions -> 5 new records (fields, outcome, correlation) linked prev_hash -> hash."""
        st = H.Store("sec09-")
        try:
            pw = H.password()
            st.authn.create_user("rev", pw, ["reviewer"], "op")
            st.authn.create_user("disp", pw, ["dispositioner"], "op")
            az = authz.Authorizer(st.con, st.s, st.clock, st.authn, st.anchor)
            t_rev, t_disp = st.authn.login("rev", pw, "setup"), st.authn.login("disp", pw, "setup")
            st.con.execute("CREATE TABLE scratch_decision(case_id TEXT, transition TEXT)")
            st.con.commit()
            base = audit.head(st.con)[0]
            with audit.change(st.con, st.clock, anchor=st.anchor, actor="rev", actor_kind="human", action="DECISION_EVENT",
                              outcome="success", correlation_id="c-dec", object_ref="case:1",
                              details={"transition": "start_review"}):
                st.con.execute("INSERT INTO scratch_decision VALUES ('1','start_review')")
            with audit.change(st.con, st.clock, anchor=st.anchor, actor="rev", actor_kind="human", action="POLICY_CHANGE",
                              outcome="success", correlation_id="c-pol", object_ref="policy:P-1@2",
                              details={"from_version": 1, "to_version": 2}):
                pass
            with self.assertRaises(AuthForbidden):
                az.authorize("POST", "/api/v2/zone-h/actions", t_disp, "c-zh")       # holders empty
            with self.assertRaises(AuthForbidden):
                az.authorize("GET", "/api/v2/metrics/case-cost", t_rev, "c-authz")
            with self.assertRaises(AuthBadCredentials):
                st.authn.login("rev", "wrong", "c-login")
            rows = st.audit_rows()[base:]
            got = [(r["action"], r["outcome"], r["correlation_id"]) for r in rows]
            self.assertEqual(got, [("DECISION_EVENT", "success", "c-dec"), ("POLICY_CHANGE", "success", "c-pol"),
                                   ("ZONE_H_ATTEMPT", "denied", "c-zh"), ("AUTHZ_DENIED", "denied", "c-authz"),
                                   ("LOGIN", "denied", "c-login")])
            with open(SCHEMA, encoding="utf-8") as f:
                schema = json.load(f)
            ts = re.compile(schema["properties"]["occurred_at"]["pattern"])
            all_rows = st.audit_rows()
            prev = GENESIS
            for r in all_rows:
                rec = dict(r, details=json.loads(r["details"]))
                self.assertEqual(set(rec), set(schema["properties"]))
                self.assertTrue(set(schema["required"]) <= {k for k, v in rec.items() if v is not None})
                self.assertRegex(r["occurred_at"], ts)
                self.assertEqual(r["details"], canonical(rec["details"]))
                self.assertEqual(r["prev_hash"], prev)
                prev = r["hash"]
            self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")
        finally:
            st.close()


if __name__ == "__main__":
    unittest.main()
