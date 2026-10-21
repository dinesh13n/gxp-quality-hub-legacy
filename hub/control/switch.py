"""Audited flag changes (Stage 23 DW-17; FF-2 rule 4): every change of a decision flag is a CONFIG_CHANGED audit record with the flag,
the old and the new value, the approval reference and the config hashes before / after (credential-like keys never appear: audit.py
refuses them). Two writers:

  record_authority_changes   at every start-up that audits CONFIG_LOADED: a capability_authority value in the loaded config that differs from
                             the last recorded value (default `shadow`) is audited as a config-file change - so a hand-edited config file
                             cannot flip a capability without a record. Nothing is written when nothing changed (no record on a default install).
  change_record              the explicit operator commands of hub.control (set-flag, flip-to-shadow).

The L3 rollback (rollback-strategy L3) is the same record in the other direction: authoritative -> shadow, approval_ref null (returning to
the safe default needs no approval), direction `to_default`. Other decision flags are audited by the explicit commands; an edit of the
config file for them is visible through the CONFIG_LOADED config hash only (S23-DEV-03).
"""
import json

from hub.control import flags
from hub.security import audit, settings

PREFIX = "flag:"


def recorded_authority(con):
    """{capability: last audited new value} from CONFIG_CHANGED records (later records win)."""
    p = PREFIX + flags.AUTHORITY_KEY + "."
    out = {}
    for ref, details in con.execute("SELECT object_ref, details FROM audit_log WHERE action = 'CONFIG_CHANGED' AND substr(object_ref, 1, ?) = ?"
                                    " ORDER BY audit_seq", (len(p), p)):
        out[ref[len(p):]] = json.loads(details).get("new")
    return out


def change_record(con, clock, anchor, actor, actor_kind, correlation_id, flag, old, new, approval_ref, source, extra=None):
    to_default = new == flags.default_of(flag) if flags.is_registered(flag) else False
    details = {"flag": flag, "old": old, "new": new, "approval_ref": approval_ref, "source": source,
               "direction": "to_default" if to_default else "to_non_default"}
    details.update(extra or {})
    return audit.append(con, clock, anchor=anchor, actor=actor, actor_kind=actor_kind, action="CONFIG_CHANGED", outcome="success",
                        correlation_id=correlation_id, object_ref=PREFIX + flag, reason=(extra or {}).get("reason"), details=details)


def record_authority_changes(con, clock, anchor, cfg, correlation_id, command):
    """Audit capability_authority values that differ from the last recorded state. Returns the list of appended records."""
    now = dict(cfg.get(flags.AUTHORITY_KEY) or {})
    before = recorded_authority(con)
    refs = cfg.get(flags.APPROVALS_KEY) or {}
    out = []
    for cap in sorted(set(now) | set(before)):
        old, new = before.get(cap, flags.AUTHORITY_DEFAULT), now.get(cap, flags.AUTHORITY_DEFAULT)
        if old == new:
            continue
        flag = flags.AUTHORITY_KEY + "." + cap
        ref = refs.get(flag) if new != flags.AUTHORITY_DEFAULT else None
        out.append(change_record(con, clock, anchor, "hub", "system", correlation_id, flag, old, new, ref, "config-file",
                                 {"command": command, "config_hash": settings.config_hash(cfg)}))
    return out
