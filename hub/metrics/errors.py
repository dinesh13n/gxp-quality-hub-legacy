"""INC-07 metric error codes (docs/12-specs/error-handling-spec.md, F07-3) as HubError subclasses. Exit code 30 is an INC-07 choice for the whole
E-MET-* family (the spec gives none): Stage 12 addendum needed (RTD-58)."""
from hub.core.errors import HubError


class MetTagRequired(HubError):
    code, exit_code, http, message = "E-MET-TAG-REQUIRED", 30, 422, "a metric involving closed / resolved / approved / cost / handling time needs a definition tag"


class MetTagMix(HubError):
    code, exit_code, http, message = "E-MET-TAG-MIX", 30, 422, "arithmetic or comparison across different definition tags or policy versions"


class MetCutoffRequired(HubError):
    code, exit_code, http, message = "E-MET-CUTOFF-REQUIRED", 30, 422, "month-end total needs an explicit cut-off and denominator"


class MetUnparsableInput(HubError):
    code, exit_code, http, message = "E-MET-UNPARSABLE-INPUT", 30, 422, "unparsable amounts present"


class MetSourceRefused(HubError):
    code, exit_code, http, message = "E-MET-SOURCE-REFUSED", 30, 422, "source is not accepted for this meaning"


class MetNotAvailable(HubError):
    code, exit_code, http, message = "E-MET-NOT-AVAILABLE", 30, 501, "not available"


class MetNotReproducible(HubError):
    code, exit_code, http, message = "E-MET-NOT-REPRODUCIBLE", 30, 409, "stored value does not recompute"


class MetUnknownMetric(HubError):
    code, exit_code, http, message = "E-MET-UNKNOWN-METRIC", 30, 404, "unknown metric or value id"


class MetDefinitionRequired(HubError):
    code, exit_code, http, message = "E-MET-DEFINITION-REQUIRED", 30, 422, "a definition tag or clock is required"
