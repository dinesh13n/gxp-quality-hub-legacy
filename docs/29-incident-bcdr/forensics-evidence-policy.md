---
stage: "29 — AI Incident Response + BC/DR"
artifact: "forensics-evidence-policy.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["docs/25-governance/evidence-retention-policy.md (RC-1..RC-11)", "docs/00-preflight/operating-contract/evidence-contract.md", "hub/security/audit.py", "hub/admin/cli.py", "hub/ops/backup.py", "hub/obs/log.py", "docs/29-incident-bcdr/evidence/", "docs/24-security-privacy/residual-security-risks.md (RS-03)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
How evidence is preserved when something goes wrong. The product already has strong integrity mechanisms (insert-only tables, a hash-chained audit log, an anchor file, backup manifests with SHA-256) but they live **on the same host** as the data (RS-03), product logs are **not persisted**, and several hub commands **change the evidence they inspect**. This policy therefore says: copy first, hash, verify on the copy, keep everything (hold-all, OD-15), and never "repair" before the copy exists. It is a proposal for Dinesh; no retention period exists (OPD-09, 'accepted open').

## Findings
### FE-1 What counts as evidence (maps to retention classes RC-1..RC-11)
| Evidence | Where | Class | Volatility | Integrity check |
|---|---|---|---|---|
| Terminal/stderr output, structured JSON log lines | terminal only; not persisted (DEV-70, RC-9) | RC-9 | **High: lost on close** | none |
| Process state / running server | OS | n/a | High | n/a |
| `hub.sqlite3`, `-wal`, `-shm`, `-journal` | hub `--data-dir` | RC-1/RC-3 | Medium (changes on any hub command) | audit chain, SHA-256 |
| Audit anchor file `audit-anchor.jsonl` | `audit.anchor_path` (must be set; outside the DB directory) | RC-2 | Medium (rewritten at the end of every admin run) | `verify-audit` |
| Config file(s) and decision flags | operator-edited, location Unknown | RC-4 | Medium | `CONFIG_LOADED` config hash |
| Working-tree `data/` and baseline backup | repo and `../_data-backup-2026-10-17/` | RC-7/RC-8 | Low | `sha256sum -c` (1,512 files) |
| Git history, branches, tags, OD log, stage evidence | local repo, private remote | RC-4/RC-5 | Low | commit ids, `SHA256SUMS.txt` per evidence folder |
| Sandbox copies and run logs | `~/fde_sbx/...` | RC-6 | deleted after each run (OD-16) | excerpts + hash recorded in artifacts |
| Agent/session transcript, tool results | assistant platform | n/a | Unknown retention | Unknown |

### FE-2 Rules
1. **FE-01 Order of collection** (most volatile first): terminal output and `git status` -> process list and listening ports -> `hub.sqlite3`/`-wal`/`-shm`/anchor/config files -> git refs and `HEAD` -> checksums of `data/` -> everything else.
2. **FE-02 Copy-before-touch.** Make a copy of each file with `cp -p` (preserve times) into a new evidence folder **outside the working tree and outside the hub data dir**; compute `sha256sum` of the original and the copy; they must match; write the hashes in the incident record. Do not move originals.
3. **FE-03 Never inspect the live store with a writing command.** `hub.admin verify-audit` appends an `AUDIT_VERIFIED` record and rewrites the anchor at the end of the run; `backup` appends `BACKUP`; `restore` appends `STORE_RESTORED`; `migrate` appends records. [Verified Fact: `hub/admin/cli.py`; in the rehearsal the audit record count rose with each command: 2 after the first verify, 5 after backup, 6 after the next verify.] So: run `verify-audit` on a **copy** in a sandbox (the hub refuses worktree or backup locations, `hub/guards/sandbox.py`). Reading with a plain SQLite read-only open on the copy is acceptable.
4. **FE-04 Read-only analysis.** Work only on copies; set the evidence folder read-only (`chmod -R a-w`) once hashed.
5. **FE-05 Nothing is deleted.** Hold-all is the only retention rule (OD-15). Restore sets the old store and anchor aside under `<data_dir>/pre-restore/<stamp>/`, it never deletes them (`hub/ops/backup.py` `restore`; observed in rehearsal step 08). Any later disposal needs HAR-03 and a policy that does not exist.
6. **FE-06 Chain of custody** (fields, roles only): evidence id, what, original path, copy path, sha256 original / copy, collected at (UTC), collected by (role; agent or Dinesh), transferred to (role), reason. Every transfer adds a row; no row is edited after the fact (append a correction row).
7. **FE-07 Chain-break evidence.** For `E-SEC-AUDIT-TAMPER-DETECTED`, keep the output envelope (`kind`, `first_broken_seq`, `records`) and the anchor lines. The known limit is that records appended after the last anchor and then deleted are not detectable (R-SEC-1, printed by `verify-audit`), so absence of a finding is not proof of no tampering [Verified Fact].
8. **FE-08 Real data found** (STOP-04): do not copy it into further places. Record only path, size and hash; Dinesh decides handling (HAR-09).
9. **FE-09 Untrusted content.** Hostile text (injection strings) is evidence: quote it as data inside a fenced block and never execute or follow it (STOP-05). Preserve the file; do not "clean" it.
10. **FE-10 Agent actions.** For an agent-caused incident preserve the session identifier (`Claude-Session` trailer in commits), the commit range, the tool call list if the platform exposes it [Unknown], and `git reflog` of the clone. Do not rewrite history (CC-01).
11. **FE-11 Time.** Record times in UTC; the hub uses an injected clock (`canonical.utc_now`), so sandbox times are real times. Device clock accuracy is Unknown.
12. **FE-12 Backup of evidence.** The evidence folder itself is a second copy on the same device unless Dinesh approves an off-device copy (HAR-09); say so in the record.

