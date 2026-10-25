---
stage: "29 — AI Incident Response + BC/DR"
artifact: "rto-rpo.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["docs/29-incident-bcdr/dr-plan.md", "docs/29-incident-bcdr/bc-plan.md", "hub/ops/backup.py", "docs/33-vendor-risk/exit-plan.md", "docs/37-operating-model/support-model.md", "docs/25-governance/evidence-retention-policy.md", ".fde/orchestrator-decisions.md (OD-04, OD-16, OD-21, OD-32)", "docs/29-incident-bcdr/evidence/s29-rehearsal-summary.txt"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
Recovery time and recovery point **targets** for each asset. **Every number here is a TARGET or an ASSUMPTION proposed by the agent. None is measured, agreed with a business owner, or contractually committed; no business owner exists (OD-04).** They are sized to the engagement's reality (one person, one laptop, synthetic data, no consumers) and to what the tooling can plausibly do, and they must be re-derived from a real business-impact analysis before any real use (`bc-plan.md` BC-3). The only measurements in this stage are tool wall-clock times from a sandbox rehearsal on a 104 KB synthetic store (<= 0.16 s per hub command); those measure the commands, not an end-to-end recovery, and are **not** evidence for any RTO.

Definitions used: **RPO** = maximum acceptable age of the newest recoverable copy at the moment of loss (data written after it is lost or must be re-created). **RTO** = maximum acceptable elapsed *working* time from the decision to recover until the asset is verified usable (checksum and, for the store, `verify-audit`). "Working hours" because there is no on-call.

## Findings
### RR-1 Targets by asset
| ID | Asset (DA-n) | Tier | RPO target | RTO target | Basis | How RPO is met today | How RTO would be met | Gap |
|---|---|---|---|---|---|---|---|---|
| RR-A1 | Hub store + anchor (DA-1, DA-2) | 1 | <= 1 working day, and always a backup immediately before `migrate`, a rule-set change, an authority-switch change, or a restore | <= 4 working hours on the same host (sandbox-first), <= 1 working day on a rebuilt host | Assumption A-29-RR-1; exit plan V-10 "day" | `hub.admin backup` is manual; `migrate` auto-backs-up; no schedule | RV-2 | No schedule; no off-device copy; larger-store behaviour Unknown |
| RR-A2 | Hub config + decision flags (DA-3) | 1 | 0 versions lost: every change recorded with approval_ref and committed | <= 1 working hour | A-29-RR-2 | Unknown where the file lives | RV-8 | Location/ownership Unknown |
| RR-A3 | Baseline `data/` + backup (DA-4) | 1 | 0 (static baseline; any difference is a SEV-A) | <= 4 working hours to restore a differing file set from the backup; <= 1 working day to rebuild on a new host if a copy survives | A-29-RR-3 | `sha256sum -c` rc 0 observed 2026-10-25 | RV-3 | Backup shares the device with the primary: device loss = loss of both (DRF-01) |
| RR-A4 | Git repo, docs, evidence, OD log (DA-5) | 1 | <= last merged PR / last push by the orchestrator (push cadence Unknown) | <= 1 working day to a new remote or host | exit plan V-03 | private remote; local clones | RV-9 | Unpushed work on a lost device is lost |
| RR-A5 | Cloud workspace data copy (DA-6) | 2 | n/a (derived copy) | <= 1 working day to re-provision | exit plan V-05 | checksum-gated (OD-23) | RV-9 | provider terms Unknown |
| RR-A6 | AI coding assistant / runners (DA-8) | 3 | n/a | <= 3 working days to a substitute | exit plan V-04 "days" | n/a | FO-3 | no contract; context lost on switch |
| RR-A7 | Sandbox copies (DA-7) | 4 | n/a (disposable) | <= 1 working hour to re-create | OD-16 deletes after each run | git archive + checksum-gated data | RV-1 | disk ~9.8 GB |
| RR-A8 | Hub service in shadow (BF-3) | 3 | n/a | <= 1 working day to restart after verifying A1/A2 | A-29-RR-4 | `./run.sh`; loopback | RV-2 | no health watcher |

