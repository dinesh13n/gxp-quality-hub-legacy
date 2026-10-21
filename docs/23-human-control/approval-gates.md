---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "approval-gates.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/gate/service.py", "hub/control/flags.py", "hub/security/exposure.py", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md", "docs/02-stakeholders/approval-authority-map.md", ".fde/orchestrator-decisions.md", "docs/23-human-control/autonomy-catalogue.json"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
Two kinds of gate exist. **Product gates** are enforced by the hub (Zone H holder check; `approval_ref` on decision flags; exposure approval plus the loopback rule). **Engagement gates** (HAR-01..HAR-16) are held by Dinesh Naik through the OD log. A gate here is a point where work stops until a named human has acted; each is tied to the code or the record that enforces it.

## Findings
### Product gates
| ID | Gate | Trigger | Approver the hub requires | Evidence the hub keeps | Enforced? |
|---|---|---|---|---|---|
| AG-01 | Zone H action (ZH-01..10) | any of the ten actions | interactive human, role dispositioner, in `zone_h.holders`, re-authenticated, with `authority_ref` | ZONE_H_ATTEMPT + the event with `holder_check_ref` | yes (code) |
| AG-02 | Decision flag away from default (`disposition.mode`, `closure.unconfigured_behaviour`, `workflow.transition_table`, `facts.derivation`, `case_creation.enabled`, `search.enabled`, `search.fts`, `templates.enabled`, `zone_h.holders`, `capability_authority.<cap>`) | config load / `set-flag` | operator supplies `approval_ref` (a reference to a recorded human approval) | CONFIG_CHANGED (old, new, approval_ref, source, direction) | yes (code); the reference itself is Unknown |
| AG-03 | Network exposure | `network.exposure_approved` | exposure approval AND a loopback bind; a non-loopback bind is refused regardless (DW-15) | CONFIG_LOADED; E-SEC-EXPOSURE-NOT-APPROVED exit 9 | yes (code) |
| AG-04 | Schedule enable / disable | ZH-09 | as AG-01 | SCHEDULE_CHANGED | yes |
| AG-05 | Rule-set activation | ZH-06 | as AG-01 | RULESET_ACTIVATED / DEACTIVATED + decision record | yes |
| AG-06 | Release | `hub/ops/release.py` | gate checks pass (no secrets in audit, scan clean) | release_record | yes (E-CO-RELEASE-BLOCKED) |

### Engagement gates (reconciled in `operating-contract-updates.md`)
HAR-01..HAR-16: five are enforced by code in the hub (HAR-05, 08, 09, 10, 12), five in part (HAR-01, 06, 11, 13, 16), six are process only (HAR-02, 03, 04, 07, 14, 15). See `autonomy-catalogue.json` for the per-item classification and evidence.

### Findings
- [Verified Fact] The approval rule for flags is generic: every registered decision flag is checked in `flags.check`; a flag set with no reference stops the hub from starting (S11).
- [Verified Fact] Approval wording in the audit record says "reference" - the hub never records an approval it did not receive and never fabricates one; tests use a marker that says it is not a human approval.
- [Inference] The switch does not itself require a Zone H holder (a host operator can run `set-flag`). A stricter reading of FF-2 would make the authority switch a Zone H action (ZH-11); that would need a holder, which does not exist yet. Decision for Dinesh.
- [Unknown] Where the approval register is kept (the OD log is the only one in the repo).

## Evidence References
`hub/control/flags.py`; STG23 S10..S16; TST-GATE; `.fde/orchestrator-decisions.md` OD-01, OD-25, OD-29; Stage 2 `approval-authority-map.md`.

## Assumptions
- A-23-07 A host operator holding the config file is trusted at AG-02 (single-operator capstone).

## Unknowns
- U-23-07 Whether AG-02 should be a Zone H action (ZH-11); U-23-08 where real approvals will be recorded.

## Unresolved Issues
- Decision: ZH-11 or keep the CLI + reference (for Dinesh).

## Residual Risks
- A reference string may be wrong or reused (RR-HC-1).
- Operator and approver can be the same person; no separation of duties is enforced.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
