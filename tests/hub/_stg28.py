"""Shared helpers for the Stage 28 reliability tests (DW-32 and the Stage 28 failure-injection plan). Synthetic, unvalidated.

Stage 28 test modules skip themselves inside the TST-CO-12 inner egress run (HUB_EGRESS_INNER) and run under the egress guard in
test_tst_hub_stg28_egress_guard.py (E28EGRESS), the same split as Stages 20-27. No helper imports a deny-listed module (hub.guards.no_ai rule R2):
http.server (a loopback double) is allowed, urllib.request / http.client are not used. Failures are injected into PRIVATE sandbox stores, loopback doubles and
fake clocks only - never into production, a shared service or the working tree (OD-03a).

  FakeClock          an injectable clock (breaker cooldowns without sleeping)
  Stub               a counting loopback HTTP double with a switchable plan (status, body bytes); .hits counts requests that reached it
  refused_url()      a loopback URL nothing listens on (connection refused)
  write_evidence()   JSON under HUB_SANDBOX_ROOT/s28-evidence
"""
import http.server
import json
import os
import socket
import threading
import unittest

import _support as S

LABEL = "synthetic, unvalidated"
PAGE = json.dumps({"items": [], "count": 0, "next_offset": 7}).encode()


def skip_in_inner_egress_run():
    if os.environ.get("HUB_EGRESS_INNER"):
        raise unittest.SkipTest("Stage 28 module: covered by test_tst_hub_stg28_egress_guard.py (E28EGRESS)")
    S.require_sandbox()


def write_evidence(name, doc):
    d = os.path.join(S.SANDBOX_ROOT, "s28-evidence")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    return p


class FakeClock(object):
    def __init__(self, t=1000.0):
        self.t = float(t)

    def __call__(self):
        return self.t

    def advance(self, s):
        self.t += s


def refused_url():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return "http://127.0.0.1:%d" % port


class Stub(object):
    """Loopback double: answers every request with the current plan entry (status, body); .hits counts requests."""

    def __init__(self, status=200, body=PAGE):
        self.plan, self.hits, self.paths = (status, body), 0, []
        outer = self

        class H_(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                outer.hits += 1
                outer.paths.append(self.path)
                status, body = outer.plan
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass
        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H_)
        self.url = "http://127.0.0.1:%d" % self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        self.t.start()

    def set(self, status, body=PAGE):
        self.plan = (status, body)

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.t.join(5)
