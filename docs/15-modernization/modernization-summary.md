---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "modernization-summary.md"
version: "v0.4"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
scope: "INC-01 (characterisation harness + hermetic fixtures + mutation gate) and INC-02 (hub/ skeleton, sandbox / No-AI / runtime guards, read-only adapters, deviation register, golden-compare). Later increments extend this file; INC-03 (hub DB migrations M001, C2 access & audit chain, backup/restore, first rollback rehearsal) added in v0.3. Stage 15 overall status: IN PROGRESS. INC-04 (policy & rule service: M002, as-found rule sets inactive, activation with a recorded human decision) added in v0.4."
evidence_sources: ["tests/characterization/", "docs/15-modernization/evidence/inc01/", "docs/14-transformation/transformation-backlog.md", "docs/14-transformation/transformation-gates.md", "docs/07-repo-assessment/characterization-test-plan.md", "docs/07-repo-assessment/evidence/golden/", "docs/13-traceability/traceability-summary.md (C3)", ".fde/orchestrator-decisions.md (OD-03a, OD-08, OD-09, OD-11..OD-13)", "tests/hub/", "hub/", "docs/15-modernization/evidence/inc02/", "docs/12-specs/features/f10-coexistence-change-safety.md", "docs/10-architecture/adrs/ADR-002-no-ai-boundary-enforcement.md", "docs/14-transformation/evidence/increment-test-map.csv", ".fde/orchestrator-decisions.md (OD-12, OD-14)", "docs/15-modernization/evidence/inc03/", "docs/15-modernization/rollback-rehearsal-inc03.md", "hub/", "tests/hub/", ".fde/orchestrator-decisions.md (OD-15)"]
supersedes: "v0.3 (INC-01 .. INC-03)"
---
**Label: synthetic repository, unvalidated against any organisation.**

## Summary
**Stage 15 status: IN PROGRESS (INC-01 and INC-02 of 9 delivered).** INC-01 status: **DONE WITH CONDITIONS** — the executable characterisation harness, hermetic FX-BASE125 fixture gate and mutation gate exist on branch `stage-15-inc01-harness` as new files only; on the unmodified legacy code CT-01..CT-16 pass (134/134 checks) in two identical runs, the mutation gate kills 15/15 (the shipped suite kills 1/15), the shipped tests still give their as-found result, and working-tree data were verified intact after every session. Conditions: CI cannot yet run the harness (fixture git-ignored, workflow untouched), no 3.12 parity run, AC links for CT-04..CT-16 are proposed metadata awaiting a Stage 12/13 addendum.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
1. [Verified Fact] Stage 7 verdict "NO-GO for refactoring until an executable harness and hermetic fixtures exist" — the harness and fixtures now exist and are proven to detect all 15 reference behaviour changes.
2. [Verified Fact] Legacy behaviour reproduces exactly: 132/134 checks equal with no normalisation at all, 2 equal after path/tail normalisation (D1); D5 = 0.
3. [Verified Fact] CT-11 (Java) runs: JDK 11 is present on the device, contrary to the Stage 13 gap note (ACC-8).
4. [Verified Fact] New observations pinned for later increments: `sql/legacy_reports.sql` (unrounded floats) reproduces the Stage 7 report rows when rounded to 2 dp; every write method on every route of both services returns 501; only `app/generate.py` writes the `cases` table; no disposition/release/e-signature handler exists (HAR-12 guard baseline).
5. [Inference] TG-3 INC-01 gate: exit criteria met; CG-1..CG-11 relevant items met except CG-7's No-AI guard (INC-02 by plan) and the CI aspects (RTD-01/02).

### How to run (for CI / PR description)
```sh
# from the repository root; sandbox defaults to ~/fde_sbx/s15-inc01, fixture to ../_data-backup-2026-10-17
python3 -B tests/characterization/run_characterization.py --mutation-gate
sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt
```
Details: `tests/characterization/README.md` and `how-to-run-characterization-harness.md`.

### Next
Orchestrator: review + PR + squash-merge INC-01 (OD-13). INC-02 (`hub/` skeleton, guards, RO adapters, golden-compare) uses OD-12 defaults; decide RTD-01 (CI fixture provisioning) early.

