---
stage: "17 — Finalise Implementation PRD"
artifact: "release-boundaries.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/09-initial-prd/mvp-scope.md, release-hypothesis.md, non-goals.md", "docs/14-transformation/cutover-plan.md (CUT-1..CUT-5), feature-flag-plan.md, transformation-gates.md", "docs/15-modernization/modernization-summary.md (INC-01..INC-09)", "docs/16-repo-validation/{repo-quality-gate,validation-signoff,security-scan-summary}.md", "hub/security/settings.py, hub/search/settings.py (shipped defaults, SS-02)", ".fde/orchestrator-decisions.md (OD-08, OD-16, OD-19, OD-20, OD-22, OD-24)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. A release boundary says what may be switched on, for whom, and on which decision; it does not approve anything. Owner of every decision below: Engagement lead (Dinesh Naik), unless the decision log records an answer.**

## Summary
Four boundaries are defined: **RB-0 Shadow implementation baseline** (what exists now: everything built, everything consequential off), **RB-1 Release 1 / MVP** (43 FRs + 17 PNFRs, entered step by step through CUT-1..CUT-4), **RB-2 Release 2** (9 FRs; 8 built dark, enabled per item), and **RB-3 Automation & exposure** (CUT-5). RB-4 maps each step to its prerequisite decisions and gates; RB-5 lists work that is outside every release (deferred) and RB-6 what is never in scope. The Stage 9 R1/R2 split is unchanged (PCH-02); the boundary change is that R2 is now **built but dark** (PCH-20) and that R1 automation (schedule) is held behind CUT-5 (PCH-16).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RB-0 Shadow implementation baseline (current, main 2f318be + OD-24)
| Aspect | Boundary | Evidence | Tag |
|---|---|---|---|
| Scope | All 10 capabilities; of 52 FRs: 49 built (incl. built-limited and R2 built dark), 2 partial (FR-POL-01 withdrawal, FR-RUN-01 schedule held), 1 not built (FR-MET-08) | prioritized-capabilities.md PC-3 | [Verified Fact] |
| Mode | shadow beside legacy; read-only adapters; no dual write; legacy code and `data/` byte-identical | architecture-conformance ADR-003; checksum rc 0 | [Verified Fact] |
| Switches (shipped defaults) | bind 127.0.0.1, exposure not approved; `zone_h.holders` []; `disposition.mode` none; no adopted policy; no active rule set; schedule OFF; contract bindings `record_only`; `case_creation.enabled` false; `workflow.transition_table` structural; `search.enabled` false, `search.fts` off, `templates.enabled` false | security-scan SS-02; PCH-04/07/13/14/15/16 | [Verified Fact] |
| Users | engagement lead only, sandbox copies only (OD-03a) | OD-04 | [Verified Fact] |
| Runtime | code floor Python 3.10 / SQLite 3.37; production target 3.12+ (OD-24) | NFR-RT | [Verified Fact] |
| Data | FX-BASE125, synthetic, unvalidated (OD-09) | — | [Verified Fact] |

### RB-1 Release 1 (MVP) - unchanged content, staged entry
- **Content** [Verified Fact]: 43 FRs (Stage 9 MV-2) and 17 PNFRs (MV-3); no item added or removed.
- **Entry** [Inference]: by cutover step, not all at once - CUT-1 (decision & evidence record + audit), CUT-2 (rule evaluation), CUT-3 (intake & reconcile outcomes), CUT-4 (metrics / month-end / night shift). Each step needs its own decisions and the exit criteria in `finalized-acceptance-criteria.md` FA-4.
- **R1 parts held back inside the release** [Verified Fact]: scheduled runs (FR-RUN-01 schedule, CUT-5), Zone H disposition use (FR-GATE-04/05 until holders and mode are decided), rule activation (FR-POL-04), definition/clock adoption (FR-POL-01/02), enforce binding (FR-INT-04).

