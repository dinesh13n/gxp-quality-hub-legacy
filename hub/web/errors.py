"""INC-08 HTTP-layer error codes (docs/12-specs/error-handling-spec.md ER-1..ER-3). E-SEC-CSRF uses exit code 19 (the INC-03 authority family),
the rest 31 (INC-08 family). Stage 12 addendum needed (RTD-66): E-REQ-TOO-LARGE and E-REQ-NOT-IMPLEMENTED are not in the Stage 12 registry."""
from hub.core.errors import HubError
from hub.core.req_errors import ReqInvalid  # noqa: F401  (Stage 20 DW-06: same class, defined in the core; re-exported here)


class ReqTooLarge(HubError):  # INC-08 addendum (NFR body limit)
    code, exit_code, http, message = "E-REQ-TOO-LARGE", 31, 413, "request body above the limit"


class Csrf(HubError):
    code, exit_code, http, message = "E-SEC-CSRF", 19, 403, "missing or invalid CSRF token or custom header"


class NotImplementedYet(HubError):  # INC-08 addendum: an R2 operation whose backing component is built in a later increment
    code, exit_code, http, message = "E-REQ-NOT-IMPLEMENTED", 31, 501, "operation not available in this release"


class RateLimited(HubError):  # Stage 27 addendum (RS-04): too many refused requests from one peer in the window
    code, exit_code, http, message = "E-REQ-RATE-LIMITED", 31, 429, "too many refused requests from this peer; try again later"


class StoreUnavailable(HubError):  # Stage 27 addendum (S26-F-07): the store file can not be opened / read / written
    code, exit_code, http, message = "E-STORE-UNAVAILABLE", 31, 503, "the hub store is unavailable"


class ReqTimeout(HubError):  # Stage 27 addendum (S26-F-06): the client did not deliver the declared body before the read timeout
    code, exit_code, http, message = "E-REQ-TIMEOUT", 31, 408, "the request was not received in time"
