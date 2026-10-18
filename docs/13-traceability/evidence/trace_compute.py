#!/usr/bin/env python3
"""Stage 13 - compute traceability + coverage from trace_model.json (produced by trace_parse.py). READ-ONLY on docs.
Usage: python3 trace_compute.py <repo_root> <evidence_dir>   -> writes coverage.json, tests_plan.csv, rtm.csv"""
import json, re, sys, os, glob, csv, collections
root, ev = sys.argv[1], sys.argv[2]
M = json.load(open(os.path.join(ev, 'trace_model.json')))
FR, PN, BR, SUC, NFR, RC, SBR, BEH, AC, OP, CT = (M[k] for k in ('FR','PNFR','BR','SUC','NFR','RC','SBR','BEH','AC','OP','CT'))
SP = {}
for f in glob.glob(os.path.join(root, '.fde/stage-prompts/*.md')):
    t = open(f, encoding='utf-8').read(3000)
    m = re.search(r'artifact_path:\s*"([^"]+)"', t); n = re.match(r'(\d+)', os.path.basename(f))
    if m and n: SP[int(n.group(1))] = m.group(1)
def ac_of_fr(f): return sorted(set(M['ACC4'].get(f, [])) | {a for a, v in AC.items() if f in v['frs']})
def ac_of_pn(p): return sorted(set(M['ACC5'].get(p, [])) | {a for a, v in AC.items() if p in v['pnfrs']})
def ac_of_beh(b): return sorted(set(M['ACC6'].get(b, [])) | {a for a, v in AC.items() if b in v['behs']})
def ac_of_sbr(s): return sorted(a for a, v in AC.items() if s in v['sbrs'])
incons = []
for f in FR:
    fwd = set(M['ACC4'].get(f, [])); rev = {a for a, v in AC.items() if f in v['frs']}
    if fwd != rev: incons.append(('FR', f, sorted(fwd ^ rev)))
for p in PN:
    fwd = set(M['ACC5'].get(p, [])); rev = {a for a, v in AC.items() if p in v['pnfrs']}
    if fwd != rev: incons.append(('PNFR', p, sorted(fwd ^ rev)))
for b in BEH:
    fwd = set(M['ACC6'].get(b, [])); rev = {a for a, v in AC.items() if b in v['behs']}
    if fwd != rev: incons.append(('BEH', b, sorted(fwd ^ rev)))
allids = set(FR) | set(PN) | set(BEH) | set(SBR) | set(AC) | set(BR) | set(RC) | set(OP)
dangling = collections.defaultdict(set)
def chk(src, refs):
    for r in refs:
        if r not in allids: dangling[r].add(src)
for a, v in AC.items(): chk(a, v['frs'] + v['pnfrs'] + v['behs'] + v['sbrs'] + v['brs'] + v['rcs'])
for b, v in BEH.items(): chk(b, v['frs'] + v['pnfrs'])
for s, v in SBR.items(): chk(s, v['frs'] + v['pnfrs'] + v['brs'] + v['rcs'])
for o, v in OP.items(): chk(o, v.get('frs', []))
for e in M['EV'].values(): chk(e['id'], e['frs'] + e['pnfrs'])
for e in M['SCH'].values(): chk(e['id'], e['frs'] + e['pnfrs'])
for s in M['SEC'].values(): chk(s['id'], s['frs'] + s['pnfrs'] + s['brs'])
dangling = {k: sorted(v) for k, v in dangling.items()}
def level(v):
    t = ' '.join([v['given'], v['when'], v['then']]).lower()
    if 'ct-' in t or 'golden' in t: return 'characterization/golden'
    if re.search(r'static|import test|ast |grep|source scan|enumerat', t): return 'static/introspection'
    if re.search(r'ddl|trigger|raw `?(update|delete|insert)|sqlite|sql ', t): return 'database'
    if re.search(r'p95|p50|latency|availability|probe|window|rehears|restore|backup', t): return 'nfr-measurement'
    if re.search(r'schema|json schema|openapi|contract', t): return 'contract'
    if re.search(r'get |post |put |delete |route|endpoint|http|status 4|401|403|409|/api/', t): return 'api'
    if re.search(r'walk-through|\bpage\b|\bscreen\b|view shows|\bui\b', t): return 'ui/manual-walkthrough'
    return 'service/unit'
