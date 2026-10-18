---
stage: "9 — Initial PRD / Product Intent"
artifact: "initial-prd-traceability.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/success-criteria.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/08-ai-qualification/qualification-decision.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/03-problem-value/problem-statement.md", "docs/02-stakeholders/decision-rights-map.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Approval of this PRD is Dinesh Naik's decision (HAR-11); nothing here is an approval.**

Two-way trace: every one of the 52 functional requirements and 20 NFRs traces to a Stage 3 problem element (P-1..P-5, frozen in `problem-statement.md`), to Stage 3 BR/SUC/NFR IDs, to Stage 6 root causes (RC-1..RC-8) where applicable, and to repository or document evidence. Reverse coverage shows every Stage 3 BR, SUC, NFR, problem and every Stage 6 RC maps to at least one requirement, or is listed as uncovered. Trace is generated from the requirement register, so the register and this file cannot disagree.

Uncovered check: BR: None. | SUC: None. | RC: None. | P: None. | Stage 3 NFR: None.

## Findings
### TR-1 Forward trace: functional requirement -> problem -> BR -> SUC/NFR -> RC -> evidence
| FR | Problem | Stage 3 BR | Stage 3 SUC / NFR | Stage 6 RC | Evidence |
|---|---|---|---|---|---|
| FR-DEC-01 | P-2, P-5 | BR-07, BR-08 | SUC-02, NFR-09 | RC-1, RC-2 | app/generate.py:37 is the only writer of `cases`; app/server.py is GET-only; only 2 event types exist (docs/06-root-cause/confirmed-root-causes.md RC-1, RC-2) |
| FR-DEC-02 | P-2 | BR-07 | NFR-09, NFR-11 | RC-2 | cases.version=1 for 125/125; creation event stores current status 125/125 (RC-2, V-02 PASS) |
| FR-DEC-03 | P-2 | BR-07 | NFR-09 | RC-2 | 8 REOPENED cases have 0 reopen events (RC-2) |
| FR-DEC-04 | P-2 | BR-07 | SUC-02 | RC-1 | docs/domain-assurance.md ('source attribution for each decision'); docs/03-problem-value/business-requirements.md BR-07 |
| FR-DEC-05 | P-2 | BR-09 | SUC-01, NFR-09 | RC-1, RC-3 | docs/correspondence/operations-vs-risk-2024.md (no automatic closure without verifiable evidence); BR-09 wording preserves the unowned decision (A-03-10) |
| FR-DEC-06 | P-1, P-2, P-4 | BR-03 | SUC-04, SUC-05 | RC-1, RC-3 | K-04/K-05 unmeasurable because no closure/evidence timestamps exist (.fde/orchestrator-decisions.md OD-07) |
| FR-GATE-01 | P-5 | BR-08 | SUC-01 | RC-1 | docs/domain-assurance.md; HAR-12; STOP-07 (docs/00-preflight/operating-contract/); DR-22 |
| FR-GATE-02 | P-5 | BR-08 | - | RC-1 | docs/03-problem-value/jobs-to-be-done.md JTBD-08 |
| FR-GATE-03 | P-5 | BR-08, BR-09 | NFR-07 | RC-1 | docs/08-ai-qualification/deterministic-vs-ai-boundaries.md B-1 Zone H |
| FR-GATE-04 | P-5 | BR-08 | - | RC-1 | DR-22 GAP: holder unnamed (docs/02-stakeholders/decision-rights-map.md) |
| FR-GATE-05 | P-5 | BR-07, BR-08 | - | RC-1 | U-05-02 where batch_disposition is recorded (docs/05-current-state/current-process-map.md L77); QD-5 DN-4 |
| FR-GATE-06 | P-5 | BR-08 | NFR-15 | RC-1, RC-4 | docs/03-problem-value/nfrs.md NFR-15 |
| FR-POL-01 | P-1 | BR-01, BR-02 | SUC-03, SUC-11 | RC-3 | DR-20/DR-23 GAPs; docs/03-problem-value/success-criteria.md (candidate definitions); RC-3 'never formalized' |
| FR-POL-02 | P-1, P-2 | BR-02, BR-03 | SUC-04 | RC-3 | docs/correspondence/operations-vs-risk-2024.md; DR-20 |
| FR-POL-03 | P-1 | BR-02 | NFR-09 | RC-3, RC-4 | HAR-06, HAR-11 (provisional-human-approval-rules.md) |
| FR-POL-04 | P-1, P-4 | BR-01 | - | RC-4 | app/legacy_logic.py (>50,000); legacy_js/legacy_policy.js (regional limit x 1.05, default 999,999); legacy_batch/shift_reconciliation.py (2,500-8,500) (RC-4 V-04 PASS) |
| FR-POL-05 | P-1 | BR-01 | - | RC-4 | RC-4 outcome divergence is Inference; 0 of 125 shipped cases exceed 50,000 |
| FR-POL-06 | P-1 | BR-01, BR-13 | NFR-15 | RC-4 | legacy_js/legacy_policy.js default 999,999 (RC-4) |
| FR-INT-01 | P-3 | BR-05, BR-06 | NFR-11 | RC-6 | app/partner_feeds.py reconcile overwrites processing_status in place (RC-6 V-06 PASS) |
| FR-INT-02 | P-3 | BR-05 | SUC-07, NFR-11 | RC-6 | 2025 rollback after replay inflated queue (docs/historic-decisions.md); INC-2025-014 (operations/incidents/) |
| FR-INT-03 | P-3 | BR-05, BR-06 | NFR-11 | RC-6 | Every REPLAY becomes DUPLICATE without content comparison (RC-6) |
| FR-INT-04 | P-3 | BR-04, BR-06 | NFR-11 | RC-6 | source-contract-v1.json not enforced; invalid gateway events counted not stored (RC-6); 0A IO-03 |
| FR-INT-05 | P-3 | BR-04 | SUC-06 | RC-6, RC-7 | 8,394 of 8,567 partner-feed rows unmatched on shipped DB (generator-shaped, not a business baseline; IO-10, R-05) |
| FR-INT-06 | P-3 | BR-04, BR-05 | NFR-15 | RC-6 | Fixed 11-key feed content, 6 distinct notes (EA-2, EA-3 in qualification-decision.md) |
| FR-INT-07 | P-5 | BR-08 | NFR-13 | RC-6 | 86 feed rows and 22 of 1,200 document bodies contain instruction-like text (EA-5); STOP-05 |
| FR-INT-08 | P-3 | BR-06 | SUC-08 | RC-5, RC-6 | INC-2025-014 manual reconciliation at 04:00 UTC |
| FR-ID-01 | P-3 | BR-04, BR-07 | - | RC-7 | cases has no batch/deviation/CAPA/feed key; partner_feeds.ref_id has no FK (RC-7 V-07 PASS) |
| FR-ID-02 | P-3 | BR-04 | NFR-15 | RC-7 | Stage 6 guardrail 'must not fabricate links for orphan feeds'; O8 rejection (intervention-options.md) |
| FR-ID-03 | P-1 | BR-01, BR-09 | - | RC-3, RC-7 | five status vocabularies; no constraint across states (RC-7) |
| FR-ID-04 | P-3 | BR-07 | - | RC-7 | MH-09 cross-id lookup is manual (docs/05-current-state/manual-handoffs.md) |
| FR-RUN-01 | P-3 | BR-06 | NFR-02 | RC-5 | no scheduler anywhere in repo (RC-5 V-05 PASS) |
| FR-RUN-02 | P-3 | BR-06 | NFR-14 | RC-5 | reconcile writes no run record (RC-5) |
| FR-RUN-03 | P-3 | BR-06, BR-12 | - | RC-5 | reconcile(limit=1000) vs 8,567 backlog rows over 9 runs (RC-5) |
| FR-MET-01 | P-1, P-4 | BR-01 | SUC-03 | RC-3, RC-8 | docs/03-problem-value/business-requirements.md BR-01 |
| FR-MET-02 | P-1, P-4 | BR-01 | - | RC-3, RC-8 | SC-01, SC-02 (stakeholder-conflicts.md) |
| FR-MET-03 | P-2, P-4 | BR-03 | SUC-04 | RC-3 | SUC-04 |
| FR-MET-04 | P-4 | BR-10 | SUC-10, NFR-16 | RC-8 | SQL LEFT JOIN events inflates SUM(amount) 19.3% (742,956.61 vs 622,826.44); Java double + silent NumberFormatException skip (sql/legacy_reports.sql; legacy_java/ReconcileLegacy.java; RC-8 V-08 PASS) |
| FR-MET-05 | P-4 | BR-12 | SUC-09 | RC-3, RC-7 | docs/domain-assurance.md metric names |
| FR-MET-06 | P-4 | - | NFR-16 | RC-8 | docs/baseline-measurement-notes.md; OD-04, OD-07 |
| FR-MET-07 | P-3 | BR-06 | SUC-06, SUC-08 | RC-5, RC-6 | SUC-06, SUC-08 |
| FR-MET-08 | P-4 | BR-10 | - | RC-8 | No cost source in repo; operating_costs.total_cases is random (OD-07); U-24 |
| FR-REV-01 | P-2 | BR-07 | NFR-15 | RC-4 | app/legacy_logic.py is 8 lines over 3 inputs (EA-7) |
| FR-REV-02 | P-3 | BR-04, BR-12 | - | RC-6 | docs/03-problem-value/jobs-to-be-done.md JTBD-01 |
| FR-REV-03 | P-2 | BR-07 | - | RC-1 | 1,200 documents in data/documents/source_documents.jsonl; FTS5 present in sqlite 3.37.2 (qualification-decision.md EA-5) |
| FR-REV-04 | P-2 | BR-07 | - | RC-1 | Stage 8 T4: no workflow, no requirement; weakest trace in this PRD |
| FR-SEC-01 | P-2, P-5 | - | NFR-07 | RC-1 | API/gateway have no authentication (0A SO-01, SO-02) |
| FR-SEC-02 | P-2 | - | NFR-09 | RC-1, RC-2 | No audit mechanism in code (0A SO-09, SO-10) |
| FR-SEC-03 | P-2 | - | NFR-12 | - | SO-02 access levels unenforced |
| FR-CO-01 | P-1 | BR-11, BR-13 | - | RC-4, RC-8 | docs/07-repo-assessment/ (3 goldens, CT-01..18; 14/14 mutants killed); STOP-12 |
| FR-CO-02 | P-1 | BR-11 | - | - | SC-07; docs/legacy-operations-history.md 2024 |
| FR-CO-03 | P-3 | BR-13 | - | RC-6 | 2025 rollback (historic-decisions.md) |
| FR-CO-04 | P-5 | - | - | - | docs/08-ai-qualification/qualification-decision.md; .fde/orchestrator-decisions.md OD-08 |

