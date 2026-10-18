---
stage: "14 — Transformation / Migration Plan"
artifact: "schema-migration-plan.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/12-specs/contracts/ddl/hub-schema-v0.1.sql (150 lines, 16 CREATE TABLE, append-only triggers L36-40, L61-62)", "docs/12-specs/contracts/schemas/*.schema.json (16)", "docs/12-specs/features/f10-coexistence-change-safety.md (BEH-CO-02 deviation_register, BEH-CO-05 coexistence_inventory, BEH-CO-06 rollback)", "docs/10-architecture/adrs/ADR-004-data-store-and-event-model.md", "docs/10-architecture/adrs/ADR-005-audit-trail-tamper-evidence.md", "docs/10-architecture/adrs/ADR-009-identity-crosswalk.md", "docs/10-architecture/deployment-architecture.md L23", "docs/12-specs/spec-readiness.md (RF-1, OD-S12-09/-12/-17/-19)", ".fde/orchestrator-decisions.md (OD-09, OD-10)", "data/ listing"]
supersedes: "none"
---
## Summary
**Label: synthetic repository; DRAFT plan, not an approval.**
**Legacy schemas are not migrated at all in R1** — zero DDL/DML against `data/legacy.sqlite3`, `data/enterprise_legacy.sqlite3` or any file under `data/` (HAR-01, CR-1..CR-3). "Migration" in this engagement means (a) creating the **new** `hub.sqlite3` schema in six forward-only, versioned steps aligned to increments, and (b) **copying** legacy facts into the hub as provenance-stamped, append-only events via read-only adapters. Because the hub is non-authoritative until cutover, every data migration before cutover is reversible by rebuilding `hub.sqlite3` from a legacy snapshot.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### SM-1 Schema versions (forward-only, one per increment)
| Version | Inc | Tables (from `hub-schema-v0.1.sql` unless marked) | Reversible how | Tag |
|---|---|---|---|---|
| M000 | INC-02 | `schema_migrations(version, sha256, applied_at)` **[not in DDL v0.1 — addendum]**; `deviation_register` **[addendum: BEH-CO-02 defines it, DDL omits it]**; `coexistence_inventory` **[addendum: BEH-CO-05]** | delete hub file (no data of value yet) | [Verified Fact] absent from DDL; [Inference] needed |
| M001 | INC-03 | `audit_log`; users/roles **[addendum or config — Unknown which; DDL v0.1 has no users/roles table]** | restore pre-migration backup | [Verified Fact] absence; [Unknown] intent |
| M002 | INC-04 | `policy_object`, `policy_events`, `rule_set`, `rule_row`, `active_ruleset` | restore backup | [Verified Fact] |
| M003 | INC-05 | `decision_events`, `evidence_record`, `case_state`, `crosswalk_link`, `crosswalk_link_event` | restore backup / rebuild | [Verified Fact] |
| M004 | INC-06 | `raw_intake`, `intake_outcome` (+ checkpoint storage: `run_event` RUN_CHECKPOINT or addendum) | restore backup / rebuild | [Verified Fact] tables; [Inference] checkpoint |
| M005 | INC-07 | `run_event`, `metric_definition`, `metric_value` | restore backup / rebuild | [Verified Fact] |
| M006 (opt.) | INC-09 | FTS5 virtual table (R2) — only if FTS5 is present on target (OD-S12-12) | drop virtual table (derived index) | [Unknown] FTS5 on target |

Rules: migrations are SQL files with sha256 recorded in `schema_migrations`; the runner refuses to start if an applied migration's hash changed; **no down-migrations** (append-only triggers make row-level undo impossible by design, ADR-004/005) — rollback = restore. Every migration takes a checksummed backup of `hub.sqlite3` + audit anchor first (BEH-CO-06). Runtime floor: SQL limited to SQLite 3.37.2 features (device), e.g. no `STRICT`-dependent semantics beyond 3.37, no `RETURNING` reliance beyond 3.35 [Verified Fact: device SQLite 3.37.2].