### RR-2 How the targets relate to each scenario
| Scenario | Binding target | Worst plausible RPO today | Worst plausible RTO today | Within target? |
|---|---|---|---|---|
| IS-11 chain break / DR-S1 | RR-A1 | everything since the last manual backup (Unknown age; in the rehearsal, 1 backup) | restore + verify measured at <1 s of tool time, plus human time (Unknown) | Cannot be said: human time and backup age unmeasured |
| IS-10 / DR-S4 device loss | RR-A3, RR-A4 | baseline: 0 only if the cloud copy is intact; hub store: since last off-device copy = **never** (no off-device copy) | rebuild "a day" is an order-of-magnitude Assumption | **Not met for the hub store; Unknown for baseline** |
| IS-09 outage | RR-A4..A6 | last push | hours-days | Plausible, unmeasured |
| IS-08 config | RR-A2 | Unknown | <= 1 hour | Unknown |

### RR-3 Dependencies and ordering for a full rebuild
1. Host + Python -> 2. git clone + `git fsck` -> 3. `data/` verified (RR-A3) -> 4. config (RR-A2) -> 5. hub store restore (RR-A1) -> 6. `verify-audit` -> 7. regression/harness -> 8. Dinesh decision to resume. The slowest step is likely obtaining data (RR-A3) if only the cloud copy survives.

### RR-4 Measurement plan (so the targets can become evidence)
| Measure | How | When | Owner |
|---|---|---|---|
| Restore wall-clock on a realistic store | build a sandbox store at the 125-case baseline plus runs; time backup / restore / verify | Stage 30 or at the next DR rehearsal | Engagement lead (Dinesh Naik) to assign |
| Backup age at random sample times | list backup labels vs. last audit sequence | each stage close | orchestrator |
| Rebuild on a second host | cold rebuild per DR-3 in a clean sandbox | once, before any exposure | Dinesh decision |
| Human decision latency | tabletop with Dinesh as participant | next tabletop | Dinesh |

### RR-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| RRF-01 | [Verified Fact] No RTO/RPO existed before this stage; `docs/operations-service-levels.md` is legacy history | support-model SM-3 | None to compare with | Low | High | none |
| RRF-02 | [Inference] The proposed RPO for the hub store cannot be met against device loss because no off-device copy exists | DRF-01 | Target is aspirational for DR-S4 | High (if a real store existed) | High | off-device copy approval (HAR-09) |
| RRF-03 | [Verified Fact] Tool times are tiny on the synthetic store | `evidence/s29-rehearsal-summary.txt` | Human and approval time will dominate | Low | Medium (small sample, one run) | measure at scale |
| RRF-04 | [Assumption] Working-hours RTO ignores any 24x7 expectation; none is stated | A-29-RR-4 | Wrong if a business later needs 24x7 | Unknown | Low | business owner |

## Evidence References
`hub/ops/backup.py`; `docs/29-incident-bcdr/evidence/s29-log-04`, `-08`, `-09`, `-10`; `s29-rehearsal-summary.txt`; `docs/33-vendor-risk/exit-plan.md`; `docs/25-governance/evidence-retention-policy.md` RC-7, RC-8.

## Assumptions
- A-29-RR-1 [Assumption] RPO <= 1 working day and RTO <= 4 working hours for the hub store are targets chosen by the agent under OD-32. Confirm: Engagement lead (Dinesh Naik).
- A-29-RR-2 [Assumption] Config changes are recorded and committed.
- A-29-RR-3 [Assumption] The baseline is static and is not allowed to change (OD-09 confirmed it as the shipped 125-case dataset).
- A-29-RR-4 [Assumption] Working-hours RTO is enough while no business process depends on the hub.

## Unknowns
- U-29-RR-1 Business-derived RTO/RPO (no business owner).
- U-29-RR-2 Real store size and growth.
- U-29-RR-3 Actual time for a human-in-the-loop recovery.
- U-29-RR-4 Push cadence of the orchestrator (sets RR-A4).

## Unresolved Issues
- RRF-02; no schedule; no measured recovery; no business sign-off (cannot be obtained: no stakeholder).

## Residual Risks
- RR-29-RR-1 Targets are unsupported by measurement (Medium).
- RR-29-RR-2 Device loss defeats the stated RPO (High if real data existed; Low for synthetic).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
