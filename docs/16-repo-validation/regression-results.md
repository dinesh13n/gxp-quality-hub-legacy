---
stage: "16 — Validate the Good Repo"
artifact: "regression-results.md"
version: "v0.1"
date: "2026-10-20"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/16-repo-validation/evidence/cloud-regression.log", "docs/16-repo-validation/evidence/char-run2_report.json, char-mut1..4_report.json (laptop)", "docs/16-repo-validation/evidence/char-cloud-py313_report.json", "docs/15-modernization/evidence/inc01/final-A_report.json, inc02..inc04 char-regression reports (prior digests)", "docs/15-modernization/test-execution-log.md (INC-09 final session counts)", "git diff --name-status baseline-as-found main", "../_data-backup-2026-10-17/SHA256SUMS.txt", ".fde/orchestrator-decisions.md OD-23"]
supersedes: "none"
---
**Label: synthetic data, unvalidated - method validation only.**

## Summary
**No regression.** At `main` 2c63b07 (laptop working tree = cloud clone, both `2c63b07`):
- Legacy estate (Stage 7 baseline, reference runtime Python 3.10.12 on the laptop): characterisation harness **OVERALL PASS, 134/134 checks** in 6 independent runs; capture digests byte-identical to INC-01..INC-04 evidence; shipped `tests/test_*.py` ran 15, OK, post-run DB sha `750336f3…` equals Stage 7 R1; mutation gate **15/15 KILLED**.
- Hub suite (cloud workspace per OD-23, Python 3.13.16 / SQLite 3.45.1): **393 passed, 1 skipped, 0 failed, 0 errors** across the 10 orchestrator groups, every count equal to the expected Stage 15 close-out figures; plus **TST-CO-03 3/3**, which the orchestrator regression script does not select (finding RG-03).
- Legacy paths: all **688** file changes since tag `baseline-as-found` are additions (status `A`); no legacy file is modified or deleted; no `data/` file or `*.sqlite3` is tracked.
- Data checksums: `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` **rc 0** on the laptop before the first and after the last run; rc 0 before/after in the cloud.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
[Verified Fact] Commit identity: Stage 16 started when `main` was `6a4472d`; during the stage the orchestrator reset `main` on both the laptop and the cloud clone to `origin/main` `2c63b07` (reflog `reset: moving to refs/remotes/origin/main`). Both commits have the same parent `ad5514f` and the **same tree `0d2e5c73b64f…`** (`git diff --quiet 6a4472d 2c63b07` = no difference), so every result here applies to `2c63b07` unchanged.

### R-1 Hub regression (cloud, OD-23)
| Group | Selector (`run_hub_tests.py -k`) | Expected (Stage 15 close-out) | Observed | Wall s | Tag |
|---|---|---|---|---|---|
| A | TST_SEC, TST_CO_10, TST_CO_15, INC03 | 45 | ok 45 | 27 | [Verified Fact] |
| B | TST_CO_01/02/04/05/06/07/11/13/14, INC02 | 40 + 1 skip | ok 40, skipped 1 (no python3.9, DEV-12) | 9 | [Verified Fact] |
| C | TST_CO_12 (inner egress-guarded suite) | 5 | ok 5 | 39 | [Verified Fact] |
| I45 | INC04, TST_POL, TST_DEC, TST_ID, INC05, E05EGRESS | 88 | ok 88 | 23 | [Verified Fact] |
| I6 | TST_INT, TST_CO_09, INC06, E06EGRESS | 43 | ok 43 | 55 | [Verified Fact] |
| I7 | TST_RUN, TST_MET, TST_OBS, INC07, E07EGRESS | 59 | ok 59 | 37 | [Verified Fact] |
| I8 | TST_GATE, TST_REV, TST_CO_08, TST_NFR, I8_, INC08_S | 78 | ok 78 | 40 | [Verified Fact] |
| E8 | E08EGRESS | 1 | ok 1 | 41 | [Verified Fact] |
| I9 | I9_, INC09_S | 33 | ok 33 | 16 | [Verified Fact] |
| E9 | E09EGRESS | 1 | ok 1 | 15 | [Verified Fact] |
| (extra) | TST_CO_03 | not in the script | ok 3 | 5 | [Verified Fact] |
| **Total** | | | **396 ok + 1 skipped = 397 = every test method in `tests/hub/test_*.py` (static count)** | | [Verified Fact] |

