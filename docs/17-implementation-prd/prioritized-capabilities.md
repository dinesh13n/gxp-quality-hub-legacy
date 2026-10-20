---
stage: "17 — Finalise Implementation PRD"
artifact: "prioritized-capabilities.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/09-initial-prd/capability-map.md, functional-requirements.md, mvp-scope.md", "docs/13-traceability/evidence/rtm.csv", "docs/15-modernization/modernization-summary.md (INC-01..INC-09 close-out)", "docs/15-modernization/transformation-log.md (DEV-xx)", "docs/15-modernization/remaining-technical-debt.md (RTD-xx)", "docs/16-repo-validation/{test-results,behavior-difference-report,architecture-conformance-report,remaining-debt-register}.md", "hub/ at main 2f318be (code identical to 2c63b07 validated by Stage 16)", ".fde/orchestrator-decisions.md (OD-12, OD-16..OD-24)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. "Built" means implemented and passing its planned tests in a sandbox shadow build (Stage 15/16 evidence). It is NOT an as-built or delivered claim: nothing is cut over, exposed, adopted or activated, and FINAL alone dispositions requirements.**

## Summary
All 10 capabilities exist in the shadow build at `main` 2f318be. Of 52 FRs: **R1 (43)** - 28 built, 13 built with a stated limitation, 2 partial (FR-POL-01 withdrawal; FR-RUN-01 schedule held off); **R2 (9)** - 8 built in shadow and switched off or reachable only through the R2 entry point, 1 not built (FR-MET-08). MoSCoW and release assignments from Stage 9 are **unchanged** (PCH-02). What changes is the **priority of remaining work**: change-safety (CAP-10) moves to the top because no cutover can rely on the build until golden-compare observes the built modules, the suites run in CI and the decided Python 3.12+ production runtime (OD-24) is in place; scheduling (CAP-06) and R2 enablement (CAP-08 search) move down because they wait on human decisions or on data that does not exist.

Priority scale for remaining work: **P1** must be done before any cutover step (CUT-1..CUT-5); **P2** should be done before Stage 27 hardening; **P3** later / when the related decision is taken; **decision** = blocked only by a human decision (owner Engagement lead (Dinesh Naik)); **release** = built, waits for an R2 release decision; **data** = needs real data; **deferred** = not built, stays deferred.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### PC-1 Capability priorities (implementation baseline)
| Rank | Capability | Stage 9 layer | FRs (R1/R2) | Implementation state | Remaining-work priority | Why (evidence) | Tag |
|---|---|---|---|---|---|---|---|
| 1 | CAP-10 Coexistence & change safety | constraint | 4/0 | 1 built, 3 built-limited | **P1 (raised)** | golden-compare 7 declared probes (S16-D01); no CI (RTD-01/02/14); release gates G1/G4/G8/G9/G10 not run (RTD-74); move CI / production to Python 3.12+ with a reviewed golden re-baseline (OD-24, S16-D07) | [Inference] priority; [Verified Fact] state |
| 2 | CAP-09 Access control, audit & data protection | trust | 2/1 | 1 built, 1 built-limited, 1 R2 built | P2 | security test gaps SS-04/SS-08; values proposals (RTD-26); anchor strength (RTD-29) | [Verified Fact] |
| 3 | CAP-02 Human disposition gate | trust | 6/0 | 5 built, 1 built-limited | decision (holders, mode) + P2 (single Zone H check) | holders [] and mode `none` by design; 3 copies of the check (S16-D04) | [Verified Fact] |
| 4 | CAP-01 Decision & evidence record | record | 6/0 | 4 built, 2 built-limited | P2 | evidence access matrix assumption; imported-history proxy | [Verified Fact] |
| 5 | CAP-04 Safe intake & exceptions | flow | 7/1 | 5 built, 2 built-limited, 1 R2 built | decision (contract scope, DV-02/03/07/09/10) | contract fails 3 of 4 sources; DVs open | [Verified Fact] |
| 6 | CAP-03 Policy, definitions & rule service | meaning | 5/1 | 3 built, 1 built-limited, 1 partial, 1 R2 built | decision (activation, DEV-29/30) + P2 (withdrawal) | sets inactive by design (OD-16) | [Verified Fact] |
| 7 | CAP-07 Metrics with declared definitions | meaning | 6/2 | 4 built, 2 built-limited, 1 R2 built, 1 not built | decision (definitions, clock, cut-off) + data | verdicts `not_available_no_adopted_policy`; time to close null on baseline | [Verified Fact] |
| 8 | CAP-05 Shared identity & crosswalk | record | 2/2 | 2 built, 2 R2 built | release | no case->batch keys exist (RF-6) | [Verified Fact] |
| 9 | CAP-08 Reviewer support | meaning | 2/2 | 1 built, 1 built-limited, 2 R2 built off | **P2 (walkthroughs, trace producer); R2 search lowered** | ranking quality unassessable on shipped corpus (RTD-80) | [Inference] priority |
| 10 | CAP-06 Scheduled runs & run records | flow | 3/0 | 2 built, 1 partial | **decision (lowered)** | schedule OFF until OPD-11 / HAR-10 (OD-19) | [Inference] priority |