### TR-2 Forward trace: NFR -> Stage 3 NFR / constraint -> evidence class
| PNFR | Trace | Evidence class | Target |
|---|---|---|---|
| PNFR-01 | NFR-01 | Assumption (archived working target, not measured; docs/operations-service-levels.md) | 99.5% scheduled-hour availability |
| PNFR-02 | NFR-02 | Assumption | By 06:00 local business time, 100% of scheduled nights in window |
| PNFR-03 | NFR-03 | Assumption | Within 4 h of source event |
| PNFR-04 | NFR-04 | Assumption | Stale signal max 24 h |
| PNFR-05 | NFR-05 | Assumption | RTO 8 h; RPO 24 h (older planning assumptions); restore rehearsal passes with checksum match |
| PNFR-06 | NFR-06 | Unknown | UNKNOWN target: R1 must MEASURE p50/p95 latency on the 125-case baseline and report; target set at Stage 11 (OPD-14) |
| PNFR-07 | NFR-07 | Verified Fact (gap) | 100% of endpoints authenticated and authorised; 0 anonymous reads/writes of case data in test |
| PNFR-08 | NFR-08 | Verified Fact (gap) | Secret scan finds 0; any non-loopback binding uses TLS and requires HAR-05 |
| PNFR-09 | NFR-09 | Verified Fact (gap) | 100% of decision events with actor/time/basis; audit-chain verification passes; deliberate tamper detected |
| PNFR-10 | NFR-10 | Unknown (policy) | 0 deletions of case/evidence records while no retention policy is adopted (OPD-09) |
| PNFR-11 | NFR-11 | Verified Fact (gap) | 0 duplicate effects over replay suite; 0 silent overwrites; 0 lost raw items (raw count = received count) |
| PNFR-12 | NFR-12 | Verified Fact (gap) | 100% of field classes covered by an access test |
| PNFR-13 | NFR-13 | Verified Fact | 0 effects on decision fields from the planted-string fixture set (86 feed rows; 22 document bodies; 44 regex hits) |
| PNFR-14 | NFR-14 | Verified Fact (gap) | 100% of runs have run records; every R1 KPI has a computed metric |
| PNFR-15 | NFR-15 | Inference | 100% of rule outputs show rule trace and offer override with reason |
| PNFR-16 | NFR-16 | Verified Fact (requirement) | 100% of KPIs documented; re-run gives identical value |
| PNFR-17 | (Zone D) deterministic-vs-ai-boundaries.md B-1; RC-4 | Inference | Identical input -> bit-identical output; characterisation goldens pass; 0 randomness in core paths |
| PNFR-18 | OD-08; HAR-10 | Verified Fact (decision) | 0 model calls; 0 model-inference egress; Stage 32 tripwire = 0 |
| PNFR-19 | BR-13 | Inference | Rollback rehearsed; replay-safety gate passes before each release |
| PNFR-20 | FAIL-05; OD-04 | Verified Fact (rule) | 100% of KPI outputs and reports labelled 'synthetic, unvalidated' while data is synthetic |

