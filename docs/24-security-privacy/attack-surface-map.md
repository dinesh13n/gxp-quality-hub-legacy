---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "attack-surface-map.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/web/app.py", "hub/web/server.py", "hub/security/*.py", "hub/gate/*.py", "hub/r2/protection.py", "docs/12-specs/security-spec.md", "docs/10-architecture/security-architecture.md", "docs/11-data-context/metadata-model.md", "docs/16-repo-validation/security-scan-summary.md", "docs/23-human-control/", "docs/25-governance/", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
Every way in, with what is exposed, to whom, and what stops misuse. 7 entry-point families: the loopback HTTP surface (58 routes), 12 operator CLIs, 5 environment variables, 1 configuration file, files read by adapters, the gateway client, and the build / test path. The HTTP surface is the only network-reachable one and is loopback only.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AS-1 Network surface [Verified Fact]
| ID | Entry | Reach | Auth | Notes |
|---|---|---|---|---|
| AS-01 | `GET/POST /api/v2/...` 48 operations | 127.0.0.1 only; non-loopback peers dropped before a byte is read (`verify_request`) | deny by default; session cookie or Bearer (`svc_` service token); role per route | `/healthz` and login are public |
| AS-02 | `/ui/...` 10 routes (server-rendered) | same | session cookie; CSRF token on posts | login page public |
| AS-03 | Not offered | no TLS, no CORS, no proxy, no websocket, no file upload, no `Transfer-Encoding` | n/a | any bind other than loopback is refused, even with approval and TLS keys (S03..S05 of Stage 23) |
### AS-2 Local surfaces [Verified Fact]
| ID | Entry | Who | Notes |
|---|---|---|---|
| AS-10 | `python -m hub.admin / control / web / decision / intake / metrics / policy / r2 / runs / search / security` (11 modules plus `python -m hub`) | host operator | egress guard installed; runtime floor; kill switch; CONFIG_LOADED audited |
| AS-11 | environment: `HUB_OPERATOR`, `HUB_NEW_USER_PASSWORD`, `HUB_RUN_PASSWORD`, `HUB_BACKUP_ROOT`, `HUB_WORKTREE_ROOT` (+ `HUB_ANCHOR_SEAL_KEY`, new, optional) | operator | secrets live in the environment only; never in config / audit / log |
| AS-12 | config file (JSON) | operator | validated at load; non-default decision flags need an `approval_ref` |
| AS-13 | SQLite store + anchor file (+ optional seal file) | OS file permissions | not encrypted at rest (Unknown whether required) |
### AS-3 Inbound data [Verified Fact]
| ID | Source | Trust | Handling |
|---|---|---|---|
| AS-20 | partner feed rows (8,567 shipped deliveries; 86 carry instruction-like text) | UNTRUSTED | contract check, quarantine outcomes, notes typed `Untrusted`, byte-exact `raw_intake` |
| AS-21 | documents (1,200) and archive items (420) | UNTRUSTED text; `access_level` decides visibility | derived corpus, escape on output |
| AS-22 | gateway JSON and vendor CSV | UNTRUSTED | `hub/adapters/` only (the one place an HTTP client may be imported); scheme / loopback allow-list; no redirects |
| AS-23 | reviewer free text (reasons, notes) | untrusted | stored as typed, escaped on output |
### AS-4 Build path [Verified Fact]
No third-party dependency; no CI for hub; tests run from a sandbox copy only; AI coding assistant used for development (CP-10).
### AS-5 Changes made by Stage 24 [Verified Fact]
No new network surface. Added: `python -m hub.security` (read-only except the opt-in `seal`), the `X-Hub-Reason` request header (read, never echoed), and `; Secure` on the session cookie when TLS settings exist.

## Evidence References
`hub/security/route_registry.json`, `hub/web/ui_routes.json`, `hub/web/server.py`, `hub/security/exposure.py`, `hub/guards/egress.py`, `hub/guards/no_ai.py`; tests TST-SEC-01, TST-SEC-16, Stage 23 S03..S05, Stage 24 S24..S26, S30, S31, S40, S41.

## Assumptions
- A-S24-AS-1 The operator account and the host are not an attack surface in scope (see threat model TM-3).

## Unknowns
- U-S24-AS-1 File-system permissions of the real deployment (anchor, seal, store, config).
- U-S24-AS-2 Whether a reverse proxy would ever front the hub (RTD-77).

## Unresolved Issues
- Exposure beyond loopback remains a Stage 27 / HAR-05 decision.

## Residual Risks
RS-01, RS-04, RS-13.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
