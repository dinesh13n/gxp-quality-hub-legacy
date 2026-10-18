"""TST-SEC-01 (AC-SEC-01, FR-SEC-01, PNFR-07, BEH-SEC-01) - every registered route (enumerated by the test from the
Stage 12 OpenAPI contract and the hub route registry) called without credentials -> 401 E-AUTH-UNAUTHENTICATED,
except GET /healthz and POST /api/v2/auth/login; /healthz carries no case data; unregistered routes are denied.

Level: static/introspection. INC-03 has no HTTP server (that is INC-04+); the test drives the single authorisation
decision point `hub.security.authz.Authorizer.authorize` that every route handler must call.
"""
import os
import re
import unittest

import _support as S
import _inc03 as H
from hub.security import authz, openapi_routes
from hub.security.errors import AuthForbidden, AuthUnauthenticated

OPENAPI = os.path.join(S.CODE_ROOT, "docs", "12-specs", "contracts", "openapi.yaml")
PUBLIC = {("GET", "/healthz"), ("POST", "/api/v2/auth/login")}


def setUpModule():
    S.require_sandbox()


class TST_SEC_01_RouteRegistry(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.st = H.Store("sec01-")
        cls.az = authz.Authorizer(cls.st.con, cls.st.s, cls.st.clock, cls.st.authn, cls.st.anchor)

    @classmethod
    def tearDownClass(cls):
        cls.st.close()

    def test_TST_SEC_01_a_registry_matches_contract_and_declares_permissions(self):
        """TST-SEC-01: the route registry equals the OpenAPI route table (48 operations); every route declares a permission."""
        with open(OPENAPI, encoding="utf-8") as f:
            contract = openapi_routes.parse(f.read())
        registry = authz.load_registry()
        self.assertEqual(len(contract), 48)
        self.assertEqual(registry, contract)
        for r in registry:
            with self.subTest(route=(r["method"], r["path"])):
                self.assertTrue(r["op_id"])
                self.assertTrue(r["roles"], "route without a declared permission (deny by default)")

    def test_TST_SEC_01_b_unauthenticated_401_except_public(self):
        """TST-SEC-01 / AC-SEC-01: no credentials -> 401 E-AUTH-UNAUTHENTICATED on every route except /healthz and /auth/login."""
        seen_public = set()
        for r in authz.load_registry():
            key = (r["method"], r["path"])
            with self.subTest(route=key):
                for token in (None, "", "not-a-session-token"):
                    if key in PUBLIC:
                        self.assertIsNone(self.az.authorize(r["method"], r["path"], token, "sec01"))
                        seen_public.add(key)
                    else:
                        with self.assertRaises(AuthUnauthenticated) as cm:
                            self.az.authorize(r["method"], r["path"], token, "sec01")
                        self.assertEqual((cm.exception.code, cm.exception.http), ("E-AUTH-UNAUTHENTICATED", 401))
        self.assertEqual(seen_public, PUBLIC)

    def test_TST_SEC_01_c_unregistered_route_denied_by_default(self):
        """TST-SEC-01: a route not in the registry is refused (403) even without checking credentials."""
        for m, p in (("GET", "/api/v2/admin/backdoor"), ("DELETE", "/api/v2/cases/{case_id}/events"), ("GET", "/healthz/x")):
            with self.assertRaises(AuthForbidden):
                self.az.authorize(m, p, None, "sec01")

    def test_TST_SEC_01_d_healthz_contract_has_no_case_data(self):
        """TST-SEC-01: /healthz response shape (OpenAPI Health) declares only `status`; no case fields."""
        with open(OPENAPI, encoding="utf-8") as f:
            text = f.read()
        block = re.search(r"\n    Health:\n((?:      .*\n|        .*\n)+)", text).group(1)
        self.assertIn("status", block)
        for word in ("case", "account", "amount", "evidence", "tenant"):
            self.assertNotIn(word, block.lower())


if __name__ == "__main__":
    unittest.main()
