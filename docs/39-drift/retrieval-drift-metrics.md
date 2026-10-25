---
stage: "39 — Drift + Continuous Improvement"
artifact: "retrieval-drift-metrics.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["hub/search/__init__.py", "hub/search/cli.py", "hub/search/engine.py", "hub/search/fts.py", "hub/review/search.py", "hub/review/templates.py", "docs/31-observability/metrics-spec.md (search_engine)", "docs/10-architecture/", "docs/12-specs/", ".fde/orchestrator-decisions.md (OD-08, OD-12, OD-22)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
The product has retrieval but not semantic retrieval. `hub/search` is a derived, rebuildable corpus index over documents and archive items, using SQLite FTS5/trigram behind the `search.fts` flag (default off) or a fallback engine with the same grammar and ordering formula (`hub/search/__init__.py`, ADR-012, R2). There are no embeddings, no vector store, no reranker, no generation (OD-08). Retrieval drift is therefore: the index no longer matches its sources, the engine silently changes (FTS5 present or not), ordering changes for the same query, or review templates change. **Embedding drift, chunking drift and answer-faithfulness drift do not apply and are not invented.** The search capability is R2 and switched off by default, so the practical exposure today is small.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RD-1 Metrics
| ID | Metric | How measured | Candidate threshold (Assumption) | Tier | State |
|---|---|---|---|---|---|
| RM-01 | Engine in use | `python -m hub.search status --data-dir D` reports the FTS5/trigram probe and the selected engine and reason; Stage 31 exports `search_engine` (gauge, label engine) | engine value differs from the recorded baseline engine without a config or runtime change | INVESTIGATE | [Verified Fact] status command and metric exist |
| RM-02 | Index vs corpus parity | count of corpus documents + archive items versus rows in `search_doc` after the latest corpus load (status shows the latest load) | any difference after a load completes | INVESTIGATE; fix = rebuild (the index is derived and rebuildable, `drop-index` is the audited rollback) | [Verified Fact] index is derived; [Inference] parity query is a small read-only SQL (IB-08) |
| RM-03 | Golden query set order stability | a fixed list of queries run on a sandbox copy; compare ordered result ids to a recorded run | any reordering or missing/added id for an unchanged corpus and unchanged engine | INVESTIGATE; engine switch (FTS vs fallback) must give the same order by design ("same ordering formula"), so a difference is a defect candidate | [Unknown] no golden query set is recorded for search; [Assumption] one will be derived from the 22 injection docs + 10 variants + the 86 feed rows already in fixtures (PCH-31, OD-25) as a starting corpus (IB-08) |
| RM-04 | Query-safety invariants | every term is a bound parameter inside a quoted FTS phrase; hostile corpus yields 0 HTTP 500 and 0 markup (Stage 26 RT-07) | any 500, any active markup | CHANGE (security class) and treat as a finding | [Verified Fact] tested at Stage 26/27 (hostile corpus v1; lone-surrogate 400 fix) |
| RM-05 | Template drift | sha256 of each review template body (`hub/review/templates.py`), switched off by default (PCH-22: FR-REV-04 Could / R2) | any change not accompanied by a change record | CHANGE (C1) | [Inference] templates are code, so DC-3/DC-6 controls cover them; [Unknown] no per-template pin exists (IB-09) |
| RM-06 | C3 reason requirement | config `search.require_c3_reason` unchanged from decided value | changed without a decision | CHANGE (C3 flag move) | [Verified Fact] key exists in the closed config schema |

### RD-2 What is not measured
Relevance quality (precision/recall) is not measured: there are no relevance judgments and no users (Stage 35). An invented relevance target would be a fabricated number. If search is ever enabled for real use, a labelled query set and a relevance metric must be defined first (backlog IB-08 notes the prerequisite).

## Evidence References
See header.

## Assumptions
- A-39-08 The engine baseline is "whatever `search status` reports on the reference laptop at the time the first golden query run is recorded"; no baseline is recorded today. Confirm: Dinesh.

## Unknowns
- U-39-06 SQLite/FTS5 availability on any target host (floor SQLite 3.37, OD-14). Stage 20-27 evidence is from the laptop and a cloud workspace only.

## Unresolved Issues
- G-39-05 No golden query set and no per-template pin for the search/review layer.

## Residual Risks
- RR-39-06 FTS5 vs fallback engines could diverge on edge inputs after a runtime change (Python 3.12 move). Low while search is off.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
