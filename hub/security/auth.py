"""Local authenticator (stopgap behind the Authenticator interface, ADR-013 option B, BEH-SEC-02/03).

* Users are created OFFLINE by the host operator (`python -m hub.admin user create`); a fresh install has zero
  principals and no default/bootstrap credentials (AC-SEC-04).
* Passwords: PBKDF2-HMAC-SHA256 (hashlib.pbkdf2_hmac), per-user 16-byte salt from os.urandom, iterations from
  config (>= 600000), constant-time comparison (hmac.compare_digest), minimum length from config (>= 12).
* Sessions: 256-bit token from os.urandom (the `secrets` module is not used: TST-CO-13 b forbids importing it in
  hub/; os.urandom is the same CSPRNG source); only sha256(token) is stored.
* Lockout: `lockout_threshold` failures inside `lockout_window_seconds` lock the principal for
  `lockout_duration_seconds` (proposed 5/15 min/15 min, A-12-F09-1). Failure responses are generic.
* Every login success/failure/lockout and every session rejection writes an audit record in the same
  transaction as the login_attempt / session row (BEH-SEC-05). No password/token/hash goes into audit or logs.
"""
import hashlib
import hmac
import logging
import os

from hub.security import audit
from hub.security.canonical import parse
from hub.security.errors import (AuthBadCredentials, AuthLocked, AuthSessionExpired, AuthUnauthenticated,
                                 PasswordPolicy)

LOG = logging.getLogger("hub.security.auth")
ROLES = ("reviewer", "quality_lead", "compliance", "finance_read", "integration", "dispositioner")
HUMAN_ONLY_ROLES = ("reviewer", "quality_lead", "compliance", "finance_read", "dispositioner")
_DUMMY_SALT = b"\x00" * 16


def _hash_password(password, salt, iterations):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations).hex()


def token_digest(token):
    return hashlib.sha256(token.encode("ascii")).hexdigest()


class Principal(object):
    def __init__(self, principal_id, kind, roles, status):
        self.principal_id, self.kind, self.roles, self.status = principal_id, kind, tuple(sorted(roles)), status

    @property
    def actor_kind(self):
        return "human" if self.kind == "human" else "service"

    def as_dict(self):
        return {"principal_id": self.principal_id, "kind": self.kind, "roles": list(self.roles), "status": self.status}


class Session(object):
    def __init__(self, principal, token_sha256, created_at, last_seen_at, reauth_at):
        self.principal, self.token_sha256 = principal, token_sha256
        self.created_at, self.last_seen_at, self.reauth_at = created_at, last_seen_at, reauth_at