[Inference] Ranking rule: (1) anything whose absence makes the build unsafe to rely on, (2) trust layer, (3) record layer, (4) flow and meaning, (5) items that only wait for a decision or an R2 release. The Stage 9 MV-6 "cannot cut" set (FR-DEC-01/02/04/06, FR-GATE-01/03/04, FR-INT-01..03, FR-ID-01, FR-RUN-02, FR-MET-01/04/06, FR-SEC-01/02) is entirely built (FR-DEC-02/04 and FR-SEC-02 with limitations).

### PC-2 Priority shifts versus Stage 9
| ID | Shift | From | To | Evidence | Status | Tag |
|---|---|---|---|---|---|---|
| PS-01 | Change-safety work (S16-D01, CI, release gates, runtime) | implicit in FR-CO-01/03/04 "Must/Should R1" | explicit P1 pre-cutover work items | repo-quality-gate QG-4 #2, #4, #6, #8 | Applied (planning priority, PCH-39) | [Inference] |
| PS-02 | Structural cleanup (migrations, Zone H copies, entry points, cycles) | not in PRD | P2 before Stage 27 | architecture-conformance AC-01..AC-04 | Applied (PCH-40) | [Inference] |
| PS-03 | FR-RUN-01 scheduling | Must R1 | Must R1 retained; schedule part waits on OPD-11 (decision) | OD-19; PCH-16 | Applied | [Verified Fact] |
| PS-04 | R2 FRs | "later" | built-dark; enable per item by release decision | INC-09; PCH-20 | Applied | [Verified Fact] |
| PS-05 | FR-REV-04 | Could R2 | keep or reject - Dinesh decides | RTD-87; PCH-22 | Proposed | [Assumption] |
| PS-06 | FR-MET-08 | Could R2 | not built, stays deferred | PCH-19 | Applied | [Verified Fact] |
| PS-07 | Human walkthroughs (TST-REV-03/04/08) | implicit (PR-09) | open until Stage 26 TEVV (OD-24); automated stand-ins remain | S16-D13; OD-24 | Applied | [Verified Fact] |

### PC-3 Requirement-level implementation state (all 52 FRs)
State vocabulary: BUILT; BUILT-LIMITED (built, limitation stated); PARTIAL (a named part not built); BUILT-R2 (R2 built in shadow; OFF = switched off by default); NOT BUILT.

