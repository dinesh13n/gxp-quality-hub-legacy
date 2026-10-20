---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "behavior-preservation-evidence.md"
version: "v0.4"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; INC-03 (hub DB migrations M001, C2 access & audit chain, backup/restore, first rollback rehearsal) added in v0.3. Stage 15 overall status: IN PROGRESS. INC-04 (policy & rule service: M002, as-found rule sets inactive, activation with a recorded human decision) added in v0.4."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)", "docs/15-modernization/evidence/inc03/", "docs/15-modernization/rollback-rehearsal-inc03.md", "hub/", "tests/hub/", ".fde/orchestrator-decisions.md (OD-15)"]
supersedes: "v0.3 (INC-01 .. INC-03)"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
INC-01 changes no legacy behaviour (only new files). This file records the evidence that (a) the untouched legacy code still reproduces every Stage 7 golden, (b) the harness is deterministic, (c) the harness actually detects behaviour change (mutation gate), and (d) the working-tree data were never touched. **Result: D5 UNEXPLAINED = 0; 134/134 checks green in two consecutive runs; 15/15 mutants killed; checksum rc 0 after every session.**

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### BP-1 CT results on unmodified legacy (runs `final-A`, `final-B`, HEAD ed43a0a, Python 3.10.12, SQLite 3.37.2, OpenJDK 11.0.32.1, Node v22.23.2)
| CT | Workflow | Checks | Golden source | Result A / B | Tag |
|---|---|---|---|---|---|
| CT-01 | CW-01 priority truth table (120) | 1 | stage7 batch | PASS / PASS | [Verified Fact] |
| CT-02 | CW-01 125-case priorities, 36/70/17/2 | 3 | stage7 api + invariant | PASS / PASS | [Verified Fact] |
| CT-03 | CW-01/02 manual review (20 + 6 sampled cases + meta) | 7 | stage7 batch/api | PASS / PASS | [Verified Fact] |
| CT-04 | CW-02/10/13 HTTP responses | 35 | stage7 api | PASS / PASS | [Verified Fact] |
| CT-05 | CW-03/11 baseline + operational report (125 and 6000/4326) | 5 | stage7 batch | PASS / PASS | [Verified Fact] |
| CT-06 | CW-04 gateway responses | 16 | stage7 api | PASS / PASS | [Verified Fact] |
| CT-07 | CW-04 bridge sequence + library edge cases | 8 | stage7 batch + lib | PASS / PASS | [Verified Fact] |
| CT-08 | CW-05 reconcile sequence | 4 | stage7 batch | PASS / PASS | [Verified Fact] |
| CT-09 | CW-06 vendor import | 4 | stage7 batch | PASS / PASS | [Verified Fact] |
| CT-10 | CW-07 night shift | 3 | stage7 batch | PASS / PASS | [Verified Fact] |
| CT-11 | CW-08 Java totals | 5 | stage7 batch | PASS / PASS | [Verified Fact] |
| CT-12 | CW-08 SQL report (742,956.61 vs 622,826.44) + `sql/legacy_reports.sql` itself | 8 | stage7 batch + INC-01 supplement | PASS / PASS | [Verified Fact] |
| CT-13 | CW-09 JS policy | 3 | stage7 batch | PASS / PASS | [Verified Fact] |
| CT-14 | CW-12 regeneration equivalence | 18 | stage7 batch | PASS / PASS | [Verified Fact] |
| CT-15 | CW-12 readiness scripts | 5 | stage7 batch + R7 log | PASS / PASS | [Verified Fact] |
| CT-16 | CW-14 boundary (501 everywhere, only `app/generate.py` writes `cases`, no disposition handler) | 9 | stage7 api + INC-01 supplement | PASS / PASS | [Verified Fact] |
| CT-17 | concurrency | — | none | NOT-RUN (no golden, U-07-05) | [Verified Fact] |
| CT-18 | docker | — | none | NOT-RUN (HAR-05) | [Verified Fact] |
Total 134 checks: 127 against Stage 7 goldens/logs, 7 against the INC-01 supplement golden v1 (captured on the unmodified code; see `refactoring-decisions.md` RD-04).

