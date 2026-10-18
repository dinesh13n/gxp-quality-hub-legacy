---
stage: "9 — Initial PRD / Product Intent"
artifact: "functional-requirements.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/success-criteria.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/08-ai-qualification/qualification-decision.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Approval of this PRD is Dinesh Naik's decision (HAR-11); nothing here is an approval.**

52 functional requirements across 10 capabilities (43 in R1 / MVP, 9 in R2 / later). Every requirement has a stable ID (`FR-<CAP>-nn`), a MoSCoW priority, a release, and traces to a Stage 3 problem (P-1..P-5), a Stage 3 BR-/NFR-/SUC- ID and a Stage 6 root cause (RC-1..RC-8) in the table, with repository evidence and a verification method. The product is **No-AI** (OD-08): rules, keyword/field search, templates, deterministic core. Rules nobody owns (definition of closed/resolved/approved, 48 h clock, approval-rule authority, disposition location) are expressed as **configurable policy with an explicit open decision (OPD-xx)**, and the human gate for batch disposition (DR-22) is kept intact (FR-GATE-01..06). Wording: SHALL = binding on the product once approved; classification column is in the verification table.

Requirement IDs are the keys FINAL will disposition as Delivered / Changed / Deferred / Rejected / Superseded; do not renumber.

## Findings
### FF-1 Requirements register [Verified Fact where evidence column cites code/schema; otherwise Inference - see classification table]
| ID | Requirement | MoSCoW | Release | Stage 3 trace (BR / SUC / NFR) | Stage 6 RC | Problem |
|---|---|---|---|---|---|---|
| FR-DEC-01 | Every case decision or state change SHALL be stored as a new immutable event carrying actor, timestamp, from-state, to-state, basis and evidence reference(s). Existing events SHALL never be updated or deleted by application code. | Must | R1 | BR-07, BR-08; SUC-02; NFR-09 | RC-1, RC-2 | P-2, P-5 |
| FR-DEC-02 | The current state of a case SHALL be reproducible from its event history, and the state of a case at any past time SHALL be reconstructable. Creation events SHALL record the state at creation, not the current state. | Must | R1 | BR-07; NFR-09, NFR-11 | RC-2 | P-2 |
| FR-DEC-03 | A reopen SHALL produce an explicit reopen event; a case SHALL NOT enter a reopened state without one. | Must | R1 | BR-07; NFR-09 | RC-2 | P-2 |
| FR-DEC-04 | Each decision event SHALL be retrievable together with the evidence relied on and its source, on request, by an authorised user. | Must | R1 | BR-07; SUC-02; JTBD-02 | RC-1 | P-2 |
| FR-DEC-05 | A transition to any state that the active closure policy (FR-POL-01) designates as a closing state SHALL be refused unless at least one evidence reference is attached or an authorised exception is recorded (actor, authority, reason). The system SHALL NOT judge evidence sufficiency; sufficiency criteria are a configurable policy (OPD-07). | Must | R1 | BR-09; SUC-01; NFR-09 | RC-1, RC-3 | P-2 |
| FR-DEC-06 | The system SHALL record, as separate timestamped facts, (a) receipt of the case, (b) operations-closed, and (c) evidence-complete, so that elapsed time can be computed under each candidate definition without designating one as 'closed'. | Must | R1 | BR-03; SUC-04, SUC-05 | RC-1, RC-3 | P-1, P-2, P-4 |
| FR-GATE-01 | No component of the product (rules, scheduler, importer, report, template, search) SHALL make, pre-fill as final, simulate as real, or auto-trigger a batch disposition, QA release or e-signature. | Must | R1 | BR-08; SUC-01; FAIL-01 | RC-1 | P-5 |
| FR-GATE-02 | The system SHALL present, read-only, an evidence pack for a case needing disposition (case, linked objects, evidence, rule trace, open findings) to an authorised human. | Must | R1 | BR-08; JTBD-08 | RC-1 | P-5 |
| FR-GATE-03 | Transitions classified as Zone H (disposition, release, e-signature, closure of a case failing the evidence rule, adoption of a definition or rule, acceptance of an exception rule) SHALL be accepted only from an authenticated human actor holding a configured authorised role; scheduler, importer and service accounts SHALL be rejected. | Must | R1 | BR-08, BR-09; NFR-07 | RC-1 | P-5 |
| FR-GATE-04 | The authorised-role holder list SHALL be configuration and SHALL ship empty; until at least one holder is configured, Zone H transitions SHALL be unavailable. No default holder SHALL be created. | Must | R1 | BR-08; DR-22 | RC-1 | P-5 |
| FR-GATE-05 | The recording mode of a disposition SHALL be a configuration choice: (a) record the human's decision as an event in this system, or (b) record only a reference to the decision held in an external system of record. The system SHALL NOT assume either; the choice is open (OPD-05). | Must | R1 | BR-08; BR-07 | RC-1 | P-5 |
| FR-GATE-06 | A reviewer SHALL be able to override, dismiss or refuse any rule-generated flag, classification or priority, with a reason recorded; the override SHALL never be blocked by the system. | Must | R1 | NFR-15; BR-08 | RC-1, RC-4 | P-5 |
| FR-POL-01 | Definitions of closed, resolved and approved SHALL be stored as versioned policy objects (candidate tags D-OPS, D-EVID, D-FIN supplied as candidates) with owner, effective date and status in {candidate, adopted, accepted-open}. The product SHALL ship with no adopted definition. Adoption SHALL be a Zone H transition. | Must | R1 | BR-01, BR-02; SUC-03, SUC-11 | RC-3 | P-1 |
| FR-POL-02 | The closure-time expectation (the '48 h' clock) SHALL be modelled as configurable policy: clock-start event, clock-stop event, duration, calendar basis. No value SHALL be adopted by default. Elapsed time against each configured candidate SHALL be reportable. | Must | R1 | BR-02, BR-03; SUC-04 | RC-3 | P-1, P-2 |
| FR-POL-03 | Every change to a policy object or rule table SHALL itself be an immutable event (who, when, old value, new value, authority reference) and SHALL be Zone H. | Must | R1 | BR-02; NFR-09 | RC-3, RC-4 | P-1 |
| FR-POL-04 | Approval and priority logic SHALL be provided by one table-driven rule service in which thresholds, regional limits, effective dates, owner and default behaviour are data, not code. The three as-found implementations SHALL be loadable as named rule sets (as-found-python, as-found-js, as-found-batch) and the active rule set SHALL be a Zone H policy choice. | Must | R1 | BR-01; DR-23 | RC-4 | P-1, P-4 |
| FR-POL-05 | The system SHALL report divergence between loaded rule sets for the same input (case or batch of cases), without resolving it. | Should | R2 | BR-01; DR-23 | RC-4 | P-1 |
| FR-POL-06 | When no rule matches (e.g. unknown region or year) the outcome SHALL carry an explicit 'defaulted' marker and reason in every output where it occurs. Whether the as-found default (999,999) is retained, changed or replaced by manual review is OPD-04 and requires HAR-06 approval; until decided, as-found behaviour is preserved AND marked. | Must | R1 | BR-01, BR-13; NFR-15 | RC-4 | P-1 |
| FR-INT-01 | Each received item SHALL be stored as received (raw content, source, schema revision, receipt time) in an append-only intake record; processing outcome SHALL be a separate record. `processing_status` SHALL NOT be overwritten in place. | Must | R1 | BR-05, BR-06; NFR-11 | RC-6 | P-3 |
| FR-INT-02 | Re-delivery of an item whose content is identical to one already processed SHALL change neither the exception queue nor any total. | Must | R1 | BR-05; SUC-07; NFR-11; FAIL-04 | RC-6 | P-3 |
| FR-INT-03 | A re-delivered item whose content DIFFERS from the processed one SHALL be quarantined as revised/conflicting and routed to a human reviewer; it SHALL NOT be discarded or auto-classified as duplicate. | Must | R1 | BR-05, BR-06; NFR-11 | RC-6 | P-3 |
| FR-INT-04 | Each item SHALL be validated against the declared source contract (integration/source-contract-v1.json) and supported schema revisions (1.0, 1.1, 2.0; unsupported revisions explicit). Invalid items SHALL be stored in quarantine with a reason code, not merely counted. | Must | R1 | BR-04, BR-06; NFR-11 | RC-6 | P-3 |
| FR-INT-05 | Each external item SHALL be matched to exactly one core case or flagged unmatched before reaching a reviewer queue; ambiguous (multiple) matches SHALL be flagged, never attached silently. | Must | R1 | BR-04; SUC-06 | RC-6, RC-7 | P-3 |
| FR-INT-06 | Every exception SHALL carry an enumerated reason code and queue; classification SHALL be rule-based and deterministic (touchpoint T2). | Must | R1 | BR-04, BR-05; NFR-15 | RC-6 | P-3 |
| FR-INT-07 | Inbound text (feed notes, document bodies, emails) SHALL be treated strictly as data: no inbound string SHALL alter a status, priority, queue, approval or disposition. | Must | R1 | NFR-13; BR-08 | RC-6 | P-5 |
| FR-INT-08 | Delayed, missing or revised items SHALL be detectable and attributable to source and time without manual spreadsheet reconciliation. | Should | R2 | BR-06; SUC-08 | RC-5, RC-6 | P-3 |
| FR-ID-01 | The system SHALL maintain an explicit crosswalk linking case, batch, deviation, CAPA and feed reference, each link recording key used, creator (rule or human) and time. | Must | R1 | BR-04; BR-07 | RC-7 | P-3 |
| FR-ID-02 | Orphans SHALL remain orphans: no link SHALL be created by guessing or similarity. A human MAY create a link; that is recorded as an event. | Must | R1 | BR-04; NFR-15 | RC-7 | P-3 |
| FR-ID-03 | The system SHALL surface, as findings and without auto-correction, cross-object state combinations that a configured consistency rule marks contradictory (e.g. a case closed while a linked batch is on hold). The rule set is policy (RC-3); none ships adopted. | Should | R2 | BR-01, BR-09 | RC-7, RC-3 | P-1 |
| FR-ID-04 | A read-only joined view SHALL let an investigator see all linked objects for any identifier (touchpoint T5, deterministic). | Should | R2 | BR-07 | RC-7 | P-3 |
| FR-RUN-01 | Reconcile/import runs SHALL be executable on a configured schedule and on authorised manual trigger. Whether a deterministic scheduler is an 'automated action' under HAR-10 is OPD-11. | Must | R1 | BR-06; NFR-02 | RC-5 | P-3 |
| FR-RUN-02 | Every run SHALL write a run record: start/end, trigger, inputs seen, outcomes by type, errors, and whether a capacity limit was reached. | Must | R1 | BR-06; NFR-14 | RC-5 | P-3 |
| FR-RUN-03 | No silent capacity cap SHALL exist: when work remains after a run it SHALL be reported as outstanding backlog and resumed from a checkpoint. | Must | R1 | BR-06, BR-12 | RC-5 | P-3 |
| FR-MET-01 | Every reported figure involving closed, resolved, approved, cost or handling time SHALL display the definition tag and policy version it uses. | Must | R1 | BR-01; SUC-03 | RC-3, RC-8 | P-1, P-4 |
| FR-MET-02 | The system SHALL refuse to combine, sum or compare figures carrying different definition tags in one calculation or one table, unless presented side by side explicitly labelled. | Must | R1 | BR-01; FAIL-02 | RC-3, RC-8 | P-1, P-4 |
| FR-MET-03 | Time to close SHALL be reported as median and 90th percentile separately under each configured candidate definition. | Must | R1 | BR-03; SUC-04 | RC-3 | P-2, P-4 |
| FR-MET-04 | Month-end totals SHALL be computed by one documented query/function on one configured cut-off and denominator, with no join fan-out; money SHALL use exact decimal arithmetic; unparsable amounts SHALL be surfaced as errors, not skipped. | Must | R1 | BR-10; SUC-10; NFR-16 | RC-8 | P-4 |
| FR-MET-05 | Backlog ageing and unresolved-exception rate SHALL be reported per site on one declared definition. | Should | R1 | BR-12; SUC-09 | RC-7, RC-3 | P-4 |
| FR-MET-06 | Each KPI SHALL document its window, denominator and exclusions, and SHALL be reproducible from them; every KPI computed from synthetic data SHALL be labelled 'synthetic, unvalidated'. | Must | R1 | NFR-16; FAIL-03, FAIL-05 | RC-8 | P-4 |
| FR-MET-07 | Unmatched-reference rate and reconciliation delay SHALL be reported per source. | Should | R2 | BR-06; SUC-06, SUC-08 | RC-5, RC-6 | P-3 |
| FR-MET-08 | Case cost and avoidable rework SHALL be attributable per case and per period on the agreed cut-off. | Could | R2 | BR-10 | RC-8 | P-4 |
| FR-REV-01 | For triage outcomes the system SHALL display a rule-trace explanation generated from the rule table inputs (touchpoint T1), identifying rule set, rule row and inputs. | Should | R1 | NFR-15; BR-07 | RC-4 | P-2 |
| FR-REV-02 | Reviewers SHALL have an exception queue view with reason codes, source, receipt time and age. | Must | R1 | BR-04, BR-12; JTBD-01 | RC-6 | P-3 |
| FR-REV-03 | Keyword and field search (e.g. SQLite FTS5 or equivalent) SHALL retrieve evidence documents by text and by reference, doc_id, locale, version and effective date (touchpoint T3). No generated answers. | Should | R2 | BR-07; RQ-1 baseline | RC-1 (enabling) | P-2 |
| FR-REV-04 | A structured, templated form for deviation/CAPA narrative fields MAY be provided; the author writes and signs (touchpoint T4). | Could | R2 | BR-07 | RC-1 (enabling) | P-2 |
| FR-SEC-01 | All read and write paths to case data SHALL require authentication and role-based authorisation; roles SHALL include at least reviewer, quality lead, compliance, finance (read), integration, and authorised dispositioner. | Must | R1 | NFR-07 | RC-1 (enabling) | P-2, P-5 |
| FR-SEC-02 | Every decision event, policy change, Zone H transition and authorisation failure SHALL be written to a tamper-evident audit trail. | Must | R1 | NFR-09 | RC-1, RC-2 | P-2 |
| FR-SEC-03 | Sensitive/identifying fields SHALL be handled per docs/00-preflight/operating-contract/data-use-constraints.md; access levels SHALL be enforced. | Should | R2 | NFR-12 | - | P-2 |
| FR-CO-01 | As-found behaviour captured in the Stage 7 characterisation baseline SHALL remain reproducible; any intended deviation SHALL be listed, justified and approved (HAR-06) before release. | Must | R1 | BR-13; BR-11 | RC-4, RC-8 | P-1 |
| FR-CO-02 | The legitimate parallel workflow for older customers SHALL NOT be changed or retired by this product; its owner is Unknown. | Must | R1 | BR-11 | - | P-1 |
| FR-CO-03 | Each release SHALL have a tested rollback procedure and SHALL pass the replay-safety check (FR-INT-02) as a release gate. | Should | R1 | BR-13; SH-04 | RC-6 | P-3 |
| FR-CO-04 | The product SHALL contain no AI, LLM or ML call and SHALL perform no model-inference egress. Any change requires a new Stage 8 qualification and Dinesh approval. | Must | R1 | OD-08; BR-AI-1..BR-AI-7; HAR-10 | - | P-5 |

