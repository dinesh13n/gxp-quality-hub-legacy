---
stage: "30 — Release / Cutover / Rollback"
artifact: "backup-validation.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["../_data-backup-2026-10-17/SHA256SUMS.txt", "hub/ops/backup.py", "docs/30-release/evidence/s30-log-07-backup.txt", "docs/30-release/evidence/s30-log-08-verify-backup-manifest.txt", "docs/30-release/evidence/s30-log-24-restore-corrupt-backup.txt", "docs/30-release/evidence/s30-rehearsal-summary.txt"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Stage 30 PREPARES and REHEARSES a release; it does not release, cut over, merge to production, tag, install CI, flip a shipped switch or approve anything. Every approval below is OPEN and belongs to Dinesh Naik (Engagement lead, the only human, OD-04). Defaults marked 'recommended' are agent proposals under OD-32 (scope choices only), not decisions. `zone_h.holders` ships EMPTY. The product is No-AI (OD-08).**

## Summary
Backup and rollback were verified BEFORE any cutover (there is none). Legacy baseline: manifest of 1,512 entries verifies rc 0 before and after the Stage 30 rehearsal and before and after every test group. Hub store: backup, manifest check, restore with checksum match, chain verification and corrupt-backup refusal all passed on a sandbox copy.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Check | Result | Evidence | Tag |
|---|---|---|---|---|
| BV-1 | legacy manifest `sha256sum -c` from repo root | rc 0 pre and post | `s30-rehearsal-summary.txt` | [Verified Fact] |
| BV-2 | sandbox copy of data equals the manifest | rc 0 | summary line 3 | [Verified Fact] |
| BV-3 | hub backup writes `SHA256SUMS` + manifest; `sha256sum -c` | rc 0 | logs 07-08 | [Verified Fact] |
| BV-4 | restore: checksum_match true, schema M000/M001, audit chain ok at the backup head | ok | log 21-22 | [Verified Fact] |
| BV-5 | records after the backup are set aside, not merged | confirmed (head 18 -> 5, set-aside dir) | log 20-21 | [Verified Fact] |
| BV-6 | corrupted backup refused, live store unchanged | exit 21 | logs 24-25 | [Verified Fact] |
| BV-7 | G7 as the product evaluates it (backup, restore to scratch, verify) | pass | log 09b / checklist json | [Verified Fact] |
| BV-8 | off-device copy | NONE (AP-OPS-04 open) | F-29-02 | [Verified Fact] |
| BV-9 | backup of `hub.sqlite3` and the manifest share a host; no independent record of the audit head | open | F-29-05 | [Inference] |
| BV-10 | regeneration as a substitute for the baseline | NOT valid: different hash | log 32 | [Verified Fact] |
| BV-11 | restore of a large store, timing | not measured | - | [Unknown] |

## Evidence References
`rollback-plan.md`; tests R01.

## Assumptions
- A-30-10 [Assumption] The shipped 125-case database is the baseline (OD-09).

## Unknowns
- U-30-10 restore time on a realistic store; behaviour on a full disk (D-28-07).

## Unresolved Issues
- Off-device copy (AP-OPS-04).

## Residual Risks
- RR-30-9 One device holds the baseline and every backup.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 30). |
