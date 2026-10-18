---
stage: "10 — Target Architecture + ADRs"
artifact: "ADR-004-data-store-and-event-model.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/ (capability-map, functional-requirements, nfrs, open-product-decisions)", "docs/06-root-cause/confirmed-root-causes.md", "docs/07-repo-assessment/ (repo-transformation-readiness, dependency-map, characterization-test-plan)", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md", "docs/00-preflight/ai-economics/ (preliminary-tco, quality-latency-cost-envelope)", "docs/00-preflight/operating-contract/ (provisional-human-approval-rules, stop-conditions)", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "app/store.py", "docs/06-root-cause/confirmed-root-causes.md RC-2", "docs/07-repo-assessment/dependency-map.md DM-02, DM-10"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT/PROPOSED: nothing here is an approval. ACCEPTED status for any decision can only be set by Engagement lead (Dinesh Naik) (HAR-11).**

ADR-004 — Data store and decision-record model (append-only events in SQLite). Status: PROPOSED (recommended option B).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### Status
PROPOSED (recommended option B). Postgres migration is a defined trigger, not a current decision.

### Traceability
FR-DEC-01..06, FR-INT-01, FR-ID-01, FR-RUN-02; PNFR-05, PNFR-09, PNFR-10, PNFR-11, PNFR-16; RC-1, RC-2, RC-6; H-14; OPD-09.

### Context
[Verified Fact] `cases` is a mutable snapshot: `version`=1 for 125/125, creation event stores current status, only 2 event types, 8 REOPENED cases have 0 reopen events (RC-2; `app/store.py` schema). [Verified Fact] Entire estate is SQLite files. [Verified Fact] H-14 SQLite contention is SUPPORTED by config only (not measured). [Verified Fact] No retention policy exists (OPD-09) so no deletion may occur (PNFR-10). [Inference] At 125 cases (167/month base, up to 1,670 high - Assumed, 0C volume-assumptions) a single-writer SQLite file is within range.

### Options considered
| Option | Description | For | Against | Fit across the 7 dimensions (fit/NFR/security/lock-in/cost-latency/resilience/brownfield) |
|---|---|---|---|---|
| A. Extend legacy `legacy.sqlite3` | Add tables to the shared integration-bus DB | No new file | DB is the shared integration bus used by API, bridge, reconcile, importer, gateway (DM-10); blast radius; tests destructive | Poor brownfield safety |
| B. New SQLite DB (WAL), append-only event store + projections - RECOMMENDED | Separate `hub.sqlite3`; `decision_events` is insert-only (triggers reject UPDATE/DELETE); current state = fold of events with materialised projection tables rebuildable from events; legacy DB read-only | Meets FR-DEC-01/02/03 by construction; no new infra; cheap backup/restore (file + checksum, PNFR-05); reversible | Single writer; no row-level security; triggers can be dropped by a DBA (mitigated by ADR-005 chain) | Fit High; NFR ok at scale (Assumption); lock-in none; cost minimal; resilience medium (single file); brownfield High |
| C. PostgreSQL | Managed or self-hosted server | Concurrency, roles, row-level security, mature backup | New infra, HAR-05/HAR-08, ops cost, no environment exists, no measured need | Fit High; cost above S1; lock-in low (open source); brownfield medium |
| D. Event store product / cloud ledger DB | Dedicated append-only service | Native immutability | Vendor lock-in with no evidence (guardrail); cost; overkill | Not justified |

### Decision / recommendation
Recommend B with repository interfaces so a Postgres backend (C) is a swap, not a rewrite. Retention: hold-all, no delete paths coded until OPD-09 is decided. Schema/DDL belongs to Stage 11.

### Consequences
- Positive: history reconstructable (RC-2 closed by design); projection rebuild is a verification test.
- Negative: write serialisation; need for backup rehearsal (PNFR-05); schema migrations must be explicit.
- Capacity limit: if measured concurrent writers > 1 sustained or p95 latency target (OPD-14) fails, C is triggered.

### Trigger to decide / revisit
Decide at Stage 11 with a data model; migrate to C if: multi-user concurrent writes measured to contend (H-14 test V-13), non-loopback exposure approved (HAR-05), or retention/row-level-security needs emerge.

## Evidence References
app/store.py; docs/06-root-cause/confirmed-root-causes.md RC-2; docs/07-repo-assessment/dependency-map.md DM-02, DM-10

## Assumptions
A-10-05 Volumes per 0C Base/High tiers; Confirm: Engagement lead (Dinesh Naik).

## Unknowns
U-10-07 Actual write concurrency; U-10-08 whether SQLite WAL works on the target file system.

## Unresolved Issues
PNFR-06 latency target unset (OPD-14).

## Residual Risks
Single-file corruption risk; trigger-based immutability is bypassable by someone with file access.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 10). |

