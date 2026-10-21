"""Deny-by-default route authorisation + Zone H holder check (BEH-SEC-01/04, ADR-013, SEC-2/SEC-3).

The route registry (route_registry.json, generated from the Stage 12 OpenAPI x-roles) is the permission matrix
as DATA. `authorize()` is the single decision point the future HTTP layer (INC-04+) must call:
  * route not in the registry                  -> 403 E-AUTH-FORBIDDEN (deny by default)
  * 'public' route (/healthz, /auth/login)     -> allowed without credentials
  * no/invalid session                         -> 401 E-AUTH-UNAUTHENTICATED
  * role not in x-roles                        -> 403 E-AUTH-FORBIDDEN, audited AUTHZ_DENIED
  * Zone H op (OP-GATE-01/02)                  -> additionally principal in zone_h.holders AND human AND
                                                  re-authenticated within zone_h.reauth_window_seconds;
                                                  every attempt audited ZONE_H_ATTEMPT (accepted or rejected)
"""
import json
import os

from hub.security import audit, zone_h
from hub.security.errors import AuthForbidden, AuthUnauthenticated

REGISTRY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "route_registry.json")
ZONE_H_OPS = ("OP-GATE-01", "OP-GATE-02")
PUBLIC = "public"


def load_registry(path=REGISTRY_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["routes"]


class Authorizer(object):
    def __init__(self, con, settings, clock, authenticator, anchor=None, registry=None):
        self.con, self.s, self.clock, self.authn, self.anchor = con, settings, clock, authenticator, anchor
        self.routes = {(r["method"], r["path"]): r for r in (registry if registry is not None else load_registry())}

    def route(self, method, path):
        return self.routes.get((method.upper(), path))

    def authorize(self, method, path, token, correlation_id):
        """Return the Session (or None for a public route); raise E-AUTH-* otherwise."""
        r = self.route(method, path)
        if r is None:
            raise AuthForbidden({"reason": "route not registered (deny by default)"})
        if PUBLIC in r["roles"]:
            return None
        if not token:
            raise AuthUnauthenticated()
        sess = self.authn.authenticate(token, correlation_id)
        p = sess.principal
        allowed = [x for x in p.roles if x in r["roles"]]
        zone_h = r["op_id"] in ZONE_H_OPS
        if not allowed:
            audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                         action="ZONE_H_ATTEMPT" if zone_h else "AUTHZ_DENIED", outcome="denied",
                         correlation_id=correlation_id, object_ref=r["op_id"],
                         details={"method": r["method"], "path": r["path"], "reason": "role"})
            raise AuthForbidden()
        if zone_h:
            self._zone_h(sess, r, correlation_id)
        return sess

    def _zone_h(self, sess, r, correlation_id):
        p = sess.principal
        holders = self.s["zone_h"]["holders"]
        reason = zone_h.refusal(p, sess.reauth_at, self.clock, self.s["zone_h"], require_dispositioner=False,
                                distinguish_empty=False)  # Stage 20 DW-06: the one rule (role already checked by the route)
        audit.append(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                     action="ZONE_H_ATTEMPT", outcome="denied" if reason else "success",
                     correlation_id=correlation_id, object_ref=r["op_id"],
                     details={"method": r["method"], "path": r["path"], "reason": reason or "accepted",
                              "holders_configured": len(holders)})
        if reason:
            raise AuthForbidden({"reason": reason})
