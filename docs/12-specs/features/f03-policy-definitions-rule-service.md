---
stage: "12 — Spec-Driven Design"
artifact: "features/f03-policy-definitions-rule-service.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["app/legacy_logic.py", "legacy_js/legacy_policy.js", "legacy_batch/shift_reconciliation.py", "contracts/decision-policies-archive.json", "docs/07-repo-assessment/baseline-behaviour.md (BB-01, BB-07, BB-09)", "docs/07-repo-assessment/characterization-test-plan.md (CT-01..03, CT-13)", "docs/03-problem-value/success-criteria.md (candidate definitions)", "docs/10-architecture/adrs/ADR-007-policy-and-rule-service.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Feature spec for versioned policy objects and the table-driven rule service (CAP-03): 3 as-found rule sets specified as data, 11 behaviours, 25 acceptance criteria for FR-POL-01..06. No definition, clock or active rule set ships adopted.

## Findings
### F03-1 Scope and traceability [Verified Fact: requirement text and as-found rules; Inference: design]
Feature **F03 Policy, Definitions & Rule Service** = CAP-03, component C4, ADR-007 (policy objects + one table-driven rule service, no adopted defaults), ADR-003 (`defaulted` marker in new service only), data contract DC-13.

| Implements | FR-POL-01, FR-POL-02, FR-POL-03, FR-POL-04, FR-POL-06 (R1); FR-POL-05 (R2) |
|---|---|
| Also constrained by | FR-GATE-03/06, FR-CO-01, FR-REV-01, PNFR-17, PNFR-15; BR-01, BR-02, BR-03, BR-13; RC-3, RC-4; CT-01..03, CT-13 |
| Open decisions | OD-S12-01 (definitions), OD-S12-02 (48 h clock), OD-S12-04 (approval-rule authority, default 999,999), OD-S12-13 (preserve vs fix) |

### F03-2 As-found rule sets to be loaded (read-only, origin = as-found) [Verified Fact]
| Rule set | Source | Functions | As-found logic (pinned by Stage 7 goldens) |
|---|---|---|---|
| `as-found-python` | `app/legacy_logic.py` | PRIORITY, MANUAL_REVIEW | priority: status CLOSED -> archive; else severity CRITICAL or amount > 50000 (strict, float) -> urgent; else severity HIGH or status ESCALATED -> review; else queue. manual_review_required: severity in {HIGH, CRITICAL} or status in {ESCALATED, REOPENED}. Golden: 120-row priority truth table, 20-row manual-review table; shipped distribution archive 36 / queue 70 / review 17 / urgent 2 (BB-01). |
| `as-found-js` | `legacy_js/legacy_policy.js`, `contracts/decision-policies-archive.json` | AMOUNT_LIMIT | threshold(region, year) = `limit` of the first historical version whose region matches and `effective_from` starts with the year (15 rows: APAC/EMEA/AMER x 2022..2026, limits 15000..27200 USD; approval_roles operations_lead 2022-2024, business_owner + risk_control 2025-2026); no match -> 999999. Allowed iff `Number(amount) <= threshold * 1.05`. Golden: 32 pairs and tolerance cases 26250 / 26250.01 (CT-13). |
| `as-found-batch` | `legacy_batch/shift_reconciliation.py` | SHIFT_FLAG | flagged iff status in {HOLD, REVIEW} or (threshold not null and value > threshold), threshold from `policy_register` by region where active = 1. The row-multiplying JOIN (118 distinct objects in the first 500 rows, BB-07) is an adapter defect, **not** part of the rule row logic (OD-S12-13). |

All three also publish a normalised boolean output `amount_over_limit` (python: amount > 50000; js: amount > threshold*1.05; batch: value > threshold) used only for divergence reporting (FR-POL-05). The mapping to a common key is a spec choice [Inference]; the owner may redefine it (OD-S12-04).

