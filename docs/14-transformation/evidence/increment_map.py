"""Stage 14: assign Stage 13 planned tests to Stage 15 increments (documentation helper; reads CSVs only)."""
import csv, collections, sys, os
root = sys.argv[1]; out = sys.argv[2]
tp = list(csv.DictReader(open(os.path.join(root, 'docs/13-traceability/evidence/tests_plan.csv'))))
rtm = {r['id']: r for r in csv.DictReader(open(os.path.join(root, 'docs/13-traceability/evidence/rtm.csv')))}
PREFIX = {'CO':'INC-02','SEC':'INC-03','POL':'INC-04','DEC':'INC-05','ID':'INC-05','INT':'INC-06',
          'RUN':'INC-07','MET':'INC-07','OBS':'INC-07','GATE':'INC-08','REV':'INC-08','NFR':'INC-08'}
CO_OVR = {'TST-CO-03':'INC-04','TST-CO-10':'INC-03','TST-CO-15':'INC-03','TST-CO-09':'INC-06','TST-CO-08':'INC-08'}
rows=[]
for t in tp:
    p = t['test_id'].split('-')[1]
    reqs = [q for q in t['req'].split(';') if q]
    rel = sorted({rtm[q]['release'] for q in reqs if q in rtm}) or ['?']
    inc = CO_OVR.get(t['test_id'], PREFIX[p])
    why = 'prefix'
    if t['test_id'] in CO_OVR: why = 'override (dependency)'
    if rel == ['R2']:
        inc, why = 'INC-09', 'R2-only requirement'
    elif t['level'] in ('api','ui/manual-walkthrough') and inc not in ('INC-08','INC-09'):
        inc, why = 'INC-08', 'needs HTTP/UI surface (C1)'
    rows.append({'test_id':t['test_id'],'ac':t['ac'],'level':t['level'],'evidence_class':t['evidence_class'][:1],
                 'open_decision':t['class_note'] if t['evidence_class'].startswith('B') else '',
                 'release':'/'.join(rel),'increment':inc,'assignment_rule':why,'status':'PLANNED / NOT-RUN'})
with open(out,'w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
c = collections.Counter(r['increment'] for r in rows)
cb = collections.Counter((r['increment'], r['evidence_class']) for r in rows)
print('total', len(rows))
for inc in sorted(c):
    print(inc, c[inc], 'A=%d B=%d C=%d' % (cb[(inc,'A')], cb[(inc,'B')], cb[(inc,'C')]),
          'B-decisions:', ','.join(sorted({r['open_decision'] for r in rows if r['increment']==inc and r['open_decision']})))
