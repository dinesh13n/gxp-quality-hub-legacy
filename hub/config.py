"""Hub configuration and the INC-02 feature flags (docs/14-transformation/feature-flag-plan.md FF-1).

Introduced in INC-02 (safe defaults, FF-2 rule 1):
  data_origin                    synthetic (only accepted value until HAR-15)
  hub.kill                       false     (kill switch; true refuses every command except selfcheck)
  capability_authority.<cap>     shadow    ('authoritative' needs approval_refs['capability_authority.<cap>'] (HAR-11) since Stage 23 DW-17;
                                           refused without it; ships OFF: no capability is authoritative by default)
  runtime.floor                  "3.10"    (OD-S12-12 default; "3.12" = ADR-018 option)
These keys are not in hub-config.schema.json v0.1 -> schema addendum (Stage 15 open item; HAR-13: the Stage 12
file is not edited in place).
"""
import copy
import json

from hub.control import flags
from hub.core.errors import ConfigInvalid
from hub.runtime import DEFAULT_FLOOR, FLOORS

DEFAULTS = {
    "data_origin": "synthetic",
    "hub": {"kill": False},
    "capability_authority": {},
    "runtime": {"floor": DEFAULT_FLOOR},
}


def _merge(base, over):
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _merge(base[k], v)
        else:
            base[k] = v
    return base


# Stage 27 S26-F-05: the known configuration keys (docs/23-human-control/stage12-v0.2/schemas/hub-config.schema.json plus `rate_limit`, S27-DEV-07, plus the two INC-09 sections `crosswalk_view` and `intake_reports`).
# A dict value is a nested closed key set; None = free-form map (the keys are data: capability names, flag paths, workflow states); a list =
# a list of closed objects. A key that is not listed is refused with E-CFG-INVALID instead of being ignored (a mistyped safety key such as
# `hub.kil` used to be inert).
_FREE = None
KNOWN_KEYS = {
    "data_origin": _FREE, "hub": {"kill": _FREE}, "runtime": {"floor": _FREE}, "capability_authority": _FREE, "approval_refs": _FREE,
    "zone_h": {"holders": _FREE, "reauth_window_seconds": _FREE},
    "network": {"bind": _FREE, "exposure_approved": _FREE, "exposure_approval_ref": _FREE, "tls": {"cert_file": _FREE, "key_file": _FREE}},
    "audit": {"anchor_path": _FREE, "anchor_every": _FREE},
    "auth": {"pbkdf2_iterations": _FREE, "password_min_length": _FREE, "lockout_threshold": _FREE, "lockout_window_seconds": _FREE,
             "lockout_duration_seconds": _FREE, "session_idle_seconds": _FREE, "session_absolute_seconds": _FREE},
    "disposition": {"mode": _FREE, "values": _FREE}, "closure": {"unconfigured_behaviour": _FREE},
    "workflow": {"transition_table": _FREE, "transitions": _FREE}, "facts": {"derivation": _FREE}, "case_creation": {"enabled": _FREE},
    "schedule": {"enabled": _FREE, "expected": [{"job": _FREE, "at": _FREE}], "grace_minutes": _FREE},
    "runs": {"batch_size": _FREE, "heartbeat_stale_seconds": _FREE}, "site": {"timezone": _FREE},
    "search": {"enabled": _FREE, "fts": _FREE, "max_doc_chars": _FREE, "require_c3_reason": _FREE}, "templates": {"enabled": _FREE},
    "gateway": {"retries": _FREE},
    "contract_bindings": [{"source": _FREE, "contract_file": _FREE, "mode": _FREE}],
    "rate_limit": {"enabled": _FREE, "window_seconds": _FREE, "max_rejected": _FREE},
    # read by the INC-09 code (hub.r2.joined, hub.r2.intake_reports) but missing from the v0.2 schema: listed here so that a shipped option is not refused (S27-DEV-03)
    "crosswalk_view": {"depth_cap": _FREE, "size_cap": _FREE}, "intake_reports": {"delay_threshold_hours": _FREE, "freshness_hours": _FREE},
}


def unknown_keys(cfg, known=None, path=""):
    """Sorted dotted paths of the keys in `cfg` that KNOWN_KEYS does not list."""
    known = KNOWN_KEYS if known is None else known
    out = []
    if not isinstance(cfg, dict):
        return out
    for k in sorted(cfg, key=str):
        here = (path + "." + str(k)) if path else str(k)
        if k not in known:
            out.append(here[:80])
            continue
        sub, v = known[k], cfg[k]
        if isinstance(sub, dict):
            out += unknown_keys(v, sub, here)
        elif isinstance(sub, list) and isinstance(v, list):
            for i, item in enumerate(v):
                out += unknown_keys(item, sub[0], "%s[%d]" % (here, i))
    return out


def validate(cfg):
    for k, sub in KNOWN_KEYS.items():  # a section of the wrong shape is a config error, not an AttributeError further down
        if k in cfg and ((isinstance(sub, dict) and not isinstance(cfg[k], dict)) or (isinstance(sub, list) and not isinstance(cfg[k], list))):
            raise ConfigInvalid({k: "must be an %s" % ("object" if isinstance(sub, dict) else "array")})
    bad = unknown_keys(cfg)
    if bad:
        raise ConfigInvalid({"unknown_keys": bad[:20], "reason": "key not in the hub-config schema (S26-F-05)"})
    if cfg.get("data_origin") != "synthetic":
        raise ConfigInvalid({"data_origin": cfg.get("data_origin"), "reason": "only 'synthetic' before HAR-15"})
    if not isinstance(cfg.get("hub", {}).get("kill"), bool):
        raise ConfigInvalid({"hub.kill": "must be boolean"})
    flags.check(cfg)  # Stage 23 DW-17: a non-default decision flag (incl. capability_authority.<cap> = authoritative) needs approval_refs[flag]
    if cfg.get("runtime", {}).get("floor") not in FLOORS:
        raise ConfigInvalid({"runtime.floor": cfg.get("runtime", {}).get("floor")})
    return cfg


def load(path=None, overrides=None):
    cfg = copy.deepcopy(DEFAULTS)
    if path:
        # Stage 27 S26-F-04: an unreadable / non-JSON / non-object file is E-CFG-INVALID (exit 2), never a traceback; the message carries no file content
        try:
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
        except OSError as e:
            raise ConfigInvalid({"config_file": "unreadable", "reason": type(e).__name__})
        except (ValueError, RecursionError):
            raise ConfigInvalid({"config_file": "not valid UTF-8 JSON"})
        if not isinstance(doc, dict):
            raise ConfigInvalid({"config_file": "the top level must be a JSON object"})
        _merge(cfg, doc)
    if overrides:
        _merge(cfg, overrides)
    return validate(cfg)


def authority(cfg, capability):
    return cfg.get("capability_authority", {}).get(capability, "shadow")