### FF-2 Evidence, verification and classification
| ID | Repository / document evidence | Verification method | Classification |
|---|---|---|---|
| FR-DEC-01 | Test: write N transitions, assert N events, no row mutated; attempted UPDATE/DELETE via application path rejected | Verified Fact (gap) / Inference (design) |
| FR-DEC-02 | Replay test: fold events -> equals stored state for 100% of cases; as-of query returns historical state | Verified Fact (gap) |
| FR-DEC-03 | Invariant check: count(REOPENED cases without reopen event) = 0 | Verified Fact (gap) |
| FR-DEC-04 | Sample audit: evidence + source present for 100% of sampled decisions | Verified Fact (need) |
| FR-DEC-05 | Test: closing transition without evidence and without exception is refused; with exception is accepted and flagged | Verified Fact (stated need); structural-presence default is an Assumption (A-09-03) |
| FR-DEC-06 | Two distinct elapsed-time measures computed on the same population | Inference |
| FR-GATE-01 | Unsafe action count = 0 over the evaluation window; negative tests (CT-16 guard) pass | Verified Fact (constraint) |
| FR-GATE-02 | Walk-through: pack shows all linked evidence; no write control is pre-selected | Inference |
| FR-GATE-03 | Negative test per Zone H transition with a service actor: rejected and logged | Verified Fact (boundary, proposed) |
| FR-GATE-04 | Fresh install: Zone H transitions refused until holder configured | Verified Fact (gap) |
| FR-GATE-05 | Both modes exercised in test; default mode = none (blocked) until configured | Unknown (location) / Inference (design) |
| FR-GATE-06 | Every rule output has an override action; override produces an event | Inference |
| FR-POL-01 | Fresh install: all definitions status candidate or accepted-open; adoption refused for service actor | Verified Fact (gap) |
| FR-POL-02 | Report shows elapsed time under >=2 candidate clocks side by side; no pass/fail verdict without an adopted policy | Verified Fact (gap) |
| FR-POL-03 | Change a threshold: event exists; service actor rejected | Inference |
| FR-POL-04 | Characterisation tests CT-01..03 reproduce each as-found rule set exactly; switching rule set is logged | Verified Fact |
| FR-POL-05 | Divergence report on the shipped 125 cases; count recorded | Inference |
| FR-POL-06 | Input with unknown region/year yields marker; outcome equals as-found golden | Verified Fact |
| FR-INT-01 | Run reconcile twice; raw rows unchanged; outcome history has both runs | Verified Fact |
| FR-INT-02 | Replay test: queue size and totals identical before/after | Verified Fact (incident) / Inference |
| FR-INT-03 | Corrected-replay fixture lands in quarantine with both versions retained | Verified Fact (mechanism) |
| FR-INT-04 | Invalid fixtures stored with reason codes; counts reconcile with quarantine rows | Verified Fact |
| FR-INT-05 | Fixture with unique, none and multiple matches yields attach/unmatched/ambiguous | Verified Fact (synthetic) |
| FR-INT-06 | 100% of exceptions have a reason code; same input -> same code | Verified Fact (synthetic) |
| FR-INT-07 | Injection fixture set (planted strings): 0 effects on any decision field | Verified Fact |
| FR-INT-08 | Delay report per source; manual step count recorded | Inference |
| FR-ID-01 | Every link has key + creator + time; lookup by any id returns linked set | Verified Fact (schema) |
| FR-ID-02 | Orphan fixture stays unlinked after all runs; manual link produces an event | Verified Fact (guardrail) |
| FR-ID-03 | Findings listed for seeded contradictory fixture; no state changed by the check | Verified Fact (absence of constraints) |
| FR-ID-04 | Lookup by any id returns the same linked set | Inference |
| FR-RUN-01 | Scheduled run starts at configured time; manual run requires role | Verified Fact |
| FR-RUN-02 | 100% of runs have a record; reconcile totals equal run-record totals | Verified Fact |
| FR-RUN-03 | Seeded backlog larger than batch size drains with no unreported remainder | Verified Fact (mechanism) |
| FR-MET-01 | Inspect reports: 100% of such figures carry a tag | Inference |
| FR-MET-02 | Attempt to merge D-OPS and D-EVID totals is refused | Inference |
| FR-MET-03 | Report contains >=2 separate series on same population | Inference |
| FR-MET-04 | Totals equal an independently computed reference on shipped data; unparsable fixture raises error | Verified Fact |
| FR-MET-05 | Per-site table produced with definition tag | Inference |
| FR-MET-06 | 100% of KPIs have documentation; re-run reproduces value | Verified Fact (requirement) |
| FR-MET-07 | Metrics produced from intake and run records | Inference |
| FR-MET-08 | Deferred until a cost input and owner exist (OPD-08) | Unknown (inputs) |
| FR-REV-01 | Explanation text regenerates identically from stored inputs | Inference |
| FR-REV-02 | Queue shows all quarantined/unmatched items with codes | Inference |
| FR-REV-03 | Labelled question set (RQ-1) measures top-5 recall of this baseline | Inference; need for Q&A is Unknown (U-S01) |
| FR-REV-04 | Deferred; candidate for Rejected at FINAL if no stakeholder asks | Unknown |
| FR-SEC-01 | Unauthenticated request to every endpoint returns refusal | Verified Fact (gap) |
| FR-SEC-02 | Audit chain verification passes; deliberate edit is detected | Verified Fact (gap) |
| FR-SEC-03 | Access-level test per field class | Verified Fact (gap) |
| FR-CO-01 | Golden diff empty except approved deviations | Verified Fact |
| FR-CO-02 | No change to that workflow in scope; inventory has an owner field | Verified Fact (stated); owner Unknown |
| FR-CO-03 | Rollback rehearsed in sandbox; gate in release checklist | Inference |
| FR-CO-04 | Dependency and egress inspection: 0 model calls (Stage 32 tripwire) | Verified Fact (decision) |

