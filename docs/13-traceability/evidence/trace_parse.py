#!/usr/bin/env python3
"""Stage 13 - parse requirement/spec/test registers from docs/ (READ-ONLY) into model.json.
Usage: python3 trace_parse.py <repo_root> <out_dir>
Never executes application code; only reads markdown under docs/."""
import re, sys, json, glob, os
root = sys.argv[1]; out = sys.argv[2]
D = lambda p: os.path.join(root, 'docs', p)
def rd(p): return open(p, encoding='utf-8').read()
def rows(text, prefix, ncols=None, minc=None):
    res = []
    for ln in text.splitlines():
        if ln.startswith('| ' + prefix):
            c = [x.strip() for x in ln.strip().strip('|').split('|')]
            if ncols and len(c) != ncols: continue
            if minc and len(c) < minc: continue
            res.append(c)
    return res
def ids(s, pat): return sorted(set(re.findall(pat, s)))
def expand_range(s):
    # expand 'CT-01..CT-16' and 'X-01..03' style ranges, return list of ids found
    found = set(re.findall(r'\bCT-\d\d\b', s))
    for a, b in re.findall(r'\bCT-(\d\d)\.\.CT-(\d\d)\b', s):
        for i in range(int(a), int(b) + 1): found.add('CT-%02d' % i)
    return found
M = {}
# ---- FR register (FF-1, 7 cols + more) ----
fr_txt = rd(D('09-initial-prd/functional-requirements.md'))
FR = {}
for c in rows(fr_txt, 'FR-', minc=7):
    if len(c) == 7 or len(c) >= 7:
        if c[0] in FR: continue
        if not re.match(r'^(Must|Should|Could|Won)', c[2]): continue
        FR[c[0]] = dict(id=c[0], text=c[1], moscow=c[2], release=c[3], trace=c[4], rc=c[5], problem=c[6] if len(c) > 6 else '')
ver = {}
for c in rows(fr_txt, 'FR-', ncols=3):
    ver[c[0]] = dict(method=c[1], cls=c[2])
for k, v in FR.items():
    v['verification'] = ver.get(k, {}).get('method', ''); v['class'] = ver.get(k, {}).get('cls', '')
    v['brs'] = ids(v['trace'], r'BR-\d+'); v['sucs'] = ids(v['trace'], r'SUC-\d+'); v['nfrs'] = ids(v['trace'], r'(?<!P)NFR-\d+')
    v['rcs'] = ids(v['rc'], r'RC-\d+')
    v['cap'] = k.split('-')[1]
M['FR'] = FR
# ---- PNFR ----
PN = {}
for c in rows(rd(D('09-initial-prd/nfrs.md')), 'PNFR-', minc=7):
    PN[c[0]] = dict(id=c[0], category=c[1], text=c[2], target=c[3], trace=c[4], evclass=c[5], release=c[6], nfrs=ids(c[4], r'NFR-\d+'))
M['PNFR'] = PN
# ---- Stage 3 / 6 upstream ----
def reg(path, pfx, mc=2):
    d = {}
    for c in rows(rd(D(path)), pfx, minc=mc):
        if re.match(r'^[A-Z]+-\d+$', c[0]) and c[0] not in d: d[c[0]] = dict(id=c[0], text=c[1], cols=c)
    return d
BR = reg('03-problem-value/business-requirements.md', 'BR-', 3)
for k in BR: BR[k]['moscow'] = BR[k]['cols'][2]
SUC = reg('03-problem-value/success-criteria.md', 'SUC-')
NFR = reg('03-problem-value/nfrs.md', 'NFR-')
RC = reg('06-root-cause/confirmed-root-causes.md', 'RC-')
for d in (BR, SUC, NFR, RC):
    for v in d.values(): v.pop('cols', None)
M.update(BR=BR, SUC=SUC, NFR=NFR, RC=RC)
# ---- SBR ----
SBR = {}
for c in rows(rd(D('12-specs/business-rules.md')), 'SBR-', minc=3):
    sid = re.match(r'SBR-[A-Z]+-\d+', c[0]).group(0)
    SBR[sid] = dict(id=sid, param='[PARAM]' in c[0], text=c[1], impl=c[2], frs=ids(c[2], r'FR-[A-Z]+-\d+'), pnfrs=ids(c[2], r'PNFR-\d+'), brs=ids(c[2], r'BR-\d+'), rcs=ids(c[2], r'RC-\d+'))
M['SBR'] = SBR
# ---- BEH ----
BEH = {}
for f in sorted(glob.glob(D('12-specs/features/*.md'))) + [D('12-specs/observability-spec.md')]:
    for c in rows(rd(f), 'BEH-', minc=3):
        if c[0] in BEH: continue
        BEH[c[0]] = dict(id=c[0], text=c[1], req=c[-1], frs=ids(c[-1], r'FR-[A-Z]+-\d+'), pnfrs=ids(c[-1], r'PNFR-\d+'), feature=('OBS' if 'observability' in f else os.path.basename(f)[:3].upper()), file=os.path.basename(f))
