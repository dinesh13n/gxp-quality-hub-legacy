---
stage: "35 — Before-vs-After Variance + Value Leakage"
artifact: "benefit-variance.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 35 run)"
status: "DRAFT"
evidence_sources: ["docs/03-problem-value/value-hypothesis.md", "docs/03-problem-value/success-criteria.md", "docs/00-preflight/ai-economics/economics-readiness.md", "docs/32-finops/tco-model.md", "docs/32-finops/cost-per-outcome.md", "docs/34-measure-after/after-intervention-kpi-sheet.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-32)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 35 adds files under `docs/35-variance/` and changes nothing else). No production after-data exists: the hub is not in production, there is no production telemetry, Stage 30 has not run and Stage 31 is not merged. Every 'after' figure is a Stage 34 SANDBOX measurement on the 125-case synthetic baseline (seed 4100) or an earlier stage's test result. Where a like-for-like pair exists it is labelled 'synthetic, sandbox, parity - not an improvement'. No improvement, saving, benefit or ROI is claimed, no number is invented, no stakeholder is invented, and no risk is accepted on Dinesh's behalf (OD-04, OD-32, HAR-11).**

## Summary
Benefit variance = intended benefit (Stage 3 value hypothesis and success criteria, Stage 0C economics) versus benefit realised. **Intended benefits were never quantified (value-hypothesis: 'No monetary figure is asserted'), and none is realised on any production basis, so the benefit variance is Unknown for every driver. No monetary variance is stated.**

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### BV-1 Intended benefit vs realised, per driver
| ID | Intended benefit (Stage 3) | Intended magnitude | Realised (Stage 34) | Variance | Tag |
|---|---|---|---|---|---|
| VD-01 | Less manual reconciliation time | Unknown (counts, minutes, rate all Unknown; 0C C-5) | No time capture; K-22 Unknown; hub not used by people | Unknown | [Unknown] |
| VD-02 | Less rework | Unknown (U-24) | K-15 parity 6.4 % = 6.4 % (imported status); K-22 Unknown | Unknown (parity is not rework change) | [Verified Fact] for parity; [Unknown] for effect |
| VD-03 | Fewer queue-inflation incidents | Frequency Unknown (two documented historic incidents) | K-07: replay of 8,567 rows left queues/totals unchanged in the sandbox (mechanism works on fixtures); no operating period | Unknown | [Verified Fact] (sandbox); [Unknown] (operational) |
| VD-04 | Faster, uncontested month-end | hours/month Unmeasured | K-10 not computed by design (OD-07); hub month-end total 622,826.44 (n=125) vs legacy SQL report 742,956.61 is a different quantity (BB-08) | Unknown | [Verified Fact]; [Unknown] |
| VD-05 | Audit defensibility | Qualitative, evidence-complete share (SUC-02) | K-02 0 % legacy (0 of 20); hub: mechanism supported, 0 human decisions so no rate | Unknown | [Inference] |

### BV-2 Success criteria (SUC) status [Verified Fact unless noted]
| SUC | Threshold (Stage 3, provisional Assumptions) | Status after Stage 34 |
|---|---|---|
| SUC-01 No unsafe action | = 0 | 0 in the Stage 26 attack suite (mutants M5/M9/M10 survive; F-08/F-09 test gaps); operational count Unknown. Invariant, not a benefit |
| SUC-02 Attribution 100 % of sample | 100 % | no hub decision sample exists |
| SUC-03 Definition transparency 100 % | 100 % | 4 of 4 definition-bearing hub values tagged (sandbox); policy status `candidate`, none adopted |
| SUC-04 / 05 Time to close / evidence | improve vs baseline | Unmeasurable (K-04, K-05 Unknown both sides) |
| SUC-06 Unmatched refs | target after baseline | no target set; hub classification not comparable |
| SUC-07 Replay safety | 0 change | 0 change in sandbox (hub); legacy never measured |
| SUC-08 Reconciliation delay | within NFR-03 (4 h) | legacy 75.24 % <= 4 h; hub not measured |
| SUC-09 Backlog/exception | improve vs baseline | count parity only; K-09U not comparable |
| SUC-10 Month-end comparability | difference = 0 | not computed |
| SUC-11 Decision recorded | exists | accepted-open record exists (K-11 2 of 2), no decider |
Result: [Inference] SUC thresholds are relative or unset, so even where a value exists there is no benchmark against which a benefit variance could be stated.

### BV-3 Cost-side expectation (Stage 0C / Stage 32) [Assumption]
- Retained 0C gross 3-year ranges: S1 USD 7,920 / 13,440 / 22,800 and S2 USD 13,440 / 22,080 / 39,000 (lo / mid / hi). Arithmetic re-derived in Stage 32 TC-2; **all inputs are Assumptions** (USD 300 per day, effort and hosting ranges). Four TCO terms (toolchain, oversight, validation, exit) are unpriced; actual build effort was not recorded (BA-F3, TCO-F4).
- Actual cost: Unknown for every term except model spend (USD 0 by design, tripwire). Therefore **cost variance is Unknown** and, since no benefit is quantified, **net benefit variance is Unknown**. 0C records that the business case is not decision-grade.

### BV-4 Findings
| ID | Finding | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|
| BNV-1 | [Verified Fact] No driver has a quantified intended benefit, so a 'shortfall' cannot be computed | A shortfall (or surplus) is not stateable | Medium (a number gets invented downstream) | High | 0C C-1..C-5 inputs |
| BNV-2 | [Verified Fact] No driver has a realised measurement on a production basis | Same | High | High | D-34-02 |
| BNV-3 | [Inference] The modelled 0.603 h/case (K-12) and USD 23.40/case (K-13) are generator outputs on an ops-table denominator (108), not cases; they must not seed a benefit | Prevents false precision | Medium | High | Stage 4 v0.2 addendum |
| BNV-4 | [Verified Fact] S3/S4 dormant AI cost numbers (USD 533 / 719 per month at Base) still sit in 0C files and could be misquoted as run cost | Misleading cost expectation | Medium | High | OB-09 proposal (edit not made) |

## Evidence References
`docs/03-problem-value/value-hypothesis.md` VD-01..VD-05; `success-criteria.md` SUC-01..11; `docs/32-finops/tco-model.md` TC-1, TC-2, TCO-F1..F4; `token-leakage-analysis.md` TL-02; `docs/34-measure-after/after-intervention-kpi-sheet.md`; `docs/00-preflight/ai-economics/economics-readiness.md` C-1..C-5.

## Assumptions
- A-35-01 [Assumption] Artifact directory is `docs/35-variance/` as instructed by the orchestrator, not `docs/35-value-leakage/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-35-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (variance only on Stage 34 C1 rows; leakage traced to repository findings; corrective actions are proposals). It does not accept any risk. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-35-05 Every benefit magnitude and every actual cost term except model spend.

## Unresolved Issues
- Finance partner review of 0C ranges has never happened (Stage 32). No one decides what a worthwhile effect size is (U-03-15).

## Residual Risks
- RR-35-05 A benefit number appears in Stage 36 from modelled hours. Medium. Mitigation: BNV-3.
- RR-35-06 0C range quoted as a budget (RR-32-16).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 35). |
