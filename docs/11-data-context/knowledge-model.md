---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "knowledge-model.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["data/legacy.sqlite3 (read-only)", "data/enterprise_legacy.sqlite3 (read-only)", "docs/data-dictionary.md", "docs/domain-assurance.md", "docs/09-initial-prd/capability-map.md", "docs/09-initial-prd/functional-requirements.md FR-POL-01, FR-MET-01, FR-ID-01..04", "docs/10-architecture/adrs/ADR-007, ADR-009, ADR-011", ".fde/orchestrator-decisions.md OD-07, OD-08"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** Under OD-08 the "knowledge" in this product is **structured, deterministic domain knowledge** (entities, relationships, controlled vocabularies, policy objects, document corpus) — not an LLM knowledge base. No ontology engine, graph database, embeddings or learned model is proposed. The model below is the minimum vocabulary needed so that Stage 12 can write schemas and so that every figure carries a definition. The most important finding is semantic: **the repository uses at least eight incompatible status vocabularies and three identifier spaces; the meaning of "closed", "resolved" and "approved" is unresolved (OPD-01) and is therefore modelled as versioned candidate policy objects, never as a built-in.**

## Findings

### K1. Core entities (target logical model; PROPOSED)

| Entity | Identity | Key attributes | Legacy source | Relationships (via crosswalk only) |
|---|---|---|---|---|
| Case | `case_id` (`C########`) | site, region, severity, opened_at, account | `cases` (125) | has Events; linked to Batch/Deviation/CAPA/Feed by `crosswalk_link` |
| DecisionEvent | `event_id` | type, from/to state, actor, actor_kind, basis, evidence_refs | `events` (145, 2 types) -> new | belongs to Case; cites Evidence |
| Batch | `batch_id` | material, site, assay, unit, qa_status | `batch_records` (125) | has LabResults, Deviations |
| Deviation | `deviation_id` | classification (CRITICAL 11 / MAJOR 15 / MINOR 16), status | `deviations` (42) | has CAPA |
| CAPA | `capa_id` | owner (data), due_at, state | `capa_actions` (21) | belongs to Deviation |
| LabResult | `result_id` | analyte, value (nullable), unit, test_status | `lab_results` (125) | belongs to Batch |
| Material / SOP / ReferenceVersion | `material_id`; `(sop_id,version)`; `(ref_key,version)` | spec/effective/valid windows | `materials` 30, `sop_versions` 45, `reference_versions` 180 | versioned, effective-dated |
| FeedItem (Intake) | `feed_id` + content hash | partner, schema_rev, kind, payload (Untrusted) | `partner_feeds` (8,567) | matched to Case by crosswalk or flagged unmatched |
| Document | `doc_id` + `version` | locale, source, effective_at, access_level, ocr_confidence, body (Untrusted) | `source_documents.jsonl` (1,200), archive (420), `document_links` (12,500 enterprise) | references a Case/Object by `reference` (30 of 1,200 resolve today) |
| PolicyObject | `(policy_id, version)` | definition, owner, effective date, status | `policy_register` (40), `contracts/decision-policies-archive.json` | applies to Rule outputs and Metrics |
| Rule / RuleSet | `(ruleset, row_id, version)` | thresholds, region, effective dates, default behaviour | JS archive + Python rules (RC-4, three divergent sets) | produces RuleTrace |
| Metric | name + definition tag + policy version | window, denominator, exclusions | `operating_costs` (modelled) | computed from events |
| Run | `run_id` | trigger, inputs, outcomes, backlog | `batch_runs` (60, legacy) -> `run_record` | stamps every ingested row |
| Actor | `actor_id`, `actor_kind` | role | `actor-N`, `user-N` strings | no identity directory exists [UNK] |

### K2. Controlled vocabularies as found (Verified Fact, read-only queries)