### TR-3 Reverse coverage
**Stage 3 business requirements**
| BR | Requirements |
|---|---|
| BR-01 | FR-POL-01, FR-POL-04, FR-POL-05, FR-POL-06, FR-ID-03, FR-MET-01, FR-MET-02 |
| BR-02 | FR-POL-01, FR-POL-02, FR-POL-03 |
| BR-03 | FR-DEC-06, FR-POL-02, FR-MET-03 |
| BR-04 | FR-INT-04, FR-INT-05, FR-INT-06, FR-ID-01, FR-ID-02, FR-REV-02 |
| BR-05 | FR-INT-01, FR-INT-02, FR-INT-03, FR-INT-06 |
| BR-06 | FR-INT-01, FR-INT-03, FR-INT-04, FR-INT-08, FR-RUN-01, FR-RUN-02, FR-RUN-03, FR-MET-07 |
| BR-07 | FR-DEC-01, FR-DEC-02, FR-DEC-03, FR-DEC-04, FR-GATE-05, FR-ID-01, FR-ID-04, FR-REV-01, FR-REV-03, FR-REV-04 |
| BR-08 | FR-DEC-01, FR-GATE-01, FR-GATE-02, FR-GATE-03, FR-GATE-04, FR-GATE-05, FR-GATE-06, FR-INT-07 |
| BR-09 | FR-DEC-05, FR-GATE-03, FR-ID-03 |
| BR-10 | FR-MET-04, FR-MET-08 |
| BR-11 | FR-CO-01, FR-CO-02 |
| BR-12 | FR-RUN-03, FR-MET-05, FR-REV-02 |
| BR-13 | FR-POL-06, FR-CO-01, FR-CO-03 |

