"""Shared helpers for the Stage 15 INC-08 hub tests (loopback HTTP surface, reviewer queue, disposition gate; M006). Synthetic, unvalidated.

Everything lives under HUB_SANDBOX_ROOT (S.tmpdir) - never inside the repository working tree (OD-03a). The store is the INC-07 template (M001..M005, 6
users, the 125 backfilled legacy cases) with M006 applied once per process; each test gets a private byte copy. The Zone H holders (holder-1, holder-2) are
SYNTHETIC TEST DATA: the shipped config keeps zone_h.holders EMPTY. The web app is exercised in-process (`Client` calls WebApp.handle, the same code the
socket server calls); a few tests also go through the real loopback listener with the raw-socket client of _http8.py.

INC-08 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER, frozen group C keeps its size) and are run under the egress
guard by test_inc08_egress_guard.py instead (inc08-design-notes D-12, same split as INC-05 .. INC-07). They do NOT skip on HUB_EGRESS_INNER5/6/7: the frozen
INC-05..07 inner runs select tests by name and none of the INC-08 tests is selected there (the I8_ naming keeps the selectors disjoint).
"""
import json
import os
import shutil
import sqlite3
import unittest
import urllib.parse as up

import _support as S
import _inc05 as D
import _inc07 as R
from hub.gate import reauth
from hub.gate.actions import ZoneHActions
from hub.gate.dispositions import DispositionService
from hub.intake.service import IntakeService
from hub.metrics.service import MetricsService
from hub.review.service import ReviewService
from hub.runs.service import RunService
from hub.security.canonical import fmt
from hub.web import schema as wschema
from hub.web.app import Request, WebApp

LABEL = "synthetic, unvalidated"
AUTH = "TEST-AUTH-08 (synthetic)"
_TPL8 = {}
CSRF = {"X-Hub-Request": "1"}


def skip_in_inner_egress_run():
    """Call from setUpModule: INC-08 modules are exercised under the egress guard by test_inc08_egress_guard.py."""
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("INC-08 module: covered by test_inc08_egress_guard.py (design note D-12)")
    S.require_sandbox()


def _template8(loaded):
    if loaded in _TPL8:
        return _TPL8[loaded]
    t7 = R._template7(loaded)
    dst = S.tmpdir("p8tpl-")
    shutil.copytree(t7["base"], dst, dirs_exist_ok=True)
    ds = D.DStore(_base=dst, _tpl=t7)
    ds.close()
    res = wschema.apply(ds.data, os.path.join(dst, "backups-m006"), ds.anchor_path, ds.clock)
    assert res["applied"], res
    _TPL8[loaded] = {"base": dst, "tokens": t7["tokens"], "pw": t7["pw"], "clock": fmt(ds.clock._t)}
    return _TPL8[loaded]


class Resp(object):
    def __init__(self, r):
        self.status, self.raw, self.content_type = r.status, r.body, r.content_type
        self.headers = dict((k.lower(), v) for k, v in r.headers)
        self.set_cookie = [v for k, v in r.headers if k.lower() == "set-cookie"]

    @property
    def text(self):
        return self.raw.decode("utf-8", "replace")

    def json(self):
        return json.loads(self.raw.decode("utf-8"))

    @property
    def code(self):
        try:
            return self.json()["error"]["code"]
        except (ValueError, KeyError, TypeError):
            return None


