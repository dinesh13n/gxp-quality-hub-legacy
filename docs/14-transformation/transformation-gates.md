---
stage: "14 — Transformation / Migration Plan"
artifact: "transformation-gates.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/14-transformation/evidence/increment-test-map.csv + increment-test-map-summary.txt (241 planned tests assigned by script)", "docs/13-traceability/evidence/tests_plan.csv, rtm.csv", "docs/13-traceability/traceability-summary.md (C1..C5)", "docs/12-specs/spec-readiness.md RD-3 (OD-S12-01..19), RD-4", "docs/12-specs/features/f10-coexistence-change-safety.md (G1..G10, DV-01..09, AC-CO-01..15)", "docs/07-repo-assessment/characterization-test-plan.md (CT-H1..H7, CT-01..CT-18)", "docs/07-repo-assessment/evidence/golden/{api,batch,lib}_golden_run1.json", "docs/07-repo-assessment/repo-transformation-readiness.md (R-1..R-12)", "docs/00-preflight/operating-contract/ (HAR, STOP, WB)", ".fde/orchestrator-decisions.md (OD-01, OD-03a, OD-05, OD-08, OD-09, OD-10)", "git: tag baseline-as-found; remotes/origin/main present"]
supersedes: "none"
---
## Summary
**Label: synthetic repository; DRAFT plan, not an approval. No test listed here has been run; all are PLANNED / NOT-RUN.**
This file defines (1) the **common gate** every Stage 15 increment must pass, (2) the **per-increment gates** INC-01..INC-09 (entry criteria, tests that must pass by planned ID, exit criteria, rollback, branch/PR), (3) the **Stage 15 entry checklist** separating the minimum approvals for INC-01 (harness only) from decisions needed later, and (4) the **Stage 16 behaviour-comparison protocol** that defines what "every behaviour difference must be explained" means in practice.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->

### TG-1 Stage 15 ENTRY CHECKLIST (owner of every item: Engagement lead (Dinesh Naik))
**(a) Minimum to start INC-01 (harness + hermetic fixtures, zero behaviour change)** — nothing else is required:
| # | Item | Recommended default | Status | Tag |
|---|---|---|---|---|
| E-1 | Approve harness approach HD-1: subprocess-per-scenario in a full sandbox repo copy, **no refactor of legacy code** (transformation-backlog TB-3) | Option B | OPEN | [Inference] |
| E-2 | Confirm write boundary: `tests/characterization/` (and goldens under it) may be added on a `stage-15-*` branch (WB-04; Stage 7 A-07-18) | Yes | OPEN | [Verified Fact] WB-04 requires branch-only |
| E-3 | Accept that Stage 13 condition C1 ("resolve decision-dependent items before Stage 15 build") is satisfied **per increment** (TG-1b) rather than all-upfront; and C3 (AC links for CT-04..CT-16) is delivered inside INC-01 | Accept | OPEN | [Verified Fact] C1/C3 text |
| E-4 | Interpreter for INC-01: device Python 3.10.12 (only interpreter present); 3.12 parity run recorded as a gap, not a blocker (CT-H5 partial). This is **not** the OD-S12-12 runtime decision | Accept 3.10.12 | OPEN | [Verified Fact] no python3.11/3.12 on device |
| E-6 | Branch/PR strategy: one branch + one PR per increment named `stage-15-incNN-<slug>` (fits OD-01 pattern `stage-NN-*`), squash-merged in order by the orchestrator (HAR-04) | Per-increment branches | OPEN | [Inference] |
| — | Already satisfied: OD-08 No-AI (approved), OD-09 baseline 125 cases / seed 4100 (approved), OD-03a sandbox rule (done), backup manifest (R-3 met), GitHub remote `origin/main` present | — | DONE | [Verified Fact] |
| — | **Not needed for INC-01**: any OD-S12-xx, any DV-01..09, OPD-05, OPD-13/PRD approval, scheduler/HAR-10, OD-S12-12 runtime, HAR-06/07/08 (no logic, config or dependency change; stdlib `unittest` only) | — | — | [Inference] |

