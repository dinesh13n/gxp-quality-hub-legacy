from gen_common import *
import collections
AC, PN, SUC = M['AC'], M['PNFR'], M['SUC']; SP = {int(k): v for k, v in C['stage_paths'].items()}
g = collections.defaultdict(list)
for t in TESTS: g[(t['execute_stage'], t['ac'].split('-')[1])].append(t)
STG = {16: 'repo validation (functional run of the planned suite against the sandbox baseline)', 25: 'governance (retention policy evidence)', 26: 'TEVV (independent re-run, security/negative)', 27: 'hardening (performance measurement)', 28: 'resilience (restore rehearsal, run completion)', 30: 'release (rollback rehearsal)', 31: 'observability (log/metric/probe evidence)', 32: 'FinOps (zero-model-call tripwire)'}
r1 = ['| Evidence stage | Folder (from stage prompt) | Meaning | Feature prefix | #tests | Expected evidence artifact (proposed) |', '|---|---|---|---|---|---|']
for (st, p), l in sorted(g.items()):
    r1.append('| %d | `%s` | %s | %s | %d | `%sevidence/<TST-ID>.log` + `results-%s.json` + `SHA256SUMS-evidence.txt` |' % (st, SP.get(st, '?'), STG.get(st, ''), p, len(l), SP.get(st, '?'), p.lower()))
nonA = [t for t in TESTS if not t['evidence_class'].startswith('A')]
r2 = ['| Test | Class | Why evidence is limited | What the evidence can show | What it cannot show |', '|---|---|---|---|---|']
for t in nonA:
    if t['evidence_class'][0] == 'C':
        can, cannot = 'mechanism and sandbox measurement, labelled "synthetic, unvalidated"', 'real-world value / attainment of the stated target'
    else:
        can, cannot = 'both modes of the configurable behaviour with explicit TEST policies', 'which mode the organisation chooses (decision open; accepted-open is legitimate)'
    r2.append('| %s | %s | %s | %s | %s |' % (t['test_id'], t['evidence_class'][0], t['class_note'] or 'depends on ' + ', '.join(AC[t['ac']]['ods']), can, cannot))
r3 = ['| PNFR | Target (Stage 9) | Planned tests | Class mix | Evidence expected | Adequacy for the TARGET claim |', '|---|---|---|---|---|---|']
for p, v in PN.items():
    c = CH[p]; mix = c['classes']
    adq = 'Adequate (mechanism, sandbox)' if mix == 'A' else ('Partial: proxy only, target is an unvalidated working target' if 'C' in mix else 'Adequate once decision made')
    if 'C' in mix and p not in ('PNFR-01','PNFR-02','PNFR-03','PNFR-04','PNFR-05'): adq = 'Mostly adequate; one or more criteria proxy-only (see T2E-5)'
    if 'B' in mix and 'C' not in mix: adq = 'Adequate for mechanism; decision-dependent criteria need both modes (see T2E-5)'
    if p == 'PNFR-06': adq = 'Measurement only: target is Unknown (OPD-14), no pass/fail possible'
    if p in ('PNFR-01', 'PNFR-02', 'PNFR-03', 'PNFR-04', 'PNFR-05'): adq = 'Partial: proxy only, target is an unvalidated working target (Assumption)'
    r3.append('| %s | %s | %s | %s | %s | %s |' % (p, v['target'][:70].replace('|', '/'), rng(c['acs']), mix, ','.join('docs/%s' % SP.get(s, '?').replace('docs/', '') for s in c['evidence_stages']), adq))
r4 = ['| SUC | Success criterion | Mechanism tests (ACs) | Outcome evidence needed | Available now? |', '|---|---|---|---|---|']
for k, u in sorted(UP.items(), key=lambda kv: (kv[1]['type'], int(kv[0].split('-')[1]))):
    if u['type'] != 'SUC': continue
    r4.append('| %s | %s | %d AC via %s | after-intervention measurement on real handling data (Stage 34) | **No**: only synthetic data exists (OD-04); K-04/K-05 unmeasurable (OD-07) |' % (k, u['text'], len(u['acs']), ids(u['frs'], 3)))
