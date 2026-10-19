"""INC-08 gate error codes (docs/12-specs/error-handling-spec.md F02-4). hub/gate/errors.py is frozen (TST-CO-05 c), so the codes added here live
in a new module. `http` is the catalogue status. Exit code 31 for the INC-08 family (Stage 12 addendum needed, RTD-66)."""
from hub.core.errors import HubError


class GateModeNone(HubError):
    code, exit_code, http, message = "E-GATE-MODE-NONE", 31, 423, "disposition.mode is none: no disposition can be recorded"


class GateValuesUnset(HubError):
    code, exit_code, http, message = "E-GATE-VALUES-UNSET", 31, 423, "disposition.values is empty: event mode cannot accept a decision"


class GatePackStale(HubError):
    code, exit_code, http, message = "E-GATE-PACK-STALE", 31, 409, "pack_hash is not current: re-read the evidence pack"


class GateReasonRequired(HubError):
    code, exit_code, http, message = "E-GATE-REASON-REQUIRED", 31, 422, "an override, dismissal or refusal needs a non-empty reason"


class GateExtrefInvalid(HubError):
    code, exit_code, http, message = "E-GATE-EXTREF-INVALID", 31, 422, "external_ref payload incomplete (system and reference are required)"


class GatePayloadInvalid(HubError):  # INC-08 addendum: payload of a Zone H action is malformed (not an authorisation failure)
    code, exit_code, http, message = "E-GATE-PAYLOAD-INVALID", 31, 422, "Zone H action payload is invalid"
