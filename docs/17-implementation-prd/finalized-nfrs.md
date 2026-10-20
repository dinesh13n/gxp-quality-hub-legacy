---
stage: "17 — Finalise Implementation PRD"
artifact: "finalized-nfrs.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/09-initial-prd/nfrs.md (PNFR-01..PNFR-20 baseline)", "docs/12-specs/nfr-spec.md, security-spec.md, observability-spec.md", "docs/13-traceability/evidence/rtm.csv (evidence classes)", "docs/15-modernization/inc08-design-notes.md (D-15 NFR helpers, D-16 determinism)", "docs/15-modernization/remaining-technical-debt.md (RTD-26, RTD-29, RTD-59, RTD-60, RTD-72, RTD-73, RTD-74, RTD-77, RTD-86)", "docs/15-modernization/rollback-rehearsal-inc0{3,6,7,8,9}.md", "docs/16-repo-validation/{security-scan-summary,dependency-scan-summary,test-results,data-contract-results}.md, evidence/secret-scan.txt", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-22, OD-24)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Every figure below comes from sandbox runs on FX-BASE125 (125 cases, seed 4100) or small synthetic stores and is "synthetic, unvalidated". Numeric targets from `docs/operations-service-levels.md` remain Assumptions (A-09-04); no target is invented here.**

## Summary
The 20 PNFRs keep their IDs and release assignment (17 R1, 3 R2). For each, this file fixes the **implementation-baseline statement**: the measurable target (unchanged unless logged), how it is verified, what the shadow build shows today, and what is still needed. Result: **9 met in the sandbox shadow build** (PNFR-07, -09, -10, -11, -13 on existing fixtures, -16, -17, -18, -20 for metrics; limits in the table), **4 partly met** (PNFR-08 loopback only / no TLS, PNFR-14 metrics not all exported, PNFR-15 no automatic trace producer, PNFR-19 release gates incomplete), **5 verified only as mechanism with an unvalidated or unprovable target** (PNFR-01..-05), **1 measured with no target** (PNFR-06, OPD-14 accepted open), **PNFR-12 built R2 with proposed values**. Three target statements change (PNFR-03/04 configurable thresholds, PNFR-06 measure-only confirmed, PNFR-13 fixture wording proposed) and one cross-cutting constraint is added: **runtime NFR-RT** from OD-24.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### FN-1 Finalised NFR register
| ID | Category | Target (implementation baseline) | Change vs Stage 9 | Verification (tests / evidence) | Shadow-build status at 2f318be | Remaining / owner | Tag |
|---|---|---|---|---|---|---|---|
| PNFR-01 | Availability | 99.5 % scheduled-hour availability - **Assumption** | none | `hub/web/nfr.py` availability helper over supplied records (TST-NFR, class C) | mechanism only; sandbox figure is not a production measure (RTD-72) | prove at Stage 28/31 on a real host; target owner Engagement lead (Dinesh Naik) | [Assumption] target; [Verified Fact] mechanism |
| PNFR-02 | Timeliness | overnight reconciliation done by 06:00 local, 100 % of scheduled nights - **Assumption** | none (scheduler OFF noted) | timeliness helper; run records | unprovable while the schedule is OFF (OD-19) and `site.timezone` supports UTC / fixed offset only (RTD-62) | needs OPD-11 decision and a real schedule (CUT-5) | [Unknown] |
| PNFR-03 | Timeliness (R2) | partner item accepted within **`intake_reports.*` threshold, shipped value 4 h** (Assumption) | target becomes a configured threshold (PCH-32) | delay report on OP-INT-04 (DEV-98) | built R2; 2,234 future `source_ts` rows not re-measured (RTD-86) | confirm threshold; define source event | [Assumption] |
| PNFR-04 | Freshness (R2) | stale signal max **`intake_reports.*` threshold, shipped 24 h** (Assumption); "risk signal" Undefined | as PNFR-03 | freshness view `?view=freshness&as_of=` | built R2 | define "risk signal" | [Assumption] / [Unknown] |
| PNFR-05 | Recovery | RTO 8 h, RPO 24 h (Assumption); restore rehearsal passes with checksum match | none | backup-before-migrate; rollback rehearsals INC-03, -06, -07, -08, -09 | rehearsals pass in sandbox; L2 restore loses post-backup writes (RTD-33) | production RTO/RPO unproven (Stage 28) | [Verified Fact] rehearsal; [Assumption] target |
| PNFR-06 | Performance | **measure p50/p95, no threshold** until OPD-14 | confirmed measure-only (PCH-33) | latency helper, TST-NFR | measured on small synthetic stores only | OPD-14 accepted open | [Verified Fact] |
| PNFR-07 | Access | 100 % of endpoints authenticated and authorised; 0 anonymous reads/writes | none | TST-SEC-01 (48-route registry, deny-by-default), I8 HTTP tests | met in shadow (loopback) | control values are proposals (RTD-26), Stage 24 | [Verified Fact] |
| PNFR-08 | Transport / secrets | secret scan 0; any non-loopback binding uses TLS and needs HAR-05 | clarified: non-loopback bind refused even with approval (PCH-45) | secret scan (1 deliberate test-fixture hit, 0 real secrets); start-up guard TST-SEC-16 | **partly met**: no TLS exists; loopback-only; "refuse even with approval" untested (SS-08) | add test (Stage 23); TLS / exposure decision (Stage 24, RTD-77) | [Verified Fact] |
| PNFR-09 | Audit (framing, not Part 11) | 100 % decision events with actor/time/basis; chain verification passes; tamper detected | none | `verify-audit` rc 0; tamper tests; per-case decision chains | met in shadow | anchor is an unsigned local file (RTD-29, OD-S12-18) - Stage 24 | [Verified Fact] |
| PNFR-10 | Retention | 0 deletions while no retention policy (hold-all) | none | insert-only triggers (`E-SEC-RETAINED`); no delete paths | met | retention policy accepted open (OD-S12-09); unbounded growth (RTD-30) | [Verified Fact] |
| PNFR-11 | Data integrity | 0 duplicate effects on replay; 0 silent overwrites; raw count = received count | none | 10,983 raw items; 67 REPLAY -> NOOP; legacy DB sha unchanged | met on shipped data | — | [Verified Fact] |
| PNFR-12 | Data protection (R2) | 100 % of field classes covered by an access test | none | C0..C3 tests, C3 reason (I9-SEC-20) | built R2; field map PROPOSED (RTD-83); finance path unreachable (RTD-82) | Stage 24 | [Verified Fact] / [Assumption] values |
| PNFR-13 | Untrusted content | 0 effects on decision fields from the planted-string fixtures; **proposed wording: 86 shipped feed rows + 22 injection documents + 10 injection variants** (44-string fixture to be built) | PCH-31 (Proposed) | TST-NFR-13; Untrusted runtime guard | met on existing fixtures | Dinesh accepts wording or the 44-string fixture is built | [Verified Fact] |
| PNFR-14 | Observability | 100 % runs have run records; every R1 KPI has a computed metric | none | run records (M005); JSON logs; `obs_metric` | run records met; 9 observability metrics not exported (RTD-60) | Stage 31 | [Verified Fact] |
| PNFR-15 | Usability / safety | 100 % of rule outputs show rule trace and offer override with reason | none | flag_action, OVERRIDE_RECORDED; trace templates | partly: traces only after `record-trace` (RTD-69); human walkthroughs open until Stage 26 (OD-24) | trace producer (P2) | [Verified Fact] |
| PNFR-16 | Metric auditability | 100 % KPIs documented; re-run identical | none | metrics reproduce from stored inputs (INC-07); DEV-79 | met | — | [Verified Fact] |
| PNFR-17 | Determinism | identical input -> identical output; goldens pass; 0 randomness in core paths | none | TST-NFR-17 across hash seeds / TZ / locale; no `time`/`random` in guarded modules; harness 134/134 | met on reference runtime | goldens runtime-specific (IA-12) | [Verified Fact] |
| PNFR-18 | No AI | 0 model calls; 0 inference egress; tripwire 0 | none | TST-CO-11/12, E05..E09; zero third-party deps | met; **manual gate, not CI** (RTD-14) | CI wiring (P1) | [Verified Fact] |
| PNFR-19 | Change safety | rollback rehearsed; replay-safety gate before each release | none | 5 rehearsals; G2 replay suite | **partly met**: G1 red by design (OD-S12-13), G4/G8/G9/G10 not run (RTD-74); no CI | P1 | [Verified Fact] |
| PNFR-20 | Honest labelling | 100 % KPI outputs and reports labelled 'synthetic, unvalidated' | none | label in every metric figure (`hub/metrics/service.py`, `cli.py`) | met for metrics; R2 reports / search pages label not separately verified | check at Stage 26 | [Verified Fact] / [Unknown] |
| NFR-RT (new, cross-cutting) | Runtime | **production Python 3.12+**; code and tests keep the **Python 3.10 / SQLite 3.37 floor** | added from OD-24 (PCH-36) | runtime self-check (`hub/runtime.py`, E-CO-RUNTIME-UNSUPPORTED); hub regression 3.13 (OD-23) | floor enforced; no production runtime exists | CI on 3.12+, reviewed legacy re-baseline (ENV-4/6), FTS5 check on target (Stage 27) | [Verified Fact] decision |