cs = collections.Counter(t['evidence_class'][0] for t in TESTS)
fnd = '''### T2E-1 Evidence classes and what counts as evidence [Verified Fact: definitions; Inference: adequacy]
| Class | Meaning | Tests |
|---|---|---|
| A | Executable now in a sandbox, no open decision: evidence = runner log + result JSON + hash manifest | %d |
| B | Decision-dependent: evidence = both modes run with explicit TEST policies; the organisation's choice remains open | %d |
| C | Sandbox/synthetic proxy only: evidence labelled "synthetic, unvalidated"; the real-world claim is not proved | %d |
| D (outcome level) | Real operating data or stakeholder evidence required (value/KPI outcomes) | 0 tests: all %d SUC outcomes fall here and are NOT obtainable (OD-04) |

**Evidence record contract (proposed for Stage 15/16)** [Assumption]: each executed test writes `evidence/<TST-ID>.log` plus a row in `results-<feature>.json` with: test id, AC id, git commit, dataset sha256 (must equal `c254649f...d70aa` for baseline tests), runner/interpreter versions, sandbox path, result (PASS/FAIL/ERROR/SKIP), duration, operator = agent id; the folder carries `SHA256SUMS-evidence.txt` (same convention as `docs/07-repo-assessment/evidence/SHA256SUMS-evidence.txt`). Post-run, `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` must pass (OD-03a).

### T2E-2 Evidence that exists today [Verified Fact]
- **Legacy baseline only.** `docs/07-repo-assessment/baseline-test-results.md`: 15/15 existing `unittest` tests pass on Python 3.10.12 in a sandbox (TR-01); `scripts/verify.sh` passes; goldens in `docs/07-repo-assessment/evidence/golden/*.json` regenerate byte-for-byte twice; 14/14 reference mutants killed (`evidence/analysis/golden_mutation_replay_summary.txt`). This supports FR-CO-01 / BR-11 / BR-13 as an *as-found* regression baseline.
- **Zero executed evidence for any new-module requirement.** The new Hub modules (`decision_events`, Zone H gate, rule service, intake, metrics, ...) do not exist; all %d planned tests are NOT-RUN. No requirement in this stage is claimed as satisfied.
- Stage 12 asserted that the contracts (16 JSON Schemas, DDL, 14 examples) were validated; this stage did not re-run them (documentation-only) [Unknown until Stage 15/16].

### T2E-3 Evidence adequacy dimensions (Required Analysis 6)
- **Adequate by type [Inference]:** insert-only/immutability (database triggers + raw UPDATE/DELETE), Zone H gating (negative tests with service actors), idempotent replay, rule-table equivalence to as-found sets (goldens), static guards (no model import / egress), contract validation. These are deterministic and machine-checkable.
- **Inadequate to prove the stated claim [Verified Fact: ACC-8]:** availability 99.5 %%, 06:00 completion, RTO 8 h / RPO 24 h (no environment; targets are unvalidated working targets); search ranking (3-base-sentence synthetic corpus); corrected-replay on real data (none in shipped data); event-derived time-to-close (no closure timestamps); concurrency on one SQLite file (uncharacterised, CT-17); Part 11 / GxP compliance (framing only, no claim).
- **Evidence that needs a human, not a script [Inference]:** FR-GATE-02 pack walk-through, FR-REV-04 narrative form, adoption decisions (ZH-05/06), role-holder configuration (OD-S12-05/06). Their evidence is a recorded Dinesh Naik decision, not a test log.

### T2E-4 Test -> evidence by stage
%s

### T2E-5 Tests whose evidence is limited (class B and C: %d)
%s

### T2E-6 PNFR evidence adequacy
%s

### T2E-7 Success criteria (outcome-level) evidence
%s
''' % (cs['A'], cs['B'], cs['C'], len(SUC), len(TESTS), '\n'.join(r1), len(nonA), '\n'.join(r2), '\n'.join(r3), '\n'.join(r4))
refs = '- `docs/13-traceability/evidence/tests_plan.csv`, `coverage.json`.\n- Stage prompts `artifact_path` (read by script): `.fde/stage-prompts/{15,16,25,26,27,28,30,31,32}_*.md`.\n- `docs/07-repo-assessment/baseline-test-results.md`, `docs/07-repo-assessment/evidence/`.\n- `docs/12-specs/acceptance-criteria.md` ACC-8; `docs/09-initial-prd/nfrs.md`; `docs/03-problem-value/success-criteria.md`.'
ass = '- A-13-06 [Assumption]: evidence folders follow the stage prompts\' `artifact_path`; the sub-folder `evidence/` and the record contract in T2E-1 are proposed here. Confirm: %s at Stage 18.\n- A-13-07 [Assumption]: classes A/B/C are computed from ACC-8 and from OD-S12 citations in the chain (AC -> BEH/SBR -> OD); an AC whose dependency is only implicit could be mis-classed A.' % OWNER
unk = '- U-13-05: runner and tooling for the new suite (pytest vs unittest; coverage tool absent on the device, Stage 7 TQ-04). Resolution: Stage 14/15.\n- U-13-06: stage numbers beyond 26 execute what, and when (Stage 28 environment for restore rehearsal; Docker unavailable).'
iss = '- All %d tests NOT-RUN; no evidence exists for any new-module requirement.\n- %d tests have limited evidence value by design (class B/C).\n- Outcome-level SUC evidence unobtainable until real data exists (OD-04).' % (len(TESTS), len(nonA))
risk = '- R-13-05 Green sandbox results may be read as production assurance. Mitigation: every report carries "synthetic, unvalidated" (PNFR-20).\n- R-13-06 Evidence produced only by the same agent that wrote the code; Stage 26 TEVV must re-run independently.'
write('test-to-evidence-map.md', SRC_STD + ['docs/07-repo-assessment/baseline-test-results.md', 'docs/13-traceability/evidence/tests_plan.csv', '.fde/stage-prompts/*.md (artifact_path)'], 'Defines what artifact will prove each of the %d planned tests, at which stage and folder, and how adequate that evidence is: class A %d, B %d (decision-dependent), C %d (sandbox proxy only). The only executed evidence today is the Stage 7 legacy baseline (15/15 unittest, goldens, 14/14 mutants). Outcome-level evidence for the 11 SUCs cannot exist until real data does.' % (len(TESTS), cs['A'], cs['B'], cs['C']), fnd, refs, ass, unk, iss, risk)
