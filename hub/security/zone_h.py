"""The ONE Zone H holder rule (Stage 20 DW-06; S16-D04 / AC-02, RTD-46 / RTD-51; BEH-GATE-01/05/07, FR-GATE-04).

Before Stage 20 the rule was written out three times (hub/gate/service.py, hub/policy/gate.py, hub/security/authz.py). Each caller now asks
this function for the refusal reason and keeps only its own error class and audit fields, so a change to the rule is made here once:
  1. the actor is a human (and, where the caller requires it, holds role `dispositioner`; an `integration` role may be rejected outright)
  2. zone_h.holders is not empty (ships EMPTY, OD-S12-06) - callers that do not distinguish an empty list report `not_a_holder`
  3. the principal is listed in zone_h.holders
  4. the last step-up re-authentication is within zone_h.reauth_window_seconds
Returns None when every condition holds, else the reason code of the FIRST failing condition. Pure: the caller passes its clock (`now`, a
callable returning an ISO timestamp, called only when condition 4 is reached - as in the three original copies) and writes the
ZONE_H_ATTEMPT audit record itself. There is no flag, environment variable or parameter that skips a condition (AC-GATE-21):
the options only choose how a failure is NAMED.
"""
from hub.security.canonical import parse

NOT_HUMAN_DISPOSITIONER = "not_a_human_dispositioner"
NON_HUMAN = "non_human"
NO_HOLDERS = "no_holders_configured"
NOT_A_HOLDER = "not_a_holder"
REAUTH = "reauth_required"


def refusal(principal, reauth_at, now, zone_h, require_dispositioner=True, reject_integration=False, distinguish_empty=True):
    """Reason code or None. `principal` has .kind, .roles, .principal_id; `zone_h` is settings['zone_h']."""
    holders = zone_h["holders"]
    if require_dispositioner:
        if principal.kind != "human" or "dispositioner" not in principal.roles or (reject_integration and "integration" in principal.roles):
            return NOT_HUMAN_DISPOSITIONER
    elif principal.kind != "human":
        return NON_HUMAN
    if not holders:
        return NO_HOLDERS if distinguish_empty else NOT_A_HOLDER
    if principal.principal_id not in holders:
        return NOT_A_HOLDER
    if parse(now()).timestamp() - parse(reauth_at).timestamp() > zone_h["reauth_window_seconds"]:
        return REAUTH
    return None
