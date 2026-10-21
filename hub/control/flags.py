"""Decision-flag register and the approval rule (Stage 23 DW-17; feature-flag-plan FF-1 / FF-2 rules 1, 3, 4; HAR-11).

FF-2 rule 3: a decision flag may hold a NON-DEFAULT value only when the config carries an `approval_refs` entry for it
(`approval_refs["<flag path>"]` = a non-empty reference to the recorded human decision, e.g. an orchestrator-decisions OD id).
The hub cannot check that the reference exists or who gave the approval (Unknown; the OD log is outside the product): the control is
"no reference, no switch", and every change is audited (CONFIG_CHANGED, see hub.control.switch). Returning a flag to its default needs
no reference. The default of every flag is the safe, non-adopting value (FF-2 rule 1); an `authoritative` capability has no consuming
code in this build (config.authority() is read by nothing yet): the switch is the gate, the consumers arrive with Stage 30.

`capability_authority.<cap>` values: shadow (default) | authoritative.
"""
import re

from hub.core.errors import ConfigInvalid

APPROVALS_KEY = "approval_refs"
AUTHORITY_KEY = "capability_authority"
AUTHORITY_DEFAULT = "shadow"
AUTHORITY_VALUES = ("shadow", "authoritative")
MAX_REF = 200
CAP_RE = re.compile(r"^[A-Za-z0-9_-]{1,40}$")

# (config path, shipped default, decision / approval link in feature-flag-plan FF-1)
DECISION_FLAGS = (
    ("disposition.mode", "none", "OD-S12-05 + HAR-12"),
    ("closure.unconfigured_behaviour", "treat_label_CLOSED_as_closing", "OD-S12-03"),
    ("workflow.transition_table", "structural", "OD-S12-16"),
    ("facts.derivation", "human_only", "OD-S12-15"),
    ("case_creation.enabled", False, "OD-S12-19"),
    ("search.enabled", False, "OD-S12-14"),
    ("search.fts", "off", "OD-S12-12 / OD-S12-14"),
    ("templates.enabled", False, "PCH-22"),
    ("zone_h.holders", [], "OD-S12-06 + HAR-11"),
)
AUTHORITY_LINK = "CUT step approval (HAR-11) + approved DV rows (HAR-06)"
# flags that already have their own, stricter control; listed so the register is complete (not checked here)
OTHER_CONTROLS = (
    ("network.exposure_approved", "hub.security.exposure.check_startup: approval + exposure_approval_ref + TLS, and hub.web.server refuses non-loopback anyway"),
    ("schedule.enabled", "refused in config by hub.runs.settings; the flag is a policy event written by a Zone H holder (ZH-09)"),
    ("data_origin", "only 'synthetic' is accepted before HAR-15 (hub.config.validate)"),
    ("hub.kill", "true only stops the hub; no approval is needed to stop it (FF-2 rule 6)"),
)


def get(cfg, path, default=None):
    cur = cfg
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def _same(a, b):
    return type(a) is type(b) and a == b


def valid_ref(ref):
    return isinstance(ref, str) and 0 < len(ref.strip()) <= MAX_REF and ref.isprintable()


def nondefault(cfg):
    """[(flag path, value, link)] for every registered decision flag (incl. each capability_authority.<cap>) that is not at its default."""
    out = []
    for path, default, link in DECISION_FLAGS:
        v = get(cfg, path, default)
        if not _same(v, default):
            out.append((path, v, link))
    for cap, mode in sorted((cfg.get(AUTHORITY_KEY) or {}).items()):
        if mode != AUTHORITY_DEFAULT:
            out.append((AUTHORITY_KEY + "." + cap, mode, AUTHORITY_LINK))
    return out


def check(cfg):
    """Raise ConfigInvalid for a bad authority value or a non-default decision flag without an approval reference."""
    caps = cfg.get(AUTHORITY_KEY, {})
    if not isinstance(caps, dict):
        raise ConfigInvalid({AUTHORITY_KEY: "must be an object capability -> shadow | authoritative"})
    refs = cfg.get(APPROVALS_KEY, {})
    if not isinstance(refs, dict) or not all(isinstance(k, str) for k in refs):
        raise ConfigInvalid({APPROVALS_KEY: "must be an object flag path -> approval reference"})
    for cap, mode in sorted(caps.items()):
        if not isinstance(cap, str) or not CAP_RE.match(cap):
            raise ConfigInvalid({AUTHORITY_KEY: str(cap)[:60], "reason": "capability name must match [A-Za-z0-9_-]{1,40}"})
        if mode not in AUTHORITY_VALUES:
            raise ConfigInvalid({AUTHORITY_KEY: cap, "value": mode, "allowed": list(AUTHORITY_VALUES)})
    for path, value, link in nondefault(cfg):
        if not valid_ref(refs.get(path)):
            raise ConfigInvalid({"flag": path, "value": value, "reason": "a non-default decision flag needs approval_refs[flag] "
                                 "(a reference to the recorded human approval; FF-2 rule 3, HAR-11)", "approval": link})
    return cfg


def default_of(path):
    for p, d, _ in DECISION_FLAGS:
        if p == path:
            return d
    if path.startswith(AUTHORITY_KEY + "."):
        return AUTHORITY_DEFAULT
    raise KeyError(path)


def is_registered(path):
    if path.startswith(AUTHORITY_KEY + "."):
        return bool(CAP_RE.match(path[len(AUTHORITY_KEY) + 1:]))
    return path in [p for p, _, _ in DECISION_FLAGS]


def effective(cfg, path):
    if path.startswith(AUTHORITY_KEY + "."):
        return (cfg.get(AUTHORITY_KEY) or {}).get(path[len(AUTHORITY_KEY) + 1:], AUTHORITY_DEFAULT)
    return get(cfg, path, default_of(path))
