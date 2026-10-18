---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "data-context-risks.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/11-data-context/*.md (all other Stage 11 artifacts)", "docs/00-preflight/discovery/initial-risk-register.md", "docs/10-architecture/architecture-risk-register.md", "docs/09-initial-prd/open-product-decisions.md", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-09"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** 19 data/knowledge risks (DR-01..DR-19), each with evidence, owner, resolving stage and status, plus the **Stage 11 Completion Gate evaluation**. Likelihood/Impact: L/M/H are judgements (Inference), not measurements. All owners are "Engagement lead (Dinesh Naik)" because he is the only human on the engagement; due dates are stages, not calendar dates (none exist).

## Findings

### Risk register

| ID | Risk | Evidence | L | I | Mitigation / control (design) | Owner | Resolve at | Status |
|---|---|---|---|---|---|---|---|---|
| DR-01 | No accountable owner/steward for any source; closed/resolved/approved definitions, retention and data ownership unanswered | data-source-inventory DI-01; OPD-01, OPD-04, OPD-09, OPD-15 | H | H | Interim steward placeholder; policy objects carry owner field; hold-all | Engagement lead (Dinesh Naik) | Stage 25 / 34 | OPEN, accepted |
| DR-02 | Declared source contract is unenforced and 0 of 8,567 payloads satisfy it | data-contracts (key-set query) | H | M | Intake validator per version; quarantine; decide envelope vs payload | Engagement lead (Dinesh Naik) | Stage 12 / 21 | OPEN |
| DR-03 | Baseline custody: git-ignored data, test-residue provenance, mtime offset | DF-03/04; OD-03a | M | H | Backup manifest (1,512 files, re-verified); fixture manifest; sandbox-only execution | Engagement lead (Dinesh Naik) | Stage 14 | MITIGATED partly |
| DR-04 | Evidence/case linkage mostly absent (feeds 97.98%, docs 97.5% orphan) -> empty evidence packs, misleading rates | DQ-06/07 | H | M | Crosswalk with no guessing; orphan reporting as measure; SDR-01 | Engagement lead (Dinesh Naik) | Stage 12 / 14 | OPEN |
| DR-05 | Unit vocabulary inconsistency (`pct`/`percent` etc.) | DQ-09 | M | M | Derived normalised column + mapping table; raw kept | Engagement lead (Dinesh Naik) | Stage 12 | OPEN |
| DR-06 | Money parsed silently/lost (Java skips unparsable; 21 odd vendor amounts) | DQ-10; DM-17 | M | H | Text+decimal; reason code; no silent skips | Engagement lead (Dinesh Naik) | Stage 12 / 14 | OPEN |
| DR-07 | Identifier defects (`GXP--` double hyphen on 2,400 vendor rows; `UNKNOWN-0` refs) | DQ-11 | M | M | Flag; documented mapping; original retained | Engagement lead (Dinesh Naik) | Stage 12 | OPEN |
| DR-08 | Late/missing/invalid-date data (e.g. `2023-02-29`; arrival vs event) undetected | DQ-12/13 | M | M | Validators; late-arrival flag; thresholds Unknown | Engagement lead (Dinesh Naik) | Stage 14 | OPEN |
| DR-09 | In-place status mutation loses history (feeds; case snapshot) | LN-03/04 | H | H | Append-only events/outcomes (ADR-004/008) | Engagement lead (Dinesh Naik) | Stage 12 / 15 | DESIGNED (PROPOSED ADRs) |
| DR-10 | Cross-vocabulary conflation of "CLOSED" (4+ vocabularies) | knowledge-model K2 | M | H | Vocabulary registry; no auto-mapping; mapping = Zone H policy | Engagement lead (Dinesh Naik) | Stage 12 / 34 | OPEN |
| DR-11 | Premature adoption of a definition (closed/48 h) drives wrong KPIs | OPD-01/02/03; OD-07 | M | H | Candidate-only policy objects; tag every figure; refuse mixed-tag math | Engagement lead (Dinesh Naik) | Stage 13 / 34 | DESIGNED |
| DR-12 | Access control not enforced today (no authn; `restricted` data readable) | metadata-model M4; PNFR-07 | H (today) | H (if real) | authn/RBAC deny-by-default (ADR-013), filter-before-rank | Engagement lead (Dinesh Naik) | Stage 24 / 25 | OPEN |
| DR-13 | Retention policy unset; hold-all may cause unbounded growth; legal hold semantics unknown | OPD-09; `retention_events` | M | M | No-delete rule; archive only by human decision | Engagement lead (Dinesh Naik) | Stage 25 | OPEN, accepted |
| DR-14 | Untrusted text (instruction-like strings, markup, FTS operators) reaches a decision path or UI unescaped | DF-08; PNFR-13 | M | H | Untrusted typing, escaping, grammar-parsed queries, fixture release gate | Engagement lead (Dinesh Naik) | Stage 14 / 24 / 26 | DESIGNED |
| DR-15 | FTS5 unavailable on target runtime or poor ranking/Hindi tokenisation; unmeasured | RT-01/03; U-11-18 | L | M | Fallback inverted index; SDR-03 ground truth; Stage 12/14 check | Engagement lead (Dinesh Naik) | Stage 12 / 14 | PARTLY RESOLVED (dev device) |
| DR-16 | AI creep (model call added silently, or T3 Q&A pressure) | ADR-002; OD-08 | L | H | Deny-list CI, no-egress, Stage 32 tripwire = 0; RQ gate | Engagement lead (Dinesh Naik) | Stage 29 / 32 | DESIGNED |
| DR-17 | Growth far above assumed volumes breaks single-file SQLite | CP-06; H-14 | L | M | Scale tier SDR-09; ADR-004 Postgres trigger | Engagement lead (Dinesh Naik) | Stage 31 / 33 | OPEN |
| DR-18 | Provenance chain only tamper-evident, anchor undecided | PR-04; ADR-005 | M | M | External anchor decision | Engagement lead (Dinesh Naik) | Stage 12 / 24 | OPEN |
| DR-19 | Synthetic fixtures insufficient to verify target behaviour; cannot validate vs reality | SD-01/04 | H | M | SDR-01..10 authored with ground truth; labelling | Engagement lead (Dinesh Naik) | Stage 14 / 17 | OPEN |

