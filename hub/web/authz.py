"""WebAuthorizer: the INC-03 deny-by-default Authorizer applied to the API registry AND the page registry (INC-08).

hub/security/authz.py is frozen (TST-SEC-01 pins its registry to the OpenAPI), so this is a subclass with one extra rule set:
  * routes that start a Zone H decision (OP-GATE-02, UI-DISPOSITION): a role failure is E-GATE-NOT-AUTHORISED (spec: 'E-AUTH-FORBIDDEN or
    E-GATE-NOT-AUTHORISED'), audited as ZONE_H_ATTEMPT denied; the holder / re-authentication checks are NOT repeated here, the choke point
    (hub.gate.actions) runs them exactly once, before it reads the payload;
  * routes that only READ the evidence pack (OP-GATE-01, UI-PACK): the INC-03 Zone H eligibility (human, holder, step-up window) runs here and its
    refusal is translated to E-GATE-NO-HOLDERS (empty list) / E-GATE-NOT-AUTHORISED / E-GATE-REAUTH-REQUIRED.
Everything else is Authorizer.authorize unchanged in meaning: unknown route -> 403, no token -> 401, role not in the matrix -> 403 + audit.
"""
from hub.gate.errors import GateNoHolders, GateNotAuthorised, GateReauthRequired
from hub.security import audit
from hub.security.authz import Authorizer, PUBLIC
from hub.security.errors import AuthForbidden, AuthUnauthenticated

CHOKE_OPS = ("OP-GATE-02", "UI-DISPOSITION")
PACK_OPS = ("OP-GATE-01", "UI-PACK")


class WebAuthorizer(Authorizer):
    def authorize(self, method, path, token, correlation_id):
        r = self.route(method, path)
        if r is None:
            raise AuthForbidden({"reason": "route not registered (deny by default)"})
        if PUBLIC in r["roles"]:
            return None
        if not token:
            raise AuthUnauthenticated()
        sess = self.authn.authenticate(token, correlation_id)
        p = sess.principal
        gate_route = r["op_id"] in CHOKE_OPS or r["op_id"] in PACK_OPS
        if not [x for x in p.roles if x in r["roles"]]:
            audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                         action="ZONE_H_ATTEMPT" if gate_route else "AUTHZ_DENIED", outcome="denied", correlation_id=correlation_id,
                         object_ref=r["op_id"], details={"method": r["method"], "path": r["path"], "reason": "role"})
            raise GateNotAuthorised({"reason": "role"}) if gate_route else AuthForbidden()
        if r["op_id"] in PACK_OPS:
            try:
                self._zone_h(sess, r, correlation_id)
            except AuthForbidden as e:
                reason = (e.details or {}).get("reason")
                if reason == "reauth_required":
                    raise GateReauthRequired({"reason": reason})
                if not self.s["zone_h"]["holders"]:
                    raise GateNoHolders({"reason": "no_holders_configured"})
                raise GateNotAuthorised({"reason": reason})
        return sess