### FF-3 Interpretation rules
- [Inference] "Configurable policy" means the product carries the *mechanism* (versioned policy objects, owner, effective date, status) and **no adopted value** for any item that DR-20/21/22/23 leave without an owner. Shipping a default would silently encode a party's rule (CG-7, Stage 3).
- [Verified Fact] No requirement contains an AI capability; FR-CO-04 forbids it (`.fde/orchestrator-decisions.md` OD-08; `qualification-decision.md` QD-1).
- [Inference] Requirements that depend on an unanswered decision are still stated, but their *content* is parameterised; their acceptance tests use fixtures with explicitly configured test policy, never an adopted real one.
- [Verified Fact] Stage 3 BR-02 and BR-11 (owner decisions) and BR-10's cost half are not product functions; they appear as open decisions (OPD-01..03, OPD-15) and FR-MET-08 (deferred).

## Stage 3 BR coverage check
| BR | Covered by |
|---|---|
| BR-01 | FR-MET-01, FR-MET-02, FR-POL-04, FR-POL-05, FR-POL-06 |
| BR-02 | FR-POL-01, FR-POL-02, FR-POL-03 (mechanism); decision itself = OPD-01..03 |
| BR-03 | FR-DEC-06, FR-MET-03, FR-POL-02 |
| BR-04 | FR-INT-04, FR-INT-05, FR-INT-06, FR-ID-01, FR-ID-02, FR-REV-02 |
| BR-05 | FR-INT-01, FR-INT-02, FR-INT-03 |
| BR-06 | FR-INT-08, FR-RUN-01..03, FR-MET-07 |
| BR-07 | FR-DEC-01..04, FR-GATE-02, FR-REV-01, FR-REV-03 |
| BR-08 | FR-GATE-01..06, FR-INT-07 |
| BR-09 | FR-DEC-05, FR-GATE-03 |
| BR-10 | FR-MET-04 (totals), FR-MET-08 (cost, deferred) |
| BR-11 | FR-CO-01, FR-CO-02 |
| BR-12 | FR-MET-05, FR-RUN-03, FR-REV-02 |
| BR-13 | FR-CO-01, FR-CO-03, FR-POL-06 |