### Completion Gate evaluation (honest)

| Gate condition | Result | Evidence / note |
|---|---|---|
| Every source has an owner and contract (or documented gap) | MET AS DOCUMENTED GAP | `data-source-inventory.md` (interim steward placeholder; real owners Unknown); contracts in `data-contracts.md`; DS-03 contract unenforced (DR-02) |
| PII and access controls defined | MET (design) | `metadata-model.md` M2-M5; enforcement not built (DR-12) |
| Retrieval and context design includes provenance and citation | MET | `retrieval-strategy.md` RS-8, `provenance-policy.md` PV-1..PV-11; context engineering N/A by OD-08 |
| All required artifacts exist | MET | 12 files in `docs/11-data-context/` with the required header and section skeleton |
| Critical gaps resolved or documented | MET | DR-01, DR-04, DR-12, DR-13 documented with owner/stage |
| Evidence supports conclusion | MET | read-only queries; FTS5 sandbox test; checksum manifest verified |
| Blocking conditions for Stage 12 | NONE identified | open items are non-blocking design inputs for Stage 12 |

**Proposed gate status: CONDITIONAL PASS.** Not PASS because ownership, retention, definitions, real-data availability and the contract scope remain Unknown/OPEN (DR-01, DR-02, DR-13); none blocks Stage 12 schema specification, which can model them as configuration/policy objects.

### Conditions carried forward (non-blocking)

| ID | Condition | Owner | Due stage |
|---|---|---|---|
| CND-11-01 | Decide what the declared source contract validates (envelope vs payload) and contract-version policy | Engagement lead (Dinesh Naik) | 12 |
| CND-11-02 | Confirm interim steward placeholder or assign real owners | Engagement lead (Dinesh Naik) | 25 |
| CND-11-03 | Retention policy (OPD-09) and legal-hold authority | Engagement lead (Dinesh Naik) | 25 |
| CND-11-04 | Confirm/decline FTS5 on target runtime; ground-truth set creation | Engagement lead (Dinesh Naik) | 12 / 14 |
| CND-11-05 | Confirm classification scheme and role-to-access_level mapping | Engagement lead (Dinesh Naik) | 24 |
| CND-11-06 | Record erratum ER-11-01 (financial_adjustments USD only) against Stage 0A DF-07 | Engagement lead (Dinesh Naik) | next 0A-consuming stage |

## Evidence References

All other Stage 11 artifacts; `initial-risk-register.md` (R-01..R-09); `architecture-risk-register.md`.

## Assumptions

- A-11-18: Likelihood/impact ratings are expert judgement, not measured.

## Unknowns

- U-11-27 Real-data availability (none; all synthetic). U-11-28 Regulatory regime (OPD-16).

## Unresolved Issues

- OPD-01, OPD-02, OPD-04, OPD-09, OPD-15, OPD-16 remain open (accepted-open per OD-09 note for Q-02-05).

## Residual Risks

- Highest residual: DR-01, DR-04, DR-12, DR-19.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial risk register and gate evaluation. |
