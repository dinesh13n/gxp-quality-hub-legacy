---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "requirement-disposition-matrix.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/09-initial-prd/functional-requirements.md", "docs/17-implementation-prd/prioritized-capabilities.md", "docs/17-implementation-prd/prd-change-log.md", "docs/17-implementation-prd/finalized-nfrs.md", "docs/20-application/application-readiness.md", "docs/13-traceability/requirements-traceability-matrix.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
All 52 FRs and 20 PNFRs are dispositioned with rationale and evidence. FR totals: Delivered 44 (36 R1 + 8 R2 built dark), Delivered + Deferred part 3, Changed 4, Deferred 1, Rejected 0, Superseded 0. 'Delivered' means built in the shadow hub and sandbox-tested only; **no requirement is released, accepted or in use**.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DM-1 Method and vocabulary
[Verified Fact] The FR register is `docs/09-initial-prd/functional-requirements.md` FF-1 (52 FR = 43 R1 / 9 R2; the '41/11' figure in the Stage 12 brief is wrong, OD-10(b), PCH-02). IDs are not renumbered.

Disposition vocabulary used here (the prompt's five values, with an explicit meaning because **nothing was released**):
- **Delivered** = built as specified **in the shadow hub** and sandbox-tested. It does NOT mean released, accepted, in production or valuable. Release state of every row: **NOT RELEASED** (Stage 30 BLOCKED, 0 of 40 approvals).
- **Delivered + Deferred part** = built, with a named part not built; the part is Deferred.
- **Changed** = a recorded change (PCH-nn / OD-nn) altered what the requirement means or what is built differs from its Stage 9 text.
- **Deferred** = not built; text unchanged.
- **Rejected** / **Superseded** = no FR was rejected or superseded (see DM-4 for non-FR items that were superseded).

Basis: [Verified Fact] the per-FR implementation state at `main` 2f318be recorded in `docs/17-implementation-prd/prioritized-capabilities.md` PC-3 and `prd-change-log.md`, updated with later-stage documents I read where they closed a Stage 17 gap (Stage 20 `application-readiness.md`; OD-25, OD-29, OD-31, OD-37). [Assumption A-43-01] The per-FR state still holds at `main` 08add05 except for the deltas named; I did not re-run any test (docs-only). [Inference] Later stages (21, 23, 24, 26-28, 30, 31) changed hub code; their regressions were green per OD-30..OD-37, which supports but does not prove each FR row.

### DM-2 Counts
| Disposition | R1 | R2 | Total |
|---|---|---|---|
| Delivered | 36 | 8 | 44 |
| Delivered + Deferred part | 3 | 0 | 3 |
| Changed | 4 | 0 | 4 |
| Deferred | 0 | 1 | 1 |
| Rejected | 0 | 0 | 0 |
| Superseded | 0 | 0 | 0 |
| **Total** | 43 | 9 | 52 |

[Verified Fact] Of the 8 R2 rows marked Delivered, all are built dark (switched off or served only by `python -m hub.r2 serve`); enabling any is a release decision (release-boundaries RB-3). [Inference] 'Delivered' totals therefore overstate user-visible capability: no FR is in use.

### DM-3 Disposition of all 52 functional requirements
| FR | Cap | MoSCoW | Rel | Disposition | Rationale / limitation | Evidence |
|---|---|---|---|---|---|---|
| FR-DEC-01 | CAP-01 | Must | R1 | Delivered | Insert-only decision events, per-case hash chain. | M003; TST-DEC-*; ADR-004 conforms (PC-3) |
| FR-DEC-02 | CAP-01 | Must | R1 | Changed | Projection reproducible (0 mismatches after 125-case backfill) but for imported cases as-of time is a `created_at` proxy; legacy `events` not imported. | PCH-12; DEV-48; RTD-50 |
| FR-DEC-03 | CAP-01 | Must | R1 | Delivered | Explicit reopen event. | PC-3; TST-DEC-* |
| FR-DEC-04 | CAP-01 | Must | R1 | Delivered | Built; evidence-access matrix is an Assumption (DEV-47); evidence-record schema not exercised on shipped data (DC-05). | PC-3; PCH list |
| FR-DEC-05 | CAP-01 | Must | R1 | Delivered | Fail-closed default `treat_label_CLOSED_as_closing`; CLOSE_EXCEPTION as closing transition is an Assumption (DEV-46). | PCH-10; INC-05 D-08 |
| FR-DEC-06 | CAP-01 | Must | R1 | Delivered | Facts recorded human-only; `rule` derivation mode not built (OD-S12-15 default). | PCH-11; DEV-44/45 |
| FR-GATE-01 | CAP-02 | Must | R1 | Delivered | Single Zone H choke point; mutant H1 killed (Stage 16, again Stage 20 G1S20/H1S20). | PC-3; application-readiness RD-1 DW-06 |
| FR-GATE-02 | CAP-02 | Must | R1 | Delivered | Evidence pack with pack_hash; no human walkthrough recorded. | INC-08; PC-3 |
| FR-GATE-03 | CAP-02 | Must | R1 | Delivered | Service/scheduler actors refused; Stage 20 DW-06 consolidated to one holder rule. | PC-3; DW-06 |
| FR-GATE-04 | CAP-02 | Must | R1 | Delivered | `zone_h.holders` ships `[]`; stays empty (OD-31). | OD-31; E-GATE-NO-HOLDERS |
| FR-GATE-05 | CAP-02 | Must | R1 | Delivered | Modes none/event/external_ref; default `none`; choice open. | PCH-15; ADR-006 |
| FR-GATE-06 | CAP-02 | Must | R1 | Delivered | Override with reason; an override on an intake item without matched case stores no case event (RTD-69). | PC-3 |
| FR-POL-01 | CAP-03 | Must | R1 | Delivered | 5 candidate policies, none adopted. Withdrawal (not built at Stage 17, PCH-09) was built at Stage 20 DW-07 (ZH-10) and approved as built (OD-29, FAC-13). | PCH-09; application-readiness RD-1 DW-07; OD-29 |
| FR-POL-02 | CAP-03 | Must | R1 | Delivered | CLOCK objects; no verdict without adopted clock. | PC-3; OD-S12-02 open |
| FR-POL-03 | CAP-03 | Must | R1 | Delivered | Immutable policy events; decision mechanism to confirm (RTD-43). | PC-3; DEV-35 |
| FR-POL-04 | CAP-03 | Must | R1 | Delivered | Three as-found sets loaded INACTIVE; parity 3/3 (870 grid + 105 boundary). | PCH-07; OD-16 |
| FR-POL-06 | CAP-03 | Must | R1 | Changed | `defaulted` marker built; the as-found 'preserve' behaviours for partial-year match (DEV-29) and 'abc'/null coercion (DEV-30) are NOT reproduced; no preserve mode. | PCH-08; DV-05; DV-11 |
| FR-INT-01 | CAP-04 | Must | R1 | Delivered | 10,983 raw items append-only; legacy table untouched. | PC-3; BD-07 |
| FR-INT-02 | CAP-04 | Must | R1 | Delivered | 67 REPLAY to NOOP_DUPLICATE; natural key per OD-18. | PCH-03; PCH-05 |
| FR-INT-03 | CAP-04 | Must | R1 | Delivered | REVISED_CONFLICT quarantine (fixtures; 0 on shipped data). | PC-3 |
| FR-INT-04 | CAP-04 | Must | R1 | Changed | Contract binding per source, default `record_only` (no quarantine on contract miss); `enforce` optional via ZH-10; contract fails 3 of 4 sources. | PCH-04; OD-28 (record_only everywhere) |
| FR-INT-05 | CAP-04 | Must | R1 | Delivered | Exact-key matching only; most partner items UNMATCHED_REF (7,903) - specified behaviour. | PCH-06; DV-10 |
| FR-INT-06 | CAP-04 | Must | R1 | Delivered | Enumerated reason codes and queues, deterministic. | PC-3 |
| FR-INT-07 | CAP-04 | Must | R1 | Delivered + Deferred part | Deferred part: static build-failing check AC-INT-23 (no later evidence it was built). Delivered: runtime Untrusted guard (E-INT-UNTRUSTED-USE) + planted-string tests. | PCH-43 |
| FR-ID-01 | CAP-05 | Must | R1 | Delivered | 168 exact-key links; case-to-batch links are human-only. | PCH-29 |
| FR-ID-02 | CAP-05 | Must | R1 | Delivered | No fuzzy linking; manual link = event. | PC-3 |
| FR-RUN-01 | CAP-06 | Must | R1 | Changed | Delivered: authorised manual trigger. Changed/Deferred: schedule mechanism built but OFF; flag only via ZH-09; `schedule.enabled: true` refused in config; switching on = CUT-5, OPD-11/HAR-10 open. | PCH-16; OD-19 |
| FR-RUN-02 | CAP-06 | Must | R1 | Delivered | Append-only run records (M005). | PC-3 |
| FR-RUN-03 | CAP-06 | Must | R1 | Delivered | Explicit cap, exact backlog, checkpoint/resume. | PC-3 |
| FR-MET-01 | CAP-07 | Must | R1 | Delivered | Definition tag + policy version + 'synthetic, unvalidated' label; tags are null until a definition is adopted. | PC-3 |
| FR-MET-02 | CAP-07 | Must | R1 | Delivered | Cross-tag combination refused. | TST-MET |
| FR-MET-03 | CAP-07 | Must | R1 | Delivered | Median/p90 per clock built; value `null` on baseline (`no_completed_cycles`). | PCH-17 |
| FR-MET-04 | CAP-07 | Must | R1 | Delivered | Decimal; cut-off and denominator required; synthetic value 622,826.44 (n 125) vs legacy report 742,956.61 (DV-01). | PCH-18 |
| FR-MET-05 | CAP-07 | Should | R1 | Delivered + Deferred part | Deferred part: D-EVID backlog returns `E-MET-NOT-AVAILABLE` (needs evidence check). Delivered: D-OPS backlog by site. | PCH-17; DEV-69 |
| FR-MET-06 | CAP-07 | Must | R1 | Delivered | KPIs reproducible from stored inputs; labelled. | PC-3 |
| FR-REV-01 | CAP-08 | Should | R1 | Delivered | Template rule-trace text. Stage 17 gap 'no automatic producer' was addressed at Stage 20 DW-08 by an operator command (`hub.web produce-traces`, S20-DEV-07); still not an automatic background producer. | PCH-23; application-readiness DW-08 |
| FR-REV-02 | CAP-08 | Must | R1 | Delivered | Reviewer exception queue; human walkthroughs TST-REV-03/04/08 UNSIGNED. | PC-3; OD-24; walkthrough-records |
| FR-SEC-01 | CAP-09 | Must | R1 | Delivered | Deny-by-default 48-route registry; PBKDF2, lockout, CSRF, loopback; control values are agent proposals; Stage 27 added 401/400/408/429/503 behaviours (agent assumptions, OD-34). | PCH-24; OD-32; OD-34 |
| FR-SEC-02 | CAP-09 | Must | R1 | Delivered | Hash-chained audit; verify-audit ok; anchor is an unsigned local file by default (opt-in seal); F-29-01 fix gives exit 17 on malformed anchor line (S30-DEV-01, acceptance OPEN). | RTD-29; OD-37 |
| FR-CO-01 | CAP-10 | Must | R1 | Delivered | Characterisation harness 134/134; Stage 20 DW-04 replaced declared probes with observed (13 probes, 0 declared, D5 = 0); `golden-compare` exits 6 by design because DV-01..DV-11 are unapproved (G1 FAIL). | PCH-26; application-readiness DW-04; gate-results G1 |
| FR-CO-02 | CAP-10 | Must | R1 | Delivered | coexistence_inventory protected; owner of the parallel workflow Unknown (OPD-15, PA-26 VACANT). | TST-CO-08; PA-26 |
| FR-CO-03 | CAP-10 | Should | R1 | Delivered | Rollback L1/L2/L3 rehearsed on sandbox copies only (Stage 30 T-02..T-04); release gate G1 fails, T-09, T-10 fail, T-05 not run. | PCH-28; go-no-go-criteria |
| FR-CO-04 | CAP-10 | Must | R1 | Delivered + Deferred part | Deferred part: CI wiring of the No-AI check (`ci/hub-hardening.yml` NOT installed, HAR-07). Delivered: deny-list, egress guard, `model_calls_total = 0`, zero third-party deps. | PCH-27; OD-34 |
| FR-POL-05 | CAP-03 | Should | R2 | Delivered | Built dark (served by R2WebApp only); 3 of 125 differ. | PCH-20; DEV-97 |
| FR-INT-08 | CAP-04 | Should | R2 | Delivered | Built dark; thresholds 4 h / 24 h are Assumptions. | PCH-20; PCH-32 |
| FR-ID-03 | CAP-05 | Should | R2 | Delivered | Built dark; no CONSISTENCY policy adopted, so no findings. | PCH-30 |
| FR-ID-04 | CAP-05 | Should | R2 | Delivered | Built dark (R2WebApp only). | PCH-20; DEV-92 |
| FR-MET-07 | CAP-07 | Should | R2 | Delivered | Built dark (R2WebApp only). | PCH-20; DEV-100 |
| FR-MET-08 | CAP-07 | Could | R2 | Deferred | Not built; `OP-MET-05` returns `E-MET-NOT-AVAILABLE`; needs a cost source and owner (OPD-08). | PCH-19; DEV-82 |
| FR-REV-03 | CAP-08 | Should | R2 | Delivered | Built dark: `search.enabled` false, `search.fts` off; ranking quality unassessed; FTS5 on target runtime Unknown. | PCH-20; RTD-79/80 |
| FR-REV-04 | CAP-08 | Could | R2 | Delivered | Built dark (`templates.enabled` false); field sets illustrative. Dinesh ruled in OD-25: keep as Could / R2 (built, switched off). | PCH-22; OD-25 |
| FR-SEC-03 | CAP-09 | Should | R2 | Delivered | Built dark: classes C0..C3, C3 read needs a reason; map is PROPOSED; finance_read masking path unreachable by any route. | PCH-25; RTD-82/83 |

Every row is [Verified Fact] for the cited state; confidence High for Stage 17 states, Medium for 'still true at 08add05' (A-43-01). Class: 35 class-B tests ran on non-adopting defaults and 9 class-C tests are sandbox proxies (finalized-acceptance-criteria), so 'Delivered' is mechanism-level only.

### DM-4 Disposition of the 20 product NFRs (PNFR-01..PNFR-20) and non-FR baseline items
| PNFR | Requirement (short) | As-built state | Disposition | Class |
|---|---|---|---|---|
| PNFR-01 | Availability 99.5 % (Assumption) | Mechanism only | Delivered (mechanism) | Unknown in practice: no host, no telemetry |
| PNFR-02 | Reconcile by 06:00, 100 % of nights | Unprovable while schedule is OFF | Delivered (mechanism); schedule OFF | Unknown |
| PNFR-03 | Partner item accepted within 4 h (config threshold, Assumption) | Built R2 dark | Changed (target became config, PCH-32) | Assumption |
| PNFR-04 | Stale signal 24 h; 'risk signal' undefined | Built R2 dark | Changed (PCH-32) | Assumption / Unknown |
| PNFR-05 | RTO 8 h / RPO 24 h (Assumption) | Restore rehearsed on sandbox copies; Stage 29 later set agent targets RTO 4 h / RPO 1 working day | Delivered (rehearsal); targets UNRECONCILED (see AB-3) | Assumption |
| PNFR-06 | Latency measured, no threshold | Measure-only | Changed (confirmed measure-only, PCH-33; OPD-14 open) | Verified Fact |
| PNFR-07 | 100 % endpoints authenticated/authorised | 48-route deny-by-default registry; shadow/loopback | Delivered | Verified Fact (sandbox) |
| PNFR-08 | Secret scan 0; non-loopback needs TLS and approval | No TLS exists; non-loopback refused even with approval (PCH-45); refusal mutant H5 killed at Stage 23 | Delivered (partly met: no TLS) | Verified Fact |
| PNFR-09 | Audit (framing, not Part 11) | verify-audit ok; tamper detected; anchor unsigned by default | Delivered | Verified Fact (sandbox) |
| PNFR-10 | 0 deletions while no retention policy | Insert-only triggers; hold-all | Delivered | Verified Fact |
| PNFR-11 | 0 duplicate effects on replay | 10,983 raw; 67 REPLAY to NOOP | Delivered | Verified Fact (synthetic) |
| PNFR-12 | Field classes covered by access test (R2) | Built R2 dark; map PROPOSED | Delivered (dark) | Verified Fact / Assumption |
| PNFR-13 | 0 effects from planted strings | Reworded to 86 feed rows + 22 injection documents + 10 variants; 44-string fixture not built | Changed (reword approved, OD-25) | Verified Fact |
| PNFR-14 | 100 % runs have records; every R1 KPI computed | Run records met; metrics not exported/persisted (Stage 31 modules built, not wired) | Delivered + Deferred part (export/persistence) | Verified Fact |
| PNFR-15 | 100 % rule outputs show trace + override | Traces via operator command; walkthroughs unsigned | Delivered with gap | Verified Fact |
| PNFR-16 | KPIs documented; re-run identical | Met | Delivered | Verified Fact |
| PNFR-17 | Determinism; goldens pass | Met on reference runtime 3.10.12; CT-13 fails on Node patch drift (S24-DEV-04) | Delivered (one registered environment failure) | Verified Fact |
| PNFR-18 | No AI: 0 model calls | Met; manual gate, not in CI | Delivered | Verified Fact |
| PNFR-19 | Rollback rehearsed; replay gate | Rehearsed; G1 red by design; no CI | Delivered with gaps | Verified Fact |
| PNFR-20 | 100 % outputs labelled 'synthetic, unvalidated' | Met for metrics; R2 pages/search label not separately verified | Delivered (R2 label Unknown) | Verified Fact / Unknown |

[Verified Fact] Source: `docs/17-implementation-prd/finalized-nfrs.md` (Stage 17), updated by OD-25 (PNFR-13 reword), Stage 23/27/30/31 documents as cited. 17 PNFR are R1 and 3 are R2 (PCH-02).

Non-FR baseline items that were **Superseded**: (a) constraint CON-04 'code change not ready until R-1, R-2, R-4, R-5' (superseded by the INC-01 harness, PCH-37); (b) the Stage 12 brief's '41/11' count (PCH-02); (c) ADR-018's blanket 'Python 3.12' for the code floor (production target 3.12+, code floor 3.10, OD-24, PCH-36). No requirement was **Rejected**.

### DM-5 Items built that no Stage 9 FR requires (added scope, for traceability)
| ID | Item | Evidence | State |
|---|---|---|---|
| BX-01 | Approval-gated authority switch (`capability_authority.<cap>`, DW-17), decision-flag `approval_ref` rule, exposure approval | `hub/control/flags.py`; `docs/23-human-control/approval-gates.md`; OD-26, OD-31 | Built, ships OFF; CLI + approval_ref (ZH-11 not adopted) |
| BX-02 | Resilience mechanisms (retry/breaker, bounded listener, budget) | `hub/resilience/`; `docs/28-reliability/resilience-readiness.md` | Built, NOT wired into gateway-pull / serve |
| BX-03 | Observability modules, SLO candidates, alert catalog | `hub/obs/`; `docs/31-observability/` | Built, NOT wired; no SLA |
| BX-04 | Release go/no-go evaluator | `hub/release/`; `docs/30-release/` | Built, NOT wired; returns NO-GO |
| BX-05 | Hardening (rate limit 429, 408/503/400/401 behaviours, restricted-note placeholder, insert-only `schema_migrations` triggers) | `docs/27-hardening/`; OD-34 | Built; behaviours are agent assumptions, not approved |
[Verified Fact] for existence and wiring status as cited; these are additive to the PRD and were not approved as requirements.

## Evidence References
`docs/09-initial-prd/functional-requirements.md`; `docs/17-implementation-prd/prioritized-capabilities.md` PC-3; `prd-change-log.md` PCH-01..PCH-48; `finalized-acceptance-criteria.md`; `docs/13-traceability/requirements-traceability-matrix.md`; `docs/20-application/application-readiness.md`; OD-10, OD-16, OD-19, OD-25, OD-29, OD-31.

## Assumptions
- A-43-01 [Assumption] Per-FR states from Stage 17 hold at main 08add05 except where a later stage document closed the gap (POL-01 withdrawal, CO-01 observed probes, REV-01 producer command). Confirm: Engagement lead (Dinesh Naik) / orchestrator full regression.
- A-43-02 [Assumption] The meaning given to 'Delivered' (built in shadow, not released) is acceptable to Dinesh.

## Unknowns
- U-43-01 Whether each FR's acceptance tests still pass at 08add05 (no test run here). Resolve: orchestrator full regression (OD-23).
- U-43-02 Per-FR re-check for Stage 27 behaviour changes (401/400/408/429/503) against Stage 12 text: no spec addendum exists (D-27-05).

## Unresolved Issues
- FR-REV-04 keep/reject was ruled 'keep' in OD-25 but remains a Could R2 built-dark item; FR-MET-08 stays Deferred; 12 FR rows carry 'accepted open' decisions (see register).
- DV-01..DV-11 preserve-or-fix (all OPEN) decide whether the Changed rows become approved changes.

## Residual Risks
- RR-DM-1 'Delivered' misread as 'released/accepted' (High if the label is dropped). Mitigation: the release-state column and header label.
- RR-DM-2 Row states are documentary and one stage stale for post-17 changes (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
