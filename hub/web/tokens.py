"""Service tokens and the composite authenticator (BEH-SEC-03, AC-SEC-08; INC-08).

* A service token belongs to a `service` principal (role `integration` only, created offline by `python -m hub.admin user create --kind service`) and
  is issued by the host operator (`python -m hub.web token issue`). Format `svc_<48 hex>` from os.urandom; only sha256(token) is stored (insert-only
  `service_token`, revocation = a row in `service_token_revocation`). The token is shown ONCE and never written to audit, log or config.
* A service token authenticates a SERVICE session: kind service, role integration, `reauth_at` = the issue time (never fresh). It can therefore never
  satisfy the Zone H eligibility check, never log in, and is refused by every human-only route (the role matrix) with an audited denial.
* CompositeAuthenticator is the one `authenticate()` the route authoriser sees: `svc_` tokens -> this module, everything else -> LocalAuthenticator
  (cookie / bearer session tokens are 64 hex chars, so the prefixes cannot collide). login / reauthenticate / logout are the human authenticator's.
Assumption A-INC08-1 (Stage 24): the Stage 12 spec names a service token (BEH-SEC-03) but defines no issue/rotate/expiry mechanism; this is the minimal
one. Expiry is optional per token; rotation = issue a new token and revoke the old one.
"""
import os

from hub.security import audit
from hub.security.auth import Principal, Session, token_digest
from hub.security.canonical import parse
from hub.security.errors import AuthUnauthenticated, PasswordPolicy

PREFIX = "svc_"


def is_service_token(token):
    return isinstance(token, str) and token.startswith(PREFIX)


def issue(con, clock, anchor, principal_id, label, operator, expires_at=None, correlation_id="web-token"):
    """Issue a token for an existing active `service` principal. Returns the token text (shown once)."""
    row = con.execute("SELECT principal_kind, status FROM principal WHERE principal_id = ?", (principal_id,)).fetchone()
    roles = [r[0] for r in con.execute("SELECT role FROM principal_role WHERE principal_id = ?", (principal_id,))]
    if row is None or row[0] != "service" or row[1] != "active" or roles != ["integration"]:
        raise PasswordPolicy({"reason": "a service token needs an active service principal with exactly the role 'integration'"})
    if not isinstance(label, str) or not label.strip() or len(label) > 80:
        raise PasswordPolicy({"reason": "label required (at most 80 characters)"})
    token = PREFIX + os.urandom(24).hex()
    digest = token_digest(token)
    with audit.change(con, clock, anchor=anchor, actor=operator, actor_kind="human", action="SERVICE_TOKEN_ISSUED", outcome="success",
                      correlation_id=correlation_id, object_ref="principal:" + principal_id,
                      details={"principal": principal_id, "label": label.strip(), "expires_at": expires_at, "digest_prefix": digest[:8]}):
        con.execute("INSERT INTO service_token(token_sha256, principal_id, label, created_at, created_by, expires_at) VALUES (?,?,?,?,?,?)",
                    (digest, principal_id, label.strip(), clock(), operator, expires_at))
    return token


def revoke(con, clock, anchor, token_or_prefix, operator, correlation_id="web-token"):
    """Revoke by full token or by the 8-hex digest prefix shown at issue time."""
    digest = token_digest(token_or_prefix) if is_service_token(token_or_prefix) else None
    if digest is None:
        rows = con.execute("SELECT token_sha256 FROM service_token WHERE token_sha256 LIKE ?", (str(token_or_prefix)[:8] + "%",)).fetchall()
        digest = rows[0][0] if len(rows) == 1 and len(str(token_or_prefix)) >= 8 else None
    if digest is None or con.execute("SELECT 1 FROM service_token WHERE token_sha256 = ?", (digest,)).fetchone() is None:
        raise AuthUnauthenticated()
    if con.execute("SELECT 1 FROM service_token_revocation WHERE token_sha256 = ?", (digest,)).fetchone():
        return {"revoked": True, "already": True}
    with audit.change(con, clock, anchor=anchor, actor=operator, actor_kind="human", action="SERVICE_TOKEN_REVOKED", outcome="success",
                      correlation_id=correlation_id, object_ref="service_token:" + digest[:8], details={"digest_prefix": digest[:8]}):
        con.execute("INSERT INTO service_token_revocation(token_sha256, revoked_at, revoked_by) VALUES (?,?,?)", (digest, clock(), operator))
    return {"revoked": True, "already": False}


class CompositeAuthenticator(object):
    def __init__(self, human, con, clock):
        self.human, self.con, self.clock = human, con, clock

    def __getattr__(self, name):  # login / reauthenticate / logout / principal / create_user ...
        return getattr(self.human, name)

    def authenticate(self, token, correlation_id, touch=True):
        if not is_service_token(token):
            return self.human.authenticate(token, correlation_id, touch)
        digest = token_digest(token)
        row = self.con.execute("SELECT principal_id, created_at, expires_at FROM service_token WHERE token_sha256 = ?", (digest,)).fetchone()
        if row is None or self.con.execute("SELECT 1 FROM service_token_revocation WHERE token_sha256 = ?", (digest,)).fetchone():
            raise AuthUnauthenticated()
        if row[2] is not None and parse(self.clock()).timestamp() > parse(row[2]).timestamp():
            raise AuthUnauthenticated()
        p = self.human.principal(row[0])
        if p is None or p.status != "active" or p.kind != "service" or list(p.roles) != ["integration"]:
            raise AuthUnauthenticated()
        return Session(Principal(p.principal_id, "service", p.roles, "active"), digest, row[1], row[1], row[1])
