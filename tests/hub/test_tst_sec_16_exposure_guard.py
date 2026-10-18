"""TST-SEC-16 (AC-SEC-16, PNFR-08, BEH-SEC-08, EC-12) - start-up with a non-loopback bind and no exposure approval is
refused E-SEC-EXPOSURE-NOT-APPROVED (process exit 9); with approval but no TLS settings it is also refused.
INC-03 has no listener yet: `python -m hub.admin startup-check` runs the start-up guard the server will call first."""
import json
import os
import unittest

import _support as S
import _inc03 as H


def setUpModule():
    S.require_sandbox()


class TST_SEC_16_ExposureGuard(unittest.TestCase):

    def _check(self, network):
        base = S.tmpdir("sec16-")
        cfg = H.write_config(base, {"network": network} if network is not None else None)
        return H.admin(["startup-check"], cfg)

    def test_TST_SEC_16_a_default_loopback_starts(self):
        """TST-SEC-16: default config -> bind 127.0.0.1, exit 0; ::1 and localhost are loopback too."""
        p = self._check(None)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(H.out_json(p), {"bind": "127.0.0.1", "exposure": "loopback"})
        for b in ("::1", "localhost", "127.0.0.1:8081", "[::1]:8081"):
            with self.subTest(bind=b):
                self.assertEqual(self._check({"bind": b}).returncode, 0)

    def test_TST_SEC_16_b_non_loopback_without_approval_refused(self):
        """TST-SEC-16 / AC-SEC-16: 0.0.0.0 / LAN IP / hostname without approval -> exit 9 E-SEC-EXPOSURE-NOT-APPROVED."""
        for b in ("0.0.0.0", "192.168.1.5:8081", "::", "hub.example.internal"):
            for net in ({"bind": b}, {"bind": b, "exposure_approved": True}):  # approved=true but no HAR-05 reference
                with self.subTest(net=net):
                    p = self._check(net)
                    self.assertEqual(p.returncode, 9)
                    self.assertEqual(json.loads(p.stderr)["code"], "E-SEC-EXPOSURE-NOT-APPROVED")
                    self.assertEqual(p.stdout, "")

    def test_TST_SEC_16_c_approved_without_tls_refused_with_tls_allowed(self):
        """TST-SEC-16 / AC-SEC-16: approval + reference but no TLS -> refused; with TLS cert/key settings -> starts."""
        net = {"bind": "0.0.0.0", "exposure_approved": True, "exposure_approval_ref": "HAR-05/synthetic-test-ref"}
        p = self._check(net)
        self.assertEqual((p.returncode, json.loads(p.stderr)["code"]), (9, "E-SEC-EXPOSURE-NOT-APPROVED"))
        self.assertIn("TLS", json.loads(p.stderr)["details"]["reason"])
        p = self._check(dict(net, tls={"cert_file": "/etc/hub/tls.crt", "key_file": "/etc/hub/tls.key"}))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(H.out_json(p)["exposure"], "approved")


if __name__ == "__main__":
    unittest.main()
