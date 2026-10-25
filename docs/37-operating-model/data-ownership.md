---
stage: "37 — Target Operating Model + RACI + Ownership"
artifact: "data-ownership.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["data/ (125-case legacy.sqlite3, seed 4100), ../_data-backup-2026-10-17/SHA256SUMS.txt", "docs/11-data-context/", "docs/24-security-privacy/{data-protection-controls,privacy-impact-assessment}.md", "docs/25-governance/{evidence-retention-policy,compliance-obligations}.md", "docs/21-integration/data-contracts.md", "docs/02-stakeholders/stakeholder-map.md SH-14", ".fde/orchestrator-decisions.md OD-02, OD-03, OD-03a, OD-09, OD-15, OD-28, OD-30, OD-32"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. The only human is Dinesh Naik, Engagement lead (OD-04). No owner, acceptance, approval or role holder is invented here. "Interim" ownership is a default placement for completeness and is NOT an accepted steady-state assignment. Nothing in this stage accepts a risk (HAR-11, TP-14).**

## Summary
All data in and around the hub is **synthetic and generated in-repo** (baseline `data/legacy.sqlite3`, 125 cases, seed 4100, OD-09; no real enterprise systems, endpoints, credentials or SLAs: OD-28 (a)). No data subject, source-system owner, retention authority or privacy regime has been identified (OD-32: field classes, tenant, regime and retention are to be decided before real data). The ownership position is therefore: **data owner roles are VACANT; Dinesh Naik is interim custodian for the synthetic data and the evidence data; STOP-04 blocks real data until a data owner exists and a decision is recorded.** Retention is hold-all by default (OD-15, OD-30) with no authority to dispose.

## Findings
### DO-1 Data domains
| ID | Data domain | Location (evidence) | Origin | Custodian | Data owner role | State | Tag |
|---|---|---|---|---|---|---|---|
| DD-01 | Legacy baseline DB (cases, as-found) | `data/legacy.sqlite3`, sha256 c254649f…d70aa (OD-02, OD-09) | synthetic | Dinesh (INTERIM) | RL-07 | VACANT | [Verified Fact] |
| DD-02 | Checked backup and manifest | `../_data-backup-2026-10-17/`, `SHA256SUMS.txt` (1,512 lines; OD-03a) | copy of DD-01 and `data/` | Dinesh (INTERIM) | RL-07 | VACANT | [Verified Fact] |
| DD-03 | Hub operational data: cases, decisions, runs, reviewer queue, rule sets | hub SQLite stores | derived from DD-01/DD-04 | Dinesh (INTERIM) | RL-03 for definitions, RL-07 for data | VACANT | [Verified Fact] |
| DD-04 | Source feeds: partner feed, vendor CSV, gateway payloads (86 feed rows) | `services/source_gateway/`, `app/partner_feeds.py`, `hub/intake/` | synthetic | Dinesh (INTERIM) | RL-08 contract; RL-07 content; sources SH-14 unnamed | VACANT | [Verified Fact] |
| DD-05 | Audit trail and decision chain, anchor | `hub/security/audit.py`; anchor file path in config (OD-15) | produced by hub | Dinesh (INTERIM) | RL-05 / RL-06 | VACANT | [Verified Fact] |
| DD-06 | Documents/corpus for R2 search (22 injection docs, 10 variants) | `hub/r2/`, fixtures | synthetic | Dinesh (INTERIM) | RL-07 | VACANT | [Verified Fact] |
| DD-07 | Regenerable alternative dataset (6,000 cases, seed 4326) | README; not part of the baseline (OD-09) | regenerable | Dinesh (INTERIM) | RL-07 | VACANT | [Verified Fact] |
| DD-08 | Evidence data: goldens, test outputs, regression logs | `tests/`, `docs/*/evidence/` | engagement | Dinesh (INTERIM) | RL-02 | VACANT | [Verified Fact] |
| DD-09 | Credentials/secrets | none real (local hashes only) | n/a | n/a | RL-05 | N/A today | [Verified Fact] |

### DO-2 Governance rules for data (existing decisions, restated by role)
| Rule | Source | Role that must own it |
|---|---|---|
| Never run tests against working-tree `data/`; use a full copy and verify checksums afterwards | OD-03, OD-03a | RL-07 (integrity), RL-02 (operation) |
| Keep all records; no deletion, no retention purge until a policy exists | OD-15 (OD-S12-09), OD-30 | RL-05 with RL-06 (VACANT) |
| Intake natural key is (partner, record_kind, ref_id, source_ts) | OD-18 | RL-08 |
| Source contracts `record_only`; late deliveries need a manual catch-up run | OD-28 | RL-08 |
| Field classes, tenant dimension, privacy regime (DPDP/GDPR named) decided before real data | OD-32; RS-06; RP-07 | RL-05 with RL-01 |
| `data_origin` = synthetic; STOP-04 on real data | PIA; STOP-04 | RL-01 gate |
| Restricted-evidence read rule (F-02, High) | OD-33; `red-team-findings.md` | open; Stage 27 default routing assumed |

### DO-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| DAF-01 | [Verified Fact] No data owner of any kind exists | `stakeholder-map.md`; OD-04 | Nobody can approve a data change or disposal | High if real data, Low synthetic | High | Who is RL-07? |
| DAF-02 | [Verified Fact] No retention authority; hold-all means unbounded growth and no disposal right | OD-30; RP-04 | Storage and privacy exposure over time | Medium | High | RL-05/RL-06 decision |
| DAF-03 | [Verified Fact] Consumers of the 13 legacy outputs outside the repo are Unknown | OD-28 (b); U-14-01 | Data contracts without known consumers | Medium | High | Business to identify |
| DAF-04 | [Verified Fact] The baseline definition of closed/resolved/48 h is unanswered, so KPI data cannot be owned by definition | OD-07; OPD-01..03; Q-02-05 | Any KPI is a generator-bounded proxy | Medium | High | RL-03 |
| DAF-05 | [Inference] The only copy of the git-ignored data besides the backup is on the laptop and the cloud workspace; no third copy | OD-23, V-05, V-10 | Loss of evidence data possible | Medium | Medium | Add a second remote/backup (VA-02 proposes mirror) |

## Evidence References
See `evidence_sources`. Privacy: `privacy-impact-assessment.md` (no telemetry leaves the host).

## Assumptions
- A-37-DO-1 [Assumption] Dinesh is the custodian of all synthetic data until handover (extends A-18-OM-1). Confirm: Engagement lead (Dinesh Naik).
- A-37-DO-2 [Assumption] The domains DD-01..DD-09 cover the repo; the git-ignored `data/lake` contents were not re-inspected for this docs-only stage. Confirm: Build agent at next build stage.

## Unknowns
- U-37-DO-1 Data residency, classification and legal basis for any future real data.
- U-37-DO-2 Who owns the source systems (ElectronicBatchRecord, LIMS-QMS, partner senders).
- U-37-DO-3 Retention periods required by any regulation (no legal review).

## Unresolved Issues
- RL-07 holder; retention policy; F-02 restricted-evidence rule; second backup copy.

## Residual Risks
- RR-37-DO-1 Real data introduced before an owner exists (High); mitigated by STOP-04, not eliminated.
- RR-37-DO-2 Hold-all growth and unbounded retention (Medium); not accepted beyond the interim OD-30 position.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 37). |