### BP-2 Behaviour-difference classification (Stage 14 TG-4)
| Class | Count | Detail | Tag |
|---|---|---|---|
| D0 IDENTICAL | 132 | equal without any normalisation (the API capture is byte-identical to `api_golden_run1.json`, sha256 c6db0a43…) | [Verified Fact] |
| D1 NORMALISED | 2 | `batch:generate_documents_regen` (N1 sandbox path in stdout); `batch:node_cwd_other` (N1 path + N4 tail window: 724 common trailing characters compared, incl. the ENOENT error and Node version) | [Verified Fact] |
| D2 KNOWN-NON-REPRODUCIBLE | 0 | partner-feed regeneration differs from shipped exactly as the golden records (`partner_regen_equals_shipped` all false) → compared as D0 | [Verified Fact] |
| D3 / D4 | 0 | no deviation rows used (DV-01..09 remain `proposed`, not needed for INC-01) | [Verified Fact] |
| **D5 UNEXPLAINED** | **0** | | [Verified Fact] |
N2 (python path) and N3 (JVM `JAVA_TOOL_OPTIONS` banner) were not exercised on this device (same interpreter path, same banner as Stage 7); they exist for other environments. [Verified Fact]

### BP-3 Determinism (CG-6)
[Verified Fact] `final-A` and `final-B` produce identical canonical capture digests (api c6db0a43…, batch 40237661…, lib c5797c3b…, supplement c3cbab2c…) and identical per-check results; the same digests were also obtained in `run-1`, `golden-supp`, `det-run-A`, `det-run-B` (6 runs). Raw batch bytes differ between runs only by the sandbox path (label) embedded in two fields — removed by N1/N4.

### BP-4 Mutation gate (CT-H6, CG-3): 15/15 KILLED
| Mutant | Change | Killed by |
|---|---|---|
| M1 | urgent threshold 50000→1 | CT-01, CT-02, CT-04, CT-05 |
| M2 | 'review' tier removed | CT-01, CT-02, CT-04 |
| M3 | manual_review_required always False | CT-03, CT-04 |
| M4 | CLOSED no longer archived | CT-01, CT-02, CT-04, CT-05 |
| M5 | negative-quantity rejection removed | CT-08 |
| M6 | replay duplicate detection removed | CT-08 |
| M7 | schema/key validation removed | CT-08 |
| M8 | night-shift comparison inverted | CT-10 |
| M9 | unknown business_key accepted | CT-07 (library golden) |
| M10 | API manual_review flag False | CT-03, CT-04 |
| M11 | partners pagination ignores limit/offset | CT-04 |
| M12 | baseline urgent_cases 0 | CT-05 |
| M13 | JS tolerance 5%→50% | CT-13 |
| M14 | idempotent import removed | CT-09 |
| M15 | gateway timeout 503→200 | CT-06 |
[Verified Fact] Compared with Stage 7: shipped suite kills 1/15 (M4); Stage 7 golden replay killed 14/14 (M11 not replayed). INC-01 adds M11 and kills all 15. Every mutant was killed by a CT comparison, none merely by a crashing capture.

### BP-5 Shipped tests still as-found (TG-3 INC-01 exit criterion)
[Verified Fact] In a fresh sandbox copy `python -m unittest discover -s tests -v` runs the same 15 tests, result OK, and leaves `legacy.sqlite3` with sha256 750336f3… — identical to Stage 7 R1 (`golden/stage7/R1_unittest_fresh.log`). The new directory has no `__init__.py`, so discovery is unchanged (Ran 15, not more).

