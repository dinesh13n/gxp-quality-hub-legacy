---
stage: "12 — Spec-Driven Design"
artifact: "interface-contracts.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/component-model.md", "docs/10-architecture/integration-architecture.md", "docs/10-architecture/adrs/ADR-003-legacy-coexistence-pattern.md", "docs/10-architecture/adrs/ADR-010-run-orchestration-scheduling.md", "docs/10-architecture/adrs/ADR-015-deployment-topology.md", "docs/07-repo-assessment/dependency-map.md (DM-10..DM-18)", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Internal interface contracts: 8 dependency rules, signatures for 11 services and the Authenticator/Authorizer/Clock seams, repository swap-point, 8 read-only adapters, 7 CLI commands with exit codes, and the configuration interface. Signatures only; no implementation code.

## Findings
### IF-1 Layering and dependency rules (from component-model CM-2; made testable) [Inference: design]
1. `http` -> `services` -> `repositories`; no upward import (import-graph test).
2. Only `adapters/legacy` (C11) may open legacy files, and only `file:<path>?mode=ro` (`immutable=1` for baseline files).
3. No module imports `app.store` or any legacy module (`app.*`, `legacy_batch.*`).
4. Only `GateService` (C5) writes Zone H events; no import path from intake, runs, metrics, reviewer support, rules (static test, AC-GATE-11, AC-RUN-12).
5. Every write method of a service calls `AuditService.append()` inside the same transaction; failure aborts.
6. The `Untrusted` type cannot flow into decision parameters (type check + runtime guard, AC-INT-23).
7. No outbound network except the loopback gateway reader in `adapters/gateway` (AC-CO-12).
8. Pure functions (rule evaluation, canonicalisation, hashing, classification, percentile, fold) take time and randomness as parameters, never read a clock.

### IF-2 Service interfaces (language-neutral signatures; Python 3.10-compatible types) — NOT implementation
| Interface | Method | Inputs -> Output | Errors | Implements |
|---|---|---|---|---|
| `DecisionService` | `append(case_id, event_type, to_state, basis, evidence_refs, expected_seq, occurred_at?, actor)` | -> `DecisionEvent` | E-DEC-* | FR-DEC-01..05 |
| | `state(case_id, as_of?)` | -> `CaseState` | E-DEC-NOT-YET-EXISTS | FR-DEC-02 |
| | `events(case_id, from_seq, limit)` | -> `Page[DecisionEvent]` | | FR-DEC-01 |
| | `event_with_evidence(event_id, viewer)` | -> `EventWithEvidence` | | FR-DEC-04 |
| | `record_fact(case_id, fact_type, ...)` | -> `DecisionEvent` | | FR-DEC-06 |
| | `verify_projection()` | -> `ProjectionReport` | | FR-DEC-02 |
| `GateService` | `status()` | -> `GateStatus` | | FR-GATE-04/05 |
| | `evidence_pack(case_id, viewer)` | -> `EvidencePack` (read-only) | | FR-GATE-02 |
| | `execute(action_code, payload, principal, session, reauth_token, pack_hash?, authority_ref)` | -> `ZoneHResult` | E-GATE-* | FR-GATE-01/03/05 |
| | `override(flag_id, action, reason, replacement?, principal)` | -> `OverrideResult` | E-GATE-REASON-REQUIRED | FR-GATE-06 |
| `PolicyService` | `create_candidate(...)`, `get(policy_id, version)`, `list(filter)`, `elapsed(case_id)` | | E-POL-* | FR-POL-01/02 |
| `RuleService` | `evaluate(function, inputs, ruleset_ref?)` | -> `RuleResult` | E-POL-NO-ACTIVE-RULESET, E-POL-INPUT-INVALID | FR-POL-04/06 |
| | `divergence(inputs, ruleset_refs)` (R2) | -> `DivergenceReport` | | FR-POL-05 |
| `IntakeService` | `receive(source, envelope, run_id)` | -> `IntakeReceipt` | E-INT-ENVELOPE-INVALID | FR-INT-01..07 |
| | `resolve_conflict(raw_id, resolution, reason, principal)` | -> `IntakeItemView` | E-INT-* | FR-INT-03 |
| | `classify(item, config_version)` | pure -> `Classification` | | FR-INT-06 |
| `CrosswalkService` | `match(item, key_registry)` pure -> `MatchResult`; `link_human(...)`, `retract(...)`, `lookup(id, id_type?)`, `view(id)` (R2), `findings()` (R2) | | E-ID-* | FR-ID-01..04 |
| `RunService` | `start(job, trigger, principal, batch_size?)`, `checkpoint(run_id, ...)`, `finish(run_id, ...)`, `abandon_stale()` | | E-RUN-* | FR-RUN-01..03 |
| `MetricsService` | `time_to_close(clocks)`, `month_end_total(cutoff, denominator, source, allow_partial=False)`, `backlog(tag, as_of)`, `combine(values, op)`, `reproduce(value_id)`, `registry()` | | E-MET-* | FR-MET-01..07 |
| `ReviewService` | `exception_queue(filter, viewer)`, `rule_trace(case_id)`, `search(query, viewer)` (R2), `draft(...)` (R2) | | E-REV-* | FR-REV-01..04 |
| `AuditService` | `append(action, actor, object_ref, outcome, reason?, details)` (same transaction), `verify(anchor_path)`, `anchor(head)` | | E-SEC-* | FR-SEC-02 |
| `Authenticator` | `authenticate(credentials) -> Principal`, `create_session(principal)`, `reauth(principal, secret)`, `revoke(session)` | | E-AUTH-* | FR-SEC-01 |
| `Authorizer` | `check(principal, permission, object?) -> Decision` (deny by default) | | E-AUTH-FORBIDDEN | FR-SEC-01 |
| `Clock` | `now_utc()` injected into services; fixed clock in tests | | | PNFR-17 |

