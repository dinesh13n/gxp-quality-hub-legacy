---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "cost-per-case.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/preliminary-finops-baseline.md FB-01..FB-12", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-2", "docs/37-operating-model/finops-ownership.md FC-01..FC-10", "docs/33-vendor-risk/vendor-inventory.md", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32", "data/legacy.sqlite3 (125 cases, OD-09)", "docs/00-preflight/ai-economics/cost-scenarios.md", "docs/04-baseline-kpis (frozen-provisional, OD-07)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
A "case" is a batch-quality case in the shipped database (125 cases, baseline confirmed by OD-09). **Measured:** model cost per case is USD 0. **Assumed:** today's human handling cost is USD 15.02 per case (0.601 h x USD 25/h, synthetic formula, FB-05/FB-06). **Unknown:** the hub's own marginal run cost per case and the human cost per case after the hub exists. **No saving is claimed**, because no benefit baseline is measured (OD-07, FAIL-05).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CC-1 Components
| Component | Per case | Class | Source |
|---|---|---|---|
| Model/token | USD 0 | [Verified Fact] | FB-01/02 |
| Human handling today (baseline) | USD 15.02 | [Assumption], rate USD 25/h unverified, hours from a synthetic formula | FB-05, FB-06; `app/baseline` |
| Hub compute and storage | Unknown | [Unknown] | FC-02, FC-08 |
| Human handling with the hub | Unknown | [Unknown] | FC-07; reviewer time not measured |
| Toolchain cost allocated per case | Not meaningful: build tooling is a fixed engineering cost (see `tco-model.md`), not a per-case cost | [Inference] | FC-03..FC-05 |

### CC-2 Illustrative baseline exposure (arithmetic on Assumptions, not a forecast)
| Tier (0C, Assumed) | Cases per month | Baseline human cost per month at USD 15.02 |
|---|---|---|
| Low | 4 | USD 60.08 |
| Base | 167 | USD 2,508.34 |
| High | 1,670 | USD 25,083.40 |
These are the cost of the existing manual process under synthetic assumptions. They are **not** hub savings. [Assumption] synthetic, unvalidated; confirm tiers and rate: Dinesh / Finance partner (SH-05, unfilled).

### CC-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CC-F1 | [Verified Fact] Shipped data supports 125 cases; the 0C monthly tiers are derived from 125 and 6,000 over 36 months, and the period is Unknown | `volume-assumptions.md` W-01..W-03 | Monthly volume is a guess | Medium | High | Real case volume |
| CC-F2 | [Verified Fact] Stage 5 refuted the idea that `operating_costs.total_cases` counts cases created in a month; the Stage 4 operating-cost table is not a cost source | OD-07 | Do not use that table for cost per case | Medium | High | none |
| CC-F3 | [Unknown] Closure and evidence timestamps do not exist, so time-to-close per case (and so reviewer cost) is unmeasurable | OD-07 (K-04, K-05) | Human cost per case cannot be measured from the repo | Medium | High | Real timestamps |

## Evidence References
`docs/00-preflight/ai-economics/cost-scenarios.md`; `volume-assumptions.md`; OD-07, OD-09.

## Assumptions
- A-32-10 USD 25/h and 0.601 h per case are the only available labour inputs. Confirm: Dinesh / SH-05.

## Unknowns
- U-32-13 Hub marginal cost per case. U-32-14 Real reviewer time per flagged case. U-32-15 Real case volume and period.

## Unresolved Issues
- Q-02-05 (closed / resolved / 48 h definitions) remains accepted open (OD-09).

## Residual Risks
- RR-32-09 CC-2 being quoted as savings. Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
