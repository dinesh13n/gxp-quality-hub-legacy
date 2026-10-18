from gen_common import *
FR, PN = M['FR'], M['PNFR']; sb = C['sbr']
L = []
fr_rows = ['| FR | MoSCoW | Rel | Upstream (BR / SUC / NFR / RC) | Behaviours | SBR | API ops | Acceptance criteria (planned test = same suffix, `TST-`) | #AC (+/-/edge) | Legacy CT | Evidence stage | Class |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
for f in FR:
    c = CH[f]
    fr_rows.append('| %s | %s | %s | %s | %s | %s | %s | %s | %d (%d/%d/%d) | %s | %s | %s |' % (f, c['moscow'], c['release'], c['upstream'].replace(';', ', '), ids(c['behs'], 4), ids(c['sbrs'], 3), ids(c['ops'], 3), rng(c['acs']), len(c['acs']), c['pos'], c['neg'], c['edge'], ids(c['cts']), ','.join(map(str, c['evidence_stages'])), c['classes']))
pn_rows = ['| PNFR | Category | Rel | Upstream NFR | Behaviours | SBR | Acceptance criteria | #AC | Evidence stage | Class | Target evidence class (Stage 9) |', '|---|---|---|---|---|---|---|---|---|---|---|']
for p in PN:
    c = CH[p]
    pn_rows.append('| %s | %s | %s | %s | %s | %s | %s | %d | %s | %s | %s |' % (p, PN[p]['category'], c['release'], ids(PN[p]['nfrs']), ids(c['behs'], 3), ids(c['sbrs'], 3), rng(c['acs']), len(c['acs']), ','.join(map(str, c['evidence_stages'])), c['classes'], PN[p]['evclass'][:50]))
up_rows = ['| ID | Kind | Title (Stage 3/6) | Realised by FR | Realised by PNFR | #AC reachable | R1 FRs | Outcome-level evidence |', '|---|---|---|---|---|---|---|---|']
for k in sorted(UP, key=lambda x: (UP[x]['type'], int(x.split('-')[1]))):
    u = UP[k]
    oc = 'Needs real operating data/stakeholder (none exist, OD-04); synthetic proxy only' if u['type'] == 'SUC' else ('Mechanism provable in sandbox; outcome needs real data' if u['type'] in ('BR',) else 'Mechanism provable in sandbox')
    up_rows.append('| %s | %s | %s | %s | %s | %d | %d | %s |' % (k, u['type'], u['text'][:70].replace('|', '/'), ids(u['frs'], 6), ids(u['pnfrs'], 4), len(u['acs']), u['n_r1_frs'], oc))
sbr_rows = ['| SBR | [PARAM] | Parent FR / PNFR | Direct AC citing SBR | Linkage level |', '|---|---|---|---|---|']
for x, v in M['SBR'].items():
    d = sb['direct'][x]; vb = sb['via_beh'][x]
    lvl = 'direct AC' if d else ('via behaviour text' if vb else 'indirect (parent FR only)')
    sbr_rows.append('| %s | %s | %s | %s | %s |' % (x, 'yes' if v['param'] else '', ids(v['frs'] + v['pnfrs'], 4), ids(d), lvl))
fc = S['fr_moscow_release']
fnd = '''### RTM-1 Method [Verified Fact]
Registers were parsed by script from the real documents (`evidence/trace_parse.py`), then linked and counted by `evidence/trace_compute.py`; output in `evidence/coverage_output.txt`, `evidence/coverage.json`, `evidence/rtm.csv`, `evidence/tests_plan.csv`. No count in this file is estimated. Direction of the chain: **Requirement -> Spec (feature / behaviour BEH / rule SBR / API op OP) -> Planned test (TST-, one per acceptance criterion; plus Stage 7 CT-xx legacy-preservation tests) -> Expected evidence (stage + folder + class)**. Test ID rule: `AC-<F>-<nn>` is verified by planned test `TST-<F>-<nn>`. Every test is **PLANNED / NOT-RUN**.

### RTM-2 Register truth and the FR split discrepancy [Verified Fact]
- Parsed FR register (`docs/09-initial-prd/functional-requirements.md` FF-1): **%d FRs = %d R1 + %d R2** (MoSCoW/release: %s). This confirms OD-10(b) and RF-4: the 41/11 split quoted in the Stage 9 brief is wrong; **43/9 is used throughout Stage 13**. Flagged for correction wherever "41/11" persists (Stage 17 addendum).
- Other registers parsed: %d PNFR, %d BR, %d SUC, %d Stage 3 NFR, %d RC, %d SBR (%d marked [PARAM]), %d behaviours, %d API operations (%s), %d acceptance criteria (%s), %d Stage 7 CT tests.
- Reference integrity: **%d dangling cross-references** (every FR/PNFR/BR/RC/BEH/SBR/AC/OP ID cited by an AC, BEH, SBR, OP, event, schema or threat row exists in a register) [Verified Fact: `dangling_refs` in coverage.json].

### RTM-3 Forward coverage (requirement -> spec -> planned test) [Verified Fact: computed]
| Level | Measure | Result |
|---|---|---|
| FR | with >= 1 behaviour | %d / %d |
| FR | with >= 1 acceptance criterion / planned test | %d / %d (R1: %d / %d) |
| FR | full chain (behaviour or SBR + AC + planned test) | %d / %d |
| FR | with >= 1 negative (forbidden-path) criterion | %d / %d |
| FR | with >= 1 API operation | %d / %d (the %d without are library/CLI/process requirements, see GAP-13-13) |
| FR | with >= 1 SBR (directly) | %d / %d |
| PNFR | with >= 1 AC | %d / %d |
| BR | reachable to >= 1 AC via FR/SBR | %d / %d |
| SUC | reachable to >= 1 AC via FR | %d / %d |
| NFR (Stage 3) | reachable to >= 1 AC via PNFR | %d / %d |
| RC | reachable to >= 1 AC via FR/SBR | %d / %d |
| SBR | with >= 1 AC citing the rule **directly** | %d / %d |
| SBR | with an AC via behaviour text or only via parent FR | %d / %d (indirect, see RTM-7) |
| AC | citing no requirement/behaviour/rule at all | %d (%s) |

"Covered" here means: a planned test or evaluation exists. It does **not** mean the requirement is satisfied; nothing is implemented or run. [Verified Fact: the guardrail "do not mark a requirement covered without a planned test" holds for all 52 FR / 20 PNFR; no requirement is marked verified.]

### RTM-4 Matrix: functional requirements (52) [Verified Fact]
Legend: Class A = executable now in a sandbox with no open decision; B = depends on an open decision (both modes tested); C = sandbox/synthetic proxy only (real-world value cannot be proven here); letters concatenate when the requirement has mixed criteria. Evidence stage numbers: 16 = docs/16-repo-validation/, 24/26 = security/TEVV (docs/24-security-privacy/, docs/26-tevv/), 25 = docs/25-governance/, 27 = docs/27-hardening/, 28 = docs/28-resilience/, 30 = docs/30-release/, 31 = docs/31-observability/, 32 = docs/32-finops/ (paths read from the stage prompts' `artifact_path`).

%s

### RTM-5 Matrix: product NFRs (20) [Verified Fact]
%s

### RTM-6 Matrix: upstream requirements BR / SUC / NFR / RC (derived) [Inference: derived through the FR/PNFR/SBR links]
Stage 3 BR/SUC/NFR and Stage 6 RC IDs are preserved. Their coverage is **derived**: an upstream ID is covered when a requirement that cites it has >= 1 planned test. No test cites a SUC directly. SUC-08 is realised only by an R2 FR (FR-INT-08) and NFR-12 only by an R2 PNFR (PNFR-12): both are therefore **outside the R1 gate** (see GAP-13-10).

%s

### RTM-7 Matrix: spec business rules (48 SBR) [Verified Fact]
%s

### RTM-8 Backward view summary (implementation -> requirement) [Verified Fact]
- API operations: **%d / %d** carry an FR trace (API-3 table); none is without a requirement. Operations by release: %s. Only %d operations are cited by name in any AC, so API-level tests are reached through FR/behaviour links (see spec-to-test-map.md).
- Events (15) and schemas (15): every one traces to an FR/PNFR except `SCH-ERROR` (error envelope; cross-cutting convention, no requirement ID) [GAP-13-05].
- Security threats SEC-01..SEC-15: all trace to an FR/PNFR/BR.
- Behaviours: all 108 have >= 1 AC; **%d** behaviours name no FR/PNFR (%s): justified by an open decision / ADR, not by a requirement [GAP-13-05].
- Detailed orphan analysis: coverage-gap-register.md.
''' % (S['fr_total'], S['fr_release']['R1'], S['fr_release']['R2'], ', '.join('%s %d' % kv for kv in sorted(fc.items())), S['pnfr_total'], S['upstream_counts']['BR'], S['upstream_counts']['SUC'], S['upstream_counts']['NFR'], S['upstream_counts']['RC'], S['sbr_total'], S['sbr_param'], S['beh_total'], S['op_total'], ', '.join('%s %d' % kv for kv in sorted(S['op_release'].items())), S['ac_total'], ', '.join('%s %d' % kv for kv in sorted(S['ac_kind'].items())), S['ct_total'], len(S['dangling_refs']),
 S['FR_with_beh'], S['fr_total'], S['FR_with_ac'], S['fr_total'], S['fr_release']['R1'], S['fr_release']['R1'], S['FR_full_chain'], S['fr_total'], S['FR_with_neg'], S['fr_total'], S['FR_with_op'], S['fr_total'], len(S['FR_without_op']), S['FR_with_sbr'], S['fr_total'],
 S['PNFR_with_ac'], S['pnfr_total'], S['BR_covered'], S['upstream_counts']['BR'], S['SUC_covered'], S['upstream_counts']['SUC'], S['NFR_covered'], S['upstream_counts']['NFR'], S['RC_covered'], S['upstream_counts']['RC'], S['SBR_direct_ac'], S['sbr_total'], S['sbr_total'] - S['SBR_direct_ac'], S['sbr_total'], len(S['AC_without_any_req']), ids(S['AC_without_any_req']),
 '\n'.join(fr_rows), '\n'.join(pn_rows), '\n'.join(up_rows), '\n'.join(sbr_rows), S['op_total'] - len(S['OP_without_fr']), S['op_total'], ', '.join('%s %d' % kv for kv in sorted(S['op_release'].items())), S['OP_cited_by_AC'], len(S['BEH_without_req']), ids(S['BEH_without_req']))
refs = '- Registers: `docs/09-initial-prd/functional-requirements.md` (FF-1, FF-2), `docs/09-initial-prd/nfrs.md` (NF-1), `docs/03-problem-value/{business-requirements,success-criteria,nfrs}.md`, `docs/06-root-cause/confirmed-root-causes.md`.\n- Specs: `docs/12-specs/{business-rules,api-contracts,acceptance-criteria,event-contracts,schema-specifications,security-spec,observability-spec,nfr-spec,spec-readiness}.md`, `docs/12-specs/features/f01..f10*.md`.\n- Legacy tests: `docs/07-repo-assessment/characterization-test-plan.md` (CT-01..CT-18).\n- Computation: `docs/13-traceability/evidence/trace_parse.py`, `trace_compute.py`, `coverage_output.txt`, `coverage.json`, `rtm.csv`, `tests_plan.csv`.'
ass = '- A-13-01 [Assumption]: one planned test per acceptance criterion (`TST-<F>-<nn>` = `AC-<F>-<nn>`) is an adequate granularity; Stage 15 may split or merge tests but must keep the AC link. Confirm: %s at Stage 15/18.\n- A-13-02 [Assumption]: evidence stage assignments (16 functional, 26 security/negative, 28 resilience, 31 observability, 32 cost tripwire, 25 retention, 27 performance, 30 rollback) are proposals; Stage 18 delivery planning confirms.\n- A-13-03 [Inference]: upstream BR/SUC/NFR/RC coverage derived through FR/PNFR/SBR links is accepted as coverage for those IDs because no test cites them directly.' % OWNER
unk = '- U-13-01: whether any requirement will be re-numbered or re-split when the PRD is approved (OD-S12-14). Resolution: Stage 17; the script must be re-run.\n- U-13-02: actual test code does not exist, so levels/fixtures in `tests_plan.csv` are heuristic classifications of Given/When/Then text (Inference).'
iss = '- The 41/11 vs 43/9 discrepancy must be corrected in any downstream document that quotes it (owner: %s, Stage 17).\n- 45 of 48 SBR are covered only indirectly (GAP-13-03).\n- Open decisions OD-S12-01..19 remain open or accepted-open (spec-readiness RD-3).' % OWNER
risk = '- R-13-01 Matrix drift: the matrix is a snapshot of v0.1 docs; any spec change invalidates counts until the scripts are re-run (mitigation: re-run in Stage 17, 18 and 26).\n- R-13-02 "Covered" may be read as "verified": every row is PLANNED / NOT-RUN.'
write('requirements-traceability-matrix.md', SRC_STD + ['docs/03-problem-value/*.md', 'docs/06-root-cause/confirmed-root-causes.md', 'docs/07-repo-assessment/characterization-test-plan.md'], 'Full bidirectional matrix generated by script: %d FR (%d R1 / %d R2), %d PNFR, %d BR, %d SUC, %d NFR, %d RC, %d SBR, each linked to behaviours, API operations, %d acceptance criteria / planned tests and the stage that will produce evidence. Forward coverage: FR %d/%d and PNFR %d/%d have planned tests; all upstream BR/SUC/NFR/RC are reachable (derived). Principal weakness: SBR coverage is %d/%d direct. All statuses PLANNED / NOT-RUN.' % (S['fr_total'], S['fr_release']['R1'], S['fr_release']['R2'], S['pnfr_total'], S['upstream_counts']['BR'], S['upstream_counts']['SUC'], S['upstream_counts']['NFR'], S['upstream_counts']['RC'], S['sbr_total'], S['ac_total'], S['FR_with_ac'], S['fr_total'], S['PNFR_with_ac'], S['pnfr_total'], S['SBR_direct_ac'], S['sbr_total']), fnd, refs, ass, unk, iss, risk)