### SM-2 Data migrations (legacy → hub, copy-only)
| ID | What | Source → target | Volume (evidence) | Idempotency | Verification | Inc | Tag |
|---|---|---|---|---|---|---|---|
| DM-1 | Legacy case backfill (R1 = legacy backfill only, OD-S12-19 default) | `cases` (AD-01) → `decision_events` type LEGACY_IMPORTED + `case_state` projection | 125 cases (OD-09) | key (source_db_sha256, case_id); re-run = NOOP | count 125; projection `verify-projection` 0 mismatches (G4); priority via as-found rules = CT-02 distribution 36/70/17/2 | INC-05 | [Verified Fact] counts from CT-02 |
| DM-2 | As-found rule sets | AD-06 → `rule_set`/`rule_row` (status as-found, **not active**) | 4 sources (Py, JS, SQL, archive JSON) | content hash | TST-CO-03 / CT-01..03 zero diff | INC-04 | [Inference] |
| DM-3 | Partner-feed shadow intake | `partner_feeds` (AD-03) → `raw_intake` + `intake_outcome` | 8,567 rows (RF-2) | natural key (partner, record_kind, ref_id, source_ts) + content hash (OD-10a) | 67 REPLAY rows → NOOP_DUPLICATE (RF-1); no row dropped; sum(outcomes) = input | INC-06 | [Verified Fact] counts RF-1/RF-2 |
| DM-4 | Gateway / source messages | AD-04 → `raw_intake` | `source_messages` 15 (15/15 conform) | message_id | conformance report | INC-06 | [Verified Fact] RF-2 |
| DM-5 | Crosswalk | none migrated — ADR-009 forbids inferred links; legacy has no link table → hub lists orphans | — | — | orphan report | INC-05 | [Verified Fact] ADR-009/RC-7 |
| DM-6 | Metrics history | **not migrated**; legacy `operating_costs.total_cases` is random (OD-07) — hub computes fresh, tagged values | — | — | definition tags | INC-07 | [Verified Fact] OD-07 |

### SM-3 Data migration risks
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| DR-1 | Wrong identity key would mis-classify re-deliveries | RF-1; OD-10a | thousands of false conflicts/quarantines | High | High | OD-S12-17 — needed before INC-06 |
| DR-2 | Append-only store cannot "fix" a bad backfill after cutover | ADR-004 triggers L36-40 | permanent wrong history | High post-cutover; Low pre-cutover (rebuild allowed) | High | rebuild-before-cutover rule (SM-4) |
| DR-3 | DDL v0.1 lacks tables the specs require (deviation_register, coexistence_inventory, users/roles, schema_migrations) | DDL table list vs BEH-CO-02/05 | INC-02/03 need a DDL addendum | Medium | High | Addendum authored in Stage 15 PR and back-referenced at Stage 17 (HAR-13: Stage 12 file not edited in place) |
| DR-4 | Partner feeds are not reproducible by regeneration (CT-14) | characterization-test-plan.md CT-14 | DM-3 baseline must come from the backed-up file, not regeneration | Medium | High | use backup copy, hash-gated |
| DR-5 | Retention undecided | OD-S12-09 | hub grows unbounded (hold-all) | Low (125 cases) | High | accepted-open is fine for R1 |

### SM-4 Rebuild-before-cutover rule
Until a capability is cut over (cutover-plan.md), `hub.sqlite3` is **disposable**: any backfill defect is fixed by correcting the importer and rebuilding from the hash-gated legacy snapshot. After cutover, corrections are compensating events only (ADR-004). [Inference]

## Evidence References
`docs/12-specs/contracts/ddl/hub-schema-v0.1.sql`; ADR-004/005/009; f10 BEH-CO-02/05/06; spec-readiness RF-1/RF-2; OD-07, OD-09, OD-10.

## Assumptions
- A-14-08 [Assumption] DDL addenda (DR-3) are authored as new files on the BUILD branch (e.g. `hub/migrations/M000_*.sql`) without editing Stage 12 docs (HAR-13). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-14-07 Whether users/roles live in DB or config (DDL silent; `hub-config.schema.json` exists).
- U-14-08 FTS5 availability on the target runtime.

## Unresolved Issues
- OD-S12-17 (identity key), OD-S12-09 (retention), OD-S12-19 (case creation path).

## Residual Risks
- RR-SM-1 Backfill provenance relies on legacy DB hash; if the baseline file is ever regenerated (HAR-01) provenance breaks — mitigated by OD-03 backup and hash gate.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial schema/data migration plan (Stage 14). |
