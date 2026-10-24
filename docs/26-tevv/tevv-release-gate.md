---
stage: "26 — TEVV + AI Red Teaming"
artifact: "tevv-release-gate.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["docs/26-tevv/release-thresholds.md (declared in a42ffe6)", "docs/26-tevv/tevv-results.md", "docs/26-tevv/red-team-findings.md", "docs/26-tevv/residual-tevv-risks.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW. This is the agent's computation of the gate rule that was declared before the results (`release-thresholds.md` TH-3). It is a recommendation to the Engagement lead. It is not an approval, and it accepts no risk.**

## Summary
**Gate outcome: CONDITIONAL PASS.** No BLOCKED condition applies: no unregistered failure in the groups run, the named set is green, characterization fails only on the registered CT-13 drift, the data checksum was rc 0 before and after every run, the tripwires read zero, and no Critical finding exists. PASS is not reachable: the human walkthroughs are unsigned (RT-13) and Python 3.12+ evidence is missing (RT-14). RT-07, RT-13 and RT-14 are not met; RT-01 (full run at the final HEAD), RT-11 and RT-12 have gaps; each is documented with a route in `residual-tevv-risks.md`, and Stage 27 consumes the findings. Dinesh Naik decides whether to accept the conditions.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### GT-1 Threshold computation [Verified Fact unless marked]
| ID | Threshold (as declared) | Observed | Met? |
|---|---|---|---|
| RT-01 | every group 0 FAIL/ERROR, executed = expected | S26 23/23, E26 1/1, B 42/42 (1 registered skip), I6 43/43 green; all other groups green in the pre-declaration baseline (476 methods) and untouched since (no `hub/` edit); full 23+2 group run at final HEAD is the orchestrator's (S26-DEV-03) | Met for the groups run; full run pending |
| RT-02 | named set all ok | TST-NFR-07/08/09/12/13 and TST-SEC-01..21 all ok (74 + 41 + 5 methods; SEC-18 in decided mode OD-S12-09) | Met |
| RT-03 | CT-01..CT-16 0 FAIL except CT-13 | only CT-13 fails (S24-DEV-04) | Met |
| RT-04 | checksum rc 0 before and after; legacy unchanged | rc 0/0 in every run; TST-CO-05 green | Met |
| RT-05 | 0 egress, 0 model calls, no-ai-check rc 0, 0 non-stdlib imports | 0 / 0 / rc 0 (E26 tripwires zero, D01); one documented loopback-only `urllib.request` adapter (ADR-002 R2), 13 hostile URLs refused | Met |
| RT-06 | every mutant KILLED or survivor registered | 9 of 12 killed by some group; M5, M9, M10 survive and are registered as F-10, F-08, F-09 (M9 and M10 are Medium by the RT-06 rule) | Met by registration |
| RT-07 | 0 HTTP 500 etc. | 0 active markup, 0 header injection, 0 unintended state; 5 HTTP 500 from one string (S26-F-03) | NOT met (registered, High-blocking row, routed; not a stage blocker per TH-3) |
| RT-08 | 0 differing fields | 0 of 13 sections, 350 rows | Met |
| RT-09 | 100 % cells equal registry | 0 wrongly allowed; 2 refusal-code mismatches (S26-F-01); refused cells change 0 non-audit rows | Met for safety; code mismatch registered |
| RT-10 | 100 % refused; boundary | 80 / 80 refused; footprint unchanged; boundary as declared | Met |
| RT-11 | 0 hits | 0 secret / path / traceback hits in 469 responses; restricted note leak S26-F-02 is a separate rule (access, not secrets) | Met as worded; F-02 registered High |
| RT-12 | each fault a defined code or clean refusal; 0 corruption; every tamper detected; chain verifies | 0 corruption; every tamper detected; chain ok after concurrency; config-file errors give a traceback (F-04), store faults a generic code (F-07) | Met in substance; two Low gaps |
| RT-13 | signed walkthroughs | blank records, agent rehearsal only | NOT met (blocks PASS only) |
| RT-14 | green on 3.10 and 3.12+ | 3.10 green; 3.12+ not run | NOT met (blocks PASS only) |
| RT-15 | gate rule | computed below | - |

### GT-2 Gate rule applied [Verified Fact]
- BLOCKED conditions checked one by one: RT-01 unregistered failure: none; RT-02 failure: none; RT-03 failure other than CT-13: none; RT-04: none; RT-05 non-zero: none; Critical finding unremediated and unregistered: none (no Critical found); thresholds, datasets or tests edited to produce a pass: none (the declaration commit precedes the S26 tests; M9 / M10 selectors were narrowed before their first run and the baseline run is disclosed, S26-DEV-06, S26-DEV-07).
- CONDITIONAL PASS conditions: every remaining gap is documented with owner and route in `residual-tevv-risks.md`; the High finding (S26-F-02) is routed to Stage 27 under A-26-05.
- PASS conditions: RT-13 and RT-14 not met, so PASS is not reachable.

### GT-3 Conditions attached to the CONDITIONAL PASS [Inference: proposal]
1. Dinesh performs and signs the three walkthroughs (`walkthrough-records.md`), or explicitly leaves them open.
2. The orchestrator runs the full regression (23 + 2 groups) and the 3.12+/3.13 run at the merge HEAD and reports the result (RT-01, RT-14).
3. Stage 27 takes S26-F-02 first, then F-01, F-03, F-05, F-08, F-09; Dinesh decides the restricted-evidence read rule.
4. Dinesh decides whether to accept or reject the residual items RTR-01..RTR-15. Nothing is accepted here.

### GT-4 Deviations and caveats [Verified Fact]
S26-DEV-01 groups S26 and E26 added and the non-add allow-list reset (two files). S26-DEV-02 CT-13 Node drift carried (S24-DEV-04). S26-DEV-03 full regression at final HEAD not run by the agent. S26-DEV-04 3.12+/3.13 not available on the laptop. S26-DEV-05 exact-window boundary through the pure rule because the fixed clock ticks 1 us per call. S26-DEV-06 baseline run before the threshold declaration (disclosed). S26-DEV-07 M9 / M10 selector narrowing and "+earlier" second-look runs. S26-DEV-08 planning test IDs differ from executed IDs (map in `tevv-results.md` TR-2). S26-DEV-09 group walls S26 145 s and E26 174 s against the 120 s headroom target; groups B and I6 were started in the same tool turn. S26-DEV-10 walkthroughs rehearsed by the agent only, unsigned. S26-DEV-11 the mutation clone needed a copy of the gitignored `data/` (copy only).

## Evidence References
`release-thresholds.md`, `tevv-results.md`, `red-team-findings.md`, `remediation-evidence.md`, `residual-tevv-risks.md`, `walkthrough-records.md`, `evidence/`.

## Assumptions
- A-26-05 (High routes to Stage 27, Critical blocks) and A-26-13 (severity ratings) apply. Both are the agent's defaults under OD-32 and need Dinesh's confirmation.

## Unknowns
- U-26-12 Whether the full regression at the merge HEAD, including the Stage 33 changes now on origin main (ad449a5), stays green: this branch is based on 7c60c09 and was not rebased.

## Unresolved Issues
- Open conditions GT-3 (1..4).

## Residual Risks
- RTR-01..RTR-15 in `residual-tevv-risks.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue; gate computed from thresholds declared in a42ffe6. |
