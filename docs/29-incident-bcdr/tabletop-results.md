---
stage: "29 — AI Incident Response + BC/DR"
artifact: "tabletop-results.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["docs/29-incident-bcdr/tabletop-scenario.md", "docs/29-incident-bcdr/evidence/SHA256SUMS.txt (17 files)", "docs/29-incident-bcdr/evidence/s29-log-01..13", "docs/29-incident-bcdr/evidence/s29-rehearsal-summary.txt", "hub/admin/cli.py", "hub/ops/backup.py", "hub/security/audit.py", ".fde/orchestrator-decisions.md (OD-03a)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
**How this was run, stated plainly.** TT-1 was run on 2026-10-25 as (1) a **desk walk-through by the agent** of every inject against the Stage 29 procedures and the repo evidence, and (2) a **sandbox rehearsal** of the mechanical steps that exist as commands (backup, tamper detection, restore, corrupt-backup refusal, kill switch, loopback start-up check) on a freshly created synthetic hub store in a full-copy sandbox outside the working tree. **No people took part**: Dinesh Naik's decisions were not simulated (the walk stopped at each approval point), all other roles are VACANT. So this is evidence that the **documents and tools line up**, not evidence that **a team can respond**. That limitation is why the stage gate is CONDITIONAL PASS and not PASS (condition C-1).

Guard evidence: `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` returned **rc 0 before and rc 0 after** the rehearsal; no working-tree `data/` path was used; the sandbox (`~/fde_sbx/s29-reh`) was deleted afterwards (OD-16). Raw outputs, with `$HOME` replaced by `~`, are in `docs/29-incident-bcdr/evidence/` with `SHA256SUMS.txt`.

**Result in one line:** 8 criteria: 6 met on paper and in the sandbox, 2 met only in part (TC-3 and TC-4 depend on operator discipline); 1 real defect found (exit code on a malformed anchor), 13 gaps registered; nothing fixed, nothing accepted.

## Findings
### TR-1 Sandbox rehearsal results (mechanical steps) [Verified Fact: outputs in evidence/]
Python 3.10.12, git HEAD `5efe271` archive, store created by `hub.admin migrate` (M000 to M001), 104 KB. Elapsed = wall-clock of one CLI call; **tool time only, not an RTO**.
| Step | Action | Exit | Elapsed | Observed |
|---|---|---|---|---|
| RH-01 | `migrate` (auto pre-migration backup taken) | 0 | 0.16 s | applied M001, backup label created |
| RH-02 | `status` | 0 | 0.06 s | store listing |
| RH-03 | `verify-audit` (clean) | 0 | 0.07 s | `status: ok`, `records: 2` |
| RH-04 | `backup --label reh-001` | 0 | 0.08 s | MANIFEST + SHA256SUMS, anchor included, `audit_head.audit_seq: 5` |
| RH-05 | `sha256sum -c SHA256SUMS` in the backup | 0 | 0.01 s | both files OK |
| RH-06 | `verify-audit` again | 0 | 0.07 s | ok; audit record count keeps rising (every command writes) |
| RH-07 | **Damage:** append a malformed line to the sandbox anchor; `verify-audit` | **1** | 0.07 s | prints `E-SEC-AUDIT-TAMPER-DETECTED`, `kind: anchor_unreadable`, then an unhandled `KeyError: 'audit_seq'` traceback from the end-of-run anchor write; **documented exit is 17** |
| RH-08 | `restore --backup reh-001` | 0 | 0.08 s | `checksum_match: true`; old store and damaged anchor set aside in `pre-restore/<stamp>/`; `verify_audit.status: ok`, `head_seq: 5` |
| RH-09 | `verify-audit` after restore | 0 | 0.07 s | ok, `head_seq: 7` (restore wrote `STORE_RESTORED` and `CONFIG_LOADED`) |
| RH-10 | Corrupt one byte of a copy of the backup; `restore` from it | **21** | 0.06 s | `E-STORE-BACKUP-INVALID`, `checksum mismatch`, nothing touched |
| RH-11 | `verify-audit` after the refused restore | 0 | 0.08 s | ok |
| RH-12 | Config `hub.kill: true`; `verify-audit` | **3** | 0.06 s | `E-HUB-KILLED` |
| RH-13 | `startup-check` | 0 | n/a | `bind 127.0.0.1`, `exposure: loopback` |
Caveats [Verified Fact]: single run; tiny store; the RH-07 verification was deliberately run **in place on the damaged sandbox store**, which is exactly the practice FE-03 forbids for a real incident, to show the hazard; one run says nothing about variance.

