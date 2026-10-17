---
stage: "7 — Deep Brownfield Repository Assessment & Behaviour Baseline"
artifact: "maintainability-assessment.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/07-repo-assessment/evidence/analysis/static_analysis.json", "docs/07-repo-assessment/evidence/analysis/coverage_trace_unittest.json", "docs/07-repo-assessment/evidence/analysis/mutation_probe.log", "app/*.py", "tests/*.py", "README.md", "docs/*.md", "scripts/*", "run.sh", "docs/00-preflight/discovery/security-observability-overview.md", "docs/00-preflight/discovery/technology-inventory.md"]
supersedes: "none"
---
## Summary

Maintainability is **Low-to-Moderate**: the system is small (1,435 tracked non-documentation lines; 818 Python) and dependency-free, which makes it *cheap to understand in volume* and *cheap to run* (0.6 s test suite, standard library only). It is **expensive to change safely** because (a) code density and style are hostile to review (semicolon one-liners, lines up to 922 chars, mixed indentation, no docstrings/types), (b) behaviour is guarded by almost no effective tests, (c) configuration and paths are implicit and global, (d) rules are duplicated across four languages, and (e) there is no logging or runtime visibility. Scores below use a 1 (poor) - 5 (good) rubric defined in the table; they are [Inference] from the measurements and are comparative, not industry-calibrated.

## Findings

### Scorecard

| Dimension | Score | Rubric anchor | Key evidence | Class |
|---|---|---|---|---|
| Size / comprehensibility | 4 | < 2 kLOC, flat structure, 18 app modules | 818 py lines; largest file 75 lines | [Verified Fact] / [Inference] |
| Readability / style | 1 | Consistent formatter, readable lines | 90 lines > 160 chars, longest 922; 20 files use `;`; 11 files 1-space vs 24 4-space | [Verified Fact] |
| Documentation of code | 1 | Docstrings/types on public API | 0/58 functions documented or annotated; 13/35 modules have a docstring | [Verified Fact] |
| Documentation of system | 3 | Accurate, current docs | many docs (README, 16 `docs/*.md`) but several inaccurate/destructive (AD-05..AD-09, README section duplicated 3x) | [Verified Fact] |
| Complexity | 3 | No function above CC 15 | 7 functions CC >= 15 (max 28 `server.do_GET`); 3 are test-data generators | [Verified Fact] |
| Modularity / coupling | 2 | Explicit interfaces | shared SQLite bus, import-time globals, hard-coded paths, standalone writers (DM-10..13) | [Verified Fact] |
| Duplication | 2 | Single source for rules | rules in 4 languages (LP-06); pagination x3; domain constants per generator | [Verified Fact] |
| Testability | 2 | Hermetic, injectable | `LEGACY_DB` at import; 5 writers ignore it; suite destroys data (TQ-01); servers not injectable | [Verified Fact] |
| Test effectiveness | 1 | Mutation score / behaviour assertions | 47.9 % lines, 1/15 mutants killed | [Verified Fact] |
| Build / run reproducibility | 3 | One-command, pinned | stdlib only so trivial to run; no lock/pin, Java/Node ad hoc, run from repo root only, `python` vs `python3` | [Verified Fact] |
| Observability | 1 | Logs, metrics, traces, correlation | no logger; `LOG_LEVEL` unused; static `/health`; gateway silent; no run records for batch jobs | [Verified Fact] |
| Change safety (overall) | 1 | Safe to change with fast feedback | min of testability/effectiveness/observability | [Inference] |
| Onboarding (new engineer) | 3 | < 1 day to run and reason | easy to run; hard to trust (docs conflict with behaviour); this stage's goldens materially help | [Inference] |

### Observability detail (Required Analysis #8)

| ID | Finding | Class | Evidence |
|---|---|---|---|
| MA-01 | No structured logging; API prints one stderr access line per request; gateway `log_message` is a no-op; batch CLIs print JSON to stdout only; no timestamps in access lines | [Verified Fact] | `server.py` L61, `source_gateway/server.py` L38; probe output |
| MA-02 | No correlation/trace ids in code (the only `correlation_id` values are fabricated in `ops/legacy_log_sampler.py` and lake events) | [Verified Fact] | grep; sampler is an orphan script |
| MA-03 | Batch jobs leave no durable run record: `reconcile` writes nothing to `batch_runs` (60 seeded rows are data); bridge records only the checkpoint; night-shift/Java print and exit | [Verified Fact] | BB-04/05/07 |
| MA-04 | `/health` is a static literal (does not touch the DB); `workshop_check` is the only deeper check and is a CLI | [Verified Fact] | `server.py` L13 |
| MA-05 | No metrics endpoint other than business counts at `/api/metrics`; no latency/error counters | [Verified Fact] | `server.py` L16-21 |
| MA-06 | Failure visibility: bridge counts invalid events but does not store/emit them; Java skips unparsable rows silently; reconcile raises on malformed JSON (aborting the batch) | [Verified Fact] | BB-04/05/08 |
| MA-07 | Operational docs exist (runbook 5 lines, one incident record INC-2025-014) but do not match behaviour ("queue retried twice" has no counterpart) | [Verified Fact] | RC-6 |

### Change-friction hot spots (where a change is most likely to cause regression)

1. `app/server.py do_GET` - all API behaviour in one function; no HTTP tests. Mitigation: CT-04.
2. `app/partner_feeds.reconcile` - destructive state machine, 21.5 % covered. Mitigation: CT-08.
3. `app/store.py` - import-time global used by 11 modules. Any change to connection/config ripples to all.
4. `legacy_batch/shift_reconciliation.py` and `sql/legacy_reports.sql` - join semantics; golden pins current (wrong) totals.
5. `legacy_js/legacy_policy.js` / archive JSON - policy semantics, default 999,999.

### Strengths worth preserving

* Zero third-party dependencies; offline; deterministic generators with seeds (5 of 7 datasets exactly reproducible, BB-12).
* Fast feedback (< 1.5 s for the whole verify script).
* Parameterised SQL everywhere; allow-lists for URL-derived table names.
* Idempotency keys already used in two intake paths (message_id; file digest).
* Read-only inventory scripts (`offline_inventory.py`) use `mode=ro` URIs - good practice to reuse.

## Evidence References

`evidence/analysis/static_analysis.json` (per-file lines, max line length, CC, docstrings); `evidence/analysis/coverage_trace_unittest.json`; `evidence/analysis/mutation_probe.log`; code references as listed.

## Assumptions

- A-07-17: Scores are comparative judgement from measured proxies; no organisational maintainability or coding standard is available as a repository artefact. Confirm standards target: Engagement lead (Dinesh Naik), Stage 14.

## Unknowns

- Team size, skills and release cadence of the real maintainers (not in repository; OD-04).

## Unresolved Issues

- Whether to adopt a code formatter as a first, purely mechanical step (large diff) - decision for Stage 14 after golden suite exists.

## Residual Risks

- R-07-13: Mechanical reformatting before characterisation tests exist could mask behavioural regressions inside a huge diff; sequence must be tests first, format second.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial maintainability assessment. |