**(b) Needed before later increments** (each may be *decided* or *accepted-open with the default*; accepted-open is legitimate per RD-3/BR-02):
| Before | ID | Decision | Recommended default (RD-3) | Note |
|---|---|---|---|---|
| INC-02 | E-5 | Build on PROPOSED ADRs (001/002/003/018 first) and DRAFT specs **at risk** pending OD-S12-14 / OPD-13 | Accept at risk | HAR-11: not an approval of the ADRs |
| INC-02 | E-2b | `hub/` new top-level package treated as WB-04-class path (A-14-01) | Yes | |
| INC-02 | OD-S12-12 | Target runtime (ADR-018 3.12 vs pyproject ≥3.10 vs device 3.10.12) | floor 3.10 / SQLite 3.37, FTS5 optional | no `pyproject.toml` change (avoids HAR-07); run as `python -m hub` |
| INC-03 | OD-S12-09 | Retention | hold-all, no delete paths | |
| INC-03 | OD-S12-18 | Audit anchor location | file outside DB dir via config | |
| INC-03 | A-14-08 | DDL/config-schema addenda as new files on branch (Stage 12 not edited) | Yes | |
| INC-04 | OD-S12-04 | Rule authority / active set / 999,999 default | no active set; as-found sets read-only; default preserved + marked (DV-06) | |
| INC-04 | A-14-07 | Thresholds transcribed as data, parity-proven | Yes | |
| INC-05 | OD-S12-03 | Closing set without closure policy | `treat_label_CLOSED_as_closing` | both modes tested |
| INC-05 | OD-S12-07 | Evidence sufficiency | structural presence only | |
| INC-05 | OD-S12-15 | Who records FACT_OPS_CLOSED / FACT_EVIDENCE_COMPLETE | human roles only | |
| INC-05 | OD-S12-16 | Transition table | `structural` | |
| INC-05 | OD-S12-19 | Case creation path | R1 = legacy backfill only | |
| INC-06 | OD-S12-17 | Re-delivery identity key | natural key (partner, record_kind, ref_id, source_ts) — **recommend an explicit decision** (DR-1 High) | Stage 11 v0.2 addendum |
| INC-06 | OD-S12-11 | Source-contract scope | `record_only` per source | |
| INC-07 | OD-S12-10 | Scheduler vs HAR-10 | schedule disabled | |
| INC-07 | OD-S12-01/-02/-08 | Closed/resolved definitions, 48 h clock, month-end cut-off | accepted-open → verdict `not_available_no_adopted_policy` | |
| INC-08 | OD-S12-05 (= OPD-05) | Where disposition is recorded | mode `none` | blocks pilot use only |
| INC-08 | OD-S12-06 | Dispositioner role holders | `[]` | blocks pilot use only |
| INC-09 | OD-S12-14 (= OPD-13) | PRD / R1-R2 split approval | — must be decided | R2 not started on DRAFT |
| Stage 30 | OD-S12-13 | Preserve-vs-fix DV-01..DV-09 | all `proposed` | needed only for CUT-2..CUT-4 |
| Stage 30 | OD-S12-14 | PRD/NFR/ADR approval | — | needed for CUT-1 |