### IF-3 Repository interfaces (swap point for PostgreSQL, ADR-004)
`EventStore` (insert-only append, read by case/seq/time), `ProjectionStore`, `PolicyStore`, `IntakeStore`, `CrosswalkStore`, `RunStore`, `MetricStore`, `AuditStore`. Each exposes **no update or delete** for retained entities; a conformance test suite (same tests, two backends) is the exit criterion if ADR-004's PostgreSQL trigger fires.

### IF-4 Adapters (C11 legacy and external sources) — all read-only
| Adapter | Source | Contract | Notes |
|---|---|---|---|
| `LegacyCasesReader` | `data/legacy.sqlite3` `cases`, `events` | yields `LegacyCase`, `LegacyEvent`; no writes | baseline sha256 prefix c254649f57e2; used for CASE_IMPORTED backfill and goldens |
| `LegacyFeedReader` | `partner_feeds` | yields rows with `feed_id, partner, schema_rev, source_ts, ingest_ts, ref_id, record_kind, raw_json` | ignores `processing_status` as truth (kept as `legacy_status` attribute) |
| `SourceMessagesReader` | `source_messages` | 15 rows `{id, source, received_at, body}` | contract check against `integration/source-contract-v1.json` |
| `GatewayReader` | HTTP loopback `services/source_gateway` | `GET` with paging; schemes http/https only; timeout 5 s; retries per config | the only network use |
| `VendorCsvReader` | CSV file path argument | header-name parsing; `amount` as text + Decimal | never positional |
| `DocumentReader` | `data/source_documents.jsonl`, archive `.eml`/`.html` | immutable `(doc_id, version)` rows; quoted-printable decoding; HTML tag/script stripping to text | R2 |
| `EnterpriseEvidenceReader` | `enterprise_legacy.sqlite3` | read-only | DC-08 |
| `RuleSourceLoader` | `app/legacy_logic.py` semantics, `legacy_js/legacy_policy.js`, `contracts/decision-policies-archive.json`, `legacy_batch/shift_reconciliation.py` | produces the three as-found `rule-set` objects; **does not import or execute legacy code**: logic is transcribed as data and proven equal by golden tests | avoids importing `app.*` (rule 3) |

### IF-5 Command-line interface (`hub`) [Inference: ADR-010]
| Command | Purpose | Auth | Exit codes |
|---|---|---|---|
| `hub run <job> [--trigger manual|scheduled] [--batch-size N] [--until-empty]` | run a job (F06) | service/role token or local operator identity | 0 ok; 2 refused; 3 failed |
| `hub verify-audit [--anchor PATH]` | verify chain | operator | 0 ok; 4 tamper detected |
| `hub verify-projection` | recompute case_state | operator | 0 ok; 5 mismatch |
| `hub golden-compare [--workdir PATH]` | golden harness (F10) | operator | 0 clean; 6 unapproved differences; 7 not sandbox |
| `hub user create|disable|set-role|rotate-token` | offline user administration (no web bootstrap) | host operator with filesystem access | 0 ok |
| `hub selfcheck` | print Python/SQLite/FTS5 versions, config hash, gate status | operator | 0 ok; 8 runtime unsupported |
| `hub serve [--bind HOST:PORT]` | start HTTP service (default 127.0.0.1:8081) | operator | 0; 9 exposure not approved |
All commands write audit records for state-changing actions; no command exposes a Zone H action (Zone H is reachable only through the authenticated human HTTP/UI path).

### IF-6 Configuration interface
Config is one JSON file validated by `schemas/hub-config.schema.json` plus environment variables for secrets: `HUB_CONFIG` (path), `HUB_DB` (path to `hub.sqlite3`), `HUB_AUDIT_ANCHOR` (path), `HUB_SECRET_PEPPER` (optional, env only), `HUB_SANDBOX=1` (declares a sandbox working copy). Defaults = safe fresh install (empty holders, mode none, schedule disabled, loopback bind, data origin `synthetic`). Config load writes `CONFIG_LOADED` with the config hash. All paths are configurable; no repo-relative writes (fixes DM-10..12 for new code).

### IF-7 Legacy-facing contract (what must NOT change in R1)
`app/*.py`, `legacy_js/*`, `legacy_batch/*`, `legacy_java/*`, `sql/*`, `contracts/*`, `integration/*` and `services/source_gateway/*` are inputs, not edit targets, in R1 (BEH-CO-03). The `partner_feeds.processing_status` column remains legacy truth for legacy tools only.

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-IF-1 Rule sets are transcribed as data (not imported from legacy modules) so rule 3 holds; equality is proven by goldens CT-01..03, CT-13.
- A-12-IF-2 Exit codes and env var names are proposals.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-IF-1 Java/JDK availability for CT-11 cross-language goldens in CI (Docker/JDK absent on the device per Stage 7).

## Unresolved Issues
- Informal Python-flavoured signatures must be turned into typed protocols at Stage 15 without changing semantics.

## Residual Risks
- Transcribing three rule implementations risks subtle drift; goldens are the only guard (14/15 mutants survive the shipped suite).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
