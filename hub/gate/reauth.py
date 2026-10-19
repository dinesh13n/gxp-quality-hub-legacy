"""Step-up re-authentication proof for OP-GATE-02 (OP-SEC-05 returns it; ZoneHRequest.reauth_token requires it; INC-08).

reauth_token = sha256("reauth:" || token_sha256 || ":" || reauth_at) of the SESSION that re-authenticated: it is derived, nothing is stored, and it
changes with every successful re-authentication, so an old or foreign token never matches. It is NOT a bearer credential on its own (the session
cookie / token is still required) and it does not extend the window: the window check (zone_h.reauth_window_seconds) stays in GateService.
Assumption A-INC08-2: no wire format for reauth_token exists in the Stage 12 spec beyond 'short-lived string from OP-SEC-05' (Stage 24 to confirm).
"""
import hmac

from hub.security.canonical import sha256_hex


def token_for(sess):
    return sha256_hex("reauth:%s:%s" % (sess.token_sha256, sess.reauth_at))


def matches(sess, presented):
    return isinstance(presented, str) and hmac.compare_digest(token_for(sess), presented)
