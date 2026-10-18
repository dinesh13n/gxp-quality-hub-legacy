"""INC-03 error codes (docs/12-specs/error-handling-spec.md, F09-3) as HubError subclasses.

hub/core/errors.py is frozen in INC-03 (add-only rule, TST-CO-05 c), so the new codes live here.
`http` is the status from the error catalogue (used by the route-authorisation layer; no server exists yet).
Exit codes: E-SEC-EXPOSURE-NOT-APPROVED = 9 as specified (collides with INC-02's E-CO-DENYLIST-IMPORT = 9,
recorded as RTD); every other exit code here is an INC-03 choice needing a Stage 12 addendum.
"""
from hub.core.errors import HubError


class AuthUnauthenticated(HubError):
    code, exit_code, http, message = "E-AUTH-UNAUTHENTICATED", 19, 401, "authentication required"


class AuthBadCredentials(HubError):
    code, exit_code, http, message = "E-AUTH-BAD-CREDENTIALS", 19, 401, "login failed"


class AuthSessionExpired(HubError):
    code, exit_code, http, message = "E-AUTH-SESSION-EXPIRED", 19, 401, "session expired"


class AuthLocked(HubError):
    code, exit_code, http, message = "E-AUTH-LOCKED", 19, 423, "account temporarily locked"


class AuthForbidden(HubError):
    code, exit_code, http, message = "E-AUTH-FORBIDDEN", 19, 403, "not permitted"


class ExposureNotApproved(HubError):
    code, exit_code, http, message = "E-SEC-EXPOSURE-NOT-APPROVED", 9, None, \
        "start-up refused: non-loopback bind needs exposure approval and TLS settings"


class AuditWriteFailed(HubError):
    code, exit_code, http, message = "E-SEC-AUDIT-WRITE-FAILED", 18, 500, "audit append failed; the change was rolled back"


class AuditTamperDetected(HubError):
    code, exit_code, http, message = "E-SEC-AUDIT-TAMPER-DETECTED", 17, 409, "verify-audit found a broken chain or anchor mismatch"


class SecretInAudit(HubError):  # INC-03 addendum (BEH-SEC-07: audit details never carry credentials)
    code, exit_code, http, message = "E-SEC-SECRET-IN-AUDIT", 18, 500, "credential-like key refused in audit details"


class ScanFindings(HubError):  # INC-03 addendum (gate G6)
    code, exit_code, http, message = "E-SEC-SCAN-FINDINGS", 16, None, "secret scan or deletion-path grep found something"


class ReleaseBlocked(HubError):  # INC-03 addendum (AC-CO-10/15)
    code, exit_code, http, message = "E-CO-RELEASE-BLOCKED", 20, None, "release cannot be marked ready: a gate is not 'pass'"


class BackupInvalid(HubError):  # INC-03 addendum (G7 / BEH-CO-06)
    code, exit_code, http, message = "E-STORE-BACKUP-INVALID", 21, None, "backup manifest missing or checksum mismatch"


class PasswordPolicy(HubError):  # INC-03 addendum (BEH-SEC-02 password length)
    code, exit_code, http, message = "E-AUTH-PASSWORD-POLICY", 2, None, "password does not meet the configured policy"


class StoreNotMigrated(HubError):  # INC-03 addendum
    code, exit_code, http, message = "E-STORE-NOT-MIGRATED", 22, None, "hub store is below the schema version this command needs"
