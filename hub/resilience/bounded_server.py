"""BoundedLoopbackServer (Stage 28): hub.web.server.LoopbackServer with a hard cap on concurrent connections (bulkhead for the listener).

The shipped ThreadingHTTPServer starts one thread per connection with no cap (Stage 28 finding F-CAP-01); the 10 s read timeout bounds how long a
silent client holds a thread, not how many threads exist. Here the (max_connections + 1)-th simultaneous connection is answered at once with the existing
429 E-REQ-RATE-LIMITED envelope (Retry-After 1) and closed, without starting a thread, opening the store or writing an audit row. Not wired into
`hub.web serve` (open item D-28-02); make_bounded_server mirrors hub.web.server.make_server.
"""
from hub.resilience import policy
from hub.web import server, wire
from hub.web.errors import RateLimited

DEFAULT_MAX_CONNECTIONS = 64


def _shed_bytes():
    body = (wire.dumps(wire.envelope(RateLimited({"reason": "connection limit"}), "http-shed")) + "\n").encode()
    head = ("HTTP/1.1 429 Too Many Requests\r\nContent-Type: application/json\r\nContent-Length: %d\r\nRetry-After: 1\r\nConnection: close\r\n\r\n" % len(body))
    return head.encode("latin-1") + body


class BoundedLoopbackServer(server.LoopbackServer):
    def __init__(self, addr, handler, max_connections=DEFAULT_MAX_CONNECTIONS):
        self.bulkhead = policy.Bulkhead(max_connections)
        self._shed = _shed_bytes()
        server.LoopbackServer.__init__(self, addr, handler)

    def process_request(self, request, client_address):
        if not self.bulkhead.try_enter():
            try:
                request.settimeout(1)
                request.sendall(self._shed)
            except OSError:
                pass
            self.shutdown_request(request)
            return
        server.LoopbackServer.process_request(self, request, client_address)

    def process_request_thread(self, request, client_address):
        try:
            server.LoopbackServer.process_request_thread(self, request, client_address)
        finally:
            self.bulkhead.leave()


def make_bounded_server(app, port=server.DEFAULT_PORT, read_timeout=server.READ_TIMEOUT_SECONDS, max_connections=DEFAULT_MAX_CONNECTIONS):
    host = server.bind_address(app.s)
    app.start()
    return BoundedLoopbackServer((host, port), server.make_handler(app, read_timeout), max_connections)
