---
stage: "16 — Validate the Good Repo"
artifact: "architecture-conformance-report.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/10-architecture/adrs/ADR-001..ADR-018 (all PROPOSED / DRAFT)", "docs/10-architecture/component-model.md (C1..C11)", "docs/10-architecture/target-architecture.md, security-architecture.md, deployment-architecture.md", "docs/12-specs/system-spec.md", "docs/16-repo-validation/evidence/package-graph.txt (AST import graph of hub/)", "docs/16-repo-validation/evidence/obs-laptop.json", "hub/ (163 files, 13,994 lines)", "git diff --name-status baseline-as-found main", "docs/15-modernization/transformation-log.md (DEV-28, DEV-41, DEV-51, DEV-75, DEV-90, DEV-101)", "docs/15-modernization/remaining-technical-debt.md (RTD-25/37/46/51/60/81)"]
supersedes: "none"
---
**Label: synthetic repository. The architecture baseline is itself DRAFT (all ADRs PROPOSED except the No-AI decision OD-08); "conforms" means "conforms to the proposed architecture", not to an approved one.**

## Summary
The built `hub/` conforms to the Stage 10 target architecture on every **structural safety** decision: modular monolith beside the legacy estate with additive changes only (ADR-001/003), structural No-AI enforcement (ADR-002), append-only SQLite stores with hash-chained audit and decision events (ADR-004/005), no adopted rule set / policy / schedule / holder (ADR-006/007/010), exact-key crosswalk (ADR-009), Decimal metrics with definition tags (ADR-011), FTS5 search off by default (ADR-012), loopback-only single host (ADR-015). Deviations are **in how it is put together**: domain components import the HTTP layer's package (layer leak), package-level import cycles, seven migration runners instead of one, three copies of the Zone H holder check, two server entry points, and runtime 3.10 instead of ADR-018's 3.12. None blocks Stage 17; all are recorded as debt with owners.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AC-1 ADR conformance
| ADR | Decision (proposed) | Observed at 2c63b07 | Verdict | Tag |
|---|---|---|---|---|
| 001 | Modular monolith beside legacy | `hub/` package, 23 sub-packages; 688 additions, 0 legacy edits since `baseline-as-found` | Conforms | [Verified Fact] |
| 002 | No-AI enforced structurally | deny-list (TST-CO-11), egress guard + tripwires `model_calls_total = 0` (TST-CO-12, E05..E09), stdlib only; CI wiring missing (RTD-14) | Conforms (manual gate) | [Verified Fact] |
| 003 | RO adapters, shadow, no dual-write | legacy DB sha `c254649f…` unchanged after full shadow intake; legacy `processing_status` untouched; `sqlite3.connect` only in `hub/store/db.py`, `hub/adapters/legacy_sqlite.py`, `hub/runtime.py` (`:memory:` probe) | Conforms | [Verified Fact] |
| 004 | Append-only events in SQLite | decision events hash-chained per case; projection check `mismatches 0` after backfill of 125 | Conforms | [Verified Fact] |
| 005 | Hash-chained audit | `verify-audit` rc 0 after the observation run; anchor is an unsigned local file (RTD-29) | Conforms; strength open | [Verified Fact] |
| 006 | Disposition gate, recording modes | mode `none`, holders `[]`; every Zone H path through one choke point (H1 KILLED) | Conforms | [Verified Fact] |
| 007 | Versioned policies, table-driven rules, no adopted defaults | 3 as-found sets loaded **inactive**; evaluate without ref -> `E-POL-NO-ACTIVE-RULESET`; parity with legacy code (TST-CO-03 3/3, 105 boundary cases) | Conforms | [Verified Fact] |
| 008 | Intake: raw append-only, idempotency, quarantine | 10,983 raw items; replays NOOP; quarantine with reasons; contract `record_only` | Conforms | [Verified Fact] |
| 009 | Explicit crosswalk, no inference | 168 exact-key links; no fuzzy match (AC-ID-04) | Conforms | [Verified Fact] |
| 010 | CLI jobs + run records; schedule held | scheduler OFF; switch only by Zone H | Conforms | [Verified Fact] |
| 011 | One query path, definition tags, exact decimals | month-end 622826.44 Decimal; tags null because nothing adopted | Conforms | [Verified Fact] |
| 012 | FTS5 keyword search (R2), no semantic search | FTS5 + trigram when available, identical fallback, `search.fts` off | Conforms | [Verified Fact] |
| 013 | Local authn + RBAC | PBKDF2, lockout, deny-by-default registry; values proposed (RTD-26) | Conforms; values open | [Verified Fact] |
| 014 | Layered HTTP API + server-rendered pages, stdlib | stdlib `ThreadingHTTPServer`, one dispatcher; **domain packages import `hub.web`** (AC-2); two entry points (`hub.web serve`, `hub.r2 serve`, RTD-81) | Partial | [Verified Fact] |
| 015 | Single host, loopback, file store | loopback bind + peer filter; the INC-08 "loopback even with approval" check is untested (SS-08) | Conforms; test gap | [Verified Fact] |
| 016 | Structured logs + run records + metrics tables | JSON logs, run records, `obs_metric`; several observability metrics not exported (RTD-60) | Partial | [Verified Fact] |
| 017 | Buy vs build | not evaluated (OPD-10 open) | Not assessable | [Unknown] |
| 018 | Python 3.12 stdlib | floor 3.10 / SQLite 3.37 (OD-14, OD-S12-12); reference runtime 3.10.12 is end-of-life (DS-03) | **Deviates** (recorded decision OD-14, still open at OD-S12-12) | [Verified Fact] |

