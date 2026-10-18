"""INC-05 error codes (docs/12-specs/error-handling-spec.md F01-4, F05-4) as HubError subclasses.

hub/core/errors.py, hub/security/errors.py and hub/policy/errors.py are frozen (TST-CO-05 c, add-only), so the codes live
here. `http` is the catalogue status. Exit codes: the spec gives none for E-DEC-* / E-ID-*; INC-05 chooses 25 for the
decision family and 26 for the crosswalk family (Stage 12 addendum needed, RTD-47). Codes marked "INC-05 addendum" are
not in the Stage 12 registry.
"""
from hub.core.errors import HubError


class Immutable(HubError):
    code, exit_code, http, message = "E-DEC-IMMUTABLE", 25, 409, "attempt to modify or delete an immutable record"


class CaseNotFound(HubError):
    code, exit_code, http, message = "E-DEC-CASE-NOT-FOUND", 25, 404, "unknown case id"


class NotYetExists(HubError):
    code, exit_code, http, message = "E-DEC-NOT-YET-EXISTS", 25, 404, "as_of is earlier than the first state event"


class TimeOrder(HubError):
    code, exit_code, http, message = "E-DEC-TIME-ORDER", 25, 422, "occurred_at is in the future or before the previous event"


class ReopenExplicit(HubError):
    code, exit_code, http, message = "E-DEC-REOPEN-EXPLICIT", 25, 422, "transition into REOPENED needs a REOPEN event with a basis"


class EvidenceRequired(HubError):
    code, exit_code, http, message = "E-DEC-EVIDENCE-REQUIRED", 25, 422, "closing transition has neither evidence nor an accepted exception"


class EvidenceUnresolved(HubError):
    code, exit_code, http, message = "E-DEC-EVIDENCE-UNRESOLVED", 25, 422, "evidence reference does not exist"


class SeqConflict(HubError):
    code, exit_code, http, message = "E-DEC-SEQ-CONFLICT", 25, 409, "expected_seq does not match the case"


class IdempotencyMismatch(HubError):
    code, exit_code, http, message = "E-DEC-IDEMPOTENCY-MISMATCH", 25, 422, "Idempotency-Key reused with a different request"


class NoOp(HubError):
    code, exit_code, http, message = "E-DEC-NOOP", 25, 422, "same-state transition"


class FieldTooLong(HubError):
    code, exit_code, http, message = "E-DEC-FIELD-TOO-LONG", 25, 422, "text field above its limit"


class StateUnknown(HubError):  # INC-05 addendum
    code, exit_code, http, message = "E-DEC-STATE-UNKNOWN", 25, 422, "state is not in the case_status vocabulary"


class TransitionNotAllowed(HubError):  # INC-05 addendum (strict transition table, OD-S12-16)
    code, exit_code, http, message = "E-DEC-TRANSITION-NOT-ALLOWED", 25, 422, "the strict transition table does not allow this change"


class CreationDisabled(HubError):  # INC-05 addendum (OD-S12-19: R1 = legacy backfill only)
    code, exit_code, http, message = "E-DEC-CREATION-DISABLED", 25, 409, "case creation is disabled: R1 creates cases by legacy backfill only"


class FactInvalid(HubError):  # INC-05 addendum
    code, exit_code, http, message = "E-DEC-FACT-INVALID", 25, 422, "unknown or system-written fact type"


class ChainBroken(HubError):  # INC-05 addendum
    code, exit_code, http, message = "E-DEC-CHAIN-BROKEN", 25, 409, "a per-case event hash chain does not verify"


class BackfillMismatch(HubError):  # INC-05 addendum (G4: count must be 125 and projection must verify)
    code, exit_code, http, message = "E-DEC-BACKFILL-MISMATCH", 27, None, "backfill count or projection check failed"


class LinkExists(HubError):
    code, exit_code, http, message = "E-ID-LINK-EXISTS", 26, 409, "an active link already joins these two objects"


class PairNotRegistered(HubError):
    code, exit_code, http, message = "E-ID-PAIR-NOT-REGISTERED", 26, 422, "the type pair is not in the crosswalk registry"


class SelfLink(HubError):
    code, exit_code, http, message = "E-ID-SELF-LINK", 26, 422, "an object cannot be linked to itself"


class AmbiguousType(HubError):
    code, exit_code, http, message = "E-ID-AMBIGUOUS-TYPE", 26, 422, "identifier matches several id patterns: id_type is required"


class IdReasonRequired(HubError):
    code, exit_code, http, message = "E-ID-REASON-REQUIRED", 26, 422, "a human link or retraction needs a non-empty reason"


class IdNotFound(HubError):
    code, exit_code, http, message = "E-ID-NOT-FOUND", 26, 404, "unknown identifier"


class LinkNotFound(HubError):
    code, exit_code, http, message = "E-ID-LINK-NOT-FOUND", 26, 404, "unknown link"


class CaseIdInvalid(HubError):  # INC-05 addendum
    code, exit_code, http, message = "E-DEC-CASE-ID-INVALID", 25, 422, "case id does not match C + 8 digits"


class CaseExists(HubError):  # INC-05 addendum
    code, exit_code, http, message = "E-DEC-CASE-EXISTS", 25, 409, "the case already has events"
