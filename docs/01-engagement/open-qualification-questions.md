---
stage: "1 — Engage & Qualify"
artifact: "open-qualification-questions.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/01-engagement/qualification-checklist.md", "docs/00-preflight/discovery/assumptions-unknowns.md", "docs/00-preflight/operating-contract/open-governance-decisions.md", "docs/00-preflight/ai-economics/economics-readiness.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

Questions that block or condition Go. "Blocks" = blocks the stated stage (not Stage 2 start). No question blocks Stage 2. Owner for all: **Engagement lead (Dinesh Naik)** (OD-04); due = before the resolving stage starts (no calendar dates can be committed without stakeholders).

## Findings

| ID | Question | Why it matters | Related | Type | Blocks | Resolving stage | Class |
|---|---|---|---|---|---|---|---|
| OQ-01 | Is there a real sponsor/mandate, or is Dinesh Naik the sole sponsor of a capstone/training engagement? If the latter, confirm that explicitly. | Defines what "approval" and "value" mean | Q-04, ER-02, GD-01 | Condition | Stage 2 outputs' validity | 2 | [Unknown] |
| OQ-02 | Who (named or waived) fills Quality ops, Enterprise app, Finance, Risk & security, Integration lead roles? | Needed to validate claims and definitions | Q-05/06, U-02 | Condition | Stages 3–6 validation | 2 | [Unknown] |
| OQ-03 | Confirm or override OD-02: baseline = shipped 125-case DB, or regenerated 6,000-case (seed 4326, vs default 4100 U-03)? | Before/after comparability | Q-11, U-13, A-02 | **Blocking Stage 4** | 4 | 1 → 4 | [Unknown] |
| OQ-04 | Is any real operational data (handling times, costs, backlog) obtainable, or is the engagement permanently synthetic? | Determines whether value can ever be measured vs only modelled | Q-02, Q-13, U-24 | Condition | 4, 34–36 | 2 / 4 | [Unknown] |
| OQ-05 | Which definitions are authoritative: "closed", "resolved", completion flag, 48 h clock start/stop? | KPI definition | Q-16, U-18, ER-06 | **Blocking Stage 4** | 4 | 2 / 3 | [Unknown] |
| OQ-06 | Who decides the ops-vs-compliance-vs-finance conflict, and is it in scope to resolve or only to record? | Prevents encoding an unowned policy | Q-20, ER-06 | Condition | 6, 9 | 2 | [Unknown] |
| OQ-07 | Deadline, budget, expected duration, and success criteria for the engagement? | Urgency vs readiness | Q-15, ER-11 | Condition | 18 (planning) | 2 | [Unknown] |
| OQ-08 | Is AI/agentic capability an intended outcome, optional, or out of scope? | Prevents premature AI commitment | SCOPE-AMB-04, ER-05 | Condition | 8 | 2 → 8 | [Unknown] |
| OQ-09 | Are GxP/Part 11 references framing only (A-08) or a binding obligation on any resulting system? | Governance scope and cost | Q-10, GD-11 | Condition | 24, 25 | 2 / 25 | [Assumption] |
| OQ-10 | Locate original archive/ZIP and record checksum; confirm commit a6eb4e8 = original (A-01, U-14, U-01). | Provenance | Q-12, ER-14 | Condition | none (non-blocking) | 2 | [Unknown] |
| OQ-11 | Where is batch disposition performed and recorded (A-07/U-17)? | GxP gate not in code | R-12 | Condition | 5 | 2 / 5 | [Assumption] |
| OQ-12 | Scope of Java/JS/SQL consumers, night-shift estate, security hardening (SCOPE-AMB-01/02/05)? | Scope drift | ER-10, GD-10 | Condition | 5 | 2 / 5 | [Unknown] |
| OQ-13 | Approve extending SHA256SUMS to all 1,512 data files (GD-03) before any code-executing stage; confirm OD-05 remote and CI-on-push (GD-09). | Baseline integrity, egress | ER-07, ER-13 | Condition | 7 (code execution) / first push | before 7 | [Verified Fact] open item |
| OQ-14 | Is a second reviewer required for GxP-relevant design decisions (GD-05)? | Independent review | ER-04 | Condition | 23 | 23 / 25 | [Unknown] |

## Evidence References

As cited per row.

## Assumptions

- None beyond those tagged.

## Unknowns

- All rows tagged [Unknown].

## Unresolved Issues

- All 14 open; none blocks Stage 2. OQ-03 and OQ-05 block Stage 4.

## Residual Risks

- If answers never arrive from real stakeholders, outputs remain synthetic-labelled (ER-01).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial question register. |
