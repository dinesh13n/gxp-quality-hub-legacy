---
stage: "23 — HITL/HOTL & Deterministic Control Boundaries"
artifact: "escalation-matrix.md"
version: "v0.1"
date: "2026-10-21"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/02-stakeholders/escalation-map.md ES-01..ES-09, ES-20..ES-25", "docs/00-preflight/operating-contract/stop-conditions.md", "hub/core/errors.py", "docs/23-human-control/stage12-v0.2/error-code-registry.json", "tests/hub/test_tst_hub_stg23_registry.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. The product is No-AI (OD-08). zone_h.holders ships EMPTY; every holder named in a test is SYNTHETIC TEST DATA, not an approver. approval_ref values are references the hub cannot verify (Unknown). Nothing here is a human approval; the sole provisional approver is Dinesh Naik (OD-01).**

## Summary
The engagement route is unchanged from Stage 2 (stage agent, orchestrator, Dinesh Naik; no level beyond him; ES-09 no alternate) and stays PROVISIONAL. Stage 23 adds the **hub-level** triggers: the error codes and exit codes that mean a human must look. There is still no client-side owner, on-call or incident process (ES-20..ES-25 gaps), so each hub trigger names the engagement route and marks the domain owner Unknown.

## Findings
### Hub triggers (verified from the generated registry, `error-code-registry.json`)
| ID | Trigger (code, exit / HTTP) | Meaning | First responder | Escalate to | Action |
|---|---|---|---|---|---|
| EH-01 | E-GATE-NO-HOLDERS (19 / 423) | a Zone H action was requested but no holder is configured | operator | Dinesh Naik (OD-S12-06 open) | decide who holds; never add a holder without approval |
| EH-02 | E-GATE-NOT-AUTHORISED (19 / 403) | non-holder or non-human tried Zone H | operator reads audit | Dinesh Naik if repeated | review ZONE_H_ATTEMPT records |
| EH-03 | E-SEC-AUDIT-TAMPER-DETECTED (17 / 409), E-DEC-CHAIN-BROKEN (25 / 409) | audit or decision chain does not verify | operator stops the hub | Dinesh Naik; STOP-01 style halt | restore from backup only with approval (HAR-01) |
| EH-04 | E-CO-DENYLIST-IMPORT (9), E-CO-EGRESS-ATTEMPT (11), E-OBS-TRIPWIRE (14) | an AI package, an egress attempt or a model call was detected | operator | Dinesh Naik (HAR-10 / HAR-08 / HAR-09) | block release; remove the cause |
| EH-05 | E-SEC-EXPOSURE-NOT-APPROVED (9) | non-loopback bind attempted | operator | Dinesh Naik (HAR-05) | none; the bind stays refused |
| EH-06 | E-RUN-TOTALS-MISMATCH (29 / 500) | a run's totals do not reconcile | reviewer / operator | Dinesh Naik (no domain owner) | keep the run record; investigate (ES-21 gap) |
| EH-07 | E-CFG-INVALID (2) at start-up with a flag / approval message | decision flag without `approval_ref` | operator | Dinesh Naik for the approval | supply a recorded reference or revert |
| EH-08 | E-CO-RELEASE-BLOCKED (20), E-SEC-SECRET-IN-AUDIT (18) | release gate failed or a secret-like value reached the audit | operator | Dinesh Naik (HAR-14 if waiver wanted) | fix; never waive on the agent's own authority |
| EH-09 | E-HUB-KILLED (3) | `hub.kill` is set | operator | n/a | by design |
| EH-10 | an `authoritative` capability shows divergence from human decisions | rule output disagrees with the person | reviewer | Dinesh Naik | `flip-to-shadow` (L3) |

Exit codes 2 and 9 are each shared by more than one meaning (documented, kept, OD-29); the exit code alone does not identify the cause, so the first responder reads the JSON `code`.

### Engagement and domain routes
Unchanged and PROVISIONAL: ES-01..ES-09 (engagement) and ES-20..ES-25 (domain gaps) in `docs/02-stakeholders/escalation-map.md`. Stage 23 adds no new level and no alternate approver.

### Findings
- [Verified Fact] All codes named above exist in the registry with the exit and HTTP values shown (STG23 S20 diff 0).
- [Inference] Without a client owner the matrix ends at Dinesh Naik for every trigger; a real deployment needs named owners (Stage 25, Stage 37).
- [Unknown] Response-time expectations (none documented, U-02-13).

## Evidence References
Registry JSON / Markdown; Stage 2 `escalation-map.md`; STG23 S20..S24.

## Assumptions
- A-23-10 The Stage 2 ladder stays the only route (confirm: Dinesh Naik).

## Unknowns
- U-23-11 Domain incident owner and on-call (ES-24 gap). U-23-12 Response-time targets.

## Unresolved Issues
- No alternate approver (ES-09).

## Residual Risks
- A single point of failure can stall escalation or tempt a shortcut approval (RR-HC-5, Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-21 | claude-fde-agent | Initial issue (Stage 23 BUILD). |
