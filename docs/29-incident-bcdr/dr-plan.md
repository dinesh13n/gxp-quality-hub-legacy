---
stage: "29 — AI Incident Response + BC/DR"
artifact: "dr-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["hub/ops/backup.py", "hub/admin/cli.py", "docs/33-vendor-risk/exit-plan.md", "docs/33-vendor-risk/portability-assessment.md", "docs/25-governance/evidence-retention-policy.md", "docs/10-architecture/deployment-architecture.md", ".fde/orchestrator-decisions.md (OD-03, OD-03a, OD-16, OD-23)", "docs/29-incident-bcdr/evidence/", "docs/15-modernization/rollback-rehearsal-inc03.md", "docs/15-modernization/rollback-rehearsal-inc09.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
Disaster recovery for the assets that matter: the **hub store and anchor**, the **baseline `data/` and its backup**, the **git repository and evidence**, and the **build tooling**. Design is deliberately simple because the deployment is simple: one host, one SQLite file, one anchor file, stdlib-only code, no cluster, no database server. Recovery means **rebuilding a host from git plus verified backups and proving it by checksum and `verify-audit`**. A sandbox rehearsal on 2026-10-25 exercised the hub's own backup, tamper detection, restore and corrupt-backup refusal on a synthetic store (see `tabletop-results.md` RH-01..RH-12). **No restore was run against working-tree `data/`; no live disaster test was run** (excluded by the stage and by HAR-01).

## Findings
### DR-1 Assets and where copies live today
| ID | Asset | Primary | Copies today | Off-device copy? | Tag |
|---|---|---|---|---|---|
| DA-1 | Hub store `hub.sqlite3` (+ wal/shm) | hub `--data-dir` (outside the working tree) | `backup` creates labelled copies via `VACUUM INTO` with MANIFEST + SHA256SUMS; `migrate` takes an automatic pre-migration backup | no | [Verified Fact] mechanism |
| DA-2 | Audit anchor `audit-anchor.jsonl` | `audit.anchor_path` (required config) | included in each backup | no | [Verified Fact] |
| DA-3 | Hub config and decision flags | operator-edited file, location Unknown | git only if the operator commits it | Unknown | [Unknown] |
| DA-4 | Baseline `data/` (50 MB, 1,512 files; `legacy.sqlite3` sha256 c254649f...d70aa) | working tree, git-ignored | `../_data-backup-2026-10-17/` (same mount as the working tree) with `SHA256SUMS.txt` | **no** (HAR-09 forbids sending data off device) | [Verified Fact] |
| DA-5 | Git repository, docs, evidence, OD log | laptop clone | private GitHub remote `dinesh13n/gxp-quality-hub-legacy`; orchestrator's cloud workspace clone | yes (code and docs only) | [Verified Fact] (PRs #1..#17 merged) |
| DA-6 | Cloud workspace copy of data for regression | provider VM | checksum-gated copy (OD-23) | it is itself an off-device copy of data (HAR-09 approved by OD-23 for this purpose) | [Verified Fact] |
| DA-7 | Sandbox copies | `~/fde_sbx/...` | none by design; deleted after each run (OD-16) | n/a | [Verified Fact] |
| DA-8 | Tooling (assistant, runners) | providers | none | n/a | [Inference] |

### DR-2 Disaster scenarios and recovery path
| ID | Disaster | Surviving assets (Inference) | Recovery path | Needs |
|---|---|---|---|---|
| DR-S1 | Hub store corrupted or tampered (IS-11) | backups in the backup root; set-aside copies | RV-2: copy evidence, verify backup, restore into a sandbox, verify chain, then decision on the live path | Dinesh (HAR-01 if working-tree path) |
| DR-S2 | Hub store lost, backup intact | backups, anchor in backup | RV-2 restore | none beyond Dinesh decision |
| DR-S3 | Working-tree `data/` altered or deleted | `../_data-backup-2026-10-17/` | RV-3: compare with `sha256sum -c`; restore only the differing files with approval | HAR-01, HAR-03 |
| DR-S4 | Laptop/VM disk lost (backup and `data/` on the same device) | GitHub (code, docs, evidence); cloud workspace copy of data (checksum-gated, OD-23) | RV-10: new host; clone; re-obtain `data/` from the cloud workspace copy ONLY after checking its manifest, or regenerate (`python -m app.generate --reset`) knowing equality with the baseline is **Unknown** | Dinesh (HAR-09 for moving data back to a device) |
| DR-S5 | GitHub unavailable or locked out | local clone(s); cloud workspace clone | exit plan V-03: `git push --mirror` to a new remote | HAR-09 |
| DR-S6 | Assistant/workspace unavailable | repo, tests, OD log, `.fde/` | exit plan V-04/V-05 | Dinesh |
| DR-S7 | Device and cloud copy both lost | GitHub only | rebuild code/docs; data regenerated or re-supplied; baseline equality Unknown; **SEV-A** | Dinesh |
| DR-S8 | Python/SQLite end of life or CVE | n/a | V-01/V-02 upgrade path; runtime target 3.12+ with 3.10 floor (OD-24) | Dinesh |
| DR-S9 | Ransomware/malware on the host | GitHub, cloud workspace | treat as DR-S4; do not restore from a possibly infected backup without hash comparison against an independent source | Dinesh |

