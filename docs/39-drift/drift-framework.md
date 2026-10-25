---
stage: "39 — Drift + Continuous Improvement"
artifact: "drift-framework.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["hub/obs/catalog.py", "hub/obs/alerts.py", "hub/obs/slo.py", "docs/31-observability/alert-catalog.md", "docs/31-observability/slo-sla-definitions.md", "docs/26-tevv/release-thresholds.md", "docs/26-tevv/tevv-results.md", "docs/35-variance/corrective-action-backlog.md", "hub/policy/as_found_pins.json", "hub/adapters/baseline_pins.json", "hub/config.py", "hub/runtime.py", "docs/37-operating-model/change-governance.md", ".fde/orchestrator-decisions.md (OD-04, OD-08, OD-24, OD-32..OD-36)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
This stage defines how the engagement notices that something has changed that nobody decided to change. Because the hub is No-AI, the drift that can actually happen is deterministic and mostly detectable by hash, diff or count. Eight drift classes (DC-1..DC-8) are defined; each is mapped to a signal that already exists in the repository (pins, goldens, the Stage 31 metric catalogue and alert rules, the Stage 26 regression and characterization harness) or is marked as a GAP. Three tiers of response (WATCH, INVESTIGATE, CHANGE) link every signal to the controlled change process. **Nothing here is wired, scheduled or running: there is no scheduler (OD-19/OD-28), no alert delivery (OD-04, Stage 31 D-31-08), no production telemetry. The framework is a design plus the evidence that each detector can run offline.**

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### DF-1 Scope decision [Assumption A-39-02]
The Stage 39 prompt lists data, knowledge, retrieval, prompt, model and agent drift. For a No-AI product these are re-read as follows (decision taken under OD-32 default-answer authority; confirm: Engagement lead, Dinesh Naik):

| Prompt layer | Reading for this product | Artifact |
|---|---|---|
| Data drift | synthetic-baseline drift: the shipped 125-case SQLite and fixtures versus their pins; distribution of the baseline; schema of the legacy stores | `data-drift-metrics.md` |
| Knowledge drift | documentation-vs-code drift (specs, catalogues, counts quoted in docs), register drift (FR, deviation, risk), ownership drift | `knowledge-drift-metrics.md` |
| Retrieval drift | keyword/FTS search and template drift only (no embeddings, no vector index, no reranker) | `retrieval-drift-metrics.md` |
| Prompt / model drift | any appearance of a model call, egress, AI import or prompt-like artefact is the drift; plus rule-set and decision-policy drift as the product's "model"; plus runtime/dependency drift | `prompt-model-drift-metrics.md` |
| Agent drift | no product agents exist (OD-08); the drift that can exist is in how engagement/coding agents change the repository | `agent-drift-metrics.md` (largely N/A with process monitors) |

### DF-2 Drift classes [Verified Fact: each class has the cited detector or a cited gap]
| Class | What drifts | Existing detector (path) | State |
|---|---|---|---|
| DC-1 Rule-set / decision-policy drift | the three as-found rule sources and the archived decision-policy JSON change; a rule set is activated or edited | sha256 pins in `hub/policy/as_found_pins.json` (change = reviewed PR); rule sets ship INACTIVE (OD-16); Stage 31 invariant INV-03 / ALT-03 for Zone H acts | detector exists; no rule set is active (activation needs a human, holders EMPTY) |
| DC-2 Configuration / schema drift | hub config keys and defaults; SQLite tables; migrations; spec'd error codes and exit codes | closed key schema in `hub/config.py` (unknown key -> `E-CFG-INVALID`, Stage 27); migrations under `hub/store/migrations`, `hub/store/forward`, `hub/policy/migrations`; baseline table/column lists in `hub/adapters/baseline_pins.json`; insert-only `schema_migrations` triggers (A-27-05) | detector exists for keys and legacy tables; no automated "docs list == code list" check for config sections (GAP G-39-03) |
| DC-3 Golden / characterization drift | behaviour of the legacy-visible outputs versus recorded goldens, including environment-caused drift | `tests/characterization/` (CT-01..CT-18), `tests/characterization/golden/MANIFEST.sha256`, `python -m hub golden-compare` (exit 6 = UNAPPROVED / NOT-RUN by design), 133/134 CT checks passing with CT-13 `batch:node_cwd_other` failing on Node patch drift (S24-DEV-04) | detector exists; one known open drift (CT-13) |
| DC-4 Dependency / runtime drift | Python, SQLite, Node, Java versions; container base image; stdlib-only rule | `python -m hub selfcheck` (floor 3.10, option 3.12, `hub/runtime.py`); `python -m hub no-ai-check` (exit 9 on findings); `Dockerfile` pins `python:3.12-slim` while the device runs 3.10.12 | detector exists; runtime floor decision (OD-24) vs end-of-life (see `change-trigger-thresholds.md` CT-04) |
| DC-5 Data-distribution drift (synthetic baseline) | the 125-case baseline (seed 4100, OD-09) changes or is replaced by the 6,000-case alternative; backup diverges from working tree | `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` (OD-03/OD-03a); `hub/adapters/baseline_pins.json`; `tests/characterization/fixtures/FX-BASE125.sha256` | detector exists (hash); no distribution-shape snapshot exists (GAP G-39-01) |
| DC-6 Documentation-vs-code drift | numbers and lists quoted in docs (group counts, FR counts, alert ids, metric names) diverge from code | tests D03 (every catalogue name documented), C05, A01 (alerts have owner/action/runbook) in `tests/hub/test_tst_hub_stg31_*.py`; Stage 12 addenda process | partial: Stage 31 only; earlier stages have none (GAP G-39-02) |
| DC-7 Ownership / governance drift | owner of an asset becomes vacant or unaccepted; a decision stays open past its trigger; approvals missing | Stage 37 asset-ownership map (0/28 accepted steady-state owners, OD-34), `docs/37-operating-model/change-governance.md` change classes C0..C8, E | register exists on paper; nothing computes ageing (GAP G-39-04) |
| DC-8 Operational-signal drift | error ratio, auth failures, missed runs, queue depth/age, breaker state, SLO budget burn | Stage 31: 13 alert rules (`hub/obs/alerts.py`), 5 SLO candidates + 3 invariants (`hub/obs/slo.py`), `python -m hub.obs evaluate` | rules exist; 4 depend on unexported metrics, 4 on unwired Stage 28 mechanisms; no traffic exists |

