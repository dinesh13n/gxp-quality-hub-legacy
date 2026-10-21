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


def validate(cfg):
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
        with open(path, encoding="utf-8") as f:
            _merge(cfg, json.load(f))
    if overrides:
        _merge(cfg, overrides)
    return validate(cfg)


def authority(cfg, capability):
    return cfg.get("capability_authority", {}).get(capability, "shadow")