def fixture(v):
    t = ' '.join([v['given'], v['when'], v['then']]).lower(); r = []
    if re.search(r'shipped|125|baseline|legacy', t): r.append('FX-BASE125 (copy of data/legacy.sqlite3, seed 4100, hash-gated)')
    if re.search(r'planted|86 |22 |44 ', t): r.append('FX-PLANTED (86 feed rows / 22 doc bodies / 44 hits)')
    if re.search(r'polic|clock|rule set|definition', t): r.append('FX-TESTPOLICY (explicit test policy, never adopted)')
    if re.search(r'fresh|no holder|empty|unconfigured|not configured', t): r.append('FX-FRESHINSTALL')
    if re.search(r'replay|re-deliver|redeliver|feed|intake|csv|vendor', t): r.append('FX-SYNTHETIC-FEED (synthetic intake items)')
    if re.search(r'restore|backup|rehears', t): r.append('FX-SANDBOX-COPY')
    return r or ['FX-UNIT-SYNTHETIC (in-memory/temp DB)']
NFR_MAP = {1:28,2:28,3:31,4:31,5:28,6:27,7:26,8:26,9:26,10:25,11:16,12:26,13:26,14:31,15:16,16:16,17:16,18:32,19:30,20:16}
def stages(v):
    p = v['prefix']
    if p in ('DEC','GATE','POL','INT','ID','RUN','MET','REV','CO'): return 16, 15
    if p == 'SEC': return 26, 15
    if p == 'OBS': return 31, 15
    if p == 'NFR': return NFR_MAP[int(re.search(r'PNFR-(\d+)', v['impl']).group(1))], 15
    return 16, 15
def sp(n): return SP.get(n, 'docs/%02d-*/' % n)
ACC8_C = {'AC-NFR-01': 'ACC-8 availability: no environment', 'AC-NFR-02': 'ACC-8 06:00 completion: no schedule', 'AC-NFR-05': 'ACC-8 RTO/RPO: unvalidated targets',
          'AC-REV-15': 'ACC-8 search quality: 3-sentence synthetic corpus', 'AC-INT-07': 'ACC-8 corrected replay: none in shipped data', 'AC-MET-08': 'ACC-8 no real closure timestamps (OD-07)',
          'AC-DEC-22': 'ACC-8 concurrency on one SQLite file uncharacterised (CT-17)'}
VAGUE = re.compile(r'\b(appropriate|user-friendly|reasonable|adequate|fast|quickly|promptly|easy|easily|sufficient|robust|good|nice|as needed)\b', re.I)
ODRE = r'OD-S12-\d+'
beh_ods = {b: set(re.findall(ODRE, v['text'] + ' ' + v['req'])) for b, v in BEH.items()}
sbr_ods = {s_: set(re.findall(ODRE, v['text'] + ' ' + v['impl'])) | ({'PARAM'} if v['param'] else set()) for s_, v in SBR.items()}
ac_behs = {a: set(v['behs']) | {b for b, l in M['ACC6'].items() if a in l} for a, v in AC.items()}
for a, v in AC.items():
    v['ods_direct'] = list(v['ods'])
    v['ods'] = sorted(set(v['ods']) | {o for b in ac_behs[a] for o in beh_ods.get(b, ())} | {o for s_ in v['sbrs'] for o in sbr_ods.get(s_, ()) if o.startswith('OD')})
tests = []
for a, v in sorted(AC.items()):
    ex, au = stages(v)
    cls, note = 'A: executable now in sandbox (no open decision)', ''
    if a in ACC8_C: cls, note = 'C: synthetic/sandbox proxy only', ACC8_C[a]
    elif v['ods']: cls, note = 'B: decision-dependent (test both modes)', ','.join(v['ods'])
    if v['prefix'] == 'NFR' and re.search(r'PNFR-0[1-5]\b', v['impl']) and a not in ACC8_C: cls, note = 'C: synthetic/sandbox proxy only', 'PNFR target is an unvalidated working target (Assumption)'
    vague = sorted(set(m.lower() for m in VAGUE.findall(v['then'])))
    tests.append(dict(test_id='TST-' + a[3:], ac=a, kind=v['kind'], level=level(v), fixture='; '.join(fixture(v)), author_stage=au, execute_stage=ex,
        evidence_path=sp(ex), evidence_class=cls, class_note=note, ct_links=','.join(v['cts']), status='PLANNED / NOT-RUN', vague_terms=','.join(vague),
        req=';'.join(v['frs'] + v['pnfrs'] + v['brs'] + v['sbrs'] + v['behs'])))
