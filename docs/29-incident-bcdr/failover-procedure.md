---
stage: "29 — AI Incident Response + BC/DR"
artifact: "failover-procedure.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["docs/29-incident-bcdr/dr-plan.md", "docs/29-incident-bcdr/rto-rpo.md", "docs/33-vendor-risk/exit-plan.md", "docs/33-vendor-risk/substitution-strategy.md", "docs/10-architecture/deployment-architecture.md", "hub/web/server.py", "hub/security/exposure.py", ".fde/orchestrator-decisions.md (OD-23, OD-24)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
Failover here means **moving work or service to a substitute resource by a manual, human-approved procedure**. There is **no high availability, no standby node, no replication, no load balancer and no automatic failover**, and none is appropriate for a loopback-only, single-writer SQLite service that no process depends on. The Stage 28 resilience design that would normally supply failover targets was not available to this run (IR-03); this document uses the vendor exit plan (V-01..V-11) and failure semantics instead and must be reconciled when Stage 28 merges. Failover of the hub across a network is out of bounds anyway: binding beyond 127.0.0.1 is refused (HAR-05, `E-SEC-EXPOSURE-NOT-APPROVED`).

## Findings
### FO-0 Preconditions for any failover
1. An incident record exists and the primary is contained (`containment-procedures.md`); evidence is copied (FE-02).
2. Dinesh has said "fail over" in the engagement conversation; the orchestrator records it as an OD entry (HAR-11). The agent never self-declares.
3. The substitute is verified **before** it is trusted: checksum, `verify-audit`, regression.
4. **Split-brain rule:** the old primary is marked read-only/killed (`hub.kill: true`, process stopped) before the substitute accepts any write. Two live writers on two copies of the store is a SEV-A (diverging audit chains).
5. Failback is a separate decision; do not switch back automatically.

### FO-1 Hub store: move to a second host (cold)
| Step | Action | Check |
|---|---|---|
| 1 | Stop the primary hub process by PID; set `hub.kill: true` | `hub.admin` exits 3 |
| 2 | Take the latest verified backup (or take a fresh one only if the primary is healthy and after copying evidence) | `sha256sum -c SHA256SUMS` in the backup dir, `verify_backup` OK |
| 3 | On the substitute host (Python >=3.10, same commit): create a config with `audit.anchor_path`; `hub.admin restore --data-dir D --backup B` into a data dir outside the repo | restore report `checksum_match: true`, `verify_audit.status: ok` |
| 4 | Run the loopback server on the substitute (`127.0.0.1` only) | `startup-check` reports `exposure: loopback` |
| 5 | Record the audit head (`audit_seq`, `hash`) at hand-over in both hosts' records | equal to the backup manifest `audit_head` |
| 6 | Tell consumers: none are known; otherwise Unknown (OD-28 b) | n/a |
RPO consequence: records written on the primary after the backup are not on the substitute (DRF-04); they stay in the primary's files and in `pre-restore/`.

### FO-2 Working-tree `data/`: no failover target
`data/` is the baseline, not a live service. There is nothing to fail over; recovery is RV-3. Using the cloud workspace copy as a source is a recovery step with HAR-09 considerations, not a failover.

### FO-3 Build assistant substitution (exit plan V-04)
Pause; export the OD log and `.fde/` working agreements; Dinesh chooses the substitute; onboarding requires golden-compare and hub regression on the first change; reviewer reads diffs. The product is unaffected. Target: <= 3 working days (RR-A6) [Assumption].

### FO-4 Cloud workspace to another runner (V-05)
Provision a runner with Python >=3.10; copy the checksum-gated data; run `tests/hub/run_hub_groups.py --all`; expect executed = expected. Keep the characterization harness and data checksums on the reference laptop (OD-23). Delete copies at the old provider only with a recorded deletion (HAR-09/HAR-03).

### FO-5 Remote repository (V-03)
Create the new remote (HAR-09), `git push --mirror`, export PR text, update the remote record (OD-05), compare `git ls-remote` SHAs, `git fsck`.

### FO-6 Not provided (and why)
| Not provided | Reason |
|---|---|
| Active-active or active-passive hub | single-writer SQLite; loopback only; no consumers; would create audit-chain divergence risk |
| Automatic failover or health-triggered switch | no monitoring, no on-call; automatic action would conflict with human-in-the-loop principles (HAR-10) |
| Network VIP/DNS failover | non-loopback exposure refused (HAR-05) |
| Database replication | SQLite file; backup+restore is the supported mechanism (ADR-015) |

### FO-7 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| FOF-01 | [Verified Fact] No standby, replication or automatic failover exists; the supported mechanism is backup + restore | `hub/ops/backup.py`, deployment-architecture | Recovery is manual and slow relative to HA | Low (inert) / High (live) | High | Stage 28 design |
| FOF-02 | [Inference] The split-brain hazard is real: restoring the same backup on two hosts yields two chains with the same prefix | `restore` semantics | Diverging evidence | Medium | Medium | add a host-id marker? (option, not done) |
| FOF-03 | [Verified Fact] The substitute needs the same code commit and Python floor; goldens are environment-specific | OD-23, OD-24 | Different interpreter can show environmental diffs | Low | High | none |
| FOF-04 | [Unknown] Whether a second physical host is available to Dinesh | none | FO-1 cannot be rehearsed on a real second host | Medium | Low | confirm |

## Evidence References
`hub/ops/backup.py`; `hub/guards/sandbox.py`; `hub/security/exposure.py` (loopback); `docs/33-vendor-risk/exit-plan.md` V-03, V-04, V-05, V-10; rehearsal logs 08, 09, 12, 13.

## Assumptions
- A-29-FO-1 [Assumption] Manual cold failover is sufficient while the hub is inert. Confirm: Dinesh.
- A-29-FO-2 [Assumption] A substitute host with Python >=3.10 can be found when needed.

## Unknowns
- U-29-FO-1 Availability of a second host.
- U-29-FO-2 Stage 28 resilience targets (not available).
- U-29-FO-3 Time to complete FO-1 with human steps.

## Unresolved Issues
- No second-host rehearsal; Stage 28 reconciliation pending; no host-id marker to detect split-brain.

## Residual Risks
- RR-29-FO-1 Split-brain by operator error (Medium).
- RR-29-FO-2 Failover is untested on real second hardware (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
