---
stage: "10 — Target Architecture + ADRs"
artifact: "component-model.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

Eleven components with responsibilities, owned data, permitted dependencies and zone. Names are working names; module layout is design, not code.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CM-1 Components
| # | Component | Responsibility | Owns (data) | May call | Zone | CAP | ADR |
|---|---|---|---|---|---|---|---|
| C1 | HTTP layer | Routing, session, input validation, output escaping; no business logic | - | Services | D | CAP-09 | 014 |
| C2 | Access & Audit | Authenticator interface, RBAC, audit hash chain, verify-audit | users, roles, audit_log | repositories | D | CAP-09 | 005, 013 |
| C3 | Decision Record | Append events, fold state, as-of queries, reopen events, evidence refs, closure evidence check | decision_events, case_state projection | C2, C4 | D (closure failing rule = H) | CAP-01 | 004 |
| C4 | Policy & Rule Service | Policy objects, rule sets/rows, pure evaluation, rule trace, `defaulted` marker | policy_object, rule_set, rule_row | C2 | D; adoption H | CAP-03 | 007 |
| C5 | Disposition Gate | Zone H transitions, authorised-holder check, recording modes none/event/external_ref, read-only evidence pack | holder list (config), disposition refs | C2, C3, C4, C7 | H | CAP-02 | 006 |
| C6 | Intake | receive/validate/classify/match/outcome, quarantine, reason codes | intake_raw, intake_outcome, quarantine | C4, C7 | D | CAP-04 | 008 |
| C7 | Crosswalk | Explicit links, orphans, human links as events, joined view | crosswalk_link | C3 | D | CAP-05 | 009 |
| C8 | Runs | CLI jobs, run records, checkpoints, backlog | run_record, checkpoint | C6, C9 | D | CAP-06 | 010 |
| C9 | Metrics | Definition-tagged KPIs, decimals, no fan-out, labels | metric_definition, metric_result | C3, C4, C8 | D | CAP-07 | 011 |
| C10 | Reviewer Support | Exception queue, rule-trace views, FTS search (R2), templates (R2) | fts index | C4, C6 | D | CAP-08 | 012 |
| C11 | Legacy Adapters + Harness | Read-only readers for legacy DBs/feeds/docs; golden comparison; shadow reports | none (reads) | - | D | CAP-10 | 003, 018 |

### CM-2 Dependency rules [Inference - design]
1. HTTP -> services -> repositories; no upward calls.
2. Only C11 may open legacy files, and only with `file:...?mode=ro`.
3. No component imports `app.store` or any legacy module.
4. Only C5 may write Zone H transitions; C5 rejects non-human actors; no job, importer or report may call C5 write methods.
5. C2 audit is called by every write path; failures to audit abort the write.
6. Untrusted text type cannot be passed into C3/C4/C5 decision parameters.
7. No module performs outbound network calls except C11's gateway reader on loopback.

### CM-3 Evidence trace
FR-GATE-01 (no component may make dispositions) is enforced by rule 4 and a static test that no call path from C6/C8/C9/C10 reaches C5 writes.

## Evidence References
ADR-001..018; docs/09-initial-prd/capability-map.md.

## Assumptions
Module granularity is a design choice; Stage 12 may adjust.

## Unknowns
Whether UI needs more than server-rendered pages.

## Unresolved Issues
None blocking.

## Residual Risks
Component count may grow beyond a monolith-friendly size.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

