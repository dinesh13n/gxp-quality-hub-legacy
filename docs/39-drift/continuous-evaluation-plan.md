---
stage: "39 — Drift + Continuous Improvement"
artifact: "continuous-evaluation-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["docs/39-drift/*.md", "hub/cli.py", "hub/obs/cli.py", "hub/search/cli.py", "tests/characterization/run_characterization.py", "tests/hub/run_hub_groups.py", "docs/26-tevv/tevv-plan.md", "docs/31-observability/operational-runbook.md", "docs/31-observability/evidence/results.json", ".fde/orchestrator-decisions.md (OD-03a, OD-23, OD-32, OD-35, OD-36)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
The runnable plan: which evaluation sets exist, how an evaluation session is executed safely, how it is recorded, what cannot yet be evaluated, and the order in which gaps are closed. **This stage executed none of it** (docs-only; detector availability is taken from cited code and recorded Stage 26/31 results). A first real session is backlog item IB-01.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### CEP-1 Evaluation sets
| Set | Contents | Exists today? | Source |
|---|---|---|---|
| ES-1 Integrity | backup checksum, as-found pins, legacy baseline pins, fixture and golden manifests | yes (hash checks) | DM-01..03, PM-06 |
| ES-2 Behaviour | full hub regression (27+ groups as of Stage 27; the count grows), characterization CT-01..CT-16 | yes | RT-01, RT-03; `tests/hub/run_hub_groups.py --all`; `tests/characterization/run_characterization.py` |
| ES-3 Tripwires and controls | `no-ai-check`, zero-counters, Zone H, rule-set activation, config flags | yes | PM-01..05, PM-07, PM-10 |
| ES-4 Operational | `python -m hub.obs evaluate` over sample files; SLO candidates; alerts | rules yes, input data no (no traffic, 4 rules need unexported metrics, 4 need unwired mechanisms) | Stage 31 |
| ES-5 Knowledge | doc-vs-code tests, register and ownership coverage, open-decision ageing | partial (Stage 31 only) | KM-01..08 |
| ES-6 Runtime | `selfcheck`, toolchain versions, dated triggers | yes | PM-11..15 |
| ES-7 Search | `search status`, index parity, golden queries | status yes; golden queries no | RM-01..06 |
| ES-8 Distribution | snapshot compare | no | DM-04, DM-05 |

### CEP-2 Session procedure (E1/E2/E3) [Assumption: procedure; Verified Fact: each command exists as cited]
1. Declare the session: date, commit sha, reason (cadence or trigger), operator, and which sets run. Do not change a detector or threshold during the session.
2. Sync: use a FULL copy of the repo outside the working tree (OD-03a) at the commit under evaluation; never run against working-tree `data/`.
3. `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` from repo root: record rc (must be 0) [ES-1].
4. Pins: compare the as-found and baseline pins to the files; golden MANIFEST check [ES-1].
5. Toolchain: `python -m hub selfcheck`; record node/java versions as the harness records them [ES-6].
6. Tripwires: `python -m hub no-ai-check` (rc 0 expected) [ES-3].
7. Behaviour: run groups per the runner, respecting the 180 s per-call device cap (split calls as in OD-21) [ES-2]; characterization only on the reference laptop (Python 3.10.12 goldens, OD-23).
8. Operational: if sample files exist, `python -m hub.obs evaluate --samples NOW [--previous BEFORE]`; report `no_data` rules as NOT-RUN [ES-4].
9. Knowledge: run the doc-vs-code tests; walk KM-03..KM-08 by hand until scripts exist [ES-5].
10. Re-run step 3; record rc. Delete sandbox copies (OD-16 housekeeping).
11. Write the evaluation record (CEP-3). Classify every result as pass / watch / investigate / NOT-RUN. Open backlog items for INVESTIGATE results. Do not "fix" anything in the session.

### CEP-3 Evaluation record (proposed format) [Assumption]
One new file per session, never overwritten: `docs/39-drift/evaluations/EVAL-YYYY-MM-DD-nn.md` (created by a future run through the change process, class C0). Fields: session id; commit sha; operator; trigger; sets run; for each metric id the observed value, baseline reference, tier; NOT-RUN list with reasons; backlog items opened; checksum rc before/after; label "synthetic, unvalidated". Thresholds used are cited by version of `change-trigger-thresholds.md`.

### CEP-4 Roles
Evaluation operator: Dinesh Naik or an agent he starts. Decision on any CHANGE: Dinesh. Reviewer of the record: nobody else exists; this is the single-approver risk (DQ-17, open, not accepted here). Roles RL-02, RL-03, RL-04 and others remain VACANT (OD-34).

### CEP-5 Gaps that stop parts of the plan (non-blocking for this stage; each needs an owner)
| ID | Gap | Blocks | Owner / due |
|---|---|---|---|
| G-39-01 | no distribution snapshot or per-table count baseline | DM-04, DM-05, TRG-14 | Engagement lead (Dinesh Naik); before any pilot or production use |
| G-39-02 | no doc-vs-code check outside Stage 31 (FR register parse, counts, back-references) | KM-03, KM-04, KM-08 | same |
| G-39-03 | config sections in docs not machine-compared to `hub/config.py` closed schema (Stage 27 spec addenda for new codes/config sections are an open decision D-27-05) | part of DC-2 | same |
| G-39-04 | open-decision and ownership ageing not computed; items have no due dates | KM-06, KM-07, TRG-11 | same |
| G-39-05 | no golden query set; no per-template pin for search/review | RM-03, RM-05, TRG-16 | same |
| G-39-06 | Stage 31 alerts ALT-04/05 need unexported metrics (F-29-01 `verify-audit` KeyError routed to Stage 30); ALT-10/11 need Stage 28 mechanisms wired (D-28-01) | DC-8 partly | same |
| G-39-07 | no alert delivery, no scheduler, no CI installed (HAR-07), so nothing notices drift unless a person runs a session | all | same |

### CEP-6 Exit criteria for "continuous evaluation is operating" (not met today)
At least one recorded session with all ES-1..ES-3 sets passing and NOT-RUN items listed; an owner accepted by Dinesh for the evaluation duty; G-39-01..05 closed or accepted open with a decision; TRG-13 re-calibration done once real data exists. None is met, which is why no "operating" claim is made.

## Evidence References
See header.

## Assumptions
- A-39-17 The command forms cited in CEP-2 work as documented in `hub/cli.py` and `hub/obs/cli.py` on a sandbox copy; they were not re-run in this stage.

## Unknowns
- U-39-12 Wall time of a full session on a fresh host; U-39-13 whether the reference laptop stays available (it is the only place the goldens are valid, OD-23).

## Unresolved Issues
- IB-01 (first session) not done. Evaluation records location not yet created.

## Residual Risks
- RR-39-12 The plan is only as good as the first session; until run, detector claims are inherited from earlier stages. Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
