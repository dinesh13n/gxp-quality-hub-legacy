"""C11 loopback HTTP surface and server-rendered pages (ADR-014 option B, F02/F08/F09, INC-08). Package name `web` (not `http`) so that the
stdlib `http` package is never shadowed.

LOOPBACK ONLY: the listener binds 127.0.0.1 (hub.security.exposure.check_startup runs before any socket is created; a non-loopback bind
without approval + TLS settings exits 9). This package makes NO TLS-termination claim and is NOT an external exposure (OD-19, HAR-05).
The stdlib `http.server` is used for serving only (no outbound client, no third-party package). Human-only dispositions: every Zone H
action goes through one choke point (hub.gate.actions) that calls GateService; `disposition.mode` ships `none`. No AI/model call.
Synthetic, unvalidated.
"""
import hub

CODE_VERSION = "%s+inc08" % hub.__version__
