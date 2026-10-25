"""Raw-socket HTTP/1.1 test client for the INC-08 loopback listener (INC-08 tests; stdlib `socket` only).

http.client / urllib.request are deliberately NOT used: the No-AI R2 rule (hub.guards.no_ai) forbids them outside hub/adapters, and the rule also scans
tests/hub. The client only ever connects to 127.0.0.1 (the egress guard allows loopback; the documented exception for the INC-08 test sockets is exactly
this: loopback, nothing else - see inc08-design-notes D-12).
"""
import json
import socket
import threading

from hub.web import server


class Served(object):
    """Start a WebApp on 127.0.0.1 with an ephemeral port; use as a context manager."""

    def __init__(self, app, read_timeout=None):
        self.app = app
        self.read_timeout = read_timeout  # Stage 27 (S26-F-06): None = the listener default (hub.web.server.READ_TIMEOUT_SECONDS)
        self.srv = None

    def __enter__(self):
        self.srv = server.make_server(self.app, 0) if self.read_timeout is None else server.make_server(self.app, 0, self.read_timeout)
        self.port = self.srv.server_address[1]
        self.host = self.srv.server_address[0]
        self.thread = threading.Thread(target=self.srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()
        self.thread.join(5)

    def request(self, method, path, body=None, headers=None, raw_body=None, extra_lines=()):
        h = {"Host": "127.0.0.1:%d" % self.port}
        h.update(headers or {})
        data = raw_body if raw_body is not None else (json.dumps(body).encode("utf-8") if body is not None else b"")
        if data and "Content-Type" not in h:
            h["Content-Type"] = "application/json"
        if data or method in ("POST", "PUT", "PATCH"):
            h["Content-Length"] = str(len(data))
        head = ("%s %s HTTP/1.1\r\n" % (method, path)) + "".join("%s: %s\r\n" % kv for kv in h.items()) + "".join(l + "\r\n" for l in extra_lines) + "\r\n"
        return raw(self.host, self.port, head.encode("latin-1") + data)


class Raw(object):
    def __init__(self, status, headers, body):
        self.status, self.headers, self.body = status, headers, body

    def json(self):
        return json.loads(self.body.decode("utf-8"))


def raw(host, port, payload, timeout=10):
    s = socket.create_connection((host, port), timeout=timeout)
    try:
        s.sendall(payload)
        buf = b""
        while True:
            try:
                chunk = s.recv(65536)
            except socket.timeout:
                break
            if not chunk:
                break
            buf += chunk
    finally:
        s.close()
    head, _, body = buf.partition(b"\r\n\r\n")
    lines = head.decode("latin-1").split("\r\n")
    status = int(lines[0].split(" ")[1])
    hdrs = {}
    for l in lines[1:]:
        k, _, v = l.partition(":")
        hdrs.setdefault(k.strip().lower(), v.strip())
    return Raw(status, hdrs, body)
