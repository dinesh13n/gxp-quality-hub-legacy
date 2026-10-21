---
stage: "21 — Enterprise Integration"
artifact: "authentication-map.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["services/source_gateway/server.py", "app/gateway_bridge.py", "hub/adapters/gateway_client.py (check_url)", "hub/adapters/legacy_sqlite.py", "hub/security/auth.py, authz.py, zone_h.py, exposure.py, route_registry.json", "hub/web/server.py (bind_address)", "hub/intake/service.py (set_binding, resolve_conflict)", "docs/20-application/access-control-implementation.md", "docs/12-specs/security-spec.md", "tests/hub/test_tst_int_17_29_match_untrusted_sources.py TST-INT-25", "tests/hub/test_inc06_supplementary.py S04", "tests/hub/test_tst_hub_stg21_integration.py S03"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. No credential, key, certificate or service account exists for any integration; nothing here is a design for real enterprise authentication (that is Stage 24 and needs a real system).**

## Summary
On the **consumed** side there is no authentication anywhere: the shipped gateway stub accepts any loopback GET, and the legacy databases and CSV are files. The hub compensates with **channel restriction instead of credentials**: loopback-only URLs refused before any connection (TST-INT-25), hash-pinned read-only snapshots (TST-CO-04), sandbox path guards; and it **sends no credential** (STG21 S03: no `Authorization`, `Cookie` or `Proxy-Authorization` header, no body). On the **provided** side the hub HTTP API authenticates sessions and authorises per route (deny by default) and binds loopback only; integration-relevant decisions (contract binding, conflict resolution) need a human session, and the binding change additionally needs a Zone H holder, of which there are none.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AM-1 Consumed integrations
| INT | Counterpart authn | Hub authn sent | Compensating control | Authz on the hub side | Evidence | Tag |
|---|---|---|---|---|---|---|
| INT-01/02/03/04/05 (SQLite) | none (file) | n/a | host filesystem access; per-run snapshot; `mode=ro&immutable=1`; write-refusing authorizer; sha256 + schema pin; working-tree source refused | host operator runs `hub.intake` / jobs | TST-CO-04 a-f | [Verified Fact] |
| INT-06 (gateway stub) | none (`server.py` has no auth check) | none: no Authorization / Cookie / body | URL scheme http(s) only and host loopback only, checked BEFORE any connection; no proxy; redirects refused; egress guard in every hub process | operator CLI `gateway-pull`; scheduled jobs OFF | TST-INT-25, S03, INC06 S09, E21 (0 egress attempts) | [Verified Fact] |
| INT-07 (CSV) | none (file) | n/a | sandbox path guard on the legacy root; read `rb` | operator | TST-INT-27 | [Verified Fact] |
| INT-08..10 (rule data, documents, captures) | none (files) | n/a | MANIFEST / pin checks (AD-08), content treated as untrusted data (AD-07) | n/a | TST-CO-01/02, PNFR-13 | [Verified Fact] |

### AM-2 Provided integrations
| Surface | Authn | Authz | Integration-relevant operations | Evidence | Tag |
|---|---|---|---|---|---|
| INT-11 hub HTTP API | session token (256-bit, only sha256 stored), lockout, re-auth for Zone H | route registry, deny by default; roles; Zone H holder rule in one place (`hub/security/zone_h.py`) | intake item reads (reviewer / quality_lead / compliance / dispositioner), conflict resolution (human reviewer / quality_lead + reason) | TST-SEC-*, TST-GATE-*, STG20 S20/S21 | [Verified Fact] |
| INT-11 bind | n/a | non-loopback bind refused (E-SEC-EXPOSURE-NOT-APPROVED) | — | `hub/web/server.py` | [Verified Fact] |
| INT-12 hub CLI | host operator (OS account) | no role check beyond host access; CLI records no decision and cannot switch a binding | `ingest-legacy`, `gateway-pull`, `verify-replay`, `report` | `hub/intake/cli.py` docstring | [Verified Fact] |
| Contract binding change (ZH-10) | human session + fresh re-auth | holder in `zone_h.holders` (EMPTY) + authority_ref | `IntakeService.set_binding` | INC06 S04; E-GATE-NO-HOLDERS | [Verified Fact] |

### AM-3 Findings register
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| AUF-01 | The consumed gateway has no authentication; the hub relies on loopback-only reachability | `server.py`; TST-INT-25 | acceptable only while source and hub share a host; any real source needs mutual authentication | Medium | High | U-21-AU-1 (Stage 24) |
| AUF-02 | The hub never transmits a credential to a source | S03 | no credential leakage path exists today | Low | High | — |
| AUF-03 | Only a Zone H holder can enforce a contract; with holders empty, contract enforcement is impossible by design | INC06 S04 | OD-S12-11 options O2-O4 need a named holder first | Low | High | DQ-S21-01 |

## Evidence References
- As in the tables; `docs/20-application/access-control-implementation.md`.

## Assumptions
- A-21-AU-1 [Assumption] Host-level access control (who may run the CLI) is provided by the operating environment, as accepted for the CLI since INC-02. Confirm: Engagement lead (Dinesh Naik), Stage 24.

## Unknowns
- U-21-AU-1 Authentication scheme for any real upstream system (OAuth client credentials, mTLS, signed files, SFTP keys) - no real system exists; Engagement lead (Dinesh Naik), Stage 24.
- U-21-AU-2 Real Zone H holders (OD-S12-06) - unchanged Unknown.

## Unresolved Issues
- None that Stage 21 can resolve without a real system.

## Residual Risks
- RR-21-AU-1 A future non-loopback source would arrive without an authentication design (Medium; mitigated: the client refuses non-loopback hosts until a code change is reviewed).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
