"""Structured log contract (observability-spec OBS-2, BEH-OBS-01, BEH-SEC-07; INC-07): JSON lines with a FIXED field whitelist.

Only the whitelisted fields can be logged; ids are pattern-checked (`object_ref` is an id, never free text), `error_code` must be an
E-* code, and no other key is ever written, so credentials, tokens, credential hashes, raw bodies, free text from Untrusted fields
and SQL cannot reach a log line by construction. `prohibited_findings` is the log scan of AC-OBS-04 (a belt-and-braces check of the
produced lines). Durations are measured with the injected clock (no `time` import in the core, TST-CO-13 b).
Sink: a callable taking one line (the CLI writes to stderr; stdout carries the command result - DEV-70).
"""
import contextlib
import json
import re

from hub.core.errors import HubError
from hub.security.canonical import parse

LEVELS = ("DEBUG", "INFO", "WARN", "ERROR")
EVENTS = ("http_request", "auth_login", "auth_denied", "zone_h_attempt", "decision_appended", "policy_changed", "intake_received",
          "intake_outcome", "run_started", "run_finished", "run_failed", "run_abandoned", "run_refused", "projection_verify",
          "audit_verify", "golden_compare", "config_loaded", "db_busy", "fts_engine_selected", "startup_selfcheck", "metric_computed")
FIELDS = ("ts", "level", "event", "correlation_id", "run_id", "actor", "actor_kind", "op_id", "outcome", "error_code", "duration_ms",
          "object_ref", "code_version", "config_version")
_ID = re.compile(r"^[A-Za-z0-9._:@#-]{1,80}$")
_CODE = re.compile(r"^E-[A-Z0-9-]{2,60}$")
_OUTCOMES = ("success", "denied", "error")
_DENIED = ("E-AUTH-", "E-GATE-")


def _id(v):
    return None if v is None else (v if isinstance(v, str) and _ID.match(v) else "redacted")


class Logger(object):
    def __init__(self, clock, sink=None, code_version=None, config_version=None):
        self.clock, self.sink, self.code_version, self.config_version = clock, sink, code_version, config_version

    def emit(self, event, level="INFO", correlation_id=None, run_id=None, actor=None, actor_kind=None, op_id=None, outcome=None,
             error_code=None, duration_ms=None, object_ref=None):
        if event not in EVENTS or level not in LEVELS:
            raise ValueError("unknown log event or level")
        rec = {"ts": self.clock(), "level": level, "event": event, "correlation_id": _id(correlation_id), "run_id": _id(run_id),
               "actor": _id(actor), "actor_kind": actor_kind if actor_kind in ("human", "service", "rule", "system") else None,
               "op_id": _id(op_id), "outcome": outcome if outcome in _OUTCOMES else None,
               "error_code": error_code if isinstance(error_code, str) and _CODE.match(error_code) else None,
               "duration_ms": None if duration_ms is None else round(float(duration_ms), 3), "object_ref": _id(object_ref),
               "code_version": _id(self.code_version), "config_version": _id(self.config_version)}
        if self.sink is not None:
            self.sink(json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return rec

    @contextlib.contextmanager
    def step(self, op_id, correlation_id, event="http_request", actor=None, actor_kind=None, object_ref=None, run_id=None):
        """One log line per completed operation with correlation id, op id, outcome, error code and duration (AC-OBS-01).
        The yielded dict may be updated (`run_id`, `object_ref`) before the line is written."""
        t0 = parse(self.clock())
        info = {"run_id": run_id, "object_ref": object_ref}
        outcome, code, level = "success", None, "INFO"
        try:
            yield info
        except HubError as e:
            outcome, code = ("denied" if e.code.startswith(_DENIED) else "error"), e.code
            level = "WARN" if outcome == "denied" else "ERROR"
            raise
        except BaseException:
            outcome, code, level = "error", "E-HUB-INTERNAL", "ERROR"
            raise
        finally:
            ms = (parse(self.clock()) - t0).total_seconds() * 1000.0
            self.emit(event, level, correlation_id, info.get("run_id"), actor, actor_kind, op_id, outcome, code, ms, info.get("object_ref"))


def envelope_with_correlation(err, correlation_id):
    """The error envelope carries the same correlation id as the log line and the audit record (AC-OBS-01)."""
    env = err.envelope()
    env["correlation_id"] = correlation_id
    return env


_PATTERNS = (
    ("credential_assignment", re.compile(r"(?i)(?:passw(?:or)?d|passwd|secret|api[_-]?key|authorization|cookie|bearer)\s*[\"']?\s*[:=]")),
    ("hex_digest", re.compile(r"\b[0-9a-f]{64}\b")),
    ("credential_hash_field", re.compile(r"(?i)pw_(?:hash|salt)|token_sha256|session_id")),
    ("markup_or_sql", re.compile(r"(?i)<script|union\s+select|;\s*drop\s|'\s*or\s+'1'\s*=\s*'1")),
)


def prohibited_findings(lines, literals=()):
    """Scan produced log lines (AC-OBS-04): known secrets / raw text passed as `literals`, credential-like keys, 64-hex digests (tokens,
    hashes), markup / SQL injection fixtures. Returns [{line, kind}]; the matched text is never echoed."""
    out = []
    for i, line in enumerate(lines):
        for kind, rx in _PATTERNS:
            if rx.search(line):
                out.append({"line": i, "kind": kind})
        for lit in literals:
            if lit and lit in line:
                out.append({"line": i, "kind": "literal"})
    return out
