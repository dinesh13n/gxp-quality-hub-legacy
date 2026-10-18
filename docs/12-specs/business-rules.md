---
stage: "12 — Spec-Driven Design"
artifact: "business-rules.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/functional-requirements.md", "docs/03-problem-value/business-requirements.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/12-specs/features/*.md", "docs/09-initial-prd/functional-requirements.md", "docs/09-initial-prd/nfrs.md", "docs/10-architecture/adrs/", "docs/11-data-context/data-contracts.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Specs describe NEW target modules; no implementation code is written in this stage. Nothing here is an approval; approval is Dinesh Naik's decision (HAR-11).**

Register of 48 testable spec business rules (SBR-) across all ten features, each traced to FR/PNFR/BR/RC IDs; 7 rules marked [PARAM] where content depends on an open decision and only the mechanism and configurable parameter are specified.

## Findings
### BR-1 How to read this register
Spec business rules carry the ID prefix **SBR-** to avoid collision with Stage 3 business requirements (**BR-01..BR-13**). Each rule is a testable statement; the Implements column lists FR-/PNFR-/BR-/RC- IDs for the Stage 13 traceability matrix. Rules marked **[PARAM]** have content that depends on an open decision; the rule specifies the mechanism and the configurable parameter, never a value. Rule IDs are referenced by feature specs and acceptance criteria.

### BR-2 Decision and evidence record (F01)
| ID | Rule | Implements |
|---|---|---|
| SBR-DEC-01 | `decision_events` rows are insert-only. `seq` per case is gapless from 1. Corrections are new events referencing the corrected `event_id`; no event is ever altered or removed. | FR-DEC-01; BR-07; RC-2 |
| SBR-DEC-02 | `recorded_at` is server UTC and not client-settable. `occurred_at <= recorded_at` and `occurred_at >= occurred_at` of the previous event of the same case. | FR-DEC-02; PNFR-17 |
| SBR-DEC-03 **[PARAM]** | **Closing-state set.** (a) If a CLOSURE policy is active (selected by ZH-05 and status adopted or accepted-open) the closing set is `body.closing_states` of that policy. (b) If none is active, behaviour follows `closure.unconfigured_behaviour`: `treat_label_CLOSED_as_closing` (**default**; every transition into a state whose vocabulary role tag is `closing_label` is checked, fail-closed) or `none` (no check; events flagged `closure_check = not_configured`). The choice of (b) value is Zone H configuration (ZH-08-class) and is open decision OD-S12-03. | FR-DEC-05; BR-09; RC-3 |
| SBR-DEC-04 | A closing transition requires >= 1 `evidence_ref` that resolves to an existing evidence record **or** an accepted `close_exception` (Zone H). Sufficiency is never evaluated; it is policy (OPD-07, OD-S12-07). | FR-DEC-05; BR-09 |
| SBR-DEC-05 | Imported legacy REOPENED cases without a reopen event carry the marker `LEGACY_UNEVIDENCED_REOPEN`; the invariant 'no REOPENED case without a REOPEN event' is evaluated on non-marked cases and the marked ones are listed. No reopen event is invented. | FR-DEC-03; DQ-16 |
| SBR-DEC-06 | A REOPEN event increments `cycle`; the three fact events (FACT_RECEIVED, FACT_OPS_CLOSED, FACT_EVIDENCE_COMPLETE) belong to a cycle. Elapsed time under a clock is computed per completed cycle. | FR-DEC-06; FR-MET-03 |
| SBR-DEC-07 | Transition legality: `structural` mode permits any change between two distinct states of the case vocabulary except Zone H ones; a strict table may replace it (OD-S12-16). Vocabularies are never mapped to each other. | FR-DEC-01; FR-POL-01 |

### BR-3 Human gate (F02)
| ID | Rule | Implements |
|---|---|---|
| SBR-GATE-01 | The Zone H action list ZH-01..ZH-10 is closed. An action outside the list cannot be accepted (E-GATE-UNKNOWN-ACTION). | FR-GATE-03 |
| SBR-GATE-02 | A Zone H action is accepted iff: interactive human session AND principal in `zone_h.holders` AND role dispositioner AND re-authentication within `zone_h.reauth_window_seconds` AND mode/values permit the action AND `pack_hash` current (for ZH-01..03). Any other combination is rejected and audited. No setting disables a condition. | FR-GATE-01; FR-GATE-03; FR-GATE-04; BR-08 |
| SBR-GATE-03 **[PARAM]** | Disposition recording follows `disposition.mode` in {none (default), event, external_ref}; the mode in force at write time is stored on the event; past events are never rewritten. | FR-GATE-05; OPD-05 |
| SBR-GATE-04 | Override, dismiss or refuse of any rule-generated item is always accepted from an authenticated reviewer-class role when a non-empty reason is supplied; the original output is retained. | FR-GATE-06; PNFR-15 |
| SBR-GATE-05 | Inbound text, rule output, report content, search results and template content never populate a disposition value or trigger a Zone H event. | FR-GATE-01; FR-INT-07 |

