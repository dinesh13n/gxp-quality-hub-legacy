---
stage: "27 — Production Hardening"
artifact: "production-readiness-checklist.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["docs/27-hardening/*.md", "docs/27-hardening/evidence/", "tests/hub/regression_groups.json", "tests/hub/non_add_edits.json"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW: nothing here is an approval and no risk is accepted. Every acceptance, every decision and every sign-off named below is Dinesh Naik's (Engagement lead) and is not recorded by this stage. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
**Stage 27 gate: CONDITIONAL PASS (agent's computation; a recommendation, not an approval).** 24 of 38 readiness checks are MET; the 14 that are not are listed with an owner, a due point and a risk in section PRC-3 and none of them blocks the gate. Blocking conditions: **none**. The system is ready for the next stage, not for production: it has no TLS, no second factor, no hosted 3.12+ evidence, no signed walkthroughs and no installed CI gate.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### PRC-1 Completion gate [Verified Fact]
| Gate condition | Result | Evidence |
|---|---|---|
| SBOM exists | MET | `evidence/sbom.cdx.json`, `sbom-summary.md` |
| scans complete | MET with two NOT RUN rows declared (SCN-11, SCN-12: no tool available) | `scan-results.md` |
| every critical / high vulnerability dispositioned | MET (0 Critical; 4 High: 1 fixed, 3 open with owner and decision) | `vulnerability-disposition.md` |
| regression passes after hardening | MET | PRC-2 below |
| all required artifacts exist | MET (11 of 11) | this directory |
| critical gaps resolved or documented | MET | PRC-3 |
| evidence supports the conclusion | MET for CONDITIONAL PASS; NOT sufficient for PASS | PRC-3 |

### PRC-2 Readiness checks
#### Identity and access
| ID | Check | Status | Evidence |
|---|---|---|---|
| PR-01 | deny by default for unregistered routes, tested in both layers | MET | S26 A01, `STG27_M5` |
| PR-02 | Zone H holders list empty in the shipped config; no service actor can pass the gate | MET | S26 A02, `STG27_M9` |
| PR-03 | authentication before validation on the gate route | MET | `STG27_F01` |
| PR-04 | restricted evidence and its note limited to the roles in the access rule | MET under assumption A-27-02 | `STG27_F02`; D-27-01 |
| PR-05 | account lockout, session idle / absolute expiry, re-authentication window | MET | S24 controls, S26 A06 |
| PR-06 | second factor | NOT MET | RS-02, DQ-S24-01 |
| PR-07 | service-token expiry required | NOT MET | RS-08, DQ-S24-05 |

#### Secrets
| ID | Check | Status | Evidence |
|---|---|---|---|
| PR-08 | no credential or key in the repository or shipped config | MET | SCN-02 (0 / 0) |
| PR-09 | credentials stored as salted slow hashes; tokens as digests | MET | `secrets-hardening.md` SH-1 |
| PR-10 | store, data directory and new anchor file owner-only | MET | `STG27_H04` |
| PR-11 | key custody and rotation for the anchor seal key | NOT MET | DQ-S24-02 |
| PR-12 | secret scan of git history | UNKNOWN | not run |

#### Runtime and exposure
| ID | Check | Status | Evidence |
|---|---|---|---|
| PR-13 | loopback-only listener; non-loopback refused | MET | S23 S03 .. S05 |
| PR-14 | TLS | NOT MET (not applicable on loopback) | RS-01, DQ-S24-03 |
| PR-15 | read timeout, body limit, anomaly handling | MET | S26 C06 (14 anomalies), X6 |
| PR-16 | rate limit for unauthenticated traffic | MET with caveat (shared loopback peer) | `STG27_L01..L04` |
| PR-17 | failures fail closed without leaking paths, SQL or traces; store fault distinct | MET | S26 B07 (0 hits in 469), C01, `STG27_F07` |
| PR-18 | strict configuration (unknown keys and unreadable files refused with a code) | MET | `STG27_F04`, `F05` |
| PR-19 | no debug mode, test secrets or unnecessary ports in the hub | MET | SCN-08 |
| PR-20 | hub container recipe, supervisor, resource limits | NOT BUILT | RH-5 |
| PR-21 | legacy container files hardened | NOT MET (frozen until Stage 30) | VR-04, D-27-06 |

#### Data and store
| ID | Check | Status | Evidence |
|---|---|---|---|
| PR-22 | ledger tables insert-only incl. `schema_migrations` | MET | `STG27_H01`, `H02` |
| PR-23 | audit chain verifies after hostile traffic and concurrency | MET | S26 C03, C04; `STG27_F01` |
| PR-24 | contract schemas for every store table and the intake request | MET (structure only) | `STG27_C01`, `C02` |
| PR-25 | backup schedule, restore drill, retention for production | NOT MET | Stage 29; migration rollback rehearsals exist (INC03 / INC09 S13) |

#### Dependencies and supply chain
| ID | Check | Status | Evidence |
|---|---|---|---|
| PR-26 | SBOM generated and reproducible | MET | `sbom-summary.md`, `STG27_B01` |
| PR-27 | no third-party package; deny-list gate clean | MET | SCN-01, SCN-05 |
| PR-28 | supported interpreter | NOT MET | VR-02 (3.10 end of life 2026-10-01) |
| PR-29 | regression evidence on Python 3.12+ | NOT MET | U-27-01, RTR-08 |
| PR-30 | CI gates installed | NOT MET (written, not installed) | HAR-07, D-27-03 |
| PR-31 | actions and base image pinned by digest or SHA | NOT MET | SCG-01, SCG-06 |
| PR-32 | signed commits / tags, build provenance | NOT MET / UNKNOWN | SCG-03, SCG-04 |

#### Quality and governance
| ID | Check | Status | Evidence |
|---|---|---|---|
| PR-33 | mutation sample kills the controls it targets | MET | 13 of 13 killed |
| PR-34 | structure ratchet (cycles 0 / 0, over-complex <= 9) | MET | `STG27_S01` |
| PR-35 | human walkthroughs TST-REV-03 / 04 / 08 signed | NOT MET | RTR-07, D-27-08 |
| PR-36 | No-AI product, 0 egress, 0 model calls | MET | E27, SCN-01 |
| PR-37 | legacy code and `data/` byte-identical; checksum rc 0 before and after | MET | every group log, TST-CO-05 |
| PR-38 | no approval, holder, stakeholder or data invented | MET | this stage's documents |


### PRC-R Regression after hardening [Verified Fact: one group per call on the laptop, Python 3.10.12, data checksum rc 0 before and after each]
| Group | Executed / expected | ok | FAIL | ERROR | skipped | Wall (s, laptop) | Checksum rc pre / post |
|---|---|---|---|---|---|---|---|
| A | 45 / 45 | 45 | 0 | 0 | 0 | 82 | 0 / 0 |
| B | 42 / 42 | 41 | 0 | 0 | 1 | 95 | 0 / 0 |
| C1 | 5 / 5 | 5 | 0 | 0 | 0 | 67 | 0 / 0 |
| C2 | 1 / 1 | 1 | 0 | 0 | 0 | 92 | 0 / 0 |
| C3 | 1 / 1 | 1 | 0 | 0 | 0 | 68 | 0 / 0 |
| I45 | 91 / 91 | 91 | 0 | 0 | 0 | 102 | 0 / 0 |
| I6 | 43 / 43 | 43 | 0 | 0 | 0 | 100 | 0 / 0 |
| I7 | 59 / 59 | 59 | 0 | 0 | 0 | 85 | 0 / 0 |
| I8a | 35 / 35 | 35 | 0 | 0 | 0 | 79 | 0 / 0 |
| I8b | 43 / 43 | 43 | 0 | 0 | 0 | 74 | 0 / 0 |
| E8 | 1 / 1 | 1 | 0 | 0 | 0 | 90 | 0 / 0 |
| I9 | 33 / 33 | 33 | 0 | 0 | 0 | 67 | 0 / 0 |
| E9 | 1 / 1 | 1 | 0 | 0 | 0 | 66 | 0 / 0 |
| S20 | 18 / 18 | 18 | 0 | 0 | 0 | 104 | 0 / 0 |
| E20 | 1 / 1 | 1 | 0 | 0 | 0 | 110 | 0 / 0 |
| S21 | 7 / 7 | 7 | 0 | 0 | 0 | 97 | 0 / 0 |
| E21 | 1 / 1 | 1 | 0 | 0 | 0 | 100 | 0 / 0 |
| S23 | 26 / 26 | 26 | 0 | 0 | 0 | 113 | 0 / 0 |
| E23 | 1 / 1 | 1 | 0 | 0 | 0 | 111 | 0 / 0 |
| S24 | 21 / 21 | 21 | 0 | 0 | 0 | 102 | 0 / 0 |
| E24 | 1 / 1 | 1 | 0 | 0 | 0 | 105 | 0 / 0 |
| S26 | 23 / 23 | 23 | 0 | 0 | 0 | 142 | 0 / 0 |
| E26 | 1 / 1 | 1 | 0 | 0 | 0 | 144 | 0 / 0 |
| S27 | 25 / 25 | 25 | 0 | 0 | 0 | 110 | 0 / 0 |
| E27 | 1 / 1 | 1 | 0 | 0 | 0 | 98 | 0 / 0 |
| **total** | **526 / 526** | **525** | **0** | **0** | **1** | | |

Characterization harness (`tests/characterization/run_characterization.py`): 133 of 134 checks pass; the only failing check is CT-13 (Node patch drift, golden v22.23.2 vs v22.23.4, known S24-DEV-04); CT-17 and CT-18 NOT-RUN as before. Data checksum (`sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt`) rc 0 before and after the whole run. TST-CO-05 (legacy byte-identical, only declared edits) is in group B: green.

New tests: group S27 (25 tests: findings 9, limiter 5, store and schemas 7, supply 4) and E27 (1 test, the same 25 tests under the egress guard, 0 egress attempts, model calls 0). Existing tests changed: 11 test files plus the two registers (`regression_groups.json`, `non_add_edits.json`), each listed with its reason in `tests/hub/non_add_edits.json`; no test was weakened to pass (each changed test now asserts the fixed behaviour, and the original assertion of the defect is gone only because the defect is gone).

### PRC-3 Non-blocking gaps (CONDITIONAL PASS needs owner, due point and risk) [Verified Fact]
| Gap | Owner | Due point | Risk if it stays |
|---|---|---|---|
| no Python 3.12+ evidence (PR-29, RTR-08) | orchestrator cloud run, Dinesh via D-27-03 | before PASS / before exposure | Medium |
| interpreter end of life (PR-28, VR-02) | Dinesh (D-27-02) | before exposure or real data | High if exposed |
| walkthroughs unsigned (PR-35, RTR-07) | Dinesh | before PASS | process |
| CI additions not installed; actions tag-referenced (PR-30, PR-31) | Dinesh (D-27-03) | next change to `.github/` | Medium |
| second factor, token expiry, key custody (PR-06, 07, 11) | Dinesh (DQ-S24-01, -05, -02) | before exposure | Medium |
| hub container / supervision / backups (PR-20, PR-25) | Stage 29 / 30 | Stage 29 | Medium |
| legacy container files (PR-21, VR-04) | Dinesh (D-27-06) | Stage 30 | High if run exposed |
| TLS (PR-14) | Dinesh (DQ-S24-03) | before any exposure | High if exposed |
| F-02 rule confirmation (PR-04) | Dinesh (D-27-01) | before real data | Medium |
| specs not updated for 3 new error codes and 3 config sections | Dinesh (D-27-05) | Stage 30 documentation | Low |
| 9 over-complex functions; wall time near the call cap | agent / Stage 29 | backlog | Low |
| git-history secret scan, signing, branch protection unknown (PR-12, PR-32) | Dinesh | before exposure | Low-Medium |

### PRC-4 Recommended next action [Inference]
Proceed to Stage 28. Before any real data or exposure: take D-27-01, D-27-02 and D-27-03 first.

## Evidence References
- all documents in this directory and `evidence/`
- `evidence/regression/final-*.json` (25 groups), `evidence/characterization-summary.txt`
- `.fde/orchestrator-decisions.md` (OD-27, OD-31, OD-32, OD-33)

## Assumptions
- 'MET' means the check passes on the synthetic, loopback, single-user setup that exists; it is not a claim about production.
- The group results are the laptop's (Python 3.10.12); the orchestrator's cloud run is the second opinion (RTR-09).

## Unknowns
- U-27-01, U-27-02, U-27-03, U-27-12.

## Unresolved Issues
- Every NOT MET row in PRC-2 and every gap in PRC-3.

## Residual Risks
- Ready-for-next-stage is not ready-for-production.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 27 BUILD). |

### Addendum: verification notes at hand-off
- Per the coordinator, the laptop re-ran only S27, E27, B and the characterization harness at the final tree; the other group logs are from earlier runs in this stage (hub code identical apart from comments) and the orchestrator's cloud run of all 27 groups is the authoritative regression.
- S26 and E26 exceeded the 180 s call cap late in the stage (host I/O slowed; sandbox build alone took 95 s). S26 was verified as two parts (17 + 6 ok, `evidence/regression/split-S26*-report.json`); E26 was verified in the dev sandbox copy (1 ok, 127 s); the logs `final-S26/E26.json` are the earlier whole-group runs (142 s / 144 s, 23 / 1 ok).
- Open items registered, not started: further complexity refactors (9 functions), remaining mutants beyond 13, SHA pinning, CI installation, hub container recipe.
