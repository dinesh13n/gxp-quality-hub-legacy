"""WebApp: the framework-free request dispatcher of the loopback HTTP surface (ADR-014 option B; INC-08).

`handle(Request) -> Response` has no socket in it (hub.web.server owns the listener), so every rule below is the same in-process and over the wire.
Check order is the deterministic precedence of error-handling-spec ER-1 (the first failure is returned):
  1 transport: body size (413), malformed JSON / form (400 E-REQ-INVALID)      2 route (deny by default, 403) and authentication (401)
  3 CSRF (403)       4 authorisation, Zone H eligibility (403/423/401)      5 validation (400/422)      6 existence (404)      7 state (409)      8 rules (422)
Refusals at steps 2-4 are audited. One SQLite connection is opened per request and closed after it (no shared mutable state between requests apart
from the in-process metrics counters). Every response carries X-Correlation-Id (a valid incoming id is echoed, else a fresh one), nosniff,
`Content-Security-Policy: default-src 'self'`, Cache-Control: no-store, and NO CORS header. No request can reach the network: the app opens no socket.
"""
import os
import re
import sqlite3

from hub import web as hubweb
from hub.core.errors import HubError
from hub.decision import settings as dsettings
from hub.gate import modes
from hub.obs.log import Logger
from hub.security import audit, exposure, settings as sec_settings, transport
from hub.security.auth import LocalAuthenticator
from hub.security.canonical import parse, sha256_hex
from hub.security.errors import AuthForbidden, AuthSessionExpired, AuthUnauthenticated
from hub.store import db
from hub.web import csrf, ratelimit, schema as web_schema, wire
from hub.web.authz import CHOKE_OPS, WebAuthorizer
from hub.web.errors import Csrf, RateLimited, ReqInvalid, ReqTooLarge, StoreUnavailable
from hub.web.obs_http import HttpMetrics
from hub.web.routes import Table
from hub.web.tokens import CompositeAuthenticator

BODY_LIMIT = 1024 * 1024
SESSION_COOKIE = "hub_session"
_CID = re.compile(r"^[A-Za-z0-9._:-]{8,64}$")
_COOKIE_TOKEN = re.compile(r"^[A-Za-z0-9_]{16,200}$")
SECURITY_HEADERS = (("X-Content-Type-Options", "nosniff"), ("Content-Security-Policy", "default-src 'self'"), ("Cache-Control", "no-store"),
                    ("Referrer-Policy", "no-referrer"), ("X-Frame-Options", "DENY"))


REJECT_CODES = ("E-AUTH-UNAUTHENTICATED", "E-AUTH-BAD-CREDENTIALS", "E-AUTH-FORBIDDEN")  # what the limiter counts (403 only for an unregistered route)


def _is_store_fault(exc):
    """True for a failure of the SQLite file itself (cannot open, read-only, corrupt, disk full); a constraint / programming error stays a 500."""
    return isinstance(exc, (sqlite3.OperationalError, sqlite3.DatabaseError)) and not isinstance(
        exc, (sqlite3.IntegrityError, sqlite3.ProgrammingError, sqlite3.DataError, sqlite3.NotSupportedError, sqlite3.InterfaceError))


class Request(object):
    def __init__(self, method, path, query=None, headers=None, body=b"", peer="127.0.0.1"):
        self.method, self.path, self.query = method.upper(), path, dict(query or {})
        self.headers = dict((k.lower(), v) for k, v in (headers or {}).items())
        self.body, self.peer = body or b"", peer


class Response(object):
    def __init__(self, status, body=b"", content_type="application/json", headers=None):
        self.status, self.body, self.content_type, self.headers = status, body, content_type, list(headers or [])


class Ctx(object):
    """What a handler sees. Services are built on first use, on this request's connection."""

    def __init__(self, app, con, req, route, params, sess, cid, token, body):
        self.app, self.con, self.req, self.route, self.params, self.sess, self.cid, self.token, self.body = \
            app, con, req, route, params, sess, cid, token, body
        self.clock, self.s, self.anchor = app.clock, app.s, app.anchor
        self.extra_headers = []
        self.audit_actor = None
        self._svc = {}

    def svc(self, name, factory):
        if name not in self._svc:
            self._svc[name] = factory(self)
        return self._svc[name]

    def q(self, name, default=None):
        v = self.req.query.get(name)
        return default if v is None else v