### BR-4 Policy and rules (F03)
| ID | Rule | Implements |
|---|---|---|
| SBR-POL-01 | Policy object versions and rule rows are immutable; change = new version; each change is a `policy_events` row with old value, new value, actor, time and a non-empty `authority_ref`. | FR-POL-03 |
| SBR-POL-02 | The shipped product contains no policy object with status `adopted`, no active rule set, no `disposition.mode` other than `none`, no holder, and no enabled schedule. | FR-POL-01; FR-GATE-04; FR-RUN-01; CG-7 |
| SBR-POL-03 | `evaluate()` is pure: output = f(rule-set version, inputs). | FR-POL-04; PNFR-17 |
| SBR-POL-04 **[PARAM]** | **Defaulted marker.** An outcome carries `defaulted = true` if no row matches or an input is outside the field's declared domain; the as-found default value is retained and marked until a decision under OPD-04 / HAR-06 says otherwise. | FR-POL-06; BR-13 |
| SBR-POL-05 | As-found rule sets are read-only; custom sets are separate objects. | FR-POL-04; FR-CO-01 |
| SBR-POL-06 **[PARAM]** | A pass/fail verdict on a clock exists only when the clock is `adopted` and `duration_hours` is set; otherwise only elapsed times are reported. | FR-POL-02 |
| SBR-POL-07 | Adopted versions of the same (`kind`, `definition_tag`) cannot have overlapping effective windows. | FR-POL-01 |
| SBR-POL-08 | Boundary convention for a duration check: within the clock iff `elapsed <= duration` (inclusive) in the clock's calendar basis. [Assumption; owner of the clock may change it as policy.] | FR-POL-02 |

### BR-5 Intake and exceptions (F04)
| ID | Rule | Implements |
|---|---|---|
| SBR-INT-01 **[PARAM]** | **Item identity.** `identity_key = sha256(canonical([source, partner, record_kind, ref_id, source_ts]))`. `business_key` and `feed_id` are not identities (FND-INT-2). Identity-key definition per source is configuration; the feed definition is OD-S12-17. | FR-INT-02; FR-INT-03; RC-6 |
| SBR-INT-02 | `content_hash = sha256(canonical({schema_rev, payload}))`, canonical = UTF-8, sorted keys, no insignificant whitespace; transport fields excluded. | FR-INT-02; FR-INT-03 |
| SBR-INT-03 | **Reason precedence** (highest first): UNSUPPORTED_REVISION, INVALID_JSON, MISSING_ENVELOPE_FIELD, UNKNOWN_RECORD_KIND, MISSING_PAYLOAD_FIELD, CONTRACT_VIOLATION (enforce only), REVISED_CONFLICT, UNPARSABLE_AMOUNT, NO_BUSINESS_KEY, AMBIGUOUS_MATCH, UNMATCHED_REF, NEGATIVE_VALUE, UNKNOWN_UNIT, UNKNOWN_CURRENCY, IDENTIFIER_PATTERN. The first applicable is `primary_reason`; all applicable are in `all_reasons`. | FR-INT-06 |
| SBR-INT-04 | Order of stages: store raw -> identity/hash comparison (NOOP or conflict) -> validate -> classify -> match -> outcome. A conflict still records validation results in `all_reasons`. | FR-INT-02; FR-INT-03; FR-INT-04 |
| SBR-INT-05 | Matching is exact string equality (NFC + trim) on registered keys; 0 hits -> UNMATCHED_REF, 1 -> link, >1 -> AMBIGUOUS_MATCH. | FR-INT-05; FR-ID-02 |
| SBR-INT-06 | Untrusted text never reaches decision parameters; payload `state`/`quality_flag`/`subtype` are stored as source attributes only. | FR-INT-07; PNFR-13 |
| SBR-INT-07 **[PARAM]** | Contract binding default is `record_only` for every source; `enforce` is per-source configuration (OD-S12-11). | FR-INT-04 |
| SBR-INT-08 | Duplicates (`NOOP_DUPLICATE`) are excluded from every queue, total and metric by definition of the outcome views. | FR-INT-02; PNFR-11 |

