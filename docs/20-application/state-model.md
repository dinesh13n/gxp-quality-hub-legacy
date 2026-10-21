---
stage: "20 — Application & Services Engineering"
artifact: "state-model.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/policy/migrations/M002_policy_rules.sql", "hub/runs/migrations/M005_runs_metrics.sql", "hub/store/migrations/M000_coexistence.sql", "hub/store/forward/M001_access_audit.sql", "hub/policy/withdrawal.py", "hub/coexistence/register.py", "hub/golden/observe.py", "hub/web/migrations/M006*.sql"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. No migration was added or changed in Stage 20 (M000..M007 unchanged; DW-29 consolidation is Stage 27).**

## Summary
Stage 20 adds state only as rows in existing append-only tables: a `POLICY_WITHDRAWN` policy event (type already allowed by M002), rule_trace rows from the producer, deviation_register rows DV-10 / DV-11 and a guarded text refresh of DV-02/03/04/07/09. Golden observation runs in a throw-away scratch store that is deleted after the run.

## Findings
### SM-1 Policy version lifecycle (effective view)
| Stored status (immutable row) | Event | Effective view | Applies? | Tag |
|---|---|---|---|---|
| candidate | — | candidate | no verdicts | [Verified Fact] |
| accepted-open | POLICY_ACCEPTED_OPEN | accepted-open | no verdicts | [Verified Fact] |
| adopted | POLICY_ADOPTED | adopted | from effective_from to effective_to | [Verified Fact] |
| adopted | + POLICY_WITHDRAWN {withdrawn_from} | `withdrawal` object added when in effect; listed under status report `withdrawn` | until the day before withdrawn_from | [Verified Fact] |
- [Verified Fact] "In effect at T" = event recorded at or before T and withdrawn_from <= date(T) (`hub/policy/withdrawal.py`), so an earlier stored metric value reproduces exactly (STG20 S11).
- [Verified Fact] Withdrawal does not change `policy_object.status` (CHECK has no `withdrawn`, rows immutable) nor `metric_value.policy_status` (CHECK has no `withdrawn`); the marker lives in the event, the overlay and `metric_value.detail` - a design forced by the DDL, recorded as S20-DEV-06.
- [Verified Fact] One withdrawal per version; a re-adoption may start on or after withdrawn_from (overlap rule, STG20 S13).

### SM-2 Deviation register rows
| Row state | Transition | Who | Tag |
|---|---|---|---|
| absent | INSERT OR IGNORE from seed v2 on every store open | product (seed) | [Verified Fact] |
| proposed, approval_ref NULL, text = INC-02 seed | refreshed to seed v2 text | product (seed refresh) | [Verified Fact] |
| proposed with other text, approved, rejected | never touched by the product | human (outside the product, HAR-06) | [Verified Fact] |

### SM-3 Observation record (golden-observe)
`{schema golden-observation/v1, code_digest, baseline{legacy.sqlite3, partner_export.csv(tiny)}, observations{9 ids}}`; accepted by golden-compare only while both digests match; otherwise the 9 module probes are NOT-RUN with a stated reason. [Verified Fact]

### SM-4 Rule traces
Producer writes one insert-only `rule_trace` (+ audit RULE_TRACE_RECORDED, actor `rule-trace-producer`, kind `rule`) per case whose (inputs, result) differ from the latest trace for (function, rule set); otherwise `unchanged`. Flags `FLG-RT-*` start `open`; human actions append `flag_action` rows. [Verified Fact]

## Evidence References
STG20 S07, S08, S11, S12, S13, S14; `docs/20-application/evidence/register-dump.json`, `golden-observation.json`.

## Assumptions
- A-20-SM-1 [Assumption] Day-granular withdrawal (YYYY-MM-DD, inclusive start of non-application) matches the effective_from/effective_to convention; confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-20-SM-1 Whether a withdrawal may be reversed (not specified; not built - a new adoption is the path).

## Unresolved Issues
- A DDL addendum adding `withdrawn` to the status enums would allow a stored status; deferred to the Stage 27 migration consolidation (DW-29) if wanted.

## Residual Risks
- RR-SM-1 Consumers that read `policy_object.status` by SQL and were not updated would ignore a withdrawal; the four consumers found (closure, consistency, clocks, metrics) were updated; others found later must use `hub.policy.withdrawal` (Low).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | First issue. |
