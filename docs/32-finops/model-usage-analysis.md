---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "model-usage-analysis.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/preliminary-finops-baseline.md FB-01..FB-12", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-1..ER-4", "docs/37-operating-model/finops-ownership.md FO-1..FO-3", "docs/33-vendor-risk/vendor-inventory.md V-01..V-11", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32, OD-33, OD-34", "hub/guards/no_ai.py", "docs/27-hardening/evidence/no-ai-check.json", "docs/27-hardening/evidence/sbom.cdx.json", "docs/10-architecture/model-service-scorecard.md", "docs/33-vendor-risk/vendor-inventory.md V-04", "docs/00-preflight/ai-economics/provisional-model-call-inventory.md MC-01..MC-06"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
**Product model usage: none.** The hub has no model client, no AI/ML package, and no network client outside the `adapters/` directory. **Build-tool model usage exists and is not measured**: an AI coding assistant helped build the repository (V-04; OD-08 calls it dev tooling, not product AI), and the repository holds no usage, token or invoice record for it.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### MU-1 Product (runtime) usage
| ID | Finding | Evidence | Confidence |
|---|---|---|---|
| MU-F1 | [Verified Fact] No deny-listed AI/ML/LLM import in `hub/`, `tests/hub/` or `pyproject.toml` (rules R1, R3); scan result `findings: []` | `no-ai-check.json` | High (heuristic list; see CG-2) |
| MU-F2 | [Verified Fact] No dependency manifest or lock file exists; the hub has zero third-party libraries | `vendor-inventory.md` absences; SBOM | High |
| MU-F3 | [Verified Fact] HTTP client imports are allowed only under `adapters/` (rule R2); `urllib.request` is used there and in legacy scripts against loopback URLs | `hub/guards/no_ai.py`; `vendor-inventory.md` | High |
| MU-F4 | [Verified Fact] The sensor `record_model_call()` exists for a future approved AI element; nothing in the product calls it | `hub/obs/metrics.py` | High |
| MU-F5 | [Verified Fact] The 0C model-call inventory MC-01..MC-06 and token, context, loop budgets are retired as active budgets and kept dormant | ER-1 | High |

### MU-2 Model usage by purpose (all rows)
| Purpose | Model calls in product | Notes |
|---|---|---|
| T1 case triage explanation | 0 | rules with rule-trace text (qualification-decision.md) |
| T2 partner-feed exception classification | 0 | rules with reason codes and quarantine |
| T3 document Q&A | 0 | keyword / field search (`hub/search/engine.py`); AI-assisted option held only for RQ-1..RQ-3 re-qualification |
| T4 deviation/CAPA narrative | 0 | rules / templates |
| T5 cross-store investigation | 0 | rules (crosswalk); agentic rejected |

### MU-3 Build-tool usage (not product)
| ID | Finding | Evidence | Confidence |
|---|---|---|---|
| MU-F6 | [Verified Fact] The assistant is in the AI register and the vendor inventory (V-04); at the Stage 33 count 51 of 51 commits carried the co-author trailer; main is at 56 commits at 5efe271 (trailer not recounted here) | `vendor-inventory.md`; `git log` | High for the count at Stage 33 |
| MU-F7 | [Unknown] Plan, seat price, token consumption, data-use terms of the assistant | U-33-01 | n/a |
| MU-F8 | [Inference] Assistant usage is a real engineering cost driver (it did most authoring), but no figure can be derived from the repository. Reasoning: commit trailers show involvement, not volume | MU-F6 | Medium |

### MU-4 Model-version change control
No model, so none applies. If a model is ever introduced, the RQ-1..RQ-3 re-qualification and a new Dinesh decision come first (OD-08).

## Evidence References
`hub/guards/no_ai.py`; `hub/obs/metrics.py`; `docs/27-hardening/evidence/no-ai-check.json`; `docs/08-ai-qualification/qualification-decision.md`.

## Assumptions
- A-32-05 The deny-list's coverage is enough for a docs-stage statement of "no model usage in the repo as scanned"; it is heuristic (A-12-F10-2). Confirm: Dinesh.
- A-32-06 Build-tool spend is outside product unit economics and is tracked under FC-04. Confirm: Dinesh.

## Unknowns
- U-32-07 Assistant plan, charges and token use. U-32-08 Whether anyone else uses an AI assistant on this repository.

## Unresolved Issues
- Usage exports from the assistant, if any exist, are not in the repository.

## Residual Risks
- RR-32-05 Hidden dev-tooling cost transfers to whoever inherits the account (FF-04). Medium.
- RR-32-06 A heuristic deny-list can miss a vendored or renamed client. Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
