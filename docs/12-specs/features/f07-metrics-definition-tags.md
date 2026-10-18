---
stage: "12 — Spec-Driven Design"
artifact: "features/f07-metrics-definition-tags.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["sql/legacy_reports.sql", "legacy_java/ReconcileLegacy.java", "app/baseline.py", "data/legacy.sqlite3 (read-only, immutable; cases.amount, 125 rows)", "docs/04-baseline-kpis/baseline-kpi-sheet.md (K-09-OPS)", "docs/07-repo-assessment/baseline-behaviour.md (BB-08)", "docs/10-architecture/adrs/ADR-011-metrics-and-definition-tags.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Feature spec for metrics with declared definitions (CAP-07): tag-mandatory registry, tag-mixing refusal, per-clock median/p90 with stated method, fan-out-free exact-decimal totals with verified reference value 622,826.44, 11 behaviours, 21 acceptance criteria for FR-MET-01..08.

## Findings
### F07-1 Scope and traceability [Verified Fact: requirement text and reference values; Inference: design]
Feature **F07 Metrics & Reporting with Declared Definitions** = CAP-07, component C9, ADR-011 (one query path, definition tags, exact decimals), data contract DC-16, quality rule DQ-21.

| Implements | FR-MET-01, FR-MET-02, FR-MET-03, FR-MET-04, FR-MET-06 (R1 Must); FR-MET-05 (R1 Should); FR-MET-07 (R2); FR-MET-08 (R2 Could) |
|---|---|
| Also constrained by | FR-POL-02, FR-DEC-06, FR-RUN-02, PNFR-16, PNFR-17, PNFR-20; BR-01, BR-03, BR-10, BR-12; RC-3, RC-8; FAIL-02, FAIL-03, FAIL-05; OD-07 |
| Open decisions | OD-S12-01/02 (definitions and clock), OD-S12-08 (cut-off, denominator, cost source) |
| Legacy evidence | SQL report 1: `SUM(c.amount)` after `LEFT JOIN events` = **742,956.61** vs true `SUM(cases.amount)` = **622,826.44** (+19.3 %; BB-08; re-verified read-only in this stage: 125 rows, Decimal sum 622,826.44, all amounts typed REAL with <= 2 decimals); Java skips blank amounts silently (10 of 2,400 tiny; 200 of 50,000 bundled); `operating_costs.total_cases` is random, not cases created (OD-07) |