T = {t['ac']: t for t in tests}
def tests_of(acs): return ['TST-' + a[3:] for a in acs]
def mk(i, typ, moscow, rel, upstream, behs, sbrs, ops, acs, extra_ct=()):
    cts = sorted({c for a in acs for c in AC[a]['cts']} | set(extra_ct))
    return dict(id=i, type=typ, moscow=moscow, release=rel, upstream=upstream, behs=behs, sbrs=sbrs, ops=ops, acs=acs, tests=tests_of(acs), cts=cts,
        evidence_stages=sorted({T[a]['execute_stage'] for a in acs}), ods=sorted({o for a in acs for o in AC[a]['ods']}),
        classes=''.join(sorted(set(T[a]['evidence_class'][0] for a in acs))), pos=sum(AC[a]['kind'] == 'positive' for a in acs),
        neg=sum(AC[a]['kind'] == 'negative' for a in acs), edge=sum(AC[a]['kind'] == 'edge' for a in acs))
CH = {}
for f, v in FR.items():
    CH[f] = mk(f, 'FR', v['moscow'], v['release'], ';'.join(v['brs'] + v['sucs'] + v['nfrs'] + v['rcs']), sorted(b for b, x in BEH.items() if f in x['frs']),
               sorted(s for s, x in SBR.items() if f in x['frs']), sorted(o for o, x in OP.items() if f in x.get('frs', [])), ac_of_fr(f), re.findall(r'CT-\d\d', v['verification']))
for p, v in PN.items():
    CH[p] = mk(p, 'PNFR', '-', v['release'].split(';')[0].strip(), ';'.join(v['nfrs']), sorted(b for b, x in BEH.items() if p in x['pnfrs']), sorted(s for s, x in SBR.items() if p in x['pnfrs']), [], ac_of_pn(p))
# ---------- upstream (BR/SUC/NFR/RC) derived coverage ----------
UP = {}
def derive(kind, reg, key_fr, key_sbr):
    for u in reg:
        frs = sorted(f for f, v in FR.items() if u in v[key_fr])
        pns = sorted(p for p, v in PN.items() if kind == 'NFR' and u in v['nfrs'])
        sbrs = sorted(s for s, v in SBR.items() if key_sbr and u in v[key_sbr])
        acs = {a for f in frs for a in CH[f]['acs']} | {a for p in pns for a in CH[p]['acs']}
        acs |= {a for a, v in AC.items() if (kind == 'BR' and u in v['brs']) or (kind == 'RC' and u in v['rcs'])}
        acs |= {a for s in sbrs for a in ac_of_sbr(s)}
        UP[u] = dict(id=u, type=kind, text=reg[u]['text'][:140], moscow=reg[u].get('moscow', ''), frs=frs, pnfrs=pns, sbrs=sbrs, acs=sorted(acs),
                     n_r1_frs=sum(FR[f]['release'] == 'R1' for f in frs))
