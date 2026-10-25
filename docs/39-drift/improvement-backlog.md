---
stage: "39 — Drift + Continuous Improvement"
artifact: "improvement-backlog.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 39 run)"
status: "DRAFT"
evidence_sources: ["docs/35-variance/corrective-action-backlog.md", "docs/39-drift/*.md", "docs/26-tevv/residual-tevv-risks.md", "docs/31-observability/observability-validation.md", "docs/28-reliability/resilience-readiness.md", ".fde/orchestrator-decisions.md (OD-32..OD-36)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 39 adds files under `docs/39-drift/` and changes nothing else). The product is No-AI (OD-08), not in production, loopback-only, synthetic data only; there is no production telemetry (OD-04). "Drift" here means DETERMINISTIC drift (rule-set, configuration, schema, golden/characterization, dependency/runtime, synthetic-baseline data, documentation-vs-code, ownership). No model, embedding or prompt drift is invented. Every threshold, cadence and window is a CANDIDATE ASSUMPTION written by the agent under OD-32, not a commitment, not a measured need, and not approved by Dinesh Naik. No risk is accepted here.**

## Summary
Twenty improvement items IB-01..IB-20 and nine decisions D-39-01..D-39-09 for Dinesh. **Every item is PROPOSED. None is started, approved or costed** (no effort figure exists; no rate, OD-04, Stage 32). Items that change code, config, controls, rule sets, owners or production state go through `controlled-change-process.md` and need Dinesh's recorded decision. Items marked "no decision needed" are read-only or documentation work in a sandbox. Priority is agent Inference: P1 prerequisite to any valid drift signal or has a near date, P2 closes a monitoring gap, P3 housekeeping. Owner of every item: Engagement lead (Dinesh Naik). Due: the trigger event stated, because no calendar date exists, except IB-02.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### IBL-1 Backlog
| ID | Item | Closes / links | Type | Decision needed? | Priority | Trigger / due |
|---|---|---|---|---|---|---|
| IB-01 | Run the first evaluation session per `continuous-evaluation-plan.md` CEP-2 on a sandbox copy and store the record | CEP-6, RR-39-12 | Evaluation (read-only) | No (start of session is Dinesh's call) | P1 | next working session |
| IB-02 | Decide the Python 3.10 end-of-life response: confirm the date, obtain 3.12+ regression and characterization evidence in the cloud workspace, decide the floor and the golden re-baseline | TRG-04, PM-12, D-27-02, RT-14, RR-39-07 | Evidence + decision | Yes (C6) | P1 | on or before 2026-10-31 (Assumption A-39-12) |
| IB-03 | Decide CT-13: pin Node 22.23.2 for the reference environment, or re-record the golden under a change record; until then register the exact signature as KNOWN-DRIFT | PM-11, S24-DEV-04, RR-39-08 | Decision | Yes (C2/C6) | P1 | before the next merge that needs a green harness |
| IB-04 | Capture the synthetic-baseline snapshot: per-table counts and the distributions in DM-05, in a sandbox, recorded as a baseline file under a new docs path | G-39-01, DM-04, DM-05, TRG-14 | Measurement (read-only) | No | P2 | before any pilot |
| IB-05 | Add an `as_of` parameter to hub metrics so ageing is reproducible (same item as CA-03) | DM-05, VL-12 | Code change | Yes (C1) | P2 | with Stage 30 scope decision |
| IB-06 | Write a read-only script set for KM-03 (FR register vs traceability), KM-07/KM-08 (ownership coverage; superseded front-matter scan) | G-39-02, KM-03/07/08 | Tooling, new files only | Yes (new tooling is C1 on a branch) | P2 | after Stage 30 |
| IB-07 | Adopt "as of commit <sha>" on every count quoted in a doc; add to document template | KM-04 | Convention | Yes (C0) | P3 | next doc stage |
| IB-08 | Build the search golden query set and engine/order parity check; define a relevance metric before search is ever enabled for real use | G-39-05, RM-02, RM-03, RD-2 | Test design | Yes (new tests are C1) | P3 | before enabling `search.fts` |
| IB-09 | Pin review templates (per-template sha256) | RM-05 | Tooling | Yes (C1) | P3 | with IB-08 |
| IB-10 | Scan docs and decision log for self-approval wording ("approved/accepted/signed" without an OD reference) | AM-06 | Review (read-only) | No | P3 | each docs stage |
| IB-11 | Check and record remote branch protection and required reviews (settings are outside this repo) | U-39-09, CCP-3a | Confirmation | Yes (Dinesh checks) | P1 | before relying on AM-01 |
| IB-12 | Install the CI workflow under `.github` with action SHA pins (HAR-07, D-27-03) | CCP-2, G-39-07 | Decision + change | Yes (C6) | P2 | Dinesh decision |
| IB-13 | Add a test that fails when a threshold or baseline file changes without a change-record reference | CCP-3d, CCP-5 | Test design | Yes (C1) | P2 | after IB-12 |
| IB-14 | Add a test that fails if a golden or MANIFEST is modified in the same commit as the code it checks, unless a decision id is cited | CCP-3c, CCP-4 | Test design | Yes (C1; harness is guarded by TST-CO-05 c) | P3 | after IB-13 |
| IB-15 | Compare `hub/config.py` closed schema to spec/doc sections mechanically (include the new Stage 27 config sections and error codes) | G-39-03, DC-2 | Tooling + spec addendum | Yes (D-27-05) | P2 | Stage 30 or later |
| IB-16 | Give every open decision, risk and finding a trigger event or date and an owner, so ageing can be computed | G-39-04, KM-06, KM-07 | Register hygiene | Yes (owners are Dinesh's) | P2 | before any pilot |
| IB-17 | Fix the metrics Stage 31 lists as gaps (`audit_chain_verify_ok` after F-29-01; `projection_mismatch_count`; `db_busy_total`; `exception_age_hours_p90`) and wire Stage 28 mechanisms where decided | G-39-06, ALT-04/05/10/11, F-29-01 | Code change | Yes (C1/C3) | P2 | Stage 30 |
| IB-18 | Decide whether a scheduler/reminder for E1 should exist (a reminder outside the repo is not a change to the product) | RR-39-11, OPD-11, HAR-10 | Decision | Yes (C3 if in-product) | P3 | Dinesh decision |
| IB-19 | On TRG-13 (real window, real data or pilot): recalibrate every candidate threshold from the first 30 days, re-run Stages 34, 35, 36 as v0.2, mark this stage v0.2 | TRG-13, OD-36 | Re-measure | Yes (trigger) | P1 on trigger | event |
| IB-20 | Record legacy `Dockerfile`/compose decisions: pin base image digest, keep or retire (floor 3.10 vs image 3.12) | PM-14, D-27-06 | Decision + change | Yes (C6) | P3 | Stage 30 |

### IBL-2 Decisions requested (all open)
| ID | Question | Recommended default (Assumption, not an approval) |
|---|---|---|
| D-39-01 | Accept the drift-layer reading in DF-1 (No-AI: deterministic drift only) | accept |
| D-39-02 | Accept the cadence in `evaluation-cadence.md` (E0..E4; monthly hygiene candidate) | accept as candidate |
| D-39-03 | Accept the triggers TRG-01..16 as candidates (not commitments) | accept as candidate |
| D-39-04 | Python 3.10 end of life: floor move now, or keep the 3.10 floor with 3.12+ target and record exposure | obtain 3.12+ evidence first (IB-02); decision stays Dinesh's |
| D-39-05 | CT-13: Node pin or golden re-record | Node pin for the reference environment (smaller blast radius); Dinesh decides |
| D-39-06 | Who runs evaluations after Stage 38/FINAL | Dinesh by default; any other name must come from Dinesh |
| D-39-07 | Confirm remote branch protection state; whether to install CI (HAR-07) | check first (IB-11), then decide |
| D-39-08 | Priority order of IB-01..IB-20 | as listed (P1 first) |
| D-39-09 | Whether any drift finding should become an accepted risk (none is accepted here) | no; leave all RS/RP/VA/RTR/F-xx open |

### IBL-3 Sequencing [Inference]
IB-02 (dated), IB-03, IB-11, IB-01 first; then IB-04, IB-05, IB-12, IB-13, IB-15, IB-16, IB-17; P3 items follow; IB-19 waits for its event. Doing P2 monitoring tooling before IB-01 would add detectors that were never exercised.

### IBL-4 What the backlog does not do
It does not accept any risk, move any threshold into a commitment, name any owner, activate any monitoring, or claim any improvement. Completing an item reduces the chance of undetected deterministic drift; it does not produce value that Stage 36 could count.

## Evidence References
See header; items cross-reference `docs/35-variance/corrective-action-backlog.md` CA-01..CA-17 where they coincide (CA-03 = IB-05, CA-10 = IB-12/IB-17, CA-14 routing of open registers).

## Assumptions
- A-39-20 Priorities and recommended defaults are agent Inference under OD-32 (scope/sequencing only). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-39-15 Effort and cost per item (no estimate; no rate exists).

## Unresolved Issues
- All 20 items and 9 decisions are open.

## Residual Risks
- RR-39-14 The backlog can be read as approved work. Status of every item is PROPOSED.
- RR-39-15 IB-02 has a near date and no 3.12+ evidence; if it slips, the floor interpreter is end-of-life with no recorded decision. Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 39). |
