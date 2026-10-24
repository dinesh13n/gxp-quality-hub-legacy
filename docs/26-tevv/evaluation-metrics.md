---
stage: "26 — TEVV + AI Red Teaming"
artifact: "evaluation-metrics.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["docs/18-delivery/evaluation-rubric.md", "tests/hub/_groups.py", "tests/hub/run_hub_groups.py", "docs/26-tevv/release-thresholds.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Metrics are counts of observations on synthetic data in sandbox copies; none is a performance, quality-of-decision, value, time or cost claim. No AI-quality metric (groundedness, relevance, abstention, hallucination rate, model cost) is defined because the product has no model (OD-08, ER-1).**

## Summary
Fourteen metrics M-01..M-14, each with a formula, unit, denominator, the tool that produces it and the threshold that consumes it. Counting rules are fixed here so a result cannot be re-counted to look better.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### EM-1 Metric definitions [Verified Fact: declared]
| ID | Name | Definition | Unit / denominator | Produced by | Used by |
|---|---|---|---|---|---|
| M-01 | Failure count | FAIL + ERROR test records in a group run | count; denominator = executed methods | `run_hub_groups.py` / driver `unittest-result.json` | RT-01, RT-02 |
| M-02 | Completeness | executed methods == statically selected methods (`_groups.expected`) | boolean per group | `run_hub_groups.py` field `complete` | RT-01 |
| M-03 | Checksum status | exit code of `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` | rc, before and after | runner `checksum_rc_pre/post` | RT-04 |
| M-04 | Egress attempts | entries in `hub.guards.egress.attempts()` during a guarded run | count | `test_tst_hub_stg26_egress_guard.py` (E26) | RT-05 |
| M-05 | Model calls | `model_calls_total` tripwire | count | `hub.obs.metrics.tripwires()` | RT-05 |
| M-06 | Mutant kill ratio | KILLED / (KILLED + SURVIVED); NOT-APPLIED and INCONCLUSIVE are reported separately and never counted as killed | ratio and list | `evidence/s26_mutation_gate.py` | RT-06 |
| M-07 | Server-error rate | HTTP 500 responses / adversarial requests sent | count (must be 0) and denominator | S26-B* | RT-07 |
| M-08 | Active-markup hits | tag pattern `<(script|img|svg|iframe)` in `text/html` bodies; non-JSON non-HTML bodies without `nosniff` | count | S26-B02/B03 | RT-07 |
| M-09 | State-change count | rows added or changed in every non-audit table across a refused or hostile request set (snapshot of per-table counts and a content hash of mutable tables) | count of tables that differ | S26-A*, S26-B* | RT-07, RT-09, RT-10 |
| M-10 | Invariance diffs | number of differing decision-relevant fields (decision events, case state, rule results, flags, metrics) between a hostile-text run and a neutral-text run on identical stores | count | S26-B04 | RT-08 |
| M-11 | Authorisation cell mismatches | cells (route x principal) whose outcome class differs from the registry-derived expectation | count / cells | S26-A01 | RT-09 |
| M-12 | Zone H bypass count | Zone H attempts accepted or footprint changes, with the shipped empty holder list or an ineligible identity | count / attempts | S26-A02, A03 | RT-10 |
| M-13 | Leakage hits | occurrences of secret markers (password hash/salt values, token digests, issued tokens, `Traceback`, `sqlite3.` text, absolute sandbox paths) in response bodies and headers | count / responses scanned | S26-B07 | RT-11 |
| M-14 | Resilience outcomes | per fault: observed error code or refusal, `integrity_check`, `verify-audit` result | table | S26-C* | RT-12 |

### EM-2 Counting rules [Verified Fact: declared]
1. A test method is one unit; skipped methods are counted separately and only the registered skip is allowed (RT-01).
2. Per-class results for corpus tests list class sizes (strings per class) so a partial run cannot pass unnoticed (the corpus size is hash-pinned, `adversarial-dataset-spec.md`).
3. A response is "scanned" only when its body was decoded; a decode failure is reported, never skipped silently.
4. State-change comparison excludes `audit_log` and the HTTP-level metrics counters; the audit table is checked separately: refusals must ADD audit rows, never remove or alter them, and the chain must verify afterwards.
5. A metric without a denominator in the result file is not reported as met.

### EM-3 Not defined, on purpose [Inference]
Latency percentiles, throughput, memory (class C, Stages 28/31); search recall@10 (no labelled set, OPD-12); cost per case (class C proxy only); any model metric (No-AI).

## Evidence References
`docs/18-delivery/evaluation-rubric.md` ER-1..ER-5; `tests/hub/_groups.py`; `tests/hub/run_hub_groups.py`; `docs/26-tevv/release-thresholds.md`.

## Assumptions
- A-26-07 [Assumption] Table-count and content-hash snapshots are enough to show "no state change" for refused requests; they do not see in-memory metrics counters (excluded by rule 4).

## Unknowns
- U-26-05 Whether any consumer outside the repo depends on a metric name here (none known).

## Unresolved Issues
- None.

## Residual Risks
- RR-26-05 Count-based evidence cannot show absence of an unknown attack class.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue; declared before any S26 test ran. |
