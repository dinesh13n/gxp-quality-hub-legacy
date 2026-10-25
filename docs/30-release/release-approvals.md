---
stage: "30 — Release / Cutover / Rollback"
artifact: "release-approvals.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/30-release/evidence/approvals-register.json", "hub/release/gonogo.py", ".fde/orchestrator-decisions.md (OD-32..OD-36)", "docs/14-transformation/cutover-plan.md", "docs/17-implementation-prd/implementation-prd.md"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Stage 30 PREPARES and REHEARSES a release; it does not release, cut over, merge to production, tag, install CI, flip a shipped switch or approve anything. Every approval below is OPEN and belongs to Dinesh Naik (Engagement lead, the only human, OD-04). Defaults marked 'recommended' are agent proposals under OD-32 (scope choices only), not decisions. `zone_h.holders` ships EMPTY. The product is No-AI (OD-08).**

## Summary
**No approval exists and none is recorded.** The machine-readable register (`evidence/approvals-register.json`) holds 40 records, all OPEN. This document lists them with the agent's recommended default so Dinesh can decide quickly; a recommendation is not a decision. G1..G10 gate evidence is shown in `go-no-go-criteria.md`; the human acknowledgement of each gate (AP-GATE-*) stays open. DV-01..DV-11 are not accepted; CUT-1..CUT-5 are not decided. Open items from Stages 26-37 are carried below, unchanged.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AP-1 Approval register (40 records, 0 approved) [Verified Fact]
| ID | Decision | Scope | Agent recommended default (not a decision) | Status |
|---|---|---|---|---|
| AP-REL-01 | Release decision (go / no-go) for the hub in shadow mode | REL | no-go until every technical criterion passes and AP-GATE-*, AP-OPS-* (REL) are recorded | OPEN |
| AP-GATE-G1 | Human acknowledgement of the evidence for gate G1: golden diff: unapproved differences = 0 | REL | acknowledge only after reading the evidence file named in gate-results.json; G1 cannot pass while any DV row is proposed | OPEN |
| AP-GATE-G2 | Human acknowledgement of the evidence for gate G2: replay-safety suite (AC-INT-04/05) passes | REL | acknowledge after reading the evidence file named in gate-results.json | OPEN |
| AP-GATE-G3 | Human acknowledgement of the evidence for gate G3: verify-audit ok | REL | acknowledge after reading the evidence file named in gate-results.json | OPEN |
| AP-GATE-G4 | Human acknowledgement of the evidence for gate G4: verify-projection 0 mismatches | REL | acknowledge after reading the evidence file named in gate-results.json | OPEN |
| AP-GATE-G5 | Human acknowledgement of the evidence for gate G5: No-AI tripwire: deny-list clean, no egress, model_calls_total = 0 | REL | acknowledge after reading the evidence file named in gate-results.json | OPEN |
| AP-GATE-G6 | Human acknowledgement of the evidence for gate G6: secret scan 0; deletion-path grep 0 | REL | acknowledge after reading the evidence file named in gate-results.json | OPEN |
| AP-GATE-G7 | Human acknowledgement of the evidence for gate G7: backup/restore rehearsal checksum match | REL | acknowledge after reading the evidence file named in gate-results.json | OPEN |
| AP-GATE-G8 | Human acknowledgement of the evidence for gate G8: Zone H negative tests (AC-GATE-09/11/12) pass | REL | acknowledge after reading the evidence file named in gate-results.json | OPEN |
| AP-GATE-G9 | Human acknowledgement of the evidence for gate G9: planted-string fixture suite (86/22/44) 0 effects | REL | acknowledge after reading the evidence file named in gate-results.json | OPEN |
| AP-GATE-G10 | Human acknowledgement of the evidence for gate G10: determinism: bit-identical across PYTHONHASHSEED/TZ/locale | REL | acknowledge after reading the evidence file named in gate-results.json | OPEN |
| AP-DV-01 | Preserve-or-fix decision for DV-01: SQL month-end total 742,956.61 (join fan-out) becomes 622,826.44 | CUT step CUT-4 | fix (adopt the hub figure) for CUT-4; keep legacy report running as comparator | OPEN |
| AP-DV-02 | Preserve-or-fix decision for DV-02: replayed message: legacy DUPLICATE 64 becomes NOOP_DUPLICATE 67 / REVISED_CONFLICT | CUT step CUT-3 | fix | OPEN |
| AP-DV-03 | Preserve-or-fix decision for DV-03: quantity out of range: legacy REJECTED 154 becomes NEGATIVE_VALUE flag, item kept | CUT step CUT-3 | change of class: adopt as built | OPEN |
| AP-DV-04 | Preserve-or-fix decision for DV-04: Java blank amounts: silently skipped becomes UNPARSABLE_AMOUNT quarantine | CUT step CUT-4 | fix | OPEN |
| AP-DV-05 | Preserve-or-fix decision for DV-05: JS tolerance with 'abc' / null becomes E-POL-INPUT-INVALID | CUT step CUT-2 | fix | OPEN |
| AP-DV-06 | Preserve-or-fix decision for DV-06: unknown region / year 999999 becomes the same value marked defaulted | CUT step CUT-2 | accept the additive marker | OPEN |
| AP-DV-07 | Preserve-or-fix decision for DV-07: reconcile overwrites status in place becomes append-only outcomes (DV-07a: outcome classification EXCEPTION 8,109 etc.) | CUT step CUT-3 | fix, after Dinesh has seen the 7,903 UNMATCHED_REF volume | OPEN |
| AP-DV-08 | Preserve-or-fix decision for DV-08: night-shift distinct objects 118 vs 500 (reference query, no batch job built; weak evidence) | CUT step CUT-4 | do not cut over this figure; keep legacy authoritative until a hub job exists | OPEN |
| AP-DV-09 | Preserve-or-fix decision for DV-09: invalid gateway event: counted, not stored becomes quarantined, stored (label MISSING_ENVELOPE_FIELD) | CUT step CUT-3 | fix, with the corrected label | OPEN |
| AP-DV-10 | Preserve-or-fix decision for DV-10: partner outcomes: exact ref_id matching, most legacy-ACCEPTED rows become EXCEPTION / UNMATCHED_REF (proposed row) | CUT step CUT-3 | fix (exact match, BEH-INT-08) | OPEN |
| AP-DV-11 | Preserve-or-fix decision for DV-11: JS partial-year threshold: prefix match 15000 becomes 999999 defaulted (proposed row, DEV-29) | CUT step CUT-2 | fix (4-digit year required) | OPEN |
| AP-CUT-1 | Decision to make 'decision and evidence record, audit' authoritative (CUT-1) | CUT-1 | decide last of the value-bearing steps only after the Zone H and closure questions are answered; keep shadow until then | OPEN |
| AP-CUT-2 | Decision to make 'rule evaluation' authoritative (CUT-2) | CUT-2 | first step in the recommended order (CUT-2, CUT-1, CUT-3, CUT-4, CUT-5); needs DV-05, DV-06, DV-11 and OD-S12-04 | OPEN |
| AP-CUT-3 | Decision to make 'intake and reconcile outcomes' authoritative (CUT-3) | CUT-3 | after CUT-1 and CUT-2; needs a named consumer and a decision to stop the in-place legacy reconcile | OPEN |
| AP-CUT-4 | Decision to make 'metrics, month-end and night-shift figures' authoritative (CUT-4) | CUT-4 | after CUT-3; needs consumers named and the OD-S12-01/-02/-08 definitions | OPEN |
| AP-CUT-5 | Decision to make 'automation and exposure' authoritative (CUT-5) | CUT-5 | last; keep loopback-only and the scheduler off unless Dinesh decides otherwise (D-27-09, HAR-10) | OPEN |
| AP-OPS-01 | target host and promotion path named and approved (environment-promotion-plan.md) | REL | there is no production host; name one or accept shadow-on-the-laptop as the only environment | OPEN |
| AP-OPS-02 | rollback authority, rollback triggers and who may call them | REL | Dinesh is the only rung (F-29-07); record that explicitly | OPEN |
| AP-OPS-03 | cutover window, change freeze and communications | REL | no window exists; choose one only when a real consumer exists | OPEN |
| AP-OPS-04 | off-device copy of the baseline and the hub backups (HAR-09, F-29-02) | REL | approve an encrypted off-device copy (HAR-09) or accept the single-device risk in writing | OPEN |
| AP-OPS-05 | monitoring owner and alert channel for the release window (D-31-08, F-29-03) | REL | manual evaluation (RB-00) until a second human exists (D-31-08) | OPEN |
| AP-OPS-06 | manual walkthroughs TST-REV-03 / 04 / 08 signed or explicitly left open (D-27-08) | REL | leave open and say so, or perform and sign the three walkthroughs | OPEN |
| AP-OPS-07 | runtime floor and Python 3.12+ evidence (D-27-02) | REL | keep the 3.10 floor as shipped; run 3.12 / 3.13 evidence in the orchestrator cloud before any exposure | OPEN |
| AP-OPS-08 | install the hardening CI file under .github with pinned SHAs, or not (D-27-03, HAR-07) | REL | do not install CI now; decide with the SHA pins when a remote exists | OPEN |
| AP-OPS-09 | legacy Dockerfile / compose hardening, or leave the legacy files as they are (D-27-06) | REL | leave the legacy files unchanged (frozen path); the hardened recipe is in deployment-strategy.md as a proposal | OPEN |
| AP-OPS-10 | wire the Stage 28 / 31 mechanisms before release, or release without them (D-28-01, D-28-02, D-31-01, D-31-02) | REL | release without wiring (as built); wiring is a separate approved change | OPEN |
| AP-OPS-11 | residual risks RS / RP / VA / RTR / F-xx accepted, rejected or carried (none is accepted by any stage) | REL | carry every risk as open; accept none by default | OPEN |
| AP-OPS-12 | consumers of the legacy outputs identified and a re-pointing owner named (U-14-01) | CUT-2/CUT-3/CUT-4 | name the consumers or keep CUT-2..CUT-4 closed | OPEN |
| AP-OPS-13 | real Zone H holders named, only if the Zone H gate is to be used (OD-S12-05 / 06, HAR-12) | CUT-1 | keep holders empty; the Zone H gate stays unused | OPEN |

