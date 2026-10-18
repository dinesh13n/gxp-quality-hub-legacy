---
stage: "12 — Spec-Driven Design"
artifact: "features/f05-identity-crosswalk.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["data/legacy.sqlite3 (read-only, immutable; deviations, capa_actions, batch_records, cases)", "docs/11-data-context/data-quality-rules.md (DQ-06, DQ-07, DQ-24)", "docs/11-data-context/knowledge-model.md (K2, ER-11-02)", "docs/10-architecture/adrs/ADR-009-identity-crosswalk.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Feature spec for the explicit identity crosswalk (CAP-05): key registry with measured baseline resolution (42/42, 21/21, 173/8,567, 30/1,200, case<->batch 0), 8 behaviours, 17 acceptance criteria for FR-ID-01..04.

## Findings
### F05-1 Scope and traceability [Verified Fact: requirement text and key evidence; Inference: design]
Feature **F05 Shared Identity & Crosswalk** = CAP-05, component C7, ADR-009 (explicit `crosswalk_link`, no inference), data contract DC-12, quality rules DQ-06, DQ-07, DQ-18, DQ-24.

| Implements | FR-ID-01, FR-ID-02 (R1); FR-ID-03, FR-ID-04 (R2) |
|---|---|
| Also constrained by | FR-INT-05, FR-GATE-02, FR-MET-07, PNFR-11, PNFR-17; BR-04, BR-07; RC-7; touchpoint T5 (deterministic) |
| Open decisions | OD-S12-01 (consistency rules are policy, none shipped adopted) |
| Legacy evidence | explicit keys exist only as: `deviations.batch_id -> batch_records` (42/42 resolve), `capa_actions.deviation_id -> deviations` (21/21), `lab_results.batch_id`; **no key links `cases` to batches/deviations/CAPA** (0 of 125 case ids equal a batch id); feed `ref_id` equals `cases.id` for 173/8,567; document `reference` for 30/1,200 (DQ-06, DQ-07); five status vocabularies; enterprise `cross_references.relationship` has the single value `relates_to` (ER-11-02) |

### F05-2 Key registry shipped (match rules are data; exact equality only)
| Link type | From -> To | Key used | Created by | Baseline resolves |
|---|---|---|---|---|
| LT-01 | deviation -> batch | `deviations.batch_id = batch_records.batch_id` | rule | 42 of 42 [Verified Fact] |
| LT-02 | capa -> deviation | `capa_actions.deviation_id = deviations.deviation_id` | rule | 21 of 21 [Verified Fact] |
| LT-03 | lab_result -> batch | `lab_results.batch_id` | rule | 125 expected (not re-counted here) [Inference] |
| LT-04 | feed_item -> case | feed `ref_id = cases.id` | rule | 173 of 8,567 [Verified Fact, DQ-06] |
| LT-05 | document -> case | document `reference = cases.id` | rule | 30 of 1,200 [Verified Fact, DQ-07] |
| LT-06 | case <-> batch / deviation / capa | no key exists | **human only** | 0 by rule [Verified Fact] |

### F05-3 Behaviours
| ID | Behaviour (binding once approved) | Implements |
|---|---|---|
| BEH-ID-01 | **Link record** (SCH-CROSSWALK): `link_id`, `from_type`, `from_id`, `to_type`, `to_id`, `key_used`, `creator_kind` in {rule, human}, `creator` (rule id or user id), `created_at`, `reason` (required for human), `run_id` (for rule). Links are append-only; removal is a `LINK_RETRACTED` event referencing `link_id` with reason; the current link set is the set of non-retracted links. | FR-ID-01 |
| BEH-ID-02 | **Rule links only by exact registered key.** A rule creates a link only if the registered key values are equal as strings after Unicode NFC and trim, and the target resolves to exactly one entity. No prefix, case-folding, edit-distance, token or similarity matching exists in the code (the deny-list test forbids `difflib`, `fuzzy`, `levenshtein` imports in the crosswalk module). | FR-ID-02 |
| BEH-ID-03 | **Orphans stay orphans.** An item with no registered-key match remains unlinked in every run; orphan counts per source are a reported measure (DQ-24, FR-MET-07), never an error to repair. Re-running the matcher after more data arrives may create a new rule link only through an exact key. | FR-ID-02 |
| BEH-ID-04 | **Human link.** `OP-ID-02` lets roles reviewer, quality_lead, compliance create a link of a registered pair (LT-06 pairs included) with a non-empty `reason`; stored with `creator_kind = human` and an event `LINK_CREATED_HUMAN` (actor, time, reason). A duplicate active link is refused (E-ID-LINK-EXISTS); an unregistered type pair is refused (E-ID-PAIR-NOT-REGISTERED); self-links are refused. Service/integration actors cannot create human links (E-AUTH-FORBIDDEN). | FR-ID-01, FR-ID-02 |
| BEH-ID-05 | **Lookup.** `OP-ID-01` accepts `id` and optional `id_type`. If `id_type` is absent the id is compared with registered id patterns (case `C\d{8}`, batch `BT\d{8}`, others registered); a string matching several patterns returns the candidates and requires `id_type` (E-ID-AMBIGUOUS-TYPE) - no guessing. Response lists direct links with key, creator, time. | FR-ID-01 |
| BEH-ID-06 | **(R2) Joined view.** `OP-ID-04` returns the connected set of entities over active links (breadth-first, depth cap 4, size cap 500, `truncated` flag and count when capped), read-only, deterministic order (type, id). Entering with any member id returns the same set. Fields are filtered by caller role/tenant/access level first (F09). | FR-ID-04 |
| BEH-ID-07 | **(R2) Consistency findings.** `CONSISTENCY` policy objects (F03) define pairs of conditions over linked entities (e.g. `case.state in {X}` with `batch.qa_status in {Y}`). The check writes `finding` rows `{rule_ref, object_refs, detected_at, policy_version}` idempotently (one open finding per rule+objects+version), changes no state, and never auto-corrects. No CONSISTENCY policy ships adopted, so a fresh install yields zero findings. | FR-ID-03 |
| BEH-ID-08 | **Vocabularies are not mapped.** The word CLOSED in cases, batch QA, deviations and enterprise tables is not treated as equivalent; consistency rules compare per-vocabulary values explicitly. | FR-ID-03, knowledge-model K2 |

