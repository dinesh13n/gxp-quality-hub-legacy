"""Transport hardening decided as options in Stage 24 (DW-19; A-INC08-3, RTD-90 / A-INC09-5). Synthetic, unvalidated. Pure functions, no I/O.

* Session cookie `Secure` flag (A-INC08-3): the cookie keeps HttpOnly; SameSite=Strict; Path=/ and gains `Secure` exactly when TLS settings
  (network.tls.cert_file AND key_file) are configured - i.e. when the operator has declared a TLS deployment. On the default loopback install nothing
  changes (no TLS settings, no `Secure`). No new configuration key is needed. The hub itself still serves loopback HTTP only (hub.web.server); a TLS
  terminating proxy is the Stage 27 / HAR-05 question, so this is the cookie half of that decision and nothing more (Assumption A-S24-TLS-1).
* C3 reason transport (RTD-90): `reason` for a restricted read is accepted from the request header `X-Hub-Reason` as well as from the query parameter
  `?reason=` (which stays accepted: removing it would change the shipped contract; whether to retire it is open decision DQ-S24-04). The header wins
  when both are present. A header is not written to URLs, browser history or the usual proxy access logs. Header values are ISO-8859-1 text on the
  wire; the hub treats the value as text exactly like the query value (length-bounded to 500 characters by hub.r2.protection.require_reason).
"""
REASON_HEADER = "x-hub-reason"
COOKIE_NAME = "hub_session"


def cookie_secure(settings):
    """True when the resolved security settings declare a TLS deployment (cert and key both set)."""
    tls = (settings.get("network") or {}).get("tls") or {}
    return bool(tls.get("cert_file")) and bool(tls.get("key_file"))


def harden_cookies(settings, headers):
    """Return `headers` (a list of (name, value)) with `; Secure` appended to every Set-Cookie that lacks it, when cookie_secure(settings)."""
    if not cookie_secure(settings):
        return list(headers)
    out = []
    for k, v in headers:
        if k.lower() == "set-cookie" and "; secure" not in v.lower():
            v = v + "; Secure"
        out.append((k, v))
    return out


def with_reason_header(req):
    """Copy a header-carried reason into req.query['reason'] (the header wins); a request without the header is returned unchanged."""
    value = req.headers.get(REASON_HEADER)
    if isinstance(value, str) and value.strip():
        req.query["reason"] = value
    return req