**Stage 3 success criteria**
| SUC | Requirements |
|---|---|
| SUC-01 | FR-DEC-05, FR-GATE-01 |
| SUC-02 | FR-DEC-01, FR-DEC-04 |
| SUC-03 | FR-POL-01, FR-MET-01 |
| SUC-04 | FR-DEC-06, FR-POL-02, FR-MET-03 |
| SUC-05 | FR-DEC-06 |
| SUC-06 | FR-INT-05, FR-MET-07 |
| SUC-07 | FR-INT-02 |
| SUC-08 | FR-INT-08, FR-MET-07 |
| SUC-09 | FR-MET-05 |
| SUC-10 | FR-MET-04 |
| SUC-11 | FR-POL-01 |

**Stage 6 root causes**
| RC | Requirements |
|---|---|
| RC-1 | FR-DEC-01, FR-DEC-04, FR-DEC-05, FR-DEC-06, FR-GATE-01, FR-GATE-02, FR-GATE-03, FR-GATE-04, FR-GATE-05, FR-GATE-06, FR-REV-03, FR-REV-04, FR-SEC-01, FR-SEC-02 |
| RC-2 | FR-DEC-01, FR-DEC-02, FR-DEC-03, FR-SEC-02 |
| RC-3 | FR-DEC-05, FR-DEC-06, FR-POL-01, FR-POL-02, FR-POL-03, FR-ID-03, FR-MET-01, FR-MET-02, FR-MET-03, FR-MET-05 |
| RC-4 | FR-GATE-06, FR-POL-03, FR-POL-04, FR-POL-05, FR-POL-06, FR-REV-01, FR-CO-01 |
| RC-5 | FR-INT-08, FR-RUN-01, FR-RUN-02, FR-RUN-03, FR-MET-07 |
| RC-6 | FR-INT-01, FR-INT-02, FR-INT-03, FR-INT-04, FR-INT-05, FR-INT-06, FR-INT-07, FR-INT-08, FR-MET-07, FR-REV-02, FR-CO-03 |
| RC-7 | FR-INT-05, FR-ID-01, FR-ID-02, FR-ID-03, FR-ID-04, FR-MET-05 |
| RC-8 | FR-MET-01, FR-MET-02, FR-MET-04, FR-MET-06, FR-MET-08, FR-CO-01 |

