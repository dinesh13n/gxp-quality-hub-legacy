---
stage: "9 — Initial PRD / Product Intent"
artifact: "mvp-scope.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/success-criteria.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/08-ai-qualification/qualification-decision.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Approval of this PRD is Dinesh Naik's decision (HAR-11); nothing here is an approval.**

**MVP = Release 1 (R1): 43 functional requirements and 17 NFRs.** R1 is the *smallest set that is safe and that removes the structurally confirmed defects (RC-1, RC-2, RC-5, RC-6, RC-7, RC-8) while leaving RC-3 and RC-4 as explicit configurable policy.* 9 functional requirements and 3 NFRs are deferred to R2. Everything is No-AI. The R1/R2 split is an agent proposal (A-09-02, OPD-13).

## Findings
### MV-1 MVP selection principles
1. [Inference] **Safety first**: nothing ships that could touch the human gate (FR-GATE-01..06 are all R1; the role-holder list ships empty).
2. [Inference] **Fix what is confirmed, parameterise what is not**: RC-1/2/5/6/7/8 are High-confidence engineering defects (Stage 6 CR-D); RC-3/RC-4 are decisions, so only the mechanism ships.
3. [Inference] **Measurability before improvement**: K-04/K-05 are unmeasurable today (OD-07); R1 must produce the timestamps and keys that make a baseline possible (FR-DEC-06, FR-ID-01).
4. [Inference] **Defer anything whose need is weakly evidenced**: document search (U-S01), templates (no workflow), cost attribution (no cost source).
5. [Verified Fact] **Sandbox only**: every acceptance run executes in a full repo copy (OD-03a).

