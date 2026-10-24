"""Register of the security control VALUES (Stage 24, DW-19; RTD-26, DQ-09). Synthetic, unvalidated.

Each entry names a shipped value, where it lives, its floor (if any), the evidence behind it and the decision that is still open. NOTHING here is an
approval: `status` is PROPOSED for every value, because no human decision on DQ-09 has been recorded (OD-30 / OD-31 left it open). `drift()` compares the
register with the shipped defaults of hub.security.settings, so a changed default fails tests/hub/test_tst_hub_stg24_controls.py until the register (and
docs/24-security-privacy/security-control-matrix.md) says why. `python -m hub.security controls` prints the register.
"""
from hub.security import settings

PROPOSED = "PROPOSED - not approved; accepted open until the Engagement lead decides (DQ-09)"
OWNER = "Engagement lead (Dinesh Naik)"

# id, config path (None = not a config value), shipped value, floor, evidence, decision still open
CONTROLS = (
    ("SC-01", "auth.pbkdf2_iterations", 600000, 600000, "PBKDF2-HMAC-SHA256, 16-byte salt (hub/security/auth.py); public password-storage guidance names 600,000 for this KDF [Assumption: recalled guidance, re-check at adoption]",
     "keep 600,000 or raise; a KDF other than PBKDF2 (scrypt / Argon2) is not in the Python 3.10 stdlib guarantee (hashlib.scrypt depends on OpenSSL)"),
    ("SC-02", "auth.password_min_length", 12, 12, "hub/security/auth.py create_user; no composition rules, no expiry",
     "keep 12, or move toward 15 (current NIST SP 800-63B-4 guidance for a password used as the only authenticator [Assumption: recalled, re-check]); no MFA exists"),
    ("SC-03", "auth.lockout_threshold", 5, None, "TST-SEC-05; lockout is per principal (RTD-34)", "5 failures; per-source limiting needs a source identity that loopback does not have"),
    ("SC-04", "auth.lockout_window_seconds", 900, None, "TST-SEC-05", "15 minutes counting window"),
    ("SC-05", "auth.lockout_duration_seconds", 900, None, "TST-SEC-05", "15 minutes lock; a permanent lock needs an unlock procedure that does not exist"),
    ("SC-06", "auth.session_idle_seconds", 1800, None, "hub/security/auth.py authenticate", "30 minutes idle timeout"),
    ("SC-07", "auth.session_absolute_seconds", 28800, None, "hub/security/auth.py authenticate", "8 hours absolute lifetime"),
    ("SC-08", "zone_h.reauth_window_seconds", 300, None, "hub/gate/reauth.py; TST-GATE", "5 minutes step-up window for Zone H"),
    ("SC-09", "zone_h.holders", [], None, "hub/security/settings.py DEFAULTS; OD-17, OD-31", "WHO the holders are: Dinesh only (OD-31 left them empty)"),
    ("SC-10", "audit.anchor_every", 100, None, "hub/security/audit.py", "anchor every 100 audit records and at the end of every run; anchor path required, outside the database directory"),
    ("SC-11", "network.bind", "127.0.0.1", None, "hub/security/exposure.py; hub/web/server.py bind_address", "loopback only; any exposure is HAR-05 plus an unbuilt TLS story (RTD-77)"),
    ("SC-12", "network.exposure_approved", False, None, "hub/security/exposure.py", "refused without approval reference and TLS keys; the server refuses non-loopback even with them (S23)"),
)
# Choices that are code, not configuration: asserted by tests, listed so the matrix can cite them.
FIXED = (
    ("SC-20", "session cookie attributes", "HttpOnly; SameSite=Strict; Path=/; Secure only when TLS settings are present (hub/security/transport.py)", "A-INC08-3"),
    ("SC-21", "CSRF", "X-Hub-Request: 1 on JSON writes; derived csrf_token on form posts; none on the login POST", "A-INC08-5"),
    ("SC-22", "service token", "svc_ + 48 hex (os.urandom(24)); sha256 stored; optional expiry; rotation = issue + revoke", "A-INC08-1"),
    ("SC-23", "reauth_token", "sha256 of 'reauth:' + session digest + ':' + reauth_at", "A-INC08-2"),
    ("SC-24", "login response body", "returns token and csrf_token besides the cookie", "A-INC08-4"),
    ("SC-25", "C3 reason transport", "X-Hub-Reason header or ?reason= (header wins)", "RTD-90 / A-INC09-5"),
    ("SC-26", "request body limit", "1 MiB; Transfer-Encoding refused", "hub/web/app.py BODY_LIMIT"),
)


def _get(tree, path):
    cur = tree
    for part in path.split("."):
        cur = cur[part]
    return cur


def entries():
    return [{"id": i, "path": p, "shipped": v, "floor": f, "evidence": e, "open_decision": d, "status": PROPOSED, "owner": OWNER}
            for (i, p, v, f, e, d) in CONTROLS]


def drift():
    """[(id, path, register value, settings default)] where the register disagrees with hub.security.settings.DEFAULTS; also floors that moved."""
    out = []
    for (i, p, v, f, _e, _d) in CONTROLS:
        d = _get(settings.DEFAULTS, p)
        if d != v:
            out.append((i, p, v, d))
        if f is not None and settings.FLOORS.get(p.split(".")[-1]) != f:
            out.append((i, p + " (floor)", f, settings.FLOORS.get(p.split(".")[-1])))
    return out


def report():
    return {"label": "synthetic, unvalidated", "status": PROPOSED, "controls": entries(),
            "fixed": [{"id": i, "name": n, "value": v, "assumption": a} for (i, n, v, a) in FIXED], "drift": drift()}
