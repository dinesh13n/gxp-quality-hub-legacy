---
stage: "34 — Measure After-Intervention KPIs"
artifact: "kpi-comparability-check.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 34 run)"
status: "DRAFT"
evidence_sources: ["docs/04-baseline-kpis/measurement-methodology.md", "docs/04-baseline-kpis/kpi-baseline-signoff.md", "docs/04-baseline-kpis/baseline-kpi-sheet.md", "docs/34-measure-after/evidence/after_measure_baseline.json", "docs/34-measure-after/evidence/hub-06-values.json", "docs/34-measure-after/evidence/hub-15-values-after-intake.json", "docs/12-specs/features/f07-metrics-definition-tags.md", ".fde/orchestrator-decisions.md (OD-02, OD-07, OD-09, OD-22)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Every number below is either (a) a SANDBOX measurement on a copy under `~/fde_sbx` of the 125-case synthetic baseline (seed 4100, sha256 `c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa`), or (b) a result already recorded by an earlier stage's tests, or (c) Unknown. NOTHING here is production performance: the hub is not in production, no production telemetry exists, Stage 30 has not been run and Stage 31 is not merged (in progress on branch stage-31-observability by another agent). Documentation only. No KPI definition is changed, no benefit is claimed, no risk is accepted (OD-04, OD-32).**

## Summary
Completed before any after-claim (Execution Method step 2). **Verdict: comparability is CONFIRMED only for the legacy path (same DB, same script, same reference time) and for three hub-path items (K-09-OPS count and site split, K-15, K-11). It is NOT confirmed for any production measurement because none exists.** Window and population are identical on the legacy path *because nothing in the legacy path changed*, which makes "unchanged" a property of the construction, not a finding about the intervention.

## Findings
### CC-1 Frozen yardstick check [Verified Fact]
| Item | Stage 4 frozen value | Stage 34 observed | Match |
|---|---|---|---|
| KPI dictionary (K-01..K-22, D-OPS/D-EVID/D-FIN split) | `kpi-dictionary.md` v0.1, sha256 `516e2dd83e05…55b0e4` | file untouched on branch `stage-34-measure-after` (only `docs/34-measure-after/` added) | YES |
| Baseline DB | `data/legacy.sqlite3` sha256 `c254649f57e2…d70aa`, 125 cases (OD-02, confirmed OD-09) | sandbox copy and working-tree file both `c254649f…d70aa` | YES |
| Measurement script | `measure_baseline.py` sha256 `cb062e1bae21…53f60a6` | same | YES |
| Reference time | AS_OF 2025-12-19T07:11Z (A-04-03) | legacy script uses the same (max timestamp in data) | YES |
| Output | `measure_baseline.output.json` sha256 `31ffa1b2b136…12d61ba` | re-run output sha256 `31ffa1b2…12d61ba`, `cmp` identical | YES |
| Python / SQLite | 3.10.12 | 3.10.12 / 3.37.2 | YES |

### CC-2 Window comparability
| Dimension | Before | After (legacy path) | After (hub path) | Verdict |
|---|---|---|---|---|
| Case window | created 2023-01-25 .. 2025-12-19 | same data | same 125 cases (backfill: 125 imported, 250 events, 0 projection mismatches) | Comparable |
| Reference time | AS_OF 2025-12-19T07:11Z, fixed | same | **wall clock of the run** (`as_of` 2026-10-25T05:1x Z), 310 days later | **Not comparable for any age-dependent figure.** Status counts do not depend on as_of, ages do. Hub CLI offers no as_of parameter [Verified Fact: `hub/metrics/cli.py` snapshot options] |
| Feed / exception window | 2021-01 .. 2024-12 | same | same rows via shadow intake | Comparable as population; classification differs (CC-4) |
| Post-intervention exposure | none | none | none: sandbox fixture, no operating period, no users | There is no "after window". A real one needs a start date, an exposure definition and a minimum duration, all Unknown |

### CC-3 Population comparability
- [Verified Fact] Legacy path population: 125 cases / 8,567 feed rows / 224 policy exceptions / 60 batch runs / 72 outages, identical to Stage 4.
- [Verified Fact] Hub path: cases identical (125) via backfill; feed rows identical (8,567) but the hub keeps 8,583 raw rows after ingest (the 8,567 plus 15 source messages plus 1 gateway row) and grows to 17,150 after the replay check; exception population is the hub's queue (8,335 exception/quarantine/flag items), not `policy_exceptions` (224).
- [Inference] The hub exposes no per-case "handled via new path" flag for production; adoption (K-21) has no numerator.
- [Verified Fact] No hub store exists in the working tree (`data/` has no `hub.sqlite3`): there is no persistent post-intervention population.

### CC-4 Definition comparability per KPI (hub vs Stage 4)
| KPI | Same definition? | Reason |
|---|---|---|
| K-09-OPS count | YES | hub closing-state set {CLOSED} = `status <> 'CLOSED'` of K-09-OPS (`closing_states: ["CLOSED"]`, `closure_basis: label`) |
| K-09-OPS age | NO | hub emits buckets only, at wall-clock as_of; no median/p90 |
| K-09U | NO | hub: open exception-queue items / all queue items (A-12-F07-2); Stage 4: `policy_exceptions.outcome` shares (UE-1, UE-2) |
| K-06 | NO | hub outcome classes (UNMATCHED_REF, NO_BUSINESS_KEY, QUARANTINED, NOOP_DUPLICATE) are not `ref_id NOT IN cases.id`; 173 matched (Stage 4) vs 168 linked (hub) |
| K-07 | partly | Stage 4 definition (queue and totals before/after replay) is what `verify-replay` checks; but the Stage 4 value is Unknown, and the hub system differs from the legacy system |
| K-03 | NO (population) | different set of reported figures |
| K-02 | NO | no STATUS_REVIEWED events in the hub path |
| K-15 | YES | `status = 'REOPENED'` count over 125 |
| K-11 | YES | count of DR-20/DR-21 with a decision or accepted-open record; but meaning differs from a decision |
| K-10, K-12, K-13 | n/a | hub refuses `operating_costs` as "cases created"; no hub value |

### CC-5 Inherited comparability caveats from Stage 5 / OD-07 [Verified Fact]
- A-04-01 ("operating_costs.total_cases = cases created in month") was **refuted** (OD-07): K-10 compares unrelated populations, and K-12/K-13 divide by the ops-table total (108), not by cases (125). These caveats apply to before and after alike; they were not corrected in Stage 4 (frozen). K-06, K-08, K-09U are generator-bounded proxies (OD-07).
- **Proposed Stage 4 v0.2 addendum (NOT applied; needs a change record per kpi-baseline-signoff.md and Dinesh's decision):** (a) mark K-10 as "population mismatch confirmed (OD-07), not a reconciliation measure"; (b) restate the reference-time rule so a hub-path comparison must pass `as_of = 2025-12-19T07:11Z` or the figure is labelled not comparable; (c) add the hub equivalent of K-09U and K-06 as *separate* KPI ids rather than reusing the names. Stage 34 did not apply any of this and has not redefined a KPI.

### CC-6 Claim gate [Verified Fact]
No claim of improvement is made for any KPI. Claims allowed by this check: (1) legacy-path values are unchanged; (2) hub backlog count and per-site split equal the legacy values; (3) hub replay check shows zero queue/total drift in the sandbox; (4) a K-11 record exists. Claims NOT allowed: any time, cost, quality, adoption or benefit claim.

## Evidence References
`evidence/after_measure_baseline.json`; `evidence/hub-03/04-snapshot*.json`; `evidence/hub-06-values.json`; `evidence/hub-12-verify-replay.json`; `evidence/hub-10-ingest-legacy.json`; `docs/04-baseline-kpis/measurement-methodology.md` (rule: record window, denominator, exclusions and assumptions before comparing); `hub/metrics/cli.py`.

## Assumptions
- A-34-05 [Assumption] "Comparable" requires same definition, same population and same reference time; this is the Stage 4 rule restated, not a new definition. Confirm: Engagement lead (Dinesh Naik).
- A-34-06 [Assumption] The hub closing-state set equals D-OPS only because the shipped candidate policy `D-OPS@1` says so; it is a candidate, not adopted (OPD-01 accepted open).

## Unknowns
- U-34-04 Minimum production observation window and exposure definition for a real after-measurement. Owner: Engagement lead (Dinesh Naik).
- U-34-05 Whether Dinesh wants hub metrics to accept an `as_of` parameter so they can be compared at the frozen reference time (a code change, out of scope for this docs-only stage).

## Unresolved Issues
- OD-07 Stage 4 v0.2 addendum still unraised; Stage 4 freeze unsigned.
- Hub wall-clock `as_of` prevents like-for-like ageing (routed as D-34-03).

## Residual Risks
- RR-34-04 Because legacy values are identical by construction, a later stage could mistake the check for a "no regression" finding. It only shows the legacy data and script were not altered.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 34). |
