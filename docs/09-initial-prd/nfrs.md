---
stage: "9 — Initial PRD / Product Intent"
artifact: "nfrs.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/success-criteria.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/08-ai-qualification/qualification-decision.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/operations-service-levels.md", "docs/00-preflight/operating-contract/data-use-constraints.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Approval of this PRD is Dinesh Naik's decision (HAR-11); nothing here is an approval.**

20 product NFRs (PNFR-01..PNFR-20) with measurable targets, each traced to a Stage 3 NFR (NFR-01..NFR-16) or a Stage 8 / OD-08 constraint. Numeric thresholds for availability, timeliness and recovery come from archived working targets that the source itself calls "not measured guarantees" (`docs/operations-service-levels.md`); they are **Assumptions (owner Engagement lead (Dinesh Naik))**. Where no target exists (performance, retention) the NFR is stated as a *measurement or hold requirement* rather than an invented number. Compliance items are framing, not certification (A-08, DR-29).

## Findings
### NF-1 NFR register
| ID | Category | Requirement | Measurable target | Trace | Evidence class | Release |
|---|---|---|---|---|---|---|
| PNFR-01 | Availability | Case review and reconciliation available in scheduled hours | 99.5% scheduled-hour availability | NFR-01 | Assumption (archived working target, not measured; docs/operations-service-levels.md) | R1 measure; target Assumption |
| PNFR-02 | Timeliness | Overnight reconciliation completes before start of business | By 06:00 local business time, 100% of scheduled nights in window | NFR-02 | Assumption | R1 |
| PNFR-03 | Timeliness | Partner feed accepted promptly | Within 4 h of source event | NFR-03 | Assumption | R2 |
| PNFR-04 | Freshness | Risk signals not older than tolerated age | Stale signal max 24 h | NFR-04 | Assumption | R2 |
| PNFR-05 | Recovery | Service restorable from backup | RTO 8 h; RPO 24 h (older planning assumptions); restore rehearsal passes with checksum match | NFR-05 | Assumption | R1 (rehearsal) |
| PNFR-06 | Performance | Reviewer-facing retrieval and queue refresh does not impede handling | UNKNOWN target: R1 must MEASURE p50/p95 latency on the 125-case baseline and report; target set at Stage 11 (OPD-14) | NFR-06 | Unknown | R1 measure |
| PNFR-07 | Security: access | Only authenticated, authorised users read or change case data | 100% of endpoints authenticated and authorised; 0 anonymous reads/writes of case data in test | NFR-07 | Verified Fact (gap) | R1 |
| PNFR-08 | Security: transport/secrets | Data in transit protected; no secrets in source | Secret scan finds 0; any non-loopback binding uses TLS and requires HAR-05 | NFR-08 | Verified Fact (gap) | R1 |
| PNFR-09 | Compliance: audit | Every decision and state change attributable and tamper-evident (framing only, not Part 11 certification) | 100% of decision events with actor/time/basis; audit-chain verification passes; deliberate tamper detected | NFR-09 | Verified Fact (gap) | R1 |
| PNFR-10 | Compliance: retention | Retention follows a policy once decided | 0 deletions of case/evidence records while no retention policy is adopted (OPD-09) | NFR-10 | Unknown (policy) | R1 (hold-all) |
| PNFR-11 | Data integrity | Imports idempotent, contract-validated, lossless | 0 duplicate effects over replay suite; 0 silent overwrites; 0 lost raw items (raw count = received count) | NFR-11 | Verified Fact (gap) | R1 |
| PNFR-12 | Data protection | Sensitive fields handled per data-use constraints | 100% of field classes covered by an access test | NFR-12 | Verified Fact (gap) | R2 |
| PNFR-13 | Untrusted content | Inbound content never acts as instruction or approval | 0 effects on decision fields from the planted-string fixture set (86 feed rows; 22 document bodies; 44 regex hits) | NFR-13 | Verified Fact | R1 |
| PNFR-14 | Observability | Failures/delays visible with source and time correlation | 100% of runs have run records; every R1 KPI has a computed metric | NFR-14 | Verified Fact (gap) | R1 |
| PNFR-15 | Usability / safety | Humans can understand, override and refuse any flag or recommendation | 100% of rule outputs show rule trace and offer override with reason | NFR-15 | Inference | R1 |
| PNFR-16 | Metric auditability | KPIs reproducible from documented window, denominator, exclusions | 100% of KPIs documented; re-run gives identical value | NFR-16 | Verified Fact (requirement) | R1 |
| PNFR-17 | Determinism | Core decision, rule, intake and metric paths reproducible | Identical input -> bit-identical output; characterisation goldens pass; 0 randomness in core paths | (Zone D) deterministic-vs-ai-boundaries.md B-1; RC-4 | Inference | R1 |
| PNFR-18 | No AI | No model call in the product | 0 model calls; 0 model-inference egress; Stage 32 tripwire = 0 | OD-08; HAR-10 | Verified Fact (decision) | R1 |
| PNFR-19 | Change safety | Releases reversible and not causing 2025-style rollback | Rollback rehearsed; replay-safety gate passes before each release | BR-13 | Inference | R1 |
| PNFR-20 | Honest labelling | Outputs from synthetic data are labelled | 100% of KPI outputs and reports labelled 'synthetic, unvalidated' while data is synthetic | FAIL-05; OD-04 | Verified Fact (rule) | R1 |

### NF-2 Notes
- [Verified Fact] PNFR-07/08/09/11/14 close verified gaps from Stage 0A (no auth, no TLS, no audit, destructive imports, no logging). Remediation design belongs to Stages 10, 23-25; this PRD only states the target.
- [Verified Fact] PNFR-13 baseline: instruction-like strings are present in the data (86 feed rows; 22 of 1,200 document bodies; 44 regex hits across stores; `qualification-decision.md` EA-5). Even with No-AI they must not alter any decision field.
- [Inference] PNFR-17 (determinism) is the NFR that makes the No-AI decision testable: it lets Stage 7 goldens act as the regression oracle.
- [Inference] PNFR-18 exists so that Stage 32 can assert zero model-call cost as a tripwire (QD-4).
- [Unknown] PNFR-06: no latency target exists anywhere in the repo (U-03-11). R1 must measure it.

## Evidence References
`docs/03-problem-value/nfrs.md`; `docs/operations-service-levels.md`; `docs/00-preflight/discovery/security-observability-overview.md`; `docs/08-ai-qualification/deterministic-vs-ai-boundaries.md`; OD-08.

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
- PNFR-01..05 targets unvalidated (A-09-04). PNFR-06 and PNFR-10 have no number by design (OPD-14, OPD-09).

## Residual Risks
- Presenting archived 99.5%/RTO figures as measured would be false precision.
- Security NFRs (PNFR-07/08) are unmet in the shipped system (R-11 Not met); R1 cannot be exposed beyond loopback until met (HAR-05).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Initial PRD v0.1). |