### INC-02 (branch `stage-15-inc02-hub-skeleton`) - DONE WITH CONDITIONS
1. [Verified Fact] New `hub/` package (stdlib only, `python -m hub`) beside the legacy estate: runtime self-check (floor 3.10/3.37), sandbox guard (E-CO-NOT-SANDBOX), No-AI deny-list (E-CO-DENYLIST-IMPORT), loopback-only egress guard (E-CO-EGRESS-ATTEMPT), `Untrusted` type, `model_calls_total` / `egress_attempts_total` zero-tripwires, read-only adapters AD-01/AD-02/AD-08, M000 + deviation register (DV-01..DV-09 `proposed`), `golden-compare`.
2. [Verified Fact] The 10 planned INC-02 tests (TST-CO-01, -02, -04, -05, -06, -07, -11, -12, -13, -14) are executable and green in two sandbox runs (46 methods: 45 ok, 1 skipped - no python3.9 on device); 3 supplementary tests green.
3. [Verified Fact] golden-compare on FX-BASE125: 2 identical, 9 UNAPPROVED (DV-01..DV-09), exit 6 - as AC-CO-01 specifies while no deviation is approved.
4. [Verified Fact] Legacy behaviour preserved: INC-01 harness 134/134 with identical capture digests, mutation gate 15/15, shipped suite as-found, legacy paths unchanged, backup manifest rc 0 throughout.
5. [Verified Fact] Two hub defects and one deny-list gap were found by the new tests during development and fixed before the final runs (test-execution-log #15, #17).
6. Conditions: RTD-13 (Stage 12 addenda), RTD-14 (CI wiring), RTD-15 (declared probes), RTD-16, RTD-18, RTD-20 (DV decisions).

### How to run INC-02 tests
```sh
# from the repository root; sandbox defaults to ~/fde_sbx/s15-inc02, fixture to ../_data-backup-2026-10-17
python3 -B tests/hub/run_hub_tests.py                    # all INC-02 tests (~2 min)
python3 -B tests/hub/run_hub_tests.py -k TST_CO_04       # one test ID
python3 -B tests/characterization/run_characterization.py  # INC-01 regression gate
sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt
```

### Next (after INC-02)
Orchestrator: review + PR + squash-merge INC-02 (OD-13). INC-03 (audit trail, ADR-005) uses OD-12 defaults; STOP and ask Dinesh on OD-S12-17 before INC-06; Dinesh's OD-S12-13 decisions on DV-01..DV-09 needed before INC-04 merges (RTD-20).

### MS-INC03 INC-03 summary (branch `stage-15-inc03-hub-db-audit`) - DONE WITH CONDITIONS
- [Verified Fact] Delivered TB-09 (forward-only migration runner, M001, backup-before-migrate), TB-10 (C2: offline users/roles in the DB, PBKDF2 + lockout + hashed sessions, deny-by-default route authorisation + Zone H holder/re-auth check, hash-chained insert-only audit with config-path anchor, `verify-audit`, CONFIG_LOADED), TB-11 (backup/restore with manifest; release checklist G1-G10) and the first rollback rehearsal (PASS except the G2 clause, which cannot run yet).
- [Verified Fact] Tests: 16/16 planned INC-03 IDs green (40 methods) + 5 supplementary; INC-02 46 methods unchanged; INC-01 harness 134/134 with identical digests; mutation 15/15; backup manifest rc 0 after every session.
- [Verified Fact] Refactoring decision on users/roles: DB addendum (RD-24), holders in config (default []), permission matrix as data.
- Conditions: Stage 12 addenda (RTD-23/24); security values are proposals for Stage 24 (RTD-26); C2 parts outside INC-03 (RTD-27); G1/G2/G4/G8/G9/G10 not evaluable yet - every release checklist blocks (RTD-32); runner disk use (RTD-31) and subTest recording gap (RTD-28).
- Stage 15 overall: **IN PROGRESS** (INC-04..INC-09 not started; OD-S12-17 question to Dinesh is due before INC-06 per OD-12).

### MS-INC04 INC-04 summary (branch `stage-15-inc04-rule-service`) - DONE WITH CONDITIONS
- [Verified Fact] Delivered TB-12: policy objects (candidate / adopted / accepted-open, versioned, immutable), table-driven rule sets as data with a pure Decimal engine and the `defaulted` marker, AD-06 importer that loads the three as-found rule sets (Python priority > 50,000 + manual review; JS regional limit x1.05 with 999,999 fallback; night-shift 2,500-8,500 thresholds) as named, versioned, read-only, **inactive** candidates, clock verdicts (none without an adopted clock), and activation that is refused unless a human Zone H holder recorded a decision in the hash-chained audit trail. M002 and `python -m hub.policy`.
- [Verified Fact] Nothing ships adopted or active: a fresh store has 5 candidate policies and no active rule set; `zone_h.holders` is still empty, so nobody can adopt or activate until Dinesh names holders (OD-S12-06).
- [Verified Fact] Tests: 25/25 planned IDs green (29 methods) + 8 supplementary; INC-02 / INC-03 suites unchanged (A 45, B 40 + 1 skipped, C 5); harness 134/134; mutation 8/8 KILLED; legacy and `data/` byte-identical (checksum rc 0).
- [Verified Fact] Parity: 120 + 20 + 32 golden rows and 870 live legacy-vs-service grid cases (python, node in the sandbox) show no difference; the night-shift golden is reproduced for four limits.
- Conditions: DEV-29 / DEV-30 (OD-S12-13 preserve-or-fix, Dinesh), DEV-28 (M002 outside the main runner, RTD-37), DEV-35 (decision mechanism to confirm, RTD-43), Stage 12 addenda (RTD-38), not built: divergence report, withdrawal, HTTP routes (RTD-39), group C headroom (RTD-44).
- How to run: `python3 -B tests/hub/run_hub_tests.py --sandbox-root ~/fde_sbx/<x> --label D -k TST_POL -k TST_CO_03 -k INC04` (about 65 s); delete `c_pristine` and `scratch` afterwards.
- Stage 15 overall: **IN PROGRESS** (INC-05..INC-09 not started; OD-S12-17 question to Dinesh is due before INC-06 per OD-12).

## Evidence References
- INC-03 evidence: `docs/15-modernization/evidence/inc03/` (summary.txt, hub-final-{A,B,C} reports, char-regression-inc03_report.json, mutation-gate-inc03.txt, checksum-log.txt, rollback-rehearsal-1/); `docs/15-modernization/rollback-rehearsal-inc03.md`; commits `git log --oneline main..stage-15-inc03-hub-db-audit`.
- All INC-01 artifacts in this folder; `evidence/inc01/`.

## Assumptions
- A-15-01 [Assumption] The Stage 0A backup `../_data-backup-2026-10-17/data` is the authoritative copy of the OD-09 baseline (its manifest equals the working tree, checksum rc 0). Confirm: Engagement lead (Dinesh Naik).

## Unknowns
- U-15-01 CI fixture provisioning; U-15-02 3.12 behaviour.

## Unresolved Issues
- RTD-01..RTD-12 (`remaining-technical-debt.md`).

## INC-05 summary
Decision records are now appended only through a human-gated, hash-chained service; the 125 shipped cases are backfilled read-only from the hash-gated snapshot with provenance; the crosswalk links by exact keys and reports orphans. 39 planned tests plus 14 supplementary and 1 egress test pass in sandboxes; INC-02/03/04 groups and the characterization harness stay green; data checksums rc 0. Open: RTD-46..52. No approvals were fabricated; `zone_h.holders` is empty.

## INC-06 summary
Inbound records are now stored raw and immutably, deduplicated by the OD-18 natural key, validated against the declared source contract (record_only by default; enforce needs a human Zone H holder), quarantined or queued with reasons, matched by exact keys and audited per run. 28 planned tests (27 TST-INT + TST-CO-09) plus 14 supplementary and 1 egress test pass in sandboxes; INC-02..05 groups and the characterization harness stay green; data checksums rc 0. Open: RTD-53..57. No approvals fabricated; `zone_h.holders` is empty.

## INC-07 summary
Runs now have complete, append-only records (single-flight, explicit cap, exact backlog, checkpoint/resume with no duplicate effects), metrics are computed deterministically with definition tags and reproduce from stored inputs, and logs / reports / zero-tripwires are in place. THE SCHEDULER IS OFF (OD-19): nothing starts a run by itself, and the schedule flag can only be switched by a Zone H holder, so with the shipped empty holder list it stays off. 39 planned tests plus 19 supplementary and 1 egress test pass in sandboxes; INC-02..06 groups and the characterization harness stay green; data checksums rc 0. Baseline: month-end total 622826.44 (n 125), backlog 89 of 125 under D-OPS, time to close null (`no_completed_cycles`). Open: RTD-58..65; scheduler vs HAR-10 and the Zone H holders are human decisions. No approvals fabricated; `zone_h.holders` is empty.

## INC-08 summary
(Recorded at the Stage 15 close-out; INC-08 was merged as PR #8, OD-21.) A loopback-only HTTP surface and server-rendered pages serve the 48 registry operations through one deny-by-default dispatcher (CSRF, security headers, audited refusals); the reviewer queue and template-generated rule-trace explanations exist; the disposition gate ships in mode `none` and every Zone H action goes through one choke point. 64 planned tests, 14 supplementary and 1 egress test passed; five R2 operations answered 501 (DEV-82). Details: `inc08-design-notes.md`, test-execution-log INC-08.

## INC-09 summary
R2 is built in shadow and switched off by default: keyword / field search on SQLite FTS5 behind `search.fts` (default `off`) with a runtime-detected fallback that returns identical pages, a derived corpus index of the 1,200 documents and 420 archive items (rebuildable; `drop-index` is the rollback), field-class data protection with audited, reason-bearing C3 reads, the rule divergence report (3 of 125 shipped cases differ, reported not resolved), intake delay / freshness reports, the joined crosswalk view, consistency findings (none without an adopted policy), per-source data quality, and deterministic template drafts (off by default). The five INC-08 501 operations now answer in `R2WebApp`; OP-MET-05 stays E-MET-NOT-AVAILABLE. 20 planned tests plus 13 supplementary and 1 egress test pass; every earlier group and the characterization harness stay green; checksums rc 0. No AI, no embeddings, no model call, no network egress; `zone_h.holders` empty. Open: RTD-78..RTD-90.

## Stage 15 close-out (INC-01 .. INC-09)
**Gate outcome recorded: CONDITIONAL PASS** - every planned increment is delivered, tested and behaviour-preserving; no blocking gap remains inside Stage 15's authority; the non-blocking gaps below are documented with owner, stage-relative due point and risk. Stage 15 cannot claim PASS because several gate conditions depend on human decisions and later stages (G1 golden-compare is red by design, CI does not run the suites, mutation gates were not run for INC-08/09, Stage 12 addenda are pending).

| Increment | Scope | Planned tests | Status | Evidence |
|---|---|---|---|---|
| INC-01 | characterisation harness, FX-BASE125 fixture gate, mutation gate | CT-01..CT-16 (harness; not in the 241) | merged (PR #1) | evidence/inc01, BP-1..BP-7 |
| INC-02 | hub skeleton, guards, RO adapters, deviation register, golden-compare | 10 | merged (PR #2) | evidence/inc02 |
| INC-03 | M001, access & audit chain, backup/restore | 16 | merged (PR #3) | evidence/inc03 |
| INC-04 | M002, policy & rule service (as-found sets inactive) | 25 | merged (PR #4) | evidence/inc04 |
| INC-05 | M003, decision record, crosswalk, 125-case backfill | 39 | merged (PR #5) | evidence/inc05 |
| INC-06 | M004, intake in shadow (OD-18 natural key) | 28 | merged (PR #6) | evidence/inc06 |
| INC-07 | M005, runs and metrics, scheduler off | 39 | merged (PR #7) | evidence/inc07 |
| INC-08 | M006, loopback HTTP, reviewer queue, disposition gate `none` | 64 | merged (PR #8) | evidence/inc08 |
| INC-09 | M007, R2 search / corpus / reports / templates | 20 | this branch (PR pending, OD-13) | evidence/inc09 |

- [Verified Fact] Totals: **241 of 241** planned Stage 13 tests (10 + 16 + 25 + 39 + 28 + 39 + 64 + 20) are implemented and green in sandbox runs; one method of group B is skipped on this device (no python3.9 interpreter), as in every increment. Plus the INC-01 harness (CT-01..CT-16; CT-17/18 NOT-RUN by design) and per-increment supplementary and egress tests. Final INC-09 session: 11 hub groups + harness green (test-execution-log INC-09).
- [Verified Fact] Legacy code and `data/` byte-identical across Stage 15; forward-only hub migrations M000..M007 with backup-before-migrate (restore rehearsals recorded for INC-03, INC-06, INC-07, INC-08 and INC-09); no AI dependency or model call (TST-CO-11/12, E05..E09 egress groups); `zone_h.holders` empty; no rule set active, no policy adopted, scheduler off, disposition mode `none`, search / FTS / drafts off.
- [Inference] Stage 15 completion-gate check: every change maps to a backlog item (TB-01..TB-21; CUT items are Stage 30) - met; behaviour-preservation evidence per increment - met (BP-* sections; INC-05/06/08 in their design notes and test logs); changes within Stage 0B boundaries (sandbox-only execution, additive paths, no pyproject / CI change) - met; required artifacts exist - met; critical gaps documented - met (below); evidence supports the conclusion - met for the shadow build, not for any cutover.

**Open decisions handed on** (owner: Engagement lead, Dinesh Naik, unless stated):
- Stage 16 (validation / behaviour comparison): run the TG-4 protocol at the merged HEAD; classify every difference; human walkthroughs behind TST-REV-03/04/08; mutation gates for INC-08/09 (RTD-76, RTD-89).
- Stage 17 (PRD final): Stage 12/13 addenda (codes, exit codes, config keys, query parameters, audit actions: RTD-13/23/24/38/66/78); OPD-01..03 'closed / resolved / approved' and the 48 h clock, OPD-04..06, OPD-11 (scheduler vs HAR-10), retention (OD-S12-09), FR-REV-04 keep or reject (RTD-87), the 43/9 FR count correction (OD-10b), labelled search set (OPD-12, RTD-80).
- Stage 24 (security): A-INC08-1..5, A-INC09-1/5, TLS and exposure (RTD-77), field classes and finance read surface (RTD-82/83), C3 reason transport (RTD-90), audit anchor strength (R-SEC-1).
- Stage 27 (CI / delivery): CI fixture provisioning and running the hub suites in CI (RTD-01/14), runtime target 3.10 vs 3.12 and FTS5 on the target (OD-S12-12, RTD-79), one server entry point (RTD-81).
- Stage 30 (cutover): DV-01..DV-09 preserve-or-fix (OD-S12-13) - golden-compare stays exit 6 until then; DEV-29/30 and the negative-quantity DV; Zone H holders, disposition mode and values (OD-S12-05/06); rule-set activation (OD-S12-04); CONSISTENCY policies; enabling `search.enabled` / `search.fts`; CUT-1..CUT-5.

**Why not BLOCKED:** no condition inside Stage 15's authority is unmet; every open item above is either a human decision (recorded as 'accepted open' under OD-12/OD-22) or a later stage's deliverable. **Why not PASS:** release gates G1, G4, G8, G9, G10 are not run or failing (RTD-74), CI does not execute the suites, and the mutation gate was not run for INC-08/09.

**Recommended next action:** orchestrator review and PR for INC-09 (OD-13), then Stage 16.

## Residual Risks
- RR-MS-1 Harness evidence is device-specific until it runs in CI on the target runtime.
- RR-MS-2 Goldens and fixture are only as trustworthy as the backup; the hash gate detects but cannot repair drift.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-01 (branch `stage-15-inc01-harness`). |
| v0.2 | 2026-10-18 | claude-fde-agent | INC-02 (branch `stage-15-inc02-hub-skeleton`): sections added; INC-01 content unchanged. |
| v0.3 | 2026-10-18 | claude-fde-agent | INC-03 (branch `stage-15-inc03-hub-db-audit`): sections added; earlier content unchanged. |
| v0.4 | 2026-10-18 | claude-fde-agent | INC-04 (branch `stage-15-inc04-rule-service`): sections added; earlier content unchanged. |
| v0.5 | 2026-10-19 | claude-fde-agent | INC-05 (branch `stage-15-inc05-decision-record`): sections added; earlier content unchanged. |
| v0.6 | 2026-10-19 | claude-fde-agent | INC-06 (branch `stage-15-inc06-intake`): sections added; earlier content unchanged. |
| v0.7 | 2026-10-19 | claude-fde-agent | INC-07 (branch `stage-15-inc07-runs-metrics`): sections added; earlier content unchanged. |
| v0.8 | 2026-10-20 | claude-fde-agent | INC-08 summary recorded at close-out (not added in INC-08). |
| v0.9 | 2026-10-20 | claude-fde-agent | INC-09 (branch `stage-15-inc09-search-corpus`) and the Stage 15 close-out (gate outcome CONDITIONAL PASS); status DRAFT -> IN REVIEW; earlier content unchanged. |
