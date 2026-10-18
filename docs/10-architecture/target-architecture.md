---
stage: "10 — Target Architecture + ADRs"
artifact: "target-architecture.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

Target: a No-AI modular monolith ("the hub") running beside the untouched legacy estate. New code is a Python package with capability modules, its own SQLite database holding an append-only event store, policy/rule tables, intake records, crosswalk, run records and a hash-chained audit log. Legacy stores are read only through adapters. The human disposition gate supports two recording modes and ships blocked. Status: PROPOSED, nothing ACCEPTED.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TA-1 Architecture in one view
```
 Users (reviewer, quality lead, compliance, finance(read), integration, authorised dispositioner)
        |  authn/RBAC (ADR-013)          [loopback, TLS if ever exposed - HAR-05]
 +------v-------------------------------------------------------------+
 | HTTP layer (API + server-rendered pages)  -- no business logic     |
 +------+-------------------------------------------------------------+
 | Service layer (in-process interfaces)                              |
 |  Gate (Zone H) | Decision Record | Policy/Rules | Intake | Crosswalk |
 |  Runs | Metrics | Reviewer support | Audit                         |
 +------+-------------------------------------------------------------+
 | Repositories (SQLite impl; Postgres swap possible)  ADR-004        |
 +------+---------------------------+---------------------------------+
        |                           |
  hub.sqlite3 (WAL, append-only)   Adapters (read-only)  -> legacy.sqlite3, enterprise_legacy.sqlite3,
  + audit hash chain + anchor        gateway (HTTP loopback), partner CSV, docs/archive
        |
  CLI jobs (run records) <- external trigger (disabled until OPD-11)
 [No model calls. No outbound network from product process. ADR-002]
```

### TA-2 Zones preserved (Stage 8 B-1)
- [Verified Fact] Zone H: disposition, QA release, e-signature, closure failing evidence rule, adoption of definitions/rules/active rule set. Enforced in Gate service; non-human actors rejected (FR-GATE-03).
- Zone D: everything else. Zone A: empty, no component admitted (OD-08).

### TA-3 Capability to component trace
| CAP | Component (see component-model.md) | ADRs | Key FRs |
|---|---|---|---|
| CAP-01 | Decision Record | 004, 005 | FR-DEC-01..06 |
| CAP-02 | Gate | 006 | FR-GATE-01..06 |
| CAP-03 | Policy/Rules | 007 | FR-POL-01..06 |
| CAP-04 | Intake | 008 | FR-INT-01..08 |
| CAP-05 | Crosswalk | 009 | FR-ID-01..04 |
| CAP-06 | Runs | 010 | FR-RUN-01..03 |
| CAP-07 | Metrics | 011 | FR-MET-01..08 |
| CAP-08 | Reviewer support | 012, 007 | FR-REV-01..04 |
| CAP-09 | Access/Audit | 005, 013 | FR-SEC-01..03 |
| CAP-10 | Coexistence/harness | 003, 002, 018 | FR-CO-01..04 |

### TA-4 NFR trace
| PNFR | Architectural answer |
|---|---|
| 01 availability | single host, honest: unproven (ADR-015); target Assumption |
| 02 overnight by 06:00 | CLI jobs + external schedule (ADR-010), held pending OPD-11 |
| 03/04 | R2; adapter + run timers |
| 05 recovery | file backup + checksum manifest + restore rehearsal (ADR-015) |
| 06 performance | latency timers measure first; no target (OPD-14) (ADR-016) |
| 07/08 | authn/RBAC deny-by-default; secret scan; loopback/TLS (ADR-013) |
| 09 | hash-chain + tamper test (ADR-005) |
| 10 | hold-all, no delete paths (ADR-004) |
| 11 | append-only intake, content hash, contract validation (ADR-008) |
| 12 | field-class access levels (R2) |
| 13 | Untrusted typing + fixture gate (ADR-002, 008) |
| 14 | structured logs, run records (ADR-016) |
| 15 | rule trace + override always possible (ADR-007, 006) |
| 16 | metrics module with documented definitions (ADR-011) |
| 17 | pure functions, goldens, no randomness (ADR-003, 007) |
| 18 | deny-list + egress gate + tripwire (ADR-002) |
| 19 | rollback rehearsal, replay-safety gate (ADR-003, 015) |
| 20 | labelling in all outputs (ADR-011) |

### TA-5 Root-cause trace [Inference]
RC-1: Decision Record + Gate (004-006). RC-2: event store and folded state (004). RC-3: policy objects with no default (007) - mechanism only. RC-4: three rule sets as data, adoption Zone H (003, 007) - mechanism only. RC-5: run records, checkpoints (010). RC-6: intake pipeline (008). RC-7: crosswalk (009). RC-8: metrics module (011).

### TA-6 Open decisions handled by design
| Open item | Treatment |
|---|---|
| OPD-01..03 | policy objects, status candidate/accepted-open, none adopted (ADR-007) |
| OPD-04 | all three rule sets loadable; as-found preserved + marked; change needs HAR-06 |
| OPD-05 | both recording modes, default none (ADR-006) |
| OPD-10 | reversible interfaces; no selection (ADR-017) |
| OPD-11 | scheduler disabled until answered (ADR-010) |
| OPD-09 | hold-all |
| OPD-14 | measure only |

### TA-7 Release shape [Inference]
R1 = 41 FR (trust, record, flow, intake, policy mechanism, metrics core). R2 = 11 FR (search, divergence report, cross-object findings, joined view, cost, field-class access). The split is an agent proposal pending OPD-13.

### TA-8 Preconditions before any build (Stage 7)
Executable golden harness with hermetic fixtures (CT-H1..H7), mutation gate, baseline dataset 125/4100 hash verified; all code runs in a sandbox copy (OD-03a).

## Evidence References
docs/09-initial-prd/*; ADR-001..018; docs/08-ai-qualification/deterministic-vs-ai-boundaries.md.

## Assumptions
A-10-01..A-10-19 across ADRs.

## Unknowns
Open OPD items above; real load; hosting.

## Unresolved Issues
OPD-13 (PRD approval) is a condition.

## Residual Risks
PRD still DRAFT; architecture rests on unapproved requirements.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

