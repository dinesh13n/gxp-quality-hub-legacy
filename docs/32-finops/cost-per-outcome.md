---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "cost-per-outcome.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/preliminary-finops-baseline.md FB-01..FB-12", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-2", "docs/37-operating-model/finops-ownership.md FC-01..FC-10", "docs/33-vendor-risk/vendor-inventory.md", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32", "docs/04-baseline-kpis (frozen-provisional)", "docs/37-operating-model/finops-ownership.md FO-2 item 5", "docs/00-preflight/discovery/workflow-overview.md WF-11"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
**No cost per outcome can be computed.** An outcome needs a definition owned by the process owner (RL-03, VACANT), and the definitions of "closed", "resolved" and the 48-hour clock are accepted-open (OD-09, OD-22). No KPI baseline is measured (OD-07, K-04 and K-05 unmeasurable). This artifact fixes the structure and lists candidate outcome units so that cost can be joined later; every value is Unknown.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CO-1 Candidate outcome units (proposals for RL-03 to choose or reject)
| Candidate | Why it could work | Why it cannot be costed yet |
|---|---|---|
| Case dispositioned with a recorded human decision and `approval_ref` | Exists as an audit/decision event in the hub | Zone H holders are empty; no real decisions |
| Feed run completed with totals matching | Run records and totals-mismatch route ER-06 exist | scheduler OFF; no real runs |
| Exception resolved from the reviewer queue | Queue depth metric exists | resolution definition open (OPD-01..03) |
| Rule-flagged item reviewed | Review time is the human cost driver | reviewer time not measured (U-24) |

### CO-2 Formula
`cost_per_outcome = (token + compute + storage + review + allocated_fixed) / outcomes_in_period`. Token term is 0. All other terms Unknown. `allocated_fixed` follows the TCO split in `tco-model.md`.

### CO-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| COUT-F1 | [Verified Fact] No outcome definition and no benefit baseline exist | OD-07; FAIL-05; FO-2 item 5 | FinOps cannot report cost per outcome | Medium | High | RL-03 |
| COUT-F2 | [Verified Fact] Value claims stay "synthetic, unvalidated" | `finops-ownership.md` FO-2 | No ROI input for Stage 36 | Medium | High | Stage 36 |
| COUT-F3 | [Inference] Because the model term is zero, cost per outcome will be a fixed-cost and labour question, not a token question. Reasoning: CRQ-F3 | tripwire evidence | Optimisation effort should go to review time and hosting | Low | Medium | Measurement |

## Evidence References
OD-07, OD-09, OD-22; `docs/37-operating-model/finops-ownership.md`.

## Assumptions
- A-32-12 The four candidates are examples only; none is adopted. Confirm: RL-03 (VACANT; Dinesh interim).

## Unknowns
- U-32-17 Outcome definition and volume. U-32-18 Value per outcome (no benefit is modelled).

## Unresolved Issues
- Stage 36 (ROI) has no cost-per-outcome input from this stage.

## Residual Risks
- RR-32-11 A cost-per-outcome number appearing before the outcome is defined. Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
