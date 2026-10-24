---
stage: "24 — Security + Privacy + Responsible AI by Design"
artifact: "privacy-impact-assessment.md"
version: "v0.1"
date: "2026-10-24"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/*.py", "hub/web/*.py", "hub/gate/", "hub/r2/protection.py", "hub/core/untrusted.py", "hub/guards/", "tests/hub/test_tst_hub_stg24_*.py", "docs/24-security-privacy/evidence/", "docs/12-specs/security-spec.md", "docs/16-repo-validation/security-scan-summary.md", ".fde/orchestrator-decisions.md", "docs/00-preflight/operating-contract/data-use-constraints.md", "docs/25-governance/evidence-retention-policy.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT / IN REVIEW: nothing here is an approval. Control VALUES are PROPOSALS (DQ-09 is not decided). No residual risk is accepted: the owner for every item is the Engagement lead (Dinesh Naik); acceptance would be his recorded decision (OD log). The product is No-AI (OD-08); zone_h.holders ships EMPTY; authority switches stay CLI + approval_ref (OD-31).**

## Summary
Privacy impact of the hub as built. The estate is synthetic (DU-01): no real person, patient, employee or customer is in the repository. The hub still holds personal-data analogues (pseudonymous user and actor ids, free text) and, in a real deployment, would hold personal data; this assessment treats them as if Confidential (DU-02) so that the design is production-valid. 345 store columns are classified (C1 125, C2 161, C3 59); 13 column names carry a staff identifier; 5 columns hold credential material (all C3). No privacy regime is assessed because none is identified (U-11-17). The overall privacy risk for the synthetic shadow deployment is Low; for a real deployment it is Unknown until the questions in PI-6 are answered.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### PI-1 Data inventory [Verified Fact: columns from the live M000..M007 store; classes are Assumption A-11-02]
| Category | Where | Class | Personal-data analogue? | Notes |
|---|---|---|---|---|
| Credentials | `principal.pw_hash`, `pw_salt`; `session.token_sha256`; `service_token(.revocation).token_sha256` | C3 | no (secret) | PBKDF2 hash with per-user salt; token digests only, token shown once |
| Staff identifiers | `actor`, `created_by`, `recorded_by`, `granted_by`, `resolved_by`, `attached_by`, `revoked_by`, `triggered_by`, `creator`, `owner`, `principal_id`, `holder_check_ref`, `authority_ref` | C2 (C3 in `audit_log`, `principal`, `session`, `login_attempt`) | yes (A-11-10) | pseudonymous ids (`rev`, `actor-N`); no directory join |
| Free text | `reason`, `notes`, `body`, `payload`, `replacement`, `details`, `fields`, `inputs` ... | C2 | may carry anything | Untrusted; escaped on output; never interpreted |
| Case and quality data | decision events, evidence, intake, rule traces, metrics | C2 / C1 | quasi-identifiers (`account_id`, case ids) | synthetic |
| Documents | `search_doc` (derived) | C2 or C3 by `access_level`; unknown = restricted | free text | 328 of 1,200 documents restricted |
| Audit trail | `audit_log` | C3 | actor + reason | hash-chained, insert-only, hold-all |
### PI-2 Flows [Verified Fact]
Inbound: partner feeds, documents, gateway (loopback), reviewer input. Outbound: none (egress guard; loopback only; no AI service receives any data, MA-4). Storage: one SQLite file and an anchor file on the host, no encryption at rest (Unknown whether required). Exports: C3 reads and exports need a non-empty audited reason.
### PI-3 Privacy-by-design controls [Verified Fact unless marked]
| Principle | Control | Evidence |
|---|---|---|
| Data minimisation | stdlib hub holds only what the specs name; no third-party analytics; no telemetry leaves the host | S30, TST-CO-12, E24 |
| Purpose limitation | roles and class readers (`CLASS_READERS`): C3 only for quality_lead, compliance, dispositioner; finance sees masked identifiers (path unreachable today) | I9-NFR-12 |
| Access control | deny by default; documents filtered by `access_level` before ranking; missing level = restricted | I9, MA-1 |
| Accountability | every C3 read audited with the reason (header or query) | I9-SEC-20, S25 |
| Integrity | insert-only history; hash chain; opt-in seal | S01..S04, S26 |
| Confidentiality in logs | no credential key in audit details; log redaction; plaintext password / token / hash absent from audit | TST-SEC-15, S12 |
| Retention | hold-all; no delete path; period Unknown (OD-30) | S03 |
| Data subject rights (access, correction, erasure) | **not built**: insert-only design conflicts with erasure; no subject-access function | Unknown regime; see PI-6 |
### PI-4 Privacy risks [Inference]
| ID | Risk | L | I | Control | Residual |
|---|---|---|---|---|---|
| PR-01 | Actor ids (and free text) are personal data in a real deployment; the insert-only store cannot erase them | Medium | Medium | pseudonymous ids, hold-all is a decision not a law | RS-06 |
| PR-02 | `reason` in a URL (query form) reaches future proxy logs | Low (loopback) | Medium | header form added; query form retained | RS-09 |
| PR-03 | A real deployment adds direct identifiers (names, emails) | Medium | High | none; X-2 forbids real data today | RS-06 |
| PR-04 | No encryption at rest; backups copy everything | Low | Medium | file permissions (Unknown) | RS-12 |
| PR-05 | Finance masking untested over HTTP (route unreachable) | Low | Low | unit-level test I9-NFR-12 | RS-05 |
| PR-06 | No tenant dimension in the hub store (4 tenants in the enterprise estate) | Medium | High (if multi-tenant) | none | RS-06 |
### PI-5 Overall rating [Inference]
Synthetic shadow deployment: **Low**. Real data: **not rated** (regime, roles, retention and data subjects Unknown).
### PI-6 Questions for the Engagement lead
(a) Which privacy regime would apply (U-11-17: for example India DPDP, GDPR for German data)? (b) Retention period and erasure position (OD-30 hold-all is a placeholder). (c) Is encryption at rest required? (d) Are tenant boundaries needed in the hub store? (e) Who are the data subjects if real staff ids replace pseudonyms?

## Evidence References
`docs/24-security-privacy/evidence/field-map.json` (345 columns, class + tags), `evidence/store-table-dispositions.json`, `hub/security/datamap.py`, `hub/r2/protection.py`, `docs/11-data-context/metadata-model.md` M2..M4, `docs/00-preflight/operating-contract/data-use-constraints.md`, `docs/25-governance/evidence-retention-policy.md`.

## Assumptions
- A-S24-PI-1 Synthetic data means no legal privacy obligation applies today; this assessment is practice for a real deployment.
- A-S24-PI-2 The class of each column is the proposed C0..C3 (A-11-02), not an approved classification.

## Unknowns
- U-S24-PI-1 Applicable privacy regime and data subjects (U-11-17). U-S24-PI-2 Retention period. U-S24-PI-3 Encryption-at-rest requirement. U-S24-PI-4 Whether a data-subject request process is needed.

## Unresolved Issues
- DQ-S24-08 (field classes, tenant, regime, retention).

## Residual Risks
RS-06 (privacy regime / tenant / erasure), RS-09, RS-12.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-24 | claude-fde-agent | First issue (Stage 24). |
