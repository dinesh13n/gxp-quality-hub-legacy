---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "data-protection-controls.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/*.py", "tests/hub/test_tst_hub_stg24_*.py", "docs/24-security-privacy/evidence/", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
Controls that protect data at rest, in use and in transit, as built. Retained-table protection was the main gap: the Stage 15 scan guarded 18 tables while the live store has 44 (39 retained, 3 mutable, 2 derived); Stage 24 added a single disposition register that the scan, release gate and tests all read. 345 columns now carry a class; credential columns are all C3. Transport is loopback HTTP only; there is no encryption at rest.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DP-1 At rest [Verified Fact]
| Control | Detail | Test |
|---|---|---|
| Table disposition register | `hub/security/tables.py`: 44 tables classified; must equal the live M000..M007 store | S01 |
| Scan uses the register | `scan.py` derives `RETAINED_TABLES` (39) from it | S02 |
| Product delete sites reviewed | only 4 sites (`case_state`, `active_ruleset` x2, `run_lock` x3, `search_doc` x2 counts) | S03 |
| Delete refused on retained tables | 28 populated retained tables exercised | S04, `evidence/delete-refusal.json` |
| Credentials | PBKDF2 hash + salt; tokens stored as SHA-256 digest only | TST-SEC-04, -08 |
| Backups | checksum manifest verified before restore; `data/` untouched, SHA256SUMS rc 0 before and after | TST-CO-07, -09 |
| Anchor seal | opt-in HMAC chain; detects edit or truncation of the anchor file by someone without the key | S26 |
| Encryption at rest | **none** (file permissions of the host only) | Unknown whether required |
### DP-2 In use [Verified Fact]
Class readers (C3: quality_lead, compliance, dispositioner), audited reasons, finance masking function (route unreachable), restricted documents filtered before ranking, errors carry no stack or SQL, logs redact credential patterns, secret scan over code, tests and these docs (S33).
### DP-3 In transit [Verified Fact]
Loopback only; non-loopback bind refused unless an exposure setting exists (SC-11); no TLS in the product. If `network.tls` settings are supplied the cookie gains `Secure` (S24 test); the server itself does not terminate TLS today. [Inference] TLS should terminate at a proxy at Stage 27 if exposure is ever approved.
### DP-4 Gaps [Inference]
Mutable tables `active_ruleset`, `run_lock`, `schema_migrations` (the last has no trigger), derived `case_state`; unsealed anchor by default; no encryption; no retention period; erasure conflicts with insert-only history.

## Evidence References
`hub/security/tables.py`, `hub/security/datamap.py`, `hub/security/anchor_seal.py`, `evidence/store-table-dispositions.json`, `evidence/delete-refusal.json`, `evidence/field-map.json`, `evidence/anchor-seal.json`, `evidence/cookie-attributes.json`.

## Assumptions
- A-S24-DP-1 Hold-all retention (OD-30) stays until a retention period is decided. A-S24-DP-2 Anchor seal OFF by default is acceptable for the synthetic shadow phase.

## Unknowns
- U-S24-DP-1 Encryption-at-rest requirement. U-S24-DP-2 Key custody for the seal. U-S24-DP-3 Retention period.

## Unresolved Issues
- DQ-S24-02 (anchor strength), DQ-S24-08 (classes, retention).

## Residual Risks
RS-01, RS-03, RS-06, RS-12.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