derive('BR', BR, 'brs', 'brs'); derive('SUC', SUC, 'sucs', None); derive('NFR', NFR, 'nfrs', None); derive('RC', RC, 'rcs', 'rcs')
S = {}
def cov(items, pred): return sum(1 for i in items if pred(i))
S['fr_total'] = len(FR); S['fr_release'] = dict(collections.Counter(v['release'] for v in FR.values()))
S['fr_moscow_release'] = {'%s/%s' % k: n for k, n in collections.Counter((v['moscow'], v['release']) for v in FR.values()).items()}
S['pnfr_total'] = len(PN); S['ac_total'] = len(AC); S['ac_kind'] = dict(collections.Counter(v['kind'] for v in AC.values()))
S['beh_total'] = len(BEH); S['sbr_total'] = len(SBR); S['op_total'] = len(OP); S['ct_total'] = len(CT)
S['sbr_param'] = sum(v['param'] for v in SBR.values()); S['op_release'] = dict(collections.Counter(v.get('release', '?') for v in OP.values()))
S['upstream_counts'] = dict(BR=len(BR), SUC=len(SUC), NFR=len(NFR), RC=len(RC))
S['FR_with_ac'] = cov(FR, lambda f: CH[f]['acs']); S['FR_with_beh'] = cov(FR, lambda f: CH[f]['behs']); S['FR_with_sbr'] = cov(FR, lambda f: CH[f]['sbrs']); S['FR_with_op'] = cov(FR, lambda f: CH[f]['ops'])
S['FR_with_beh_or_sbr'] = cov(FR, lambda f: CH[f]['behs'] or CH[f]['sbrs'])
S['FR_full_chain'] = cov(FR, lambda f: CH[f]['acs'] and (CH[f]['behs'] or CH[f]['sbrs']))
S['FR_R1_full_chain'] = cov([f for f in FR if FR[f]['release'] == 'R1'], lambda f: CH[f]['acs'] and (CH[f]['behs'] or CH[f]['sbrs']))
S['FR_with_neg'] = cov(FR, lambda f: CH[f]['neg']); S['FR_with_ct'] = cov(FR, lambda f: CH[f]['cts'])
for nm, pred in (('FR_without_ac', lambda f: not CH[f]['acs']), ('FR_without_beh', lambda f: not CH[f]['behs']), ('FR_without_sbr', lambda f: not CH[f]['sbrs']),
                 ('FR_without_op', lambda f: not CH[f]['ops']), ('FR_without_negative', lambda f: not CH[f]['neg'])):
    S[nm] = [f for f in FR if pred(f)]
S['PNFR_with_ac'] = cov(PN, lambda p: CH[p]['acs']); S['PNFR_without_ac'] = [p for p in PN if not CH[p]['acs']]
S['PNFR_without_beh_or_sbr'] = [p for p in PN if not (CH[p]['behs'] or CH[p]['sbrs'])]
for k, reg in (('BR', BR), ('SUC', SUC), ('NFR', NFR), ('RC', RC)):
    S[k + '_covered'] = cov(reg, lambda u: UP[u]['acs']); S[k + '_uncovered'] = [u for u in reg if not UP[u]['acs']]
    S[k + '_no_fr_or_pnfr'] = [u for u in reg if not (UP[u]['frs'] or UP[u]['pnfrs'])]
    S[k + '_only_r2_frs'] = [u for u in reg if UP[u]['frs'] and UP[u]['n_r1_frs'] == 0]
S['SBR_with_ac'] = cov(SBR, lambda s: ac_of_sbr(s)); S['SBR_without_ac'] = [s for s in SBR if not ac_of_sbr(s)]
S['SBR_without_req'] = [s for s, v in SBR.items() if not (v['frs'] or v['pnfrs'])]
S['BEH_with_ac'] = cov(BEH, lambda b: ac_of_beh(b)); S['BEH_without_ac'] = [b for b in BEH if not ac_of_beh(b)]
S['BEH_without_req'] = [b for b, v in BEH.items() if not (v['frs'] or v['pnfrs'])]
S['BEH_without_req_detail'] = {b: BEH[b]['req'][:80] for b in S['BEH_without_req']}
S['OP_without_fr'] = [o for o, v in OP.items() if not v.get('frs')]
op_ac = {o: sorted({a for b in v['behs'] for a in ac_of_beh(b)}) for o, v in OP.items()}
S['OP_without_ac_via_beh'] = [o for o in OP if not op_ac[o]]; S['OP_with_ac_via_beh'] = len(OP) - len(S['OP_without_ac_via_beh'])
S['OP_no_beh_ref'] = [o for o, v in OP.items() if not v['behs']]
S['AC_without_any_req'] = [a for a, v in AC.items() if not (v['frs'] or v['pnfrs'] or v['brs'] or v['sbrs'] or v['behs'])]
S['AC_without_fr_or_pnfr_direct'] = [a for a, v in AC.items() if not (v['frs'] or v['pnfrs'])]
def resolves(a):
    v = AC[a]
    if v['frs'] or v['pnfrs']: return True
    return any(BEH.get(b, {}).get('frs') or BEH.get(b, {}).get('pnfrs') for b in v['behs']) or any(SBR.get(s, {}).get('frs') or SBR.get(s, {}).get('pnfrs') for s in v['sbrs'])