### F07-2 Behaviours
| ID | Behaviour (binding once approved) | Implements |
|---|---|---|
| BEH-MET-01 | **Metric registry.** Every metric is declared in `metric_definition` (SCH-METRIC-DEF): `metric_id`, `name`, `category` in {time, count, money, rate, age}, `definition_tag` (required, non-null, when the figure involves closed, resolved, approved, cost or handling time), `window`, `denominator`, `exclusions`, `cutoff_ref`, `basis` in {event_derived, modelled}, documentation text. A metric whose category involves those concepts but whose tag is null cannot be registered (E-MET-TAG-REQUIRED); a release test enumerates the registry. | FR-MET-01, FR-MET-06 |
| BEH-MET-02 | **Metric value** (SCH-METRIC-VALUE) always carries `definition_tag`, `policy_version` (of the policy object supplying the tag; 'candidate' status shown), window, denominator, exclusions, `n`, `basis`, `inputs_hash`, `code_version`, `computed_at` and the label **'synthetic, unvalidated'** while the data is synthetic (flag `data_origin = synthetic`, set by configuration and not removable per figure). Every rendering (API, HTML, CSV export, report) shows tag, policy version and label. | FR-MET-01, FR-MET-06, PNFR-20 |
| BEH-MET-03 | **No mixing.** The only arithmetic/comparison entry points are `combine(values, op)` and `compare(a, b)`. If the inputs carry different `definition_tag` (or different policy versions of the same tag) they raise E-MET-TAG-MIX. Tables may show different tags only through `side_by_side()`, which requires one labelled column per tag, performs no sum/ratio/difference across columns and prints 'different definitions - not comparable'. A report that claims improvement under one tag while another tag worsens carries the flag `FAIL-02-conflict` (OPD-03). | FR-MET-02 |
| BEH-MET-04 | **Time to close.** For each configured CLOCK (any status, F03) the report gives `n`, `median`, `p90` separately (never pooled across clocks). Population = completed cycles (a start and a stop event of the clock exist for the cycle; F01 `cycle` counter); incomplete cycles are excluded and counted as `open_count`. Median: arithmetic mean of the two middle values for even n. p90: nearest-rank (ceil(0.9 x n)-th smallest). Durations in hours with the clock's `calendar_basis`. `n = 0` yields `value: null, reason: "no_completed_cycles"`, never 0. | FR-MET-03, FR-DEC-06 |
| BEH-MET-05 | **Month-end totals.** One function `month_end_total(cutoff_ts, denominator_ref, source)` computed by one documented query on the target tables without joins that can fan out (a test asserts the query plan has no join to a many-side table; row count of the base set equals contributions). Arithmetic uses `decimal.Decimal` (money from REAL read via `Decimal(repr(x))`, quantised to the currency minor unit with ROUND_HALF_EVEN only at presentation). `cutoff_ts` and denominator are policy (CUTOFF kind) and required parameters; there is no hidden default (E-MET-CUTOFF-REQUIRED). Reference on the baseline: `SUM(cases.amount)` for all 125 cases = 622,826.44. | FR-MET-04 |
| BEH-MET-06 | **Unparsable amounts.** For sources holding text amounts (vendor rows, feed quantities) an unparsable value is an error object `{row_id, raw_text, code}`. By default the function raises E-MET-UNPARSABLE-INPUT listing rows; the caller may pass `allow_partial=true`, then the result is flagged `partial = true` with the error list and count and is never rendered without that flag. Nothing is skipped silently. | FR-MET-04 |
| BEH-MET-07 | **Reproducibility.** `reproduce(metric_value_id)` recomputes from the stored parameters and an `inputs_hash` over the inputs (event ids / row ids and content hashes) and returns equal/not-equal with a diff; a stored value that does not reproduce is reported as a defect. Each KPI has a generated documentation page (window, denominator, exclusions, tag, code reference). | FR-MET-06, PNFR-16 |
| BEH-MET-08 | **Backlog ageing and unresolved-exception rate per site (R1 Should).** Parameters: `definition_tag` (required) and `as_of`. Backlog = cases not in the closing state set of the declared definition at `as_of` (state by F01 as-of); ageing buckets (<= 90, 91-365, 366-730, > 730 days) from `created_at`; per `site`. Unresolved-exception rate = open exception-queue items / all exception-queue items, per site of the matched case (unmatched items under site 'unknown'). One declared definition per table. | FR-MET-05 |
| BEH-MET-09 | **Cost data guard.** `operating_costs.total_cases` is never accepted as 'cases created' (E-MET-SOURCE-REFUSED); any metric using `operating_costs` has `basis = modelled` and shows it. | FR-MET-04, OD-07 |
| BEH-MET-10 | **(R2) Unmatched rate and delay per source.** `unmatched_reference_rate` = UNMATCHED_REF + NO_BUSINESS_KEY outcomes / validated items, and `reconciliation_delay` = distribution of (`ended_at` of first run that produced an outcome minus `receipt_time`), both per source and period, from intake and run records. | FR-MET-07 |
| BEH-MET-11 | **(R2, Could) Case cost and rework.** Specified only as an interface placeholder: `OP-MET-05` returns E-MET-NOT-AVAILABLE until a cost input and owner exist (OPD-08). | FR-MET-08 |

### F07-3 Error cases
E-MET-TAG-REQUIRED, E-MET-TAG-MIX, E-MET-CUTOFF-REQUIRED, E-MET-UNPARSABLE-INPUT, E-MET-SOURCE-REFUSED, E-MET-NOT-AVAILABLE, E-MET-UNKNOWN-METRIC, E-MET-NOT-REPRODUCIBLE, E-MET-DEFINITION-REQUIRED (error-handling-spec.md).

