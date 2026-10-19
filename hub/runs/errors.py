"""INC-07 run error codes (docs/12-specs/error-handling-spec.md, F06-4) as HubError subclasses.

hub/core/errors.py is frozen (add-only rule, TST-CO-05 c). `http` is the catalogue status. The spec gives no exit code for the E-RUN-*
family: INC-07 chooses 29 (INC-06 used 28; E-MET-* uses 30) - a Stage 12 addendum is needed (RTD-58).
"""
from hub.core.errors import HubError


class RunScheduleDisabled(HubError):
    code, exit_code, http, message = "E-RUN-SCHEDULE-DISABLED", 29, 409, "scheduled trigger refused: schedule.enabled is false"


class RunAlreadyRunning(HubError):
    code, exit_code, http, message = "E-RUN-ALREADY-RUNNING", 29, 409, "another run of this job holds the lock"


class RunTotalsMismatch(HubError):
    code, exit_code, http, message = "E-RUN-TOTALS-MISMATCH", 29, 500, "run totals do not reconcile with the outcome rows"


class RunUnknownJob(HubError):
    code, exit_code, http, message = "E-RUN-UNKNOWN-JOB", 29, 404, "job is not in the closed catalogue"


class RunCheckpointInvalid(HubError):
    code, exit_code, http, message = "E-RUN-CHECKPOINT-INVALID", 29, 409, "checkpoint is corrupt or unknown"


class RunNotFound(HubError):  # INC-07 addendum (OP-RUN-03 reuses E-RUN-UNKNOWN-JOB in the spec; a separate class keeps the meaning clear)
    code, exit_code, http, message = "E-RUN-UNKNOWN-JOB", 29, 404, "unknown run id"
