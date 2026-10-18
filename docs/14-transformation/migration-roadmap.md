---
stage: "14 — Transformation / Migration Plan"
artifact: "migration-roadmap.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/14-transformation/*.md (this stage)", "docs/14-transformation/evidence/increment-test-map-summary.txt", "docs/07-repo-assessment/repo-transformation-readiness.md (go/no-go, R-1..R-12)", "docs/10-architecture/architecture-decision-summary.md", "docs/12-specs/spec-readiness.md", "docs/13-traceability/traceability-summary.md", ".fde/orchestrator-decisions.md (OD-01, OD-05, OD-08, OD-09, OD-10)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository; DRAFT plan, not an approval. No calendar dates exist; phases are stage-relative.**
Four phases: **P0 Make change observable** (INC-01) → **P1 Build beside, in shadow** (INC-02..INC-08 = R1) → **P2 Validate** (Stage 16 comparison, later security/TEVV stages) → **P3 Per-capability cutover** (CUT-1..CUT-5, Stage 30). R2 (INC-09) follows R1 only after PRD approval. Legacy code and data are untouched through P0–P2; the first consumer-visible change is a CUT step, each individually approved and reversible. This addresses the Stage 7 verdict "NO-GO for refactoring until an executable harness, hermetic fixtures and rule-conflict authority exist": the harness and fixtures come first, and the rule-conflict authority (OD-S12-04/-13) is only needed at cutover because no legacy rule is changed before then.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### MR-1 Roadmap
| Phase | Stage | Increment / step | Outcome | Legacy behaviour change | Gate |
|---|---|---|---|---|---|
| P0 | 15 | INC-01 harness + hermetic fixtures | Stage 7 goldens executable; mutation gate | none | TG-3 INC-01 |
| P1 | 15 | INC-02 hub skeleton + guards + RO adapters + golden-compare | safety rails | none | TG-3 |
| P1 | 15 | INC-03 store migrations + access & audit + backup/restore | tamper-evident foundation | none | TG-3 |
| P1 | 15 | INC-04 policy & rule service (as-found sets) | rule parity proven | none | TG-3 |
| P1 | 15 | INC-05 decision record + crosswalk + 125-case backfill | decision record in shadow | none | TG-3 |
| P1 | 15 | INC-06 intake in shadow | non-destructive intake | none | TG-3 |
| P1 | 15 | INC-07 runs + metrics (schedule off) | definition-tagged figures | none | TG-3 |
| P1 | 15 | INC-08 HTTP/pages + reviewer queue + disposition gate (`none`) | R1 build complete (shadow) | none | TG-3 (G1..G10) |
| P2 | 16 (+23–27 per their prompts) | behaviour comparison vs Stage 7 baseline | diff register, D5 = 0 | none | TG-4 |
| P3 | 30 | CUT-2 rules → CUT-1 decision record → CUT-3 intake → CUT-4 metrics → CUT-5 automation/exposure | hub authoritative per capability | **yes, approved per DV** | cutover-plan CO-1 |
| R2 | after R1 | INC-09 FTS search + templates | R2 scope (9 FR) | none | TG-3 |

### MR-2 Branch and PR strategy (recommended; E-6 in the entry checklist)
- One branch per increment, `stage-15-incNN-<slug>`, cut from the latest `main`; matches OD-01's `stage-NN-*` BUILD pattern. [Inference]
- One PR per increment on GitHub `dinesh13n/gxp-quality-hub-legacy` (remote `origin` present [Verified Fact]); PR body = increment gate checklist (CG-1..CG-11 + increment rows) with evidence paths, the rollback note and the diff register summary. [Inference]
- Squash-merge **in order** by the orchestrator after review (HAR-04); never force-push `main` (WB-08). A tag `stage-15-incNN` after each merge gives a rollback anchor. [Inference]
- If the orchestrator prefers a single `stage-15-*` branch: one commit per increment with the same gate checklist per commit; rollback = revert that commit. [Inference]
- Stage agents do not run git write commands; they write files and evidence; the orchestrator commits (task contract). [Verified Fact] task instructions.

### MR-3 Increment-size principle
Each increment adds one component group (≤ 2 components), one schema version, and ≤ ~65 planned tests; INC-08 is the largest (64 tests) because it holds all API-level tests; Stage 15 may split it into INC-08a (C1 + API tests for existing services) and INC-08b (C10 + C5) without changing the plan's logic. [Inference]

### MR-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| MRF-1 | The plan contains no step that changes legacy behaviour before Stage 30 | CS-2, TG-2 CG-4 | Stage 7 NO-GO conditions are respected | Low | High | — |
| MRF-2 | Value delivery is late (shadow until CUT) | cutover-plan | stakeholder patience (only Dinesh) | Medium | Medium | Dinesh may pull CUT-1 earlier after Stage 16/26 |
| MRF-3 | Stage 9 brief count 41/11 is wrong; plan uses 43 R1 / 9 R2 (OD-10b) | rtm.csv | INC-09 holds R2 tests only | Low | High | Stage 17 correction (C4) |

## Evidence References
All sibling artifacts; `evidence/increment-test-map-summary.txt`; readiness verdict; OD log.

## Assumptions
- A-14-04, A-14-10 (sequential single-reviewer merges; squash-merge acceptable).

## Unknowns
- U-14-01 consumers; U-14-02 runtime; U-14-03 Stage 17 re-scoping.

## Unresolved Issues
- Entry checklist items OPEN (transformation-gates.md TG-1).

## Residual Risks
- RR-MR-1 Long shadow period invites "just switch it" pressure (cf. R-07-14); mitigated by explicit CUT gates.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial roadmap (Stage 14). |
