"""TST-SEC-18 (AC-SEC-18, PNFR-08, PNFR-10, BEH-SEC-07/11; class B: OD-S12-09 = hold-all, OD-15) - secret scan and
deletion-path grep over the code base -> 0 secret findings; no DELETE statements on retained tables; every retained
table in the store has an aborting delete trigger. Positive controls prove the scanners fire."""
import os
import unittest

import _support as S
import _inc03 as H
from hub.security import scan


def setUpModule():
    S.require_sandbox()


class TST_SEC_18_SecretScanDeletionGrep(unittest.TestCase):

    def test_TST_SEC_18_a_code_base_clean(self):
        """TST-SEC-18 / AC-SEC-18: hub/ + tests/hub secret scan 0; hub/ deletion grep 0; store retention triggers complete."""
        st = H.Store("sec18a-")
        try:
            rep = scan.run(S.CODE_ROOT, st.con)
        finally:
            st.close()
        self.assertEqual(rep["secret_findings"], [])
        self.assertEqual(rep["deletion_findings"], [])
        self.assertEqual(rep["tables_without_delete_trigger"], [])
        self.assertTrue(rep["clean"])

    def test_TST_SEC_18_b_positive_controls(self):
        """TST-SEC-18: planted key block / token / credential assignment and a retained-table delete are each detected."""
        d = S.tmpdir("sec18b-")
        samples = {
            "k.txt": "-----" + "BEGIN RSA PRIVATE KEY-----\n",
            "a.py": "aws = '" + "AK" + "IA" + "ABCDEFGHIJKLMNOP'\n",
            "c.py": "pass" + "word = '" + "hunter2hunter2'\n",
            "g.json": '{"t": "' + "gh" + "p_" + "a" * 36 + '"}\n',
        }
        for fn, text in samples.items():
            with open(os.path.join(d, fn), "w") as f:
                f.write(text)
        kinds = sorted(x["kind"] for x in scan.secret_scan([d]))
        self.assertEqual(kinds, ["aws_access_key_id", "credential_assignment", "github_token", "private_key_block"])
        with open(os.path.join(d, "m.sql"), "w") as f:
            f.write("DEL" + "ETE FROM audit_log WHERE 1;\nDEL" + "ETE FROM scratch;\nDR" + "OP TABLE IF EXISTS principal;\n")
        found = sorted((x["kind"], x["table"]) for x in scan.deletion_grep([d]))
        self.assertEqual(found, [("delete", "audit_log"), ("drop_table", "principal")])

    def test_TST_SEC_18_c_cli_scan(self):
        """TST-SEC-18: `python -m hub.admin scan --data-dir` -> exit 0, clean."""
        base = S.tmpdir("sec18c-")
        cfg = H.write_config(base)
        d = os.path.join(base, "data")
        H.admin(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg)
        p = H.admin(["scan", "--data-dir", d], cfg)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(H.out_json(p)["clean"])


if __name__ == "__main__":
    unittest.main()
