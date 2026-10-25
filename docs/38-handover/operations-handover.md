---
stage: "38 — Handover + Knowledge Transfer"
artifact: "operations-handover.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/31-observability/operational-runbook.md", "docs/31-observability/alert-catalog.md", "docs/31-observability/slo-sla-definitions.md", "docs/29-incident-bcdr/ (11 procedures + tabletop)", "docs/30-release/ (11 files + evidence/)", "docs/28-reliability/", "docs/37-operating-model/support-model.md", "docs/37-operating-model/escalation-model.md", "operations/runbook.md", "operations/incidents/INC-2025-014.md", "docs/32-finops/", ".fde/orchestrator-decisions.md OD-28, OD-34..OD-37"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. This is the handover of a PREPARED-BUT-UNRELEASED system: Stage 30 is BLOCKED (0 of 40 approvals), no cutover, authority flip, tag or release happened, and the hub is not deployed beyond loopback. The only human is Dinesh Naik, Engagement lead (OD-04). No receiving team, trainee, walkthrough audience, exercise result, sign-off or approval is invented here; vacant roles stay vacant (Stage 37). Nothing here accepts a risk (HAR-11). The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
How to operate, observe, diagnose, release, roll back and recover the hub, and how little of this has been done by a person. There is **no production operation to transfer**: no deployment, no on-call, no ticketing, no SLA, no incident history for the hub, no telemetry sink (`support-model.md` Summary). What exists is a set of procedures, CLIs and sandbox rehearsals. Release and cutover were **prepared and rehearsed, not executed**; Stage 30 is BLOCKED (OD-37).

## Findings
### OH-1 Where each operating topic lives [Verified Fact]
| Topic | Primary document | Mechanics | Rehearsed? |
|---|---|---|---|
| Install / deploy (shadow) | `docs/30-release/deployment-strategy.md` DS-1; `environment-promotion-plan.md` | `hub.admin migrate/status/startup-check/verify-audit`; `golden-compare` (exit 6 expected) | Agent, sandbox (logs 01-06) |
| Cutover per capability CUT-1..5 | `cutover-checklist.md`; `feature-flag-plan.md` | `hub.control set-flag --approval-ref`, `flip-to-shadow` | Agent, sandbox only; shipped config never touched |
| Go / no-go | `go-no-go-criteria.md`; `hub/release/` evaluator (merged, not wired) | evaluator returns NO-GO | Agent; 0 of 40 approvals |
| Observe | `docs/31-observability/operational-runbook.md` RB-00..RB-12; `alert-catalog.md` ALT-01..13; `slo-sla-definitions.md` | `hub.obs evaluate/traces/catalog/expo`; `hub report health` | STG31 tests only; observability not wired |
| Incident response | `docs/29-incident-bcdr/incident-severity-matrix.md` (SEV-A/B/C), `containment-procedures.md`, `ai-incident-playbook.md`, `communications-plan.md`, `forensics-evidence-policy.md` | kill switch, copy-then-verify | Desk tabletop by an agent; **no human participants** |
| Backup, restore, DR/BC | `dr-plan.md`, `bc-plan.md`, `recovery-procedure.md`, `failover-procedure.md`, `rto-rpo.md`; `docs/30-release/backup-validation.md` | `hub.admin backup/restore` | Agent, sandbox (L2) |
| Rollback | `docs/30-release/rollback-plan.md` L1/L2/L3 | git revert; restore; `flip-to-shadow` | Agent, sandbox, all three |
| Reliability and degradation | `docs/28-reliability/` (timeouts, breaker, fallback matrix, capacity) | `hub/resilience/` built, not wired | Unit-level only |
| Cost | `docs/32-finops/` | zero model spend by design; all other costs Unknown | n/a |
| Support tiers and escalation | `support-model.md`; `escalation-model.md` | T0..T4; every route ends at Dinesh | Not exercised |
| Legacy operation | `operations/runbook.md` (3 short paragraphs: `./run.sh`, `GET /health`, `python -m app.generate --reset`, `python -m app.integration`) | unchanged legacy | n/a; INC-2025-014 follow-up owner unknown |

