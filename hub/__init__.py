"""GxP Quality Hub - new modules built beside the legacy estate (Stage 15, strangler pattern, ADR-003).

INC-02 skeleton: runtime self-check, sandbox / No-AI / egress guards, Untrusted text type, zero-model-call
tripwire, read-only legacy adapters, deviation register and `golden-compare`.

The product is No-AI (OD-08, ADR-002): standard library only; no model, LLM or ML dependency; no outbound
network except loopback. Everything here is synthetic and unvalidated against any organisation.
Run as `python -m hub <command>` (no pyproject.toml change, OD-14 / OD-S12-12).

Keep this file importable on old interpreters (no 3.10-only syntax) so the runtime self-check can report
E-CO-RUNTIME-UNSUPPORTED instead of failing with a SyntaxError.
"""
__version__ = "0.2.0-inc02"
STAGE = "15 INC-02"
