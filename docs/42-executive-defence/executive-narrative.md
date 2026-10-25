---
stage: "42 — Executive Defence & Final Value Story"
artifact: "executive-narrative.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/42-executive-defence/executive-evidence-index.md", "docs/30-release/release-outcome.md", "docs/36-roi/roi-model.md", "docs/35-variance/before-after-analysis.md", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
## Summary

**Label: synthetic repository, unvalidated against any organisation. Every number is synthetic, unvalidated unless stated.**

The one-paragraph truth (C-19, C-21, C-25): *We rebuilt the case-handling and partner-feed logic of a synthetic GxP quality estate into a No-AI, stdlib-only "hub" that sits beside the untouched legacy code, and we tested it hard in a sandbox. It reproduces legacy behaviour where it should, adds controls the legacy code lacks, and every consequential switch is off. It is not released: the release gate is BLOCKED with 0 of 40 approvals. It has no users and no after-window, so we cannot say it saves anything; ROI, NPV and payback are not computable. What we can defend is the problem diagnosis, the decision to use no AI, the engineering discipline and the honesty of the evidence. What we cannot defend is value.*

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### EN-1 The storyline in seven beats (each with claim IDs from `executive-evidence-index.md`)

1. **The problem is structural, not (provably) a volume problem.** [Verified Fact] Eight root causes are confirmed in code and schema: no recorded decision step, mutable case state, no owned definition of "closed", three unsynchronised approval rules, manual and unrecorded execution, destructive intake, no shared identity model, and month-end totals computed without a shared definition (the SQL join inflates a total by 19.3 % on the shipped data: 742,956.61 vs 622,826.44). (C-02) [Unknown] Whether any of this costs a real organisation time or money. (C-01)
2. **We measured a baseline, and it is weak.** [Verified Fact] 22 KPIs: 16 synthetic values, 6 Unknown; the freeze is unsigned; one assumption (A-04-01) was refuted. (C-03, C-04)
3. **We decided No-AI.** [Verified Fact] The gaps are absences of design and of an owner, not interpretation of unstructured input; AI options scored lowest and were rejected on fit and risk; Dinesh approved (OD-08). (C-05, C-06)
4. **We built a modular, additive, deterministic hub with human control.** [Verified Fact] Stdlib only, append-only stores, hash-chained audit, Zone H human gate, everything consequential off; 241 acceptance tests green in the sandbox; legacy characterisation 134/134. (C-07..C-12)
5. **We attacked it, and it was not clean.** [Verified Fact] TEVV found 11 findings (one High: a restricted note readable by a reviewer role); Stage 27 fixed F-01..F-07 and killed the three surviving mutants (13 of 13 killed in its own gate, a result recorded by Stage 27 and not re-run here); walkthroughs remain unsigned; no Python 3.12+ evidence. (C-14, C-15, C-34)
6. **We prepared a release and could not execute it.** [Verified Fact] Rollback levels L1-L3 were rehearsed on sandbox copies; the evaluator says NO-GO; 0 of 40 approvals; monitoring (T-09) and High-finding dispositions (T-10) fail. (C-19, C-20)
7. **We looked for value and found none that can be stated.** [Verified Fact] No after-window, three parity pairs, 17 leakage items, zero verified benefits, ROI/NPV/payback not computable. (C-21..C-26)

### EN-2 What the executive is asked to take away
| Message | Status |
|---|---|
| The diagnosis is credible at code level | Defensible (repo-level only) |
| No-AI was the right call for this problem | Defensible on fit and risk; outcome superiority not measured |
| The engineering is disciplined and honest about its limits | Defensible (record of defects caught and registered, C-31) |
| The product is ready for production | **Not defensible** (C-15, C-19) |
| The product creates value | **Not defensible yet; unknown** (C-25) |
| The path to proving value is defined | Defensible as a plan (C-29), gated, not a commitment |

### EN-3 Decisions the audience is actually being asked for
Only Dinesh Naik can decide these (single approver; see `next-step-recommendations.md` for the full list): the release decision and the 40 approvals; whether to name Zone H holders and other roles; DV-01..DV-11 preserve-or-fix; whether to run a real pilot and define an after-window; which cost and labour inputs to supply so Stage 36 can be re-run; and whether to accept or reject the open risk registers.

### EN-4 Anticipated hard questions and defensible answers
(Answers use "unknown / not yet measured" where that is the truth.)

