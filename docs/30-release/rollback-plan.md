---
stage: "30 — Release / Cutover / Rollback"
artifact: "rollback-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/14-transformation/rollback-strategy.md", "hub/ops/backup.py", "hub/control/cli.py", "docs/30-release/evidence/s30-rehearsal-summary.txt", "docs/30-release/evidence/s30-log-21-restore.txt", "docs/30-release/evidence/s30-log-27-l1-revert-stage-31.txt"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Stage 30 PREPARES and REHEARSES a release; it does not release, cut over, merge to production, tag, install CI, flip a shipped switch or approve anything. Every approval below is OPEN and belongs to Dinesh Naik (Engagement lead, the only human, OD-04). Defaults marked 'recommended' are agent proposals under OD-32 (scope choices only), not decisions. `zone_h.holders` ships EMPTY. The product is No-AI (OD-08).**

## Summary
Three rollback levels (Stage 14), all rehearsed on sandbox copies: **L1 code** (git revert), **L2 hub state** (restore backup + anchor), **L3 authority** (`flip-to-shadow`). Legacy is never modified, so the legacy fallback is always available. Rollback after an authoritative period is compensating, not restorative: the ledger is append-only (RF-RB-2).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| Level | Procedure | Rehearsed result | Data loss | Tag |
|---|---|---|---|---|
| L3 | `python -m hub.control flip-to-shadow --capability C --reason T --data-dir D`, then re-point consumers to legacy | flip held then reverted; two CONFIG_CHANGED records (`to_non_default` with the sandbox marker, `to_default` with `rollback: L3`); verify-audit ok before and after (logs 12-19) | none; events recorded while authoritative are kept and reviewed | [Verified Fact] |
| L2 | stop; `hub.admin restore --backup B`; `verify-audit`; restart | restore checksum_match true, chain ok at backup head 5; records written after the backup (head 18) were SET ASIDE in `pre-restore/<stamp>/`, not merged (F-29-06) | real RPO loss between backup and failure; manual decision to re-ingest or review | [Verified Fact] |
| L2 negative | corrupted backup | refused with E-STORE-BACKUP-INVALID exit 21, live store unchanged, verify-audit ok (logs 24-25) | none | [Verified Fact] |
| L1 | `git revert --no-edit <squash commit>` on a new branch + PR (never force-push, WB-08) | reverting the Stage 31 squash (d1e3dbb) in a clone applied cleanly; `hub/` and `tests/hub` equal the pre-Stage-31 tree (diff rc 0); reverting the revert restored main exactly (logs 27-31) | none | [Verified Fact] |
| Legacy safety net | `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` from repo root, rc 0 | rc 0 before and after the rehearsal and every group | - | [Verified Fact] |

Findings:
- RB-1 [Verified Fact] Rollback authority is Dinesh alone (F-29-07); no alternate. Triggers are in `go-no-go-criteria.md` GN-2.
- RB-2 [Verified Fact] Backups and the baseline share one device; no off-device copy (F-29-02). A device loss is not recoverable by this plan (AP-OPS-04).
- RB-3 [Verified Fact] `verify-audit` and `backup` append audit records and rewrite the anchor (F-29-04); verify a sandbox copy when evidence must stay untouched.
- RB-4 [Verified Fact] Regenerating the baseline is NOT a rollback path: `app.generate --count 125 --seed 4100 --reset` produced a database with a different hash (5068c2b4... vs c254649f...) in the sandbox (log 32). F-29-12 answered: not bit-identical.
- RB-5 [Verified Fact] F-29-01 is fixed: `verify-audit` on a malformed anchor ends with exit 17, so rollback automation keyed on 17 works (tests F01..F03).
- RB-6 [Unknown] Whether a restore takes acceptable time on a larger store: the sandbox store is tiny (about 0.1 s).

## Evidence References
`s30-rehearsal-summary.txt`, logs 07-08 and 20-31; tests R01, R02, R04.

## Assumptions
- A-30-07 [Assumption] RTO 4 h / RPO 1 working day remain agent targets (Stage 29), not agreed.

## Unknowns
- U-30-07 consumers' behaviour on re-pointing (U-14-01).

## Unresolved Issues
- AP-OPS-02 (rollback authority and triggers) and AP-OPS-04 (off-device copy) are OPEN.

## Residual Risks
- RR-30-6 Post-cutover rollback loses nothing but cannot erase records; compensating entries are visible forever.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 30). |