class WebApp(object):
    def __init__(self, data_dir, cfg, clock, documents=None, sources=None, run_resources=None, site_of=None, log_sink=None, body_limit=BODY_LIMIT,
                 now_ms=None):
        self.data_dir = os.path.abspath(data_dir)
        self.cfg, self.clock = cfg, clock
        self.s = sec_settings.resolve(cfg)
        self.d = dsettings.resolve(cfg)
        self.disp = modes.resolve(cfg)
        self.search_cfg = dict({"enabled": False}, **(cfg.get("search") or {}))
        self.anchor_path = sec_settings.anchor_path(self.s, self.data_dir)
        self.anchor = audit.Anchor(self.anchor_path, self.s["audit"]["anchor_every"])
        self.documents, self.sources, self.run_resources, self.site_of = documents, dict(sources or {}), run_resources, site_of
        self.body_limit = body_limit
        self.last_exception = None
        self.table = Table()
        self.metrics = HttpMetrics()
        self.limiter = ratelimit.RejectLimiter(ratelimit.resolve(cfg))  # Stage 27 (RS-04)
        self.config_hash = sec_settings.config_hash(cfg)
        self.log = Logger(clock, log_sink, hubweb.CODE_VERSION, self.config_hash[:16])
        from hub.review.search import SearchService
        self.search = SearchService(bool(self.search_cfg["enabled"]), documents)
        from hub.web import api, ui
        self.api, self.ui = api, ui

    # ------------------------------------------------------------------ lifecycle
    def _connect(self):
        con = db.open_hub(self.data_dir)  # the one sanctioned opener (TST-CO-04 d allows sqlite3.connect only in hub.store.db): guard + core migration check
        con.execute("PRAGMA busy_timeout = 30000")
        return con

    def start(self, correlation_id="web-start"):
        """Start-up self-check, BEFORE any listener exists: exposure guard (exit 9), schema M006 (and below) applied, CONFIG_LOADED audited
        with the config hash and the holder list (AC-GATE-22 / AC-SEC-21). Returns the exposure report."""
        rep = exposure.check_startup(self.s)
        con = self._connect()
        try:
            web_schema.require(con)
            audit.append(con, self.clock, anchor=self.anchor, actor="hub", actor_kind="system", action="CONFIG_LOADED", outcome="success",
                         correlation_id=correlation_id, object_ref="config",
                         details={"config_hash": self.config_hash, "command": "web-serve", "zone_h_holders": list(self.s["zone_h"]["holders"]),
                                  "anchor_every": self.s["audit"]["anchor_every"], "bind": rep["bind"]})
            from hub.control import switch  # Stage 23 DW-17 (FF-2 rule 4)
            switch.record_authority_changes(con, self.clock, self.anchor, self.cfg, correlation_id, "web-serve")
            audit.write_anchor(con, self.anchor_path)
        finally:
            con.close()
        self.log.emit("fts_engine_selected", "INFO", correlation_id, op_id="OP-REV-03", outcome="success")  # the search engine in use (fallback; FTS5 is INC-09)
        self.log.emit("startup_selfcheck", "INFO", correlation_id, op_id="OP-SYS-01", outcome="success")
        return rep

    def flush_metrics(self):
        con = self._connect()
        try:
            return self.metrics.snapshot(con, self.clock)
        finally:
            con.close()

    # ------------------------------------------------------------------ request handling
    def _cid(self, req):
        v = req.headers.get("x-correlation-id")
        return v if isinstance(v, str) and _CID.match(v) else "http-" + os.urandom(8).hex()

    @staticmethod
    def _token(req):
        auth = req.headers.get("authorization", "")
        if auth[:7].lower() == "bearer ":
            t = auth[7:].strip()
            return t if _COOKIE_TOKEN.match(t) else "invalid"
        for part in req.headers.get("cookie", "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == SESSION_COOKIE:
                return v if _COOKIE_TOKEN.match(v) else "invalid"
        return None

    def handle(self, req):
        req = transport.with_reason_header(req)  # Stage 24 DW-19 (RTD-90): X-Hub-Reason header
        cid = self._cid(req)
        t0 = parse(self.clock()).timestamp()
        info = {"op_id": "UNROUTED", "actor": None, "actor_kind": None}
        con = None
        wait = self.limiter.blocked(req.peer, t0)
        rejected = False
        try:
            if wait:
                self.metrics.auth_failure("rate_limited")
                raise RateLimited({"retry_after_seconds": wait})  # before the store is opened and without an audit row (RS-04)
            con = self._connect()
            resp = self._dispatch(con, req, cid, info)
        except HubError as e:
            resp = self._error(e, cid)
            rejected = e.code in REJECT_CODES and (e.code != "E-AUTH-FORBIDDEN" or info["op_id"] == "UNROUTED")
            if wait:
                resp.headers.append(("Retry-After", str(wait)))
            if info.get("kind") == "ui" and e.code in ("E-AUTH-UNAUTHENTICATED", "E-AUTH-SESSION-EXPIRED"):
                resp = Response(303, b"", "text/plain", [("Location", "/ui/login")])
        except sqlite3.Error as exc:  # Stage 27 S26-F-07: a store fault is its own, content-free 503 (also for /healthz), not the generic 500
            self.last_exception = exc  # diagnostic hook for tests; never serialised
            resp = self._error(StoreUnavailable() if _is_store_fault(exc) else HubError(), cid)
        except Exception as exc:  # noqa: BLE001 - fail closed: generic 500, no detail on the wire
            self.last_exception = exc  # diagnostic hook for tests; never serialised
            resp = self._error(HubError(), cid)
            resp.status = 500
        finally:
            if con is not None:
                con.close()
        if rejected:
            self.limiter.record(req.peer, t0)
        ms = (parse(self.clock()).timestamp() - t0) * 1000.0
        code = None
        if resp.status >= 400:
            try:
                code = __import__("json").loads(resp.body)["error"]["code"]
            except Exception:  # noqa: BLE001
                code = None
        self.metrics.request(info["op_id"], resp.status, ms)
        self.log.emit("http_request", "INFO" if resp.status < 400 else ("WARN" if resp.status < 500 else "ERROR"), cid, None, info["actor"],
                      info["actor_kind"], info["op_id"], "success" if resp.status < 400 else ("denied" if resp.status in (401, 403, 423) else "error"),
                      code, ms, None)
        resp.headers = [("X-Correlation-Id", cid)] + list(SECURITY_HEADERS) + transport.harden_cookies(self.s, resp.headers)  # Stage 24 DW-19 (A-INC08-3)
        return resp

    def _error(self, e, cid):
        status = getattr(e, "http", None) or (500 if e.code == "E-HUB-INTERNAL" else 422)
        return Response(status, (wire.dumps(wire.envelope(e, cid)) + "\n").encode("ascii"))

    def _deny(self, con, cid, actor, kind, reason, op, req):
        audit.append(con, self.clock, anchor=self.anchor, actor=actor, actor_kind=kind, action="AUTHZ_DENIED", outcome="denied",
                     correlation_id=cid, object_ref=op, reason=reason,
                     details={"method": req.method, "reason": reason, "path_sha256": sha256_hex(req.path)[:16]})

    @staticmethod
    def _read_body(req, route, kind):
        """Step 1 of ER-1: the request body, parsed (JSON for the API, urlencoded for the pages); None for a body-less POST of OP-SEC-02 / OP-SEC-04."""
        if req.method != "POST":
            return None
        ctype = req.headers.get("content-type", "").split(";")[0].strip().lower()
        optional = route["op_id"] in ("OP-SEC-02", "OP-SEC-04")
        if kind == "ui" and route["op_id"] != "UI-STATIC":
            body = wire.parse_form(req.body) if ctype in ("application/x-www-form-urlencoded", "") else None
            if body is None:
                raise ReqInvalid({"pointer": "", "reason": "form posts use application/x-www-form-urlencoded"})
            return body
        if ctype == "application/json":
            return wire.parse_json(req.body) if (req.body or not optional) else None
        if req.body or not optional:
            raise ReqInvalid({"pointer": "", "reason": "Content-Type must be application/json"})
        return None

    def _session(self, con, cid, req, route, token):
        """Step 2 of ER-1: the authenticated session, or None for a public route / the Zone H choke point without a usable token (the choke point then
        refuses with 401 itself, Stage 27 S26-F-01)."""
        if "public" in route["roles"]:
            return None
        choke = route["op_id"] in CHOKE_OPS
        if not token or token == "invalid":
            self.metrics.auth_failure("unauthenticated")
            if not choke:
                self._deny(con, cid, "anonymous", "system", "unauthenticated", route["op_id"], req)
                raise AuthUnauthenticated()
            return None
        try:
            return CompositeAuthenticator(LocalAuthenticator(con, self.s, self.clock, self.anchor), con, self.clock).authenticate(token, cid, touch=False)
        except AuthSessionExpired:
            self.metrics.auth_failure("session_expired")
            raise
        except AuthUnauthenticated:
            self.metrics.auth_failure("unauthenticated")
            if not choke:
                self._deny(con, cid, "anonymous", "system", "unauthenticated", route["op_id"], req)
                raise
            return None

    def _dispatch(self, con, req, cid, info):
        if len(req.body) > self.body_limit:
            raise ReqTooLarge({"limit_bytes": self.body_limit})
        route, kind, params = self.table.match(req.method, req.path)
        if route is None:
            self.metrics.auth_failure("unknown_route")
            self._deny(con, cid, "anonymous", "system", "route_not_registered", "route", req)
            raise AuthForbidden({"reason": "route not registered (deny by default)"})
        info["op_id"], info["kind"] = route["op_id"], kind
        body = self._read_body(req, route, kind)
        token = self._token(req)
        public = "public" in route["roles"]
        sess = self._session(con, cid, req, route, token)
        if sess is not None:
            info["actor"], info["actor_kind"] = sess.principal.principal_id, sess.principal.actor_kind
            if req.method not in ("GET", "HEAD"):
                self._csrf(con, cid, req, route, kind, sess, body)
        authn = CompositeAuthenticator(LocalAuthenticator(con, self.s, self.clock, self.anchor), con, self.clock)
        authz = WebAuthorizer(con, self.s, self.clock, authn, self.anchor, registry=self.table.api + self.table.ui)
        if not public and (sess is not None or route["op_id"] not in CHOKE_OPS):
            try:
                sess = authz.authorize(route["method"], route["path"], token, cid)
            except AuthForbidden:
                self.metrics.auth_failure("forbidden")
                raise
            except HubError as e:
                if e.code.startswith("E-GATE-"):
                    self.metrics.auth_failure("zone_h_denied")
                raise
        ctx = Ctx(self, con, req, route, params, sess, cid, token, body)
        handler = getattr(self.api if kind == "api" else self.ui, "op_" + route["op_id"].replace("-", "_"))
        out = handler(ctx)
        if isinstance(out, Response):
            out.headers += ctx.extra_headers
            return out
        status, doc = out
        return Response(status, (wire.dumps(doc) + "\n").encode("ascii"), headers=ctx.extra_headers)

    def _csrf(self, con, cid, req, route, kind, sess, body):
        if kind == "ui":
            ok = csrf.form_ok(sess, (body or {}).get("csrf_token"))
        else:
            ok = csrf.header_ok(req.headers)
        if not ok:
            self.metrics.auth_failure("csrf")
            p = sess.principal
            audit.append(con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind, action="CSRF_REFUSED",
                         outcome="denied", correlation_id=cid, object_ref=route["op_id"], reason="csrf",
                         details={"method": req.method, "reason": "missing_or_invalid_csrf"})
            raise Csrf({"reason": "missing or invalid " + ("csrf_token" if kind == "ui" else "X-Hub-Request header")})
