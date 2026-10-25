---
stage: "40 — Scale / 90-Day Transformation Roadmap"
artifact: "reusable-components.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 40 run)"
status: "DRAFT"
evidence_sources: ["hub/ (23 packages)", "tests/hub/regression_groups.json", "docs/26-tevv/tevv-release-gate.md", "docs/27-hardening/production-readiness-checklist.md", "docs/28-reliability/resilience-readiness.md", "docs/31-observability/slo-sla-definitions.md", "docs/12-specs/contracts/", "docs/27-hardening/error-registry/", "docs/37-operating-model/target-operating-model.md", "docs/36-roi/roi-model.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32..OD-36)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 40 adds files under `docs/40-scale/` and changes nothing else). This is a PROPOSAL. It does not say the value case is proven (Stage 36: ROI NOT COMPUTABLE), it schedules no cutover (Stage 30 and the cutover decision are Dinesh Naik's), and it accepts no risk on Dinesh's behalf (OD-04, OD-32, HAR-11).**

## Summary
**Result: 0 components have been reused outside the first use case, so 0 components have demonstrated reuse (grade E3).** What the repository does hold is *structural* reuse evidence (grade E2): standard-library-only code, an own test group, a schema or contract, and low coupling to quality-domain vocabulary. On that basis this file sorts 20 candidate assets (plus 11 exclusions) into four tiers: **A reuse-supported (3), B reuse-conditional (13), C not yet reusable (4), X excluded as first-use-case assumption or debt (list in RC-4).** "Reuse-supported" means "a second use case could adopt it with the stated conditions", not "it has been adopted". Every tier is an Inference from cited evidence; a first real reuse would turn a tier-A item into E3 evidence.

## Findings
### RC-1 Evidence grades used (defined here, applied in all Stage 40 files)
| Grade | Meaning | Tag |
|---|---|---|
| E3 | Reused by a second use case, team or deployment and still passing | none exists: [Verified Fact] (no second use case appears anywhere in the repo; `docs/03-problem-value/scope-exclusions.md`) |
| E2 | Structural evidence: stdlib-only + own regression group or mutation-killed control + schema/contract + low domain coupling | [Verified Fact] for each cited item; the reuse conclusion is [Inference] |
| E1 | Built and tested in sandbox, but not wired, not switched on, or environment-bound | [Verified Fact] |
| E0 | No evidence | [Unknown] |

Domain-coupling figure = files under the package containing at least one of: batch, deviation, oos_, capa, site_code, zone_h, gxp, disposition (case-insensitive grep at main `ef72e4e`; a coarse proxy, not a design review) [Verified Fact: count; Inference: meaning].

### RC-2 Component register
| ID | Asset | Paths | Reuse evidence | Coupling (files) | Tier | Conditions before a second use case adopts it | Confidence |
|---|---|---|---|---|---|---|---|
| RC-01 | Boundary guards: sandbox, No-AI, egress, runtime self-check, Untrusted text type | `hub/guards/`, `hub/__init__.py` | E2: 0 of 4 files domain-coupled; zero-model-call and zero-egress tripwires read 0 in S26 (RT-05) and E26/E27/E28 groups; SCN-01/05 no third-party package | 0/4 | A | OD-08 (No-AI) must hold for the new use case, else the guard is wrong for it; Python floor decision (D-27-02) | High |
| RC-02 | Store + tamper-evident audit chain + verify-audit | `hub/store/`, `hub/admin/`, ADR-005, `docs/27-hardening/schemas/store-tables/` | E2: S26 tamper tests (every tamper detected, chain ok after concurrency, RT-12); STG27 H01/H02 insert-only incl. `schema_migrations`; backup/restore with checksum manifest (OD-03) | 1/5 and 1/3 | A | F-29-01 (`verify-audit` KeyError) fixed; opt-in anchor seal decision (RS-03, DQ-S24-02) and key custody (PR-11); off-device backup (HAR-09, PR-25); retention rule (OD-S12-09 hold-all today) | Medium-High |
| RC-03 | Grouped regression runner + sandbox-copy discipline | `tests/hub/run_hub_groups.py`, `tests/hub/regression_groups.json` (29 groups), OD-03a, OD-23 | E2: full hub regression green at each merge (OD-27, OD-30, OD-34, OD-35, OD-36); the orchestrator's pass caught real defects at S21, S24, S28, S31 | n/a | A | Wall-time limits: group C ~145 s of the 180 s device cap (OD-21); needs a hosted runner for 3.12+ (RTR-08) | Medium |
| RC-04 | Policy / rule service (engine only) | `hub/policy/`, ADR-007 | E2 for the engine: CT-01..03 parity (TST-CO-03); rule sets ship INACTIVE (OD-16) | 3/13 | B | Rule *contents* are first-use-case (RC-4 X-01). New use case needs its own rule owner (the rule-set owner named RC-3/RC-4 in OD-16 is still open) and a recorded human activation | Medium |
| RC-05 | Intake pipeline + source-contract (record_only) + natural key | `hub/intake/`, `integration/source-contract-v1.json`, `docs/27-hardening/schemas/intake-envelope.schema.json` | E2: STG27 C01/C02 structure checks; natural key decided by Dinesh (OD-18); gateway client bounded retry (OD-28) | 3/13 | B | Per-source contracts written (OD-28); `record_only` never exercised as `enforce` (OD-S12-11); schema_version allow-list open; real source behaviour Unknown (U-28-01) | Medium |
| RC-06 | Identity crosswalk | `hub/crosswalk/`, ADR-009 | E1-E2: 125-case backfill in sandbox; 5-row gap between K-06 matched rows (173) and hub linked (168) not investigated (U-34-02) | 2/5 | B | Close U-34-02; the 125-case synthetic set is not evidence about any other population | Low-Medium |
| RC-07 | Metrics framework with definition tags | `hub/metrics/`, ADR-011 | E2 for the mechanism: 0/8 domain-coupled; PNFR-20 labelling met for metrics | 0/8 | B | The *definitions* are Stage 4 proxies, FROZEN-PROVISIONAL and unsigned (OD-07); each adjacent use case needs its own signed definitions | Medium |
| RC-08 | Decision / evidence record + disposition gate + authority switch (CLI + `approval_ref`) | `hub/decision/`, `hub/gate/`, `hub/control/`, ADR-006, DW-17 | E2: S26 A02 and mutant M9; FR-GATE-03 invariant; ships off, Zone H holders EMPTY (OD-17, OD-31) | 2/9, 9/11, 4/6 | B | The *pattern* is reusable; Zone H, disposition and GxP framing are first-use-case (9/11 gate files coupled). Authorised holders are a human fact that does not exist (RL-04 VACANT). Single-approver: Dinesh answered DQ-17 'accept the single-approver risk' for the engagement (OD-30) while RP-01 stays open in the register; carrying it to a scaled footprint is not decided | Medium |
| RC-09 | AuthN/AuthZ, sessions, lockout, rate limit, CSRF, restricted-evidence rule | `hub/security/`, `hub/web/ratelimit.py`, ADR-013 | E2: S26 authz matrix, 80/80 attacks refused; PR-01..PR-19 mostly MET | 10/19 | B | No TLS, no second factor, no token expiry (PR-06, PR-07, PR-14; RS-01, RS-02, RS-08); restricted-note rule is an agent assumption A-27-02 (D-27-01); finance read surface not built | Medium |
| RC-10 | Reviewer queue and reviewer surfaces | `hub/review/`, `hub/web/` | E1-E2: INC-08 tests; HTTP surface loopback only; manual walkthroughs TST-REV-03/04/08 UNSIGNED (RTR-07) | 2/6, 8/18 | B | Human sign-off of walkthroughs; no real reviewer has used it (K-21 = 0 of 125) | Low-Medium |
| RC-11 | Run orchestration (scheduler OFF) + run records | `hub/runs/`, ADR-010 | E1: built; scheduler never switched on; HAR-10 / OPD-11 undecided | 8/14 | B | Scheduler decision; catch-up policy (D-28-04) | Low-Medium |
| RC-12 | Error registry + JSON schemas + OpenAPI contract | `docs/27-hardening/error-registry/`, `docs/12-specs/contracts/`, `docs/27-hardening/schemas/` | E2 structure: registry-derived tables (S24-DEV-05); 16 contract schemas | n/a | B | FAC-09: 23 schema-less tables (deferred); new error codes need spec addenda (D-27-05) | Medium |
| RC-13 | Golden-compare engine + characterisation method | `hub/golden/`, `tests/characterization/`, `docs/15-modernization/how-to-run-characterization-harness.md` | E2 for the method; E1 for the goldens: bound to Python 3.10.12 (OD-23); CT-13 fails on Node patch drift (S24-DEV-04) | 1/5 | B | Only applicable when an adjacent use case has a legacy estate to preserve; goldens must be re-baselined per environment under approval | Medium |
| RC-14 | Observability code: metrics, log, SLO definitions, alert catalogue | `hub/obs/`, `docs/31-observability/` | E1: Stage 31 is built but nothing wired; 5 SLO CANDIDATES (2 without an SLI source); no SLA exists | 6/13 | C | Wiring decision; SLO numbers are agent assumptions (D-31-01..10) | Medium |
| RC-15 | Resilience mechanisms: retry budget, breaker, bulkhead, bounded listener | `hub/resilience/`, `hub/web/bounded_server.py` | E1: injection tests pass; **not wired** into `gateway-pull` or `web serve` (D-28-01, D-28-02); numeric defaults are assumptions | 0/3 | C | Wire, then re-run failure injection on the wired path | Medium |
| RC-16 | Reviewer search (FTS) and R2 reports / templates | `hub/search/`, `hub/r2/` | E1: INC-09 built dark; FTS5 on target Unknown (OD-S12-12) | 0/9, 5/14 | C | Switched off by design; needs a separate approval | Medium |
| RC-17 | Legacy coexistence adapters (read-only) | `hub/adapters/`, `hub/coexistence/`, ADR-003 | E1: tied to this legacy estate | 1/5, 2/2 | C | Only meaningful for a use case that has its own legacy to wrap | High |
| RC-18 | Stage documentation system: OD log, evidence labels, artifact header, gate definitions | `.fde/orchestrator-decisions.md`, `docs/**` | E2: applied across Stages 0A-37 with the same skeleton | n/a | B | Depends on one human decider; no second approver exists (OD-04) | Medium |
| RC-19 | TEVV kit: declared thresholds, datasets, mutation gate, red-team plan | `docs/26-tevv/`, `docs/26-tevv/evidence/s26_mutation_gate.py` | E2: thresholds declared before results (TH-3); 13 of 13 mutants killed after S27 | n/a | B | 12-mutant sample (RTR-13); agent-run red team only (RTR-14) | Medium |
| RC-20 | Production-readiness checklist (38 checks) | `docs/27-hardening/production-readiness-checklist.md` | E2: 24 of 38 MET, 14 documented | n/a | B | Re-score per use case; 14 checks currently NOT MET/UNKNOWN | Medium |

### RC-3 Tier A, B, C counts [Verified Fact: counts of the table above]
A = RC-01..RC-03 (3). B = RC-04..RC-13, RC-18..RC-20 (13). C = RC-14..RC-17 (4). Total 20.

### RC-4 Excluded: first-use-case assumptions and debt (not to be reused or copied)
| ID | Excluded item | Why | Evidence |
|---|---|---|---|
| X-01 | The three as-found rule sets (Python > 50,000; JS regional limit x1.05 with 999,999 fallback; night-shift 2,500-8,500) | They encode unowned thresholds; inactive candidates | OD-16 (rule-set owner, called RC-3/RC-4 in that entry, is still open) |
| X-02 | Stage 4 KPI definitions and their proxies (P-01..P-04, K-06, K-08, K-09U, K-10, K-12, K-13) | Generator-bounded; compare unrelated populations | OD-07 |
| X-03 | The 125-case synthetic baseline and the 6,000-case regenerable set as "evidence" | Synthetic, seed-bounded | OD-02, OD-09 |
| X-04 | Python 3.10-bound goldens | Environment-specific | OD-23 |
| X-05 | The legacy Dockerfile / compose | Never executed, unhardened (PR-21) | D-27-06 |
| X-06 | Numeric defaults (retries 3, breaker 3/60 s, cap 64, budget 20%, RTO 4 h / RPO 1 working day, SLO 99.5/95/99%, rate limit 100 refusals/60 s, 90-day token expiry) | Agent assumptions, unapproved | OD-32, OD-34..OD-36 |
| X-07 | USD 300/day labour rate, 0C ranges, USD 533 / 719 AI-option costs | Unvalidated; AI option not chosen | I-10 in `roi-model.md`; OB-09 |
| X-08 | Loopback-only posture and empty Zone H holders presented as "security" | They are absence of exposure/holders, not controls that scale | PR-13, PR-14, RL-04 |
| X-09 | Single-approver model (Dinesh is the only human) | Accepted by Dinesh for the engagement (DQ-17, OD-30); RP-01 still open in the register; not decided for scale | DQ-17 / OD-30 |
| X-10 | Hold-all retention | Interim default | OD-S12-09, GD-07 |
| X-11 | Stage 34/35/36 sandbox "after" values | Parity, not improvement | `docs/35-variance/kpi-variance-table.md` V-1 |

## Evidence References
See `evidence_sources`; per-row paths in RC-2. Grep for coupling run against main `ef72e4e` (read-only).

## Assumptions
- A-40-01 [Assumption] Tier boundaries (RC-1) are the agent's. Confirm: Engagement lead (Dinesh Naik).
- A-40-02 [Assumption] Domain-term grep is an acceptable coupling proxy. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-40-01 Whether any component works for a use case outside quality-deviation handling: no test exists. Resolved only by a first real reuse (E3).
- U-40-02 Python 3.12+ behaviour of every component (RTR-08).

## Unresolved Issues
- Stage 39 (drift) is not merged at `ef72e4e`; drift evidence per component is not consumed (see `scale-governance.md` SG-7).

## Residual Risks
- A tier-A label read as "proven reusable" (SR-01 in `scale-risk-assessment.md`).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue |
