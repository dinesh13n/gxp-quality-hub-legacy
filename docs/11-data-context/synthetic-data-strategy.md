---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "synthetic-data-strategy.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/operating-contract/data-use-constraints.md SD-1..SD-3, P-1..P-5, X-1..X-6", ".fde/orchestrator-decisions.md OD-03a, OD-04, OD-08, OD-09", "data/lake/tiny/manifest.json", "data/archive_documents/manifest.json", "data/documents/source_documents.jsonl", "docs/07-repo-assessment/characterization-test-plan.md", "docs/11-data-context/data-quality-rules.md", "docs/11-data-context/retrieval-strategy.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** No real data exists or may be introduced (X-2, OD-04); everything the engagement builds and tests uses synthetic data. This strategy fixes (1) the **baseline fixture** (shipped 125 cases, seed 4100; OD-09), (2) the **additional synthetic sets** required because the shipped corpora are too homogeneous or too orphaned to exercise the target design, (3) rules for generating, labelling, checksumming and isolating them. No generator is run or modified in this documentation-only stage; generation is a Stage 14/17 BUILD-time activity in an isolated copy (OD-03a).

## Findings

### S1. Baseline fixture (frozen)

| Item | Value | Class |
|---|---|---|
| Dataset | shipped `data/legacy.sqlite3` (125 cases; sha256 `c254649f…d70aa`), `enterprise_legacy.sqlite3`, tiny lake, documents JSONL, archive | [VF] |
| Seed | 4100 (OD-09); lake tiny seed 7421 (manifest) | [VF] |
| Status | Baseline confirmed by Dinesh (OD-09); the README 6,000-case/seed-4326 set is **not** baseline | [VF] decision |
| Use | Characterisation goldens, quality-rule regression (DQ values in `data-quality-rules.md`), replay fixtures | [INF] |
| Weakness | test-fixture residue; orphans; 3-sentence corpus; one dataset only | [VF] |

### S2. Synthetic data requirements (SDR) not met by the baseline

| ID | Requirement | Why (evidence) | Used by | Size/shape (proposed) |
|---|---|---|---|---|
| SDR-01 | **Linked estate fixture**: cases, batches, deviations, CAPAs, feeds and documents with *intentional* unique, none and ambiguous crosswalk keys, with known expected link table | 98% feed orphans; 97.5% doc orphans; no key from case to batch (ADR-009) | FR-ID-01..04 tests | ~200 cases; link outcomes stated as ground truth |
| SDR-02 | **Idempotency/replay set**: identical re-delivery, changed-content re-delivery, out-of-order, late, missing business_key, unsupported rev | 67 REPLAY rows are all marked DUPLICATE without comparison | FR-INT-02/03/08, PNFR-11 | ~100 feed items with expected outcome per item |
| SDR-03 | **Retrieval ground truth**: diverse multilingual document bodies (>= dozens of distinct topics), queries with known relevant doc_ids, access-level mix, versions with supersession | corpus has 3 base sentences | RT-03, AT-1..AT-6, RQ-1 baseline | >= 300 documents, >= 50 queries (matches RQ-1 order of magnitude; Assumption) |
| SDR-04 | **Untrusted-text fixture** (existing + extended): reuse 86 feed / 22 doc / 9 evidence / archive / lake strings; add delimiter, markup, SQL/FTS-operator, path-like and very-long variants | DF-08; PNFR-13 | PNFR-13, AT-2, AT-4 | existing set + variants |
| SDR-05 | **Event history set**: cases with full lifecycles including reopen with and without events, closure with/without evidence, multiple definition candidates | 8 REOPENED with 0 reopen events; 2 event types | FR-DEC-01..06, FR-MET-03 | ~100 case histories |
| SDR-06 | **Money/units set**: unit synonyms, negative, empty, comma/decimal variants, multi-currency | `pct`/`percent`; 21 odd `amount_text`; INR/USD | FR-MET-04, DQ-09/10 | ~200 rows |
| SDR-07 | **Policy conflict set**: same case through the three divergent rule sets, unknown region/year | RC-4; 999,999 default | FR-POL-04..06, FR-CO-01 | ~60 inputs |
| SDR-08 | **Access/tenant set**: users per role, documents per `access_level` and tenant | no auth/role data exists | PNFR-07/12, MA-3 | 6 roles x 4 tenants |
| SDR-09 | **Scale tier**: regenerated larger estate (e.g. the documented 6,000-case/seed-4326 generator) for performance/capacity measurement only, labelled "scale tier, not baseline" | H-14 SQLite contention unmeasured; OPD-14 | PNFR-06, ADR-004 trigger | 6,000 cases, sandbox only |
| SDR-10 | **Encoding set**: es/de/ja/hi/pt strings, combining characters, NFC/NFD variants | DQ-22 | retrieval, UI | ~100 strings |

