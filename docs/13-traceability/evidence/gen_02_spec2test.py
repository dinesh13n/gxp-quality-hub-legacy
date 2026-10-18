from gen_common import *
import collections
AC, BEH, OP, CT = M['AC'], M['BEH'], M['OP'], M['CT']
T = {t['ac']: t for t in TESTS}
acb = C['ac_behs']
# feature summary
fe = collections.OrderedDict()
for pfx in ['DEC','GATE','POL','INT','ID','RUN','MET','REV','SEC','CO','OBS','NFR']:
    a = [x for x in AC if AC[x]['prefix'] == pfx]; b = [x for x in BEH if x.split('-')[1] == pfx]
    fe[pfx] = (len(b), len([1 for s in M['SBR'] if s.split('-')[1] == pfx]), len(a), sum(AC[x]['kind'] == 'positive' for x in a), sum(AC[x]['kind'] == 'negative' for x in a), sum(AC[x]['kind'] == 'edge' for x in a),
               collections.Counter(T[x]['evidence_class'][0] for x in a), sorted({T[x]['execute_stage'] for x in a}))
r1 = ['| Feature prefix | BEH | SBR | AC = planned tests | + | - | edge | Class A/B/C | Evidence stage(s) |', '|---|---|---|---|---|---|---|---|---|']
for p, v in fe.items(): r1.append('| %s | %d | %d | %d | %d | %d | %d | %s | %s |' % (p, v[0], v[1], v[2], v[3], v[4], v[5], '/'.join(str(v[6].get(k, 0)) for k in 'ABC'), ','.join(map(str, v[7]))))
r1.append('| **All** | %d | %d | %d | %d | %d | %d | %s | |' % (len(BEH), len(M['SBR']), len(AC), S['ac_kind']['positive'], S['ac_kind']['negative'], S['ac_kind']['edge'], '/'.join(str(sum(1 for t in TESTS if t['evidence_class'][0] == k)) for k in 'ABC')))
rb = ['| BEH | Requirement(s) named by the behaviour | ACs (planned tests `TST-`) | #AC |', '|---|---|---|---|']
for b, v in BEH.items():
    acs = sorted(a for a in AC if b in acb[a]); rb.append('| %s | %s | %s | %d |' % (b, ids(v['frs'] + v['pnfrs']) if (v['frs'] or v['pnfrs']) else '**none** (%s)' % v['req'][:30], rng(acs), len(acs)))
ra = ['| Planned test | AC | Kind | Level (heuristic) | Fixture | Requirement / rule / behaviour | Author stage | Evidence stage | Class | Status |', '|---|---|---|---|---|---|---|---|---|---|']
for t in TESTS: ra.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (t['test_id'], t['ac'], t['kind'], t['level'], t['fixture'].replace(' (copy of data/legacy.sqlite3, seed 4100, hash-gated)', '').replace(' (86 feed rows / 22 doc bodies / 44 hits)', '').replace(' (explicit test policy, never adopted)', '').replace(' (synthetic intake items)', '').replace(' (in-memory/temp DB)', ''), t['req'].replace(';', ', '), t['author_stage'], t['execute_stage'], t['evidence_class'][0], 'PLANNED / NOT-RUN'))
ro = ['| Op | Route | Release | Requirement(s) | Cited by AC | Cited by BEH | Test path | Level of link |', '|---|---|---|---|---|---|---|---|']
for o, v in OP.items():
    ca, cb = C['op']['ac'][o], C['op']['beh'][o]
    via = sorted({a for b in cb for a in AC if b in acb[a]}) if cb else []
    lvl = 'direct (AC names op)' if ca else ('via behaviour' if cb else 'via parent FR only')
    ro.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (o, v['route'][:48].replace('|', '/'), v.get('release', '?'), ids(v.get('frs', []), 4), ids(ca, 3), ids(cb, 3), rng(ca or via) if (ca or via) else 'FR ACs: ' + rng(sorted({a for f in v.get('frs', []) for a in CH[f]['acs']}))[:60], lvl))
