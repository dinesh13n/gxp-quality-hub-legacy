---
stage: "30 — Release / Cutover / Rollback"
artifact: "environment-promotion-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["environments/", "compose.yaml", "Dockerfile", "docs/14-transformation/coexistence-strategy.md", "docs/27-hardening/runtime-hardening.md", "hub/web/", "docs/30-release/evidence/s30-rehearsal-summary.txt"]
supersedes: "none"
---
**Label: synthetic, unvalidated. Stage 30 PREPARES and REHEARSES a release; it does not release, cut over, merge to production, tag, install CI, flip a shipped switch or approve anything. Every approval below is OPEN and belongs to Dinesh Naik (Engagement lead, the only human, OD-04). Defaults marked 'recommended' are agent proposals under OD-32 (scope choices only), not decisions. `zone_h.holders` ships EMPTY. The product is No-AI (OD-08).**

## Summary
The only environment that exists is the developer laptop. The promotion path proposed here has three rungs: **sandbox copy** (every test and rehearsal, `~/fde_sbx`, OD-03a), **shadow host** (one named host, hub in shadow, loopback, scheduler off), **authoritative** (per capability, CUT-n). Rung 2 and 3 do not exist yet and are Dinesh decisions (AP-OPS-01).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| EP-1 | [Verified Fact] `environments/` and `compose.yaml` / `Dockerfile` belong to the frozen legacy system (root user, all-interface bind as shipped, VR-04) | `docs/27-hardening/runtime-hardening.md` RH-4 | they must not be used to host the hub; changing them is a legacy-path edit | High if exposed | High | D-27-06 |
| EP-2 | [Verified Fact] There is no hub container recipe, supervisor or resource limit (PR-20 NOT BUILT) | production-readiness-checklist | host install is manual | Medium | High | - |
| EP-3 | [Verified Fact] The hub binds loopback only; non-loopback is refused by two independent checks; no TLS | VR-03, S23 S03..S05 | a host install is reachable only from the host itself | None while loopback | High | D-27-09 |
| EP-4 | [Verified Fact] Rehearsals ran on copies built by `git archive HEAD` plus the verified backup data, outside the working tree | `s30-rehearse.sh` | promotion by copy is repeatable | - | High | - |
| EP-5 | [Inference] Promotion gates: rung 1 -> 2 needs release-record `ready` (G1..G10 pass) plus AP-REL-01 and AP-OPS-01..11; rung 2 -> 3 needs AP-CUT-n, its AP-DV rows, a rehearsed L3 and a named consumer | `hub/release/register.py` | machine-checkable via `python -m hub.release evaluate` | - | Medium | - |
| EP-6 | [Verified Fact] Python 3.10 reached end of life on 2026-10-01; production target is 3.12+ (OD-24), no 3.12 evidence exists | VR-02, D-27-02 | any host install on 3.10 runs an unpatched interpreter | High before exposure | High | AP-OPS-07 |

## Evidence References
`deployment-strategy.md`, `release-approvals.md` (AP-OPS-01, 07, 08, 09).

## Assumptions
- A-30-03 [Assumption] The first host is Dinesh's own machine or a host he names; no shared infrastructure.

## Unknowns
- U-30-03 whether any organisation-managed environment (dev/test/prod) exists beyond this laptop.

## Unresolved Issues
- Rung 2 and 3 hosts unnamed (AP-OPS-01).

## Residual Risks
- RR-30-2 Using legacy container files as a hub host would inherit VR-04.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 30). |
