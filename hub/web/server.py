"""The loopback listener (INC-08): a stdlib ThreadingHTTPServer around hub.web.app.WebApp.

* Binds the configured address and REFUSES anything that is not loopback (this increment exposes nothing: no TLS termination, no reverse proxy
  claim; a non-loopback bind is E-SEC-EXPOSURE-NOT-APPROVED even when the INC-03 approval keys are set, Stage 24 decides any exposure).
* `server_bind` is overridden to skip socket.getfqdn() (a reverse-DNS lookup that would be a network call under the egress guard).
* A peer that is not loopback is dropped before any byte is read. Bodies are read up to the limit + 1 only; Transfer-Encoding is not supported.
* Stage 27 S26-F-06: every connection has a socket read timeout (READ_TIMEOUT_SECONDS, default 10). A client that sends a short body, a partial header
  block or nothing at all is answered 408 E-REQ-TIMEOUT (when it is still reading) or dropped, and its handler thread is released.
* One request per connection (Connection: close). No access log (the structured log of hub.obs.log is the one record); no Server banner detail.
"""
import socket
import socketserver
import sys
import urllib.parse as _up
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from hub.security import exposure
from hub.security.errors import ExposureNotApproved
from hub.web import wire
from hub.web.app import Request, Response, SECURITY_HEADERS
from hub.web.errors import ReqInvalid, ReqTimeout

DEFAULT_PORT = 8081
READ_TIMEOUT_SECONDS = 10


class LoopbackServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def server_bind(self):
        socketserver.TCPServer.server_bind(self)  # not HTTPServer.server_bind: no getfqdn
        host, port = self.server_address[:2]
        self.server_name, self.server_port = host, port

    def verify_request(self, request, client_address):
        return exposure.is_loopback(client_address[0])

    def handle_error(self, request, client_address):
        """A socket error of one client (timeout, reset) is that client's problem: no traceback on stderr. Any other exception keeps the default report."""
        if issubclass(sys.exc_info()[0] or Exception, OSError):
            return
        socketserver.TCPServer.handle_error(self, request, client_address)


def make_handler(app, read_timeout=READ_TIMEOUT_SECONDS):
    class Handler(BaseHTTPRequestHandler):
        timeout = read_timeout  # StreamRequestHandler.setup() applies it to the connection socket
        protocol_version = "HTTP/1.1"
        server_version = "GxPHub"
        sys_version = ""

        def log_message(self, *a):
            pass

        def _serve(self):
            sp = _up.urlsplit(self.path)
            q = {}
            for k, v in _up.parse_qsl(sp.query, keep_blank_values=True, max_num_fields=50):
                q.setdefault(k, v)
            headers = dict((k.lower(), v) for k, v in self.headers.items())
            if "transfer-encoding" in headers:
                resp = Response(400, (wire.dumps(wire.envelope(ReqInvalid({"reason": "Transfer-Encoding is not supported"}), "http-te")) + "\n").encode())
                resp.headers = list(SECURITY_HEADERS)
            else:
                try:
                    n = int(headers.get("content-length", "0") or 0)
                except ValueError:
                    n = -1
                if n < 0:
                    resp = Response(400, (wire.dumps(wire.envelope(ReqInvalid({"reason": "bad Content-Length"}), "http-cl")) + "\n").encode())
                    resp.headers = list(SECURITY_HEADERS)
                else:
                    try:
                        body = self.rfile.read(min(n, app.body_limit + 1)) if n else b""
                    except (socket.timeout, OSError):  # the declared body did not arrive in time (S26-F-06)
                        body = None
                    if body is None:
                        resp = Response(408, (wire.dumps(wire.envelope(ReqTimeout({"reason": "request body not received in time"}), "http-timeout")) + "\n").encode())
                        resp.headers = list(SECURITY_HEADERS)
                    else:
                        resp = app.handle(Request(self.command, sp.path, q, headers, body, self.client_address[0]))
            self.send_response(resp.status)
            self.send_header("Content-Type", resp.content_type)
            self.send_header("Content-Length", str(len(resp.body)))
            self.send_header("Connection", "close")
            for k, v in resp.headers:
                self.send_header(k, v)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(resp.body)
            self.close_connection = True

        do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_HEAD = do_OPTIONS = _serve

    return Handler


def bind_address(s):
    host = s["network"]["bind"]
    if not exposure.is_loopback(host):
        raise ExposureNotApproved({"bind": host, "reason": "INC-08 serves loopback only; any other exposure is a Stage 24 decision"})
    return host


def make_server(app, port=DEFAULT_PORT, read_timeout=READ_TIMEOUT_SECONDS):
    """Start-up self-check first (exposure, schema, CONFIG_LOADED audit), then bind. Port 0 = an ephemeral port (tests)."""
    host = bind_address(app.s)
    app.start()
    return LoopbackServer((host, port), make_handler(app, read_timeout))