| # | Question | Defensible answer | Basis |
|---|---|---|---|
| Q1 | What is the ROI? | Not computable. There are zero verified benefits, one of ten cost terms is measured (model spend USD 0 by design), and no discount rate exists. We will not offer a number. | C-25 |
| Q2 | How much time or money does it save? | Unknown, not yet measured. There is no after-window, no time capture, no labour rate and no volume. The only hours-per-case figure (0.603) is a generator estimate. | C-21, C-26, C-03 |
| Q3 | Who is using it? | Nobody. Adoption is 0 of 125 cases and there are 0 principals. It runs only in a sandbox. | C-21 |
| Q4 | Why is it not live? | The release gate is BLOCKED by design: 0 of 40 required human approvals, golden comparison fails until 11 behaviour differences are decided, monitoring has no persisted metrics or alerts, and High findings lack recorded decisions. | C-19 |
| Q5 | The dashboards say parity. Is that good? | Parity means the hub reproduces the legacy count from an imported copy of the same data. It is not improvement. We claim no improvement. | C-22 |
| Q6 | Are the baseline numbers real? | No. They are measured on a synthetic, test-residue database. 97.98 % of partner-feed rows reference cases that do not exist in it. They validate the method only. | C-03 |
| Q7 | Why no AI? Is that a failure of ambition? | The root causes are missing owners, keys and records; AI cannot supply an owner, and an LLM consumer adds an injection risk (86 feed rows and 22 of 1,200 documents carry instruction-like strings). AI can be re-qualified through RQ-1..RQ-3 if real documents and a measured keyword-search shortfall appear. | C-05 |
| Q8 | Is it GxP / Part 11 compliant? | We make no compliance claim. Part 11 is framing only; no regulation clause or auditor requirement beyond what earlier stages cite was added. | C-28 |
| Q9 | Is it secure? | Secure enough for synthetic data on loopback in shadow mode, no more. No TLS, single-factor passwords, 16 residual risks open, no external penetration test. It must not take real data or network exposure yet. | C-13 |
| Q10 | What did testing find? | 11 findings, one High; seven fixed in Stage 27, three test gaps closed (the three surviving mutants were killed: 13 of 13), one open plus nine complex functions. Mutation sampling covers only 13 chosen mutants. Reviewer walkthroughs are unsigned. | C-14, C-15 |
| Q11 | Who owns it after you leave? | No one yet. 0 of 28 assets have an accepted owner; 17 of 24 accountable roles are vacant; Dinesh is interim owner of record, not an accepting owner. | C-27 |
| Q12 | What if Dinesh is unavailable? | Single point of failure and single approver. This is a recorded risk (RP-01, DQ-17); no second reviewer is appointed. | C-27, C-28 |
| Q13 | What does it cost? | Unknown. Only assumption ranges exist (gross 3-year, USD 7,920-22,800 for the deterministic scenario, 13,440-39,000 for the larger one), built on an unvalidated USD 300/day rate and excluding toolchain, oversight, validation, exit, parallel-running and adoption costs. | C-25 |
| Q14 | Could the build have gone wrong silently? | It went wrong several times and was caught: four late-found defects in the orchestrator's full regression, one a real No-AI violation in a test helper. The control worked; the rework hours were not recorded. | C-31 |
| Q15 | Does it still behave like the legacy system? | Yes where tested: characterisation 134/134 at Stage 16, 15/15 mutants killed, 0 unexplained differences; 11 differences are deliberate and unapproved. CT-13 fails only on a Node patch-version drift. | C-09 |
| Q16 | What is the earliest you can show value? | Not within 90 days with certainty. The roadmap reaches at most a limited-entry decision, needs 17 unmet pre-conditions closed first, and may still end at "ROI not computable" if the pilot window is too short. | C-29 |
| Q17 | Are the SLOs a commitment? | No. Five SLO candidates, no SLA, thresholds are agent assumptions. | C-18 |
| Q18 | Which vendors do we depend on? | At build time: the AI coding assistant, code host and cloud workspace. At run time: Python and SQLite only. Vendor acceptances VA-01..VA-07 are proposed, not accepted. | C-33, C-10 |
| Q19 | What were the data origins? | Synthetic: the shipped 125-case database (sha256 c254649f...d70aa, seed 4100, confirmed by Dinesh in OD-09). No real data has touched the hub. | C-03, OD-09 |
| Q20 | Are Stage 38 (handover) and Stage 41 (retirement) done? | No. Those documents do not exist at main b1de232. | C-32 |

### EN-5 Presentation rule (mandatory)
Any number from this engagement spoken or shown must carry one of: "synthetic, unvalidated", "sandbox", "agent assumption" or "Unknown". A number with no label is not to be presented.

### EN-6 Stage 42 gate computation (agent's computation; a recommendation, not an approval)
| Gate condition | Met? | Evidence |
|---|---|---|
| Every material claim maps to lifecycle evidence | Met | `executive-evidence-index.md` C-01..C-34, EI-2 lists claims deliberately not made |
| Failures and trade-offs are included | Met | `lessons-learned.md`, `tevv-summary.md` TS-2/TS-3, `architecture-defence.md` AD-4, `residual-risks.md` |
| All 14 required artifacts exist | Met | `docs/42-executive-defence/` (path deviation S42-DEV-01) |
| Critical gaps resolved or explicitly documented | Met (documented) | `residual-risks.md`, `next-step-recommendations.md` NS-1 |
| Evidence supports the stage conclusion | Met, because the conclusion is limited to "diagnosis and discipline defensible; value unproven; release blocked" | C-19, C-21, C-25 |

**Outcome: CONDITIONAL PASS for the defence documents.** The conditions are the human decisions in `next-step-recommendations.md` NS-1. **The underlying project status is BLOCKED and is inherited, not cleared:** Stage 30 release gate BLOCKED (0 of 40 approvals), Stage 36 benefits sign-off UNSIGNED, ROI/NPV/payback NOT COMPUTABLE, Stages 38 and 41 not produced. If the gate is read as requiring a released, value-proven outcome, Stage 42 is BLOCKED. Stage FINAL (as-built PRD) may document the shadow build as built, labelled "not released", only on Dinesh's instruction; it must not state value or release.

## Evidence References
`docs/42-executive-defence/executive-evidence-index.md` C-01..C-34; `.fde/orchestrator-decisions.md`.

## Assumptions
- A-42-03 [Assumption] The audience is internal to the engagement or a capstone panel; no real executive, sponsor or customer exists (OD-04). Confirm: Dinesh.

## Unknowns
- U-42-03 Who the actual audience will be and what decision they hold. 
- U-42-04 Whether any value exists in a real organisation (C-01).

## Unresolved Issues
- Release decision and approvals (C-19); benefits sign-off (C-25); ownership (C-27).

## Residual Risks
- Over-reading: a polished narrative can sound more finished than the evidence. The EN-2 table and EN-5 rule are the mitigation.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | Initial narrative. |