### AP-2 Decisions carried from earlier stages (Dinesh-owned) [Verified Fact]
| ID | Decision | Recommended default | Stage 30 disposition |
|---|---|---|---|
| D-27-01 | restricted-evidence read rule (F-02) | withhold from roles that may not read the record (as built) | carried, **not implemented or decided** by Stage 30 |
| D-27-02 | adopt Python 3.12 floor before exposure | keep floor 3.10; gather 3.12/3.13 evidence in the cloud | carried, **not implemented or decided** by Stage 30 |
| D-27-03 | install `ci/hub-hardening.yml` under .github with SHA pins (HAR-07) | not installed (Stage 30 did not install it) | carried, **not implemented or decided** by Stage 30 |
| D-27-04 | rate-limit defaults (100 refusals / 60 s) | as built | carried, **not implemented or decided** by Stage 30 |
| D-27-05 | spec addenda for new error codes and config sections | none written | carried, **not implemented or decided** by Stage 30 |
| D-27-06 | harden legacy Dockerfile / compose / env examples (VR-04) | leave unchanged; proposal in deployment-strategy DS-5 | carried, **not implemented or decided** by Stage 30 |
| D-27-07 | 9 complex functions over 15 | backlog; ratchet test | carried, **not implemented or decided** by Stage 30 |
| D-27-08 | sign or reject walkthroughs TST-REV-03/04/08 | unsigned | carried, **not implemented or decided** by Stage 30 |
| D-27-09 | TLS / exposure | stay loopback | carried, **not implemented or decided** by Stage 30 |
| D-28-01 | wire GuardedGateway into gateway-pull, persist breaker state | not wired (separate approved change) | carried, **not implemented or decided** by Stage 30 |
| D-28-02 | wire BoundedLoopbackServer into web/r2 serve, cap 64 | not wired | carried, **not implemented or decided** by Stage 30 |
| D-28-03 | confirm retry/breaker/budget defaults once a real source exists | before real data | carried, **not implemented or decided** by Stage 30 |
| D-28-04 | late-delivery catch-up | manual idempotent catch-up now | carried, **not implemented or decided** by Stage 30 |
| D-28-05 | shape errors fail fast | yes, as built | carried, **not implemented or decided** by Stage 30 |
| D-28-06 | capacity, freshness, RTO/RPO targets | SLO candidates only | carried, **not implemented or decided** by Stage 30 |
| D-28-07 | approved host for disk-full / power-loss injection | open | carried, **not implemented or decided** by Stage 30 |
| D-28-08 | CT-18 container restart (HAR-05) | keep NOT-RUN | carried, **not implemented or decided** by Stage 30 |
| D-28-09 | lower SQLite busy_timeout 30 s to 5 s | not changed (behaviour change) | carried, **not implemented or decided** by Stage 30 |
| D-28-10 | freshness indicator on reads | not built | carried, **not implemented or decided** by Stage 30 |
| D-31-01 | persist HTTP metrics periodically | not built (edit to hub/web/app.py) | carried, **not implemented or decided** by Stage 30 |
| D-31-02 | wire resilience_samples with GuardedGateway | together with D-28-01; not built | carried, **not implemented or decided** by Stage 30 |
| D-31-03 | SLO-02 100 % vs 95 % | 95 % candidate, 100 % stays the requirement | carried, **not implemented or decided** by Stage 30 |
| D-31-04 | read-only /metrics route | defer | carried, **not implemented or decided** by Stage 30 |
| D-31-05 | log destination and hold-all retention | launcher appends to a file; no deleting rotation | carried, **not implemented or decided** by Stage 30 |
| D-31-06 | export the six gap metrics | after the F-29-01 fix (now done); not built | carried, **not implemented or decided** by Stage 30 |
| D-31-07 | send X-Correlation-Id on gateway GET | not changed (hub/adapters edit) | carried, **not implemented or decided** by Stage 30 |
| D-31-08 | alert channel / on-call | none until a second human exists | carried, **not implemented or decided** by Stage 30 |
| D-31-09 | emit or retire 17 never-emitted log events | not changed | carried, **not implemented or decided** by Stage 30 |
| D-31-10 | re-derive SLO numbers after 30 days of real use | after first real use | carried, **not implemented or decided** by Stage 30 |