class LocalAuthenticator(object):
    """Authenticator interface: create_user / login / authenticate / reauthenticate / logout."""

    def __init__(self, con, settings, clock, anchor=None):
        self.con, self.s, self.clock, self.anchor = con, settings, clock, anchor
        self.a = settings["auth"]

    # ---- administration (offline, host operator) ----
    def principal(self, principal_id):
        row = self.con.execute("SELECT principal_id, principal_kind, status FROM principal WHERE principal_id = ?",
                               (principal_id,)).fetchone()
        if row is None:
            return None
        roles = [r[0] for r in self.con.execute("SELECT role FROM principal_role WHERE principal_id = ? ORDER BY role",
                                                (principal_id,))]
        return Principal(row[0], row[1], roles, row[2])

    def count_principals(self):
        return self.con.execute("SELECT count(*) FROM principal").fetchone()[0]

    def create_user(self, principal_id, password, roles, operator, kind="human", correlation_id="cli"):
        roles = sorted(set(roles))
        bad = [r for r in roles if r not in ROLES]
        if bad or not roles:
            raise PasswordPolicy({"roles": roles, "allowed": list(ROLES)}) if not bad else \
                PasswordPolicy({"unknown_roles": bad})
        if kind == "service" and any(r in HUMAN_ONLY_ROLES for r in roles):
            raise PasswordPolicy({"reason": "service principals may only hold 'integration' (BEH-SEC-03)"})
        if kind == "human" and "integration" in roles:
            raise PasswordPolicy({"reason": "'integration' is a non-human role (SEC-2)"})
        salt = hashed = algo = iters = None
        if kind == "human":
            if not isinstance(password, str) or len(password) < self.a["password_min_length"]:
                raise PasswordPolicy({"min_length": self.a["password_min_length"]})
            salt = os.urandom(16)
            iters = self.a["pbkdf2_iterations"]
            hashed, algo = _hash_password(password, salt, iters), "pbkdf2_sha256"
        now = self.clock()
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=operator, actor_kind="human",
                          action="USER_CREATED", outcome="success", correlation_id=correlation_id,
                          object_ref="principal:" + principal_id,
                          details={"kind": kind, "roles": roles, "kdf": algo, "kdf_iterations": iters}):
            self.con.execute("INSERT INTO principal(principal_id, principal_kind, pw_algo, pw_iterations, pw_salt, pw_hash,"
                             " status, created_at, created_by) VALUES (?,?,?,?,?,?,'active',?,?)",
                             (principal_id, kind, algo, iters, salt.hex() if salt else None, hashed, now, operator))
            for r in roles:
                self.con.execute("INSERT INTO principal_role(principal_id, role, granted_at, granted_by) VALUES (?,?,?,?)",
                                 (principal_id, r, now, operator))
        return self.principal(principal_id)

    # ---- lockout state ----
    def _seconds(self, ts):
        return parse(ts).timestamp()

    def _locked_until(self, principal_id, now_s):
        row = self.con.execute("SELECT max(occurred_at) FROM login_attempt WHERE principal_id = ? AND outcome = 'lockout_started'",
                               (principal_id,)).fetchone()
        if row[0] is None:
            return None
        until = self._seconds(row[0]) + self.a["lockout_duration_seconds"]
        return until if now_s < until else None

    def _recent_failures(self, principal_id, now_s):
        since = now_s - self.a["lockout_window_seconds"]
        n = 0
        for (ts, outcome) in self.con.execute(
                "SELECT occurred_at, outcome FROM login_attempt WHERE principal_id = ? ORDER BY attempt_seq DESC",
                (principal_id,)):
            if outcome in ("success", "lockout_started") or self._seconds(ts) < since:
                break
            if outcome == "bad_credentials":
                n += 1
        return n

    # ---- login ----
    def login(self, principal_id, password, correlation_id):
        """Return a fresh session token (shown once). Raises E-AUTH-BAD-CREDENTIALS / E-AUTH-LOCKED (generic)."""
        now = self.clock()
        now_s = self._seconds(now)
        p = self.principal(principal_id)
        known = p is not None and p.status == "active" and p.kind == "human"
        actor = principal_id if p is not None else "unknown-principal"
        if known and self._locked_until(principal_id, now_s):
            _hash_password(password or "", _DUMMY_SALT, self.a["pbkdf2_iterations"])
            with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind="human",
                              action="LOGIN", outcome="denied", correlation_id=correlation_id,
                              details={"result": "locked"}):
                self.con.execute("INSERT INTO login_attempt(principal_id, occurred_at, outcome) VALUES (?,?,'locked')",
                                 (principal_id, now))
            LOG.warning("login refused (locked) principal=%s correlation_id=%s", actor, correlation_id)
            raise AuthLocked()
        ok = False
        if known:
            row = self.con.execute("SELECT pw_salt, pw_iterations, pw_hash FROM principal WHERE principal_id = ?",
                                   (principal_id,)).fetchone()
            cand = _hash_password(password or "", bytes.fromhex(row[0]), row[1])
            ok = hmac.compare_digest(cand, row[2])
        else:
            _hash_password(password or "", _DUMMY_SALT, self.a["pbkdf2_iterations"])  # equalise timing
        if ok:
            token = os.urandom(32).hex()
            digest = token_digest(token)
            with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind="human",
                              action="LOGIN", outcome="success", correlation_id=correlation_id,
                              details={"result": "session_created"}):
                self.con.execute("INSERT INTO login_attempt(principal_id, occurred_at, outcome) VALUES (?,?,'success')",
                                 (principal_id, now))
                self.con.execute("INSERT INTO session(token_sha256, principal_id, created_at, last_seen_at, reauth_at)"
                                 " VALUES (?,?,?,?,?)", (digest, principal_id, now, now, now))
            LOG.info("login ok principal=%s correlation_id=%s", actor, correlation_id)
            return token
        lock = False
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind="human",
                          action="LOGIN", outcome="denied", correlation_id=correlation_id,
                          details={"result": "bad_credentials", "principal_known": p is not None}):
            self.con.execute("INSERT INTO login_attempt(principal_id, occurred_at, outcome) VALUES (?,?,'bad_credentials')",
                             (principal_id if p is not None else None, now))
            if known and self._recent_failures(principal_id, now_s) >= self.a["lockout_threshold"]:
                self.con.execute("INSERT INTO login_attempt(principal_id, occurred_at, outcome) VALUES (?,?,'lockout_started')",
                                 (principal_id, now))
                lock = True
        if lock:
            audit.append(self.con, self.clock, anchor=self.anchor, actor=actor, actor_kind="human", action="LOCKOUT",
                         outcome="success", correlation_id=correlation_id, object_ref="principal:" + principal_id,
                         details={"threshold": self.a["lockout_threshold"],
                                  "duration_seconds": self.a["lockout_duration_seconds"]})
        LOG.warning("login failed principal=%s correlation_id=%s", actor, correlation_id)
        raise AuthBadCredentials()

    # ---- sessions ----
    def authenticate(self, token, correlation_id, touch=True):
        """Resolve a session token to a Session; E-AUTH-UNAUTHENTICATED / E-AUTH-SESSION-EXPIRED otherwise."""
        if not token:
            raise AuthUnauthenticated()
        digest = token_digest(token)
        row = self.con.execute("SELECT principal_id, created_at, last_seen_at, reauth_at, revoked_at FROM session"
                               " WHERE token_sha256 = ?", (digest,)).fetchone()
        if row is None or row[4] is not None:
            raise AuthUnauthenticated()
        now = self.clock()
        now_s = self._seconds(now)
        if now_s - self._seconds(row[2]) > self.a["session_idle_seconds"] or \
                now_s - self._seconds(row[1]) > self.a["session_absolute_seconds"]:
            with audit.change(self.con, self.clock, anchor=self.anchor, actor=row[0], actor_kind="human",
                              action="SESSION_EXPIRED", outcome="denied", correlation_id=correlation_id):
                self.con.execute("UPDATE session SET revoked_at = ? WHERE token_sha256 = ?", (now, digest))
            raise AuthSessionExpired()
        p = self.principal(row[0])
        if p is None or p.status != "active":
            raise AuthUnauthenticated()
        if touch:
            with self.con:
                self.con.execute("UPDATE session SET last_seen_at = ? WHERE token_sha256 = ?", (now, digest))
        return Session(p, digest, row[1], now if touch else row[2], row[3])

    def reauthenticate(self, token, password, correlation_id):
        """Step-up re-authentication (Zone H window, zone_h.reauth_window_seconds)."""
        sess = self.authenticate(token, correlation_id)
        row = self.con.execute("SELECT pw_salt, pw_iterations, pw_hash FROM principal WHERE principal_id = ?",
                               (sess.principal.principal_id,)).fetchone()
        ok = hmac.compare_digest(_hash_password(password or "", bytes.fromhex(row[0]), row[1]), row[2])
        now = self.clock()
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=sess.principal.principal_id,
                          actor_kind="human", action="REAUTH", outcome="success" if ok else "denied",
                          correlation_id=correlation_id):
            if ok:
                self.con.execute("UPDATE session SET reauth_at = ? WHERE token_sha256 = ?", (now, sess.token_sha256))
        if not ok:
            raise AuthBadCredentials()
        sess.reauth_at = now
        return sess

    def logout(self, token, correlation_id):
        sess = self.authenticate(token, correlation_id, touch=False)
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=sess.principal.principal_id,
                          actor_kind="human", action="LOGOUT", outcome="success", correlation_id=correlation_id):
            self.con.execute("UPDATE session SET revoked_at = ? WHERE token_sha256 = ?", (self.clock(), sess.token_sha256))
