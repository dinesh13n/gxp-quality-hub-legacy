---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "benefit-assumptions.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/value-hypothesis.md", "docs/03-problem-value/success-criteria.md", "docs/00-preflight/ai-economics/economics-readiness.md", "docs/35-variance/benefit-variance.md", ".fde/orchestrator-decisions.md (OD-04, OD-07, OD-32)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on Dinesh Naik on his behalf (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
Register of every benefit assumption the repository contains, each with its source and its status. **All five Stage 3 value drivers are unquantified Assumptions; none has a magnitude, a unit volume or a rate.** This register preserves them (prompt: 'preserve benefit assumptions with sources') and does not promote any of them to a benefit.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### BA-1 Benefit assumption register
| ID | Driver (Stage 3) | Intended effect | Magnitude | Volume | Rate | Source | Status | Tag |
|---|---|---|---|---|---|---|---|---|
| BAS-01 | VD-01 Reduced manual reconciliation time | reviewers spend less time reconciling | Unknown | Unknown | Unknown (0C C-5) | `value-hypothesis.md` | Unquantified hypothesis | [Assumption] |
| BAS-02 | VD-02 Reduced rework | fewer reworked cases | Unknown (U-24) | Unknown | Unknown | same | Unquantified hypothesis | [Assumption] |
| BAS-03 | VD-03 Fewer queue-inflation incidents | fewer incidents | Unknown | Frequency Unknown (two documented historic incidents) | Unknown | same; `historic-decisions.md` | Unquantified hypothesis | [Assumption] |
| BAS-04 | VD-04 Faster, uncontested month-end | fewer hours per month | Unmeasured | 1 close per month (structure only) | Unknown | same | Unquantified hypothesis | [Assumption] |
| BAS-05 | VD-05 Audit defensibility | risk avoided, reported qualitatively as evidence-complete share (SUC-02) | not monetised by design | n/a | n/a | same; `success-criteria.md` SUC-02 | Qualitative only | [Assumption] |

### BA-2 Numbers that look like benefits and must NOT be used [Verified Fact]
| Figure | Where | Why excluded |
|---|---|---|
| 0.603 h/case (K-12), USD 23.40/case (K-13), 65.14 h on the 125-case DB | Stage 4 baseline; `value-hypothesis.md` DF-06 | Generator outputs ('modelled estimate'); denominator is the ops-table total (108), not cases (125) (A-04-01 refuted, OD-07). A baseline cost of a synthetic dataset is not a saving (BNV-3) |
| 6.4 % rework (8 of 125) before and after | K-15 | Imported status, parity; not a change in rework |
| 89 of 125 backlog before and after | K-09-OPS | Hub backfills the legacy status, equality is by construction |
| USD 533 / 719 per month (S3 / S4) | 0C files | Retired AI options (OD-08); cost numbers, not benefits (CLK-2) |
| 622,826.44 vs 742,956.61 month-end totals | K-10 | Different quantities (BB-08) |

### BA-3 Success-criteria threshold status [Verified Fact]
SUC thresholds are relative to a baseline ('improve vs baseline') or unset (A-03-13); no tolerance or 'worthwhile effect size' exists (U-03-15). Therefore no threshold can convert a measured difference into a benefit even if one were observed.

### BA-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| BAF-1 | [Verified Fact] Five benefit assumptions exist; zero carry a magnitude, volume and rate | `value-hypothesis.md` | No benefit stream can be valued | High (a number gets invented downstream) | High | 0C C-1..C-5 |
| BAF-2 | [Verified Fact] Of the five, four are time/effort drivers whose key measurement (effort, timestamps) does not exist (K-04, K-05, K-22 Unknown) | Stage 34; OD-07 | Even after adoption they cannot be shown without a capture design | High | High | CA-06 |
| BAF-3 | [Inference] VD-05 is non-monetary by design; forcing a money value would be an invention. Reasoning: Stage 3 states 'not monetised' | `value-hypothesis.md` | Keep as qualitative evidence share | Low | High | none |


## Evidence References
`docs/03-problem-value/value-hypothesis.md` VD-01..VD-05; `success-criteria.md` SUC-01..11; `docs/35-variance/benefit-variance.md` BV-1, BNV-1..BNV-4; `docs/00-preflight/ai-economics/economics-readiness.md` C-1..C-5.

## Assumptions
- A-36-03 [Assumption] The Stage 3 hypothesis V0 is worth testing (inherited A-03-14). Confirm: Engagement lead (Dinesh Naik).
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-01 Magnitude, volume and rate for BAS-01..BAS-04. Resolution: 0C C-1, C-2, C-5 supplied by a real owner.
- U-36-02 What effect size is worthwhile (U-03-15).

## Unresolved Issues
- No stakeholder exists who can confirm any benefit assumption (OD-04).

## Residual Risks
- RR-36-01 A modelled figure from BA-2 is quoted as a benefit (High).
- RR-36-02 Qualitative VD-05 is monetised to fill a gap (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
