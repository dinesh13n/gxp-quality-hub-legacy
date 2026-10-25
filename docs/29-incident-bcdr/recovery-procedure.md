---
stage: "29 — AI Incident Response + BC/DR"
artifact: "recovery-procedure.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["hub/ops/backup.py", "hub/admin/cli.py", "hub/control/cli.py", "docs/29-incident-bcdr/dr-plan.md", "docs/29-incident-bcdr/rto-rpo.md", "docs/29-incident-bcdr/evidence/", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md (HAR-01, HAR-03, HAR-09)", ".fde/orchestrator-decisions.md (OD-03, OD-03a, OD-15, OD-16, OD-23)", "docs/21-integration/failure-semantics.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
Step-by-step recovery for each scenario, written so it can be rehearsed in a sandbox first. General rules: **recover into a sandbox and verify before touching anything real; restore into working-tree `data/` only with Dinesh's recorded approval (HAR-01); delete nothing (HAR-03, hold-all); end every recovery with a checksum check and, for the store, `verify-audit`; Dinesh records the decision to resume.** Commands marked (R) were run in the 2026-10-25 sandbox rehearsal (`evidence/`); the rest are procedure only and unrehearsed. Targets are in `rto-rpo.md` and are not measurements.

Conventions: `A="python3 -B -m hub.admin --config C"` where `C` is a config file that sets `audit.anchor_path`; `D` is a hub data dir outside any git worktree and outside the baseline backup path (the hub refuses otherwise, E-CO-NOT-SANDBOX).

## Findings
### RV-0 Gate before any recovery
1. Contained (CT done) and evidence copied and hashed (FE-02).
2. Incident severity recorded; for SEV-A, Dinesh has been told (CM-T1).
3. Dinesh's decision to recover is in the conversation and logged (OD entry via the orchestrator).
4. Before and after every recovery touching the repo area: `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` from repo root must return rc 0 (STOP-01). (R: rc 0 before and after the rehearsal.)

### RV-1 No-state-change recovery (IS-01, IS-05 first response, IS-06, IS-07)
Re-create the sandbox from `git archive HEAD` (no `.git`) into a fresh folder; copy data checksum-gated; re-run the failed step; delete or move aside the old sandbox only per HAR-03; record. Check: sandbox run equals expected result; working-tree checksum rc 0.

### RV-2 Restore the hub store (IS-08 partly, IS-11, DR-S1, DR-S2)
| Step | Command / action | Expected result (from rehearsal) |
|---|---|---|
| 1 | Evidence copy of store, wal/shm, anchor, config (FE-02) | hashes match |
| 2 | Choose the backup: newest label whose `verify_backup` passes; `cd BACKUP && sha256sum -c SHA256SUMS` | OK for each file (R step 05) |
| 3 | In a sandbox data dir: `$A restore --data-dir D_SBX --backup BACKUP` (R step 08) | `checksum_match: true`, `schema_after_restore` listed, `verify_audit.status: ok`, previous files under `D_SBX/pre-restore/<stamp>/` |
| 4 | If the backup is corrupt: restore refuses with `E-STORE-BACKUP-INVALID` (exit 21) and **changes nothing** (R step 10, step 11 verify ok); pick an older backup | refused, store intact |
| 5 | `$A verify-audit --data-dir D_SBX` (R step 09) | `status: ok` |
| 6 | Decide with Dinesh how to treat records written after the backup (they are in `pre-restore/`; no merge tool exists: DRF-04): re-ingest from the sources (idempotent intake, FS-DUP-01), or list them for manual review | decision recorded |
| 7 | Only after the sandbox is good and Dinesh approves, repeat step 3 on the real data dir | same output |
| 8 | Remove `hub.kill` only after step 7 and after Dinesh agrees; restart loopback server; `startup-check` shows loopback (R step 13) | `exposure: loopback` |
| 9 | Take a fresh `backup` (after copying evidence if the incident is still open) | new label, manifest written |
Note: `restore` also appends a `STORE_RESTORED` audit record and `CONFIG_LOADED`; the chain continues after the restored head (R: head_seq 5 -> verify at 7).

### RV-3 Restore baseline `data/` from the backup (IS-02, DR-S3) [procedure only; HAR-01 and HAR-03 apply]
1. Stop; do not run any generator or test in the working tree (STOP-02, HAR-16).
2. `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` from repo root; keep the list of mismatching/missing files.
3. Dinesh approves (HAR-01) naming the files; if any file must be overwritten or removed that is also HAR-03.
4. Copy the listed files from the backup, not the other direction, with `cp -p`; never touch the backup.
5. Re-run the check: rc 0; record before/after.
6. For files present in `data/` but not in the manifest (extra files): do not delete; list them for Dinesh.

### RV-4 Compromised tool (IS-03) [procedure only]
Freeze `main`; tag HEAD; list commits made since the suspected time; compare their diff against the orchestrator's regression result; revert by a new PR (never history rewrite); re-run `run_hub_groups.py --all` and the harness on the reference laptop; resume only on Dinesh's decision; vendor steps per exit plan V-01..V-09.