| FR | Cap | MoSCoW | Release | Implementation state | Evidence (summary) | Remaining scope / limitation | Remaining priority |
|---|---|---|---|---|---|---|---|
| FR-DEC-01 | CAP-01 | Must | R1 | BUILT | M003 insert-only, per-case hash chain; TST-DEC-*; ADR-004 conforms | — | — |
| FR-DEC-02 | CAP-01 | Must | R1 | BUILT-LIMITED | projection check mismatches 0 after 125-case backfill | imported cases: as-of is a created_at proxy, legacy events not imported (PCH-12) | P3 |
| FR-DEC-03 | CAP-01 | Must | R1 | BUILT | TST-DEC-* | — | — |
| FR-DEC-04 | CAP-01 | Must | R1 | BUILT-LIMITED | TST-DEC-*; evidence access matrix A-15-05-1 (DEV-47) | access matrix needs owner confirmation; evidence-record schema not exercised on shipped data (DC-05) | P2 |
| FR-DEC-05 | CAP-01 | Must | R1 | BUILT | class-B tests green on default `treat_label_CLOSED_as_closing` (PCH-10) | re-test after OD-S12-03/07 decisions | P2 |
| FR-DEC-06 | CAP-01 | Must | R1 | BUILT | human_only facts (PCH-11) | `rule` derivation mode not built (OD-S12-15) | P3 |
| FR-GATE-01 | CAP-02 | Must | R1 | BUILT | single Zone H choke point; mutant H1 KILLED; no disposition handler outside it | — | — |
| FR-GATE-02 | CAP-02 | Must | R1 | BUILT | evidence pack with pack_hash (INC-08); automated tests | no human walkthrough recorded | P2 |
| FR-GATE-03 | CAP-02 | Must | R1 | BUILT | service/scheduler actors refused; audited ZONE_H_ATTEMPT | Zone H logic in 3 copies (S16-D04) | P2 |
| FR-GATE-04 | CAP-02 | Must | R1 | BUILT | `zone_h.holders` = [] shipped; E-GATE-NO-HOLDERS | holders accepted open (OD-S12-06) | decision |
| FR-GATE-05 | CAP-02 | Must | R1 | BUILT | modes none/event/external_ref; default none (PCH-15) | mode accepted open (OD-S12-05) | decision |
| FR-GATE-06 | CAP-02 | Must | R1 | BUILT-LIMITED | flag_action table, OVERRIDE_RECORDED | override on an intake item without a matched case stores no case event (RTD-69) | P3 |
| FR-POL-01 | CAP-03 | Must | R1 | PARTIAL | 5 candidate policies, none adopted; adoption = Zone H | withdrawal not built (DEV-36, PCH-09) | P2 |
| FR-POL-02 | CAP-03 | Must | R1 | BUILT | CLOCK objects; no verdict without adopted clock | clock accepted open (OD-S12-02) | decision |
| FR-POL-03 | CAP-03 | Must | R1 | BUILT | immutable policy_events + audit; POLICY_DECISION_RECORDED (DEV-35) | decision mechanism to confirm (RTD-43) | P2 |
| FR-POL-04 | CAP-03 | Must | R1 | BUILT | 3 as-found sets INACTIVE; parity TST-CO-03 3/3, 870 grid + 105 boundary cases (PCH-07) | activation accepted open (OD-S12-04) | decision |
| FR-POL-05 | CAP-03 | Should | R2 | BUILT-R2 | divergence report: 3 of 125 differ, nulls reported (DEV-97) | served only by R2WebApp | release |
| FR-POL-06 | CAP-03 | Must | R1 | BUILT-LIMITED | `defaulted` marker (DV-06) | DEV-29 / DEV-30 differ from legacy; preserve-or-fix open (PCH-08) | decision |
| FR-INT-01 | CAP-04 | Must | R1 | BUILT | 10,983 raw items append-only; legacy table untouched (BD-07) | — | — |
| FR-INT-02 | CAP-04 | Must | R1 | BUILT | 67 REPLAY -> NOOP_DUPLICATE; OD-18 natural key | — | — |
| FR-INT-03 | CAP-04 | Must | R1 | BUILT | REVISED_CONFLICT quarantine (fixtures; 0 on shipped data) | — | — |
| FR-INT-04 | CAP-04 | Must | R1 | BUILT-LIMITED | per-source record_only (PCH-04) | contract fails 3 of 4 sources; enforce unusable on shipped data (OD-S12-11) | decision |
| FR-INT-05 | CAP-04 | Must | R1 | BUILT | exact-key match; unmatched/ambiguous flagged (PCH-06) | — | — |
| FR-INT-06 | CAP-04 | Must | R1 | BUILT | enumerated reason codes and queues | — | — |
| FR-INT-07 | CAP-04 | Must | R1 | BUILT-LIMITED | runtime Untrusted guard; planted-string tests (PCH-43) | static check (AC-INT-23) not built | P3 |
| FR-INT-08 | CAP-04 | Should | R2 | BUILT-R2 | delay / freshness reports (DEV-98) | thresholds Assumption (PCH-32) | release |
| FR-ID-01 | CAP-05 | Must | R1 | BUILT | 168 exact-key links (PCH-29) | — | — |
| FR-ID-02 | CAP-05 | Must | R1 | BUILT | no fuzzy match (AC-ID-04); manual link = event | — | — |
| FR-ID-03 | CAP-05 | Should | R2 | BUILT-R2 | consistency check command (DEV-99) | no CONSISTENCY policy adopted -> no findings | release |
| FR-ID-04 | CAP-05 | Should | R2 | BUILT-R2 | joined view (DEV-92, DEV-106) | served only by R2WebApp | release |
| FR-RUN-01 | CAP-06 | Must | R1 | PARTIAL | manual authorised trigger; schedule flag via ZH-09 only (PCH-16) | schedule OFF; scheduler vs HAR-10 accepted open (OPD-11) | decision |
| FR-RUN-02 | CAP-06 | Must | R1 | BUILT | append-only run_event / run records (M005) | — | — |
| FR-RUN-03 | CAP-06 | Must | R1 | BUILT | explicit cap, exact backlog, checkpoint/resume | — | — |
| FR-MET-01 | CAP-07 | Must | R1 | BUILT | tag + policy version/status + 'synthetic, unvalidated' label on every figure | tags null until a definition is adopted | decision |
| FR-MET-02 | CAP-07 | Must | R1 | BUILT | cross-tag combination refused (TST-MET) | — | — |
| FR-MET-03 | CAP-07 | Must | R1 | BUILT-LIMITED | median/p90 per clock | null on baseline (`no_completed_cycles`) (PCH-17) | data |
| FR-MET-04 | CAP-07 | Must | R1 | BUILT | Decimal, one table, cut-off required; 622,826.44 (PCH-18) | cut-off accepted open (OD-S12-08) | decision |
| FR-MET-05 | CAP-07 | Should | R1 | BUILT-LIMITED | backlog by site, D-OPS | D-EVID = E-MET-NOT-AVAILABLE (DEV-69) | P3 |
| FR-MET-06 | CAP-07 | Must | R1 | BUILT | metrics reproduce from stored inputs; labels | — | — |
| FR-MET-07 | CAP-07 | Should | R2 | BUILT-R2 | OP-MET-06 per-source unmatched rate (DEV-100) | served only by R2WebApp | release |
| FR-MET-08 | CAP-07 | Could | R2 | NOT BUILT | OP-MET-05 = E-MET-NOT-AVAILABLE (PCH-19) | needs cost source and owner (OPD-08) | deferred |
| FR-REV-01 | CAP-08 | Should | R1 | BUILT-LIMITED | template rule-trace text | no automatic trace producer (PCH-23, RTD-69) | P2 |
| FR-REV-02 | CAP-08 | Must | R1 | BUILT | reviewer queue with reason, source, receipt time, age | human walkthroughs TST-REV-03/04/08 open until Stage 26 (OD-24, S16-D13) | P2 |
| FR-REV-03 | CAP-08 | Should | R2 | BUILT-R2 (OFF) | FTS5 + identical fallback; `search.enabled` false, `search.fts` off | ranking quality unassessed (RTD-80, OPD-12); FTS5 on target runtime Unknown (RTD-79) | release |
| FR-REV-04 | CAP-08 | Could | R2 | BUILT-R2 (OFF) | 2 deterministic templates; `templates.enabled` false | keep / reject proposed (PCH-22) | decision |
| FR-SEC-01 | CAP-09 | Must | R1 | BUILT | deny-by-default registry (48 routes), PBKDF2, lockout, CSRF, loopback | control values proposals (RTD-26); header values untested (SS-04) | P2 |
| FR-SEC-02 | CAP-09 | Must | R1 | BUILT-LIMITED | hash-chained audit; verify-audit rc 0 | anchor = unsigned local file (RTD-29, OD-S12-18) | P2 |
| FR-SEC-03 | CAP-09 | Should | R2 | BUILT-R2 | C0..C3 classes, C3 reason (PCH-25) | field map proposed; finance path unreachable (RTD-82/83) | release |
| FR-CO-01 | CAP-10 | Must | R1 | BUILT-LIMITED | harness 134/134; golden-compare exit 6 by design | 7 declared probes (S16-D01); DV decisions open (OD-S12-13) | P1 |
| FR-CO-02 | CAP-10 | Must | R1 | BUILT | coexistence_inventory protected (TST-CO-08) | owner Unknown (OPD-15) | decision |
| FR-CO-03 | CAP-10 | Should | R1 | BUILT-LIMITED | 5 rollback rehearsals (PCH-28) | release gates G1/G4/G8/G9/G10 not run or failing (RTD-74) | P1 |
| FR-CO-04 | CAP-10 | Must | R1 | BUILT-LIMITED | no-ai-check, egress tripwires = 0 | not in CI (RTD-14) | P1 |

