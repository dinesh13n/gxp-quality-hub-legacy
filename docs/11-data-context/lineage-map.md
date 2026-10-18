---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "lineage-map.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/data-flow-overview.md DF-01..DF-10", "docs/07-repo-assessment/dependency-map.md DM-10..DM-18", "docs/10-architecture/target-architecture.md TA-1", "docs/10-architecture/adrs/ADR-003, ADR-004, ADR-005, ADR-008, ADR-009, ADR-011", "app/store.py", "app/generate.py", "app/partner_feeds.py", "app/gateway_bridge.py", "app/historical_fixture.py"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** Two lineage views: **as-found** (generator -> stores -> consumers, from Stage 0A/7) and **target** (adapters -> raw intake -> hub events -> projections -> metrics/search, from Stage 10). Headline: as-found lineage is *code-defined but not recorded* — no table stores which generator, seed or run produced a row, and the shipped DB is residue of a test run (DF-03). Target design records lineage as data (source, hash, run_id on every hub row).

## Findings

### L1. As-found lineage [Verified Fact unless marked]

```
app.generate (seed) --------------> cases, events, source_messages, operating_costs  (legacy.sqlite3)
app.domain_data ------------------> materials, batch_records, deviations, lab_results, capa_actions, sop_versions, reference_versions
app.partner_feeds (staging) ------> partner_feeds (8,567) --reconcile--> processing_status UPDATED IN PLACE
upstream simulator -> gateway HTTP :8090 -> app.gateway_bridge (poll, 5 s timeout, no retry) -> gateway_inbox
vendor CSV -> importer -------------> vendor_file_imports / vendor_file_rows (2,400)
app.enterprise_legacy ------------> enterprise_legacy.sqlite3 (12 tables) -> shift_reconciliation only
app.historical_fixture (seed 7421 tiny) -> data/lake/{tiny,bundled} -> Java ReconcileLegacy (CSV by position)
app.generate_documents -----------> data/documents/source_documents.jsonl   (no consumer in code)
app.archived_documents -----------> data/archive_documents/*.eml|html       (no consumer; deletes dir on regenerate)
tests (setUp) --------------------> overwrite legacy.sqlite3 with 125-case fixture (DF-02)  <-- why baseline = 125 cases
```

| ID | Finding | Evidence | Impact | Risk | Conf. | Class |
|---|---|---|---|---|---|---|
| LN-01 | No row-level lineage metadata exists: no `source_run_id`, generator version or seed column in `cases`, `events`, `partner_feeds`. Seed 4100 is a documented fact (OD-09), not stored in the DB. | PRAGMA table_info this stage | Baseline provenance rests on checksum `c254649f…d70aa` and docs only | Medium | High | [VF] |
| LN-02 | Only the partner/lake paths carry some provenance: `partner_feeds.partner/schema_rev/source_ts/ingest_ts`, `gateway_inbox.source_system/received_at`, lake `manifest.json` (seed 7421, `sha256_partner_export`). | DDL; manifest | Partial source attribution | Low | High | [VF] |
| LN-03 | Reconcile mutates `processing_status` in place; prior status is lost; 8,000 NEW / 500 RETRY / 67 REPLAY currently. | `app/partner_feeds.py`; ADR-008 context | History of a feed's handling not reconstructable | High | High | [VF] |
| LN-04 | Case lineage is snapshot-only: `cases.version`=1 for 125/125; 8 REOPENED, 0 reopen events. | queries this stage; RC-2 | State at past time cannot be reconstructed | High | High | [VF] |
| LN-05 | Orphan lineage: 8,394 of 8,567 feeds and 1,170 of 1,200 documents point to cases that do not exist in the baseline. Lineage from evidence to case is mostly absent. | queries this stage | Evidence packs for most items will be empty without crosswalk links | Medium | High | [VF]; cause [INF] generator-shaped |
| LN-06 | Shipped baseline custody: `data/*.sqlite3` and `data/lake/` are git-ignored; backup manifest now covers all 1,512 files (OD-03a); file mtime vs DB-internal timestamp offset unexplained (DF-04). | OD-03a; DF-04 | Chain of custody for baseline is local-only | Medium | High | [VF]; cause [UNK] |
| LN-07 | Cross-language edges: partner CSV -> Java by position; policy JSON -> JS only (RC-4); Python never reads it. | DM-17, DM-18 | Silent drift between three implementations | Medium | High | [VF] |

### L2. Target lineage (PROPOSED; ADR-003/004/008/009 not accepted)

```
legacy DBs / gateway / CSV / docs / archive      (read-only adapters; never modified)
        | adapter reads  [source, source_ref, fetched_at, adapter_version]
        v
  raw_intake  (append-only; content_hash; schema_rev; raw bytes)  -- run_id -->  run_record
        | validate (contract version)        -> quarantine (reason code) 
        v
  intake_outcome (append-only; rule_id + rule_version + reason code)
        | crosswalk (exact key only)          -> crosswalk_link (creator rule|human)
        v
  decision_events (append-only, hash chain)  --fold-->  case_state projection (rebuildable)
        |                                              |
        +--> audit chain (ADR-005) <-------------------+
        v
  metrics (definition tag + policy version + window + denominator)   doc_index (FTS5; source_hash, doc_id, version)
```

| ID | Target lineage rule | Source | Class |
|---|---|---|---|
| LT-01 | Every hub row carries `source`, `source_ref`, `source_hash`, `ingested_at`, `run_id`, `adapter_version` (DQ-23). | ADR-008 | [INF] |
| LT-02 | Derived values (projection, metric, index) store the *inputs' identifiers and rule/policy version*, so each is recomputable; projection rebuild equals stored state is a verification test. | ADR-004; FR-DEC-02 | [INF] |
| LT-03 | Transform steps are named, versioned, deterministic functions; the same input yields bit-identical output (PNFR-17). | NFR | [INF] |
| LT-04 | Baseline fixture lineage is recorded in a manifest: commit `a6eb4e8` (tag `baseline-as-found`), seed 4100, sha256 of each DB, row counts. | OD-06, OD-09 | [VF] inputs; [INF] manifest design |
| LT-05 | Corrections are new events referencing the original event, never edits (CC-07 spirit). | FR-DEC-01 | [INF] |
| LT-06 | Lineage queries ("which inputs produced this figure/decision?") are a supported read path for auditors (FR-DEC-04, FR-MET-06). | PRD | [INF] |

## Evidence References

DF-01..DF-10; DM-10..DM-18; query this stage: `PRAGMA table_info` on every table (no lineage columns), `cases.version`, event types, orphan counts; `data/lake/tiny/manifest.json`.

## Assumptions

- A-11-07: Target lineage fields can be added to the new hub store without touching legacy schemas (ADR-003). Confirm: Engagement lead (Dinesh Naik), Stage 12.

## Unknowns

- U-11-10 Whether the original pre-test 6,000-case ZIP exists (U-14). U-11-11 Cause of file-mtime offset (DF-04).

## Unresolved Issues

- None blocking; legacy lineage gaps are documented and preserved as the as-found baseline.

## Residual Risks

- DR-03 (baseline custody), DR-04 (orphan evidence), DR-09 (in-place mutation).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial as-found and target lineage. |
