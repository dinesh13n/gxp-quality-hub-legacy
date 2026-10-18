"""Hub error codes (docs/12-specs/error-handling-spec.md, F10-5) and CLI exit codes.

Exit codes 6, 7 and 8 are specified (E-CO-UNAPPROVED-DEVIATION, E-CO-NOT-SANDBOX, E-CO-RUNTIME-UNSUPPORTED).
All other exit codes and the codes marked "INC-02 addendum" are INC-02 choices that need a Stage 12 spec
addendum (recorded in docs/15-modernization/remaining-technical-debt.md). Messages are fixed per code;
user/legacy text only ever goes into `details` (error-handling-spec rule 6).
"""

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_KILLED = 3


class HubError(Exception):
    code = "E-HUB-INTERNAL"
    exit_code = 1
    message = "internal error"

    def __init__(self, details=None):
        self.details = details
        Exception.__init__(self, "%s: %s%s" % (self.code, self.message, (" (%s)" % (details,)) if details else ""))

    def envelope(self):
        return {"code": self.code, "message": self.message, "details": self.details}


class UnapprovedDeviation(HubError):
    code, exit_code, message = "E-CO-UNAPPROVED-DEVIATION", 6, "golden-compare found an unapproved difference"


class NotSandbox(HubError):
    code, exit_code, message = "E-CO-NOT-SANDBOX", 7, "refused: working data inside the original repository or backup"


class RuntimeUnsupported(HubError):
    code, exit_code, message = "E-CO-RUNTIME-UNSUPPORTED", 8, "Python/SQLite below the supported floor"


class DenylistImport(HubError):
    code, exit_code, message = "E-CO-DENYLIST-IMPORT", 9, "deny-listed dependency or import found"


class LegacyWriteRefused(HubError):
    code, exit_code, message = "E-CO-LEGACY-WRITE-REFUSED", 10, "write to a legacy store refused"


class EgressAttempt(HubError):
    code, exit_code, message = "E-CO-EGRESS-ATTEMPT", 11, "outbound connection attempt detected"


class UntrustedUse(HubError):
    code, exit_code, message = "E-INT-UNTRUSTED-USE", 12, "Untrusted value reached a decision parameter"


class LegacySchemaDrift(HubError):  # INC-02 addendum (adapter-strategy AS-2 rule 4)
    code, exit_code, message = "E-CO-LEGACY-SCHEMA-DRIFT", 13, "legacy schema differs from the pinned schema"


class FixtureMismatch(HubError):  # INC-02 addendum; same meaning as INC-01 harness E-FX-HASH
    code, exit_code, message = "E-FX-HASH", 2, "legacy baseline file does not match the pinned sha256"


class TripwireTripped(HubError):  # INC-02 addendum (observability-spec BEH-OBS-06 / gate G5)
    code, exit_code, message = "E-OBS-TRIPWIRE", 14, "a zero-tripwire metric is non-zero"


class ConfigInvalid(HubError):  # INC-02 addendum
    code, exit_code, message = "E-CFG-INVALID", 2, "configuration value not allowed"


class HubKilled(HubError):  # INC-02 addendum (feature-flag-plan `hub.kill`)
    code, exit_code, message = "E-HUB-KILLED", 3, "hub.kill is set; command refused"


class MigrationDrift(HubError):  # INC-02 addendum
    code, exit_code, message = "E-STORE-MIGRATION-DRIFT", 15, "an applied migration file has changed"
