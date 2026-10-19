"""CSRF controls (PNFR-07, AC-SEC-17; INC-08).

* JSON writes (every authenticated POST under /api/v2) must carry the custom header `X-Hub-Request: 1`. A cross-site HTML form or a plain
  cross-origin fetch can not set a custom header without a CORS preflight, and this server answers no preflight (no CORS headers are ever sent).
* HTML form posts (/ui/...) must carry a `csrf_token` field equal to csrf_token(session): sha256("csrf:" || token_sha256). It is derived, nothing is
  stored, and it changes with every login. The session cookie is HttpOnly + SameSite=Strict as defence in depth.
* A refusal is E-SEC-CSRF 403, audited, and changes nothing.
Assumption A-INC08-5 (Stage 24): the login POST has no pre-session token (login CSRF is accepted as low risk on a loopback-only, single-organisation
tool); SameSite=Strict does not cover it.
"""
import hmac

from hub.security.canonical import sha256_hex

HEADER = "x-hub-request"
HEADER_VALUE = "1"


def csrf_token(sess):
    return sha256_hex("csrf:" + sess.token_sha256)


def header_ok(headers):
    return headers.get(HEADER) == HEADER_VALUE


def form_ok(sess, presented):
    return isinstance(presented, str) and hmac.compare_digest(csrf_token(sess), presented)
