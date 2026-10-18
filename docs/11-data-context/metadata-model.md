---
stage: "11 — Data, Knowledge & Context Strategy"
artifact: "metadata-model.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["data/documents/source_documents.jsonl access_level", "data/enterprise_legacy.sqlite3 access_audit, retention_events, organizations", "data/archive_documents (example.invalid headers)", "docs/00-preflight/operating-contract/data-use-constraints.md DU-02, DU-03, X-1..X-6", "docs/09-initial-prd/functional-requirements.md FR-SEC-01..03, FR-GATE-04", "docs/09-initial-prd/nfrs.md PNFR-07, PNFR-10, PNFR-12", "docs/10-architecture/security-architecture.md", "docs/10-architecture/adrs/ADR-013"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** Defines (1) the metadata every hub record and document carries, (2) a would-be **data classification scheme** and field-level PII/sensitivity map for the synthetic estate, and (3) an access-control matrix by role. All data is synthetic (README L44; DU-01); classification is applied *as if Confidential* so designs are production-valid (DU-02). The regulatory framing (GxP, 21 CFR Part 11) is **unconfirmed (OPD-16)** and is used only as design framing, not a compliance claim. Retention is **hold-all** until OPD-09 is decided. Access to restricted content today is unenforced: no authentication exists (PNFR-07 gap).

## Findings

### M1. Mandatory metadata (technical)

| Field | Applies to | Purpose | Class |
|---|---|---|---|
| `source`, `source_ref`, `source_hash` (sha256 of canonical content), `ingested_at`, `run_id`, `adapter_version` | every hub row and document version | lineage/provenance (see `provenance-policy.md`) | [INF] design |
| `schema_rev` / `contract_version` | intake records | contract validation | [INF] |
| `classification` (C0-C3 below), `access_level`, `tenant`, `site`, `region`, `locale` | records and documents | access control, filtering | [INF] |
| `effective_at`, `superseded_by`, `valid_from/valid_to` | documents, policy objects, rules, references | point-in-time retrieval | [INF] |
| `definition_tag`, `policy_version`, `synthetic_label` ("synthetic, unvalidated") | metrics | FR-MET-01, PNFR-20 | [INF] |
| `retention_class`, `legal_hold`, `retention_policy_ref` | records | hold-all until policy; legal hold overrides | [INF]; policy [UNK] |
| `trust` = `trusted_structured` / `untrusted_text` | every field | untrusted-text handling (below) | [INF] |
| `ocr_confidence` (nullable) | OCR-derived documents | reliability flag; NULL = unknown | [VF] field |

### M2. Classification scheme (WOULD-BE, [Assumption] A-11-02; Stage 24 decides)

| Class | Meaning | Synthetic examples |
|---|---|---|
| C0 Public | none in estate | - |
| C1 Internal | operational data without people/finance | `materials`, `sop_versions`, `reference_versions`, lake `master_data` |
| C2 Confidential | identifiers of people/accounts/tenants, financial, evidence | `cases.account_id`, `access_audit.actor`, `workflow_tasks.assigned_to`, `financial_adjustments`, `retention_events` (legal_hold), `partner_feeds`, `vendor_file_rows`, documents with `engineering/quality/operations` |
| C3 Restricted | highest sensitivity | documents with `access_level=restricted` (328 of 1,200); anything under legal hold (123 `legal_hold=1`); audit trail |

### M3. Field-level PII / sensitivity map (Verified Fact on presence; classification is Assumption)

| Store.column | What it is | Indicator | Would-be class | Handling in product |
|---|---|---|---|---|
| `cases.account_id` | `ACCT-nnnnnn` pseudonymous account | quasi-identifier | C2 | shown to authorised roles only; masked in exports to finance unless needed |
| `access_audit.actor`, `state_history.actor`, `workflow_tasks.assigned_to`, `policy_exceptions.actor`, `capa_actions.action_owner` | `actor-N`/`user-N`/team strings | personal-data analogue | C2 | pseudonymous IDs only; no directory join |
| `.eml` From/To (`*@example.invalid`) | addresses | contact data analogue | C2 | `example.invalid` guaranteed non-routable; body treated Untrusted |
| `source_documents.body`, `risk_note`, `narrative`, `notes` | free text | may carry instructions (DU-03), may carry PII in real life | C2/C3 by `access_level` | Untrusted; escaped; never interpreted |
| `organizations.name`, `tenant` | org/tenant | tenancy boundary | C2 | tenant filter mandatory on queries (4 tenants in enterprise DB) |
| `financial_adjustments.amount`, `vendor_file_rows.amount_text`, `operating_costs.*` | money | financial | C2 | finance (read) role; exact decimal |
| `retention_events.legal_hold`, `expiry_date` | records-management | legal | C3 | read-only; changes are Zone H events |
| `access_audit` (4,167 rows; 220 empty `access_reason`) | access log | audit | C3 | product-written audit must be non-empty (DQ-15) |
| `ocr_confidence`, `locale`, `version` | technical | none | C1 | - |