## Evidence References
Per-row evidence column; Stage 6 `confirmed-root-causes.md` CR-A; Stage 3 `business-requirements.md`, `nfrs.md`, `success-criteria.md`; Stage 8 `deterministic-vs-ai-boundaries.md` (Zones H/D/A).

## Assumptions
- A-09-01 Stage 3 BR/NFR/SUC items stand as *candidate* requirements; no stakeholder has accepted them (synthetic, unvalidated). Confirm: Engagement lead (Dinesh Naik).
- A-09-02 The R1 (MVP) / R2 (later) split is an agent proposal. Confirm: Engagement lead (Dinesh Naik).
- A-09-03 For FR-DEC-05 the structural presence of an evidence reference (not its sufficiency) is an acceptable default closure check; sufficiency is policy (OPD-07). Confirm: Engagement lead (Dinesh Naik).
- A-09-04 NFR numeric targets are archived working targets, not measured guarantees (`docs/operations-service-levels.md`). Confirm: Engagement lead (Dinesh Naik).
- A-09-05 Content statistics from the synthetic data (fixed-key feeds, short stubs) represent real content structure well enough for a No-AI product (A-08-14).
- A-09-06 The user roles in FR-SEC-01 are derived from documentary personas PER-01..PER-08, not observed users.

## Unknowns
- U-09-01 Definitions of closed/resolved/approved and the 48 h clock (OPD-01, OPD-02) - accepted open (Q-02-05 unanswered).
- U-09-02 Owner of approval-rule conflicts (OPD-04) and where batch disposition is recorded (OPD-05).
- U-09-03 Real volumes, timings, labour and cost (no production telemetry; OD-04). No benefit is quantified in this PRD.
- U-09-04 Whether any user wants natural-language document Q&A (U-S01); whether the real corpus would defeat keyword search (RQ-1..RQ-3).
- U-09-05 Retention policy (OPD-09); performance targets (OPD-14); owner of the parallel legacy-customer workflow (OPD-15).

## Unresolved Issues
- FR-GATE-05, FR-POL-01/02/04/06, FR-DEC-05 are parameterised on open decisions OPD-01..07; they cannot be fully specified until Dinesh decides or records 'accepted open'.
- FR-REV-04 and FR-MET-08 have the weakest traces; candidates for Rejected/Deferred at FINAL.

## Residual Risks
- Reader may treat SHALL statements as agreed policy; they are candidates.
- R1 depends on a decision write path that is net-new and regulated-adjacent (highest change risk in `repo-transformation-readiness.md`).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Initial PRD v0.1). |
