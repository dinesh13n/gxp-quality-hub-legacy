"""Security settings (INC-03) resolved from the hub config dict returned by hub.config.load().

Defaults (feature-flag-plan FF-1; OD-15 / OD-12). The numeric controls are Stage 12 PROPOSALS
(A-12-F09-1) implemented as configurable values; they need Stage 24 confirmation:
  auth.pbkdf2_iterations        600000  (floor 600000)   PBKDF2-HMAC-SHA256, 16-byte per-user salt
  auth.password_min_length      12      (floor 12)
  auth.lockout_threshold        5       failed logins ...
  auth.lockout_window_seconds   900     ... within 15 min ...
  auth.lockout_duration_seconds 900     ... lock the account for 15 min
  auth.session_idle_seconds     1800 / auth.session_absolute_seconds 28800
  zone_h.holders                []      (FR-GATE-04: ships empty; OD-S12-06 open - no holders by default)
  zone_h.reauth_window_seconds  300     step-up re-authentication window
  audit.anchor_path             REQUIRED for audit-writing commands, outside the DB directory (OD-S12-18 / OD-15)
  audit.anchor_every            100
  network.bind                  127.0.0.1; non-loopback needs exposure_approved + exposure_approval_ref + TLS
The `auth` key and `network.tls` are not in hub-config.schema.json v0.1 -> schema addendum (RTD).
"""
import copy
import os

from hub.core.errors import ConfigInvalid
from hub.security.canonical import canonical, sha256_hex

DEFAULTS = {
    "auth": {"pbkdf2_iterations": 600000, "password_min_length": 12, "lockout_threshold": 5,
             "lockout_window_seconds": 900, "lockout_duration_seconds": 900,
             "session_idle_seconds": 1800, "session_absolute_seconds": 28800},
    "zone_h": {"holders": [], "reauth_window_seconds": 300},
    "audit": {"anchor_path": None, "anchor_every": 100},
    "network": {"bind": "127.0.0.1", "exposure_approved": False, "exposure_approval_ref": None,
                "tls": {"cert_file": None, "key_file": None}},
}
FLOORS = {"pbkdf2_iterations": 600000, "password_min_length": 12}


def _merge(base, over):
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _merge(base[k], v)
        else:
            base[k] = copy.deepcopy(v)
    return base


def _int(value, name, lo, hi=None):
    if isinstance(value, bool) or not isinstance(value, int) or value < lo or (hi is not None and value > hi):
        raise ConfigInvalid({name: value, "allowed": [lo, hi]})


def resolve(cfg):
    """Return the validated security settings (a new dict) for a loaded hub config."""
    s = copy.deepcopy(DEFAULTS)
    for key in DEFAULTS:
        if key in (cfg or {}):
            if not isinstance(cfg[key], dict):
                raise ConfigInvalid({key: "must be an object"})
            _merge(s[key], cfg[key])
    a = s["auth"]
    _int(a["pbkdf2_iterations"], "auth.pbkdf2_iterations", FLOORS["pbkdf2_iterations"])
    _int(a["password_min_length"], "auth.password_min_length", FLOORS["password_min_length"], 1024)
    for k in ("lockout_threshold", "lockout_window_seconds", "lockout_duration_seconds",
              "session_idle_seconds", "session_absolute_seconds"):
        _int(a[k], "auth." + k, 1)
    z = s["zone_h"]
    if not isinstance(z["holders"], list) or len(set(z["holders"])) != len(z["holders"]) or \
            not all(isinstance(h, str) and h for h in z["holders"]):
        raise ConfigInvalid({"zone_h.holders": "unique non-empty strings"})
    _int(z["reauth_window_seconds"], "zone_h.reauth_window_seconds", 1, 3600)
    _int(s["audit"]["anchor_every"], "audit.anchor_every", 1)
    if s["audit"]["anchor_path"] is not None and not isinstance(s["audit"]["anchor_path"], str):
        raise ConfigInvalid({"audit.anchor_path": "string"})
    n = s["network"]
    if not isinstance(n["exposure_approved"], bool) or not isinstance(n["bind"], str):
        raise ConfigInvalid({"network": "bind string / exposure_approved boolean"})
    return s


def config_hash(cfg):
    """sha256 of the canonical form of the whole loaded config (CONFIG_LOADED, AC-SEC-21 / AC-GATE-22)."""
    return sha256_hex(canonical(cfg))


def anchor_path(settings, data_dir):
    """Resolve audit.anchor_path: must be set, absolute, outside the hub DB directory and in a sandbox-safe place."""
    p = settings["audit"]["anchor_path"]
    if not p:
        raise ConfigInvalid({"audit.anchor_path": None,
                             "reason": "must be set in config (OD-S12-18 default accepted under OD-15)"})
    from hub.guards import sandbox  # function-level since Stage 27: breaks the guards -> obs -> security -> guards cycle (OD-27 debt)
    p = os.path.expanduser(p)
    if not os.path.isabs(p):
        raise ConfigInvalid({"audit.anchor_path": p, "reason": "must be absolute"})
    real = sandbox.real(p)
    if sandbox.inside(real, data_dir):
        raise ConfigInvalid({"audit.anchor_path": p, "reason": "must be outside the database directory (BEH-SEC-06)"})
    sandbox.assert_safe_path(os.path.dirname(real), "audit anchor directory")
    return real
