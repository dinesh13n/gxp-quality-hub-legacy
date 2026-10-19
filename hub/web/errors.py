"""INC-08 HTTP-layer error codes (docs/12-specs/error-handling-spec.md ER-1..ER-3). E-SEC-CSRF uses exit code 19 (the INC-03 authority family),
the rest 31 (INC-08 family). Stage 12 addendum needed (RTD-66): E-REQ-TOO-LARGE and E-REQ-METHOD are not in the Stage 12 registry."""
from hub.core.errors import HubError


class ReqInvalid(HubError):
    code, exit_code, http, message = "E-REQ-INVALID", 31, 400, "malformed request"


class ReqTooLarge(HubError):  # INC-08 addendum (NFR body limit)
    code, exit_code, http, message = "E-REQ-TOO-LARGE", 31, 413, "request body above the limit"


class Csrf(HubError):
    code, exit_code, http, message = "E-SEC-CSRF", 19, 403, "missing or invalid CSRF token or custom header"


class MethodNotAllowed(HubError):  # INC-08 addendum (AC-INT-02: PUT/DELETE of a raw intake item)
    code, exit_code, http, message = "E-REQ-METHOD", 31, 405, "method not allowed on this route"