### BR-6 Identity, runs, metrics, security, coexistence
| ID | Rule | Implements |
|---|---|---|
| SBR-ID-01 | Rule links only by registered exact key; no similarity of any kind. | FR-ID-02; ADR-009 |
| SBR-ID-02 | Orphan counts are reported measures; orphans are never repaired by the product. | FR-ID-02; FR-MET-07; DQ-24 |
| SBR-ID-03 | A human link needs a registered pair, a reason and an authenticated human reviewer-class role; it is an event. | FR-ID-01; FR-ID-02 |
| SBR-RUN-01 | No hidden capacity cap: every limit is configuration, printed in the run record; remaining work is counted and checkpointed. | FR-RUN-03; BR-12 |
| SBR-RUN-02 | One active run per job; a dead run is closed by RUN_ABANDONED. | FR-RUN-02 |
| SBR-RUN-03 | Jobs never perform Zone H actions. | FR-GATE-01; FR-RUN-01 |
| SBR-RUN-04 **[PARAM]** | `schedule.enabled` defaults false; enabling is ZH-09 (OD-S12-10). | FR-RUN-01 |
| SBR-MET-01 | A metric involving closed, resolved, approved, cost or handling time must name a `definition_tag`. | FR-MET-01 |
| SBR-MET-02 | Values with different tags or tag-policy versions are never summed, averaged or compared. | FR-MET-02 |
| SBR-MET-03 | Median = mean of middle two for even n; p90 = nearest-rank ceil(0.9 n); n=0 gives null. | FR-MET-03 |
| SBR-MET-04 | Money is `Decimal`; no float arithmetic; rounding (ROUND_HALF_EVEN) only at presentation. | FR-MET-04; NFR-16 |
| SBR-MET-05 | An unparsable amount is an error, never skipped; partial results are flagged. | FR-MET-04 |
| SBR-MET-06 | Every KPI output carries window, denominator, exclusions, tag and 'synthetic, unvalidated' while data are synthetic. | FR-MET-06; PNFR-20 |
| SBR-MET-07 | `operating_costs.total_cases` is never 'cases created' (OD-07). | FR-MET-04 |
| SBR-SEC-01 | Deny by default for routes, fields, roles and unknown access levels. | FR-SEC-01; FR-SEC-03 |
| SBR-SEC-02 | Audit record is written in the same transaction as the audited change; failure aborts the change. | FR-SEC-02; PNFR-09 |
| SBR-SEC-03 | Hold-all: no delete path for retained tables until a retention policy is adopted (OPD-09). | PNFR-10 |
| SBR-CO-01 | A difference from a Stage 7 golden is acceptable only if it is in the deviation register with status `approved` and an approval reference (HAR-06). | FR-CO-01; BR-13 |
| SBR-CO-02 | Executable acceptance runs only in a full repo copy outside the working tree (OD-03a), with manifest verification after. | FR-CO-01 |
| SBR-CO-03 | No AI, LLM or ML call or dependency; no model-inference egress. | FR-CO-04; PNFR-18 |

## Evidence References
See evidence_sources in the header and per-row citations.

## Assumptions
- A-12-01 Stage 9 FRs/PNFRs and Stage 10 ADRs are DRAFT/PROPOSED; specs treat them as candidate requirements, not approvals (A-09-01, OPD-13). Confirm: Engagement lead (Dinesh Naik).
- A-12-02 The client is fictional/synthetic; every figure is 'synthetic, unvalidated'. Dinesh Naik is the only human stakeholder (OD-04).
- A-12-BR-1 SBR-POL-08 inclusive boundary and SBR-MET-03 percentile method are conventions chosen for testability; the owner may change them as policy.

## Unknowns
- U-12-01 Target runtime (Python version, SQLite build, FTS5 availability) is unknown; device dev runtime is Python 3.10.12 / SQLite 3.37.2 (OD-S12-12). Owner: Engagement lead (Dinesh Naik).
- U-12-BR-1 Real business rules for closure, approval and evidence sufficiency do not exist in the repo (RC-3, RC-4).

## Unresolved Issues
- [PARAM] rules cannot get final content before OD-S12-01..08, 10, 11, 17.

## Residual Risks
- A convention mistaken for a business decision (SBR-POL-08, SBR-MET-03) could be cited as client policy; labelled Assumption.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Stage 12). |
