---
stage: "14 — Transformation / Migration Plan"
artifact: "transformation-risks.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/14-transformation/*.md (this stage)", "docs/07-repo-assessment/repo-transformation-readiness.md (heat map, R-07-14)", "docs/07-repo-assessment/baseline-test-results.md (TQ-01, TQ-05)", "docs/10-architecture/architecture-risk-register.md", "docs/12-specs/spec-readiness.md (RF-1..RF-4, RD-3)", "docs/13-traceability/coverage-gap-register.md, traceability-summary.md (C1..C5)", ".fde/orchestrator-decisions.md (OD-07, OD-10)", "device facts: Python 3.10.12, SQLite 3.37.2, java+node present, no python3.11/3.12"]
supersedes: "none"
---
## Summary
**Label: synthetic repository; DRAFT plan, not an approval.**
18 transformation risks across the six required analysis dimensions. The dominant risk class is **decision latency** (19 open OD-S12 items, 9 DVs), which the plan converts from a blocker into per-increment entry criteria with safe defaults. The highest technical risks are a wrong re-delivery identity key (TR-07), unobservable change if the harness is skipped or weakened (TR-01), and environment parity (no Python 3.12 on the device; TR-05). **No blocking condition remains for Stage 14**; Stage 15 INC-01 can start once the five INC-01 entry items (E-1..E-4, E-6) are confirmed.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### TR-1 Analysis dimensions (required by the stage prompt)
| Dimension | Conclusion | Where | Confidence |
|---|---|---|---|
| 1 Dependency order | harness → C11 → C2 → C4 → C3/C7 → C6 → C8/C9 → C1/C10/C5; follows component-model dependencies | dependency-sequence DS-1/DS-2 | High |
| 2 Increment size & reversibility | 9 increments, ≤ 2 components each, all revertible by code revert (+ hub rebuild) | transformation-gates TG-3, rollback RB-1 | High |
| 3 Coexistence risk | low by construction (RO adapters, no dual-write, loopback, legacy unchanged); residual lock-contention and two-truths confusion | coexistence CS-4 | Medium |
| 4 Data migration risk | zero legacy migration; hub backfill copy-only and rebuildable until cutover; identity-key risk high | schema-migration SM-3 | High |
| 5 Rollback feasibility | High for INC-01..09; Medium for CUT steps (consumers Unknown) | rollback RB-1 | High / Medium |
| 6 Verification per increment | common gate CG-1..11 + per-increment planned tests (241 assigned) + Stage 16 D0–D5 protocol | transformation-gates TG-2..TG-4 | High (plan) / none executed |

### TR-2 Risk register (owner for all: Engagement lead (Dinesh Naik))
| ID | Risk | Evidence | Dimension | Likelihood | Impact | Mitigation | Resolving stage | Tag |
|---|---|---|---|---|---|---|---|---|
| TR-01 | Harness skipped/weakened → change unobservable (shipped suite kills 1/15 mutants) | TQ-05, TD-02 | 6 | Medium | High | INC-01 first; mutation gate CG-3; goldens only via reviewed PR | 15 | [Verified Fact] evidence |
| TR-02 | Test run corrupts repo `data/` (import-time DB binding, repo-relative writers) | TQ-01, WB-F1/F2 | 3 | Medium | High | CG-1 sandbox guard, CG-5 manifest check, OD-03a | 15+ | [Verified Fact] |
| TR-03 | Decisions arrive late or flip after build → rework | RD-3 (19 open), GF-2 (35 class-B) | 2 | High | Medium | safe defaults behind flags; both modes tested; just-in-time decision list TG-1(b) | 15/17 | [Inference] |
| TR-04 | Building on PROPOSED ADRs / DRAFT PRD (OD-S12-14) | DS-2 in ADR summary | 2 | Medium | Medium | E-5 explicit at-risk acceptance; harness-first is spec-independent | 17 | [Verified Fact] status |
| TR-05 | Runtime parity: ADR-018 3.12 vs device 3.10.12 only; CT-H5 cannot run 3.12 locally | RF-3; device check | 6 | High | Low-Medium | floor 3.10/3.37 (BEH-CO-09); 3.12 run deferred, needs HAR-08 to install | 15/OD-S12-12 | [Verified Fact] |
| TR-06 | Golden drift: re-captured goldens silently "fix the test" | CT-H4 | 6 | Medium | High | versioned goldens, `--update-golden` PR only, D1 list reviewed | 15/16 | [Inference] |
| TR-07 | Wrong re-delivery identity key | RF-1, OD-10a | 4 | Medium | High | natural key default; explicit OD-S12-17 decision before INC-06 | 15 INC-06 | [Verified Fact] |
| TR-08 | DDL/config-schema gaps (deviation_register, coexistence_inventory, users/roles, migrations table; 7 flag keys) | DR-3, FL-1 | 4 | High | Low | addenda as new files on branch (A-14-08) | 15/17 | [Verified Fact] |
| TR-09 | SQLite lock contention hub-read vs legacy-write | CX-1, CT-17 not captured | 3 | Low | Medium | snapshot reads (immutable) | 15 INC-02 | [Inference] |
| TR-10 | Two truths visible during shadow | CX-3 | 3 | Medium | Medium | SHADOW banner; authority flag | 15 INC-08 | [Inference] |
| TR-11 | Consumers of legacy outputs unknown → cutover step 4 unplannable | CF-1 | 5 | High | Medium | CUT steps hold until consumer named | 30 | [Verified Fact] absence |
| TR-12 | Zone H accidentally usable (HAR-12) | ADR-006 | 3 | Low | Critical | mode `none`, holders `[]`, G8 negative tests, STOP-07 | 15 INC-08 | [Inference] |
| TR-13 | Product AI creeps in (OD-08) | OD-08 | 3 | Low | High | deny-list + egress (G5), Stage 32 tripwire | 15 INC-02 | [Verified Fact] OD-08 |
| TR-14 | Planted prompt-injection strings in docs/data processed as instructions by tooling | Stage 0B STOP-05, G9 | 3 | Medium | Medium | treat as data; planted-string suite G9 | 15 INC-08 | [Verified Fact] |
| TR-15 | Single reviewer bottleneck | OD-04 (Dinesh only human) | 2 | High | Medium | small PRs; machine-checkable gates | 15 | [Verified Fact] |
| TR-16 | Long shadow period without value | MRF-2 | — | Medium | Medium | CUT-1 first value step | 30 | [Inference] |
| TR-17 | Tooling unavailable offline (coverage/lint/SAST) | R-9 | 6 | High | Low | stdlib-only gates; mutation kill rate > coverage % (CT-H7) | 15 (HAR-08 if installing) | [Verified Fact] |
| TR-18 | Stage 9 count error (41/11) propagates into planning | OD-10b | 2 | Low | Low | plan uses 43/9 from rtm.csv | 17 | [Verified Fact] |