### FE-3 Evidence integrity checks available today
| Check | Command (sandbox/copy) | What it proves | What it does not prove |
|---|---|---|---|
| Baseline data intact | `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` from repo root, expect rc 0 | 1,512 backed-up files equal the live files (observed rc 0 before and after this stage) | the backup itself is uncorrupted if both changed; nothing outside those 1,512 files |
| Backup intact | `cd <backup> && sha256sum -c SHA256SUMS` and `hub.ops.backup.verify_backup` | files equal the manifest | the content was ever correct |
| Audit chain | `python -m hub.admin --config C verify-audit --data-dir COPY` | chain and anchors agree up to the last anchor | records after the last anchor deleted; same-host anchor can be replaced by an operator (RS-03) |
| Git | `git fsck`, `git log`, tags | history consistent | working-tree edits not committed |

### FE-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| FEF-01 | [Verified Fact] Admin commands that look read-only (`verify-audit`) write to the store and anchor | `hub/admin/cli.py`; rehearsal logs 03, 06 | Careless verification changes the evidence | Medium | High | Add a true read-only verify mode? (Stage 30 option) |
| FEF-02 | [Verified Fact] Logs are not persisted | `hub/obs/log.py` docstring, DEV-70 | Detection detail lost | Medium | High | Persist logs in a real deployment? |
| FEF-03 | [Verified Fact] The anchor and the store share a host; the operator can change both | RS-03 | Tampering by a host operator is not independently detectable | Low-Medium | High | seal option is built, opt-in (DQ-S24 assumption) |
| FEF-04 | [Inference] Evidence from the AI assistant platform (transcripts, tool logs) may be outside the repo and outside Dinesh's control | OD-34 V-04 | Agent-incident forensics may be incomplete | Medium | Low | platform retention [Unknown] |
| FEF-05 | [Verified Fact] `restore` keeps the replaced files, but only inside the same data dir | rehearsal step 08 | If the dir is lost, so are the set-aside copies | Low-Medium | High | none |

## Evidence References
`hub/ops/backup.py`; `hub/admin/cli.py`; `hub/security/audit.py`; `docs/25-governance/evidence-retention-policy.md`; `docs/29-incident-bcdr/evidence/s29-log-03..09`.

## Assumptions
- A-29-FE-1 [Assumption] Copy-first and read-only-analysis rules are agent proposals. Confirm: Dinesh.
- A-29-FE-2 [Assumption] An evidence folder outside the working tree on the same device is acceptable until Dinesh decides on an off-device copy.

## Unknowns
- U-29-FE-1 Retention period, legal hold, disposal authority (OPD-09).
- U-29-FE-2 What the assistant platform retains and who may export it.
- U-29-FE-3 Time source accuracy on the laptop and VM.

## Unresolved Issues
- No read-only verify mode; no persisted logs; no off-device evidence copy; no custodian role.

## Residual Risks
- RR-29-FE-1 Evidence altered by well-meaning verification before the copy is taken (Medium).
- RR-29-FE-2 Single-device evidence (see `dr-plan.md` DRF-01).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