### F07-4 Acceptance criteria
| ID | Given | When | Then | Implements | Kind |
|---|---|---|---|---|---|
| AC-MET-01 | the metric registry | enumerated by a test | every metric of category time/money involving closed, resolved, approved, cost or handling time has a non-null tag; registering one without a tag fails E-MET-TAG-REQUIRED | FR-MET-01 | negative |
| AC-MET-02 | any rendered report/API/CSV figure of those categories | inspected (100%) | tag, policy version, status (candidate/adopted/accepted-open) and the label 'synthetic, unvalidated' appear | FR-MET-01, PNFR-20 | positive |
| AC-MET-03 | one figure tagged D-OPS and one D-EVID | `combine(sum)` and `compare` are called | both raise E-MET-TAG-MIX | FR-MET-02 | negative |
| AC-MET-04 | the same two figures | `side_by_side` is used | rendered in separate labelled columns with no derived cross-column value and the 'not comparable' note | FR-MET-02 | positive |
| AC-MET-05 | D-OPS improves and D-EVID worsens between two periods | the trend report is generated | flag FAIL-02-conflict is present and no single 'improved' headline is produced | FR-MET-02, BR-01 | edge |
| AC-MET-06 | a fixture with 10 completed cycles under clock C-OPS and 8 under C-EVID | the time-to-close report runs | two separate series, each with n, median, p90 per stated method, plus open_count; no pooled series | FR-MET-03 | positive |
| AC-MET-07 | fixture durations [1,2,3,4,100] and [1,2,3,4] | median and p90 computed | median 3 and 2.5; p90 nearest-rank 100 and 4 | FR-MET-03 | edge |
| AC-MET-08 | the 125 shipped cases (events: CASE_CREATED only for most) | time-to-close is requested for event-derived clocks | `value: null`, reason `no_completed_cycles`, n = 0 (K-04/K-05 remain unmeasurable per OD-07); no zero or invented value | FR-MET-03, PNFR-20 | edge |
| AC-MET-09 | the shipped 125 cases | `month_end_total` is called with an explicit cutoff after all case dates and source = cases.amount | result 622,826.44 exactly (Decimal), `n = 125`; the legacy 742,956.61 is not produced | FR-MET-04 | positive |
| AC-MET-10 | the same call without cutoff or denominator | called | E-MET-CUTOFF-REQUIRED | FR-MET-04 | negative |
| AC-MET-11 | a cases fixture where two cases have 2 events and 1 event respectively | totals computed | each case amount counted once (no fan-out); an equivalent join-based query on the same fixture inflates and the test asserts they differ | FR-MET-04 | negative |
| AC-MET-12 | a text-amount fixture with 1 blank, 1 'abc', 1 negative among 100 rows | totals computed | default call raises E-MET-UNPARSABLE-INPUT naming 2 rows; with allow_partial the result is flagged partial with 2 errors; negative value is summed as-is and flagged NEGATIVE_VALUE | FR-MET-04 | negative |
| AC-MET-13 | float sums 0.1+0.2 style fixture | totals computed | exact decimal result 0.30 (no binary rounding drift) | FR-MET-04 | edge |
| AC-MET-14 | a metric computed and stored | `reproduce` runs after unrelated data are added | equal value (inputs_hash restricts the inputs); if a code change alters it, E-MET-NOT-REPRODUCIBLE is reported | FR-MET-06, PNFR-16 | positive |
| AC-MET-15 | all registered KPIs | documentation is generated | 100% have window, denominator, exclusions and tag; a KPI missing one fails the build | FR-MET-06 | negative |
| AC-MET-16 | `operating_costs.total_cases` offered as 'cases created' | a metric is configured with it | E-MET-SOURCE-REFUSED | BEH-MET-09 | negative |
| AC-MET-17 | tag D-OPS declared, as_of 2025-12-19 | backlog by site is produced | per-site backlog counts and bucket counts; total backlog under D-OPS = cases whose state is not CLOSED at as_of (89 of 125 per Stage 4 K-09-OPS, if the fixture is the baseline); table has one tag | FR-MET-05 | positive |
| AC-MET-18 | backlog requested without a definition tag | requested | E-MET-DEFINITION-REQUIRED | FR-MET-05 | negative |
| AC-MET-19 | R2: intake and run records for two sources | per-source metrics run | unmatched rate and delay distribution per source are produced and reproducible | FR-MET-07 | positive |
| AC-MET-20 | R2: OP-MET-05 requested | called | E-MET-NOT-AVAILABLE | FR-MET-08 | negative |
| AC-MET-21 | any metric endpoint | called twice with identical parameters | byte-identical JSON (apart from `computed_at`, excluded from the comparison) | PNFR-17 | positive |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-F07-1 Median/p90 methods (mean-of-middle; nearest-rank) are spec choices; no owner defined a method. Confirm: Engagement lead (Dinesh Naik).
- A-12-F07-2 'Unresolved-exception rate' is defined here as open exception-queue items / all exception-queue items per matched-case site; the PRD gives no formula.
- A-12-F07-3 Age buckets copied from the Stage 4 sheet (<=90, 91-365, 366-730, >730).

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-F07-1 Month-end cut-off and denominator (OPD-08).
- U-12-F07-2 Cost input and owner (OPD-08); no benefit is quantified here.

## Unresolved Issues
- OD-S12-08: metric functions require explicit cut-off/denominator parameters; no adopted values ship.
- Most event-derived KPIs return null on shipped data (no real closure timestamps).

## Residual Risks
- New totals will differ from legacy figures by design (golden diff must list each difference, FR-CO-01).
- Null results may be misread as zero; AC-MET-08 pins null.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