### DR-3 Rebuild a host (cold standby by procedure; no standing standby exists)
Steps (all inside sandbox first): (1) host with Python >=3.10 (3.10.12 is the reference for goldens; 3.12+ is the production target, OD-24); (2) `git clone` the private remote (or the mirror) and check out the tagged commit; (3) `git fsck`; (4) re-obtain data (DR-S4 options) and run `sha256sum -c` against the manifest; (5) create a config file with `audit.anchor_path` set and `data_origin: synthetic`; (6) restore the hub store from the latest verified backup into a hub data dir outside the repo; (7) `verify-audit`; (8) run the orchestrator regression `tests/hub/run_hub_groups.py --all` (expected executed = expected, 419 methods at Stage 20; the count has since changed) and the characterization harness on the reference Python; (9) record result; (10) decision to resume by Dinesh. Effort order-of-magnitude "day" is from the exit plan V-10 [Assumption].

### DR-4 Constraints specific to this host [Verified Fact]
- The hub refuses to run inside a git worktree or on the baseline backup path (E-CO-NOT-SANDBOX, exit 7): hub data dirs live outside the repository.
- VM disk is about 9.8 GB (OD-16): do not keep multiple full sandboxes; delete only with HAR-03 (or move to `_to_delete/`).
- Group C of the regression is near the 180 s device-call cap (OD-21): a slow restored host may fail on time, not on correctness.
- Goldens from Python 3.10.12 differ on 3.13 by environment only (OD-23): compare on the reference interpreter.

### DR-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| DRF-01 | [Verified Fact] Baseline data and its only backup are on the same mount; no off-device copy; HAR-09 forbids one without approval | `../_data-backup-2026-10-17/`, `evidence-retention-policy.md` RC-7/RC-8 | Device loss destroys both | High for the baseline (Medium: regenerable? Unknown) | High | Will Dinesh approve an encrypted off-device copy (HAR-09)? |
| DRF-02 | [Unknown] Whether `python -m app.generate --reset` with seed 4100 reproduces the 125-case baseline byte-for-byte (README documents a different 6,000-case/seed-4326 dataset, OD-02/OD-09) | OD-09 | Regeneration may not give the baseline | Medium | Low | test in a sandbox (not done: out of scope here) |
| DRF-03 | [Verified Fact] Hub restore, backup verification, corrupt-backup refusal and post-restore chain check work in the sandbox | `evidence/s29-log-08..11` | Core DR mechanism is sound on a small store | Low | High (small, synthetic store only) | behaviour on a large or concurrently written store is Unknown |
| DRF-04 | [Verified Fact] `restore` replaces the store with the backup state; records written after the backup are not merged back, they sit in `pre-restore/` | `hub/ops/backup.py`; log 08 | RPO is real data loss; manual re-entry/merge has no tool | Medium | High | decide re-ingest vs. manual review |
| DRF-05 | [Verified Fact] Config location and its backup are not defined | `hub/config.py` | A wrong config after rebuild could change authority | Medium | Medium | store config in git with approval refs |
| DRF-06 | [Inference] Backups are not scheduled; frequency is whatever the operator does | no scheduler (OD-28) | RPO depends on discipline | Medium | Medium | schedule when a service owner exists |
| DRF-07 | [Verified Fact] Earlier rollback rehearsals exist for INC-03 and INC-09 (code rollback), not data/DR | `docs/15-modernization/rollback-rehearsal-inc03.md`, `-inc09.md` | Code rollback evidence exists; DR evidence did not before this stage | Low | Medium | none |

## Evidence References
`hub/ops/backup.py` (`backup`, `verify_backup`, `restore`); `hub/admin/cli.py`; rehearsal logs `docs/29-incident-bcdr/evidence/s29-log-01..13`; `docs/33-vendor-risk/exit-plan.md`; `docs/25-governance/evidence-retention-policy.md`; OD-03, OD-03a, OD-16, OD-21, OD-23, OD-24.

## Assumptions
- A-29-DR-1 [Assumption] Cold standby by procedure (no standing second host) is adequate while the hub is inert. Confirm: Dinesh.
- A-29-DR-2 [Assumption] Order-of-magnitude rebuild effort follows the exit plan (day). Not measured.
- A-29-DR-3 [Assumption] The cloud workspace copy of data stays checksum-gated and is a valid recovery source for synthetic data.

## Unknowns
- U-29-DR-1 Regeneration equivalence (DRF-02).
- U-29-DR-2 Behaviour at larger store sizes and under concurrent writers.
- U-29-DR-3 Config file location and ownership.
- U-29-DR-4 Cloud workspace data lifecycle terms (V-05).

## Unresolved Issues
- No off-device data backup; no backup schedule; no merge tool for post-backup records; Stage 28 design not available to reconcile (IR-03).

## Residual Risks
- RR-29-DR-1 Single-device loss of baseline (High if regeneration is not equivalent).
- RR-29-DR-2 Restore-time behaviour at scale unmeasured (Medium).
- RR-29-DR-3 No live disaster test was performed (excluded); DR is rehearsed in a sandbox only.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
