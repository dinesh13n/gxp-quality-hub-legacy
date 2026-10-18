---
stage: "14 — Transformation / Migration Plan"
artifact: "cutover-plan.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/12-specs/features/f10-coexistence-change-safety.md (DV-01..DV-09, G1..G10, BEH-CO-05 CO-WF-01)", "docs/12-specs/spec-readiness.md RD-3/RD-4", "docs/10-architecture/adrs/ADR-003, ADR-006, ADR-010, ADR-015", "docs/07-repo-assessment/critical-workflow-inventory.md (CW-01..CW-14)", "docs/07-repo-assessment/repo-transformation-readiness.md (heat map: 'consumers unknown')", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md (HAR-05/06/10/11/12)", "docs/14-transformation/coexistence-strategy.md, feature-flag-plan.md, rollback-strategy.md"]
supersedes: "none"
---
## Summary
**Label: synthetic repository; DRAFT plan, not an approval. Cutover is executed in Stage 30, not Stage 15.**
There is **no big-bang cutover**. Stage 15 (INC-01..INC-08) ends with the hub fully built **in shadow**; nothing a user or downstream consumer relies on changes. Authority then moves **per capability** in five independent cutover steps (CUT-1..CUT-5), each gated by the specific preserve-vs-fix (DV) and OD-S12 decisions it needs, a Stage 16 behaviour comparison with zero unexplained differences, and a rehearsed L3 rollback. Legacy decommissioning is **not planned** here: legacy keeps running read-only-to-hub as comparator and fallback, and the protected parallel workflow CO-WF-01 is never touched (BEH-CO-05).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### CO-1 Cutover steps
| Step | Capability → hub authoritative | Legacy counterpart (unchanged code) | DV items that change visible behaviour | Decisions required (owner: Engagement lead (Dinesh Naik)) | Verification | Rollback (L3) | Tag |
|---|---|---|---|---|---|---|---|
| CUT-1 | Decision & evidence record (C3) + audit (C2); Zone H gate stays `none` unless OD-S12-05/06 decided | **none** (CW-14 absent) | none (net-new) | OD-S12-14 PRD/ADR approval; OD-S12-01, -03, -07, -15, -16, -19; Stage 23-27 security/TEVV; for Zone H use: OD-S12-05, -06 + HAR-12 | G1..G10 green; TST-DEC/GATE/SEC executed in Stage 16/26 | authority flag → shadow; recorded events retained & reviewed | [Verified Fact] CW-14; [Inference] rest |
| CUT-2 | Rule evaluation (priority, manual review, JS threshold) | `app/legacy_logic.py`, `legacy_js/legacy_policy.js` | DV-05 (fix), DV-06 (additive marker) | OD-S12-04 (rule authority, active set, fix-vs-preserve), OD-S12-13 for DV-05/06, HAR-06 | TST-CO-03 zero diff on preserved sets; only approved DV diffs | flag back; legacy still computes | [Inference] |
| CUT-3 | Intake & reconcile outcomes | `app/gateway_bridge.py`, `app/partner_feeds.reconcile`, `app/historical_estate.py` | DV-02, DV-03, DV-07, DV-09 | OD-S12-11, OD-S12-17, OD-S12-13 per DV, HAR-06; operational decision to stop running legacy in-place reconcile (it overwrites state, DV-07) | G2 replay-safety; DM-3 outcome sums; Stage 16 diff | resume legacy reconcile on a restored copy; hub back to shadow | [Inference] |
| CUT-4 | Metrics / month-end / night shift figures | `app/baseline.py`, `legacy_java/`, `sql/legacy_reports.sql`, `legacy_batch/shift_reconciliation.py` | DV-01, DV-04, DV-08 | OD-S12-01, -02, -08 (definitions, clock, cut-off), OD-S12-13, HAR-06; identification of consumers (U-14-01) | figures reconciled: legacy value, hub value, explained delta (e.g. 742,956.61 → 622,826.44 fan-out) | consumers re-pointed to legacy report | [Verified Fact] DV-01 values |
| CUT-5 | Automation & exposure: enable schedule; bind beyond loopback | none | none | OD-S12-10 (+HAR-10), HAR-05, Stages 23-25 | run records; exposure approval_ref | `schedule.enabled=false`; bind 127.0.0.1 | [Inference] |

Order recommendation: CUT-2 → CUT-1 → CUT-3 → CUT-4 → CUT-5 (rules first because every other capability evaluates them; exposure last). Each CUT is independently revertible; none requires another to stay cut over except CUT-1 → CUT-2 rule dependency (if CUT-2 is reverted, CUT-1 records rule traces against the as-found set, which is identical by TST-CO-03). [Inference]

### CO-2 Cutover runbook skeleton (per step, completed in Stage 30)
1. Entry: all decisions in the row recorded with approval_ref (HAR-11); Stage 16 comparison report shows 0 UNEXPLAINED and every DV used is `approved`.
2. Backup hub + anchor (checksummed); verify legacy backup manifest (STOP-01).
3. Flip `capability.<cap>.authority=authoritative` (audited CONFIG_CHANGED).
4. Re-point the consumer (who/what is Unknown, U-14-01) — **cannot be planned concretely until a real consumer exists**.
5. Verification window: run legacy and hub in parallel; daily golden-compare; any UNEXPLAINED → L3 rollback.
6. Exit: Dinesh records acceptance; legacy keeps running as comparator.

### CO-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| CF-1 | No consumer of legacy outputs is identifiable in the repo | heat map "consumers unknown" | CUT-2..CUT-4 step 4 cannot be concretely planned | Medium | High | U-14-01 |
| CF-2 | CUT-1 has no legacy counterpart → no behaviour comparison possible; verification relies on acceptance tests only | CW-14 | higher validation burden (Stage 26 TEVV) | Medium | High | — |
| CF-3 | Every DV is `proposed`, none approved | F10-2 | no CUT-2..CUT-4 can happen today | — (by design) | High | OD-S12-13 |
| CF-4 | A big-bang alternative (switch all at once) has no justification: it couples 9 DV decisions and removes per-capability rollback | DV list | rejected | — | High | — |

## Evidence References
F10-2/F10-3; RD-3/RD-4; CW-01..CW-14; ADR-003/006/010/015; HAR list.

## Assumptions
- A-14-11 [Assumption] Legacy remains runnable as fallback throughout Stage 30. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-14-01 consumers; U-14-05 owner of CO-WF-01 (OPD-15).

## Unresolved Issues
- All CUT entry decisions open (by design; Stage 30).

## Residual Risks
- RR-CO-1 Shadow period without cutover delivers no business value; mitigated by CUT-1 (net-new decision record) being the first value-bearing step once approved.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial cutover plan (Stage 14). |