class WStore(D.DStore):
    """A private M001..M006 hub store plus an in-process web app. loaded=True (default) holds the 125 backfilled legacy cases."""

    def __init__(self, loaded=True, extra=None, app_kw=None):
        D.DStore.__init__(self, loaded, extra, _tpl=_template8(loaded))
        self.isvc = IntakeService(self.con, self.s, self.clock, self.anchor)
        self.runs = RunService(self.con, self.s, self.clock, self.anchor, self.cfg)
        self.met = MetricsService(self.con, self.s, self.clock, self.anchor, self.cfg)
        self.rev = ReviewService(self.con, self.s, self.clock, self.anchor)
        self.disp = DispositionService(self.con, self.s, self.clock, self.anchor, self.d)
        self.app_kw = dict(app_kw or {})
        self._app = None

    @property
    def app(self):
        if self._app is None:
            self._app = WebApp(self.data, self.cfg, self.clock, **self.app_kw)
        return self._app

    def fresh(self, name):
        tok = self.authn.login(name, self.pw, "t-fresh-login")
        return self.authn.authenticate(tok, "t-fresh")

    def call(self, method, path, body=None, token=None, headers=None, ctype="application/json", raw=None, cookie=None, csrf=True):
        """One in-process request. body: dict (JSON-encoded) or str/bytes via `raw`. csrf=True adds the X-Hub-Request header on writes."""
        sp = up.urlsplit(path)
        q = dict(up.parse_qsl(sp.query, keep_blank_values=True))
        h = {}
        if token:
            h["Authorization"] = "Bearer " + token
        if cookie:
            h["Cookie"] = "hub_session=" + cookie
        if csrf and method != "GET":
            h.update(CSRF)
        h.update(headers or {})
        data = raw if raw is not None else (json.dumps(body).encode("utf-8") if body is not None else b"")
        if isinstance(data, str):
            data = data.encode("utf-8")
        if data and ctype:
            h["Content-Type"] = ctype
        resp = Resp(self.app.handle(Request(method, sp.path, q, h, data)))
        if resp.status == 500 and self.app.last_exception is not None:  # an unexpected exception is a test failure, with its traceback
            import traceback
            e = self.app.last_exception
            self.app.last_exception = None
            raise AssertionError("HTTP 500 for %s %s\n%s" % (method, path, "".join(traceback.format_exception(type(e), e, e.__traceback__))))
        return resp

    def get(self, path, name=None, **kw):
        return self.call("GET", path, token=self.tokens[name] if name else None, **kw)

    def post(self, path, body, name=None, **kw):
        return self.call("POST", path, body, token=self.tokens[name] if name else None, **kw)

    def reauth_token(self, name):
        """OP-SEC-05 over the app for a template session: the proof ZoneHRequest.reauth_token carries."""
        r = self.post("/api/v2/auth/reauth", {"password": self.pw}, name)
        assert r.status == 201, r.text
        return r.json()["reauth_token"]

    def zh(self, name, action, payload=None, case_id=None, pack_hash=None, authority_ref=AUTH, token=None, reauth_token=True):
        body = {"action": action, "authority_ref": authority_ref}
        if payload is not None:
            body["payload"] = payload
        if case_id is not None:
            body["case_id"] = case_id
        if pack_hash is not None:
            body["pack_hash"] = pack_hash
        if reauth_token is True:
            body["reauth_token"] = self.reauth_token(name)
        elif reauth_token:
            body["reauth_token"] = reauth_token
        return self.post("/api/v2/zone-h/actions", body, name) if token is None else self.call("POST", "/api/v2/zone-h/actions", body, token=token)

    def pack(self, name, case_id):
        return self.get("/api/v2/cases/%s/evidence-pack" % case_id, name)

    def set_mode(self, mode, values=("accept", "reject", "hold"), who="holder-1"):
        """ZH-08 through the service choke point (synthetic holder), so the mode is a stored, audited event."""
        sess = self.reauth(who)
        return ZoneHActions(self.con, self.s, self.clock, self.anchor, self.d, None, self.cfg).execute(
            sess, {"action": "ZH-08", "authority_ref": AUTH, "reauth_token": reauth.token_for(sess),
                   "payload": {"mode": mode, "values": list(values)}}, "t-mode")

    def counts(self):
        return dict((t, self.count(t)) for t in ("decision_events", "case_state", "evidence_record", "policy_events", "flag_action", "rule_trace",
                                                  "crosswalk_link", "raw_intake", "run_event", "metric_value"))

    def count(self, table, where="1=1", args=()):
        return self.con.execute("SELECT count(*) FROM %s WHERE %s" % (table, where), args).fetchone()[0]

    def new_case(self, cid="C90000001"):
        self.mk(cid)
        return cid

    def load_rules(self):
        """The three as-found rule sets (read-only, inactive) from the hash-gated sandbox copy of the legacy data."""
        self.pol.load_as_found(S.LEGACY_ROOT, S.tmpdir("p8rs-"), "t-rs")

    def add_trace(self, case_id, function="PRIORITY", inputs=None, ruleset_ref="as-found-python@1"):
        """Store one rule evaluation for a case (the reviewer-support trace). Returns {trace_id, flag_id}."""
        inputs = inputs or {"status": "CLOSED", "severity": "LOW", "amount": 1}
        res = self.pol.evaluate(function, inputs, ruleset_ref)
        return self.rev.record_trace("rules-engine", "system", case_id, function, ruleset_ref, inputs, res, "t-trace")

    def zh_counts(self):
        """Zone H write footprint: decision events, policy events, flag actions."""
        return (self.count("decision_events"), self.count("policy_events"), self.count("flag_action"))

    def login_cookie(self, name):
        r = self.call("POST", "/api/v2/auth/login", {"username": name, "password": self.pw}, csrf=False)
        assert r.status == 201, r.text
        return r.json()["token"]

    def close(self):
        D.DStore.close(self)


_SHIPPED = {}


def shipped_store():
    """A WStore holding the whole shipped partner feed (8,567 deliveries, FX-BASE125 sandbox copy) ingested once per process; READ-ONLY for tests."""
    if "st" not in _SHIPPED:
        import _inc06 as I
        st = WStore()
        by, _ = I.legacy_deliveries()
        st.isvc.ingest("partner_feed", by["partner_feed"], "full-web", "t-full-web")
        _SHIPPED["st"] = st
    return _SHIPPED["st"]


def close_shipped():
    st = _SHIPPED.pop("st", None)
    if st is not None:
        st.close()


def corpus_provider():
    """The shipped 1,200-document JSONL (sandbox copy) as the injected search document provider; None when the copy has no document file."""
    path = os.path.join(S.LEGACY_ROOT, "data", "documents", "source_documents.jsonl")
    if not os.path.isfile(path):
        return None
    import hashlib
    docs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                d["hash"] = hashlib.sha256(d["body"].encode("utf-8")).hexdigest()
                docs.append(d)

    def provider():
        return docs
    return provider
