---
stage: "1 — Engage & Qualify"
artifact: "qualification-checklist.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/discovery/*.md", "docs/00-preflight/operating-contract/*.md", "docs/00-preflight/ai-economics/economics-readiness.md", "docs/business-context.md", "docs/correspondence/operations-vs-risk-2024.md", "docs/historic-decisions.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

Seven required analysis dimensions, expanded to 21 criteria. Status scale: **MET** (evidence), **PARTIAL**, **NOT MET**, **UNKNOWN**. Result: 5 MET, 9 PARTIAL, 4 NOT MET, 3 UNKNOWN. No criterion is a hard disqualifier by itself, but the 4 NOT MET items become conditions on Go (see `engagement-go-no-go.md`). Claims (C) are separated from validated evidence (E) in each row.

## Findings

| # | Dimension | Criterion | Claim (C) | Validated evidence (E) | Status | Confidence | Impact | Unresolved |
|---|---|---|---|---|---|---|---|---|
| Q-01 | 1 Significance | Business problem is stated | C: rising exception effort, inconsistent feed data (`business-context.md`) | E: structural inconsistencies exist in synthetic data (DF-03, WF-06, IO-01..03) | PARTIAL | Medium | Problem is real *in the simulator* only | Real-world existence (OQ-01) |
| Q-02 | 1 | Problem magnitude quantified | C: none | E: none; costs are synthetic/modelled; shipped DB is test residue (DF-01) | NOT MET | High | Value cannot be sized | Baseline (OQ-04, Stage 4) |
| Q-03 | 1 | Value signal independent of AI | — | E: deterministic gaps (WF-05/06, IO-01..03) need no model (0C key finding 5) | MET [Inference] | Medium | Engagement has value path without AI | Confirm at Stage 8 |
| Q-04 | 2 Sponsorship | Named sponsor exists | C: none | E: none; proxy = engagement lead (GD-01) | NOT MET | High | No external mandate | OQ-01 |
| Q-05 | 2 | Business owner identified | Roles only | E: no named person | UNKNOWN | High | Cannot confirm definitions | OQ-02 |
| Q-06 | 2 | Technical owner identified | ADR-007 "owner transferred 2024" | E: none named | UNKNOWN | High | No one to confirm runtime | OQ-02 |
| Q-07 | 2 | Decision rights defined | — | E: provisional contract, Dinesh sole approver (GD-01) | PARTIAL | Medium | Authority is PROVISIONAL | Stage 2 |
| Q-08 | 3 Feasibility | System understood well enough to plan | — | E: 12 discovery artifacts, 15 tests green in isolated copy (`discovery-summary.md`) | MET | High | — | Stage 7 deepens |
| Q-09 | 3 | Safe execution model | — | E: full-copy sandbox rule OD-03a; backup + checksums (6 SQLite) | MET | High | Baseline protected | GD-03: lake files un-checksummed |
| Q-10 | 3 | Governance / compliance feasibility | C: GxP, Part 11 framing | E: no audit trail, no authn/z (SO-01/02/09); A-08 assumes framing only | PARTIAL | Medium | Any real use would need controls | OQ-09 |
| Q-11 | 4 Data/access | Authoritative baseline dataset | OD-02 provisional: shipped 125-case DB | E: README promises 6,000 (seed 4326); shipped DB incoherent (R-03) | PARTIAL | High | Wrong baseline invalidates KPIs | OQ-03 (blocking Stage 4) |
| Q-12 | 4 | Original snapshot / provenance | Commit msg "unmodified" | E: no origin repo, 2 commits (now 6 with FDE history); A-01 unverified | PARTIAL | Medium | Provenance unproven | OQ-10 |
| Q-13 | 4 | Real data / production access | — | E: none, and prohibited by contract (E3/E4 denied) | NOT MET (by design) | High | Real baselines unobtainable in-engagement | OQ-04 |
| Q-14 | 4 | Data safe to use | — | E: synthetic; ≥286 injection-like strings treated as data (DF-08) | MET | High | Controls needed if any AI consumer | Stage 24/26 |
| Q-15 | 5 Urgency vs readiness | Deadline / urgency evidenced | C: finance & risk requests "remain active" | E: no dates, no SOW | UNKNOWN | High | Cannot prioritise | OQ-07 |
| Q-16 | 5 | Readiness to measure baseline | — | E: definitions conflict ("closed", "resolved"); no telemetry (SO-12..17) | NOT MET | High | Urgency > readiness for Stage 4 | OQ-05 |
| Q-17 | 6 Premature/non-viable | AI need evidenced | C: repo framed for "AI intervention" | E: zero AI today; 0C: tokens <1 % of cost; Stage 8 undecided | PARTIAL | Medium | AI commitment would be premature | Stage 8 |
| Q-18 | 6 | Economics envelope exists | — | E: 0C S0–S4 scenarios, all inputs Assumed; benefits unmodelled | PARTIAL | Medium | Not a business case | C-1..C-5 (0C) |
| Q-19 | 7 Dependencies | Stakeholder access for definitions | — | E: none | PARTIAL | High | Stages 2–6 constrained | OQ-01, OQ-05 |
| Q-20 | 7 | Policy conflict resolvable in engagement | C: 2024 ops/compliance/finance conflict | E: document only; "never formalized" | PARTIAL | Medium | Must be escalated as decision, not solved by tooling | OQ-06 |
| Q-21 | 7 | Constraints compatible with scope | — | E: DESIGN/read-only through Stage 14; BUILD on branch from Stage 15 (per OD-01) | MET | High | — | HAR for config/CI |

**Totals:** MET = Q-03, Q-08, Q-09, Q-14, Q-21 (5); PARTIAL = Q-01, Q-07, Q-10, Q-11, Q-12, Q-17, Q-18, Q-19, Q-20 (9); NOT MET = Q-02, Q-04, Q-13, Q-16 (4); UNKNOWN = Q-05, Q-06, Q-15 (3). Total 21.

## Evidence References

Finding IDs per Stage 0A artifacts (DF-, WF-, IO-, SO-, TO-); GD-/STOP-/HAR- per 0B; C-1..C-5 per 0C.

## Assumptions

- Status/confidence ratings are the agent's judgement; the engagement lead validates.

## Unknowns

- Q-05, Q-06, Q-15 outcomes.

## Unresolved Issues

- NOT MET items Q-02, Q-04, Q-13, Q-16 carry into conditions (see Go/No-Go).

## Residual Risks

- Rating a synthetic-only engagement as "viable" may be read as a business endorsement (ER-01).

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial checklist. |
