---
stage: "41 — Retirement / Decommissioning"
artifact: "archive-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/25-governance/evidence-retention-policy.md (RC-1..RC-11, RP-2)", "docs/30-release/{backup-validation,rollback-plan}.md", "docs/30-release/evidence/s30-log-07-backup.txt, s30-log-08-verify-backup-manifest.txt, s30-log-21-restore.txt, s30-log-24-restore-corrupt-backup.txt", "docs/29-incident-bcdr/{bc-plan,dr-plan,recovery-procedure}.md", "docs/33-vendor-risk/portability-assessment.md", "docs/37-operating-model/data-ownership.md", "docs/00-preflight/operating-contract/{provisional-human-approval-rules,data-use-constraints}.md (HAR-03, HAR-09, DU X-3, X-6)", "hub/ops/backup.py", ".fde/orchestrator-decisions.md (OD-03, OD-03a, OD-16, OD-21)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. DOCUMENTATION ONLY. No archive is created, moved, copied off the device, or deleted by this stage. Creating an archive that leaves the device needs HAR-09; deleting any file in the repo or the backup needs HAR-03. Archive location, medium and retention are OPEN decisions owned by Dinesh Naik.**

## Summary
An archive is the **recoverable, hash-listed, restore-tested** form of an asset that has reached RL-2 (stopped). This plan specifies what goes into each archive, how it is built and verified, how it is restored, and what must be true before the live copy is touched. It reuses mechanisms that exist and were rehearsed in Stage 30 (hub backup with manifest, `sha256sum -c`, restore with chain verification, corrupt-backup refusal) and adds only git-based and file-based archives that need no new code. Nothing here is a procedure that has been run against production; there is none. Rehearsal evidence is from sandbox copies (BV-1..BV-7). [Verified Fact]

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AR-1 Archive units
| ID | Archive unit | Contents | Built by (existing mechanism) | Verified by | Source assets | Tag |
|---|---|---|---|---|---|---|
| AU-1 | Legacy code archive | `git bundle` (or `git archive`) of the legacy paths at tag `baseline-as-found` (a6eb4e8) and at the final pre-retirement commit; list of paths from `coexistence-strategy.md` CS-2 | git (no execution of legacy code needed) | bundle verify; tree hash equal to the tag's tree for those paths | RA-01..RA-10, RA-14 | [Inference] design; [Verified Fact] tag exists (`git tag`) |
| AU-2 | Legacy data archive | `data/` as a file set (1,512 files) plus the OD-03 manifest `SHA256SUMS.txt`; `legacy.sqlite3` sha256 c254649f…d70aa | existing backup `../_data-backup-2026-10-17/` (already made, OD-03) | `sha256sum -c` rc 0 from repo root (observed rc 0 pre and post Stage 30 rehearsal: BV-1) | RA-11, RA-21 | [Verified Fact] backup and check |
| AU-3 | Hub store archive | `hub.sqlite3` (all retained tables), audit anchor file, config (including decision flags), schema version list M000..M007 | `hub.ops.backup` (manifest) as rehearsed (BV-2..BV-5) | manifest check; `verify-audit` rc 0; restore into a scratch dir and re-verify | RA-15, RA-16 (index excluded), RA-22 (hashes only) | [Verified Fact] mechanism; [Unknown] production use |
| AU-4 | Evidence archive | the git repository itself: `docs/**`, `docs/*/evidence/` with `SHA256SUMS.txt`, `.fde/`, all tags and PR history exported from the remote | `git clone --mirror` / `git bundle --all`; PR text is not in git and must be exported separately (exit plan V-03) | `git fsck`; `git ls-remote` SHAs equal | NR-3, NR-6, RA-20 | [Verified Fact] exit-plan steps; [Unknown] PR export tooling |
| AU-5 | Release and rehearsal evidence | `docs/30-release/evidence/` (33 logs + registers); OD log | in git (AU-4) | `SHA256SUMS.txt` | Stage 30 | [Verified Fact] |
| AU-6 | Toolchain record | list of accounts, versions and settings needed to rebuild: Python 3.10.12 / 3.12+, SQLite 3.37 floor, JDK 11, Node 22, GitHub settings, workspace settings | written by the owner (no secrets) | owner review | RA-17..RA-20, RA-25 | [Inference]; contents [Unknown] |

