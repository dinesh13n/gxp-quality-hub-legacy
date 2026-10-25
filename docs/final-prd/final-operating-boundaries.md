---
stage: "FINAL — Authoritative Final As-Built PRD (run as Stage 43)"
artifact: "final-operating-boundaries.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/23-human-control/", "docs/37-operating-model/", "docs/29-incident-bcdr/", "docs/30-release/rollback-plan.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only. Authoritative ONLY as "as-built, NOT released": the hub is a shadow build; nothing here records a release, an approval, realised value or a sign-off.**

## Summary
The hard limits within which the shadow hub may be operated, and the human gates that stop work. Boundaries are enforced partly by code and partly by procedure; no operator exists.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### OB-1 What the as-built system is allowed to do [Verified Fact]
Read legacy snapshots (read-only); write only to its own hub store; serve HTTP/CLI on 127.0.0.1; compute figures with declared definitions; quarantine and queue exceptions; record decisions/audit; run manual authorised reconcile runs. Synthetic data only.

### OB-2 What it must never do (standing boundaries)
| Boundary | Source | Enforcement |
|---|---|---|
| No AI / LLM / ML, no inference egress | OD-08, FR-CO-04 | deny-list, egress guard, tripwires (manual gate) |
| No automatic batch disposition, QA release or e-signature | FR-GATE-01 | single Zone H choke point; no holder |
| Legacy is never written; legacy stays authoritative until a recorded human approval | ADR-003, OD-26, OD-31 | read-only adapters; authority switch OFF |
| No deletion/retention purge (hold-all) | OD-15, OD-30 | insert-only triggers; no delete paths |
| No real data; no exposure beyond loopback; no TLS-less exposure | STOP-04; RS-01 | bind refusal ×2 |
| No fabricated approvals, KPIs or data | OD-04 | register rules; evaluator refuses agent approvers |
| No risk acceptance, holder naming, cutover approval or irreversible step by an agent | OD-32 | process (stop and ask Dinesh) |
| No change to the parallel workflow for older customers | FR-CO-02 | coexistence inventory protected |
| No run of code or tests in the working tree; code only in full copies outside it | OD-03a | procedure |
| `data/` checksums must verify after any run | OD-03a | `sha256sum -c` |

### OB-3 Engagement gates held by Dinesh [Verified Fact]
HAR-01..HAR-17 (e.g. HAR-05 container restart / non-loopback exposure, HAR-07 CI install, HAR-09 off-device backup, HAR-10 automated action/scheduler, HAR-11 risk/PRD approval, HAR-12 holders, HAR-13 contract approval). Work stops until a named human acts. Dinesh Naik is the only human on the engagement (OD-04).

### OB-4 Environment boundaries [Verified Fact]
Reference laptop (Python 3.10.12 / SQLite 3.37.2, Node patch pinned in goldens) for characterisation and data checks; orchestrator cloud workspace (Python 3.13) for the full hub regression, with git-ignored data copied once and checksum-gated (OD-23); device VM disk ~9.8 GB (delete sandbox copies after each run, OD-16); per-call cap 180 s.

### OB-5 Rollback levels (rehearsed in sandbox only) [Verified Fact]
L1 code revert of a squash commit; L2 hub-state backup/restore (corrupt backup refused, exit 21); L3 authority flip back to shadow (flip refused without reference, exit 2). Rollback triggers: `verify-audit` exit 17; UNEXPLAINED golden difference; non-127.0.0.1 bind; model call or egress tripwire non-zero; outcome-sum mismatch; `hub.kill` needed. Rollback authority: Dinesh alone (F-29-07; AP-OPS-02 OPEN).

### OB-6 Support and escalation [Verified Fact / Inference]
No support model is staffed: RL-02..RL-11, RL-13 VACANT; no on-call; manual evaluation of alerts (RB-00); incident severity matrix exists on paper; escalation ends at Dinesh. [Inference] There is no operating boundary an on-call person could rely on today.

## Evidence References
See `evidence_sources` in the header and the per-row evidence columns.

## Assumptions
- A-43-15 [Assumption] HAR numbering as in the Stage 23 approval-gates document.

## Unknowns
- U-43-17 Who, other than Dinesh, may invoke the kill switch or roll back.

## Unresolved Issues
- See `open-items-and-decision-register.md`.

## Residual Risks
- See `residual-risk-register.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
