"""AD-04 gateway client (INC-06, BEH-INT-11, AC-INT-25/26): HTTP GET only, loopback only, bounded retries, 5 s timeout.

* The URL must be http or https and its host loopback (127.0.0.0/8, ::1, localhost); `file:`, `ftp:` and any other scheme or host is refused
  with E-INT-URL-SCHEME-REFUSED BEFORE any connection (no read). No proxy is used and redirects are refused.
* An unreachable source (connection error, timeout, HTTP 5xx / 429, unusable response) is retried up to `retries` times with exponential
  back-off, then E-INT-SOURCE-UNREACHABLE is raised: a run error, never a data outcome (no item is fabricated).
* Offsets are the hub's (intake_run_event checkpoints); the legacy gateway_checkpoints table is never touched.
This module is under adapters/ because it is the only place allowed to import an HTTP client (ADR-002 R2).
"""
import ipaddress
import json
import threading
import urllib.error
import urllib.parse
import urllib.request


MAX_BYTES = 5 * 1024 * 1024


def check_url(url):
    from hub.intake.errors import UrlSchemeRefused  # function-level since Stage 27: breaks the adapters -> intake edge of two package cycles (OD-27 debt)
    if not isinstance(url, str):
        raise UrlSchemeRefused({"reason": "not a string"})
    u = urllib.parse.urlsplit(url.strip())
    if u.scheme not in ("http", "https"):
        raise UrlSchemeRefused({"scheme": u.scheme[:10], "reason": "only http(s)"})
    host = (u.hostname or "").strip("[]")
    ok = host.lower() == "localhost"
    if not ok:
        try:
            ok = ipaddress.ip_address(host).is_loopback
        except ValueError:
            ok = False
    if not ok:
        raise UrlSchemeRefused({"host": host[:60], "reason": "loopback only (ADR-015)"})
    return u


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **kw):
        return None


def _sleep(seconds):
    threading.Event().wait(seconds)      # no `time` import in adapters (TST-CO-13 b)


def _open(url, timeout):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect)
    return opener.open(url, timeout=timeout)


def fetch_events(url, offset=0, limit=50, retries=3, timeout=5, sleep=_sleep, backoff=0.5, opener=_open):
    """GET <url>/api/events?offset&limit -> {"items": [...], "next_offset": int, "attempts": n}."""
    u = check_url(url)
    full = "%s://%s%s/api/events?offset=%d&limit=%d" % (u.scheme, u.netloc, u.path.rstrip("/"), int(offset), int(limit))
    attempts, last = 0, None
    for i in range(int(retries) + 1):
        attempts += 1
        try:
            with opener(full, timeout) as resp:
                body = resp.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise ValueError("response too large")
            doc = json.loads(body.decode("utf-8"))
            if not isinstance(doc, dict) or not isinstance(doc.get("items"), list) or not isinstance(doc.get("next_offset"), int):
                raise ValueError("unexpected response shape")
            return {"items": doc["items"], "next_offset": doc["next_offset"], "attempts": attempts}
        except urllib.error.HTTPError as e:
            last = "http_%d" % e.code
            if e.code < 500 and e.code != 429:
                break  # client errors are not retried
        except (urllib.error.URLError, OSError, ValueError) as e:
            last = e.__class__.__name__
        if i < int(retries):
            sleep(backoff * (2 ** i))
    from hub.intake.errors import SourceUnreachable  # function-level (cycle debt, Stage 27)
    raise SourceUnreachable({"attempts": attempts, "last_error": last, "retries": int(retries)})