### RV-5 Leakage (IS-04) [procedure only]
Remove nothing; list locations; if not pushed, do not push and add a new commit that stops tracking a mistaken file only with Dinesh's agreement (history stays); if pushed to the private remote, Dinesh decides on the remote's handling (HAR-09); rotate any credential that was real (Unknown whether any exists); re-run the secret scan (S33) and egress tests; report per CM-T3.

### RV-6 Retrieval defect (IS-05) [procedure only]
Reproduce in a sandbox copy; log expected vs actual; fix by a normal PR with a new test; re-review any decision that relied on the wrong result by recording a new, linked decision event (insert-only; no edits).

### RV-7 Cost/disk (IS-07) [procedure only]
Disk: move sandbox copies to a `_to_delete/` folder; ask Dinesh for deletion (HAR-03); free space; confirm free space with `df`. Spend: Dinesh checks the provider usage page (not visible to the agent); counters `model_calls_total`, `egress_attempts_total` re-read.

### RV-8 Configuration (IS-08) [procedure only]
Compare the live config file with the last recorded version; every non-default decision flag must carry an `approval_ref` (the hub refuses start-up otherwise; EH-07); use `$A`-style hub.control commands for flag changes so a `CONFIG_CHANGED` audit record exists; `python -m hub.control flags` must show no unexpected non-default; use `flip-to-shadow` to retreat an `authoritative` capability; re-run `startup-check`.

### RV-9 Repo and tooling (IS-03, IS-06, IS-09, DR-S5, DR-S6)
Per `failover-procedure.md` FO-3..FO-5. Verify with `git fsck`, `git ls-remote` SHA match, regression executed = expected, harness on the reference laptop.

### RV-10 Disaster rebuild (IS-10, DR-S4, DR-S7, DR-S9) [procedure only, unrehearsed]
Follow `dr-plan.md` DR-3. Data source order: (1) surviving backup, verified; (2) cloud workspace copy, verified against the manifest (HAR-09 approval to bring it back); (3) regeneration (`app.generate --reset`), **not** equivalent to the baseline unless proven (U-29-DR-1); in case 3 the baseline is declared lost, the incident stays open, and Dinesh decides the new baseline (HAR-02). Always SEV-A until the baseline question is settled.

### RV-11 Feed delay/divergence (IS-12)
Run the idempotent catch-up ingest (late items are picked up, FS-STALE-02); compare run totals with source counts; keep the failed run record; do not overwrite with spreadsheet figures; if root cause is disputed, record both claims and escalate (ER-12).

### RV-12 Closing checklist (every recovery)
| Check | Pass condition |
|---|---|
| Data checksums | `sha256sum -c` rc 0 before and after |
| Store | `verify-audit` status ok on the recovered store |
| Backup | new verified backup exists |
| Evidence | incident folder hashed and read-only |
| Approvals | each HAR needed is cited with its OD entry; none invented |
| Records | incident record complete; residual risks listed and left OPEN unless Dinesh accepts |
| Learning | change history entry or addendum raised, never an in-place overwrite |

### RV-13 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| RVF-01 | [Verified Fact] Store restore, corrupt-backup refusal and post-restore chain verification worked on a synthetic sandbox store | logs 08-11 | Mechanism is sound at small scale | Low | High (small) | scale |
| RVF-02 | [Verified Fact] A restore into a data dir that holds a tampered anchor sets the anchor aside, so the tamper evidence is kept | log 08 (`set_aside`) | Good for forensics | Low | High | none |
| RVF-03 | [Verified Fact] No merge tool for post-backup records | `restore` code | Manual decision needed | Medium | High | DRF-04 |
| RVF-04 | [Inference] RV-3 and RV-10 are unrehearsed because rehearsal on working-tree data is forbidden and no second host exists | HAR-01, HAR-16 | Highest-impact recoveries have the least evidence | Medium | Medium | rehearse RV-3 on a sandbox copy of `data/` at Stage 30? |

## Evidence References
`evidence/s29-log-01..13` (SHA256SUMS in the folder); `hub/ops/backup.py`; `hub/admin/cli.py`; `docs/21-integration/failure-semantics.md`.

## Assumptions
- A-29-RV-1 [Assumption] Re-ingest from sources is an acceptable way to cover post-backup records for synthetic data. Confirm: Dinesh.
- A-29-RV-2 [Assumption] Moving sandboxes to `_to_delete/` is acceptable when disk is short (OD-16 pattern).

## Unknowns
- U-29-RV-1 Behaviour of restore on a large or busy store.
- U-29-RV-2 Equivalence of regenerated data to baseline.
- U-29-RV-3 Whether extra files exist in `data/` outside the manifest (observed equal count 1,512 = 1,512 on 2026-10-25).

## Unresolved Issues
- RV-3, RV-4, RV-5, RV-10 unrehearsed; no merge tool; Stage 28 reconciliation pending.

## Residual Risks
- RR-29-RV-1 Recovery steps fail under pressure because they have not been run by the person who will run them (Medium).
- RR-29-RV-2 Restored state is older than the lost state; lost records need manual re-creation (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
