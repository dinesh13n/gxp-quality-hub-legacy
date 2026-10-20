"""INC-09 (R2) error codes. Exit code 32 is an INC-09 choice for the R2 family; E-SEC-REASON-REQUIRED keeps the security family exit code 19.
Stage 12 addendum needed (RTD-78): E-REV-INDEX-ABSENT, E-R2-INPUT-INVALID and the exit code 32 are not in the Stage 12 registry;
E-SEC-REASON-REQUIRED (422) and E-REV-TEMPLATE-INVALID (422) are (error-handling-spec.md)."""
from hub.core.errors import HubError


class ReasonRequired(HubError):
    code, exit_code, http, message = "E-SEC-REASON-REQUIRED", 19, 422, "a read of C3 data or an export needs a non-empty reason"


class IndexAbsent(HubError):  # INC-09 addendum
    code, exit_code, http, message = "E-REV-INDEX-ABSENT", 32, 409, "the derived search corpus has not been built (python -m hub.search build-index)"


class R2InputInvalid(HubError):  # INC-09 addendum
    code, exit_code, http, message = "E-R2-INPUT-INVALID", 32, 422, "report parameter invalid"
