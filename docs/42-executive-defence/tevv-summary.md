---
stage: "42 — Executive Defence & Final Value Story"
artifact: "tevv-summary.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/26-tevv/tevv-release-gate.md", "docs/26-tevv/tevv-results.md", "docs/26-tevv/red-team-findings.md", "docs/26-tevv/residual-tevv-risks.md", "docs/27-hardening/hardening-plan.md", "docs/16-repo-validation/regression-results.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation.** Testing, evaluation, verification and validation was substantial and disciplined, and it is **sandbox-only**. TEVV gate: **CONDITIONAL PASS** (not PASS). Thresholds were declared before the results (commit a42ffe6), nothing was edited to pass, and the red team found no Critical issue but did find real defects, most fixed in Stage 27. Open: the three human walkthroughs are unsigned, no Python 3.12+ run exists, and no external penetration test exists (C-09, C-11, C-14, C-15, C-34).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### TS-1 What was run and what it showed
| Layer | Result | Where | Class |
|---|---|---|---|
| Legacy characterisation (Python 3.10.12, laptop) | 134/134 checks in 6 runs at Stage 16; CT-13 later fails only on Node patch drift (v22.23.2 golden vs v22.23.4) | Stage 16, Stage 26 TR-3, Stage 30 | [Verified Fact] |
| Legacy mutation gate | 15/15 killed; shipped suite kills 1/15 | Stage 15/16 | [Verified Fact] |
| Hub acceptance tests | 241 planned, all green in sandbox (Stage 16: 396 ok, 1 skipped, 0 fail over 397 methods) | Stage 16/17 | [Verified Fact] |
| Stage 26 groups | S26 23/23, E26 1/1, B 42/42 (1 registered skip), I6 43/43; named set TST-NFR/TST-SEC all ok | `tevv-results.md` TR-1 | [Verified Fact] |
| Behaviour comparison | 0 differing fields across 13 sections, 350 rows (RT-08); D5 = 0 | Stage 16, 26 | [Verified Fact] |
| Authorisation matrix | 0 wrongly allowed; 2 refusal-code mismatches (F-01, fixed) | RT-09 | [Verified Fact] |
| Zone H attacks | 80/80 refused | RT-10 | [Verified Fact] |
| Adversarial corpus | 114 strings (sha256 1806bd77...56f7b), 469 responses, 0 secret/path/traceback hits | RT-11 | [Verified Fact] |
| Faults | 0 corruption; every tamper detected; chain ok after concurrency | RT-12 | [Verified Fact] |
| Mutation (Stage 26) | 12 sampled: 9 killed, M5/M9/M10 survived; Stage 27 killed all three (13/13) | TR-4; `hardening-plan.md` | [Verified Fact] |
| Full regression (orchestrator, cloud, Python 3.13) | 31 groups green at Stage 30 merge (OD-37) | OD-37 | [Verified Fact] (as reported by the orchestrator) |

### TS-2 Findings the testing produced (not hidden)
- 11 findings F-01..F-11; one High (F-02 restricted note readable by a reviewer role); F-03: 5 HTTP 500 from one string; F-01 refusal order; F-04 config errors give a traceback; F-07 generic store-fault code. F-01..F-07 fixed in Stage 27 (behaviour changes recorded as agent assumptions A-27-02, A-27-04, A-27-05). F-11 and nine over-complex functions remain open.
- The orchestrator's full regression, not the build agents, caught: S21-DEV-02 (a real No-AI R2 defect in a test helper), S24-DEV-05 (two I6 failures), S28-DEV-08 (four red groups; a capped listener imported `hub.web` from `hub/resilience`), S31-DEV-08 (twelve red groups; a test variable named `secret` tripped the secret scan). [Verified Fact] (OD-28, OD-32, OD-35, OD-36)
- "Test once" policy (OD-23) trades speed for late discovery; the late discoveries above are its cost. [Inference]

### TS-3 What TEVV did NOT establish
| Gap | Why it matters |
|---|---|
| **Human walkthroughs TST-REV-03/04/08 unsigned** (agent rehearsal only) | Reviewer-facing surfaces never touched by a human; RT-13 blocks PASS |
| **No Python 3.12+ evidence** | Production target (OD-24) is untested; goldens are 3.10.12-specific; 10 of 16 CT checks differ on 3.13 by environment only (OD-23) |
| **No external penetration test**, static analysis only | RS-14 |
| **No performance, load or capacity testing against a target** | No target exists; 180 s per-call cap on the laptop limits runs |
| **No user acceptance testing** | No users |
| **No test with real data** | Only synthetic data; OD-04 |
| **Planned tests that are proxies**: 35 class-B tests pass only on non-adopting defaults; 9 class-C tests give sandbox proxies | "241 green" means green under those qualifiers |
| **Disk-full, power-loss, container-restart injection** need an approved host | FM-11 not injected; D-28-07/08 |
| **Characterisation of enterprise-side tests** CT-17/CT-18 not run by design | U-07-05, HAR-05 |
| **Full regression at the final HEAD by the agent** was not run in Stage 26/30 | Delegated to the orchestrator (OD-23) |

### TS-4 Integrity of the testing itself [Verified Fact]
Thresholds RT-01..RT-15 and the dataset specs were committed before any S26 test; one disclosed baseline run preceded the declaration (S26-DEV-06); M9/M10 selectors were narrowed before first run (S26-DEV-07). The data checksum gate returned rc 0 before and after every run. This is good practice but it is **self-review by the same engagement lead's agents**, with one human (RP-01).

## Evidence References
`docs/26-tevv/` all files; `docs/27-hardening/hardening-plan.md`, `scan-results.md`; `docs/16-repo-validation/regression-results.md`, `test-results.md`; OD-23, OD-24, OD-33..OD-37.

## Assumptions
A-26-05 (High routes to Stage 27, Critical blocks) and A-26-13 (severities) are agent defaults awaiting Dinesh.

## Unknowns
Behaviour on 3.12+; real-reviewer usability; performance under any realistic load; effort spent on rework.

## Unresolved Issues
RT-07 (re-assess after Stage 27 fixes: the Stage 27 claim is F-03 fixed, not independently re-verified by TEVV), RT-13, RT-14, RTR-01..RTR-15 acceptance or rejection, TEVV delta after wiring (SB-14).

## Residual Risks
False comfort from a large green count; mutation sample of 13; agent-authored tests share the author's blind spots.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial. |
