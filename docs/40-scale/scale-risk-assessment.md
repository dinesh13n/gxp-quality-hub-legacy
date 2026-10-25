---
stage: "40 — Scale / 90-Day Transformation Roadmap"
artifact: "scale-risk-assessment.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 40 run)"
status: "DRAFT"
evidence_sources: ["docs/24-security-privacy/residual-security-risks.md (RS-01..RS-16)", "docs/25-governance/risk-acceptance-register.md (RP-01..RP-12)", "docs/33-vendor-risk/vendor-risk-acceptance.md (VA-01..VA-07)", "docs/26-tevv/residual-tevv-risks.md (RTR-01..RTR-15)", "docs/29-incident-bcdr/incident-readiness.md", "docs/36-roi/payback-analysis.md", "docs/37-operating-model/", "docs/40-scale/reuse-readiness-assessment.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. PROPOSAL. No value claim (Stage 36: ROI NOT COMPUTABLE), no cutover scheduled. Only Dinesh Naik can accept a risk (HAR-11, TP-14); this file accepts none, and the existing registers (RS-01..16, RP-01..12, VA-01..07, RTR-01..15, F-xx) stay open. Likelihood and impact are ordinal agent Inference.**

## Summary
Sixteen scale risks. **Four are High likelihood and High impact** (SR-01, SR-02, SR-06, SR-07) **and five more are gate-blocking by construction** (SR-05, SR-08, SR-09, SR-10, SR-11). The dominant themes: (1) over-reading evidence (a structural reuse tier read as proof; a default read as a decision; a parity result read as improvement); (2) a single human decider and vacant roles; (3) controls that exist but are not wired or not held by anyone; (4) data and exposure decisions that must precede real data. Each risk is tied to the gate that must close it in `90-day-roadmap.md`. These are *proposed* new entries; routing them into the Stage 25 register is a Dinesh decision (SB-38).

## Findings
| ID | Risk | Evidence | L | I | Gate that must close or contain it | Mitigation (proposal) | Owner role | Confidence |
|---|---|---|---|---|---|---|---|---|
| SR-01 | A tier-A/B 'reusable' label is read as 'proven'; scale proceeds on structure, not on a second use | E3 = 0 (`reusable-components.md`) | H | H | G2, G3 | Keep E-grade on every claim; require a real second-unit run before E3 | Dinesh | High |
| SR-02 | Agent defaults (OD-32) are treated as approved decisions; thresholds, SLOs, retries, RTO/RPO scale as 'agreed' | OD-32..OD-36: all numerics are AGENT ASSUMPTIONS | H | H | G0 | Disposition each default explicitly (SB-02); X-06 list not copied | Dinesh | High |
| SR-03 | Roadmap or adjacent list read as demand or value; economics treated as proven | ROI NOT COMPUTABLE; 0 verified benefits; no sponsor | M | H | G0, G2 | Fixed labels in every Stage 40 file; no value figure; Stage 42/FINAL carry 'unproven' | Dinesh | High |
| SR-04 | First-use-case debt copied into new units (rule sets, goldens, proxies, hold-all retention, single approver) | RC-4 X-01..X-11 | M | H | every scale step | Non-carry checklist SB-40 as an entry criterion | Dinesh | Medium |
| SR-05 | Control present but inert at scale: Zone H with no holder, rule sets with no owner, resilience/observability not wired | `zone_h.holders` empty; D-28-01/02; D-31 | H | M | G1 | Name holders or declare unused; wire or record 'not used' | Dinesh | High |
| SR-06 | Single-person bottleneck: one named human decides, reviews and approves; capacity and key-person risk | OD-04; DQ-17 (accepted for the engagement, OD-30; RP-01 open); DS-3 (one reviewer) | H | H | G0, every gate | Sequence decisions; do not parallelise scale steps; name second approver or accept single-approver explicitly (PC-3) | Dinesh | High |
| SR-07 | Vacant ownership at scale: nobody answers incidents, owns cost, rules, data | 0 of 28 assets accepted; RL-02..RL-11 VACANT | H | H | G1 (pilot), G3 (broader) | SB-05..SB-07, SB-31 before pilot | Dinesh | High |
| SR-08 | Real data arrives before field classes, tenant, regime and retention are decided | DQ-S24; OD-S12-09; GD-07 | M | H | G1 | SB-21 is a G1 exit criterion | Dinesh | Medium |
| SR-09 | Exposure beyond loopback without TLS, second factor, token expiry, off-device backup | PR-06, PR-07, PR-14, PR-25; RS-01, RS-02, RS-08 | M | H | G1 (if exposure intended) | SB-20 decision; do not widen exposure until closed | Dinesh | High |
| SR-10 | Runtime support: Python 3.10 end of life; no 3.12+ evidence; goldens bound to 3.10.12 | PR-28, PR-29, RTR-08, OD-23, OD-24 | H | M | G1 | SB-08, SB-12 | Dinesh / orchestrator | High |
| SR-11 | Value cannot be shown inside the pilot window (month-end, persistence need a full after-window; window length undecided) and the decision to continue is made without it | PC-1, I-02, D-34-02; K-10 month-end | H | M | G2 | Decide window before pilot (SB-27); permit 'proceed on non-economic grounds' only as Dinesh's explicit, recorded decision | Dinesh | Medium |
| SR-12 | Scale outgrows verification: group C ~145 s of 180 s cap; 12-mutant sample; agent-run red team only; walkthroughs unsigned | OD-21; RTR-13, RTR-14, RTR-07 | M | M | G1 | SB-11, SB-12, SB-14, SB-15 | Dinesh / orchestrator | Medium |
| SR-13 | Audit and data growth under hold-all retention and unauthenticated traffic | RTR-12 (81 bytes/request); OD-S12-09 | L | M | G2 | Retention rule; restore drill; rate-limit review (A-27-04) | Dinesh | Low-Medium |
| SR-14 | Contract drift per source: `record_only` hides breakage; schema_version allow-list open; late deliveries | OD-28; U-28-01 | M | M | G2 for AU-02 | Per-source contracts (SB-22); decide when to use `enforce` | Dinesh (source owner VACANT) | Medium |
| SR-15 | No-AI invariant breaks as scope grows (AU-07, vendor features) | OD-08; INV-01/02 | L | H | any new unit | Keep tripwires; AU-07 needs a new decision | Dinesh | High |
| SR-16 | Currency: roadmap goes stale as Stage 39 (drift) and Stages 30/38 land and v0.2 of Stages 34/35/36 are produced | U-40-09; OD-36 | H | M | G0, G2 | Re-issue triggers (SG-7); this file is v0.1 | Dinesh | High |

**Heat summary [Verified Fact: count of table]:** High-impact with High likelihood: SR-01, SR-02, SR-06, SR-07 (4); gate-blocking by construction: SR-05, SR-08, SR-09, SR-10, SR-11 (conditions in G1/G2).

## Evidence References
Per-row. Registers in `docs/24-security-privacy/`, `docs/25-governance/`, `docs/26-tevv/`, `docs/33-vendor-risk/`.

## Assumptions
- A-40-09 [Assumption] Ordinal L/I are the agent's reading; Dinesh may re-rate (as RTR-15).

## Unknowns
- U-40-11 Real volumes, concurrency and source behaviour (SR-13, SR-14).
- U-40-12 Hosting, if any, and its terms (OB-07).

## Unresolved Issues
- None of RS/RP/VA/RTR/F-xx are accepted, fixed or routed by this stage; the roadmap only sequences their disposition (SB-02).

## Residual Risks
- All of SR-01..SR-16 remain open after this stage.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue |
