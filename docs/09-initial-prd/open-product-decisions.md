---
stage: "9 — Initial PRD / Product Intent"
artifact: "open-product-decisions.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/business-requirements.md", "docs/03-problem-value/nfrs.md", "docs/03-problem-value/success-criteria.md", "docs/06-root-cause/confirmed-root-causes.md", "docs/08-ai-qualification/qualification-decision.md", ".fde/orchestrator-decisions.md (OD-03a, OD-07, OD-08, OD-09)", "docs/00-preflight/operating-contract/open-governance-decisions.md", "docs/02-stakeholders/decision-rights-map.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository, unvalidated against any organisation. Status DRAFT: not approved. Approval of this PRD is Dinesh Naik's decision (HAR-11); nothing here is an approval.**

16 open product decisions and 2 closed decisions that shape this PRD. Owner for every open item is **Engagement lead (Dinesh Naik)** (sole approver; no other human exists). OPD-01..03 (definitions, the 48 h clock, the speed-vs-evidence decider) are **accepted open** (Q-02-05 unanswered); OPD-04 (rule authority) and OPD-05 (disposition location) are open and unanswered. For all five the PRD does not choose and expresses the matter as configurable policy. No due calendar dates are committed (no stakeholders); resolving stages are given instead. None blocks the Stage 9 gate; OPD-13 is the condition on it.

## Findings
### OD-1 Open decisions
| ID | Decision needed | Trace | Status | Requirements affected | How the PRD stays neutral | Resolving stage | Blocking? |
|---|---|---|---|---|---|---|---|
| OPD-01 | Definition of closed / resolved / approved (D-OPS, D-EVID, D-FIN or other) | RC-3; DR-20, DR-23; SC-02, SC-05; Q-02-05 | ACCEPTED OPEN (OD-09 note) | FR-POL-01, FR-MET-01..03, FR-DEC-05/06 | Product ships candidates only; every figure tagged; no adopted default | Before Stage 13 (specs) for adoption; Stage 9 proceeds open | No (stage 9) / Yes for any KPI target |
| OPD-02 | Meaning of the '48 h' clock: start event, stop event, calendar basis, and whether 48 h is right | DR-20; SC-01; Q-02-05 | ACCEPTED OPEN | FR-POL-02, FR-MET-03 | Clock is parameterised; elapsed time shown under several candidates; no pass/fail verdict | Before Stage 13 | No |
| OPD-03 | Decider for speed-vs-evidence trade-off (finance vs risk) | DR-21; SC-03 | ACCEPTED OPEN | FR-DEC-05, FR-MET-02, FR-POL-02 | FAIL-02 rule: no improvement claimed on one definition while another worsens | Before Stage 13 | No |
| OPD-04 | Owner of approval/priority-rule conflicts: fix vs preserve; correctness of the three rules; default 999,999 for unknown region/year | RC-4; DR-23; R-5; QD-5 DN-3 | OPEN (owner unassigned) | FR-POL-04..06, FR-CO-01 | Three rule sets loaded as named candidates; as-found behaviour preserved and marked; any change needs HAR-06 | Before Stage 14/15 (code change) | No for PRD; Yes for any rule change |
| OPD-05 | Where batch disposition and the decision-of-record actually live (this system vs external) | U-05-02; QD-5 DN-4; C-3; DR-22 | OPEN | FR-GATE-02, FR-GATE-05, FR-DEC-01 | Recording mode configurable (event here / external reference); default blocked; human gate intact (DR-22) | Stage 10 (architecture) needs an answer or an explicit 'unknown, design both' | No for PRD; shapes Stage 10 |
| OPD-06 | Who holds the authorised-disposition role (named role holder(s)) | DR-22; PER-07 | OPEN | FR-GATE-03, FR-GATE-04 | Holder list ships empty; Zone H unavailable until configured | Before any pilot use | No |
| OPD-07 | Evidence sufficiency criteria for closure and the exception rule | BR-09; A-03-10; SC-01 | OPEN | FR-DEC-05 | Structural presence check only (A-09-03); sufficiency left to policy | Before Stage 13 | No |
| OPD-08 | Month-end cut-off, denominator, and source of cost data | SC-04; BR-10; U-24 | OPEN | FR-MET-04, FR-MET-08 | Cut-off configurable; cost attribution deferred (R2) | Stage 13 / 34 | No |
| OPD-09 | Retention policy for case and evidence records | DR-24; NFR-10 | OPEN | PNFR-10 | Hold-all: no deletion until policy adopted | Stage 25 | No |
| OPD-10 | Buy-vs-build (O9, commercial QMS) in scope? | QD-5 DN-5; CD-4 | OPEN (not evaluated) | (whole PRD) | PRD assumes build; O9 recorded as unevaluated | Stage 10 | No; blind spot |
| OPD-11 | Is a deterministic scheduler an 'automated action' under HAR-10? | QD-5 DN-6; CD-5 | OPEN | FR-RUN-01 | Scheduler allowed only for non-Zone-H runs; confirm | Before Stage 15 | No |
| OPD-12 | Whether to make RQ-1..RQ-3 operational (question-set size, recall threshold) and whether any user wants document Q&A | QD-5 DN-7; U-S01 | OPEN | FR-REV-03, non-goal NG-01 | Keyword/field search in R2 only; RQ proposals (>=50 questions, 80% top-5) stay proposals | Stage 12 / when real corpus exists | No |
| OPD-13 | Approval of this Initial PRD, of the R1/R2 split and of the NFR targets (HAR-11) | HAR-11; A-09-02, A-09-04 | OPEN - Dinesh Naik | (whole PRD) | Status DRAFT until recorded in the OD log | Before Stage 10 relies on it as final | Condition of CONDITIONAL PASS |
| OPD-14 | Performance/latency targets | U-03-11; NFR-06 | OPEN | PNFR-06 | R1 measures only | Stage 11 | No |
| OPD-15 | Owner of the parallel workflow for older customers; may it ever be retired | SC-07; BR-11; EX-04 | OPEN | FR-CO-02 | Out of product scope; protected | Stage 5/37 | No |
| OPD-16 | Is the product meant for a real organisation or remain a synthetic capstone? (affects whether any PRD claim can ever be validated) | ER-01; OD-04 | OPEN | (all) | All outputs labelled synthetic, unvalidated | Stage 34 | No |

### OD-2 Decisions already made (applied in this PRD)
| ID | Decision | Source | Application |
|---|---|---|---|
| OPD-C1 | Product is No-AI | OD-08 (2026-10-18) | Applied: FR-CO-04, PNFR-18, non-goals NG-01..NG-04 |
| OPD-C2 | Baseline dataset = shipped 125 cases, seed 4100 | OD-09 (2026-10-18) | Applied: baseline for all verification fixtures; 6,000-case dataset not part of baseline |

### OD-3 Findings on the open set
- [Verified Fact] DR-20, DR-21, DR-22, DR-23, DR-24 are all GAPs in `docs/02-stakeholders/decision-rights-map.md`.
- [Inference] OPD-05 is the decision with the largest architectural consequence: whether the new decision write path is the system of record or a mirror determines the shape of Zone H (QD-5 DN-4). Stage 10 should design both modes or demand the answer.
- [Inference] Because Dinesh is the only human, "accepted open" is a legitimate recorded outcome (BR-02 allows it); it must be recorded explicitly (SUC-11) rather than implied by silence.

## Evidence References
`docs/02-stakeholders/decision-rights-map.md`; `docs/08-ai-qualification/qualification-decision.md` QD-5, CD-1..CD-7; `docs/00-preflight/operating-contract/open-governance-decisions.md`; `.fde/orchestrator-decisions.md`.

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
- All OPD items above; OPD-13 (approval of this PRD) is the only item the gate treats as a condition.

## Residual Risks
- If Dinesh later answers an OPD differently from the neutral stance, affected requirements change (FINAL will mark them Changed).
- Silence is not a decision: unanswered items must be recorded as 'accepted open' or the KPI work cannot start.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial draft (Initial PRD v0.1). |