### FN-2 Notes
- [Verified Fact] Security-relevant defaults hold in the shipped configuration: bind 127.0.0.1, exposure not approved, `zone_h.holders` [], disposition `none`, search / FTS / drafts off, scheduler off (security-scan-summary SS-02).
- [Inference] PNFR-01..05 cannot move beyond "mechanism verified" in this engagement: there is no production host or telemetry (OD-04). Stage 13 class C (9 tests) already recorded this limit.
- [Verified Fact] Two hub mutants survive (H3 header values, H5 non-loopback bind): PNFR-07/08 hardening could regress silently until tests are added (S16-D09).

## Evidence References
See `evidence_sources`; per-row verification column; `docs/16-repo-validation/evidence/hub-mutation.json`.

## Assumptions
- A-09-04 (carried) NFR numeric targets are archived working targets, not measured guarantees. Confirm: Engagement lead (Dinesh Naik).
- A-17-FN-1 [Assumption] Sandbox measurements are acceptable as evidence of mechanism, never of production compliance. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-17-FN-1 Production availability, timeliness, latency and recovery (no host; Stages 28/31).
- U-17-FN-2 Definition of "risk signal" (PNFR-04).

## Unresolved Issues
- PNFR-13 wording (PCH-31); PNFR-08 TLS / exposure (Stage 24); PNFR-19 release gates and CI (P1); OPD-14 latency target (accepted open).

## Residual Risks
- RR-FN-1 Reading sandbox NFR figures as production evidence would be false precision (Medium).
- RR-FN-2 Runtime move to 3.12+ may change legacy comparison outputs (ENV-4/6) (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