### F03-3 Behaviours
| ID | Behaviour (binding once approved) | Implements |
|---|---|---|
| BEH-POL-01 | **Policy objects** (SCH-POLICY): `policy_id`, `version` (integer, immutable once written), `kind` in {DEFINITION, CLOCK, CLOSURE, CONSISTENCY, CUTOFF}, `name`, `definition_tag` (D-OPS, D-EVID, D-FIN or other), `body` (JSON validated by kind), `owner` (string or `unassigned`), `effective_from`, `effective_to`, `status` in {candidate, adopted, accepted-open}. Editing creates a new version; old versions are never changed. | FR-POL-01 |
| BEH-POL-02 | **Seed content.** On a fresh install the store contains exactly three DEFINITION candidates (D-OPS 'operations marks the case closed', D-EVID 'closed and verifiable evidence and authorised approver recorded', D-FIN 'successfully resolved for cost purposes, undefined') and two CLOCK candidates (start FACT_RECEIVED; stop FACT_OPS_CLOSED or FACT_EVIDENCE_COMPLETE; `candidate_duration_hours = 48`), all `status = candidate`, `owner = unassigned`. No row has status `adopted`. Source of the candidate wording: docs/03-problem-value/success-criteria.md. | FR-POL-01, FR-POL-02 |
| BEH-POL-03 | **Adoption.** Transition candidate -> adopted, or recording `accepted-open` (explicit, dated, with authority_ref and reason), is Zone H ZH-05. Service, importer, scheduler actors are rejected (F02). Two adopted versions of the same (`kind`, `definition_tag`) with overlapping effective windows are refused (E-POL-OVERLAP). | FR-POL-01, FR-GATE-03 |
| BEH-POL-04 | **Clock model.** A CLOCK body holds `clock_start_event`, `clock_stop_event`, `duration_hours` (nullable), `calendar_basis` in {wall_clock, business_calendar}, `calendar_ref` (required iff business_calendar; no calendar exists in the repo - Unknown). Elapsed time is computable under every configured clock whatever its status. A pass/fail verdict ('within 48 h') is produced only for a clock with status `adopted` and non-null `duration_hours`; otherwise the output carries `verdict: "not_available_no_adopted_policy"`. | FR-POL-02, FR-DEC-06, FR-MET-03 |
| BEH-POL-05 | **Change events.** Every create-version, adoption, accepted-open, withdrawal, rule-row edit, rule-set activation or deactivation writes an immutable `policy_events` row `{event_id, policy_ref, actor, occurred_at, old_value, new_value, authority_ref, event_type}`; `authority_ref` must be non-empty (E-POL-AUTHORITY-REQUIRED). Edits are Zone H (ZH-10); creating a *candidate* may be done by roles quality_lead or compliance and is audited. | FR-POL-03, FR-SEC-02 |
| BEH-POL-06 | **Rule service.** `RuleService.evaluate(ruleset_ref, function, inputs)` is a pure function of (rule-set version, inputs): no clock, randomness, I/O or database read inside the evaluation. It returns `{outcome, trace[], defaulted, defaulted_reason, ruleset_ref, authoritative}`. `trace` lists each row examined `{row_id, ordinal, matched, inputs_used}` and is sufficient to regenerate the explanation text (F08). | FR-POL-04, FR-REV-01, PNFR-17 |
| BEH-POL-07 | **Rule data.** Rule rows hold thresholds, regions, effective dates, owner and default behaviour as data. The three as-found sets are loaded by a loader that reads the legacy files read-only (C11) and are marked `origin = as-found`, `read_only = true`; edits create a *custom* set, never modify an as-found one. | FR-POL-04, FR-CO-01 |
| BEH-POL-08 | **Active set.** Per function there is a pointer `active_ruleset`. It ships **unset**. Setting it is ZH-06. `evaluate` with an explicit `ruleset_ref` always works (read-only what-if) and returns `authoritative = false` unless that set is the active one for the function. `evaluate` without `ruleset_ref` while no active set exists returns E-POL-NO-ACTIVE-RULESET. | FR-POL-04, FR-GATE-03 |
| BEH-POL-09 | **Defaulted marker.** If no rule row matches, or any input value is outside the declared domain of its field (unknown status, severity, region or year), the result carries `defaulted = true` and a `defaulted_reason` in {NO_MATCH_REGION_YEAR, UNKNOWN_INPUT_VALUE, NULL_INPUT}; every output that shows the result (API, pack, report, trace text) shows the marker. The as-found default **value** is preserved (999999 for AMOUNT_LIMIT; `queue` for PRIORITY fall-through) **and marked**; changing the value or replacing it by manual review requires an approved change (HAR-06) and OD-S12-04. | FR-POL-06, FR-CO-01 |
| BEH-POL-10 | **Divergence report (R2).** `GET /rules/divergence` runs every loaded set that publishes `amount_over_limit` over a case set or batch of inputs and lists the cases where outputs differ, with each set's trace. It resolves nothing and changes no state. | FR-POL-05 |
| BEH-POL-11 | **Input validation.** `amount` is parsed as `Decimal`; non-numeric, NaN or infinite input returns E-POL-INPUT-INVALID rather than an outcome (the as-found JS returned undefined behaviour for 'abc'/null - golden CT-13; behaviour change recorded in OD-S12-13). | FR-POL-04, PNFR-17 |

### F03-4 Error cases
E-POL-NO-ACTIVE-RULESET, E-POL-OVERLAP, E-POL-AUTHORITY-REQUIRED, E-POL-INPUT-INVALID, E-POL-READONLY-SET, E-POL-UNKNOWN-FUNCTION, E-POL-NOT-FOUND, E-POL-CLOCK-CALENDAR-REQUIRED, E-GATE-NOT-AUTHORISED (error-handling-spec.md).

### F03-5 Acceptance criteria
| ID | Given | When | Then | Implements | Kind |
|---|---|---|---|---|---|
| AC-POL-01 | a fresh install | all policy objects are listed | exactly three DEFINITION and two CLOCK objects exist, all `candidate`, `owner = unassigned`; count(adopted) = 0 | FR-POL-01, FR-POL-02 | positive |
| AC-POL-02 | a fresh install | a service-actor token requests adoption of D-OPS | rejected E-GATE-NOT-AUTHORISED and audited; status still candidate | FR-POL-01, FR-GATE-03 | negative |
| AC-POL-03 | a holder session | D-OPS is adopted with effective_from and authority_ref | new version status adopted, POLICY_ADOPTED event with old/new value and authority_ref stored | FR-POL-01, FR-POL-03 | positive |
| AC-POL-04 | D-OPS adopted for 2026 | a second adoption with overlapping window for the same tag is posted | E-POL-OVERLAP | BEH-POL-03 | negative |
| AC-POL-05 | a holder session | 'accepted-open' is recorded for D-FIN with reason | status accepted-open, dated event exists; a report shows the definition as accepted-open, not as adopted | FR-POL-01 | positive |
| AC-POL-06 | clocks C-OPS and C-EVID are candidates and two cases exist | elapsed time is requested | elapsed under both clocks is returned side by side; `verdict = not_available_no_adopted_policy`; no pass/fail anywhere | FR-POL-02 | positive |
| AC-POL-07 | a CLOCK created with `calendar_basis = business_calendar` and no `calendar_ref` | it is saved | E-POL-CLOCK-CALENDAR-REQUIRED | FR-POL-02 | negative |
| AC-POL-08 | a CLOCK adopted with duration 48 | elapsed 47.9 h and 48.1 h cases are evaluated | verdicts within / not within, boundary rule 'elapsed <= duration' is stated in the response | FR-POL-02 | edge |
| AC-POL-09 | any policy edit or rule-row edit | it is executed with empty authority_ref | E-POL-AUTHORITY-REQUIRED; nothing stored | FR-POL-03 | negative |
| AC-POL-10 | a threshold edit by a holder | the policy_events are read | one event with who, when, old value, new value, authority_ref; a service actor attempting the same edit is rejected and logged | FR-POL-03 | positive |
| AC-POL-11 | the loader run against the shipped repo | rule sets are listed | `as-found-python`, `as-found-js`, `as-found-batch` exist with `origin = as-found`, `read_only = true`; an edit attempt returns E-POL-READONLY-SET | FR-POL-04 | positive |
| AC-POL-12 | `as-found-python` and the 120-row truth table of Stage 7 (`batch_golden.priority_truth_table`) | each row is evaluated with explicit ruleset_ref | all 120 outcomes equal the golden (byte-equal JSON of outcomes) | FR-POL-04, FR-CO-01 | positive |
| AC-POL-13 | `as-found-python` and the 20-row manual-review table | evaluated | all 20 equal golden, including CLOSED+HIGH = true | FR-POL-04, FR-CO-01 | positive |
| AC-POL-14 | `as-found-js` and the 32 (region, year) pairs plus tolerance cases 26250 and 26250.01 | evaluated | thresholds and allow/deny equal golden (26250 allowed, 26250.01 denied for APAC 2026 limit 25000 x 1.05) | FR-POL-04, FR-CO-01 | edge |
| AC-POL-15 | `as-found-batch` and a fixed row set of (status, value, threshold) cases | evaluated | flags equal the row-level predicate; a test shows the rule service does not multiply rows | FR-POL-04 | positive |
| AC-POL-16 | no active ruleset for PRIORITY | evaluate is called without ruleset_ref | E-POL-NO-ACTIVE-RULESET | FR-POL-04 | negative |
| AC-POL-17 | no active ruleset | evaluate is called with explicit `as-found-python` | outcome returned with `authoritative = false` | FR-POL-04 | positive |
| AC-POL-18 | a holder sets `active_ruleset[PRIORITY] = as-found-python` | the pointer is read and the change audited | pointer set, RULESET_ACTIVATED event exists; a service actor attempt is rejected | FR-POL-04, FR-GATE-03 | positive |
| AC-POL-19 | `as-found-js`, region 'MARS', year 2026 | evaluated | limit 999999 returned with `defaulted = true`, reason NO_MATCH_REGION_YEAR; the same marker appears in the API response, pack and trace text | FR-POL-06 | edge |
| AC-POL-20 | `as-found-python` with status 'WEIRD' | evaluated | outcome `queue` (as-found) with `defaulted = true`, reason UNKNOWN_INPUT_VALUE | FR-POL-06, FR-CO-01 | edge |
| AC-POL-21 | a known status and severity (LOW, OPEN) falling to the final queue row | evaluated | outcome `queue`, `defaulted = false` | FR-POL-06 | positive |
| AC-POL-22 | the same (ruleset version, inputs) evaluated 1000 times in two processes | outputs compared | bit-identical JSON; evaluation function performs no I/O (verified by a test that runs it with file, network and clock access patched to raise) | PNFR-17, BEH-POL-06 | positive |
| AC-POL-23 | amount 'abc', null or NaN | evaluate is called | E-POL-INPUT-INVALID; no outcome | BEH-POL-11 | negative |
| AC-POL-24 | R2: the 125 shipped cases and the three sets | the divergence report runs | lists cases where `amount_over_limit` differs, with traces; the count is recorded; no state change and no 'correct' set named | FR-POL-05 | positive |
| AC-POL-25 | every policy version row | an UPDATE is attempted | rejected (immutability) | FR-POL-01, FR-POL-03 | negative |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-F03-1 The normalised output key `amount_over_limit` is a spec convenience for divergence reporting only; it does not assert that the three rules are meant to agree. Confirm: Engagement lead (Dinesh Naik).
- A-12-F03-2 Domain lists for UNKNOWN_INPUT_VALUE (status vocabulary, severity LOW/MEDIUM/HIGH/CRITICAL, regions AMER/APAC/EMEA in cases) are taken from the shipped data; real domains are unknown.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-F03-1 Which of the three rules (if any) is correct (OPD-04).
- U-12-F03-2 Business calendar for 'business_calendar' clocks - none exists.
- U-12-F03-3 Whether 48 h is the right duration (OPD-02).

## Unresolved Issues
- OD-S12-01, OD-S12-02, OD-S12-04, OD-S12-13: mechanism fully specified; content parameterised; acceptance tests use explicitly configured test policies that are never shipped as adopted.

## Residual Risks
- Reader may take candidate wording of D-OPS/D-EVID/D-FIN as agreed policy; every surface labels them candidate.
- Rejecting NaN/'abc' inputs changes as-found JS behaviour (OD-S12-13).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