### TR-3 Blocking-condition check for Stage 14
| Condition | Blocking? | Why |
|---|---|---|
| Open OD-S12 decisions | No | each mapped to the increment/CUT it blocks with a safe default (TG-1b) |
| DV-01..09 undecided | No | only CUT-2..CUT-4 need them (Stage 30) |
| PRD approval (OPD-13) | No for INC-01..08 (at-risk acceptance E-5); Yes for INC-09 and CUT-1 | TG-1b |
| Scheduler vs HAR-10 (OD-S12-10) | No | schedule disabled by default |
| Disposition location (OPD-05) | No | mode `none` |
| Python runtime | No | floor 3.10; E-4 for INC-01 |
| Stage 7 NO-GO (C-1..C-6 / R-1, R-2, R-4, R-5) | No for the plan; INC-01 is precisely the action that clears R-1/R-2; R-4 cleared by OD-09; R-5 (rule authority) needed only at CUT-2 because no rule changes before | readiness file |

### TR-4 Stage 14 Completion Gate evaluation
| Gate condition | Result | Evidence |
|---|---|---|
| Every increment has rollback and verification | **Met (planned)** — INC-01..09 and CUT-1..5 each have a rollback (RB-1) and verification (TG-3, CO-1) | rollback-strategy.md, transformation-gates.md |
| Components to remain unchanged are listed | **Met** | coexistence-strategy.md CS-2 |
| Gates per increment defined | **Met** | transformation-gates.md TG-2/TG-3 |
| All required artifacts exist at the paths | **Met** — 11 of 11 in `docs/14-transformation/` (+ `evidence/`) | final listing |
| Critical gaps resolved or explicitly documented | **Met (documented)** — none resolved by this stage; all owned | TR-2, TG-1 |
| Evidence supports the conclusion | **Met for a plan**; nothing executed; no rollback rehearsed; all approvals OPEN | this file |
**Stage 14 status: CONDITIONAL PASS** — no blocking gap; non-blocking conditions: entry items E-1..E-6 OPEN; TG-1(b) decisions OPEN; DDL/config addenda (TR-08); 3.12 parity (TR-05); consumers Unknown (TR-11). Due: E-1..E-4/E-6 before Stage 15 INC-01; others per TG-1(b).

## Evidence References
Sibling artifacts; readiness heat map; TQ-01/05; RD-3; RF-1..RF-4; OD-07/10.

## Assumptions
- A-14-13 [Assumption] Likelihood/impact ratings are qualitative judgement (no incident data exists, OD-04).

## Unknowns
- U-14-01..U-14-10 (see sibling artifacts).

## Unresolved Issues
- All TG-1 items OPEN.

## Residual Risks
- RR-TR-1 The plan has not been exercised; first real evidence is INC-01's equivalence report.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial risk register and gate evaluation (Stage 14). |