### TG-2 Common gate (applies to every increment; "exit" = PR may be merged)
| # | Check | How | Evidence location | Tag |
|---|---|---|---|---|
| CG-1 | Executes only in sandbox full copy (OD-03a); harness refuses otherwise | E-CO-NOT-SANDBOX | run log | [Verified Fact] OD-03a |
| CG-2 | CT-01..CT-16 green on **unmodified** legacy vs Stage 7 goldens (from INC-01 onward) | INC-01 harness | `docs/15-*/evidence/` | [Inference] |
| CG-3 | Mutation gate M1..M15 all killed (CT-H6) | `mutation_probe.sh` port | same | [Verified Fact] Stage 7: 14/14 replay kills, M11 to add |
| CG-4 | Legacy paths unchanged: `git diff --stat baseline-as-found..HEAD -- app legacy_batch legacy_java legacy_js sql contracts integration services scripts ops tests/test_*.py data` empty | TST-CO-05 | PR description | [Inference] |
| CG-5 | Backup intact: `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0 before and after | shell | log | [Verified Fact] OD-03a |
| CG-6 | Determinism: two consecutive runs byte-identical (after CT-H3) | harness | log | [Verified Fact] Stage 7 did 2 runs |
| CG-7 | No new dependency / egress (HAR-08); No-AI guard green from INC-02 (TST-CO-11/12) | deny-list | log | [Verified Fact] OD-08 |
| CG-8 | All tests assigned to this increment in `increment-test-map.csv` are executed and pass; class-B tests pass in **both** modes | unittest | evidence | [Inference] |
| CG-9 | Behaviour-diff register (TG-4) has 0 UNEXPLAINED rows | `hub golden-compare` (from INC-02) | evidence | [Inference] |
| CG-10 | Rollback for this increment described in PR and (INC-03+) rehearsed | rollback-strategy RB-1 | PR | [Inference] |
| CG-11 | `git status --porcelain` clean apart from the increment's paths; no DB/lake committed (HAR-09) | shell | PR | [Verified Fact] WB/HAR-09 |

### TG-3 Per-increment gates
Test counts are from `evidence/increment-test-map-summary.txt` (A = executable now, B = decision-dependent, C = sandbox proxy only).
| Inc | Branch | Scope (no legacy change in any row) | Entry criteria (beyond previous INC merged) | Tests that must pass | Exit evidence | Rollback |
|---|---|---|---|---|---|---|
| INC-01 | `stage-15-inc01-characterization-harness` | `tests/characterization/`: FX-BASE125 hash-gated fixture, subprocess runner, CT-H3 normaliser, reviewed `--update-golden`, CT-01..CT-16 (+CT-17/18 recorded NOT-RUN), M1..M15 gate, `ac_links` metadata for CT-04..CT-16 (C3), sandbox guard | TG-1(a) E-1..E-4, E-6 | CT-01..CT-16 green on untouched code; M1..M15 killed (15/15); 2 identical runs; the 7 shipped `tests/test_*.py` still run (sandbox) with as-found results | Stage 7 equivalence report (new capture == golden_run1 after normalisation) | L1 revert (only new files) |
| INC-02 | `stage-15-inc02-hub-skeleton-guards` | `hub/` skeleton, runtime self-check, sandbox guard, No-AI deny-list/egress test, RO adapters AD-01/02/08, deviation register (DV-01..09 `proposed`), `hub golden-compare`, M000 | E-5, E-2b, OD-S12-12 | 10 tests: TST-CO-01, -02, -04, -05, -06, -07, -11, -12, -13, -14 (B: OD-S12-12) | golden-compare lists DV rows as UNAPPROVED, exit ≠ 0 as specified (AC-CO-01) | L1 |
| INC-03 | `stage-15-inc03-store-audit` | migration runner M000/M001, C2 users/roles/audit chain, `verify-audit`, backup/restore tooling | OD-S12-09, OD-S12-18, A-14-08 | 16 tests: TST-SEC (service/static/db level) + TST-CO-10, -15 (B: OD-S12-09) | G3 verify-audit ok; G7 restore checksum match | L1 + L2 |
| INC-04 | `stage-15-inc04-policy-rules` | C4, AD-06, as-found rule sets (not active), DV-06 marker, M002 | OD-S12-04, A-14-07 | 25 tests: TST-POL-* + TST-CO-03 (B: OD-S12-04, -13) | CT-01..03 zero diff via as-found sets | L1 + L2 rebuild |
| INC-05 | `stage-15-inc05-decision-crosswalk` | C3 events/projection/as-of/closure check, C7 crosswalk, DM-1 backfill (125), M003 | OD-S12-03, -07, -15, -16, -19 | 39 tests: TST-DEC-* + TST-ID-* (non-API) (B: OD-S12-03/07/15/16) | G4 verify-projection 0; 125 imported; CT-02 distribution 36/70/17/2 reproduced | L1 + L2 rebuild |
| INC-06 | `stage-15-inc06-intake-shadow` | C6 raw store/classify/quarantine, AD-03/04/05, DM-3/DM-4, M004 | OD-S12-17, OD-S12-11 | 28 tests: TST-INT-* (non-API) + TST-CO-09 (B: OD-S12-11/13/17; C: 1) | G2 replay-safety; 8,567 in = sum of outcomes; 67 REPLAY → NOOP_DUPLICATE | L1 + L2 rebuild |
| INC-07 | `stage-15-inc07-runs-metrics` | C8 CLI jobs/run records (schedule off), C9 metrics with definition tags, M005 | OD-S12-10, OD-S12-01/02/08 accepted-open | 39 tests: TST-RUN-*, TST-MET-*, TST-OBS-* (B: OD-S12-10/12; C: 1) | no run without operator trigger; verdict `not_available_no_adopted_policy` | L1 + L2 |
| INC-08 | `stage-15-inc08-http-reviewer-gate` | C1 loopback HTTP + pages ("SHADOW" banner), C10 queue (R1), C5 gate mode `none` | OD-S12-05/-06 accepted-open | 64 tests: TST-GATE-*, TST-REV-* (R1), TST-NFR-*, all API-level tests, TST-CO-08 (B: OD-S12-05/06/12; C: 4) | G1..G10 all green = R1 build complete → Stage 16 | `hub.kill`, L1 |
| INC-09 | `stage-1x-inc09-r2-search` (after R1 release) | FTS5 search + templates | OD-S12-14, OD-S12-12 (FTS5) | 20 tests (R2-only reqs; C: 3) | — | `search.fts=off`, L1 |
Total = 10+16+25+39+28+39+64+20 = **241** [Verified Fact: script output].

### TG-4 Stage 16 behaviour comparison protocol ("every behaviour difference must be explained")
**Baseline (frozen):** Stage 7 goldens `docs/07-repo-assessment/evidence/golden/{api,batch,lib}_golden_run1.json`, dataset FX-BASE125 (`data/legacy.sqlite3` sha256 c254649f…d70aa, OD-09), tag `baseline-as-found`, mutation results M1..M15. Goldens are never edited in place; a re-capture is a new versioned file via the reviewed `--update-golden` PR (CT-H4).
**Runs (sandbox, at Stage 15 final HEAD and at every increment):** (1) legacy capture through the INC-01 harness; (2) `hub golden-compare` of hub outputs vs goldens; (3) mutation gate; (4) a second identical run for determinism.
**Classification — every difference gets exactly one class:**
| Class | Meaning | Allowed? |
|---|---|---|
| D0 IDENTICAL | equal after normalisation | yes |
| D1 NORMALISED | field on the CT-H3 list (ports, absolute sandbox paths, `received_at`, `last_sync`) | yes; list changes only by reviewed PR |
| D2 KNOWN-NON-REPRODUCIBLE | scenario documented by Stage 7 as non-reproducible (partner-feed regeneration, CT-14) | yes, only for those scenarios |
| D3 APPROVED-DEVIATION | matches a DV row with `status=approved` and non-empty `approval_ref` (HAR-06) | yes |
| D4 PROPOSED-DEVIATION | matches a DV row exactly (golden_ref, legacy value, new value) but not approved | yes in **hub shadow output only**; blocks the related CUT step |
| D5 UNEXPLAINED | anything else — **including any difference in legacy capture**, since legacy code is unchanged | **no**: STOP-12; increment/PR cannot merge |
**"Explained" means, concretely,** a row in the Stage 16 behaviour-diff register with all of: diff_id; scenario + golden JSON path (CT-xx); legacy value; new value; class D0–D5; cause (commit SHA / PR / increment, or environment factor proven by re-run); linked DV-xx and/or planned test ID; approval_ref or "none"; reproduce command; evidence file sha256. Numeric differences carry the recomputation (e.g. DV-01: 742,956.61 legacy vs 622,826.44 hub = join fan-out, with the SQL that shows it). Pass condition: **D5 = 0**; D3/D4 counts reported; every D4 listed against the CUT step it blocks. An environment-caused legacy diff (e.g. interpreter version) is not "explained" by assertion: it needs a reproduced A/B run and a reviewed normalisation change.

### TG-5 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| GF-1 | INC-01 needs no OD-S12, DV, PRD or runtime decision | TG-1(a); test map (no TST in INC-01) | Stage 15 can start with 5 lightweight confirmations | Low | High | Dinesh may want more upfront |
| GF-2 | 35 class-B tests are spread over INC-02..INC-08 (1/1/4/10/5/4/10) | summary.txt | decisions can be taken just-in-time | Medium (rework if a decision flips) | High | U-13-13 |
| GF-3 | 9 class-C tests can only produce sandbox proxies | summary.txt (C counts) | some NFR evidence is weak | Medium | High | Stage 26/31 |
| GF-4 | CT-17 (concurrency) and CT-18 (docker, HAR-05) not executable in INC-01 | CT plan P3 | recorded NOT-RUN | Low | High | — |

## Evidence References
`evidence/increment-test-map.csv`, `evidence/increment-test-map-summary.txt`, `evidence/increment_map.py`; Stage 13 tests_plan.csv/rtm.csv; RD-3; F10-2/F10-3; CT plan; goldens.

## Assumptions
- A-14-12 [Assumption] Prefix-based assignment of tests to increments (with dependency/API/R2 overrides) is adequate; Stage 15 may move individual tests with a note. Confirm at each PR review.

## Unknowns
- U-14-10 Whether the 3.12 parity run (CT-H5) can be performed anywhere (no 3.12 on device; network installs need HAR-08).

## Unresolved Issues
- E-1..E-6 and TG-1(b) items are OPEN — none are invented as approved.

## Residual Risks
- RR-TG-1 Gate fatigue with a single reviewer; mitigated by machine-checkable CG-1..CG-11.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | Initial gates, entry checklist and Stage 16 protocol (Stage 14). |