S['AC_unresolvable_to_FR_PNFR'] = [a for a in AC if not resolves(a)]
S['EV_without_req'] = [e for e, v in M['EV'].items() if not (v['frs'] or v['pnfrs'])]; S['SCH_without_req'] = [e for e, v in M['SCH'].items() if not (v['frs'] or v['pnfrs'])]
S['SEC_threats_without_req'] = [e for e, v in M['SEC'].items() if not (v['frs'] or v['pnfrs'] or v['brs'])]
S['ERR_total'] = len(M['ERR'])
errs_in_ac = {e for v in AC.values() for e in re.findall(r'E-[A-Z]+(?:-[A-Z0-9]+)+', ' '.join([v['given'], v['when'], v['then']]))}
S['ERR_asserted_by_AC'] = len(errs_in_ac & set(M['ERR'])); S['ERR_not_asserted_by_AC'] = sorted(set(M['ERR']) - errs_in_ac); S['ERR_in_AC_but_undefined'] = sorted(errs_in_ac - set(M['ERR']))
ct_expl = collections.defaultdict(set)
for a, v in AC.items():
    for c in v['cts']: ct_expl[c].add(a)
rng = [a for a, v in AC.items() if re.search(r'CT-\d\d\.\.CT-\d\d', ' '.join([v['given'], v['when'], v['then']]))]
S['CT_explicit_link'] = {c: sorted(ct_expl[c]) for c in CT if ct_expl[c]}
S['CT_no_ac_link'] = [c for c in CT if not ct_expl[c]]; S['AC_with_CT_range'] = rng
S['CT_fr_links'] = {c: sorted({f for a in ct_expl[c] for f in AC[a]['frs']}) for c in CT}
S['CT_in_FR_verification'] = {f: sorted(set(re.findall(r'CT-\d\d', v['verification']))) for f, v in FR.items() if re.search(r'CT-\d\d', v['verification'])}
S['test_levels'] = dict(collections.Counter(t['level'] for t in tests)); S['test_classes'] = dict(collections.Counter(t['evidence_class'] for t in tests))
S['tests_by_execute_stage'] = dict(collections.Counter(t['execute_stage'] for t in tests))
S['tests_with_vague_terms'] = [(t['test_id'], t['vague_terms']) for t in tests if t['vague_terms']]
S['FR_only_C'] = [f for f in FR if CH[f]['classes'] and set(CH[f]['classes']) <= {'C'}]
S['FR_has_B'] = [f for f in FR if 'B' in CH[f]['classes']]; S['FR_has_C'] = [f for f in FR if 'C' in CH[f]['classes']]
S['PNFR_only_C'] = [p for p in PN if CH[p]['classes'] and set(CH[p]['classes']) <= {'C'}]; S['PNFR_has_B'] = [p for p in PN if 'B' in CH[p]['classes']]
S['spec_internal_inconsistencies'] = incons; S['dangling_refs'] = dangling
S['FR_R2_ids'] = [f for f, v in FR.items() if v['release'] == 'R2']
S['stage_paths_used'] = {n: SP.get(n) for n in sorted({t['execute_stage'] for t in tests} | {15, 16, 26})}
S['OD_total'] = len(M['OD']); S['AC_decision_dependent'] = sum(1 for t in tests if t['evidence_class'].startswith('B'))
S['OD_not_referenced_by_AC'] = sorted(set(M['OD']) - {o for v in AC.values() for o in v['ods']})
# --- SBR / OP / CT multi-level linkage ---
sbr_direct = {x: ac_of_sbr(x) for x in SBR}
sbr_via_beh = {x: sorted({a for a in AC for b in ac_behs[a] if x in re.findall(r'SBR-[A-Z]+-\d+', BEH[b]['text'])}) if True else [] for x in SBR}
sbr_via_fr = {x: sorted({a for f in SBR[x]['frs'] for a in CH[f]['acs']} | {a for p in SBR[x]['pnfrs'] for a in CH[p]['acs']}) for x in SBR}
S['SBR_direct_ac'] = cov(SBR, lambda x: sbr_direct[x]); S['SBR_via_beh_text'] = cov(SBR, lambda x: sbr_direct[x] or sbr_via_beh[x])
S['SBR_via_fr_only'] = [x for x in SBR if not sbr_direct[x] and not sbr_via_beh[x] and sbr_via_fr[x]]; S['SBR_no_path'] = [x for x in SBR if not (sbr_direct[x] or sbr_via_beh[x] or sbr_via_fr[x])]
S['SBR_param_ids'] = [x for x, v in SBR.items() if v['param']]
alltext = {a: ' '.join([v['given'], v['when'], v['then'], v['impl']]) for a, v in AC.items()}
op_cited_in_ac = {o: sorted(a for a in AC if o in alltext[a]) for o in OP}
op_cited_in_beh = {o: sorted(b for b in BEH if o in BEH[b]['text']) for o in OP}
S['OP_cited_by_AC'] = cov(OP, lambda o: op_cited_in_ac[o]); S['OP_cited_by_BEH'] = cov(OP, lambda o: op_cited_in_beh[o])
S['OP_cited_by_AC_or_BEH'] = cov(OP, lambda o: op_cited_in_ac[o] or op_cited_in_beh[o])
S['OP_ac_path_direct_or_beh_or_fr'] = cov(OP, lambda o: op_cited_in_ac[o] or op_ac[o] or any(CH[f]['acs'] for f in OP[o].get('frs', [])))
S['OP_only_via_fr'] = [o for o in OP if not (op_cited_in_ac[o] or op_ac[o] or any(a for b in op_cited_in_beh[o] for a in ac_of_beh(b)))]
S['OP_r2'] = [o for o, v in OP.items() if v.get('release') == 'R2']
# CT mentions across spec docs
ct_docs = collections.defaultdict(set)
for f in glob.glob(os.path.join(root, 'docs/12-specs/**/*.md'), recursive=True):
    t = open(f, encoding='utf-8').read()
    for c in CT:
        if c in t: ct_docs[c].add(os.path.relpath(f, os.path.join(root, 'docs')))
    for a_, b_ in re.findall(r'CT-(\d\d)\.\.CT-(\d\d)', t):
        for i in range(int(a_), int(b_) + 1): ct_docs['CT-%02d' % i].add(os.path.relpath(f, os.path.join(root, 'docs')) + ' (range)')