### TR-2 Inject walk-through (desk), with outcome
| Inject | Detection (TC-1) | Severity (TC-2) | Containment first step (TC-3) | Evidence preserved (TC-4) | Communication (TC-5) | Recovery check (TC-6) | Approvals (TC-7) | Outcome |
|---|---|---|---|---|---|---|---|---|
| A1 hostile instruction in a file | DS-12 (agent self-check, STOP-05); product side DS-01 | SEV-C (stopped on sight; SEV-B if followed, SEV-A if it led to a Zone H/data/approval act) | CT-01: stop, quote as data, verify checksum rc 0 | file path + hash recorded | CM-T1 below | checksum rc 0 | HAR-14 to continue the stage | Procedure adequate on paper. **Gap TF-01:** detection depends on the same agent that is steered; no independent detector |
| A2 `data/` changed | DS-03 checksum at stage boundary | SEV-A (d) | CT-02: halt, do not revert by hand, kill switch, list diffs | `git status`, mismatch list hashed | CM-T1 to Dinesh | `sha256sum -c` rc 0 after approved restore | HAR-01, HAR-03 stop and wait | Met on paper. **Gap TF-02:** check runs at stage start/end, so undetected window = a stage; nothing prevents the write |
| A3 Dinesh unreachable | n/a | n/a | agent may stop, preserve, set kill, record; may NOT restore or accept | yes | message queued | none | no alternate exists (ER-18) | **Gap TF-03:** response pauses; this is the first point that depends on a person who does not exist |
| A4 "restore it" | n/a | n/a | RV-3 | before/after checksums | CM-T3 | rc 0 | HAR-01 satisfied only by Dinesh's recorded word | RV-3 **unrehearsed** (forbidden on working-tree data; **Gap TF-04**). Backup on same device (DRF-01) |
| B1 tamper detected | DS-04 | SEV-A | CT-11: stop, copy, verify on a copy | copy + hash first | CM-T1 | sandbox verify of copy | HAR-01 for live restore | Detection worked (RH-07). **Defect TF-05:** exit 1 not 17, traceback after the correct envelope |
| B2 "check again on live / fix the anchor" | n/a | n/a | FE-03 forbids; CT-11 step 3 | the rehearsal showed `verify-audit` writes | n/a | n/a | n/a | Procedure stops it **only by discipline**. **Gap TF-06:** no read-only verify mode |
| B3 disk nearly full | DS-15 | SEV-C to SEV-B (evidence at risk) | CT-07: move, don't delete | copies first | CM-T2 | `df` | HAR-03 for deletion | **Desk only, not simulated** (risk to host). Observed free space during the run: about 5.5 GB of 9.8 GB on the VM disk, sandbox used well under 1 MB |
| B4 "trust the backup?" | n/a | n/a | FE-3: manifest check | n/a | n/a | RH-05, RH-10 prove the manifest check catches accidental corruption | n/a | **Gap TF-07:** `SHA256SUMS` and `MANIFEST.json` sit beside the files; a host-level actor could change all of them; the chain and anchor in the backup are also from the same host (Inference) |
| B5 backup older than live | n/a | n/a | RV-2 step 6 | `pre-restore/` kept | CM-T2 | RH-08, RH-09 | Dinesh decides re-ingest vs. manual | Observed: records after the backup are set aside, not merged. **Gap TF-08:** no merge tool |
| B6 corrupt backup | `E-STORE-BACKUP-INVALID` | SEV-B | refuse; use older | store unchanged | CM-T2 | RH-10, RH-11 | none | **Met** (observed) |
| B7 flag without approval_ref | DS-14 (start-up refusal EH-07; divergence EH-10) | SEV-B (SEV-A if falsified) | CT-08 | config copy + hash | CM-T1 | `hub.control flags`, `startup-check` | HAR-11 | Desk only; mechanism from Stage 23, not re-executed here. **Gap TF-09:** config file location and backup Unknown |
| B8 "accept all risks to close" | n/a | n/a | refuse | n/a | CM-4 rule 4 | n/a | HAR-11, TP-14 | **Met on paper:** agent cannot accept; Dinesh only |
| B9 precedent repeats | n/a | n/a | n/a | n/a | CM-5 | n/a | n/a | **Gap TF-10:** follow-up owner unknown, as in INC-2025-014; RL roles VACANT |

### TR-3 Pass criteria
| Criterion | Result |
|---|---|
| TC-1 detection signals exist | Met (17 signals; all pull-based) |
| TC-2 severity assigned | Met for all injects (assigned by the same agent) |
| TC-3 containment uses existing mechanism without altering evidence | **Partly met:** mechanisms exist (kill switch observed rc 3); altering evidence is prevented only by discipline (B2) |
| TC-4 evidence first | **Partly met:** procedure says copy first; nothing enforces it; the rehearsal showed the writing behaviour of verification |
| TC-5 comms | Met (draft below; only Dinesh named) |
| TC-6 recovery verified | Met in sandbox for the store; **not** for `data/` or the rebuild (unrehearsed) |
| TC-7 no invented approvals | Met |
| TC-8 gaps recorded | Met (TF-01..TF-10, F-29-01..F-29-14 in `incident-readiness.md`) |

