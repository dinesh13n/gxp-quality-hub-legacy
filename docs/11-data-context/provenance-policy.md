---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "provenance-policy.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/11-data-context/lineage-map.md", "docs/11-data-context/metadata-model.md", "docs/09-initial-prd/functional-requirements.md FR-DEC-04, FR-REV-01, FR-REV-03, FR-GATE-02, FR-MET-06, PNFR-20", "docs/10-architecture/adrs/ADR-005-audit-trail-tamper-evidence.md", "docs/10-architecture/adrs/ADR-008-intake-pipeline.md", "docs/10-architecture/adrs/ADR-012-reviewer-search.md", "data/lake/tiny/manifest.json", ".fde/orchestrator-decisions.md OD-06, OD-09"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** Defines what provenance every stored, displayed, searched or reported item must carry, and what a **citation** is in a No-AI product: a *machine-verifiable pointer to the exact stored source record* (not a model-generated reference). This satisfies the stage guardrail "no retrieval without provenance and citation". Provenance fields are designed into the hub store; the as-found legacy stores largely lack them (LN-01), so legacy data is cited by path + table + key + the baseline checksum.

## Findings

### P1. Provenance record (minimum)

| Field | Definition | Required for |
|---|---|---|
| `source_system` | adapter id (e.g. `legacy.partner_feeds`, `docs.jsonl`, `archive.eml`) | all ingested rows |
| `source_locator` | file path + table/line + primary key (`data/documents/source_documents.jsonl#DOC-00000000`) | all |
| `source_version` / `schema_rev` | document version (`revB`, `v2`) or contract revision | documents, feeds |
| `source_hash` | sha256 of the canonical raw content | all |
| `fetched_at` / `ingested_at` | UTC, adapter clock | all |
| `run_id`, `adapter_version` | run record reference | all |
| `dataset_ref` | for synthetic baseline: commit `a6eb4e8` (tag `baseline-as-found`), seed 4100, DB sha256 (`c254649f…d70aa` for `legacy.sqlite3`) | fixtures, KPI outputs |
| `trust` and `synthetic_label` | trusted_structured / untrusted_text; "synthetic, unvalidated" | outputs |

### P2. Citation rules

| Rule | Statement | Class |
|---|---|---|
| PV-1 | A **citation** = `(doc_id | table+key, version, source_hash prefix 12, effective_at, source_locator)`; it must resolve to exactly one stored record, verifiable by recomputing the hash. | [INF] |
| PV-2 | Every search hit, evidence-pack item, rule trace, queue row and metric displays or links its citation. An item without provenance is not displayed as evidence (it appears as "unsourced" only to administrators). | [INF] |
| PV-3 | Metrics cite inputs by definition tag, policy version, window, denominator, exclusions and run_id; a drill-down lists contributing record ids (FR-MET-06, PNFR-16). | [INF] |
| PV-4 | Rule outputs cite rule set, row id, version and the input values used (FR-REV-01). | [INF] |
| PV-5 | Decision events cite evidence refs and basis (FR-DEC-01/04). Zone H decisions additionally cite the human actor and authority reference (FR-POL-03). | [INF] |
| PV-6 | Citations are never generated from text content; they are looked up from keys. Text inside documents (including "SYSTEM NOTE", "IGNORE PREVIOUS INSTRUCTIONS…") can neither create nor alter a citation. | [INF] ADR-002 |
| PV-7 | A superseded document keeps its citation valid; the view shows `superseded_by`. | [INF] |
| PV-8 | If the cited source is later found corrupted (hash mismatch), the item is flagged "provenance broken" and withheld from decision packs until a human resolves. | [INF] |

### P3. Integrity of provenance

- PV-9 Provenance rows are append-only and included in the audit hash chain (ADR-005, PROPOSED). Hash chain is tamper-*evident*, not tamper-proof (single-file SQLite; DBA could rewrite; mitigated by external anchor, ADR-005).
- PV-10 Baseline custody: the pre-existing checksum manifest (all 1,512 files) is the reference; this stage re-verified it after read-only inspection (`sha256sum -c --quiet`, exit 0).
- PV-11 Legacy data without row-level provenance is wrapped by the adapter at read time with `source_locator` and hash of the row's canonical serialisation; provenance is then "as read at time T", not "as authored".

### P4. Findings

| ID | Finding | Evidence | Impact | Risk | Conf. | Class |
|---|---|---|---|---|---|---|
| PR-01 | Legacy tables lack provenance columns; only `partner_feeds`, `gateway_inbox` and lake manifests carry partial source info. | lineage LN-01/02 | Provenance for legacy rows can only be adapter-asserted | Medium | High | [VF] |
| PR-02 | The baseline's own provenance is a test-run residue with an unexplained mtime offset. | DF-03/04 | Citations of the baseline must say "shipped fixture, test-derived" | Low | High | [VF]/[UNK] |
| PR-03 | Citation to a case from a document is mostly impossible today (30 of 1,200 resolve). | queries | Evidence packs will show "no linked case" for most documents | Medium | High | [VF] |
| PR-04 | Tamper-evidence is only as strong as the external anchor (ADR-005 PROPOSED); not yet decided or built. | ADR-005 | Provenance integrity claim limited | Medium | Medium | [INF] |
| PR-05 | The lake `manifest.json` records `sha256_partner_export`, which can be checked for the CSV only; other lake files have no per-file hash except via the backup manifest. | `data/lake/tiny/manifest.json` | Verified partially | Low | High | [VF] |

## Evidence References

`data/lake/tiny/manifest.json` (seed 7421, sha256 of CSV); `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` exit 0 (2026-10-18, after this stage's read-only queries); ADR-005/008/012; OD-06/OD-09.

## Assumptions

- A-11-15: sha256 over canonical serialisation is acceptable as `source_hash`. Confirm: Engagement lead (Dinesh Naik), Stage 12.

## Unknowns

- U-11-23 Whether regulated record requirements (e.g. Part 11 audit expectations) apply (OPD-16). U-11-24 External anchor mechanism (ADR-005).

## Unresolved Issues

- Hash-chain anchoring choice (ADR-005) is PROPOSED; provenance integrity design depends on it.

## Residual Risks

- DR-03, DR-04, DR-18.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial provenance and citation policy. |
