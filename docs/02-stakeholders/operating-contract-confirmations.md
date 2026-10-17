---
stage: "2 — Stakeholder Discovery & Authority Confirmation"
artifact: "operating-contract-confirmations.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/operating-contract/provisional-operating-contract.md", "docs/00-preflight/operating-contract/open-governance-decisions.md", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md", "docs/00-preflight/operating-contract/provisional-tool-agent-permissions.md", "docs/01-engagement/engagement-go-no-go.md", "docs/01-engagement/open-qualification-questions.md", ".fde/orchestrator-decisions.md", "git tag -l (baseline-as-found = a6eb4e8)", "sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt (1,512 lines, CHECK_OK at 2026-10-17)"]
supersedes: "none (records updates to 0B; 0B originals are unchanged)"
---
## Summary

Status of every Stage 0B PROVISIONAL item after Stage 2. Statuses: **CONFIRMED** (source evidence of approval), **CHANGED** (superseded by a later recorded decision/action), **OPEN** (still PROVISIONAL, owner and question stated).

Result: **1 confirmed in effect (HAR-11/OD-04), 1 partly confirmed (HAR-04/OD-01), 3 changed by recorded actions (GD-03, GD-08, GD-14), all other items remain OPEN.** No stakeholder can confirm anything other than Dinesh Naik, and he has not been asked in this run; this stage cannot approve on his behalf (TP-14, AG-5, HAR-11). All open items need his explicit answer or an explicit waiver. 0B originals are not modified.

## Findings

### A. Parties and authority (0B contract section 1)

| 0B item | 0B status | Stage 2 status | Basis |
|---|---|---|---|
| Dinesh Naik: engagement lead, sole human, approves all HAR, decisions, overrides | PROVISIONAL | **OPEN** (partly evidenced). Approval of OD-01 and OD-04 is a [Verified Fact]; "sole sponsor / all decisions" is [Assumption] A-0B-06 | OD log; `approval-authority-map.md` |
| claude-fde-agent orchestrator: delegated review and merge | PROVISIONAL | **PARTLY CONFIRMED** for sequencing and merge-after-review (OD-01); commit/tag/push rights still PROVISIONAL (TP-07) | OD-01 |
| claude-fde-agent stage agent | PROVISIONAL | **OPEN** (Stage 23) | TP matrix |
| Client stakeholders (5 roles) | "None - not identified" | **Unchanged: no authority recorded.** Roles named in `business-context.md`, unconfirmed; unfilled | `stakeholder-map.md` |

### B. Governance decisions GD-01..GD-15

| ID | Stage 2 status | Update / reason | Owner | Next stage |
|---|---|---|---|---|
| GD-01 decision rights | **OPEN** | Evidence only for OD-01/OD-04 approvals. Needs Q-02-01 | Engagement lead (Dinesh Naik) | 23 / 37 |
| GD-02 baseline dataset | **OPEN** (blocks Stage 4) | OD-02 still "Provisional default". Q-02-04 | Engagement lead (Dinesh Naik) | Before 4 |
| GD-03 extend checksum manifest | **CHANGED - action done** | `SHA256SUMS.txt` now has 1,512 lines (equals 1,512 data files); `sha256sum -c --quiet` passes (OD-03a "Done") [Verified Fact] | Engagement lead (Dinesh Naik) to acknowledge | 25 (acknowledge) |
| GD-04 tool/agent permission matrix | **OPEN** | No approval recorded | Engagement lead (Dinesh Naik) | 23 |
| GD-05 separation of duties | **OPEN** | No second approver exists. Q-02-09 | Engagement lead (Dinesh Naik) | 23 / 25 |
| GD-06 environment ownership, Docker host | **OPEN** | Unknown | Engagement lead (Dinesh Naik) | 5 / 7 |
| GD-07 retention of sandbox logs | **OPEN** | Unknown | Engagement lead (Dinesh Naik) | 25 |
| GD-08 tag baseline | **CHANGED - action done** | Tag `baseline-as-found` exists on a6eb4e8 (`git tag -l`, `git rev-parse`; OD-06 "Done") [Verified Fact] | Engagement lead (Dinesh Naik) to acknowledge | 25 (acknowledge) |
| GD-09 remote + CI-on-push | **OPEN** | OD-05 "Pending repo creation". Q-02-12 | Engagement lead (Dinesh Naik) | Before first push |
| GD-10 scope ambiguities SCOPE-AMB-01..05 | **OPEN** | No stakeholder to rule. Q-02-10 | Engagement lead (Dinesh Naik) | 5 / 24 |
| GD-11 GxP/Part 11 framing only | **OPEN** | `domain-assurance.md` says synthetic environment, "not compliance certification" [Verified Fact]; whether binding is [Assumption]. Q-02-06 | Engagement lead (Dinesh Naik) | 25 |
| GD-12 human-control rules for AI | **OPEN** | HAR-12/STOP-07 prohibition stands; no AI exists (0 model calls) | Engagement lead (Dinesh Naik) | 23 |
| GD-13 steady-state ownership | **OPEN - governance gap** | No owner anywhere; ADR-007 owner unnamed | Engagement lead (Dinesh Naik) | 37 |
| GD-14 amend OD-03 to full-copy sandbox | **CHANGED - done** | Recorded as OD-03a [Verified Fact] | Engagement lead (Dinesh Naik) to acknowledge | 25 (acknowledge) |
| GD-15 instruction precedence | **OPEN** | No approval recorded | Engagement lead (Dinesh Naik) | 25 |

### C. Human approval rules HAR-01..HAR-16