**Stage 3 problem elements**
| P | Requirements |
|---|---|
| P-1 | FR-DEC-06, FR-POL-01, FR-POL-02, FR-POL-03, FR-POL-04, FR-POL-05, FR-POL-06, FR-ID-03, FR-MET-01, FR-MET-02, FR-CO-01, FR-CO-02 |
| P-2 | FR-DEC-01, FR-DEC-02, FR-DEC-03, FR-DEC-04, FR-DEC-05, FR-DEC-06, FR-POL-02, FR-MET-03, FR-REV-01, FR-REV-03, FR-REV-04, FR-SEC-01, FR-SEC-02, FR-SEC-03 |
| P-3 | FR-INT-01, FR-INT-02, FR-INT-03, FR-INT-04, FR-INT-05, FR-INT-06, FR-INT-08, FR-ID-01, FR-ID-02, FR-ID-04, FR-RUN-01, FR-RUN-02, FR-RUN-03, FR-MET-07, FR-REV-02, FR-CO-03 |
| P-4 | FR-DEC-06, FR-POL-04, FR-MET-01, FR-MET-02, FR-MET-03, FR-MET-04, FR-MET-05, FR-MET-06, FR-MET-08 |
| P-5 | FR-DEC-01, FR-GATE-01, FR-GATE-02, FR-GATE-03, FR-GATE-04, FR-GATE-05, FR-GATE-06, FR-INT-07, FR-SEC-01, FR-CO-04 |

**Stage 3 NFRs (via FR or PNFR)**
| NFR | Requirements |
|---|---|
| NFR-01 | PNFR-01 |
| NFR-02 | FR-RUN-01, PNFR-02 |
| NFR-03 | PNFR-03 |
| NFR-04 | PNFR-04 |
| NFR-05 | PNFR-05 |
| NFR-06 | PNFR-06 |
| NFR-07 | FR-GATE-03, FR-SEC-01, PNFR-07 |
| NFR-08 | PNFR-08 |
| NFR-09 | FR-DEC-01, FR-DEC-02, FR-DEC-03, FR-DEC-05, FR-POL-03, FR-SEC-02, PNFR-09 |
| NFR-10 | PNFR-10 |
| NFR-11 | FR-DEC-02, FR-INT-01, FR-INT-02, FR-INT-03, FR-INT-04, PNFR-11 |
| NFR-12 | FR-SEC-03, PNFR-12 |
| NFR-13 | FR-INT-07, PNFR-13 |
| NFR-14 | FR-RUN-02, PNFR-14 |
| NFR-15 | FR-GATE-06, FR-POL-06, FR-INT-06, FR-ID-02, FR-REV-01, PNFR-15 |
| NFR-16 | FR-MET-04, FR-MET-06, PNFR-16 |

### TR-4 Findings [Inference]
- All requirements trace to a problem (P-1..P-5). Requirements with a "-" in the RC column (FR-CO-02, FR-CO-04, FR-SEC-03) trace to Stage 3 constraints (BR-11, OD-08, NFR-12), not to a root cause; that is intentional and flagged.
- The weakest traces are FR-REV-03/04 (no stakeholder asked; Stage 8 T3/T4) and FR-MET-08 (no cost source). They are R2 and are the likeliest FINAL dispositions of Deferred or Rejected.
- Stage 3 BR-02 and BR-11 are decisions/guards and are met only by mechanism (FR-POL-01..03, FR-CO-02); they cannot reach "met" without Dinesh's recorded decision.
- Stage 6 root causes RC-3 and RC-4 are traced to *mechanism* requirements only (CR-D).

## Evidence References
`docs/03-problem-value/` (problem-statement, business-requirements, nfrs, success-criteria); `docs/06-root-cause/confirmed-root-causes.md`; per-row evidence in `functional-requirements.md`.

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
- Uncovered items, if any, are listed in the Summary line; see below for explanation.
- Traceability is to candidate, unvalidated upstream items.

## Residual Risks
- Circular evidence: Stage 3, 6, 8 and 9 share one author/approver pair (ER-11).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Initial PRD v0.1). |
