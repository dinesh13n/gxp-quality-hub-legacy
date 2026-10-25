---
stage: "27 — Production Hardening"
artifact: "runtime-hardening.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/web/server.py", "hub/web/app.py", "hub/web/ratelimit.py", "hub/security/exposure.py", "hub/config.py", "Dockerfile", "compose.yaml", "environments/", ".github/workflows/verify.yml", "ci/hub-hardening.yml", "tests/hub/test_tst_hub_stg26_resilience.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW: nothing here is an approval and no risk is accepted. Every acceptance, every decision and every sign-off named below is Dinesh Naik's (Engagement lead) and is not recorded by this stage. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
The hub listens on loopback only (127.0.0.1:8081), refuses a non-loopback bind even with an approval reference, answers every response with the security headers, caps a request body at 1 MiB, and now also has a 10 s per-connection read timeout, a per-peer limiter for refused requests, a distinct 503 for a store fault and strict configuration (unknown keys and unreadable files are refused with a code). The legacy container files do not meet the same bar (root user, 0.0.0.0 binds, unpinned image) but they are frozen until Stage 30, so the findings are recorded and not changed.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RH-1 Exposure (ports and endpoints) [Verified Fact]
| Surface | State | Evidence |
|---|---|---|
| hub HTTP listener | `127.0.0.1:8081` default; `network.bind` non-loopback refused unless `exposure_approved` + approval ref + TLS files, and the server refuses it anyway | `hub/security/exposure.py`, `hub/web/server.py` (HAR-05), S23 S03 / S04 / S05 |
| hub endpoints | 48 API operations + UI routes, deny by default (unregistered 403), roles per route | S26 A01 |
| unauthenticated routes | `/healthz`, login; a flood is rate limited (BC-07) | S27 L03 |
| legacy app (`app/`) | port 8080 / 8090 bound `0.0.0.0` in `compose.yaml` and `Dockerfile` | legacy, unchanged |

### RH-2 Stage 27 runtime changes [Verified Fact]
| Control | Before | After | Test | Mutant |
|---|---|---|---|---|
| read timeout | none (a short body held a thread) | `READ_TIMEOUT_SECONDS = 10`; 408 E-REQ-TIMEOUT; client socket errors are quiet | S26 C06 (1 s timeout in the test) | X6 killed |
| store fault | generic 500 for everything | `sqlite3.OperationalError` / `DatabaseError` = 503 E-STORE-UNAVAILABLE, also `/healthz`; `IntegrityError`, `ProgrammingError` etc. stay 500 | S26 C01, S27 F07 | X5 killed |
| flood of refused requests | 1 audit row each (81 bytes per request) | 429 after 100 per peer per 60 s, no store open, no audit row, `Retry-After` | S26 A07, S27 L01..L04 | X7 killed |
| configuration | unknown keys ignored, traceback on a bad file | closed key set, E-CFG-INVALID exit 2 | S26 C02, S27 F04 / F05 | X4 killed |
| malformed JSON text | lone surrogate = 500 | 400 | S26 B08, S27 F03 | X3 killed |
| file modes | umask | owner-only (BC-09) | S27 H04 | - |
| request complexity | `WebApp._dispatch` complexity 22 | split into `_read_body`, `_session` (same behaviour; no test had to change for it) | S27 S01 | - |

### RH-3 Controls that were already in place and re-verified [Verified Fact]
Security headers on every response (`X-Content-Type-Options: nosniff`, `Content-Security-Policy: default-src 'self'`, `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`), 1 MiB body limit (413), `Transfer-Encoding` refused, 14 transport anomalies handled (S26 C06), the egress guard (non-loopback connect refused in tests), the kill switch `hub.kill` (E-HUB-KILLED, exit 3), runtime floor check (`python -m hub selfcheck`).

### RH-4 Legacy container and environment files (read, not changed) [Verified Fact; severity Inference]
| Finding | Evidence | Impact | Risk | Confidence |
|---|---|---|---|---|
| image runs as root (no `USER`) | `Dockerfile` | a flaw in the legacy app has root inside the container | Medium | High |
| base image `python:3.12-slim` by tag, not digest | `Dockerfile` | a rebuild can change the image silently | Low-Medium | High |
| binds `HOST=0.0.0.0`, ports published on every interface | `Dockerfile`, `compose.yaml`, `environments/production-like.env.example` | exposure beyond loopback if run as shipped (the legacy app has no TLS and its own auth model) | High if exposed, Low on a closed laptop | High |
| no resource limits, read-only root, `no-new-privileges` or capability drop | `compose.yaml` | a runaway process can exhaust the host | Low-Medium | High |
| healthcheck uses `urllib.request` | `compose.yaml` | none for the hub (legacy only) | Info | High |
| `LOG_LEVEL=DEBUG` in `environments/dev.env.example` | file | dev only | Info | High |
These files are legacy paths (TST-CO-05 a) and Dockerfile / Compose / env profiles are HAR-07 items. Stage 27 changes none; D-27-06 asks Dinesh whether Stage 30 hardens them.

### RH-5 Not built [Verified Fact: absent]
No container recipe for the hub itself, no TLS in the product (RS-01, loopback only), no process supervisor, no resource limits, no log shipping. The hub is run as `python -m hub.web` from a checked-out tree.

## Evidence References
- `hub/web/server.py`, `hub/web/app.py`, `hub/config.py`, `hub/web/ratelimit.py`
- `tests/hub/test_tst_hub_stg26_resilience.py` (C01, C02, C06), `test_tst_hub_stg27_findings.py`, `test_tst_hub_stg27_limiter.py`
- `Dockerfile`, `compose.yaml`, `environments/*.env.example` (read only)
- `docs/27-hardening/evidence/runtime-selfcheck.json`

## Assumptions
- A-27-06 10 s read timeout.
- A-27-04 limiter defaults.
- The legacy container files describe how the legacy app is run for the exercise; whether anyone runs them outside a laptop is unknown.

## Unknowns
- U-27-09 Throughput and latency under the limiter and the timeout: no measurement beyond the Stage 26 / NFR tests (class C evidence).
- U-27-10 How the hub will be hosted (no hosting decision exists).

## Unresolved Issues
- Hub container recipe, TLS termination, supervision: not built (Stage 29 / 30 and DQ-S24-03).
- D-27-06 legacy container hardening.

## Residual Risks
- Plaintext HTTP if anyone ever binds beyond loopback (the code refuses; RS-01).
- The legacy compose file exposes ports on all interfaces if started as shipped.
- A slow-body client now costs at most 10 s of a thread, not unbounded; a slow-read client of a large response is not covered by a write timeout [Inference].

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 27 BUILD). |
