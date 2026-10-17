---
stage: "0A — Pre-Flight Repository & System Orientation"
artifact: "security-observability-overview.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/server.py", "services/source_gateway/server.py", "app/store.py", ".gitignore", "environments/*.env.example", "Dockerfile", "compose.yaml", "ops/legacy_log_sampler.py", "docs/domain-assurance.md", "docs/operations-service-levels.md", "operations/runbook.md", "data/enterprise_legacy.sqlite3 (access_audit, retention_events)"]
supersedes: "none"
---
## Summary

Presence check only (quality deferred to Stage 7). **No authentication or authorisation mechanism exists** on either HTTP service. No secrets exist in the repo (none are needed). Logging is limited to the stdlib HTTP access log on stderr for the API; the gateway suppresses its logs. There is no metrics, tracing, alerting or audit-trail mechanism in code; audit/retention concepts exist only as synthetic data. The regulatory framing (21 CFR Part 11, GMP data integrity) is explicitly "not compliance certification".

## Findings

### Security presence

| ID | Control | Present? | Evidence | Class | Confidence |
|---|---|---|---|---|---|
| SO-01 | Authentication (API :8080, gateway :8090) | **No** — no header/token checks in any handler | `app/server.py` L11-60; gateway L11-40 | [Verified Fact] | High |
| SO-02 | Authorisation / RBAC / tenant scoping | **No** — all rows of all tables returned to any caller; `access_level` on documents and `tenant` columns are not enforced anywhere | code review; `source_documents.jsonl` | [Verified Fact] | High |
| SO-03 | Transport security (TLS) | **No** — plain HTTP; bind `0.0.0.0` in Docker / staging / production-like env examples | `Dockerfile` L4; `environments/*.env.example` | [Verified Fact] | High |
| SO-04 | Secrets handling | No secrets in repo (grep for password/secret/token/api_key/credential/bearer: 0 matches); `.env` is git-ignored; env examples contain only host/port/log level | `.gitignore` L4; `environments/` | [Verified Fact] | High |
| SO-05 | Input handling | Pagination parsed with `int()` + clamps; table names allow-listed; parameterised values; JSON payloads stored raw; no schema validation of inbound contracts (`source-contract-v1.json` unused) | `app/server.py` L24-31, L46; `app/integration.py` | [Verified Fact] | High |
| SO-06 | Untrusted content | Instruction-like strings embedded in feeds/documents/events (see `data-flow-overview.md` DF-08); docs state feeds "must not be treated as trusted instructions" | `docs/partner-feed-operations.md` L13; README "Domain expansion" | [Verified Fact] | High |
| SO-07 | Container hardening | Runs as root (no `USER`), unpinned `python:3.12-slim`, copies whole build context (`.dockerignore` excludes only `__pycache__`, `*.pyc`, `.git`) | `Dockerfile`; `.dockerignore` | [Verified Fact] | High |
| SO-08 | Dependency / supply-chain | No third-party Python deps; no SCA tooling; CI uses tag-pinned actions (`@v4`, `@v5`), not SHA-pinned | `pyproject.toml`; `verify.yml` | [Verified Fact] | High |
| SO-09 | Audit trail of user actions | **No** mechanism in code. `access_audit` (4,167 rows, 220 with empty `access_reason`) and `state_history` exist only as generated data in `enterprise_legacy.sqlite3`; `partner_feeds` status is overwritten in place with no history | `app/enterprise_legacy.py` L22, L50; `app/partner_feeds.py` L70 | [Verified Fact] | High |
| SO-10 | Electronic records / signatures (Part 11 concepts) | Named as policy concepts (`qa_signature`, `electronic_record_retention`) and in docs; no e-signature, record locking or retention enforcement code | `domain-profile.json` `policies`; `docs/domain-assurance.md` L5 | [Verified Fact] | High |
| SO-11 | Data integrity checks | SQLite `PRAGMA foreign_keys=ON`, `integrity_check`/`foreign_key_check` in scripts; idempotency keys in bridge and file import | `app/store.py` L10; `scripts/offline_inventory.py`; `app/gateway_bridge.py` L22-25 | [Verified Fact] | High |

### Observability presence

| ID | Signal | Present? | Evidence | Class | Confidence |
|---|---|---|---|---|---|
| SO-12 | Logging | API: stdlib access log to stderr (`log_message` override, L61). Gateway: **disabled** (`log_message: pass`, L41). Batch/CLI jobs: JSON result to stdout only. No logging framework/config; `LOG_LEVEL` env var unused | cited lines; grep | [Verified Fact] | High |
| SO-13 | Structured logs | Only synthetic sample generator `ops/legacy_log_sampler.py` (prints 300 JSON lines with `correlation_id`, `latency_ms`, `level`) — not wired to any component | `ops/legacy_log_sampler.py` | [Verified Fact] | High |
| SO-14 | Metrics | No telemetry metrics. `/api/metrics` returns **business** aggregates (case totals, status counts, operating-cost table) | `app/server.py` L16-21 | [Verified Fact] | High |
| SO-15 | Tracing / correlation | None in code. `trace_id`/`correlation_id` fields exist in lake event data only | `app/historical_fixture.py` L49 | [Verified Fact] | High |
| SO-16 | Health checks | `/health` on both services (static `ok`, no dependency check); Compose healthchecks call them | `app/server.py` L13; gateway L13; `compose.yaml` L13-18, L28-32 | [Verified Fact] | High |
| SO-17 | Alerting / SLOs | None implemented. Archived targets (99.5% availability, reconciliation before 06:00, feed accepted within 4 h, RTO 8 h, RPO 24 h) are "historical working targets, not measured guarantees" | `docs/operations-service-levels.md` | [Verified Fact] | High |
| SO-18 | Backup / recovery | No backup job; runbook recovery = regenerate data (`python -m app.generate --reset`) which **destroys** current data | `operations/runbook.md` L3 | [Verified Fact] | High |

## Evidence References

As cited; grep results for credential keywords and `LOG_LEVEL`; read-only queries on `access_audit`.

## Assumptions

- A-08: The engagement treats GxP / Part 11 statements as framing for a training simulator, not as a compliance obligation on this codebase. Confirm — owner: Engagement lead (Dinesh Naik), Stage 0B / 25.

## Unknowns

- U-15 data classification; U-22 intended identity provider / user roles; U-23 whether stated RTO/RPO are still business targets.

## Unresolved Issues

- No mechanism exists to evidence who viewed or changed what — relevant to Stage 24/25 and to any automation proposal.

## Residual Risks

- R-04 unauthenticated access to all data; R-14 no operational telemetry; R-09 untrusted content. See `initial-risk-register.md`.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial Stage 0A discovery draft (read-only inspection of commit `b126c56`). |
