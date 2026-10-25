---
stage: "42 — Executive Defence & Final Value Story"
artifact: "production-outcomes.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/34-measure-after/", "docs/35-variance/", "docs/30-release/release-outcome.md", "docs/31-observability/", "docs/37-operating-model/"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** **There are no production outcomes.** The hub has not been released, cut over, tagged, exposed or used (C-19, C-21). What exists are sandbox measurements on the 125-case synthetic baseline (seed 4100, sha256 c254649f...d70aa), earlier-stage test results, and an explicit list of what cannot be measured. This document exists so no one reads sandbox parity as production performance.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### PO-1 Production facts
| Fact | Value | Class | Evidence |
|---|---|---|---|
| Release executed | **No** (NOT RELEASED) | [Verified Fact] | `docs/30-release/release-outcome.md` |
| Cutover steps CUT-1..CUT-5 performed | 0 | [Verified Fact] | OD-37 |
| Approvals recorded | 0 of 40 | [Verified Fact] | `docs/30-release/evidence/approvals-register.json` |
| Hub store in `data/` | none exists in the working tree | [Verified Fact] | `kpi-comparability-check.md` CC-3 |
| Adoption K-21 | 0 of 125 cases | [Verified Fact] | `adoption-metrics.md` AD-1 |
| Human principals / sessions / dispositions | 0 / 0 / 0 | [Verified Fact] | `after-intervention-kpi-sheet.md` K-01 |
| Production telemetry, incidents, overrides | none exist; override leakage is Unknown, not zero | [Verified Fact] | `human-override-metrics.md`; VL-3 |
| SLA | none; five SLO candidates | [Verified Fact] | `slo-sla-definitions.md` |
| Zone H holders | empty | [Verified Fact] | OD-31 |
| Owners accepted for production assets | 0 of 28 | [Verified Fact] | `docs/37-operating-model/` |

### PO-2 Sandbox measurements (not production), by comparability class
| Class | Meaning | KPIs | Honest reading |
|---|---|---|---|
| C1 like-for-like | same definition, population, reference time | K-09-OPS count 89 of 125 and per-site 22/18/14/10/11/14; K-15 6.4 % (8 of 125); K-11 2 of 2 as "accepted open" records | Parity of an imported snapshot; K-11 records that nobody decided. **Not improvement.** |
| C2 unchanged by construction | legacy path re-measured, byte-identical output (sha256 31ffa1b2...12d61ba) | 16 KPI ids | Because the hub is additive; says nothing about regression or benefit |
| C3 hub-only, no before | | K-01, K-07 replay-safe `ok: true`, K-03 4 of 4 tagged | Mechanism evidence; before was Unknown |
| C4 not comparable | different definition/population/reference time | K-02, K-06, K-08 (hub), K-09U, K-10, age buckets | Do not compare. The hub's `as_of` is wall-clock 310 days after the frozen AS_OF |
| C5 Unknown both sides | | K-04 (all variants), K-05, K-09-EVID, K-09-FIN, K-22, K-04-FIN | No closure/evidence/effort timestamps exist anywhere |

### PO-3 Numbers that look like outcomes and are not
| Number | Where | Why it is not an outcome |
|---|---|---|
| 100 % unresolved exception rate (8,335 of 8,335) | hub path K-09U | Means no reviewer has acted (0 principals); not a performance level |
| 8,109 exceptions / 7,903 UNMATCHED_REF on shadow intake | hub intake | The synthetic feed rows reference cases that do not exist (test residue); it is a property of the data |
| 0.603 h per case | K-12 | Generator estimate, not a time record |
| USD 23.40 per case | K-13 | Artefact of near-constant infra cost and volume |
| 5-row gap between legacy matched rows (173) and hub links (168) | K-06 | Not investigated [Unknown] |
| Replay "safe" | K-07 | Outcome-level in one sandbox run; raw store grows |

### PO-4 What the exposure to production would require (cross-reference)
The 12 hard G1 conditions in `docs/40-scale/90-day-roadmap.md` (walkthroughs signed, 3.12+ regression, holders or declared unused, owner and responder, data decisions, exposure posture, off-device backup and restore drill, F-29-01 follow-up, wiring or "not used", after-window definition, Stage 30 decision, non-carry checklist). [Verified Fact] none is shown as fully met at b1de232 in the records I read. One is partly advanced since the roadmap was written: F-29-01 was fixed in Stage 30 (exit 17, S30-DEV-01, acceptance by Dinesh pending) but the other F-xx dispositions are open (G1-8). The roadmap's own statement that all 17 pre-conditions were unmet dates from main ef72e4e, before Stage 30.

## Evidence References
C-19, C-21, C-22, C-23, C-27; `docs/34-measure-after/` (all), `docs/35-variance/before-after-analysis.md`.

## Assumptions
A-34-* carried; the sandbox store is a fair stand-in for a first post-intervention state (it is a fixture, no operating period).

## Unknowns
Everything operational: latency, availability, error rate in use, reviewer behaviour, override rate, incident rate, cost.

## Unresolved Issues
After-window definition (D-34-02), as_of parameter for the hub (D-34-03), baseline freeze (D-34-04), Stage 34/35/36 v0.2 re-run.

## Residual Risks
Parity read as improvement; synthetic magnitudes read as client performance (FAIL-05).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
