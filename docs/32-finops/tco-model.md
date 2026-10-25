---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "tco-model.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/{preliminary-finops-baseline,preliminary-tco,cost-scenarios,volume-assumptions}.md", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-1..ER-4", "docs/37-operating-model/{finops-ownership,escalation-model,raci,decision-rights}.md", "docs/33-vendor-risk/{vendor-inventory,vendor-risk-acceptance,exit-plan}.md", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32, OD-33, OD-34", "docs/00-preflight/ai-economics/preliminary-tco.md (arithmetic reproduced)", "docs/33-vendor-risk/exit-plan.md", "docs/27-hardening/production-readiness-checklist.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
A TCO model **structure** with explicit unknowns. The only monetary figures are the Stage 0C gross ranges for the two scenarios Stage 8 kept (S1 deterministic, S2 non-ML part), quoted with their class (Assumption, synthetic, unvalidated) and **with their arithmetic re-derived from their own stated components**, which checks internal consistency only. No figure here is a forecast, a quote or a budget. Benefits are not modelled (no evidence, OD-04), so this TCO cannot show the product to be worthwhile. S3/S4 are retired (ER-1) and not carried.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TC-1 Model
`TCO_3y = Build + Ops_3y + Hosting_3y + Toolchain_3y + Human_oversight_3y + Validation_and_compliance + Exit`
| Term | Definition | 0C figure (Assumption) | Measured? | Input Dinesh must supply |
|---|---|---|---|---|
| Build | person-days x day rate | S1 15 / 25 / 40 pd; S2 25 / 40 / 70 pd; USD 300 per day | **No.** Actual effort not recorded (BA-F3). ER-2 says true effort may lie at or above S2 | Actual or estimated person-days; confirmed day rate |
| Ops_3y | person-days per year x 3 x rate | S1 3 / 5 / 8; S2 5 / 8 / 12 pd per year | No | Support model and staffing (FC-09) |
| Hosting_3y | USD per month x 36 | S1 20 / 40 / 100; S2 40 / 80 / 200 USD per month | No (FC-02; nothing deployed) | Hosting decision and price |
| Toolchain_3y | code host + AI assistant + cloud workspace + CI | **not in 0C** | No (FC-03..FC-06) | Plans and charges (U-33-01, U-33-02) |
| Human_oversight_3y | reviewer minutes x volume x rate | S1/S2 = 0 in 0C, which ER-4 calls an omission favouring S1/S2 | No | Reviewer time (U-24), volume, rate |
| Validation_and_compliance | CSV/CSA, security review, training, incident handling | **not priced in 0C ("hidden TCO items", Unknown)** | No | Compliance owner estimate (RL-06 VACANT) |
| Token | USD 0 | 0 | Yes by design | none |
| Exit | cost of leaving toolchain vendors | not in 0C | No | per `exit-plan.md` once priced |

### TC-2 Reproduction of the retained 0C ranges (Assumptions; arithmetic only)
| Scenario | Build | Ops 3y | Hosting 3y | Gross 3y (lo / mid / hi, USD) | Recomputed from components? |
|---|---|---|---|---|---|
| S1 | 7,500 (mid: 25 x 300) | 4,500 (mid: 5 x 3 x 300) | 1,440 (mid: 40 x 36) | 7,920 / 13,440 / 22,800 | Mid 7,500+4,500+1,440 = 13,440. Lo 4,500+2,700+720 = 7,920. Hi 12,000+7,200+3,600 = 22,800. Matches. [Verified Fact] |
| S2 | 12,000 | 7,200 | 2,880 | 13,440 / 22,080 / 39,000 | Mid 12,000+7,200+2,880 = 22,080. Matches. |
Reading rule [Inference]: the planning range for the chosen No-AI product is S1 lo to S2 hi (USD 7.9k to 39.0k gross, 3 years), **unvalidated**, and it excludes the toolchain, oversight, validation and exit terms above, so the true range is above it by an unknown amount.

### TC-3 What the repository measures that bears on TCO
| Fact | Value | Source | Bearing |
|---|---|---|---|
| Third-party libraries in the hub | 0 | `vendor-inventory.md` | No licence or subscription cost for dependencies |
| Product vendors with fees | 0 identified; toolchain accounts Unknown | V-01..V-11 | Toolchain is the only likely fee source |
| Regression time per full pass (laptop) | 2,403 s | PRC-R | Engineering time per release |
| Model spend | 0 | tripwire | Token term zero |
| Hosting | no vendor chosen | ADR-015 | Hosting term Unknown |

### TC-4 Sensitivity (structure; no new numbers)
Volume affects only oversight and storage (fixed hosting and build do not scale). Largest swing terms by construction: build effort (+/-50% or worse, 0C), oversight rate and minutes, hosting choice. Token price has no effect (zero).

### TC-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| TCO-F1 | [Verified Fact] The retained 0C ranges are internally consistent but wholly assumed | TC-2 | They can frame a conversation, not a budget | Medium | High | Finance partner review (none available) |
| TCO-F2 | [Verified Fact] Four TCO terms (toolchain, oversight, validation, exit) have no price anywhere | TC-1 | Gross range understated | Medium | High | Inputs in TC-1 |
| TCO-F3 | [Inference] If hosting stays loopback-only on a laptop, hosting and token terms are near zero and TCO becomes labour plus toolchain. Reasoning: ADR-015, no external service | `vendor-inventory.md` | Changes which inputs matter | Low | Low | Cutover/hosting decision |
| TCO-F4 | [Unknown] Whether the build effort to date fits S1, S2 or neither | BA-F3 | The key TCO term | Medium | n/a | OB-04 |

## Evidence References
`docs/00-preflight/ai-economics/preliminary-tco.md` (components as stated there); `economics-baseline-reconciliation.md` ER-2, ER-4.

## Assumptions
- A-32-18 USD 300 per person-day and the 0C effort and hosting ranges stay Assumptions, synthetic, unvalidated. Confirm: Dinesh and a Finance partner (SH-05, unfilled).
- A-32-19 A 3-year horizon and 0% growth carry over from 0C (A-TC01).

## Unknowns
- U-32-24 Every input in the right-hand column of TC-1. U-32-25 Currency and budget.

## Unresolved Issues
- Finance review of the 0C ranges has never happened.

## Residual Risks
- RR-32-16 The 0C range quoted as a budget (Medium). RR-32-17 Understated range because four terms are unpriced (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
