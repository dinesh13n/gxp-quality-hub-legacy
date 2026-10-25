---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "cost-per-workflow.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/preliminary-finops-baseline.md FB-01..FB-12", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-2", "docs/37-operating-model/finops-ownership.md FC-01..FC-10", "docs/33-vendor-risk/vendor-inventory.md", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32", "docs/00-preflight/discovery/workflow-overview.md WF-01..WF-11", "docs/37-operating-model/finops-ownership.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
Workflows are the Stage 0A catalogue WF-01..WF-11. For every workflow, model/token cost is USD 0 (the product is No-AI). Per-workflow compute and human cost are Unknown because no workflow runs in production and no handling time was measured. The only workflow-level labour figure is the whole-case 0.601 h (an Assumption on a synthetic formula) and it is **not** split across workflows here; splitting it would be invention.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CW-1 Table
| Workflow (0A) | Token cost | Compute cost | Human cost | Class | Notes |
|---|---|---|---|---|---|
| WF-01 Intake of upstream batch-quality events | USD 0 | Unknown | Unknown | [Verified Fact] 0; others [Unknown] | records, quarantine and exception handling are hub scope |
| WF-02 Partner feed staging and reconciliation | USD 0 | Unknown | Unknown | same | scheduler is OFF (OD-19), so no recurring compute exists |
| WF-03 Case triage / prioritisation | USD 0 | Unknown | part of 0.601 h per case [Assumption] | same | three divergent rule implementations (WF-06) |
| WF-04 Batch quality records read endpoints | USD 0 | Unknown | Unknown | same | read only |
| WF-05 Batch disposition | USD 0 | Unknown | Unknown | same | not implemented in legacy; human-gated in the hub (Zone H holders EMPTY) |
| WF-06 Approval / threshold rules | USD 0 | Unknown | Unknown | same | rule sets inactive until human decision (OD-16) |
| WF-07 Night-shift reconciliation | USD 0 | Unknown | Unknown | same | legacy estate |
| WF-08 Month-end reconciliation | USD 0 | Unknown | Unknown | same | legacy Java estate |
| WF-09 Monthly operating measures | USD 0 | Unknown | Unknown | same | metrics rely on generator-bounded proxies (OD-07) |
| WF-10 Incident handling | USD 0 | n/a (manual) | Unknown | same | manual runbook |
| WF-11 Process tensions (48 h closure vs evidence) | USD 0 | n/a | n/a | same | a policy conflict, not a costed workflow |

### CW-2 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CW-F1 | [Verified Fact] The only workflow with a scheduler concern (WF-02) has the scheduler switched off, so there is no recurring compute | OD-19, OD-20 | Run cost is zero until HAR-10 / OPD-11 is decided | Low | High | Scheduler decision |
| CW-F2 | [Inference] If the scheduler is ever switched on, WF-02 becomes the first workflow with a recurring compute cost; capture its `run_duration_seconds` from day one. Reasoning: run records and the metric exist (INC-07) | `hub/obs/collect.py` | Gives the first measurable per-workflow cost driver | Low | Medium | OPD-11 |
| CW-F3 | [Unknown] Which workflows the hub will actually own after cutover (cutover not approved) | OD-32 | Per-workflow TCO share cannot be set | Medium | High | Cutover decision (Dinesh) |

## Evidence References
`docs/00-preflight/discovery/workflow-overview.md`; `hub/obs/collect.py`.

## Assumptions
- A-32-11 Workflow numbering is the Stage 0A catalogue; the hub may redraw boundaries later. Confirm: Stage 34 re-baseline.

## Unknowns
- U-32-16 Per-workflow compute and human cost.

## Unresolved Issues
- Workflow-level handling time was never measured.

## Residual Risks
- RR-32-10 Splitting 0.601 h across workflows by guess. Low if avoided.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
