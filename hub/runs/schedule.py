"""ZH-09: switch the schedule flag on or off (BEH-RUN-02, AC-RUN-03). The ONLY run module that imports the Zone H gate; the runner and the
jobs never import it. With the shipped empty zone_h.holders nobody can enable it (E-GATE-NO-HOLDERS); a service actor is always rejected
(E-GATE-NOT-AUTHORISED). There is still no scheduler in this package: the flag only lets `--trigger scheduled` be accepted from an OS-level
entry that lives outside the repository (OD-19)."""
from hub.core.errors import ConfigInvalid
from hub.gate.service import GateService
from hub.policy.errors import AuthorityRequired
from hub.runs.flag import schedule_state
from hub.security import audit
from hub.security.canonical import canonical


class ScheduleService(object):
    def __init__(self, con, settings, clock, anchor=None):
        self.con, self.s, self.clock, self.anchor = con, settings, clock, anchor

    def state(self):
        return schedule_state(self.con)

    def set_enabled(self, sess, enabled, authority_ref, correlation_id="schedule"):
        if not isinstance(enabled, bool):
            raise ConfigInvalid({"enabled": "must be boolean"})
        if not isinstance(authority_ref, str) or not authority_ref.strip():
            raise AuthorityRequired()
        hcr = "audit:%d" % GateService(self.con, self.s, self.clock, self.anchor).require_holder(sess, "ZH-09", correlation_id, "schedule")
        old = self.state()
        p = sess.principal
        with audit.change(self.con, self.clock, anchor=self.anchor, actor=p.principal_id, actor_kind=p.actor_kind,
                          action="SCHEDULE_CHANGED", outcome="success", correlation_id=correlation_id, object_ref="schedule",
                          details={"from_enabled": old["enabled"], "to_enabled": enabled}) as ctx:
            n = self.con.execute("SELECT count(*) FROM policy_events").fetchone()[0] + 1
            eid = "PE-%08d" % n
            self.con.execute("INSERT INTO policy_events(event_id, policy_ref, event_type, actor, occurred_at, old_value, new_value,"
                             " authority_ref, holder_check_ref) VALUES (?,?,?,?,?,?,?,?,?)",
                             (eid, "schedule", "SCHEDULE_CHANGED", p.principal_id, self.clock(), canonical({"enabled": old["enabled"]}),
                              canonical({"enabled": enabled}), authority_ref.strip(), hcr))
            ctx.fields["details"]["event_id"] = eid
        return self.state()