Counts: R1 43 = 28 BUILT + 13 BUILT-LIMITED + 2 PARTIAL; R2 9 = 8 BUILT-R2 (2 of them OFF by flag) + 1 NOT BUILT. [Verified Fact] for the states (Stage 15 close-out: 241/241 planned tests green; Stage 16: 396 ok / 1 skipped / 0 fail at 2c63b07); [Inference] for the summary wording of each limitation.

### PC-4 Dependencies (updated from Stage 9 CM-2)
[Verified Fact] The Stage 9 relationships hold in the build, with these additions: CAP-03 -> CAP-04 (contract binding changes are policy events through the Zone H gate, DEV-55); CAP-03 -> CAP-06 (schedule flag is a policy event, DEV-64); CAP-02 -> CAP-03 (activation needs a recorded holder decision, DEV-35); CAP-01 -> CAP-05 (crosswalk links created in the same decision store, M003). [Verified Fact] Undesired dependencies exist in code: domain packages import `hub.web` and 16 package cycles (S16-D06) - P2.

## Evidence References
`hub/` packages per capability: CAP-01 `hub/decision`; CAP-02 `hub/gate`; CAP-03 `hub/policy`; CAP-04 `hub/intake`, `hub/adapters`; CAP-05 `hub/crosswalk`; CAP-06 `hub/runs`; CAP-07 `hub/metrics`; CAP-08 `hub/review`, `hub/search`, `hub/r2`; CAP-09 `hub/security`, `hub/admin`, `hub/web`; CAP-10 `hub/coexistence`, `hub/golden`, `hub/guards`, `tests/characterization/`.

## Assumptions
- A-17-PC-1 [Assumption] Ranking remaining work by "safety to rely on the build" first is the right planning order for Stage 18. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-17-PC-1 Effort and calendar for P1/P2 items (no delivery calendar; U-08-09).

## Unresolved Issues
- PS-05 (FR-REV-04) and every "decision" row (see implementation-prd.md IP-7).

## Residual Risks
- RR-PC-1 "Built" may be read as "delivered"; this file does not claim delivery (Medium; mitigated by the label).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
