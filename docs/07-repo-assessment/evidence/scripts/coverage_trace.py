"""Stdlib 'trace' line coverage of the existing unittest suite (coverage.py not installed). Run inside sandbox copy only."""
import trace,sys,os,unittest,json
root=os.getcwd();sys.path.insert(0,root)
tr=trace.Trace(count=1,trace=0,ignoredirs=[sys.prefix,sys.exec_prefix,'/usr/lib'])
def run():
    s=unittest.defaultTestLoader.discover('tests');r=unittest.TextTestRunner(verbosity=0).run(s);return r
r=tr.runfunc(run)
res=tr.results();counts=res.counts
rep={};tot=0;hit=0
for dp,dn,fn in os.walk(root):
    dn[:]=[d for d in dn if d not in('.git','data','docs','.fde','tests','__pycache__')]
    for f in fn:
        if not f.endswith('.py'):continue
        p=os.path.join(dp,f);ex=trace._find_executable_linenos(p)
        if not ex:continue
        h={l for (fp,l),c in counts.items() if os.path.abspath(fp)==os.path.abspath(p) and l in ex}
        rel=os.path.relpath(p,root);rep[rel]={'executable':len(ex),'hit':len(h),'pct':round(100*len(h)/len(ex),1),'missed_lines':sorted(set(ex)-h)[:60]};tot+=len(ex);hit+=len(h)
rep['__TOTAL__']={'executable':tot,'hit':hit,'pct':round(100*hit/tot,1)}
json.dump(rep,open(sys.argv[1],'w'),indent=1,sort_keys=True)
for k,v in sorted(rep.items()):print(f"{k:42} {v['hit']:4}/{v['executable']:4} {v['pct']:5}%")
print('tests ok:',r.wasSuccessful(),r.testsRun)
