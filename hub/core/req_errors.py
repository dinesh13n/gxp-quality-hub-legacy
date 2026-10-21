"""E-REQ-INVALID (Stage 20 DW-06; S16-D06 / AC-04): the request-shape error that the Zone H choke point (hub.gate.actions) raises. It was
defined in the HTTP layer (hub/web/errors.py), which made a domain package import hub.web; it now lives in the core and hub/web/errors.py
re-exports the SAME class, so every `except` / isinstance check and the HTTP mapping are unchanged."""
from hub.core.errors import HubError


class ReqInvalid(HubError):
    code, exit_code, http, message = "E-REQ-INVALID", 31, 400, "malformed request"