### AC-2 Component boundaries (component-model.md C1..C11) - static import graph
[Verified Fact] (`evidence/package-graph.txt`): no `hub` module imports any legacy package (`app`, `legacy_batch`, `services`, `scripts`, `ops`, `integration`). Network modules: `socket` only in `hub/guards/egress.py`, `http.server` only in `hub/web/server.py`, `urllib` in the gateway client / adapters / web wire code.
[Verified Fact] Module-level package cycles: 6 two-package cycles (`ops<->store`, `gate<->web`, `gate<->runs`, `r2<->search`, `review<->web`, `decision<->gate`) and 10 three-package cycles (e.g. `guards->obs->security->guards`); further cycles exist through function-level imports.
[Verified Fact] Layer leak: C5 gate (`hub/gate/actions.py`, `dispositions.py`), C10 review (`hub/review/service.py`) and search (`hub/search/schema.py`) import `hub.web` (C1) for its schema module or error classes; C1 is meant to sit above the services and hold no business logic.
[Inference] The cycles work today because Python resolves sub-module imports lazily, but they make components impossible to extract or test in isolation and raise the cost of the planned cleanup (RTD-46/51); they come from the add-only rule of Stage 15 (frozen files could not be edited, so new code was attached to existing modules).

### AC-3 Cross-cutting structure
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| AC-01 | Seven migration sets M000..M007 with **seven** version tables (`schema_migrations`, `policy_/decision_/intake_/runs_/web_/search_schema_migrations`) and per-package runners instead of one forward runner (schema-migration-plan) | `hub/*/migrations/`, DEV-28/42/59/66/76/90 | operator must run 7 `migrate` commands in order; a restore to an older backup must be reasoned per table set | Medium | High | consolidate (Stage 17 design / Stage 27) |
| AC-02 | Zone H holder logic exists three times (`hub/gate/service.py`, `hub/policy/gate.py` frozen, `hub/security/authz.py`) | DEV-41, DEV-51, RTD-46/51 | a holder-rule change must be made in three places | Medium | High | remove when non-add edits allowed |
| AC-03 | Two server entry points (R1 `WebApp`, R2 `R2WebApp`) | DEV-101, RTD-81 | ambiguity before exposure | Medium | High | choose one (Stage 27/30) |
| AC-04 | Domain -> HTTP-layer imports and package cycles (AC-2) | package graph | maintainability, isolation | Medium | High | refactor plan at Stage 17 |
| AC-05 | Golden-compare still compares 7 declared values (DEV-08 never closed) | behavior-difference-report | conformance tool weaker than designed (CAP-10) | Medium | High | S16-D01 |
| AC-06 | Runtime deviates from ADR-018 (3.10 floor; 3.10 EOL) | DS-03 | security support | High for production | Medium | OD-S12-12 |
| AC-07 | Safety posture conforms: nothing adopted / active / scheduled / exposed; No-AI holds | AC-1 | shadow build is safe to keep running | Low | High | — |

## Evidence References
- Package graph: AST walk of every `hub/**/*.py` collecting `import hub.X` / `from hub.X` at module level vs inside functions (`evidence/package-graph.txt`).

## Assumptions
- A-16-AC-1 [Assumption] The component model C1..C11 and the ADRs, though PROPOSED, are the conformance target for Stage 16 (no approved alternative exists). Confirm: Engagement lead (Dinesh Naik) at Stage 17.

## Unknowns
- U-16-AC-1 ADR-017 buy-vs-build (OPD-10).

## Unresolved Issues
- AC-01..AC-06 (debt register S16-D03..S16-D07).

## Residual Risks
- RR-AC-1 Structural debt grows if further increments keep the add-only rule (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
