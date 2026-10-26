"""Runtime egress guard (ADR-002 option B(2), BEH-CO-07, AC-CO-12, ADR-015 loopback only).

`install()` patches socket connect/connect_ex/sendto and getaddrinfo. Loopback (127.0.0.0/8, ::1, the name
'localhost') and AF_UNIX are allowed - the legacy gateway runs on loopback. Anything else is recorded,
counted in `egress_attempts_total` and refused with E-CO-EGRESS-ATTEMPT BEFORE any packet is sent (hostnames
are not resolved, because resolution itself would be egress). `python -m hub` installs it at start-up.
"""
import contextlib
import ipaddress
import socket
import threading

from hub.core.errors import EgressAttempt
from hub.obs import metrics

_lock = threading.Lock()
_state = {"installed": False, "attempts": []}
_orig = {}
# Stage 44 (OD-40): the ONE narrow exception. hub/adapters/azure_openai.py wraps its single request in `permit(<validated Azure OpenAI host>)`; while the scope is open the
# guard lets that host be resolved and the addresses it resolved to be connected to - nothing else. Everything else stays refused.
_permit = {"hosts": {}, "ips": {}}


def _host_is_loopback(host):
    if host is None:
        return True
    if isinstance(host, bytes):
        host = host.decode("ascii", "replace")
    host = str(host).split("%", 1)[0].strip("[]")
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _permitted_host(host):
    return isinstance(host, str) and _permit["hosts"].get(host.lower(), 0) > 0


def _permitted_ip(host):
    return isinstance(host, str) and _permit["ips"].get(host, 0) > 0


def _check(family, address, op):
    if family == getattr(socket, "AF_UNIX", object()):
        return
    host = address[0] if isinstance(address, tuple) and address else address
    if _host_is_loopback(host):
        return
    with _lock:
        if _permitted_ip(host) or _permitted_host(host):
            return
    rec = {"op": op, "host": str(host), "port": address[1] if isinstance(address, tuple) and len(address) > 1 else None}
    with _lock:
        _state["attempts"].append(rec)
    metrics.inc("egress_attempts_total")
    raise EgressAttempt(rec)


def _connect(self, address):
    _check(self.family, address, "connect")
    return _orig["connect"](self, address)


def _connect_ex(self, address):
    _check(self.family, address, "connect_ex")
    return _orig["connect_ex"](self, address)


def _sendto(self, *args):
    address = args[-1]
    _check(self.family, address, "sendto")
    return _orig["sendto"](self, *args)


def _getaddrinfo(host, *args, **kwargs):
    with _lock:
        permitted = _permitted_host(host)
    if permitted:
        res = _orig["getaddrinfo"](host, *args, **kwargs)
        with _lock:
            for item in res:
                ip = item[4][0]
                _permit["ips"][ip] = _permit["ips"].get(ip, 0) + 1
                _permit.setdefault("seen", []).append(ip)
        return res
    if not _host_is_loopback(host):
        rec = {"op": "getaddrinfo", "host": str(host), "port": args[0] if args else None}
        with _lock:
            _state["attempts"].append(rec)
        metrics.inc("egress_attempts_total")
        raise EgressAttempt(rec)
    return _orig["getaddrinfo"](host, *args, **kwargs)


def install():
    with _lock:
        if _state["installed"]:
            return
        _orig["connect"] = socket.socket.connect
        _orig["connect_ex"] = socket.socket.connect_ex
        _orig["sendto"] = socket.socket.sendto
        _orig["getaddrinfo"] = socket.getaddrinfo
        socket.socket.connect = _connect
        socket.socket.connect_ex = _connect_ex
        socket.socket.sendto = _sendto
        socket.getaddrinfo = _getaddrinfo
        _state["installed"] = True


def uninstall():
    with _lock:
        if not _state["installed"]:
            return
        socket.socket.connect = _orig["connect"]
        socket.socket.connect_ex = _orig["connect_ex"]
        socket.socket.sendto = _orig["sendto"]
        socket.getaddrinfo = _orig["getaddrinfo"]
        _state["installed"] = False


@contextlib.contextmanager
def permit(host):
    """Scope in which `host` (a validated Azure OpenAI host name) may be resolved and connected to. Used only by hub/adapters/azure_openai.py."""
    if not isinstance(host, str) or not host or "/" in host or " " in host:
        raise ValueError("permit needs a bare host name")
    key = host.lower()
    with _lock:
        _permit["hosts"][key] = _permit["hosts"].get(key, 0) + 1
        mark = len(_permit.setdefault("seen", []))
    try:
        yield
    finally:
        with _lock:
            _permit["hosts"][key] -= 1
            if _permit["hosts"][key] <= 0:
                del _permit["hosts"][key]
            for ip in _permit["seen"][mark:]:
                _permit["ips"][ip] -= 1
                if _permit["ips"][ip] <= 0:
                    del _permit["ips"][ip]
            del _permit["seen"][mark:]


def installed():
    return _state["installed"]


def attempts():
    with _lock:
        return list(_state["attempts"])


def reset():
    with _lock:
        _state["attempts"] = []