M['BEH'] = BEH
# ---- AC (ACC-7) ----
ac_txt = rd(D('12-specs/acceptance-criteria.md'))
AC = {}
for c in rows(ac_txt, 'AC-', ncols=7):
    AC[c[0]] = dict(id=c[0], given=c[1], when=c[2], then=c[3], impl=c[4], kind=c[5], file=c[6], prefix=c[0].split('-')[1],
                    frs=ids(c[4], r'FR-[A-Z]+-\d+'), pnfrs=ids(c[4], r'PNFR-\d+'), behs=ids(c[4], r'BEH-[A-Z]+-\d+'),
                    sbrs=ids(c[4], r'SBR-[A-Z]+-\d+'), brs=ids(c[4], r'(?<![A-Z])BR-\d+'), rcs=ids(c[4], r'RC-\d+'),
                    cts=sorted(expand_range(' '.join(c[1:4]))), ods=ids(' '.join(c[1:5]), r'OD-S12-\d+'))
M['AC'] = AC
# ACC-4 / ACC-5 tables (spec's own forward map) for cross-check
acc4 = {c[0]: ids(c[3], r'AC-[A-Z]+-\d+') for c in rows(ac_txt, 'FR-', ncols=4)}
acc5 = {c[0]: ids(c[1], r'AC-[A-Z]+-\d+') for c in rows(ac_txt, 'PNFR-', ncols=2)}
acc6 = {c[0]: ids(c[1], r'AC-[A-Z]+-\d+') for c in rows(ac_txt, 'BEH-', ncols=2)}
M['ACC4'], M['ACC5'], M['ACC6'] = acc4, acc5, acc6
# ---- OP ----
api = rd(D('12-specs/api-contracts.md'))
OP = {}
for c in rows(api, 'OP-', ncols=9 if False else None, minc=7):
    if len(c) >= 7 and c[0] not in OP:
        OP[c[0]] = dict(id=c[0], route=c[1], roles=c[2], purpose=c[3], errors=c[6], behs=ids(c[3], r'BEH-[A-Z]+-\d+'))
for c in rows(api, 'OP-', ncols=3):
    if c[0] in OP: OP[c[0]].update(frs=ids(c[1], r'FR-[A-Z]+-\d+'), release=c[2])
M['OP'] = OP
# ---- EV, SCH, E- codes ----
EV = {c[0]: dict(id=c[0], name=c[1], frs=ids(c[-1], r'FR-[A-Z]+-\d+'), pnfrs=ids(c[-1], r'PNFR-\d+')) for c in rows(rd(D('12-specs/event-contracts.md')), 'EV-', minc=6)}
SCH = {c[0]: dict(id=c[0], table=c[1], shape=c[2], frs=ids(c[-1], r'FR-[A-Z]+-\d+'), pnfrs=ids(c[-1], r'PNFR-\d+')) for c in rows(rd(D('12-specs/schema-specifications.md')), 'SCH-', minc=4)}
ERR = {c[0]: dict(id=c[0], http=c[1], feature=c[4]) for c in rows(rd(D('12-specs/error-handling-spec.md')), 'E-', minc=6)}
M.update(EV=EV, SCH=SCH, ERR=ERR)
# SEC threats
sec = rd(D('12-specs/security-spec.md'))
M['SEC'] = {c[0]: dict(id=c[0], threat=c[1], control=c[2], reqs=c[3], frs=ids(c[3], r'FR-[A-Z]+-\d+'), pnfrs=ids(c[3], r'PNFR-\d+'), brs=ids(c[3], r'(?<![A-Z])BR-\d+')) for c in rows(sec, 'SEC-', minc=5)}
# ---- CT (Stage 7) ----
CT = {}
for c in rows(rd(D('07-repo-assessment/characterization-test-plan.md')), 'CT-', minc=8):
    if re.match(r'CT-\d\d$', c[0]):
        CT[c[0]] = dict(id=c[0], workflow=c[1], pins=c[2], golden=c[3], type=c[4], pri=c[5], covered=c[6])
M['CT'] = CT
# ---- Open decisions OD-S12 ----
rd_txt = rd(D('12-specs/spec-readiness.md'))
M['OD'] = {c[0]: dict(id=c[0], decision=c[1], needed_before=c[-3] if len(c) > 6 else '') for c in rows(rd_txt, 'OD-S12-', minc=6)}
# DV deviations
f10 = rd(D('12-specs/features/f10-coexistence-change-safety.md'))
M['DV'] = {c[0]: dict(id=c[0], text=c[1], disposition=c[3]) for c in rows(f10, 'DV-', minc=4)}
# Stage 3 mentions in FR 'BR coverage' section for cross-check
os.makedirs(out, exist_ok=True)
json.dump(M, open(os.path.join(out, 'trace_model.json'), 'w'), indent=1, sort_keys=True)
print({k: len(v) for k, v in M.items()})
