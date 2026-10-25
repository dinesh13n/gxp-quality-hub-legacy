---
stage: "32 — Token Efficiency + AI FinOps + TCO"
artifact: "cache-effectiveness.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/00-preflight/ai-economics/preliminary-finops-baseline.md FB-01..FB-12", "docs/08-ai-qualification/economics-baseline-reconciliation.md ER-1..ER-4", "docs/37-operating-model/finops-ownership.md FO-1..FO-3", "docs/33-vendor-risk/vendor-inventory.md V-01..V-11", ".fde/orchestrator-decisions.md OD-04, OD-07, OD-08, OD-23, OD-32, OD-33, OD-34", "hub/search/engine.py L187", "hub/store/hardening.py L24-34", "hub/web/app.py L9, L36", "docs/00-preflight/ai-economics/token-flow-scenarios.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only (Stage 32 adds files under docs/32-finops/ and changes nothing else). The only human is Dinesh Naik, Engagement lead (OD-04). The product is No-AI (OD-08): model/token spend is USD 0 by design. No cost, price, rate, quote, invoice, owner or approval is invented here: every number is either Measured from repository evidence, quoted from an earlier-stage Assumption with its provenance, or Unknown with the input Dinesh must supply. Nothing here accepts a risk on Dinesh's behalf (HAR-11, TP-14); default-answer choices are assumptions under OD-32.**

## Summary
**Prompt cache, semantic cache and model-response cache: none exist, because there is no model.** The only caches in `hub/` are two in-process memoisations and an HTTP header that forbids caching. None has a hit-rate metric, and none has a cost attached. Cache effectiveness in the token sense is **not applicable**; no hit rate is invented.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CE-F1 | [Verified Fact] No LLM prompt or response cache; no embedding store; no vector database dependency (deny-list names chromadb, faiss, pinecone, weaviate, qdrant) | `hub/guards/no_ai.py`; SBOM | Token-cache metrics (cached input share, hit rate) are not applicable | None | High | none |
| CE-F2 | [Verified Fact] Search corpus statistics are "cached per load" in the search engine | `hub/search/engine.py` L187 | Avoids recomputing whole-corpus token statistics (keyword counts, not model tokens); saving not measured | Low (stale until reload) | High | Does a reload follow every corpus change? |
| CE-F3 | [Verified Fact] A module-level cache holds one (sha256, text) pair for the hardening manifest | `hub/store/hardening.py` L24-34 | Avoids re-reading one file; not a cost driver | Low | High | none |
| CE-F4 | [Verified Fact] Every HTTP response carries `Cache-Control: no-store` and CSP `default-src 'self'` | `hub/web/app.py` L36 | No client or intermediary caching by design (privacy and Zone H safety) | Low | High | none |
| CE-F5 | [Inference] "Token" in `engine.py` means keyword token, not model token; do not mix it into FinOps token metrics. Reasoning: the module has no model import (MU-F1) | `hub/search/engine.py` | Avoids a false "token" series | Low | High | none |
| CE-F6 | [Unknown] Hit rate, latency or CPU saving of CE-F2/CE-F3 | no instrumentation | Cannot rank as an optimisation | Low | n/a | Only matters if CPU or hosting cost becomes non-trivial |

**Rule for any future cache** (proposal, needs a C6 change): a cache must name its invalidation rule, must not retain restricted evidence beyond the access rule that protected it (F-02 / A-27-02), and must publish hit and miss counters before it is claimed as a saving.

## Evidence References
`hub/search/engine.py`; `hub/store/hardening.py`; `hub/web/app.py`; `docs/00-preflight/ai-economics/token-flow-scenarios.md` (dormant).

## Assumptions
- A-32-07 Caches in CE-F2/F3 are too small to matter for cost. Confirm by measurement if hosting cost is ever dominated by CPU (Dinesh).

## Unknowns
- U-32-09 Cache hit rates (no instrumentation).

## Unresolved Issues
- No metrics exist for cache behaviour; none is needed for a zero-model product today.

## Residual Risks
- RR-32-07 A future AI element could bring token caches whose security impact (cross-user leakage) is not assessed. Medium, conditional on RQ re-qualification.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 32). |
