"""TST-SEC-21 (AC-SEC-21, AC-GATE-22, FR-SEC-02) - holder list changed and process restarted -> the audit chain holds a
CONFIG_LOADED record with the (new) config hash. Holders ship empty (FR-GATE-04; OD-S12-06 open): the changed list
here is a synthetic test value, not a holder decision."""
import json
import os
import sqlite3
import unittest

import _support as S
import _inc03 as H
from hub import config
from hub.security import audit, settings


def setUpModule():
    S.require_sandbox()


class TST_SEC_21_ConfigLoaded(unittest.TestCase):

    def test_TST_SEC_21_a_restart_with_changed_holders(self):
        """TST-SEC-21 / AC-SEC-21: run 1 (holders []), run 2 (holders ['synthetic-holder']) -> two CONFIG_LOADED with each config hash."""
        base = S.tmpdir("sec21-")
        d = os.path.join(base, "data")
        cfg1 = H.write_config(base)
        self.assertEqual(H.admin(["migrate", "--data-dir", d, "--backup-root", os.path.join(base, "bk")], cfg1).returncode, 0)
        h1 = settings.config_hash(config.load(cfg1))
        with open(cfg1) as f:
            c = json.load(f)
        c["zone_h"] = {"holders": ["synthetic-holder"], "reauth_window_seconds": 300}
        c["approval_refs"] = {"zone_h.holders": H.TEST_APPROVAL_REF}  # Stage 23 DW-17: a non-default decision flag needs an approval_ref (a test marker, not an approval)
        cfg2 = os.path.join(base, "hub-config-2.json")
        with open(cfg2, "w") as f:
            json.dump(c, f)
        h2 = settings.config_hash(config.load(cfg2))
        self.assertNotEqual(h1, h2)
        p = H.admin(["anchor", "--data-dir", d], cfg2)  # process restart with the changed config
        self.assertEqual(p.returncode, 0, p.stderr)
        con = sqlite3.connect(os.path.join(d, "hub.sqlite3"))
        try:
            rows = [json.loads(r[0]) for r in con.execute(
                "SELECT details FROM audit_log WHERE action = 'CONFIG_LOADED' ORDER BY audit_seq")]
            self.assertEqual([r["config_hash"] for r in rows], [h1, h2])
            self.assertEqual([r["zone_h_holders"] for r in rows], [[], ["synthetic-holder"]])
            self.assertEqual(audit.verify(con, os.path.join(base, "anchor", H.ANCHOR))["status"], "ok")
        finally:
            con.close()

    def test_TST_SEC_21_b_default_holders_empty(self):
        """TST-SEC-21: default config ships zone_h.holders = [] and reauth window 300 s (Stage 12 proposal, Stage 24 to confirm)."""
        s = settings.resolve(config.load())
        self.assertEqual((s["zone_h"]["holders"], s["zone_h"]["reauth_window_seconds"]), ([], 300))


if __name__ == "__main__":
    unittest.main()
