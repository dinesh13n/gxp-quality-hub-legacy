"""Decision-record settings resolved from the loaded hub config dict (feature-flag-plan FF-1; defaults = Stage 14 defaults,
accepted on Dinesh's instruction OD-12 / OD-17). These keys are not in hub-config.schema.json v0.1 -> schema addendum (RTD-47).

  closure.unconfigured_behaviour  treat_label_CLOSED_as_closing (default, fail closed) | none     (OD-S12-03)
  workflow.transition_table       structural (default) | strict                                    (OD-S12-16)
  workflow.transitions            {from_state: [to_state, ...]} - required for strict, ignored for structural
  facts.derivation                human_only (default; the only value built)                      (OD-S12-15)
  case_creation.enabled           false (default): R1 creates cases by legacy backfill only         (OD-S12-19)
"""
import copy

from hub.core.errors import ConfigInvalid

VOCAB = ("OPEN", "UNDER_REVIEW", "CLOSED", "ESCALATED", "REOPENED")
CLOSING_LABEL = "CLOSED"      # role tag closing_label  (Assumption A-12-F01-2: a spec convenience, not a definition of 'closed')
REOPENED_LABEL = "REOPENED"   # role tag reopened
DEFAULTS = {
    "closure": {"unconfigured_behaviour": "treat_label_CLOSED_as_closing"},
    "workflow": {"transition_table": "structural", "transitions": {}},
    "facts": {"derivation": "human_only"},
    "case_creation": {"enabled": False},
}


def resolve(cfg=None):
    s = copy.deepcopy(DEFAULTS)
    for key in DEFAULTS:
        over = (cfg or {}).get(key)
        if over is None:
            continue
        if not isinstance(over, dict):
            raise ConfigInvalid({key: "must be an object"})
        for k, v in over.items():
            if k not in s[key]:
                raise ConfigInvalid({key + "." + k: "unknown setting"})
            s[key][k] = copy.deepcopy(v)
    if s["closure"]["unconfigured_behaviour"] not in ("treat_label_CLOSED_as_closing", "none"):
        raise ConfigInvalid({"closure.unconfigured_behaviour": s["closure"]["unconfigured_behaviour"]})
    if s["workflow"]["transition_table"] not in ("structural", "strict"):
        raise ConfigInvalid({"workflow.transition_table": s["workflow"]["transition_table"]})
    if s["facts"]["derivation"] != "human_only":
        raise ConfigInvalid({"facts.derivation": s["facts"]["derivation"],
                             "reason": "only human_only is built (OD-S12-15 default); rule derivation is not implemented"})
    if not isinstance(s["case_creation"]["enabled"], bool):
        raise ConfigInvalid({"case_creation.enabled": "boolean"})
    if s["workflow"]["transition_table"] == "strict":
        t = s["workflow"]["transitions"]
        if not isinstance(t, dict) or sorted(t) != sorted(VOCAB) or \
                not all(isinstance(v, list) and all(x in VOCAB for x in v) for v in t.values()):
            raise ConfigInvalid({"workflow.transitions": "strict needs a list of target states for each of %s" % list(VOCAB)})
    return s
