"""Gate error codes (docs/12-specs/error-handling-spec.md, F02-4).

E-GATE-NOT-AUTHORISED and E-GATE-NO-HOLDERS are the INC-04 classes (hub/policy/errors.py is frozen), re-exported so one
`except` clause serves both gates. New here: E-GATE-REAUTH-REQUIRED (401) and E-GATE-UNKNOWN-ACTION (422). Exit code 19
as for the other authority errors (INC-04 choice, RTD-38).
"""
from hub.core.errors import HubError
from hub.policy.errors import GateNoHolders, GateNotAuthorised  # noqa: F401  (re-export)


class GateReauthRequired(HubError):
    code, exit_code, http, message = "E-GATE-REAUTH-REQUIRED", 19, 401, "step-up re-authentication window elapsed"


class GateUnknownAction(HubError):
    code, exit_code, http, message = "E-GATE-UNKNOWN-ACTION", 19, 422, "action is not in the closed Zone H list ZH-01..ZH-10"