### BP-6 Legacy paths and data untouched
- [Verified Fact] `git diff --name-status main..HEAD | grep -v '^A'` is empty (only added files); `git diff --stat baseline-as-found..HEAD -- app legacy_batch legacy_java legacy_js sql contracts integration services scripts ops tests/test_*.py data` is empty (CG-4, AC-CO-05).
- [Verified Fact] `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0 before the first and after every execution session (12 checks, `evidence/inc01/checksum-log.txt`) (CG-5, AC-CO-07).
- [Verified Fact] Guard tests: sandbox roots inside the repo, inside `data/`, at the repo parent, `~/mnt`, `/`, and inside the backup were refused with E-CO-NOT-SANDBOX (rc 2) (AC-CO-06); a fixture with one changed byte was refused with E-FX-HASH (rc 2) (CT-H1).

### BP-7 Stage 13 condition C3 — acceptance links for CT-04..CT-16
Each CT carries `ac_links` in `tests/characterization/catalogue.json`: existing FR-CO-01, BEH-CO-01, AC-CO-01, AC-CO-02, AC-CO-05, AC-CO-07, the CT-specific FR(s) below, and one **proposed** AC (given/when/then in the catalogue).
| CT | Proposed AC | CT-specific FR | DV rows |
|---|---|---|---|
| CT-04 | AC-CO-L04 | FR-SEC-01 | — |
| CT-05 | AC-CO-L05 | FR-MET-06 | — |
| CT-06 | AC-CO-L06 | FR-INT-04 | DV-09 |
| CT-07 | AC-CO-L07 | FR-INT-02, FR-INT-05 | DV-09 |
| CT-08 | AC-CO-L08 | FR-INT-01, FR-INT-02, FR-RUN-03 | DV-02, DV-03, DV-07 |
| CT-09 | AC-CO-L09 | FR-INT-02 | — |
| CT-10 | AC-CO-L10 | FR-RUN-03, FR-MET-04 | DV-08 |
| CT-11 | AC-CO-L11 | FR-MET-04 | DV-04 |
| CT-12 | AC-CO-L12 | FR-MET-04 | DV-01 |
| CT-13 | AC-CO-L13 | FR-POL-04, FR-POL-06 | DV-05, DV-06 |
| CT-14 | AC-CO-L14 | — | — |
| CT-15 | AC-CO-L15 | FR-CO-03 | — |
| CT-16 | AC-CO-L16 | FR-GATE-01 | — |
[Inference] C3 is met at the test-metadata level; formal adoption of AC-CO-L04..L16 into `docs/12-specs/acceptance-criteria.md` needs a Stage 12/13 addendum (not done here; that file is not edited in place).

### BP-8 INC-02 - legacy behaviour unchanged (code at `23b3250`)
| Check | Result | Evidence | Tag |
|---|---|---|---|
| INC-01 harness regression (`run_characterization.py`, label `inc02-regress`) | 134/134 checks, CT-01..CT-16 PASS, shipped suite ran=15 OK as-found (post-DB sha 750336f3… = Stage 7 R1), **0 differences** | `evidence/inc02/char-regression-inc02_report.json` | [Verified Fact] |
| Capture digests vs INC-01 `final-A` | identical (api c6db0a43…, batch 40237661…, lib c5797c3b…, supplement c3cbab2c…) | same file, `capture_digests_equal_inc01_final_A: true` | [Verified Fact] |
| Mutation gate (3 chunks `inc02-mut-1..3`) | 15/15 KILLED | `evidence/inc02/mutation-gate-inc02.txt` | [Verified Fact] |
| Legacy source paths vs tag `baseline-as-found` | `git diff` empty; no untracked files (TST-CO-05 a/b) | hub final-A/B reports | [Verified Fact] |
| Branch vs `main` | every change is an added file except Stage 15's own docs (TST-CO-05 c) | `git diff --name-status main..HEAD` | [Verified Fact] |
| Working-tree data | backup manifest `sha256sum -c --quiet` rc 0 before/after every execution (1,512 entries) | `evidence/inc02/checksum-log.txt` | [Verified Fact] |
| Hub access to legacy stores | only per-run snapshot copies of the sandbox FX-BASE125 copy, opened `mode=ro&immutable=1` + authorizer; 13 write forms refused; source and snapshot sha256 unchanged (TST-CO-04) | `hub/adapters/legacy_sqlite.py`; TST-CO-04 | [Verified Fact] |

### BP-9 INC-02 golden-compare on FX-BASE125 (new side vs legacy goldens)
[Verified Fact] `python -m hub golden-compare` on the 125-case baseline: 11 probes, **2 identical** (CT-12 `true_total_amount` 622,826.44; CT-10 active policies per region), **9 UNAPPROVED** = DV-01..DV-09 (all `proposed`), 0 NOT-RUN, exit 6 (E-CO-UNAPPROVED-DEVIATION) - exactly the AC-CO-01 expectation. DV-01 is computed live: legacy 742,956.61 vs new 622,826.44; DV-08 live: 118 vs 500 distinct entities in the first 500. These are differences between legacy and the *proposed new behaviour*; no legacy behaviour changed. Evidence: `evidence/inc02/golden-compare-baseline.{json,txt}`.
[Verified Fact] With matching approved register rows (throw-away test fixture, not a HAR-06 approval) the exit is 0 (TST-CO-01 c); an approval whose values do not match the observation does not cover it (TST-CO-01 d); an unlisted golden change is UNAPPROVED (TST-CO-02).
[Verified Fact] Determinism: golden-compare and deviation-register output byte-identical across 18 environments (PYTHONHASHSEED 0/1/random x TZ UTC/Asia/Kolkata/America/Los_Angeles x LC_ALL C/en_IN.UTF-8) (TST-CO-13).

### BP-INC03 INC-03 behaviour preservation
| Check | Result | Evidence | Tag |
|---|---|---|---|
| Legacy source paths unchanged vs `baseline-as-found`; branch adds files only (except Stage 15 docs) | TST-CO-05 a/b/c ok | `evidence/inc03/hub-final-B_report.json` | [Verified Fact] |
| INC-01 characterisation harness | 134/134 PASS, shipped 15 tests OK as-found (post-DB 750336f3…), `capture_digests` identical to INC-02 regression | `evidence/inc03/char-regression-inc03_report.json` | [Verified Fact] |
| Mutation gate | 15/15 KILLED (4 chunks) | `evidence/inc03/mutation-gate-inc03.txt` | [Verified Fact] |
| INC-02 hub behaviour (golden-compare, adapters, guards, register, runtime floor, determinism) | 46 methods: 45 ok, 1 skipped (same as INC-02 final-A/B) | `hub-final-B_report.json`, `hub-final-C_report.json` | [Verified Fact] |
| golden-compare still lists DV-01..09 UNAPPROVED, exit 6 (OD-15) | yes (TST-CO-01, and inside TST-CO-15) | final-A/B | [Verified Fact] |
| INC-02 `init` still creates an M000-only store (S03) and INC-02 commands work on an M001 store | yes (INC-02 S03; INC-03 S03; rehearsal step 8) | final-B, rehearsal transcript | [Verified Fact] |
| No-AI / egress | full suite under egress guard: 0 attempts, model_calls_total 0 | `hub-final-C_inner-egress-run.json` | [Verified Fact] |
| Working-tree data | backup manifest rc 0 after every session | `evidence/inc03/checksum-log.txt` | [Verified Fact] |
[Inference] INC-03 changes no legacy behaviour: it adds new modules only, the legacy goldens are unchanged and no approved-behaviour change was needed (`approved-behavior-changes.md` ABC-INC03).

### BP-INC04 INC-04 behaviour preservation (code HEAD `86f1a9a`, device Python 3.10.12, SQLite 3.37.2, Node v22.23.2)
| Check | Result | Evidence | Tag |
|---|---|---|---|
| as-found-python vs Stage 7 goldens CT-01 / CT-03 | 120 / 120 PRIORITY and 20 / 20 MANUAL_REVIEW outcomes equal (byte-equal JSON) | TST-POL-12, TST-POL-13, TST-CO-03 a | [Verified Fact] |
| as-found-js vs CT-13 | 32 / 32 thresholds, tolerance 26250 allowed / 26250.01 denied, 7 / 7 comparable allow cases equal; 'abc' and null excluded (DEV-30) | TST-POL-14, TST-CO-03 a | [Verified Fact] |
| as-found-batch vs `shift_reconciliation` golden | flagged_count 3 / 53 / 210 / 5454 for limits 50 / 100 / 500 / 12500 reproduced by evaluating the legacy LEFT JOIN rows one by one | TST-CO-03 b | [Verified Fact] |
| Rule sets vs the LEGACY CODE executed in the sandbox copy | python grid 5 statuses x 4 severities x 12 amounts = 240 cases and JS grid 5 regions x 9 years x 14 amounts = 630 cases (every x1.05 boundary incl. 26250.01, 28560.01, 1048948.96): 0 differences | TST-CO-03 c | [Verified Fact] |
| Documented deltas to legacy | partial-year prefix match (DEV-29), non-numeric / null amount (DEV-30); both are in new modules, pinned by tests, and need OD-S12-13 | TST-HUB-INC04-S05, TST-POL-23 | [Verified Fact] |
| Default values preserved AND marked | 999999 fallback -> `defaulted`, `NO_MATCH_REGION_YEAR`; PRIORITY `queue` with unknown status / severity -> `UNKNOWN_INPUT_VALUE`; known inputs reaching the last row -> `defaulted = false` | TST-POL-19, -20, -21 | [Verified Fact] |
| Nothing active ships | fresh store: 0 adopted policies, 0 active pointers; loading the 3 as-found sets leaves `active_ruleset` empty; evaluate without a ref -> E-POL-NO-ACTIVE-RULESET | TST-POL-01, -11, -16, S01 | [Verified Fact] |
| Activation needs a recorded human decision | refused (and audited `denied`) for none / malformed / unknown / non-decision / other function / other set / non-holder / consumed / broken-chain decisions | S02 (9 refusal cases) | [Verified Fact] |
| Rule evaluation is pure and deterministic | 1000 evaluations bit-identical in this process and two child processes (PYTHONHASHSEED 0, 12345); same result with open / socket / time / urandom / sqlite3 / subprocess patched to raise | TST-POL-22 | [Verified Fact] |
| Legacy paths and data | TST-CO-05 a/b/c ok; harness 134 / 134 PASS, shipped 15 tests OK as-found (post-DB `750336f3…` = Stage 7 R1), capture digests unchanged; backup manifest rc 0 before and after | `evidence/inc04/hub-final-B_report.json`, `char-regression-inc04_report.json`, `checksum-log.txt` | [Verified Fact] |
| INC-02 / INC-03 hub behaviour | A 45 ok; B 40 ok + 1 skipped (same as INC-03 final); golden-compare still lists DV-01..09 UNAPPROVED, exit 6 | `hub-final-A_report.json`, `hub-final-B_report.json` | [Verified Fact] |
| No-AI / egress | full suite (123 tests) under the egress guard: 0 attempts, `model_calls_total` 0; deny-list scan of hub/ + tests/hub clean (TST-CO-11 d) | `hub-final-C_inner-egress-run.json` | [Verified Fact] |
| Rollback (L2 restore + rebuild) | restore of the pre-M002 backup: no policy tables, audit chain verifies; re-apply M002 + seed + load -> identical rule-set content hashes | TST-HUB-INC04-S08 | [Verified Fact] |
| Mutation gate | 8 / 8 KILLED (engine `>` -> `>=`, decision check off, tolerance 1.00, overlap off, holder membership off, default marker off, authority check off, immutability trigger removed) | `evidence/inc04/mutation-gate-inc04.txt` | [Verified Fact] |
[Inference] INC-04 changes no legacy behaviour: it adds new modules only, legacy goldens are unchanged, and no approved-behaviour change was needed (`approved-behavior-changes.md` ABC-INC04). [Assumption] The python domain lists (statuses OPEN / UNDER_REVIEW / CLOSED / ESCALATED / REOPENED, severities LOW..CRITICAL) come from the shipped data and goldens (A-12-F03-2), not from the legacy code, which has no domain. Confirm: Engagement lead (Dinesh Naik).
[Inference] Exact Decimal arithmetic replaces IEEE doubles; 870 grid cases show no difference, but a difference at the last binary digit of a x1.05 boundary cannot be excluded for untested values (RTD-42).

### BP-INC07 INC-07 behaviour preservation (device Python 3.10.12, SQLite 3.37.2, Node v22.23.2)
| Check | Result | Evidence | Tag |
|---|---|---|---|
| Legacy code and data | `git diff --name-status main`: only `A` entries; data checksum manifest rc 0 before and after every run | `evidence/inc07/` | [Verified Fact] |
| Characterization harness | OVERALL PASS (CT-17/18 NOT-RUN as before); shipped tests/test_*.py 15 OK as-found, post-DB equals Stage 7 R1 | harness run `inc07-regress` | [Verified Fact] |
| Legacy month-end total vs hub | legacy join gives 742,956.61 (BB-08 fan-out); hub single-table total is 622826.44 for the same 125 cases; the difference is the documented defect, not an approved change | TST-MET-09, TST-MET-11 | [Verified Fact] |
| INC-02..06 groups | A 45 ok; B 40 ok + 1 skipped; C 5 ok; INC04+05 88 ok; INC06 43 ok | `test-execution-log.md` | [Verified Fact] |
[Inference] INC-07 changes no legacy behaviour: it adds new modules only.

### BP-INC09 INC-09 behaviour preservation (code `d3992d4`, device Python 3.10.12, SQLite 3.37.2)
- [Verified Fact] Legacy unchanged: `git diff --name-status main` shows no legacy path and no `data/` path; INC-01 harness OVERALL PASS (CT-01..CT-16, shipped tests as-found, post_db equals Stage 7 R1); backup checksum rc 0 before and after every run.
- [Verified Fact] Earlier increments unchanged: no earlier hub module edited (subclass / delegation only); all earlier groups green with unchanged counts (test-execution-log INC-09); TST-SEC-01 (route registry pinned to the OpenAPI) green, so the R2 handlers use the frozen routes and roles.
- [Verified Fact] R1 hub behaviour unchanged: `WebApp` (R1) still answers 501 for the five R2 operations; only `R2WebApp` serves them. Search stays disabled by default, FTS off by default, drafts off by default.
- [Verified Fact] The corpus loader reads only the sandbox copy of `data/` (working tree refused, JSONL pinned) and writes only the hub store.

## Evidence References
- INC-03 evidence: `docs/15-modernization/evidence/inc03/` (summary.txt, hub-final-{A,B,C} reports, char-regression-inc03_report.json, mutation-gate-inc03.txt, checksum-log.txt, rollback-rehearsal-1/); `docs/15-modernization/rollback-rehearsal-inc03.md`; commits `git log --oneline main..stage-15-inc03-hub-db-audit`.
- `docs/15-modernization/evidence/inc01/final-A_report.json`, `final-B_report.json` (full per-check results + unittest output), `mut-1..mut-4_report.json`, `summary.txt`, `checksum-log.txt`.
- `tests/characterization/golden/MANIFEST.sha256` (golden integrity), `fixtures/FX-BASE125.sha256`.
- INC-02: `docs/15-modernization/evidence/inc02/`; `tests/hub/`; `hub/golden/probes_inc02.json`; `hub/coexistence/seed_inc02.json`.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).
- A-15-02 [Assumption] Self-review of the supplement golden v1 by the authoring agent is provisional; the PR review (OD-13) is the real review.

## Unknowns
- U-15-02 Behaviour on Python 3.12 / other JDK/Node versions (CT-H5) — not measurable on this device.
- INC-02: behaviour of the declared DV targets once real modules exist (U-15-02).

## Unresolved Issues
- AC-CO-L04..L16 not yet adopted into Stage 12 specs (GAP-13-06 partially closed).

## Residual Risks
- RR-BP-1 N4 compares tail-truncated stderr on the common suffix; a change confined to the clipped start of such a tail would not be detected (affects 1 check, `node_cwd_other`).
- RR-BP-2 Goldens depend on the git-ignored baseline data; protection is the FX-BASE125 hash gate + backup manifest.
- INC-02: 7 of 9 DV new-side values are declared, not computed (DEV-08); BP-9 proves the comparison machinery and register discipline, not the future modules.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
| v0.3 | 2026-10-18 | claude-fde-agent | INC-03 (branch `stage-15-inc03-hub-db-audit`): sections added; earlier content unchanged. |
| v0.4 | 2026-10-18 | claude-fde-agent | INC-04 (branch `stage-15-inc04-rule-service`): sections added; earlier content unchanged. |
| v0.5 | 2026-10-19 | claude-fde-agent | INC-07 (branch `stage-15-inc07-runs-metrics`): sections added; earlier content unchanged. |
| v0.9 | 2026-10-20 | claude-fde-agent | INC-09 (branch `stage-15-inc09-search-corpus`): sections added; earlier content unchanged. |
