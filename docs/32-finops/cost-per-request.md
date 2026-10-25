---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "cost-per-request.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/preliminary-finops-baseline.md FB-01..FB-12", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-2", "docs/37-operating-model/finops-ownership.md FC-01..FC-10", "docs/33-vendor-risk/vendor-inventory.md", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32", "docs/27-hardening/production-readiness-checklist.md PRC-R", "docs/27-hardening/evidence/regression/final-*.json", "docs/00-preflight/ai-economics/volume-assumptions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
A "request" is a call to the loopback HTTP surface or a CLI invocation of the hub. **Token cost per request is USD 0 by construction. Compute, hosting and human cost per request are Unknown** because nothing is deployed and no request has been served to a real user. The only measured per-unit time in the repository is **regression wall time per test method** (a toolchain unit, not a request): about 4.57 s on the laptop. It must not be reported as request latency or request cost.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CR-1 Cost formula (structure; inputs marked)
`cost_per_request = token_cost + compute_cost + storage_cost + review_cost`
| Term | Value | Class | Input Dinesh must supply |
|---|---|---|---|
| token_cost | USD 0 (0 calls) | [Verified Fact] FB-01/02; tripwire design in `cost-guardrails.md` | none |
| compute_cost | Unknown | [Unknown] FC-02 | Hosting decision (ADR-015 has no vendor) and its price |
| storage_cost | Unknown | [Unknown] FC-08 (retention is hold-all, OD-30) | Hosting price and retention policy |
| review_cost | Unknown | [Unknown] FC-07 | Measured reviewer minutes per flagged item (U-24) and a confirmed rate (0C uses USD 25/h as Assumption) |

### CR-2 Request volume
Not measured. 0C gives Assumed tiers (Low / Base / High): cases 4 / 167 / 1,670 per month; document-search queries 400 / 440 / 4,400 per month (the T3 driver is retained only as a usage metric, ER-1). [Assumption] synthetic, unvalidated.

### CR-3 Measured toolchain unit (not a request cost)
| Measure | Value | Source | Class |
|---|---|---|---|
| Regression groups | 25 | PRC-R | [Verified Fact] |
| Test methods executed / expected | 526 / 526 (525 ok, 1 registered skip) | PRC-R | [Verified Fact] |
| Summed wall time, one group per call, reference laptop, Python 3.10.12 | 2,403 s (about 40.1 min) | sum of PRC-R wall column | [Verified Fact] (arithmetic by this stage) |
| Longest group | 144 s (E26); device-call cap 180 s | PRC-R; OD-21 | [Verified Fact] |
| Egress-guarded groups (E8, E9, E20, E21, E23, E24, E26, E27) summed | 824 s | PRC-R | [Verified Fact] |
| Wall per method | about 4.57 s (2,403 / 526) | derived | [Inference] mean; most time is sandbox build and subprocess start, not per-method work (S26 sandbox build alone took 95 s once, PRC-R notes) |
| Cloud regression wall time and price | not recorded | OD-23, OD-34 | [Unknown] |

### CR-4 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CRQ-F1 | [Verified Fact] Token cost per request is 0 | tripwire evidence | None | Low | High | none |
| CRQ-F2 | [Unknown] Any monetary cost per request | FC-02, FC-07, FC-08 | Cannot state unit economics for the product | Medium | High | Hosting, review time, rate |
| CRQ-F3 | [Inference] When hosted, cost per request will be dominated by fixed hosting and human review rather than per-request compute, because per-request work is local rule evaluation and SQLite access. Reasoning: no external call exists (SS-01, V-11) | `vendor-inventory.md` | Fixed cost matters more than volume | Low | Low | Needs a load measurement (Stage 29) |
| CRQ-F4 | [Unknown] Request latency under production load | the NFR tests run in a test sandbox, not production | No per-request performance cost basis | Medium | n/a | Stage 29 measurement |

## Evidence References
`docs/27-hardening/production-readiness-checklist.md` PRC-R table; `docs/00-preflight/ai-economics/volume-assumptions.md`.

## Assumptions
- A-32-08 The 0C volume tiers are the only volume basis (synthetic, unvalidated). Confirm: Dinesh.
- A-32-09 Per-method wall time is a convenience statistic and is not a cost. Confirm: n/a.

## Unknowns
- U-32-10 to U-32-12: compute price, storage price, reviewer time (see CR-1).

## Unresolved Issues
- No request-level telemetry exists; Stage 31 absent.

## Residual Risks
- RR-32-08 Quoting 4.57 s per method as a product performance number. Low.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
