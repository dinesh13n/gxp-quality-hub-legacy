"""Disposition recording mode and values (ADR-006, BEH-GATE-06, FR-GATE-05; INC-08).

  disposition.mode     none (default) | event | external_ref       config baseline; the latest DISPOSITION_MODE_CHANGED policy event
                                                                  (written ONLY through Zone H ZH-08) wins over the baseline
  disposition.values   [] (default)                               the allowed `decision` values for event mode; no value ships

Config can not weaken the human gate: a baseline of `event` still needs a holder, a human dispositioner and a fresh step-up
re-authentication for every disposition, and `none` is the safe default. The keys are not in hub-config.schema.json v0.1 -> schema addendum
(RTD-66). Past events keep the `mode_at_write` they were stored with (BEH-GATE-06); this module never rewrites anything.
"""
import copy
import json

from hub.core.errors import ConfigInvalid

MODES = ("none", "event", "external_ref")
MAX_VALUES = 50
MAX_VALUE_LEN = 64
DEFAULTS = {"mode": "none", "values": []}


def check_values(values, where="disposition.values"):
    if not isinstance(values, list) or len(values) > MAX_VALUES or len(set(values)) != len(values) or \
            not all(isinstance(v, str) and v.strip() and len(v) <= MAX_VALUE_LEN and v == v.strip() for v in values):
        raise ConfigInvalid({where: "a list of at most %d unique, non-empty, trimmed strings of at most %d characters" % (MAX_VALUES, MAX_VALUE_LEN)})
    return list(values)


def resolve(cfg=None):
    """The validated `disposition` baseline from a loaded hub config."""
    s = copy.deepcopy(DEFAULTS)
    over = (cfg or {}).get("disposition")
    if over is None:
        return s
    if not isinstance(over, dict):
        raise ConfigInvalid({"disposition": "must be an object"})
    for k, v in over.items():
        if k not in s:
            raise ConfigInvalid({"disposition." + k: "unknown setting"})
        s[k] = copy.deepcopy(v)
    if s["mode"] not in MODES:
        raise ConfigInvalid({"disposition.mode": s["mode"], "allowed": list(MODES)})
    s["values"] = check_values(s["values"])
    return s


def current(con, base):
    """{mode, values, event_id, origin}: the baseline, replaced by the latest ZH-08 policy event when there is one."""
    row = con.execute("SELECT event_id, new_value, occurred_at FROM policy_events WHERE event_type = 'DISPOSITION_MODE_CHANGED'"
                      " AND policy_ref = 'disposition' ORDER BY rowid DESC LIMIT 1").fetchone()
    if row is None:
        return {"mode": base["mode"], "values": list(base["values"]), "event_id": None, "origin": "config_default"}
    new = json.loads(row[1])
    return {"mode": new["mode"], "values": list(new.get("values", [])), "event_id": row[0], "origin": "zone_h_event"}
