---
stage: "26 — TEVV + AI Red Teaming"
artifact: "tevv-results.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 26 TEVV run)"
status: "IN REVIEW"
evidence_sources: ["docs/26-tevv/evidence/regression/*.json", "docs/26-tevv/evidence/s26-tests/*.json", "docs/26-tevv/evidence/hub-mutation-s26.json", "docs/26-tevv/evidence/characterization-final-report.json", "docs/26-tevv/release-thresholds.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Python 3.10.12 / SQLite 3.37.2 on the reference laptop, sandbox copies only. Status IN REVIEW. Results are recorded as observed; no test, threshold or dataset was changed after a result.**

## Summary
The 23 new Stage 26 tests (group S26) and their egress-guarded run (group E26) are green; groups B and I6, the 35 class-B tests, the named set TST-NFR-07/08/09/12/13 + TST-SEC-01..21 and the characterization suite all behave as declared (CT-13 fails only on the known Node patch drift). Of 12 sampled mutants, 9 were killed by some group and 3 survive everything (M5, M9, M10); H3 and H5 are killed again. The red team found no Critical issue and 11 registered findings (`red-team-findings.md`). The backup checksum was rc 0 before and after every run. Thresholds RT-01..RT-15 were computed in `tevv-release-gate.md`.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### TR-0 Declaration record [Verified Fact]
- Thresholds, metrics, dataset specs and the red-team plan were committed as `a42ffe6bdc3dd4e2ef07b1b4644fb66fbedcf234` BEFORE any S26 test existed. The corpus (114 strings) is `tests/hub/data_s26/adversarial_corpus_v1.json`, sha256 `1806bd77cb2c69619bd074515bf497049c1288dd0c957dac6a84d90b9a556f7b`, committed before the S26 tests; the tests assert the hash.
- A baseline run before the declaration (all groups green on `main` 7c60c09, 476 methods; characterization with CT-13 only) is disclosed in `release-thresholds.md` TH-0.

### TR-1 Test runs [Verified Fact] (`evidence/regression/`)
| Run | Selector | Executed / expected | ok | FAIL+ERROR | skipped | Wall | Checksum pre/post |
|---|---|---|---|---|---|---|---|
| Group S26 | `STG26` | 23 / 23 | 23 | 0 | 0 | 145.5 s | 0 / 0 |
| Group E26 | `E26EGRESS` (inner `-k STG26` under the egress guard) | 1 / 1 (inner: 23 ok) | 1 | 0 | 0 | 173.9 s | 0 / 0 |
| Group B | `TST_CO_01,02,04,05,06,07,11,13,14, INC02` | 42 / 42 | 41 | 0 | 1 (registered: `python3.9` not installed, simulated in TST-CO-14 b) | 87.0 s | 0 / 0 |
| Group I6 | `TST_INT, TST_CO_09, INC06, E06EGRESS` | 43 / 43 | 43 | 0 | 0 | 97.0 s | 0 / 0 |
| Class B (35 ids) | one run | 41 methods | 40 | 0 | 1 (same skip) | 66 s | 0 / 0 |
| Named set (TST-NFR, TST-SEC, `I8_SEC_`, `I9_`) | three runs | 41 + 74 + 5 methods (the runs overlap) | all | 0 | 0 | - | 0 / 0 |
- Group E26 passes TST-CO-12's inner-run rule: S26 modules skip themselves inside the TST-CO-12 inner run (`HUB_EGRESS_INNER`), so groups C1..C3 keep their size.
- The full 23-group regression at the final HEAD was NOT run by this agent (S26-DEV-03); the orchestrator runs it in the cloud (OD-23).

### TR-2 S26 test inventory [Verified Fact]
| Class | Tests | What |
|---|---|---|
| A (control) | A01..A07 | route x principal matrix; Zone H bypass; identity and window boundary; mass assignment and spoofing; CSRF / CORS; session abuse; audit amplification |
| B (input / wire) | B01, B02, B03, B04, B07, B08 (input); B05, B06 (wire) | hostile reads, hostile writes, HTML safety, injection invariance, leakage sweep, registered-500 no-state; body structure abuse; URL / verb abuse |
| C (resilience) | C01..C06 | store faults, configuration faults, audit tamper, concurrency, clock rollback, transport anomalies |
| D | D01, D02 | no-AI proof; AGENT REHEARSAL of the walkthroughs |
- ID map (planning docs to executed IDs, S26-DEV-08): red-team-plan "B07 / B08" are executed as B07 leakage sweep and B08 registered-500 no-state; the planning IDs for resilience (C01..C06) and D01 are unchanged; edge spec ED-01 "exactly window" is executed as +/-1 s, +/-1 ms over HTTP and exact / +/-1 us on the pure rule (the fixed clock ticks 1 us per call, S26-DEV-05). The declared documents were not edited after results.

### TR-3 Characterization [Verified Fact]
- `characterization-final-output.txt`: CT-01..CT-16 PASS except CT-13 (`batch:node_cwd_other`, stderr tail differs: golden Node v22.23.2, laptop v22.23.4 = S24-DEV-04). CT-17 and CT-18 NOT-RUN by design (U-07-05, HAR-05). Shipped `tests/test_*.py` 15 ran, OK, post-DB hash equals Stage 7 R1.

### TR-4 Mutation gate (DW-23) [Verified Fact] (`hub-mutation-s26.json`)
| ID | Increment | Mutation | S26 / designated selectors | With earlier group |
|---|---|---|---|---|
| M1 | INC-08 | Zone H re-auth window never enforced | KILLED (A03) | - |
| M2 | INC-08 | holder membership never checked | KILLED (A03) | - |
| M3 | INC-08 | CSRF header never required | KILLED (A04, A05) | - |
| M4 | INC-08 | body limit never enforced | KILLED (B05) | - |
| M5 | INC-08 | deny-by-default branch in `WebAuthorizer` removed | SURVIVED | SURVIVED (`TST_SEC`); equivalent at system level [Inference] |
| M6 | INC-05 | reviewer may read restricted evidence | SURVIVED | KILLED (`TST_DEC_13`) |
| M7 | INC-05 | idempotency key reuse with another body accepted | SURVIVED | KILLED (`TST_DEC_23`) |
| M8 | INC-05 | unknown rule function not refused | SURVIVED | KILLED (`TST_POL_17`) |
| M9 | INC-07 | Zone H service-actor tripwire counts wrong actor kind | SURVIVED | SURVIVED (`TST_OBS`) |
| M10 | INC-07 | schedule enable without authority_ref accepted | SURVIVED | SURVIVED (`TST_RUN`) |
| H3 | Stage 16 survivor | X-Frame-Options weakened | KILLED (STG23 S01, S02) | - |
| H5 | Stage 16 survivor | non-loopback bind accepted | KILLED (STG23 S03, S04) | - |
- Kill ratio by designated tests 6 / 12 (50 %); by any group 9 / 12 (75 %); 3 survivors (F-08, F-09, F-10) registered. The M6 / M7 / M8 survivors under S26 alone are expected: the S26 tests do not target those rules, and the earlier groups kill them. M9 and M10 selectors were narrowed from all of S26 to Control + NoAI before their first run because the full group exceeded the call cap (S26-DEV-07). The throwaway clone needed the gitignored `data/` copied in (copy only; working tree untouched).
- 12 mutants is the declared sample (A-26-03), not the full mutant space.

### TR-5 Class-B re-run (DW-24) [Verified Fact]
Decided modes: OD-S12-12 (floor 3.10 / target 3.12+), OD-S12-17 (intake key), OD-S12-09 (keep all). Others ran in the specified default mode.

| Test | Decision ref | Mode | Methods | Result |
|---|---|---|---|---|
| TST-CO-14 | OD-S12-12 | decided (OD-24): floor 3.10, production target 3.12+ | 5 | ok + 1 skipped |
| TST-DEC-15 | OD-S12-07 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-DEC-16 | OD-S12-07 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-DEC-17 | OD-S12-07 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-DEC-18 | OD-S12-07 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-DEC-19 | OD-S12-07 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-DEC-20 | OD-S12-15 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-DEC-21 | OD-S12-15 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-DEC-26 | OD-S12-16 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-DEC-27 | OD-S12-03,OD-S12-07 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-DEC-28 | OD-S12-03,OD-S12-07 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-GATE-01 | OD-S12-06 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-GATE-02 | OD-S12-06 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-GATE-03 | OD-S12-05 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-GATE-04 | OD-S12-05 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-GATE-05 | OD-S12-05 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-GATE-06 | OD-S12-05 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-GATE-07 | OD-S12-05 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-GATE-08 | OD-S12-05 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-GATE-22 | OD-S12-06 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-INT-06 | OD-S12-17 | decided (OD-18): key (partner, record_kind, ref_id, source_ts) | 1 | ok |
| TST-INT-12 | OD-S12-11 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-INT-13 | OD-S12-11 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-INT-14 | OD-S12-11 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-INT-15 | OD-S12-13 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-OBS-07 | OD-S12-12 | decided (OD-24): floor 3.10, production target 3.12+ | 1 | ok |
| TST-POL-19 | OD-S12-04 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-POL-20 | OD-S12-04 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-POL-21 | OD-S12-04 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-POL-23 | OD-S12-13 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-REV-16 | OD-S12-12 | decided (OD-24): floor 3.10, production target 3.12+ | 1 | ok |
| TST-RUN-01 | OD-S12-10 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-RUN-02 | OD-S12-10 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-RUN-03 | OD-S12-10 | default mode (the specified default; no separate decision recorded by this stage) | 1 | ok |
| TST-SEC-18 | OD-S12-09 | decided (OD-15): keep all records | 3 | ok |

### TR-6 Dimension coverage [Verified Fact]
| # | Dimension | Covered by | Result |
|---|---|---|---|
| 1 | Functional | groups B, I6, class B, named set | green |
| 2 | Behaviour preservation | characterization | CT-13 drift only |
| 3 | Authorisation / control bypass | A01..A07 | no bypass; F-01 |
| 4 | Adversarial input / injection | B01..B08 | no invariance diff; F-03 |
| 5 | Leakage | B07 | F-02 |
| 6 | Resilience | C01..C06 | F-04..F-07 |
| 7 | Business-outcome proxies | below | mechanism-level only |
| 8 | No-AI | D01, E26 | 0 model calls, 0 egress |
| 9 | Mutation strength | TR-4 | 3 survivors |
| 10 | Human validation | walkthrough-records.md | OPEN (unsigned) |
| 11 | Runtime parity | - | 3.12+ not run (Unknown) |

### TR-7 Business-outcome proxies RH-1..RH-7 [Inference: mechanism evidence only, no value, time or cost claim]
| RH | Re-score | Basis |
|---|---|---|
| RH-1 attributable decisions | supported at mechanism level, unchanged | TST_DEC_13 and class B green; F-02 weakens the "restricted evidence" part until fixed |
| RH-2 replay-safe intake | supported on shipped data | group I6 green (43/43); B04 invariance |
| RH-3 definition on every figure | supported (mechanism) | group B/I6 and TST_MET in baseline |
| RH-4 honest baseline possible | unchanged; "measurable, not improved" | no new evidence |
| RH-5 month-end reconciliation | unchanged | no new evidence |
| RH-6 zero unsafe action | supported: 0 Zone H bypass in all S26 attacks | A02, A03, A04; M1, M2 killed; F-08 / F-09 are test gaps, not observed unsafe actions |
| RH-7 No-AI sufficient | mechanism supported (0 model calls); stakeholder judgement still Unknown | D01, E26 |

### TR-8 Walkthrough rehearsal [Verified Fact]
D02 reproduced TST-REV-03 (limit 500 clamped to 100, `next`, total 8,335 in the test store), TST-REV-04 (script text escaped, untrusted marker, no live script) and TST-REV-08 (override / dismiss / refuse offered for 3 of 3 flags) against rendered pages. It is an agent rehearsal. It is not a walkthrough, was not observed or signed by anyone, and RT-13 stays OPEN.

## Evidence References
`docs/26-tevv/evidence/regression/{report-S26,report-E26,report-B,report-I6,report-classB,report-named,report-named2,report-named3}.json`, `final-*.json` run logs; `evidence/s26-tests/*.json`; `evidence/hub-mutation-s26.json`; `evidence/characterization-final-{output.txt,report.json}`.

## Assumptions
- A-26-02 [Assumption] 3.12+/3.13 evidence comes from the orchestrator's cloud run.
- A-26-15 [Assumption] Class-B tests whose decision has no separate record run in the specified default mode and are labelled so.

## Unknowns
- U-26-07 Full-regression result at the final HEAD (to be produced by the orchestrator).
- U-26-08 Results on Python 3.12+ (RT-14).

## Unresolved Issues
- Findings F-01..F-11 and mutants M5, M9, M10 are open (`red-team-findings.md`, `residual-tevv-risks.md`).

## Residual Risks
- See `residual-tevv-risks.md`.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue. |