### S3. Generation and handling rules

- SG-1 Deterministic: every set is produced by a named script with a recorded seed and version; the manifest stores command, seed, counts and sha256 per file (pattern of `data/lake/tiny/manifest.json`).
- SG-2 Location: new fixtures live under a dedicated fixtures path created in a BUILD stage; generation runs only in a full repo copy outside the working tree (OD-03a); working-tree `data/` is never written (X-1).
- SG-3 Labelling: each fixture and any output derived from it carries "synthetic, unvalidated" (PNFR-20); identifiers use non-routable patterns (`example.invalid`, `actor-N`, `ACCT-n`).
- SG-4 No real-derived data: no copying, perturbing or "realistic-izing" of any real record; no scraping; names are not generated at all unless a requirement needs them (none now). Mitigates re-identification (nothing to re-identify).
- SG-5 Ground truth is authored with the data (expected links, expected outcomes), not inferred from product output.
- SG-6 Realism limits are documented: synthetic distributions (uniform status counts ~2,080 each in the enterprise DB; modelled costs) do not support any real-world KPI claim (OD-07, FR-MET-06).
- SG-7 Fixtures are small enough to be git-tracked (text/CSV/JSONL); SQLite binaries stay generated and git-ignored (X-6, HAR-09).
- SG-8 Fixture changes are versioned; goldens are never re-baselined silently (CC-05/06).
- SG-9 Adversarial fixtures are stored as fenced, labelled data; never quoted in prompts or documentation except as labelled examples (P-4).

### S4. Findings

| ID | Finding | Evidence | Impact | Risk | Conf. | Class |
|---|---|---|---|---|---|---|
| SD-01 | The shipped baseline is sufficient for characterisation/regression but insufficient for 10 of the target capabilities listed in SDR-01..10. | S2 evidence | Without new fixtures, ADR-009/008/012 behaviour cannot be verified | High | High | [INF] |
| SD-02 | Generators exist in repo (`generate`, `domain_data`, `partner_feeds`, `historical_fixture`, `generate_documents`, `archived_documents`) but several write repo-relative `data/` paths and are destructive to working-tree data (DM-12). | DM-12; DF-02 | Reuse only inside a sandbox copy, or write new fixture generators with explicit output paths | High | High | [VF] |
| SD-03 | Production data is not permitted and does not exist; synthetic-only is therefore a permanent condition, not a stopgap, until OPD-16 is answered. | OD-04 | All claims stay 'synthetic, unvalidated' | Medium | High | [VF] |
| SD-04 | Quality of synthetic data cannot be validated against reality (no real counterpart). | OD-04 | Thresholds and rates are engineering proposals only | Medium | High | [VF] |

## Evidence References

Manifests (`data/lake/tiny/manifest.json`, `data/archive_documents/manifest.json`); data profile queries; DM-12; DU/SD constraints from Stage 0B.

## Assumptions

- A-11-16: Fixture sizes in S2 are adequate for functional verification, not for statistical claims. Confirm: Engagement lead (Dinesh Naik), Stage 14.
- A-11-17: Using the documented 6,000-case generator purely as a scale tier does not conflict with OD-09 (baseline unchanged). Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- U-11-25 Whether any real (even anonymised) sample will ever be available (would need a new contract). U-11-26 Whether Dinesh wants fixtures tracked in git (HAR-09).

## Unresolved Issues

- Fixture generator ownership and location decided in Stage 14/17.

## Residual Risks

- DR-19 (insufficient test data), DR-02, DR-04.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial synthetic data strategy. |