### OH-2 The minimum an operator needs to know on day one [Verified Fact]
1. **Never operate on the working-tree `data/`**; use a sandbox copy and check `SHA256SUMS` before and after.
2. `verify-audit` and `backup` **mutate** (append audit rows, rewrite the anchor). There is no read-only verify. Copy first (F-29-04).
3. Exit codes worth knowing: 6 golden-compare unapproved (expected today), 9 egress/exposure/no-AI findings, 16 scan findings, 17 audit tamper, 20 release-checklist refuses ready, 21 corrupt backup, 3 killed (`E-HUB-KILLED`), 2 config invalid. DQ-04 keeps the clashing numbers 2 and 9 (OD-29).
4. The kill switch is read at **command start**, not by a running server; stop the process to contain a live server (DS-6).
5. A restore **sets aside** records written after the backup (`pre-restore/<stamp>/`); it never merges them. Re-ingesting or reviewing them is a manual decision (F-29-06).
6. Rollback after an authoritative period is **compensating, not restorative**: the ledger is append-only (RF-RB-2).
7. Regenerating the database is **not** a recovery path (different sha256, rollback-plan RB-4).
8. Rollback authority is Dinesh alone (F-29-07); no alternate exists (ER-18).

### OH-3 Operational targets are placeholders [Verified Fact]
RTO 4 h and RPO 1 working day are **agent targets** (OD-35, A-30-07); five SLO candidates carry **no SLA** (OD-36); retries 3, breaker 3 failures/60 s, cap 64, budget 20 %, rate limit 100 refusals/60 s are all agent assumptions. Agent timings (0.01 to 4.5 s per command on a 100 KB store) are tool times, not recovery times.

### OH-4 What cannot be recovered or covered today [Verified Fact]
| Gap | Evidence |
|---|---|
| Device loss: backups and baseline share one device; no off-device copy | F-29-02, AP-OPS-04, HAR-09 open |
| No paging, no remote access, no automatic remediation, no host metrics | runbook RB-12 |
| ES-20..ES-25 domain escalation routes have no owner | `escalation-map.md`, TF-04 |
| Nightly legacy file exchange (ADR-007) and parallel legacy-customer workflow (OPD-15) are VACANT | PA-25, PA-26 |
| Late deliveries need a manual catch-up run; scheduler is off | OD-28, RB-07 |
| Live-server kill, large-store restore time, off-device restore | U-30-04, RB-6, OX-G5 |

### OH-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| OPF-01 | [Verified Fact] All five required capabilities (deploy, observe, diagnose, roll back, recover) have a written procedure and an executable agent rehearsal, except **observe**, which has no rehearsal on live data | OH-1; `operator-exercise-results.md` OR-1 | Documentation ready; people not | High (real use), Low (inert) | High | Who is the operator? |
| OPF-02 | [Verified Fact] No human has run any operating procedure under pressure | tabletop (OD-35); RR-31-15 | Written procedures unproven for people | Medium | High | Live tabletop (Stage 29 C-1..C-7) |
| OPF-03 | [Verified Fact] Release and cutover were not executed; the hub has no operating history | OD-37 | A receiver gets a design and a rehearsal, not a service | Medium | High | AP-REL-01 |
| OPF-04 | [Inference] The runbook set is large (about 12 procedures in `docs/29`, 12 in `docs/31`, 11 in `docs/30`); a first-time operator needs a one-page path | listings | Cognitive load | Low | Medium | `handover-index.md` reading path (provided) |
| OPF-05 | [Verified Fact] `operations/runbook.md` is the legacy runbook only; it has no incident, restore or release procedure | `support-model.md` SM-3 | Do not use it as the hub runbook | Low | High | - |

## Evidence References
See `evidence_sources`; `docs/30-release/evidence/s30-rehearsal-summary.txt`; `docs/29-incident-bcdr/tabletop-results.md` TR-1, TR-2.

## Assumptions
- A-38-OH-1 Exit codes in OH-2 are as documented in the CLI docstrings and rehearsal logs, not re-run here. Confirm: first receiving operator.
- A-38-OH-2 The operator in practice reads `hub.obs evaluate` output; nothing alerts them (A-31-15).

## Unknowns
- U-38-OH-1 Real operating cost (all non-model costs Unknown, OD-35). U-38-OH-2 Real consumers' reaction to re-pointing (U-14-01, U-30-07). U-38-OH-3 RTO/RPO a business would accept.

## Unresolved Issues
- OH-4 table; AP-OPS-01..13; Stage 29 Q-29-01..09 / C-1..C-7; D-28-01..10; D-31-01..10.

## Residual Risks
- RR-38-OH-1 Device loss unrecoverable (F-29-02). High.
- RR-38-OH-2 First real incident is also the first human use of the procedures. Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 38). |
