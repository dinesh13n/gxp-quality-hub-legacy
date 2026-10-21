---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "autonomy-matrix.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/08-ai-qualification/minimum-agency-assessment.md MA-1", "docs/08-ai-qualification/deterministic-vs-ai-boundaries.md B-1", "docs/02-stakeholders/decision-rights-map.md", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md", "hub/gate/service.py", "hub/gate/actions.py", "hub/control/flags.py", "docs/23-human-control/autonomy-catalogue.json", "tests/hub/test_tst_hub_stg23_catalogue.py", ".fde/orchestrator-decisions.md OD-08, OD-29"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
Every material decision or action the built hub can take is placed on the Stage 8 agency ladder (A0..A5). **No decision is at a level above A1 for the system acting alone, except one fixed-procedure scheduled run (A3-lite, ships OFF).** All ten Zone H actions (ZH-01..ZH-10) are A5-prohibited for any automation: they can be written only by an interactive human who is a configured holder, re-authenticated, with an `authority_ref`. The shipped holder list is empty, so today every Zone H action is refused. No AI, model or prompt exists in the product (OD-08). Autonomy is not expanded beyond Stage 8: the matrix is a classification of what is built, and it adds no authority.

## Findings
### Agency ladder used (Stage 8, MA-1)
| Level | Meaning | In this hub |
|---|---|---|
| A0 | Passive: store, display, answer a query | reports, search (OFF), crosswalk view, status views |
| A1 | Flag or recommend; a human acts | rule trace + flags, exception queue, conflict flag, `capability_authority = shadow` |
| A2 | Draft for explicit human approval | template drafts (`templates.enabled` ships OFF, PCH-22) |
| A3 | Reversible action inside a fixed policy, human reviews after | only the scheduled intake / reconcile run (fixed procedure; ships OFF) |
| A4 | Multi-step planning with tools | not built; rejected (Stage 8) |
| A5 | Autonomous in a regulated decision | **prohibited** (HAR-12, STOP-07) |

### Decision inventory and autonomy level
Materiality: H = regulated decision or authority; M = changes what a reviewer sees or what is recorded; L = read-only. Reversibility: R = reversible by a later event; A = append-only (corrected only by a new, audited event); X = cannot be undone.

| ID | Decision / action | Mat. | Rev. | Level (system alone) | Who decides | Enforced by (code) | Tested by |
|---|---|---|---|---|---|---|---|
| AM-01 | ZH-01 batch disposition | H | A | A5 prohibited | human holder | `hub/gate/actions.py` `execute`, `hub/gate/service.py` `require_holder` | TST-GATE-05, STG23 S41/S42 |
| AM-02 | ZH-02 QA release | H | A | A5 prohibited | human holder | same | STG23 S41/S42 |
| AM-03 | ZH-03 e-signature record (records that a human acted; not a cryptographic or legal signature) | H | A | A5 prohibited | human holder | same | STG23 S41/S42 |
| AM-04 | ZH-04 close an exception | H | A | A5 prohibited | human holder | same | TST-DEC-15..28, S41 |
| AM-05 | ZH-05 adopt / accept-open a policy | H | A | A5 prohibited | human holder | same | TST-POL, S41 |
| AM-06 | ZH-06 activate / deactivate a rule set | H | A | A5 prohibited | human holder | same | TST-RUN, S41 |
| AM-07 | ZH-07 accept an exception rule (record only; semantics undefined in the spec) | H | A | A5 prohibited | human holder | same | STG23 S41/S42 |
| AM-08 | ZH-08 change disposition mode / values | H | A | A5 prohibited | human holder | same | TST-GATE-08, S42 |
| AM-09 | ZH-09 enable / disable the schedule | M | R | A5 prohibited | human holder | same | TST-RUN, S42 |
| AM-10 | ZH-10 edit a rule row / withdraw a policy (FAC-13, approved as built, OD-29) | H | A | A5 prohibited | human holder | same | STG20 R1 gaps, S41 |
| AM-11 | Non-exception case transition (status change by a reviewer) | M | A | A0: the hub records, validates and refuses; it never chooses | reviewer / quality_lead / compliance | `hub/decision/service.py` (OP-DEC-01) | TST-DEC |
| AM-12 | Rule evaluation, trace and flags (priority, manual review) | M | R | A1 recommend; rule sets ship inactive until ZH-06 | reviewer overrides / dismisses / refuses with reason | `hub/review/service.py`, `hub/policy/` | TST-REV, TST-GATE-18/19/20 |
| AM-13 | `capability_authority.<cap>`: shadow vs authoritative | H | R | shadow = A1; authoritative = rule result becomes decision of record (no consumer before Stage 30) | operator with a recorded `approval_ref` | `hub/control/flags.py` `check`, `hub/control/cli.py` | STG23 S10..S16 |
| AM-14 | Scheduled intake / reconcile run | M | A | A3-lite: fixed procedure, append-only, run id, idempotent; **ships OFF** | enabling = ZH-09 | `hub/runs/` | TST-RUN, TST-INT |
| AM-15 | Intake classification, duplicate / replay detection, quarantine | M | A | A1: reason codes; quarantine holds the item for a human | reviewer resolves conflicts (OP-INT-03, reason required) | `hub/intake/` | TST-INT, INC-06 |
| AM-16 | Metric and KPI arithmetic, cut-offs | M | R | A0: deterministic computation; definitions have no owner (Unknown) | n/a | `hub/metrics/` | TST-MET |
| AM-17 | Crosswalk link create / retract | M | A | A0: human-created, reason required; view is deterministic | reviewer / quality_lead / compliance | `hub/crosswalk/`, `hub/decision/` | TST-ID |
| AM-18 | Document search | L | R | A0; ships OFF (`search.enabled`) | reader | `hub/search/` | TST-REV, INC-09 |
| AM-19 | Template-rendered drafts | M | R | A2 (draft for human approval); ships OFF (`templates.enabled`, PCH-22) | author | `hub/review/templates.py` | INC-09 |
| AM-20 | Case creation | M | A | A0; ships OFF (`case_creation.enabled`) | operator with `approval_ref` | `hub/control/flags.py` | STG23 S10 |
| AM-21 | Audit append and chain verification | H | X | deterministic, no discretion; insert-only, hash-chained | n/a | `hub/security/audit.py` | TST-SEC |
| AM-22 | Change of a decision flag | H | R | A0 for the hub; human operator only; audited CONFIG_CHANGED | operator with `approval_ref`; a return to default needs none | `hub/control/cli.py` | STG23 S11..S13 |
| AM-23 | Stop the hub (`hub.kill`) / stop the schedule | M | R | human-on-the-loop intervention | operator | `hub/core/errors.py` E-HUB-KILLED | TST-CO |
| AM-24 | Serve beyond loopback | H | R | refused even with exposure approval and TLS keys (DW-15) | n/a | `hub/web/server.py` | STG23 S03..S05 |
| AM-25 | Any AI / model / network egress | H | X | prohibited (HAR-10) | n/a | `hub/guards/no_ai.py`, `hub/guards/egress.py` | TST-CO-11/12, E-groups |