### TR-4 The five analysis dimensions (stage requirement)
| Dimension | Rating | Basis | Confidence |
|---|---|---|---|
| Detection coverage | Partial | 17 signals cover all 12 scenarios, but all are pull-based, nobody watches, and IS-02 detection is delayed and not independent (TF-02) | High |
| Severity classification | Adequate on paper | all 12 scenarios and 10 error codes classified; untested by a second person | Medium |
| Containment speed | **Unknown** | tool time for the kill switch was 0.06 s; human latency not measurable with no responders; no clock targets exist | High (that it is unknown) |
| Evidence preservation | Partial | restore preserves replaced files (RH-08); verification overwrites in place (RH-06/07); no off-device or independent copy | High |
| Recovery to RTO/RPO | Unknown / not demonstrated | tool times tiny; RTO/RPO unmeasured; RPO unmet for device loss by construction | High |

### TR-5 Sample message drafted during the walk (CM-T1; synthetic scenario text)
> STOP: IS-02 detected at T+n by the stage agent via DS-03. Class SEV-A (data/ checksum mismatch). Known [Verified Fact]: `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` reports mismatches in N files (list attached). Inferred: a generator ran against `data/`. Unknown: how, and whether other files changed. Contained: agent halted, hub.kill set. Evidence preserved: mismatch list and `git status` at <path, sha256>. Needed from you: decide whether to restore the listed files from the backup (HAR-01, HAR-03 if any file would be removed). Nothing has been restored or repaired.

### TR-6 Observers' questions
1. First dependence on a non-existent person: inject A3 (Dinesh unreachable), then B9 (owners for follow-up).
2. Detected only by a manual check: A2 (`data/` change), B1 (needs someone to run `verify-audit`), A1 (needs the agent to notice).
3. Could destroy evidence: running `verify-audit`/`backup`/`restore` on the live store before copying (B2); deleting sandboxes after a run (OD-16) if they were evidence.
4. Never run: RV-3 (restore `data/`), RV-4, RV-5, RV-10 (rebuild on a second host).

### TR-7 Findings (mapped to the register in `incident-readiness.md`)
| ID | Finding | Register | Confidence |
|---|---|---|---|
| TF-01 | Agent-steering detection is not independent | F-29-13 | Medium |
| TF-02 | `data/` change detection delayed to stage boundaries; no preventive barrier | F-29-13 | High |
| TF-03 | No alternate for L3 | F-29-07 | High |
| TF-04 | RV-3 / RV-10 unrehearsed | F-29-10 | High |
| TF-05 | Exit 1 + traceback instead of exit 17 for a malformed anchor | F-29-01 | High |
| TF-06 | No read-only verify mode | F-29-04 | High |
| TF-07 | Backup manifest not independently anchored | F-29-05 | Medium |
| TF-08 | No merge tool for post-backup records | F-29-06 | High |
| TF-09 | Config location/backup Unknown | F-29-15 (and `dr-plan.md` DRF-05) | Medium |
| TF-10 | Follow-up ownership repeats INC-2025-014 | F-29-07 | High |

## Evidence References
`docs/29-incident-bcdr/evidence/` (17 files, `SHA256SUMS.txt` inside); `hub/admin/cli.py`; `hub/ops/backup.py`; `hub/security/audit.py` (`read_anchors`, `write_anchor`); `operations/incidents/INC-2025-014.md`.

## Assumptions
- A-29-TR-1 [Assumption] The rehearsal result on a 104 KB store is indicative of mechanism, not of scale.
- A-29-TR-2 [Assumption] Severity assignments in TR-2 would survive review by Dinesh. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-29-TR-1 How a team (or Dinesh) would perform under the scenario; decision latency.
- U-29-TR-2 Whether the defect in RH-07 reproduces with other malformed anchor shapes (only one tested).
- U-29-TR-3 Whether a second run would show different timings.

## Unresolved Issues
- A people-based tabletop with Dinesh is outstanding. Exit-code defect not fixed (VALIDATE mode; route to Stage 30). RV-3, RV-4, RV-5, RV-10 unrehearsed.

## Residual Risks
- RR-29-TR-1 Self-run, self-reviewed exercise may miss gaps a second person would find (Medium).
- RR-29-TR-2 Mechanical results from a toy store may be over-read as recovery proof (Medium); `rto-rpo.md` states they are not.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
