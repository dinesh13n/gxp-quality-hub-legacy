from gen_common import *
cs = S['test_classes']
gate = '''| Gate condition | Result | Evidence |
|---|---|---|
| Every requirement maps to spec, test/evaluation and expected evidence | **Met at PLANNED level**: FR 52/52, PNFR 20/20; BR 13/13, SUC 11/11, NFR 16/16, RC 8/8 reachable (derived). Not met at EXECUTED level (0 tests run) | RTM-3 |
| Critical unexplained gaps block progression | **Met**: 0 unexplained gaps; 22 explained, owned, non-blocking | coverage-gap-register.md |
| All required artifacts exist at the paths above | **Met**: 10 of 10 in `docs/13-traceability/` | listing below |
| Critical gaps resolved or explicitly documented | **Met** (documented; none critical) | GAP-1 |
| Evidence supports the stage conclusion | **Met** for the planning claim; the stage makes no claim that any requirement is satisfied | `evidence/coverage_output.txt` |
| No requirement marked covered without a planned test | **Met**: 0 requirements covered without a planned test; every row is PLANNED / NOT-RUN | RTM-4/5 |
| Backup integrity | `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` -> rc 0 (1,512 entries); `git status` shows only the new `docs/13-traceability/` folder | run in this stage |
'''
fnd = '''### SUM-1 Gate status: **CONDITIONAL PASS**
%s
No blocking condition remains. The conditions below are non-blocking but must be accepted or resolved by %s.

### SUM-2 Headline numbers (computed by script, never estimated) [Verified Fact]
| Item | Count |
|---|---|
| FR (parsed from FF-1) | %d = **%d R1 + %d R2** (OD-10b confirmed: NOT 41/11) |
| PNFR / BR / SUC / NFR / RC | %d / %d / %d / %d / %d |
| Behaviours / SBR / API ops / events / schemas | %d / %d (%d [PARAM]) / %d (%d R1 + %d R2) / %d / %d |
| Acceptance criteria = planned tests | %d (%d positive, %d negative, %d edge) |
| Planned tests by evidence class | A %d, B %d, C %d |
| Stage 7 legacy CT tests | %d (explicitly AC-linked: 3) |
| FR with behaviour / AC / full chain | %d / %d / %d of %d |
| FR with a negative criterion | %d of %d |
| SBR cited directly by an AC | %d of %d |
| Dangling references | %d |
| Orphans | 3 ACs, 2 behaviours, 1 schema (constraint-justified) |
| Gaps | 22, 0 blocking |
| Tests executed | **0** |

### SUM-3 Key findings
1. **[Verified Fact]** Forward coverage is complete at the planned level: 52/52 FR and 20/20 PNFR have behaviours, criteria and planned tests; upstream BR/SUC/NFR/RC all reach tests through them.
2. **[Verified Fact]** The FR register parses to 43 R1 + 9 R2 (40 Must/R1, 3 Should/R1, 7 Should/R2, 2 Could/R2); the Stage 9 brief's 41/11 is wrong (GAP-13-02).
3. **[Verified Fact]** Rule-level traceability is weak: only 2 of 48 SBR are cited by an AC (GAP-13-03); operations are named in AC/BEH for only %d of 48 (GAP-13-04); CT-04..CT-18 are not acceptance-linked (GAP-13-06).
4. **[Verified Fact]** %d tests (class C) can only produce sandbox proxies and %d (class B) depend on open decisions; PNFR-01..05 targets cannot be proven; all 11 SUC outcomes need real data that does not exist (GAP-13-07/08/09).
5. **[Verified Fact]** No-AI (OD-08): no AI-quality requirements exist to trace; the control is FR-CO-04/PNFR-18 with a Stage 32 tripwire. Cost: no cost requirement beyond metric correctness (GAP-13-16).

### SUM-4 Conditions for CONDITIONAL PASS (owner: %s)
| # | Condition | Resolving stage | Risk if late |
|---|---|---|---|
| C1 | Accept or resolve the decision-dependent items (class B; OD-S12-03, -11, -12, -15, -16, -17, -19 first) | before Stage 15 build | rework of F01/F04 tests |
| C2 | Tag each test with SBR ids; add per-operation contract tests; add negative ACs for the 8 FRs; assert the 27 unasserted error codes | Stage 15 test authoring | rules and error paths unguarded |
| C3 | Add acceptance links (AC-CO-xx) for the P1 legacy tests CT-04..CT-16 before the first legacy change | Stage 14/15 | silent legacy regression |
| C4 | Correct 41/11 -> 43/9 and addend OD-10 items (DC-03 key, runtime, source-contract scope); consider CON- IDs for constraint-only items | Stage 17 | wrong plan sizing |
| C5 | Re-run `evidence/trace_parse.py` + `trace_compute.py` after any spec/PRD change | Stages 17, 18, 26 | stale matrix |

### SUM-5 Hand-off
- **Stage 14/15/16:** use `evidence/tests_plan.csv` as the test backlog; `evidence/rtm.csv` as the acceptance map; keep the AC -> TST id rule.
- **Stage 18 (delivery planning):** 197 class-A tests are buildable immediately; schedule class B after decisions; tests per evidence stage: %s.
- **Stage 26 (TEVV):** independent re-run of security/negative tests (26 tests assigned) and the unasserted error codes.
- **FINAL acceptance evidence map:** requirement IDs are stable (do not renumber); disposition each FR as Delivered/Changed/Deferred/Rejected/Superseded using `rtm.csv`.

### SUM-6 Artifact index
requirements-traceability-matrix.md; spec-to-test-map.md; test-to-evidence-map.md; security-traceability.md; data-traceability.md; ai-quality-traceability.md; resilience-traceability.md; cost-traceability.md; coverage-gap-register.md; traceability-summary.md; evidence/ (trace_parse.py, trace_compute.py, gen_*.py, trace_model.json, coverage.json, coverage_output.txt, rtm.csv, tests_plan.csv, integrity_check.txt).

### SUM-7 Gate evaluation
%s
''' % ('Result **CONDITIONAL PASS** (not PASS) because nothing is executed, and some evidence cannot exist until decisions/real data arrive.', OWNER, S['fr_total'], S['fr_release']['R1'], S['fr_release']['R2'], S['pnfr_total'], S['upstream_counts']['BR'], S['upstream_counts']['SUC'], S['upstream_counts']['NFR'], S['upstream_counts']['RC'], S['beh_total'], S['sbr_total'], S['sbr_param'], S['op_total'], S['op_release']['R1'], S['op_release']['R2'], len(M['EV']), len(M['SCH']), S['ac_total'], S['ac_kind']['positive'], S['ac_kind']['negative'], S['ac_kind']['edge'], cs['A: executable now in sandbox (no open decision)'], cs['B: decision-dependent (test both modes)'], cs['C: synthetic/sandbox proxy only'], S['ct_total'], S['FR_with_beh'], S['FR_with_ac'], S['FR_full_chain'], S['fr_total'], S['FR_with_neg'], S['fr_total'], S['SBR_direct_ac'], S['sbr_total'], len(S['dangling_refs']), S['OP_cited_by_AC_or_BEH'], cs['C: synthetic/sandbox proxy only'], cs['B: decision-dependent (test both modes)'], OWNER, ', '.join('stage %s: %d' % kv for kv in sorted(S['tests_by_execute_stage'].items(), key=lambda x: int(x[0]))), gate)
write('traceability-summary.md', SRC_STD + ['docs/13-traceability/*.md'], 'Stage 13 gate: CONDITIONAL PASS. Bidirectional traceability built by script: 52 FR (43 R1 / 9 R2 - the 41/11 figure is wrong), 20 PNFR and 241 acceptance criteria all linked to planned tests with expected evidence; 0 dangling IDs; 22 explained gaps, 0 blocking. 0 tests executed; %d class-B and %d class-C tests limit what evidence can show.' % (cs['B: decision-dependent (test both modes)'], cs['C: synthetic/sandbox proxy only']), fnd,
 '- All nine sibling artifacts; `evidence/coverage_output.txt`; `.fde/orchestrator-decisions.md`; `docs/12-specs/spec-readiness.md` RD-3.', '- A-13-14 [Assumption]: Dinesh accepts planned-level coverage as sufficient to enter Stage 14.', '- U-13-13: whether Dinesh will decide or accept-open the 19 OD-S12 items before Stage 15.', '- See conditions C1-C5 and coverage-gap-register.md.', '- Residual: R-13-01..R-13-12 across artifacts; chiefly stale matrix, "covered" read as "verified", and absence of real-data evidence.')
