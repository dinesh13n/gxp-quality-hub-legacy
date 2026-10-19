"""INC-06 error codes (docs/12-specs/error-handling-spec.md F04-4) as HubError subclasses.

hub/core/errors.py is frozen (add-only rule, TST-CO-05 c); E-INT-UNTRUSTED-USE already lives there (hub.core.errors.UntrustedUse).
`http` is the catalogue status. The spec gives no exit code for the E-INT-* family: INC-06 chooses 28 (INC-05 used 25/26/27) - a Stage 12
addendum is needed (RTD-50). Item-level problems are reason codes (hub.intake.reasons), never these errors.
"""
from hub.core.errors import HubError


class RawImmutable(HubError):
    code, exit_code, http, message = "E-INT-RAW-IMMUTABLE", 28, 409, "modification of a raw or outcome row refused"


class EnvelopeInvalid(HubError):
    code, exit_code, http, message = "E-INT-ENVELOPE-INVALID", 28, 422, "request envelope unusable"


class SourceUnreachable(HubError):
    code, exit_code, http, message = "E-INT-SOURCE-UNREACHABLE", 28, 503, "source cannot be read"


class UrlSchemeRefused(HubError):
    code, exit_code, http, message = "E-INT-URL-SCHEME-REFUSED", 28, 422, "source URL is not http(s) on loopback"


class ResolutionReasonRequired(HubError):
    code, exit_code, http, message = "E-INT-RESOLUTION-REASON-REQUIRED", 28, 422, "a resolution needs a non-empty reason"


class ItemNotFound(HubError):
    code, exit_code, http, message = "E-INT-ITEM-NOT-FOUND", 28, 404, "unknown raw_id or not a revision conflict"


class ConflictAlreadyResolved(HubError):
    code, exit_code, http, message = "E-INT-CONFLICT-ALREADY-RESOLVED", 28, 409, "the conflict already has a resolution"