### Findings
- [Verified Fact] Every ZH id (10 of 10) is in the code and equals the key set of `hub.gate.service.ZONE_H_ACTIONS`; the catalogue test STG23 S40 fails if an id, path or test named in `autonomy-catalogue.json` disappears.
- [Verified Fact] The shipped configuration keeps `zone_h.holders` empty, `disposition.mode` `none` and every `capability_authority` at `shadow` (STG23 S43, S16).
- [Verified Fact] ZH-02, ZH-03 and ZH-07 had no test through the choke point before Stage 23; STG23 S41 (refusals) and S42 (one event per success) now cover all of ZH-01..ZH-10 refusals and ZH-01, 02, 03, 07, 08, 09 successes.
- [Inference] ZH-04, ZH-05, ZH-06, ZH-10 success paths are covered by earlier-stage tests (see the catalogue); S42 does not repeat them, because their payloads need policy fixtures that those tests already build.
- [Inference] Materiality / reversibility are the author's classification from the code (append-only tables, audit chain); no client has confirmed them.
- [Assumption] The A0..A5 ladder of Stage 8 is the autonomy scale for the engagement. Confirm: Dinesh Naik.
- [Unknown] Who the real holder (SH-15, DR-22) is. The hub has no way to know.

## Evidence References
`docs/23-human-control/autonomy-catalogue.json`; `tests/hub/test_tst_hub_stg23_catalogue.py` (S40..S43); `docs/23-human-control/evidence/autonomy-catalogue-check.json`, `zone-h-refusal-matrix.json`, `zone-h-success-matrix.json`; Stage 8 `minimum-agency-assessment.md`; Stage 2 `decision-rights-map.md` DR-22.

## Assumptions
- A-23-01 The Stage 8 ladder is accepted as the scale (confirm: Dinesh Naik).
- A-23-02 Materiality and reversibility columns are the author's reading of the code.

## Unknowns
- U-23-01 Real holders of Zone H authority (SH-15 unnamed).
- U-23-02 Owner of metric definitions (DR-20/DR-21 gap).

## Unresolved Issues
- None blocking. Level for `capability_authority = authoritative` is provisional until Stage 30 gives it a consumer.

## Residual Risks
- A reader may take the matrix as approval of the levels. It is not: no level is approved by a human.
- The authoritative mode has no consumer yet; its classification will need review when one exists.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