rc = ['| CT | Workflow | What it pins | Pri | Covered today (Stage 7) | Spec mentions | Explicit AC | Linked FR | Planned status |', '|---|---|---|---|---|---|---|---|---|']
for c, v in CT.items():
    sm = S['CT_spec_mentions'][c]; ex = S['CT_explicit_link'].get(c, [])
    rc.append('| %s | %s | %s | %s | %s | %d doc(s)%s | %s | %s | %s |' % (c, v['workflow'], v['pins'][:80].replace('|', '/'), v['pri'], v['covered'][:30], len(sm), ' (range only)' if sm and all('(range)' in x for x in sm) else '', ids(ex), ids(S['CT_fr_links'][c] or (['FR-CO-01'] if ex else [])), 'plan only; Stage 7 PoC captured goldens + 14/14 mutants killed (sandbox); suite itself NOT-BUILT'))
lv = ', '.join('%s %d' % kv for kv in sorted(S['test_levels'].items()))
fnd = '''### S2T-1 Method [Verified Fact]
Every acceptance criterion (AC) in `acceptance-criteria.md` ACC-7 becomes one planned test (`TST-<F>-<nn>`). Behaviours (BEH) and API operations are tested through the ACs that cite them; SBR rules through ACs that cite them or through their parent FR (see RTM-7). Stage 7 characterization tests CT-01..CT-18 are mapped separately (legacy-behaviour preservation). Level, fixture and class are **heuristics computed from the Given/When/Then text** [Inference] and must be confirmed by Stage 15 when tests are written. Nothing has been executed; status is PLANNED / NOT-RUN for all %d tests.

### S2T-2 Totals by feature [Verified Fact: computed]
%s

Planned test levels (heuristic) [Inference]: %s. Fixture rules honour OD-03a/OD-09: every executable test runs in a full sandbox copy of the repo against a hash-verified copy of the 125-case / seed-4100 baseline (`data/legacy.sqlite3` sha256 `c254649f...d70aa`), never against the working tree.

### S2T-3 Untested specs [Verified Fact: computed]
- **Behaviours:** %d of %d have >= 1 AC. None untested.
- **Acceptance-criteria quality:** vague-term scan (appropriate, reasonable, fast, ...) over all Then-clauses flags **%d** criteria [Verified Fact]; 3 criteria use a UI walk-through level and are manual.
- **API operations:** %d of %d are cited by name in an AC or behaviour; the remaining %d are reached only through their parent FR's criteria. Every operation has at least one FR with >= 1 AC, so none is untraceable, but **an operation-level contract test (one per op, driven from `contracts/openapi.yaml`) is not yet planned** [GAP-13-04].
- **SBR rules:** %d of %d cited by an AC directly; %d only via parent FR [GAP-13-03]. The 7 [PARAM] rules (%s) have mechanism-only content because they depend on open decisions.
- **Error codes:** %d of %d error codes defined in `error-handling-spec.md` are asserted by an AC; **%d are not** (%s) [GAP-13-12].
- **Contracts:** 14 example documents + `invalid-cases.json` exist in `docs/12-specs/contracts/examples/` and 16 JSON Schemas in `contracts/schemas/`; they are fixtures for contract tests (5 ACs are at contract level). Whether examples validate was claimed by Stage 12 (not re-run here: documentation-only stage) [Unknown until Stage 15/16 executes them].

### S2T-4 Planned test per behaviour (108)
%s

### S2T-5 Planned test per acceptance criterion (241)
Test ID = `TST-` + AC suffix. "Class" A/B/C as in RTM-4. Evidence stage: 16 functional validation, 26 TEVV, 31 observability, 28 resilience, 25 governance, 27 hardening, 30 release, 32 FinOps.

%s

### S2T-6 API operation -> test path (48)
%s

### S2T-7 Legacy behaviour preservation (Stage 7 CT-01..CT-18) [Verified Fact: plan; Unknown: suite]
%s

Findings: only CT-01..CT-03 are linked by an explicit AC (AC-CO-03); `FR-GATE-01` cites CT-16 and `FR-POL-04` cites CT-01 in the PRD verification column. BEH-CO-01 / AC-CO-01 describe a `hub golden-compare` harness over CT-01..CT-16 but **CT-04..CT-18 have no AC that asserts them individually** [GAP-13-06]. CT-17 (concurrency) and CT-18 (docker) are P3 with no golden (Unknown U-07-05, Docker unavailable); CT-11 (Java) needs a JDK absent on the device (ACC-8).
''' % (len(AC), '\n'.join(r1), lv, S['BEH_with_ac'], S['beh_total'], len(S['tests_with_vague_terms']), S['OP_cited_by_AC_or_BEH'], S['op_total'], S['op_total'] - S['OP_cited_by_AC_or_BEH'], S['SBR_direct_ac'], S['sbr_total'], len(S['SBR_via_fr_only']), ', '.join(S['SBR_param_ids']), S['ERR_asserted_by_AC'], S['ERR_total'], len(S['ERR_not_asserted_by_AC']), ', '.join(S['ERR_not_asserted_by_AC'][:6]) + ', ...', '\n'.join(rb), '\n'.join(ra), '\n'.join(ro), '\n'.join(rc))
refs = '- `docs/12-specs/acceptance-criteria.md` (ACC-4..ACC-8), `docs/12-specs/features/*.md`, `docs/12-specs/api-contracts.md` (API-2, API-3), `docs/12-specs/error-handling-spec.md`, `docs/12-specs/contracts/`.\n- `docs/07-repo-assessment/characterization-test-plan.md`, `baseline-test-results.md` (15/15 existing unittest tests pass in a sandbox, TR-01), `evidence/analysis/golden_mutation_replay_summary.txt`.\n- `docs/13-traceability/evidence/tests_plan.csv`, `coverage.json`.'
ass = '- A-13-04 [Assumption]: AC-per-test 1:1 mapping; unit/service level is the default where no stronger keyword appears.\n- A-13-05 [Assumption]: Stage 15 builds the tests on a BUILD branch (WB-04); Stage 16 runs them; Stage 26 re-runs independently. Confirm: %s.' % OWNER
unk = '- U-13-03: whether the Stage 12 example JSON files validate against their schemas (claimed in Stage 12, not re-executed here).\n- U-13-04: CT-17 concurrency behaviour (U-07-05), Docker/3.12 behaviour (U-07-04).'
iss = '- Operation-level contract tests are not explicit (GAP-13-04); SBR-level tags absent (GAP-13-03); CT-04..CT-18 not acceptance-linked (GAP-13-06); %d error codes unasserted (GAP-13-12).' % len(S['ERR_not_asserted_by_AC'])
risk = '- R-13-03 Heuristic test levels may mis-classify (e.g. a criterion needing a running API marked service/unit); impact is planning only.\n- R-13-04 Class A means "executable without an open decision", not "will pass".'
write('spec-to-test-map.md', SRC_STD + ['docs/12-specs/api-contracts.md', 'docs/12-specs/error-handling-spec.md', 'docs/07-repo-assessment/characterization-test-plan.md', 'docs/13-traceability/evidence/tests_plan.csv'], 'Maps every spec element to a planned test: %d behaviours and %d acceptance criteria (= %d planned tests), %d API operations, %d SBR rules and the %d Stage 7 CT legacy-preservation tests. 108/108 behaviours and 52/52 FR have tests; the weak links are SBR (direct %d/48), API operations (named in AC/BEH %d/48) and CT-04..CT-18 (no AC). All PLANNED / NOT-RUN.' % (S['beh_total'], S['ac_total'], len(TESTS), S['op_total'], S['sbr_total'], S['ct_total'], S['SBR_direct_ac'], S['OP_cited_by_AC_or_BEH']), fnd, refs, ass, unk, iss, risk)