### RB-2 Release 2 - built dark, enabled per item
| FR | Built | Switch / entry point | Enable prerequisite | Tag |
|---|---|---|---|---|
| FR-POL-05 divergence report | yes | R2WebApp / CLI | entry-point choice (RTD-81); RC-3/RC-4 owner aware it reports, not resolves | [Verified Fact] |
| FR-INT-08 delay / freshness | yes | R2WebApp (`?view=freshness`) | thresholds confirmed (PNFR-03/04) | [Verified Fact] |
| FR-ID-03 consistency findings | yes | operator command; OP-ID-05 | a CONSISTENCY policy adopted (Zone H) | [Verified Fact] |
| FR-ID-04 joined view | yes | R2WebApp | entry-point choice | [Verified Fact] |
| FR-MET-07 unmatched rate per source | yes | R2WebApp (OP-MET-06) | entry-point choice | [Verified Fact] |
| FR-REV-03 keyword / field search | yes, OFF | `search.enabled`, `search.fts` | labelled query set (OPD-12) and FTS5 on the 3.12+ target (RTD-79); fallback engine guaranteed | [Verified Fact] |
| FR-REV-04 templates | yes, OFF | `templates.enabled` | keep / reject decision (PCH-22) | [Verified Fact] |
| FR-SEC-03 field protection | yes | always on in R2WebApp | field map confirmed (Stage 24, RTD-83) | [Verified Fact] |
| FR-MET-08 cost attribution | **no** | — | cost source + owner (OPD-08) | [Verified Fact] |

### RB-3 Automation & exposure (CUT-5)
[Verified Fact] Switching on the schedule (ZH-09) needs OPD-11 / HAR-10 (accepted open, OD-22) and a holder; any bind beyond loopback needs HAR-05, TLS and Stage 23-25 decisions; one server entry point must be chosen first (RTD-81). Until then the product is loopback, manual-trigger only.

### RB-4 Cutover step -> prerequisites
| Step | Scope | Human decisions (all accepted open unless noted) | Engineering prerequisites | Rollback | Tag |
|---|---|---|---|---|---|
| CUT-1 | decision & evidence record + audit | OD-S12-01, -03, -07, -15, -16, -19; Zone H use needs OD-S12-05/06; PRD baseline approved (OD-22, decided) | FA-4 items 1-4; S16-D04 single Zone H check (P2) | authority flag -> shadow | [Verified Fact] (cutover-plan) |
| CUT-2 | rule evaluation | OD-S12-04 activation; OD-S12-13 for DV-05, DV-06, DV-11 (DEV-29); HAR-06 | TST-CO-03 zero diff on preserved sets; observed probes (FAC-05) | flag back; legacy computes | [Verified Fact] |
| CUT-3 | intake & reconcile | OD-S12-11 per source; OD-S12-17 (decided, OD-18); OD-S12-13 for DV-02, DV-03, DV-07(a), DV-09, DV-10 | G2 replay-safety; Stage 16 diff re-run | resume legacy reconcile on a restored copy | [Verified Fact] |
| CUT-4 | metrics / month-end / night shift | OD-S12-01, -02, -08; OD-S12-13 for DV-01, DV-04, DV-08; consumer identification | figures reconciled legacy vs hub with explained delta | consumers re-pointed to legacy report | [Verified Fact] |
| CUT-5 | schedule + exposure | OD-S12-10 / OPD-11, HAR-05, HAR-10; Stage 24 security decisions | runtime 3.12+ in production (OD-24, decided); CI; FAC-07/08 | schedule off; bind 127.0.0.1 | [Verified Fact] |

### RB-5 Outside every release (deferred; revisit stage)
FR-MET-08 cost attribution (OPD-08); `rule` fact derivation (OD-S12-15); case-creation path (OD-S12-19); strict transition table use (OD-S12-16); policy withdrawal (DEV-36); automatic rule-trace producer (RTD-69); static Untrusted check (AC-INT-23); service-token rotation hardening and C3 reason transport (Stage 24); structural cleanup S16-D03..D06 (before Stage 27); retention / archival (OD-S12-09); buy-vs-build evaluation (OPD-10).

### RB-6 Never in scope (non-goals unchanged)
NG-01 AI / LLM / ML / agentic capability (OD-08); NG-02 making, pre-filling or automating disposition, QA release or e-signature; NG-03 choosing a definition, clock, threshold or sufficiency rule for the organisation; NG-04 auto-closing cases or guessing links; NG-09 real data / people / systems in this engagement. [Verified Fact] (`docs/09-initial-prd/non-goals.md`).

## Evidence References
`docs/14-transformation/cutover-plan.md`; `docs/16-repo-validation/security-scan-summary.md` SS-02; prioritized-capabilities.md.

## Assumptions
- A-17-RB-1 [Assumption] Staged entry of R1 by CUT step (rather than one R1 release event) is the intended release model (as in the Stage 14 plan). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-17-RB-1 Who consumes legacy figures (needed for CUT-4); unknown in repo.
- U-17-RB-2 Calendar for any step (none exists).

## Unresolved Issues
- Every CUT step depends on accepted-open decisions; none can start now.

## Residual Risks
- RR-RB-1 R2 code built ahead of R1 decisions increases maintained surface without users (Low-Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