See `approval-authority-map.md` section B. Summary: HAR-11 **confirmed in effect** (OD-04); HAR-04 **partly confirmed** (delegated review per OD-01); HAR-01..03, 05..10, 12..16 **OPEN/PROVISIONAL**. HAR-12 prohibition stands with no available approver.

### D. Stage 1 Conditions on Go (CG-1..CG-7) touching Stage 2

| ID | Condition | Stage 2 outcome |
|---|---|---|
| CG-1 | Name owners or record explicit waiver | **OPEN**: no owner named. Waiver text prepared below (Q-02-02); not recorded because only Dinesh can waive. Fallback in CG-1: all value statements downgraded to "synthetic, unvalidated" |
| CG-2 | Confirm/override OD-02 | OPEN (Q-02-04) |
| CG-3 | Metric definitions, data availability | OPEN (Q-02-05, Q-02-11) |
| CG-4 | AI as hypothesis H6 only | Standing; OPEN for explicit confirmation (Q-02-07) |
| CG-5 | GxP/Part 11 treatment | OPEN (Q-02-06) |
| CG-6 | Checksum manifest and sandbox | **Partly met** (manifest 1,512 and check pass); remote/CI acceptance open |
| CG-7 | Escalate ops/compliance/finance conflict as owned policy decision | **Escalated** in `stakeholder-conflicts.md` SC-01..SC-03; decision open (Q-02-05) |

### E. Decisions and questions for Dinesh Naik (exact)

Each can be answered by a direct message or an "Approved" OD-log entry. Silence is not approval.

| ID | Question / decision | Options | Resolves |
|---|---|---|---|
| Q-02-01 | Are you the sole sponsor, business owner, technical owner and approver for this capstone? Any other human with authority? | (a) Yes, sole (confirm A-0B-06 / GD-01) (b) Name others | GD-01, OQ-01, CG-1 |
| Q-02-02 | Fill or waive the client roles (Quality ops lead, Enterprise app owner, Finance partner, Risk and security partner, Integration lead, plus product, data, privacy owners). Suggested waiver text: "Client-side roles are unstaffed in this synthetic capstone; outputs are not validated by client stakeholders; I (Dinesh Naik) accept this and will treat role statements as claims." | Waive all / fill some with named personas | OQ-02, CG-1, ER-02 |
| Q-02-03 | Confirm the HAR-01..HAR-16 list as the approval rules. Must you personally approve each BUILD merge (HAR-04), or does OD-01 delegation suffice? | Confirm / amend | GD-04, HAR, U-02-08 |
| Q-02-04 | Baseline dataset: keep shipped 125-case DB (OD-02) or regenerate 6,000-case (seed 4326 vs 4100)? | Keep / override | GD-02, OQ-03, CG-2 (blocks Stage 4) |
| Q-02-05 | For ops-vs-compliance-vs-finance (SC-01..03): decide the working definitions of "closed", "resolved", and the 48 h clock for the capstone, or record as open and let Stage 4 report separate provisional KPIs? | Decide / defer | OQ-05, OQ-06, CG-3, CG-7 |
| Q-02-06 | GxP / Part 11: framing only, or binding on any resulting system? | Framing / binding | GD-11, OQ-09, CG-5 |
| Q-02-07 | AI: hypothesis only until Stage 8 (CG-4), intended outcome, or out of scope? | Hypothesis / intended / out | OQ-08 |
| Q-02-08 | Pace and constraints: deadline, budget, success criteria, and how often you want confirmation checkpoints (Stages 4, 8, 14, 23, 25 proposed)? | State or "none" | OQ-07, ER-11 |
| Q-02-09 | Second reviewer for GxP-relevant design decisions: required, or accept single-approver risk (ER-04)? Accept the escalation ladder in `escalation-map.md` (ES-09: no alternate)? | Add reviewer / accept risk | GD-05, OQ-14 |
| Q-02-10 | Scope: Java/JS/SQL consumers, night-shift/enterprise estate, security hardening (SCOPE-AMB-01/02/05) in or out? | Per item | GD-10, OQ-12 |
| Q-02-11 | Is any real operational data obtainable, or is the engagement permanently synthetic? Where is batch disposition performed (A-07)? Locate original archive/checksum (provenance, OQ-10)? | Answers | OQ-04, OQ-10, OQ-11 |
| Q-02-12 | Acknowledge OD-03a / OD-06 (GD-03, GD-08, GD-14) and decide GitHub remote and CI-on-push (OD-05, GD-09). | Approve / defer | GD-03/08/09/14 |

## Evidence References

See `evidence_sources`. Commands run in Stage 2 (read-only): `git tag -l`, `git rev-parse --short a6eb4e8`, `wc -l` and `sha256sum -c --quiet` on the backup manifest (CHECK_OK), `git status --porcelain` (only `docs/02-stakeholders/` untracked).

## Assumptions

- A-02-09: Until Dinesh answers, every OPEN item continues under 0B PROVISIONAL rules. Confirm: Engagement lead (Dinesh Naik).

## Unknowns

- All Unknowns listed in the sibling artifacts (U-02-01..U-02-13).

## Unresolved Issues

- 12 questions (Q-02-01..Q-02-12) awaiting Dinesh; due: before the resolving stage listed per row, with Q-02-01, Q-02-02 requested before Stage 3 and Q-02-04, Q-02-05 before Stage 4 (these two are blocking for Stage 4).

## Residual Risks

- Prolonged PROVISIONAL status of 12 of 15 GD items and 14 of 16 HAR items (ER-02, ER-04).
- Confirmation by the orchestrating agent would be circular and is not permitted.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial confirmations record; 0B originals untouched. |