### DF-3 Response tiers [Assumption A-39-03]
| Tier | Meaning | Allowed actions | Not allowed |
|---|---|---|---|
| WATCH | a signal moved but inside its candidate band | record in the evaluation log; no change | none required |
| INVESTIGATE | a signal crossed its candidate threshold, or a detector cannot run | read-only analysis in a sandbox copy; open an improvement-backlog item | change code, config, rules, baselines or thresholds |
| CHANGE | investigation shows a change is needed | raise a change request in the class of `change-governance.md` (C0..C8/E); run the controlled change process | any edit outside the process; waiving a SEV-A/SEV-B; accepting a risk (agent never does) |
STOP is not a tier but a standing rule: any model call, egress attempt or non-human Zone H act (INV-01..03) is an incident (Stage 29) and not a drift event.

### DF-4 Baselines are preserved [Verified Fact: rule; Inference: mechanism]
Drift is only meaningful against a recorded baseline. The baselines that already exist and must never be edited to make a signal go green: backup `SHA256SUMS.txt` (OD-03a), `baseline-as-found` tag (OD-06, a6eb4e8), as-found pins, legacy baseline pins, characterization goldens and MANIFEST, Stage 26 thresholds RT-01..RT-15 (declared before results), Stage 31 SLO candidates. A baseline is replaced only by a new version with a change record (see `controlled-change-process.md` CCP-4); the old version stays.

### DF-5 What is deliberately not monitored
Latency target (none exists, PNFR-06 Unknown), cost per case (Stage 32: all costs Unknown except model spend USD 0), user adoption (no users, Stage 35), model quality (no model). Where Stage 35/36 say a value is NOT COMPUTABLE, this stage does not compute a proxy for it.

## Evidence References
`hub/policy/as_found_pins.json`, `hub/adapters/baseline_pins.json`, `hub/config.py`, `hub/runtime.py`, `hub/cli.py` (selfcheck, golden-compare, no-ai-check), `hub/obs/{catalog,alerts,slo}.py`, `tests/characterization/`, `docs/26-tevv/{release-thresholds,tevv-results}.md`, `docs/31-observability/*`, `docs/35-variance/corrective-action-backlog.md`, `docs/37-operating-model/change-governance.md`, `.fde/orchestrator-decisions.md`.

## Assumptions
- A-39-01 Artifact directory is `docs/39-drift/` as instructed by the orchestrator, not `docs/39-continuous-improvement/` as written in the stage prompt. Confirm: Engagement lead (Dinesh Naik).
- A-39-02 The drift-layer re-reading in DF-1 is accepted. Confirm: Engagement lead (Dinesh Naik).
- A-39-03 Three response tiers. Confirm: Engagement lead (Dinesh Naik).
- A-39-04 Nothing in this stage runs code; detector availability is taken from the cited code and from Stage 26/31 recorded results, not re-executed here. Confirm: orchestrator.

## Unknowns
- U-39-01 Whether the hub will ever receive production data or telemetry (D-34-01/02); until then every operational-signal threshold has no empirical anchor.
- U-39-02 Who runs the evaluations after Stage 38 (OD-34 open item: who runs orchestrator duties).

## Unresolved Issues
- Gaps G-39-01..G-39-05 (see `continuous-evaluation-plan.md` CEP-5); none closed by this stage.

## Residual Risks
- RR-39-01 A detector that exists but is never run provides no protection (no scheduler, no alert delivery). Medium.
- RR-39-02 Hash pins detect change but not intent; a reviewed PR that changes a pin is the control, and review has one person (DQ-17 single-approver risk, open). Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