[Verified Fact] no real names, patient or employee data were found (DF-07). [Unknown] whether real data would add direct identifiers (names, emails, employee IDs); out of scope (X-2).

### M4. Access-control matrix (PROPOSED; roles from FR-SEC-01; role-holders are Unknown, FR-GATE-04 ships empty)

| Data / action | Reviewer | Quality lead | Compliance | Finance (read) | Integration | Authorised dispositioner |
|---|---|---|---|---|---|---|
| C1 operational | R | R | R | R | R | R |
| C2 cases / evidence / feeds | R, annotate | R/W (non-Zone H) | R | R masked | R/W intake only | R |
| C3 restricted documents (`restricted`) | no | R if named | R | no | no | R |
| `access_level` = engineering / quality / operations documents | per level mapping (ASM) | R | R | no | no | R |
| Audit trail | no | R | R | no | no | R |
| Policy objects | R | R | R/propose | R | no | adopt (Zone H) |
| Retention / legal hold | no | R | R | no | no | change (Zone H) |
| Quarantine queue | R, route | R/W | R | no | R/W | R |

- MA-1 Deny by default; missing `access_level` or `classification` = `restricted` (A-11-04).
- MA-2 Every read of C3 and every export is written to the audit trail with a non-empty reason (DQ-15).
- MA-3 Search results are filtered by `access_level` and `tenant` **before** ranking and snippet generation; counts never reveal restricted hits (see `retrieval-strategy.md`).
- MA-4 No AI service receives any data (FR-CO-04); egress is loopback only (ADR-002/015).
- MA-5 Mapping of document `access_level` values to roles is Assumption A-11-09 (no role model exists in the repo).

### M5. Untrusted-text handling (inventory-backed)

- MU-1 Fields typed Untrusted: `partner_feeds.raw_json.notes`, `source_documents.body`, archive bodies, `evidence_events.payload`, lake `narrative`/`risk_note`, `source_messages.body`, `gateway_inbox.raw_payload`, `vendor_file_rows.payload`.
- MU-2 Count of known instruction-like strings (Verified Fact): 86 feed rows; 22 of 1,200 document bodies (9 + 5 + 8 variants); 9 enterprise evidence payloads; >=4 archive docs; 15 tiny and 150 bundled lake events.
- MU-3 Untrusted values are stored verbatim, HTML-escaped on output, length-bounded for display, never concatenated into SQL, shell, file paths or templates, and never read by rule/policy code. They are findable by search (they are data) and displayed with an "untrusted source text" marker.

### M6. Retention metadata

- MR-1 [Verified Fact] No retention job/code exists; `retention_events` has 2,084 rows all class `standard`, expiries 2027+, 123 under legal hold.
- MR-2 [Inference] Until OPD-09 is decided: no deletion paths are coded; archive copies are the only reduction mechanism and only by human decision.
- MR-3 [Unknown] Retention periods, legal-hold authority, and disposal evidence requirements.

## Evidence References

`source_documents.jsonl` (`access_level` counts: restricted 328, operations 295, engineering 305, quality 272); `enterprise_legacy.sqlite3` `retention_events` (123 holds), `access_audit` (220 empty reasons); DF-07, DF-08; `docs/10-architecture/security-architecture.md`.

## Assumptions

- A-11-09: Role-to-`access_level` mapping above is a proposal; no role model exists. Confirm: Engagement lead (Dinesh Naik), Stage 24.
- A-11-10: Pseudonymous `actor-N` IDs would be personal data in a real deployment.

## Unknowns

- U-11-15 Real classification policy (U-15). U-11-16 Real roles and holders. U-11-17 Applicable privacy regime (e.g. India DPDP, GDPR for DE data) - not assessed.

## Unresolved Issues

- Access control cannot be tested until authn/RBAC (ADR-013) exists (Stage 24/25 owns).

## Residual Risks

- DR-12 (no enforced access today), DR-13 (retention unset), DR-14 (untrusted-text leakage).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial metadata, classification, access matrix. |
