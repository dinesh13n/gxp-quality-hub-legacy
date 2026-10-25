---
stage: "27 — Production Hardening"
artifact: "hardening-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/26-tevv/red-team-findings.md", "docs/26-tevv/residual-tevv-risks.md", "docs/24-security-privacy/residual-security-risks.md", "docs/23-human-control/operating-contract-updates.md", ".fde/orchestrator-decisions.md", "tests/hub/non_add_edits.json", "docs/27-hardening/evidence/"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW: nothing here is an approval and no risk is accepted. Every acceptance, every decision and every sign-off named below is Dinesh Naik's (Engagement lead) and is not recorded by this stage. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
**Gate outcome (agent's computation, a recommendation to the Engagement lead): CONDITIONAL PASS.** The completion gate is met: an SBOM exists and is reproducible (`sbom-summary.md`), every scan in `scan-results.md` ran to completion, every Critical / High item in `vulnerability-register.md` has a disposition in `vulnerability-disposition.md` (no Critical item was found; four High items: one fixed, three dispositioned with an owner), and the regression passes after hardening (`production-readiness-checklist.md`, section PR-R). It is not a PASS because the evidence the gate cannot produce from this laptop is missing: no Python 3.12+ run (RTR-08), the human walkthroughs are unsigned (RTR-07), the CI additions are written but not wired in (HAR-07), and several decisions are Dinesh's (section "Decisions needed").

The stage fixed all nine actionable Stage 26 findings (F-01 .. F-09), closed the three surviving mutants (M5, M9, M10: killed), added the Stage 24 deferrals (per-peer limiter, hardening migration H001), closed the FAC-09 schema gap (23 store-table schemas plus the 17th, OP-INT-01, schema), removed all ten package import cycles of the Stage 20 debt and one of the ten over-complex functions, generated the SBOM, and added a 3.12 / 3.13 CI job as a file. Nothing in legacy code or `data/` changed.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### HP-1 Inputs and what the stage did with each [Verified Fact]
| Input | Item | Stage 27 action | Result |
|---|---|---|---|
| Stage 26 | S26-F-01 (Medium) OP-GATE-02 validated before authenticating | `hub/gate/service.py`: session checked first | FIXED, tests F01 + mutant X1 killed |
| Stage 26 | S26-F-02 (High) restricted evidence note readable by reviewer | `hub/decision/service.py`: note withheld from roles that may not read the record (rule A-27-02) | FIXED under an assumption: Dinesh confirms the rule (D-27-01) |
| Stage 26 | S26-F-03 (Medium) lone surrogate gave HTTP 500 | `hub/core/unitext.py`, `hub/web/wire.py`, `hub/intake/validate.py` | FIXED (400 at the wire; intake item quarantined INVALID_JSON) |
| Stage 26 | S26-F-04 (Low) config error traceback | `hub/config.py` load wraps file errors | FIXED (E-CFG-INVALID, exit 2) |
| Stage 26 | S26-F-05 (Medium) unknown config keys inert | closed key set, E-CFG-INVALID | FIXED (key set = v0.2 schema + `rate_limit` + two INC-09 sections found by group I9) |
| Stage 26 | S26-F-06 (Low) no read timeout | `hub/web/server.py` 10 s, 408 E-REQ-TIMEOUT | FIXED |
| Stage 26 | S26-F-07 (Low) store fault = generic 500 | 503 E-STORE-UNAVAILABLE; a constraint error stays 500 | FIXED |
| Stage 26 | S26-F-08 / F-09 / F-10 mutants M9, M10, M5 survive | layer tests `STG27_M9`, `STG27_M10`, `STG27_M5` | CLOSED (13 of 13 mutants killed, `evidence/mutation-s27.json`) |
| Stage 26 | S26-F-11 group wall time | not changed: S26 142 s, E26 144 s on this laptop in this run (180 s call cap) | OPEN, not blocking (cloud has no cap) |
| Stage 24 | DQ-S24-09 rate limiting (RS-04) | `hub/web/ratelimit.py` per-peer limiter for refused requests (A-27-04) | BUILT, defaults are an assumption (D-27-04) |
| Stage 24 | DQ-S24-09 hardening migration, trigger on `schema_migrations` (RS-12) | `hub/store/hardening.py` + `H001_*.sql`, applied on open (A-27-05) | BUILT |
| OD-31 | FAC-09: 23 schema-less store tables + 17th (OP-INT-01) schema | `docs/27-hardening/schemas/` (24 files) + tests `STG27_C01`, `C02` | CLOSED as structure contracts (not semantic rules) |
| OD-27 | Stage 20 debt: 4 two-cycles, 6 three-cycles, 10 functions over complexity 15 | 6 import-location edits (0 cycles left); `WebApp._dispatch` 22 -> under 15 | cycles CLOSED; complexity 10 -> 9, 9 RESIDUAL (ratchet test) |
| Stage 24 | RS-10 Python 3.10 end of life | CI file for 3.12 / 3.13 prepared; floor stays 3.10 (default) | OPEN, decision D-27-02 |
| Prompt | SBOM, scans, dispositions, readiness checklist | the 11 documents and `evidence/` | DONE |

### HP-2 Work items and acceptance criteria [Verified Fact: these are the stage's own identifiers]
- DW-25 findings and test gaps (AC-HRD-01 F-01; 02 F-02; 03 F-03; 04 F-04 / F-05; 05 F-06 / F-07; 06 mutants M5 / M9 / M10), tests `test_tst_hub_stg27_findings.py`.
- DW-26 store hardening and contract schemas (AC-HRD-10), tests `test_tst_hub_stg27_limiter.py`, `test_tst_hub_stg27_store.py`.
- DW-27 supply chain and structure (AC-HRD-07 SBOM; 08 CI additions; 09 structure ratchet), tests `test_tst_hub_stg27_supply.py`.
- DW-28 documents, scans, dispositions, readiness (this directory).
- Groups: `S27` (STG27, 25 tests) and `E27` (E27EGRESS, 1 test: the same 25 tests under the egress guard, 0 egress attempts, model_calls_total 0).

### HP-3 Behaviour changes (all default to the safest option) [Verified Fact]
| ID | Before | After | Why safest | Deviation | Assumption |
|---|---|---|---|---|---|
| BC-01 | anonymous POST to the Zone H route with an unknown action: 422 | 401 | an anonymous caller learns nothing about valid action names | S27-DEV-05 | - |
| BC-02 | reviewer / finance / integration saw the restricted evidence `note` in event `basis` | they get the fixed text `WITHHELD_BASIS` and `basis_withheld: true`; quality_lead, compliance, dispositioner unchanged; the stored basis and hash chain are untouched; an unresolvable record is withheld too | fail closed; only the view changes | S27-DEV-04 | A-27-02 |
| BC-03 | lone surrogate in a JSON string: 500 | 400 E-REQ-INVALID (intake payload text: item quarantined as INVALID_JSON) | refuse at the boundary | S27-DEV-06 | - |
| BC-04 | unknown config key ignored; unreadable file = traceback | E-CFG-INVALID (exit 2) naming the key path, never the value | a mistyped safety key can not be inert | S27-DEV-03 | A-27-03 |
| BC-05 | no per-connection read timeout | 10 s; short body = 408 E-REQ-TIMEOUT | frees a held thread | S27-DEV-09 | A-27-06 |
| BC-06 | any store fault = generic 500 | 503 E-STORE-UNAVAILABLE (retryable, content-free); constraint errors stay 500 | a defect is not mistaken for an outage | S27-DEV-07 | - |
| BC-07 | unauthenticated flood: one audit row per request | per peer, after `max_rejected` (100) refusals inside `window_seconds` (60): 429 E-REQ-RATE-LIMITED with Retry-After, no store open, no audit row | bounds audit growth (RS-04) and cost | S27-DEV-07 | A-27-04 |
| BC-08 | `schema_migrations` editable by SQL | insert-only triggers (H001), ledger `hardening_schema_migrations`; applied by `open_hub` | a store can not stay without the protection | S27-DEV-08 | A-27-05 |
| BC-09 | store file / anchor file mode follow the umask | group and other bits removed from the store file (never a bit added: a read-only 0444 file stays read-only), a new data directory is 0700, a new anchor file is 0600 | owner-only | S27-DEV-14 | A-27-08 |

### HP-4 Deviation register [Verified Fact]
| ID | Deviation | Reason |
|---|---|---|
| S27-DEV-01 | Stage 26 tests that pinned a finding as "registered" now assert the fixed behaviour (list in `tests/hub/non_add_edits.json`) | a fixed finding must not keep a test that expects the defect |
| S27-DEV-02 | `tests/hub/non_add_edits.json` reset for this stage | OD-27: each BUILD stage replaces the allow-list |
| S27-DEV-03 | closed configuration key set (BC-04) incl. the two INC-09 sections `crosswalk_view`, `intake_reports` that the code reads but the v0.2 schema lacks | S26-F-04 / F-05 |
| S27-DEV-04 | restricted-note withholding (BC-02) | S26-F-02 |
| S27-DEV-05 | authentication before validation on OP-GATE-02 (BC-01) | S26-F-01 |
| S27-DEV-06 | lone-surrogate refusal (BC-03) | S26-F-03 |
| S27-DEV-07 | store-fault 503, per-peer limiter, `_dispatch` split into `_read_body` / `_session` (behaviour identical) | S26-F-07, RS-04, OD-27 complexity |
| S27-DEV-08 | H001 hardening migration, retained-table register and data map entries, three pinned tests adapted (INC03 S01, stg24 supply and tables) | RS-12 |
| S27-DEV-09 | read timeout, 408; `_http8.Served(read_timeout=)` | S26-F-06 |
| S27-DEV-10 | error registry regenerated into `docs/27-hardening/error-registry/` (only ADDS 3 codes, test R01); the stg23 registry test points there because `docs/23` files may not be edited (TST-CO-05 c) | new HTTP codes |
| S27-DEV-11 | six imports moved from module level to function level (no behaviour change) | OD-27 cycle debt |
| S27-DEV-12 | the CI workflow is `ci/hub-hardening.yml`, not under `.github/workflows/` | `.github/` is a protected legacy path (TST-CO-05 a) and HAR-07 needs Dinesh's approval to change CI |
| S27-DEV-13 | `tests/hub/regression_groups.json` gains groups S27 and E27 | new tests |
| S27-DEV-14 | file modes (BC-09) | secrets hardening |
| S27-DEV-15 | the security control register (`hub/security/controls.py`, `docs/24` matrix) is NOT extended with the new controls | a test ties it to the Stage 24 matrix and `docs/24` files may not be edited; the new controls are listed in `runtime-hardening.md` and `supply-chain-controls.md` instead |

### HP-5 Decisions needed from Dinesh (none is taken by this stage) [Verified Fact]
| ID | Decision | Recommended default applied as assumption |
|---|---|---|
| D-27-01 | Restricted-evidence read rule for the event `basis` (F-02) | withhold from roles that may not read the record (A-27-02) |
| D-27-02 | Adopt the Python 3.12 floor (ADR-018) before any exposure; Python 3.10 reached end of life on 2026-10-01 (VR-02) | keep floor 3.10 as shipped; run the 3.12 / 3.13 evidence in the orchestrator cloud |
| D-27-03 | Install `ci/hub-hardening.yml` as `.github/workflows/hub-hardening.yml` (HAR-07) and pin actions to commit SHAs | not installed |
| D-27-04 | Limiter defaults (enabled, 60 s, 100) and the shared-loopback limitation | as built |
| D-27-05 | Spec addenda for E-REQ-TIMEOUT (408), E-REQ-RATE-LIMITED (429), E-STORE-UNAVAILABLE (503), `rate_limit`, `crosswalk_view`, `intake_reports` | none written (Stage 12 documents are not edited in place, OD-10) |
| D-27-06 | Stage 30: harden the legacy `Dockerfile` / `compose.yaml` / `environments/*.env.example` (VR-04) | leave unchanged until Stage 30 |
| D-27-07 | Residual complexity debt (9 functions over 15): accept as backlog or schedule | backlog, ratchet test keeps it from growing |
| D-27-08 | Sign or reject the walkthroughs TST-REV-03 / 04 / 08 (RTR-07) | unsigned |
| D-27-09 | TLS / exposure (DQ-S24-03): stay loopback | loopback (unchanged) |

## Evidence References
- Findings and their proofs: `docs/26-tevv/red-team-findings.md`, `tests/hub/test_tst_hub_stg27_findings.py`, `evidence/mutation-s27.json`.
- Deviations and every non-add edit with its reason: `tests/hub/non_add_edits.json` (31 entries).
- Regression: `evidence/regression/` (per-group logs) and the table in `production-readiness-checklist.md`.
- Decisions log: `.fde/orchestrator-decisions.md` (OD-27, OD-31, OD-32, OD-33).

## Assumptions
- A-27-01 Scope and sequencing choices took the recommended default (OD-32); nothing was accepted on Dinesh's behalf.
- A-27-02 F-02 rule: the event `basis` of EVIDENCE_ATTACHED follows the access rule of the evidence record it came from. Confirm: Dinesh (D-27-01).
- A-27-03 The closed configuration key set equals the v0.2 `hub-config` schema plus `rate_limit`, `crosswalk_view`, `intake_reports`. Confirm: Dinesh with the spec addendum (D-27-05).
- A-27-04 Limiter defaults enabled / 60 s / 100 refused requests per peer. They are not measured needs. Confirm: Dinesh (D-27-04).
- A-27-05 H001 is applied by every `open_hub` (no separate command), because a store must not be left without the ledger protection. It changes no data, so it needs no pre-migration backup. Confirm: Dinesh.
- A-27-06 A 10 s read timeout is long enough for the loopback clients that exist (tests, one operator). Confirm: Stage 29 measurement.
- A-27-07 `ci/` is the holding place for the workflow until HAR-07 is decided.
- A-27-08 File modes: removing group / other bits is safe on a single-user laptop; a shared-group deployment would need a different mode. Confirm: Dinesh at exposure.
- A-27-09 The FAC-09 schemas are structure contracts derived from the DDL; business vocabularies stay in the Stage 12 schemas and the rules.

## Unknowns
- U-27-01 Behaviour on Python 3.12 / 3.13: no run exists (the laptop has 3.10.12 only). Resolution: the orchestrator's cloud run (OD-23), or Dinesh's CI after D-27-03.
- U-27-02 Whether the branch protection and required checks on the GitHub repository exist (not visible from here).
- U-27-03 CVE status of the interpreter and SQLite 3.37.2 on the target host (no vulnerability feed is reachable offline).
- U-27-04 Real exposure, real users, real data volume: none exist (OD-04).

## Unresolved Issues
- Residual complexity debt: 9 functions over 15 (`evidence/static-checks.json`).
- The `spec` documents of Stage 12 do not yet mention the three new error codes or the new config sections (D-27-05).
- RTR-07 / RTR-08 / RTR-10 / RTR-11 from Stage 26 are unchanged and still open (`production-readiness-checklist.md`).

## Residual Risks
- A hardening change can hide a behaviour change; every one is listed in HP-3 and covered by a test and, where it is a fix, by a mutant that was killed.
- The limiter blocks a legitimate local client together with a flooding one while a block lasts (at most `window_seconds`), because every loopback client has the same peer address. Fail closed by design.
- The hardening plan is the agent's reading of the findings; ratings are Inference (TH-1 scale of Stage 26).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 27 BUILD). |