### MV-2 In MVP (R1) - functional
| ID | Capability | MoSCoW | Requirement (abridged) |
|---|---|---|---|
| FR-DEC-01 | CAP-01 | Must | Every case decision or state change SHALL be stored as a new immutable event carrying actor, timestamp, from-s... |
| FR-DEC-02 | CAP-01 | Must | The current state of a case SHALL be reproducible from its event history, and the state of a case at any past... |
| FR-DEC-03 | CAP-01 | Must | A reopen SHALL produce an explicit reopen event; a case SHALL NOT enter a reopened state without one. |
| FR-DEC-04 | CAP-01 | Must | Each decision event SHALL be retrievable together with the evidence relied on and its source, on request, by a... |
| FR-DEC-05 | CAP-01 | Must | A transition to any state that the active closure policy (FR-POL-01) designates as a closing state SHALL be re... |
| FR-DEC-06 | CAP-01 | Must | The system SHALL record, as separate timestamped facts, (a) receipt of the case, (b) operations-closed, and (c... |
| FR-GATE-01 | CAP-02 | Must | No component of the product (rules, scheduler, importer, report, template, search) SHALL make, pre-fill as fin... |
| FR-GATE-02 | CAP-02 | Must | The system SHALL present, read-only, an evidence pack for a case needing disposition (case, linked objects, ev... |
| FR-GATE-03 | CAP-02 | Must | Transitions classified as Zone H (disposition, release, e-signature, closure of a case failing the evidence ru... |
| FR-GATE-04 | CAP-02 | Must | The authorised-role holder list SHALL be configuration and SHALL ship empty; until at least one holder is conf... |
| FR-GATE-05 | CAP-02 | Must | The recording mode of a disposition SHALL be a configuration choice: (a) record the human's decision as an eve... |
| FR-GATE-06 | CAP-02 | Must | A reviewer SHALL be able to override, dismiss or refuse any rule-generated flag, classification or priority, w... |
| FR-POL-01 | CAP-03 | Must | Definitions of closed, resolved and approved SHALL be stored as versioned policy objects (candidate tags D-OPS... |
| FR-POL-02 | CAP-03 | Must | The closure-time expectation (the '48 h' clock) SHALL be modelled as configurable policy: clock-start event, c... |
| FR-POL-03 | CAP-03 | Must | Every change to a policy object or rule table SHALL itself be an immutable event (who, when, old value, new va... |
| FR-POL-04 | CAP-03 | Must | Approval and priority logic SHALL be provided by one table-driven rule service in which thresholds, regional l... |
| FR-POL-06 | CAP-03 | Must | When no rule matches (e.g. unknown region or year) the outcome SHALL carry an explicit 'defaulted' marker and... |
| FR-INT-01 | CAP-04 | Must | Each received item SHALL be stored as received (raw content, source, schema revision, receipt time) in an appe... |
| FR-INT-02 | CAP-04 | Must | Re-delivery of an item whose content is identical to one already processed SHALL change neither the exception... |
| FR-INT-03 | CAP-04 | Must | A re-delivered item whose content DIFFERS from the processed one SHALL be quarantined as revised/conflicting a... |
| FR-INT-04 | CAP-04 | Must | Each item SHALL be validated against the declared source contract (integration/source-contract-v1.json) and su... |
| FR-INT-05 | CAP-04 | Must | Each external item SHALL be matched to exactly one core case or flagged unmatched before reaching a reviewer q... |
| FR-INT-06 | CAP-04 | Must | Every exception SHALL carry an enumerated reason code and queue; classification SHALL be rule-based and determ... |
| FR-INT-07 | CAP-04 | Must | Inbound text (feed notes, document bodies, emails) SHALL be treated strictly as data: no inbound string SHALL... |
| FR-ID-01 | CAP-05 | Must | The system SHALL maintain an explicit crosswalk linking case, batch, deviation, CAPA and feed reference, each... |
| FR-ID-02 | CAP-05 | Must | Orphans SHALL remain orphans: no link SHALL be created by guessing or similarity. A human MAY create a link; t... |
| FR-RUN-01 | CAP-06 | Must | Reconcile/import runs SHALL be executable on a configured schedule and on authorised manual trigger. Whether a... |
| FR-RUN-02 | CAP-06 | Must | Every run SHALL write a run record: start/end, trigger, inputs seen, outcomes by type, errors, and whether a c... |
| FR-RUN-03 | CAP-06 | Must | No silent capacity cap SHALL exist: when work remains after a run it SHALL be reported as outstanding backlog... |
| FR-MET-01 | CAP-07 | Must | Every reported figure involving closed, resolved, approved, cost or handling time SHALL display the definition... |
| FR-MET-02 | CAP-07 | Must | The system SHALL refuse to combine, sum or compare figures carrying different definition tags in one calculati... |
| FR-MET-03 | CAP-07 | Must | Time to close SHALL be reported as median and 90th percentile separately under each configured candidate defin... |
| FR-MET-04 | CAP-07 | Must | Month-end totals SHALL be computed by one documented query/function on one configured cut-off and denominator,... |
| FR-MET-05 | CAP-07 | Should | Backlog ageing and unresolved-exception rate SHALL be reported per site on one declared definition. |
| FR-MET-06 | CAP-07 | Must | Each KPI SHALL document its window, denominator and exclusions, and SHALL be reproducible from them; every KPI... |
| FR-REV-01 | CAP-08 | Should | For triage outcomes the system SHALL display a rule-trace explanation generated from the rule table inputs (to... |
| FR-REV-02 | CAP-08 | Must | Reviewers SHALL have an exception queue view with reason codes, source, receipt time and age. |
| FR-SEC-01 | CAP-09 | Must | All read and write paths to case data SHALL require authentication and role-based authorisation; roles SHALL i... |
| FR-SEC-02 | CAP-09 | Must | Every decision event, policy change, Zone H transition and authorisation failure SHALL be written to a tamper-... |
| FR-CO-01 | CAP-10 | Must | As-found behaviour captured in the Stage 7 characterisation baseline SHALL remain reproducible; any intended d... |
| FR-CO-02 | CAP-10 | Must | The legitimate parallel workflow for older customers SHALL NOT be changed or retired by this product; its owne... |
| FR-CO-03 | CAP-10 | Should | Each release SHALL have a tested rollback procedure and SHALL pass the replay-safety check (FR-INT-02) as a re... |
| FR-CO-04 | CAP-10 | Must | The product SHALL contain no AI, LLM or ML call and SHALL perform no model-inference egress. Any change requir... |

### MV-3 In MVP (R1) - NFRs
- PNFR-01 Availability (99.5% scheduled-hour availability)
- PNFR-02 Timeliness (By 06:00 local business time, 100% of scheduled nights in window)
- PNFR-05 Recovery (RTO 8 h; RPO 24 h (older planning assumptions); restore rehearsal passes with checksum match)
- PNFR-06 Performance (UNKNOWN target: R1 must MEASURE p50/p95 latency on the 125-case baseline and report; target set at Stage 11 (OPD-14))
- PNFR-07 Security: access (100% of endpoints authenticated and authorised; 0 anonymous reads/writes of case data in test)
- PNFR-08 Security: transport/secrets (Secret scan finds 0; any non-loopback binding uses TLS and requires HAR-05)
- PNFR-09 Compliance: audit (100% of decision events with actor/time/basis; audit-chain verification passes; deliberate tamper detected)
- PNFR-10 Compliance: retention (0 deletions of case/evidence records while no retention policy is adopted (OPD-09))
- PNFR-11 Data integrity (0 duplicate effects over replay suite; 0 silent overwrites; 0 lost raw items (raw count = received count))
- PNFR-13 Untrusted content (0 effects on decision fields from the planted-string fixture set (86 feed rows; 22 document bodies; 44 regex hits))
- PNFR-14 Observability (100% of runs have run records; every R1 KPI has a computed metric)
- PNFR-15 Usability / safety (100% of rule outputs show rule trace and offer override with reason)
- PNFR-16 Metric auditability (100% of KPIs documented; re-run gives identical value)
- PNFR-17 Determinism (Identical input -> bit-identical output; characterisation goldens pass; 0 randomness in core paths)
- PNFR-18 No AI (0 model calls; 0 model-inference egress; Stage 32 tripwire = 0)
- PNFR-19 Change safety (Rollback rehearsed; replay-safety gate passes before each release)
- PNFR-20 Honest labelling (100% of KPI outputs and reports labelled 'synthetic, unvalidated' while data is synthetic)

### MV-4 Deferred to R2 (not in MVP)
| ID | Capability | MoSCoW | Requirement (abridged) |
|---|---|---|---|
| FR-POL-05 | CAP-03 | Should | The system SHALL report divergence between loaded rule sets for the same input (case or batch of cases), witho... |
| FR-INT-08 | CAP-04 | Should | Delayed, missing or revised items SHALL be detectable and attributable to source and time without manual sprea... |
| FR-ID-03 | CAP-05 | Should | The system SHALL surface, as findings and without auto-correction, cross-object state combinations that a conf... |
| FR-ID-04 | CAP-05 | Should | A read-only joined view SHALL let an investigator see all linked objects for any identifier (touchpoint T5, de... |
| FR-MET-07 | CAP-07 | Should | Unmatched-reference rate and reconciliation delay SHALL be reported per source. |
| FR-MET-08 | CAP-07 | Could | Case cost and avoidable rework SHALL be attributable per case and per period on the agreed cut-off. |
| FR-REV-03 | CAP-08 | Should | Keyword and field search (e.g. SQLite FTS5 or equivalent) SHALL retrieve evidence documents by text and by ref... |
| FR-REV-04 | CAP-08 | Could | A structured, templated form for deviation/CAPA narrative fields MAY be provided; the author writes and signs... |
| FR-SEC-03 | CAP-09 | Should | Sensitive/identifying fields SHALL be handled per docs/00-preflight/operating-contract/data-use-constraints.md... |

R2 NFRs: PNFR-03, PNFR-04, PNFR-12.

### MV-5 MVP boundary conditions
- **In**: append-only decision/evidence record; human gate mechanism; policy objects (no adopted default); one rule service with three as-found rule sets; non-destructive idempotent intake with quarantine; crosswalk; scheduled runs with run records; definition-tagged metrics and corrected month-end totals; exception queue; authentication, authorisation and audit; coexistence guards; zero-AI tripwire.
- **Out**: all items in `non-goals.md`.
- **Dataset**: shipped 125 cases, seed 4100 (OD-09). No claim is made about any 6,000-case dataset.
- **Environment**: loopback only; sandbox copy for all runs; no Docker/Compose without HAR-05.
- **Exit test for MVP**: the release hypotheses in `release-hypothesis.md` (RH-1..RH-7) are each supported or falsified with recorded evidence.

### MV-6 MVP minimality vs value [Inference]
Cutting any of these makes R1 unsafe or unmeasurable: FR-DEC-01/02/04/06, FR-GATE-01/03/04, FR-INT-01..03, FR-ID-01, FR-RUN-02, FR-MET-01/04/06, FR-SEC-01/02. Items marked Should in R1 (FR-REV-01, FR-MET-05, FR-CO-03) are the first candidates to cut if effort exceeds budget; effort is Unknown (U-08-09).

## Evidence References
`docs/09-initial-prd/functional-requirements.md`; `docs/09-initial-prd/nfrs.md`; `docs/06-root-cause/confirmed-root-causes.md` CR-D; `docs/07-repo-assessment/repo-transformation-readiness.md`.

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
- Build effort for R1 is Unknown (U-08-09); re-estimate at Stage 13.
- MVP excludes any user-facing validation (no users).

## Residual Risks
- R1 is large for a single engineer; the net-new decision write path carries the highest change risk.
- MVP may be reshaped by OPD-05 (system of record vs mirror).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Initial PRD v0.1). |
