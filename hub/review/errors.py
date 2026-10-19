"""INC-08 reviewer-support error codes (docs/12-specs/error-handling-spec.md F08-3). Exit code 31 (INC-08 family; Stage 12 addendum, RTD-66)."""
from hub.core.errors import HubError


class ReviewNotFound(HubError):
    code, exit_code, http, message = "E-REV-NOT-FOUND", 31, 404, "unknown flag, queue item or trace"


class QueryInvalid(HubError):
    code, exit_code, http, message = "E-REV-QUERY-INVALID", 31, 422, "unknown search field or malformed filter"


class QueryTooLong(HubError):
    code, exit_code, http, message = "E-REV-QUERY-TOO-LONG", 31, 422, "query over 200 characters or 12 terms"


class SearchDisabled(HubError):
    code, exit_code, http, message = "E-REV-SEARCH-DISABLED", 31, 501, "search is not enabled in this release"


class TemplateInvalid(HubError):
    code, exit_code, http, message = "E-REV-TEMPLATE-INVALID", 31, 422, "template fields invalid"


class DraftsDisabled(HubError):  # INC-08 addendum: OP-REV-04 (R2, Could) is deferred by default (BEH-REV-07)
    code, exit_code, http, message = "E-REV-DRAFTS-DISABLED", 31, 501, "template drafts are not enabled in this release"