| Domain | Values (count) |
|---|---|
| `cases.status` | OPEN 42, UNDER_REVIEW 30, CLOSED 36, ESCALATED 9, REOPENED 8 |
| `batch_records.qa_status` | REVIEW 50, QA_HOLD 42, CLOSED 33 |
| `deviations.status` | OPEN 14, INVESTIGATION 16, CLOSED 12 |
| `capa_actions.state` | OPEN 7, OVERDUE 6, VERIFIED 8 |
| `lab_results.test_status` | PENDING 36, OOS 35, VALID 28, INVALID 26 |
| `policy_exceptions.outcome` | REVIEW 60, OPEN 57, WAIVED 56, BLOCKED 51 |
| `partner_feeds.processing_status` | NEW 8,000, RETRY 500, REPLAY 67 |
| enterprise `operational_objects.status` / `workflow_tasks.status` | OPEN, REVIEW, HOLD, CLOSED, ESCALATED, REOPENED (about 2,080 each; tasks 945-1,140) |
| enterprise `integration_attempts.status` | FAILED / RETRY / SUCCESS / TIMEOUT 625 each |

[Inference] "CLOSED" appears in four vocabularies (cases, batch QA, deviations, enterprise objects/tasks) with no evidence that they mean the same thing. Closure policy cannot be derived from the repo (RC-3, OPD-01). Therefore the model has a `status_vocabulary` registry (name, owner, values, mapping) and **never maps across vocabularies automatically**; any mapping is a PolicyObject adopted by a human (Zone H).

### K3. Definition tags and policy knowledge

- KM-1 Candidate definition tags D-OPS, D-EVID, D-FIN (FR-POL-01) are stored as PolicyObjects with status `candidate`; none is `adopted` (OPD-01/03 open). Every figure displays tag + policy version (FR-MET-01); figures with different tags are never combined (FR-MET-02).
- KM-2 The "48 h" expectation is parameters: clock-start event, clock-stop event, duration, calendar basis (FR-POL-02); no value adopted by default (OPD-02).
- KM-3 Rule tables are data (FR-POL-04): thresholds, regions, effective dates, owner, default. The as-found unknown-region default (999,999) is recorded as a "defaulted" marker case, not silently endorsed (FR-POL-06).
- KM-4 `operating_costs.total_cases` must not be used as "cases created" (OD-07; A-04-01 refuted); the Metric entity records `basis: modelled`.

### K4. Document knowledge

- KM-5 A document is an immutable (doc_id, version) with effective date; supersession is a link, not an overwrite. Corpus facts: versions revA 289, revB 324, v1 301, v2 286; effective 2023-01-01..2025-09-26.
- KM-6 Metadata that gates access (`access_level`) travels with every derived artifact (index row, snippet, export).
- KM-7 No entity extraction, summarisation or classification of document text is performed by the product (OD-08); document "knowledge" is limited to the attributes above plus full-text.

### K5. Erratum / data-reality notes

- ER-11-01 [Verified Fact] Stage 0A DF-07 mentions "financial adjustments in 4 currencies"; this stage found `enterprise_legacy.sqlite3.financial_adjustments` is **USD only (3,125 rows)**. Multi-currency values exist in `vendor_file_rows` (e.g. INR sample) and feed payloads. Original finding preserved (CC-07); this is the correcting reference.
- ER-11-02 [Verified Fact] `operational_objects.entity_type` is the single value `batch_id` for 12,500 rows, and `cross_references.relationship` is the single value `relates_to` (4,166): the enterprise graph has no typed relationships.

## Evidence References

Queries this stage: distinct value counts for the columns above; `PRAGMA table_info`; `source_documents.jsonl` profile. Prior: `docs/data-dictionary.md`, RC-3/RC-4, OPD-01/02.

## Assumptions

- A-11-08: Logical entities are sufficient for R1/R2 scope; no ontology tooling is required. Confirm: Engagement lead (Dinesh Naik), Stage 12.

## Unknowns

- U-11-12 Real meaning of each "CLOSED". U-11-13 Real identity directory / role model for Actor. U-11-14 Whether site aliases (e.g. `IN-BLR`) map to a master site list.

## Unresolved Issues

- OPD-01/02/04 remain accepted-open; the model deliberately defers values.

## Residual Risks

- DR-10 (vocabulary conflation), DR-11 (premature definition).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial knowledge model; ER-11-01/02 corrections. |