S['CT_spec_mentions'] = {c: sorted(ct_docs[c]) for c in CT}
S['CT_zero_spec_mention'] = [c for c in CT if not ct_docs[c]]
S['spec_inconsistency_counts'] = dict(collections.Counter(i[0] for i in incons))
S['ACC6_pairs_not_in_Implements'] = sum(len(i[2]) for i in incons if i[0] == 'BEH')
S['ACC6_pairs_total'] = sum(len(v) for v in M['ACC6'].values())
S['FR_with_opd_in_text'] = {f: sorted(set(re.findall(r'OPD-\d+', v['text']))) for f, v in FR.items() if re.search(r'OPD-\d+', v['text'])}
S['AC_decision_dependent_all'] = [t['test_id'] for t in tests if t['evidence_class'].startswith('B')]
S['OD_referenced_via_chain'] = sorted({o for v in AC.values() for o in v['ods'] if o.startswith('OD')})
S['OD_not_referenced_via_chain'] = sorted(set(M['OD']) - set(S['OD_referenced_via_chain']))
S['FR_sbr_levels'] = None
json.dump(dict(stats=S, sbr=dict(direct=sbr_direct, via_beh=sbr_via_beh, via_fr=sbr_via_fr), op=dict(ac=op_cited_in_ac, beh=op_cited_in_beh), ac_behs={k: sorted(v) for k, v in ac_behs.items()},  chains=CH, upstream=UP, tests=tests, op_ac=op_ac, stage_paths=SP), open(os.path.join(ev, 'coverage.json'), 'w'), indent=1, sort_keys=True)
with open(os.path.join(ev, 'tests_plan.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(tests[0].keys())); w.writeheader(); w.writerows(tests)
with open(os.path.join(ev, 'rtm.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['id', 'type', 'moscow', 'release', 'upstream', 'behaviours', 'sbr', 'ops', 'acceptance_criteria', 'planned_tests', 'legacy_CT', 'evidence_stages', 'open_decisions', 'evidence_classes', 'status'])
    for k, c in CH.items(): w.writerow([c['id'], c['type'], c['moscow'], c['release'], c['upstream'], ' '.join(c['behs']), ' '.join(c['sbrs']), ' '.join(c['ops']), ' '.join(c['acs']), ' '.join(c['tests']), ' '.join(c['cts']), ' '.join(map(str, c['evidence_stages'])), ' '.join(c['ods']), c['classes'], 'PLANNED / NOT-RUN'])
print(json.dumps(S, indent=1, sort_keys=True))
