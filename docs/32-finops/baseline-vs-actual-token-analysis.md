---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "baseline-vs-actual-token-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/preliminary-finops-baseline.md FB-01..FB-12", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-1..ER-4", "docs/37-operating-model/finops-ownership.md FO-1..FO-3", "docs/33-vendor-risk/vendor-inventory.md V-01..V-11", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32, OD-33, OD-34", "data/legacy.sqlite3 (125 cases, OD-09)", "docs/00-preflight/ai-economics/{cost-scenarios,volume-assumptions,preliminary-tco}.md", "docs/27-hardening/production-readiness-checklist.md PR-36, PRC-R", "tests/hub/test_tst_hub_stg27_egress_guard.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
Compares the preserved Stage 0C baseline (`preliminary-finops-baseline.md` FB-01..FB-12, not edited) with what can be observed now. **There is no production, so "actual" means engineering-environment evidence only.** The only baseline item that can be compared is the zero: model calls and token spend were 0 at baseline and are 0 now, and that holds by construction. Every AI-option baseline (FB-07..FB-11) is retired by Stage 8 (ER-1) and has no actual because the option was not built. Infrastructure and human cost remain Unknown.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### BA-1 Item-by-item
| FB item | 0C baseline | 0C class | Actual now | Evidence for actual | Comparison |
|---|---|---|---|---|---|
| FB-01 model calls / month | 0 | Measured (0A grep) | 0 model calls in the hub; counter 0 in every egress-guarded test group | `hub/guards/no_ai.py`; `no-ai-check.json` findings `[]`; E27 asserts `model_calls_total` 0 | Equal. [Verified Fact] in code and tests; production [Unknown] (nothing deployed) |
| FB-02 token spend | USD 0 | Measured | USD 0; no model client, so no tokens | same | Equal. [Verified Fact] |
| FB-03 cases (shipped DB) | 125 | Measured | 125, confirmed baseline by OD-09 | OD-09 | Unchanged |
| FB-04 cases (documented dataset) | 6,000 | Measured (regenerable) | Not part of the baseline (OD-09) | OD-09 | Dropped as baseline |
| FB-05 hours per case | 0.601-0.603 | Measured from synthetic formula | Unchanged; no real handling time | U-24 | Not comparable |
| FB-06 human cost per case | USD 15.02 | Assumed (USD 25/h) | Unchanged assumption (0.601 h x 25 = 15.025) | `cost-scenarios.md`, ER-1 A-P03 | Not comparable; still Assumption |
| FB-07 token cost per case S3 / S4 | USD 0.0077 / 0.0167 | Assumed | Retired: S3/S4 not built (OD-08) | ER-1 | No actual exists |
| FB-08 monthly run S3 / S4 | USD 533 / 719 | Assumed | Retired | ER-1; FF-03 | Must not be read as a forecast for No-AI |
| FB-09 monthly calls S3 / S4 | ~672 / ~772 | Assumed | 0 (no AI option) | same | Not applicable |
| FB-10 retry rate | 5% | Assumed | n/a (no model calls to retry) | same | Not applicable |
| FB-11 avg agent steps | 6 (cap 8) | Assumed | n/a | same | Not applicable |
| FB-12 infra cost | Unknown | Unknown | Unknown | `docs/37-operating-model/finops-ownership.md` FC-02 | Still Unknown |

### BA-2 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| BA-F1 | [Verified Fact] The zero-model-call baseline is held in code and in 8 egress-guarded groups plus C1..C3; production is unobserved | E27 test; PR-36 MET | The only "actual vs baseline" result available is the zero | Low | High (for tests) | Production egress control (hosting Unknown) |
| BA-F2 | [Verified Fact] No actual cost of any kind has been measured outside model spend | FB-12; FC-02..FC-10 Unknown | Gate condition "unit economics from measured data" cannot be met for money | Medium | High | Hosting, invoices, review time |
| BA-F3 | [Inference] Stage 0C's S1 build range (15 to 40 person-days) cannot be compared with actual effort because no effort was recorded | no time-tracking in repo; 56 commits at 5efe271 is activity, not cost | The baseline that Stage 8 said to re-estimate (ER-2) stays Unknown | Medium | Medium | Dinesh: was effort tracked anywhere? |
| BA-F4 | [Verified Fact] Baseline files were preserved, not edited | `git log` for `docs/00-preflight/ai-economics/` shows no Stage 32 change | Before/after remains possible | Low | High | none |

## Evidence References
`docs/00-preflight/ai-economics/preliminary-finops-baseline.md`; `docs/08-ai-qualification/economics-baseline-reconciliation.md` ER-1, ER-2; `docs/27-hardening/production-readiness-checklist.md` PR-36.

## Assumptions
- A-32-03 Equality of the zero in tests stands in for production until a host exists. Confirm: Dinesh at the first hosting decision.
- A-32-04 FB-06 (USD 25/h) and the 0C volume tiers (4 / 167 / 1,670 cases a month) stay Assumptions. Confirm: Dinesh / Finance partner (SH-05, unfilled).

## Unknowns
- U-32-04 Any production actual (no deployment). U-32-05 Real handling time and reviewer time (U-24). U-32-06 Actual build effort in person-days.

## Unresolved Issues
- Stage 4 KPI sheet is frozen-provisional and some baselines are generator-bounded proxies (OD-07); they are not used as cost drivers here.

## Residual Risks
- RR-32-03 Reading "0 equals 0" as proof of economic value. It proves only that the cost line is empty. Medium.
- RR-32-04 Baseline drift if 0C assumptions are quoted without their class. Low.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
