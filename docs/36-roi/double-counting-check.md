---
stage: "36 - ROI / NPV / Benefits Realisation"
artifact: "double-counting-check.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 36 run)"
status: "DRAFT"
evidence_sources: ["docs/36-roi/verified-benefits.md", "docs/36-roi/roi-model.md", "docs/35-variance/value-leakage-analysis.md", "docs/03-problem-value/value-hypothesis.md", "docs/04-baseline-kpis/kpi-dictionary.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 36 adds files under `docs/36-roi/` and changes nothing else). Result in one line: ROI, NPV and payback are NOT COMPUTABLE from the evidence in this repository. There is no production after-data (the hub is not in production), the three like-for-like KPI pairs are sandbox parity and not improvement (Stage 35), Stage 3 never quantified an intended benefit, the Stage 0C economics are unvalidated Assumptions with four unpriced cost terms, and Stage 32 found model spend USD 0 and every other cost Unknown. No benefit, saving, ROI, NPV, discount rate, rate card or stakeholder is invented here; no risk is accepted on behalf of Dinesh Naik (OD-04, OD-32, HAR-11). Any placeholder in this file is an empty input slot, not a number.**

## Summary
Double-counting check performed **on the structure**, because no benefit value exists to double count. It lists the overlaps that the five Stage 3 drivers and the cost terms would create, the rule that prevents each, and states the current monetised total (0) so the check result is 'no double counting present; prevention rules defined'.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DC-1 Current state [Verified Fact]
Monetised benefit in the model: 0. Therefore realised double counting: 0. The check below is a pre-registration of rules for the day values exist.

### DC-2 Benefit-side overlaps and rules
| ID | Overlap | Why it overlaps | Rule |
|---|---|---|---|
| DCK-1 | VD-01 reconciliation time vs VD-04 month-end hours | month-end reconciliation hours are part of reconciliation time | Count a reviewer-hour once. Month-end hours (VD-04) are valued only for hours *not* already in N_recon x m_recon; otherwise drop VD-04 |
| DCK-2 | VD-01 vs VD-02 rework | a reopened case's extra reconciliation appears in both | Rework effort e_rework excludes reconciliation minutes already counted in VD-01 for the same case |
| DCK-3 | VD-03 incident effort vs VD-02 and VD-04 | an incident causes rework and month-end disputes | Incident effort e_inc is valued only for hours not recorded as rework or month-end hours for that incident |
| DCK-4 | VD-05 audit defensibility vs any money driver | risk avoided can be priced as a penalty avoided or as review time saved | VD-05 stays non-monetary (BAF-3); if later priced it must be priced as risk avoided *instead of* time |
| DCK-5 | Adoption A_t applied twice | A_t scales every V_d; applying it again to a K-21-based volume doubles the haircut (understates) or omits it (overstates) | Volumes N are *total* population counts; A_t is applied exactly once per V_d |
| DCK-6 | Same difference seen in two KPIs | e.g. K-15 rework rate and K-22 rework effort; K-09 backlog and K-04 age describe one phenomenon | Monetise one KPI per phenomenon; the other is corroboration only |
| DCK-7 | Capacity freed counted as cash | hours saved are not cost saved unless headcount, overtime or vendor spend changes | Report hours as capacity; convert to money only with a decision on where the capacity goes (Finance partner) |
| DCK-8 | Parity counted | K-09-OPS and K-15 equality (imported status) | Excluded: parity is zero variance (`verified-benefits.md` VB-1) |
| DCK-9 | Stage 4 modelled hours reused | K-12/K-13 (0.603 h, USD 23.40/case) | Excluded (BA-2) |

### DC-3 Cost-side overlaps
| ID | Overlap | Rule |
|---|---|---|
| DCK-10 | Build effort vs Ops | Post-go-live fixes are Ops, pre-go-live defect fixes are Build; one hour in one term (rework found late, VL-15, CLK-4, is Build) |
| DCK-11 | Oversight cost vs benefit netting | Reviewer time on hub decisions is a cost (`Over_t`); it must not also be netted inside m_recon saved. m_recon is the net change per case including the new hub review step |
| DCK-12 | Parallel-run double work | Valued once as `Dbl_t` cost, not also removed from the benefit of the same reviewers |
| DCK-13 | Avoided cost vs not-spent cost | Model spend USD 0 is by design (No-AI); it is **not** a saving relative to an AI option that was never chosen (S3/S4 retired). Counting USD 533/719 per month avoided would be a fabricated benefit (CLK-2) |
| DCK-14 | Coverage 'savings' | Cutting regression to save time is barred (CG-7, RR-32-12) |

### DC-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| DCF-1 | [Verified Fact] No double counting exists because nothing is monetised | `verified-benefits.md` VBF-1 | Check passes trivially | Low | High | none |
| DCF-2 | [Inference] Highest future risk: DCK-1/2/3, three time drivers sharing the same reviewer hours. Reasoning: all measured in minutes of one reviewer pool; K-22 effort capture not yet designed | Stage 3 formulas | Capture design should record effort by activity, not just total | Medium | Medium | CA-06 |
| DCF-3 | [Verified Fact] DCK-13 is a live trap: AI-option cost numbers remain in 0C files | `cost-leakage.md` CLK-2 | Misread as avoided cost | Medium | High | OB-09 |


## Evidence References
`docs/36-roi/verified-benefits.md`; `docs/03-problem-value/value-hypothesis.md` VD-01..VD-05; `docs/35-variance/cost-leakage.md` CLK-2, CLK-4; `docs/32-finops/cost-guardrails.md` CG-7.

## Assumptions
- A-36-12 [Assumption] Reviewer hours form one shared pool across VD-01..VD-04 (not evidenced; no reviewer-effort data). Confirm: Engagement lead (Dinesh Naik).
- A-36-01 [Assumption] Artifact directory is `docs/36-roi/` as instructed by the orchestrator, not `docs/36-benefits/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-36-02 [Assumption] Default-answer authority (OD-32) covers the scope choices here (skeleton instead of numbers; scenarios built only on cost-side Stage 0C ranges). It does not accept any risk, name any owner or approve anything. Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-36-11 Whether the drivers truly share hours; resolved by effort capture by activity.

## Unresolved Issues
- Check must be re-run when any slot is filled.

## Residual Risks
- RR-36-15 Overlaps appear only once values exist and are missed because this file says 'passed' (Medium). Mitigation: re-run required before any sign-off.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 36). |
