"""GatedPolicyService: the INC-04 PolicyService with Zone H eligibility routed to the shared F02 gate (DEV-34 / OD-17).

hub/policy/service.py and hub/policy/gate.py are frozen by the add-only rule (TST-CO-05 c), so the replacement is a
subclass that overrides the single hook `_zone_h`; behaviour is otherwise inherited. Differences to the local copy:
the re-authentication window raises E-GATE-REAUTH-REQUIRED (as specified) instead of E-GATE-NOT-AUTHORISED, and an
unauthenticated call raises E-AUTH-UNAUTHENTICATED. The INC-04 local copy is no longer used by this class.
"""
from hub.gate.service import GateService
from hub.policy.service import PolicyService


class GatedPolicyService(PolicyService):
    def _zone_h(self, sess, zh, cid, object_ref):
        return GateService(self.con, self.s, self.clock, self.anchor).require_holder(sess, zh, cid, object_ref)
