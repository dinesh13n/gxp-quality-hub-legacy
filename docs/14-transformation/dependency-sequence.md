---
stage: "14 — Transformation / Migration Plan"
artifact: "dependency-sequence.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/10-architecture/component-model.md (C1..C11 'depends on' column)", "docs/07-repo-assessment/repo-transformation-readiness.md (heat map, recommended sequence)", "docs/07-repo-assessment/dependency-map.md", "docs/12-specs/spec-readiness.md RD-3/RD-4", "docs/14-transformation/evidence/increment-test-map-summary.txt", "docs/14-transformation/transformation-backlog.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository; DRAFT plan, not an approval.**
Ordering principle: **observe before you change; build beside before you switch.** INC-01 (harness, no behaviour change) is the root of the graph; every later increment depends on it because it is the only way to prove "legacy unchanged". New modules then follow the component dependency order of `component-model.md`: C11 safety rails → C2 store/audit → C4 rules → C3/C7 decisions/crosswalk → C6 intake → C8/C9 runs/metrics → C1/C10/C5 surfaces. Decision-dependent behaviour is built with the spec's safe default and both modes tested, so open decisions block **use / cutover**, not **build** (RD-4).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### DS-1 Component dependencies (source) [Verified Fact]
From `component-model.md` L21-31: C1→Services; C2→repositories; C3→C2,C4; C4→C2; C5→C2,C3,C4,C7; C6→C4,C7; C7→C3; C8→C6,C9; C9→C3,C4,C8; C10→C4,C6; C11→none.
Note: C8↔C9 is a declared mutual dependency (C8 runs C9 jobs; C9 reads run records) [Verified Fact] → built in the same increment (INC-07) [Inference]. C7→C3 and C3 has no dependency on C7 → C3 and C7 share INC-05 with C3 first.

### DS-2 Increment order
```
INC-01 harness+fixtures (legacy untouched)
   └─ INC-02 hub skeleton, guards, RO adapters, golden-compare  [C11]
        └─ INC-03 store migrations + access & audit + backup/restore  [C2]
             └─ INC-04 policy & rule service (as-found sets)  [C4]
                  └─ INC-05 decision record + crosswalk + legacy backfill  [C3, C7]
                       └─ INC-06 intake in shadow  [C6]
                            └─ INC-07 runs + metrics (schedule off)  [C8, C9]
                                 └─ INC-08 HTTP/pages + reviewer queue + disposition gate (mode none)  [C1, C10, C5]
                                      ═══ R1 build complete → Stage 16 validation → … → Stage 30 cutover CUT-1..CUT-5
                                      └─ INC-09 R2 FTS search + templates  [C10]  (after R1; separate approval)
```

| Inc | Depends on | Why this position | Risk if reordered | Tag |
|---|---|---|---|---|
| INC-01 | none | Only increment that touches nothing but a new test tree; makes every later diff visible (Stage 7 "No-go until R-1/R-2") | Any earlier change is unobservable (14/15 mutants survive shipped suite) | [Verified Fact] for the risk |
| INC-02 | INC-01 | Guards (sandbox, No-AI, runtime, `mode=ro`) must exist before any module that touches data | A module could write under legacy paths (WB-F1) | [Inference] |
| INC-03 | INC-02 | Every write in C3..C9 emits an audit event (ADR-005); migrations need backup-before-migrate | Audit retrofitted later = un-auditable history | [Inference] |
| INC-04 | INC-03 | C3, C5, C6, C9, C10 all evaluate rules; CT-01..03 parity (TST-CO-03) proves rules before use | Decisions recorded with unproven rules | [Inference] |
| INC-05 | INC-04 | C3 needs C2+C4; C7 needs C3 | — | [Verified Fact] DS-1 |
| INC-06 | INC-05 | C6 needs C4 + C7 | Intake without crosswalk = orphan explosion | [Verified Fact] DS-1 |
| INC-07 | INC-06 | C8 needs C6, C9; C9 needs C3, C4 | — | [Verified Fact] DS-1 |
| INC-08 | INC-07 | C5 needs C2,C3,C4,C7; C10 needs C4,C6; HTTP last so the surface exposes only tested services; loopback only (HAR-05) | Early API invites premature use / exposure | [Inference] |
| INC-09 | R1 release | R2 scope (9 FR, `rtm.csv` release=R2); FTS5 on target Unknown (OD-S12-12) | Scope creep into R1 | [Verified Fact] R1/R2 split |

### DS-3 Parallelism
[Inference] INC-04 and the C7 half of INC-05 could be developed in parallel branches, but **branch-per-increment, merge-in-order** is recommended because one engineer (Dinesh Naik is the only human) reviews every PR and goldens must be re-run on a single linear history. No two increments merge concurrently.

### DS-4 Decision dependencies per increment (from RD-3 "blocks" column)
| Inc | Decisions that must be *answered or accepted-open with default* before the increment starts | Decisions that only block *use/cutover* later |
|---|---|---|
| INC-01 | E-1 harness approach (HD-1), E-2 write-boundary confirmation (A-14-01/A-14-03); OD-09 already decided | none |
| INC-02 | OD-S12-12 runtime (default floor 3.10/3.37); "build on PROPOSED ADRs / DRAFT specs at risk" (E-5) | OD-S12-13 (approving any DV) |
| INC-03 | OD-S12-09 retention (default hold-all), OD-S12-18 anchor (default config path) | OD-S12-06 holders |
| INC-04 | OD-S12-04 (default: no active set; as-found sets read-only) | adoption of any rule set (ZH-05/06) |
| INC-05 | OD-S12-03, -07, -15, -16, -19 (defaults in RD-3) | KPI/closure verdicts (OD-S12-01) |
| INC-06 | OD-S12-17 natural key, OD-S12-11 (default record_only) | enforcing contract on a feed |
| INC-07 | OD-S12-10 (default schedule disabled), OD-S12-01/-02/-08 accepted-open (no verdicts) | enabling schedule; KPI targets |
| INC-08 | OD-S12-05/-06 accepted-open (mode none, holders []) | any Zone H pilot use |
| INC-09 | OD-S12-14 (R1/R2 approval), OD-S12-12 FTS5 | — |

## Evidence References
`docs/10-architecture/component-model.md` L21-31; `docs/12-specs/spec-readiness.md` L37-69; `docs/13-traceability/evidence/rtm.csv` (release); `docs/14-transformation/evidence/increment-test-map-summary.txt`.

## Assumptions
- A-14-04 [Assumption] One reviewer (Dinesh Naik) → sequential merges. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-14-03 Whether Stage 17 (PRD approval) re-scopes R1 enough to reorder INC-05..INC-08.

## Unresolved Issues
- OD-S12 decisions per DS-4 are open; recorded as entry criteria in `transformation-gates.md`.

## Residual Risks
- RR-DS-1 A late decision (e.g. OD-S12-17) forces rework of a merged increment; mitigated by forward-only migrations and by keeping all decision-dependent behaviour behind config (feature-flag-plan.md).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial sequence (Stage 14). |
