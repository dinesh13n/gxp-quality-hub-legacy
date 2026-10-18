"""INC-04 error codes (docs/12-specs/error-handling-spec.md, F03-4) as HubError subclasses.

hub/core/errors.py and hub/security/errors.py are frozen (TST-CO-05 c, add-only), so the codes live here.
The HTTP status is the catalogue value. Exit codes: the spec gives none for E-POL-*; INC-04 chooses 23 for the
policy family and 19 for the gate/authority family (same as E-AUTH-*) - Stage 12 addendum needed (RTD-38).
Codes marked "INC-04 addendum" are not in the Stage 12 registry.
"""
from hub.core.errors import HubError


class NoActiveRuleset(HubError):
    code, exit_code, http, message = "E-POL-NO-ACTIVE-RULESET", 23, 409, "no active rule set and no explicit ruleset_ref"


class Overlap(HubError):
    code, exit_code, http, message = "E-POL-OVERLAP", 23, 409, "overlapping effective windows for the same definition tag"


class AuthorityRequired(HubError):
    code, exit_code, http, message = "E-POL-AUTHORITY-REQUIRED", 23, 422, "authority_ref is required"


class InputInvalid(HubError):
    code, exit_code, http, message = "E-POL-INPUT-INVALID", 23, 422, "a decimal input is missing, non-numeric, NaN or infinite"


class ReadonlySet(HubError):
    code, exit_code, http, message = "E-POL-READONLY-SET", 23, 409, "as-found rule sets are read-only"


class UnknownFunction(HubError):
    code, exit_code, http, message = "E-POL-UNKNOWN-FUNCTION", 23, 422, "function is not in the catalogue or not served by this rule set"


class NotFound(HubError):
    code, exit_code, http, message = "E-POL-NOT-FOUND", 23, 404, "unknown policy, rule set or version"


class ClockCalendarRequired(HubError):
    code, exit_code, http, message = "E-POL-CLOCK-CALENDAR-REQUIRED", 23, 422, "business_calendar needs a calendar_ref"


class GateNotAuthorised(HubError):
    code, exit_code, http, message = "E-GATE-NOT-AUTHORISED", 19, 403, "Zone H action not authorised for this actor"


class GateNoHolders(HubError):
    code, exit_code, http, message = "E-GATE-NO-HOLDERS", 19, 423, "no Zone H holders are configured"


class DecisionRequired(HubError):  # INC-04 addendum (OD-16: activation needs a recorded human decision)
    code, exit_code, http, message = "E-POL-DECISION-REQUIRED", 23, 409, "no valid recorded human decision for this activation"


class AsFoundDrift(HubError):  # INC-04 addendum (AD-06: the legacy source no longer matches the pinned transcription)
    code, exit_code, http, message = "E-POL-ASFOUND-DRIFT", 24, None, "legacy rule source differs from the pinned transcription"


class PolicyInvalid(HubError):  # INC-04 addendum (policy body / status / transition validation)
    code, exit_code, http, message = "E-POL-INVALID", 23, 422, "policy object or rule set failed validation"