### R-2 Legacy characterisation (laptop, reference runtime)
| Run | Command (sandbox `~/fde_sbx/s16-*`, deleted after) | CT checks | Mutants | Digests vs INC-01 | Tag |
|---|---|---|---|---|---|
| 1 | `run_characterization.py --sandbox-root ~/fde_sbx/s16-h` | 134/134, CT-17/18 NOT-RUN (by design) | — | report not kept (sandbox deleted; console output only) | [Verified Fact] |
| 2 | `… --label s16-run2` | 134/134; shipped suite 15 OK, R1 equal | — | identical | [Verified Fact] |
| 3-6 | `… --mutation-gate --mutants M1-M5 / M6-M9 / M10-M13 / M14,M15 --no-legacy-suite` | 134/134 each | 5+4+4+2 = **15/15 KILLED** | identical | [Verified Fact] |
Digests (all runs): api `c6db0a43…cd13`, batch `40237661…136f`, lib `c5797c3b…389d`, supplement `c3cbab2c…6d25` = INC-01 `final-A`, INC-02, INC-03, INC-04 reports. Determinism condition of TG-4 step 4 met (5 kept reports identical).

### R-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Open question |
|---|---|---|---|---|---|---|
| RG-01 | No regression in legacy behaviour or hub tests at 2c63b07 | R-1, R-2 | Stage 15 build is behaviour-preserving | Low | High | — |
| RG-02 | The cloud harness run is FAIL (124/134) for environmental reasons only (ENV-1..6 in behavior-difference-report) | `evidence/char-cloud-py313_report.json` | cloud cannot be a harness baseline (as OD-23 states) | Medium (runtime upgrade changes legacy outputs) | High | OD-S12-12 runtime target |
| RG-03 | `full_regression.sh` (orchestrator) has no selector for **TST-CO-03** (golden parity of the as-found rule sets); the 10 groups run 394 of 397 methods | static enumeration of `tests/hub/test_*.py` vs the selectors; separate run 3/3 | the key rule-parity test could silently stop running | Medium | High | add `-k TST_CO_03` to group I45 or a new group |
| RG-04 | `report.json` counts can overstate passes for subTest failures (RTD-28); Stage 16 relied on `unittest_rc` + counts, both green | runner design | low for this run | Low | Medium | fix with the next runner change |
| RG-05 | CI still runs only the shipped `tests/` (workflow unchanged); none of the above runs on a PR | `.github/workflows/` unchanged since baseline | regressions are caught only by manual runs | High (process) | High | RTD-01/02/14, Stage 27 |

## Evidence References
- Cloud command: `EXTRA_GROUPS='run I9 -k I9_ -k INC09_S; run E9 -k E09EGRESS' bash full_regression.sh /home/claude/gxp-quality-hub-legacy` (orchestrator scratchpad script; log copied to `evidence/cloud-regression.log`); `python3 -B tests/hub/run_hub_tests.py --sandbox-root /home/claude/sbx/P3 --label P3 -k TST_CO_03`.
- Laptop commands as in R-2; checksum log in `evidence/checksum-log.txt`.

## Assumptions
- A-16-RG-1 [Assumption] Hub test results on Python 3.13 / SQLite 3.45 (cloud) stand for the reference runtime, as OD-23 accepts; hub tests were not re-run on 3.10.12 in Stage 16 (they were green there at INC-09). Confirm: Engagement lead (Dinesh Naik) - already accepted in OD-23.

## Unknowns
- U-16-RG-1 Results on the eventual target runtime (OD-S12-12) - Stage 27.

## Unresolved Issues
- RG-03 selector gap; RG-05 CI wiring.

## Residual Risks
- RR-RG-1 Manual-only regression (no CI) - High until Stage 27.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-20 | claude-fde-agent | First issue. |