### AR-2 Build and verify procedure (applies to AU-2, AU-3; AU-1 and AU-4 use git)
All steps run on a FULL COPY outside the working tree (OD-03a); the working-tree `data/` is never used as a test target (OD-03).
1. Precondition: PR-01..PR-13 in `retirement-criteria.md` met for the asset, including PR-07 (legal-hold check) and an APPROVED owner decision for the archive location.
2. Freeze: stop writers (hub serve, any legacy job); record the stop in the audit trail as a human-authorised action if the hub is up.
3. Integrity before archive: run `verify-audit` and the checksum manifest; a failed check blocks the operation (G3, G7; `evidence-retention-policy.md` RP-2 rule 4).
4. Build the archive; write a manifest (path, size, sha256) and a human-readable index; record tool versions and the environment tier.
5. Verify: re-hash the archive copy; compare to the manifest and to the source.
6. Restore test into a scratch directory on a different path; run `verify-audit` (hub) or `sha256sum -c` (data); for AU-1 check out the bundle and compare tree hashes.
7. Negative test: corrupt a copy and confirm the restore is refused (Stage 30 BV-6/L2 negative showed `E-STORE-BACKUP-INVALID`, exit 21, live store unchanged).
8. Record the manifest, hashes, command output and the restore result under a new `evidence/` folder with its own `SHA256SUMS.txt`; commit it; never overwrite earlier evidence.
9. Only then may the live asset move to RL-2; deletion (RL-3) is a separate, later, separately approved step.

### AR-3 Location, medium, access (all OPEN)
| Item | Position | Tag |
|---|---|---|
| Where archives live | Not decided. Today there is one device and one private GitHub remote; no off-device copy of git-ignored data exists (RF-06, DAF-05). Off-device copy of data needs HAR-09 and DU X-6 stops committing DBs to git without it. | [Verified Fact] |
| Medium and retention of the medium | Unknown; no period (see `data-retention-plan.md`) | [Unknown] |
| Encryption at rest | No requirement exists (U-S24-DP-1); proposal: decide before any off-device copy. Key custody would then become a new secret (see `secret-key-revocation.md`) | [Unknown] / [Inference] |
| Access to archives | Owner of record: Dinesh Naik (interim). No second custodian exists | [Verified Fact] |
| Readability horizon | Python 3.10 floor, 3.12+ production target (OD-24), SQLite 3.37; hub schema migrations retained with the code (IC-4). A future reader needs a runtime that can open SQLite files and verify SHA-256 | [Inference] |
| Format neutrality | SQLite files, JSON, CSV, plain-text Markdown and git objects only; no proprietary format is introduced | [Verified Fact] (stdlib-only stack, DM-08) |

### AR-4 What is NOT archived
- Derived, rebuildable material: FTS5 index, generated reports (RC-11); [Inference] rebuild test required at clearance. The regenerated 6,000-case dataset (OD-09) is not part of the baseline, and regeneration is NOT a valid substitute for archiving the baseline (BV-10: different hash).
- Sandbox copies and scratch stores (RC-6): already disposable by OD-16; evidence is the excerpt-plus-hash in artifacts.
- Secrets: never archived. Hashes in the hub store travel inside AU-3 only because they are part of the retained tables; plaintext secrets do not exist in the repo (SH-1).

### AR-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| AF-01 | [Verified Fact] Backup, manifest check, restore and corrupt-backup refusal are rehearsed on sandbox copies only | `backup-validation.md` BV-1..BV-7 | The method is credible; no production rehearsal exists | Medium | High | Rehearse on the real target before use |
| AF-02 | [Verified Fact] Restore sets aside records written after the backup in `pre-restore/<stamp>/` and does not merge them (F-29-06) | `rollback-plan.md` L2 | An archive taken early loses later records from the restored state; the set-aside copy must be archived too | Medium | High | Include `pre-restore/` in AU-3 when present |
| AF-03 | [Verified Fact] No second copy of the baseline and backup exists; no off-device archive location is approved | RF-06; DAF-05 | The archive plan cannot reduce single-point loss until D-41-09 is decided | Medium | High | D-41-09 |
| AF-04 | [Verified Fact] PR text and review comments live only at the code host | exit plan V-03 | AU-4 is incomplete without an export | Low-Medium | High | Export method |
| AF-05 | [Inference] Archiving the hub as one unit conflicts with no partial disposal, which is the intended outcome (insert-only design) | DF-14 | Archive size grows with hold-all | Low | Medium | none |

## Evidence References
See `evidence_sources`. Companion: `data-retention-plan.md`, `decommission-checklist.md` steps A-01..A-12.

## Assumptions
- A-41-AR-1 [Assumption] A `git bundle` of legacy paths is an acceptable code archive for the owner. Confirm: Engagement lead (Dinesh Naik).
- A-41-AR-2 [Assumption] The Stage 30 backup commands (`hub.ops.backup`, `hub.admin restore`) behave on a real data directory as they did on sandbox copies. Confirm: Build agent at rehearsal time.
- A-41-AR-3 [Assumption] No archive compression or encryption is required. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-41-AR-1 Archive location and medium; off-device policy.
- U-41-AR-2 Whether encryption is required, and who would hold the key.
- U-41-AR-3 PR export tooling and completeness.

## Unresolved Issues
- UI-41-AR-1 D-41-09 (location, medium, custodian). Owner: Engagement lead (Dinesh Naik).

## Residual Risks
- RR-41-AR-1 Archive unreadable at restore time (format or runtime drift): Medium; mitigated by restore tests and format neutrality, not eliminated.
- RR-41-AR-2 A single custodian holds every archive: Medium-High (SF-03).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 41). |
