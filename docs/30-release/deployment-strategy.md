---
stage: "30 — Release / Cutover / Rollback"
artifact: "deployment-strategy.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["hub/admin/cli.py", "hub/control/cli.py", "docs/14-transformation/coexistence-strategy.md", "docs/28-reliability/resilience-architecture.md", "docs/30-release/evidence/s30-rehearsal-summary.txt"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Stage 30 PREPARES and REHEARSES a release; it does not release, cut over, merge to production, tag, install CI, flip a shipped switch or approve anything. Every approval below is OPEN and belongs to Dinesh Naik (Engagement lead, the only human, OD-04). Defaults marked 'recommended' are agent proposals under OD-32 (scope choices only), not decisions. `zone_h.holders` ships EMPTY. The product is No-AI (OD-08).**

## Summary
**Method: copy-install in shadow, then per-capability authority flags. No big-bang, no canary traffic split** (there is no traffic to split: one operator, no consumers). Phasing is by capability (CUT-1..5), each independently revertible. Deployment is a manual procedure using the existing CLIs (`hub.admin migrate`, `backup`, `verify-audit`; `hub.control set-flag` / `flip-to-shadow`), all of which were exercised on a sandbox copy.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| DS-1 | [Verified Fact] Install sequence rehearsed: fresh `migrate` (M000, M001...), `status`, `startup-check`, `verify-audit`, `golden-compare` (exit 6), `backup`, manifest check | `s30-log-01..08` | the install is 8 commands, all rc as expected | Low | High | - |
| DS-2 | [Verified Fact] Migrations take a pre-migration backup automatically (`--backup-root`) | log 01, `hub/store/migrate.py` | schema rollback is a restore | Low | High | - |
| DS-3 | [Verified Fact] A canary is not meaningful: the hub is not in any request path; "phased" means shadow comparison per capability (daily golden-compare) | cutover-plan CO-2 step 5 | verification window = parallel run | - | High | - |
| DS-4 | [Verified Fact] Resilience mechanisms (GuardedGateway, BoundedLoopbackServer) and observability modules are built but NOT wired into the CLIs/server | S28-DEV, S31-DEV-01, D-28-01/02, D-31-01/02 | a release would run without breaker, cap, persisted metrics | Medium | High | AP-OPS-10 |
| DS-5 | [Proposal, not applied] Hardened legacy container recipe if Dinesh wants legacy files changed (D-27-06): non-root user, bind 127.0.0.1, read-only root filesystem, pinned base image, no `.env` copied. Not applied: legacy paths are frozen and TST-CO-05 a would fail | `docs/27-hardening/runtime-hardening.md` RH-4 | decision only | - | Medium | AP-OPS-09 |
| DS-6 | [Verified Fact] A running server does not re-read `hub.kill`; the switch is checked at command start only (grep of `hub/`: no other reader) | `s30-log-33-kill-switch-reads.txt` | containment of a running server = stop the process (answers F-29-11 as an Inference; a live-server test was not run) | Medium | Medium | - |

## Evidence References
`rollback-plan.md`, `cutover-checklist.md`; `hub/control/flags.py` (approval-reference rule).

## Assumptions
- A-30-04 [Assumption] A manual, operator-run install is acceptable for a one-operator R1.

## Unknowns
- U-30-04 live-server behaviour on `hub.kill` (F-29-11): not run.

## Unresolved Issues
- No install script exists beyond the rehearsal script; no supervisor.

## Residual Risks
- RR-30-3 Unwired resilience (DS-4) means a stuck partner source can hang a pull.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 30). |
