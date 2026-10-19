"""Run settings resolved from the loaded hub config dict (feature-flag-plan FF-1; defaults accepted under OD-12/OD-19).

  schedule.enabled          false. Config can NOT switch it on: the flag is the latest SCHEDULE_CHANGED policy event written through
                            Zone H ZH-09 (DEV-64). A config value of true is refused (E-CFG-INVALID).
  schedule.expected         [] ; entries {"job": <catalogue job>, "at": "HH:MM"} (daily, site.timezone) used only by the missing-run detector
  schedule.grace_minutes    60 ; an expected run is "missed" only after this grace period
  runs.batch_size           NOT defaulted: batching jobs need an explicit value here or --batch-size (no hidden constant, BEH-RUN-05)
  runs.heartbeat_stale_seconds  900 (15 min, A-12-F06-1)
  site.timezone             "UTC" (Unknown; labelled) or a fixed offset "+HH:MM" / "-HH:MM" (named zones are not supported: tz data is not
                            guaranteed on the target, RTD-62)
These keys are not (all) in hub-config.schema.json v0.1 -> schema addendum (RTD-58).
"""
import copy
import re

from hub.core.errors import ConfigInvalid
from hub.runs.catalogue import JOBS

DEFAULTS = {
    "schedule": {"enabled": False, "expected": [], "grace_minutes": 60},
    "runs": {"batch_size": None, "heartbeat_stale_seconds": 900},
    "site": {"timezone": "UTC"},
}
_HHMM = re.compile(r"^([01][0-9]|2[0-3]):[0-5][0-9]$")
_TZ = re.compile(r"^([+-])([01][0-9]|2[0-3]):([0-5][0-9])$")


def _pos_int(v, name):
    if isinstance(v, bool) or not isinstance(v, int) or v < 1:
        raise ConfigInvalid({name: v, "allowed": ">= 1"})
    return v


def tz_offset_minutes(tz):
    if tz == "UTC":
        return 0
    m = _TZ.match(tz or "")
    if not m:
        raise ConfigInvalid({"site.timezone": tz, "allowed": "UTC or a fixed offset +HH:MM / -HH:MM"})
    return (1 if m.group(1) == "+" else -1) * (int(m.group(2)) * 60 + int(m.group(3)))


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
    sc = s["schedule"]
    if sc["enabled"] is not False:
        raise ConfigInvalid({"schedule.enabled": sc["enabled"],
                             "reason": "the schedule flag is switched only by a Zone H ZH-09 event, never by config (OD-S12-10, OD-19)"})
    if not isinstance(sc["expected"], list):
        raise ConfigInvalid({"schedule.expected": "must be a list"})
    for e in sc["expected"]:
        if not (isinstance(e, dict) and sorted(e) == ["at", "job"] and e["job"] in JOBS and isinstance(e["at"], str) and _HHMM.match(e["at"])):
            raise ConfigInvalid({"schedule.expected": "entries are {job: <catalogue job>, at: 'HH:MM'}"})
    _pos_int(sc["grace_minutes"], "schedule.grace_minutes")
    r = s["runs"]
    if r["batch_size"] is not None:
        _pos_int(r["batch_size"], "runs.batch_size")
    _pos_int(r["heartbeat_stale_seconds"], "runs.heartbeat_stale_seconds")
    tz_offset_minutes(s["site"]["timezone"])
    return s