### F05-4 Error cases
E-ID-LINK-EXISTS, E-ID-PAIR-NOT-REGISTERED, E-ID-SELF-LINK, E-ID-AMBIGUOUS-TYPE, E-ID-REASON-REQUIRED, E-ID-NOT-FOUND, E-ID-LINK-NOT-FOUND, E-AUTH-FORBIDDEN (error-handling-spec.md).

### F05-5 Acceptance criteria
| ID | Given | When | Then | Implements | Kind |
|---|---|---|---|---|---|
| AC-ID-01 | the shipped legacy data after rule matching | links of LT-01 and LT-02 are counted | 42 deviation->batch and 21 capa->deviation links exist, each with key_used, creator_kind = rule, created_at | FR-ID-01 | positive |
| AC-ID-02 | the 173 feed rows whose ref_id equals a case id | matched | 173 LT-04 links; 8,394 feed items remain unlinked | FR-ID-01, FR-ID-02 | positive |
| AC-ID-03 | an orphan fixture (feed ref_id 'C99999999') | the matcher runs 3 times with other data added | the item stays unlinked after every run | FR-ID-02 | negative |
| AC-ID-04 | feed ref_id 'c00000001' (case differs) and 'C0000000 1' | matched | no link is created (no case-folding/fuzzy); outcome UNMATCHED_REF | FR-ID-02 | negative |
| AC-ID-05 | the crosswalk module source | static check runs | no import of difflib/fuzzy/levenshtein/similarity libraries | FR-ID-02 | negative |
| AC-ID-06 | a reviewer links case C00000001 to batch BT00000000 with reason | OP-ID-02 is called | link stored (creator_kind human) and LINK_CREATED_HUMAN event exists with actor, time, reason | FR-ID-02, FR-ID-01 | positive |
| AC-ID-07 | the same request without reason | called | E-ID-REASON-REQUIRED | FR-ID-02 | negative |
| AC-ID-08 | a service account calls OP-ID-02 | called | rejected E-AUTH-FORBIDDEN and audited | FR-ID-02, FR-SEC-01 | negative |
| AC-ID-09 | an existing active link | the same link is posted again | E-ID-LINK-EXISTS | FR-ID-01 | negative |
| AC-ID-10 | a link between an unregistered type pair | posted | E-ID-PAIR-NOT-REGISTERED | FR-ID-01 | negative |
| AC-ID-11 | a link retracted with reason | the current set and history are read | link no longer active, original and LINK_RETRACTED event both present | FR-ID-01 | edge |
| AC-ID-12 | an id string that matches two registered patterns | lookup without id_type | E-ID-AMBIGUOUS-TYPE with candidate types, no data returned | FR-ID-01 | edge |
| AC-ID-13 | R2: batch BT00000000 with a deviation and CAPA | lookup by batch id, by deviation id and by capa id with view | the same linked set (3 entities) is returned each time | FR-ID-04 | positive |
| AC-ID-14 | R2: a view that exceeds the size cap | requested | `truncated = true` with total count, no silent cut | FR-ID-04 | edge |
| AC-ID-15 | R2: a configured test CONSISTENCY rule (case state X while linked batch qa_status Y) and a seeded contradictory fixture | the check runs twice | exactly one open finding, zero state changes anywhere (store diff empty except finding rows) | FR-ID-03 | positive |
| AC-ID-16 | R2: fresh install, no adopted CONSISTENCY policy | the check runs | zero findings and a statement 'no consistency policy adopted' | FR-ID-03 | negative |
| AC-ID-17 | a caller lacking access to restricted documents | joined view requested | restricted linked documents appear as `{access: denied}` and are not counted in totals revealed to the caller | FR-ID-04, FR-SEC-03 | negative |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-F05-1 LT-03 (lab_result->batch) resolves for all rows; counts not re-verified in this stage. Confirm at Stage 14.
- A-12-F05-2 Depth cap 4 / size cap 500 for the joined view are spec proposals.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-F05-1 Whether a real key between cases and batch/deviation/CAPA exists in the source systems (none in repo).
- U-12-F05-2 Identifier patterns for deviation and CAPA ids not enumerated here.

## Unresolved Issues
- Cross-object consistency rules (FR-ID-03) cannot ship with content until OD-S12-01 / RC-3 decisions exist.

## Residual Risks
- Low match rates (2.0% feed->case) will look like a defect; they are reported as orphan accounting (DQ-24).
- Human links are the only way to join cases to batches: quality depends on reviewers.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