### AP-3 Other open items routed to Stage 30 or the release [Verified Fact]
- Stage 26: F-01..F-11 remainder (F-11 open), RTR-01..RTR-15, walkthrough sign-off (AP-OPS-06), no 3.12+ evidence (AP-OPS-07), mutants M5/M9/M10 survive.
- Stage 29: Q-29-01..09 and C-1..C-7 (off-device backup HAR-09 = AP-OPS-04; live tabletop; RTO/RPO agent targets); F-29-01 FIXED here (S30-DEV-01); F-29-11 answered as Inference (DS-6); F-29-12 answered (RB-4); F-29-02..10, 13..16 open.
- Stage 33: VA-01..VA-07 proposed vendor-risk acceptances, none accepted. Stage 37: no accepted owners, all roles but Dinesh vacant. Stages 34-36: after-window absent, ROI not computable, benefits sign-off unsigned.
- Risk registers RS-01..RS-16, RP-01..RP-12 remain open; none accepted (AP-OPS-11).

### AP-4 How an approval is recorded [Inference]
Dinesh (or someone he names in writing) edits `approvals-register.json`: `status: APPROVED`, `approver` (his name), `approval_ref` (e.g. an OD id or message reference), `approved_on` (YYYY-MM-DD), `evidence_ref` (where the decision text lives). `python -m hub.release evaluate` then counts it. The tool cannot verify identity; the safeguard is that the entry is a visible, reviewable, git-tracked edit by a human.

## Evidence References
`go-no-go-criteria.md`; `.fde/orchestrator-decisions.md`; Stage 27/28/29/31 decision tables.

## Assumptions
- A-30-08 [Assumption] Recommended defaults follow earlier stages' recommendations; where none existed the agent chose the non-adopting option (OD-32).

## Unknowns
- U-30-08 whether Dinesh wants per-gate acknowledgement (AP-GATE-*) or one release decision.

## Unresolved Issues
- All 40 records and all 29 carried decisions are open.

## Residual Risks
- RR-30-7 Decision fatigue: 69 open items; the register groups them so the REL set (22) and each CUT set (1-7) can be decided separately.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 30). |
