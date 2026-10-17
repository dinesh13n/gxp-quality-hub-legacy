"""Apply each mutant (same set as mutation_probe.sh) to a sandbox copy and check whether the GOLDEN baseline (API + batch captures) detects it."""
import os,shutil,subprocess,sys,json
S=os.path.expanduser('~/fde_sbx/stage7');sys.path.insert(0,S)
M=[('M1','app/legacy_logic.py',"amount > 50000","amount > 1"),
('M2','app/legacy_logic.py',"if severity=='HIGH' or status=='ESCALATED': return 'review'","if False: return 'review'"),
('M3','app/legacy_logic.py',"return severity in ('HIGH','CRITICAL') or status in ('ESCALATED','REOPENED')","return False"),
('M4','app/legacy_logic.py',"if status=='CLOSED': return 'archive'","if False: return 'archive'"),
('M5','app/partner_feeds.py',"elif payload.get('quantity',0)<0:","elif False:"),
('M6','app/partner_feeds.py',"elif row['processing_status']=='REPLAY':","elif False:"),
('M7','app/partner_feeds.py',"if not key or row['schema_rev']=='unsupported':","if False:"),
('M8','legacy_batch/shift_reconciliation.py',"row['value']>row['threshold']","row['value']<row['threshold']"),
('M9','app/gateway_bridge.py',"if not present:","if False:"),
('M10','app/server.py',"r['manual_review_required']=manual_review_required(r['status'],r['severity'])","r['manual_review_required']=False"),
('M12','app/baseline.py',"'urgent_cases':sum(priority(r['status'],r['severity'],r['amount'])=='urgent' for r in data)","'urgent_cases':0"),
('M13','legacy_js/legacy_policy.js',"*1.05","*1.5"),
('M14','app/historical_estate.py',"if exists:return {'status':'already_imported','import_id':digest,'rows':0}","pass"),
('M15','services/source_gateway/server.py',"if mode=='timeout':return self.reply(503","if mode=='timeout':return self.reply(200")]
g_api=json.load(open(S+'/golden/api_golden_run1.json'));g_b=json.load(open(S+'/golden/batch_golden_run1.json'))
lo,hi=int(sys.argv[1]),int(sys.argv[2]);res=[]
for mid,f,a,b in M[lo:hi]:
    d=S+'/mutg';shutil.rmtree(d,ignore_errors=True);shutil.copytree(S+'/repo',d,symlinks=True)
    t=open(d+'/'+f).read();assert t.count(a)==1;open(d+'/'+f,'w').write(t.replace(a,b))
    env={**os.environ,'FDE_SRC':d}
    r1=subprocess.run([sys.executable,S+'/capture_api.py',d,S+'/golden/_m_api.json'],capture_output=True,text=True,env=env)
    r2=subprocess.run([sys.executable,S+'/capture_batch.py',S+'/golden/_m_batch.json'],capture_output=True,text=True,env=env)
    da=[];db=[]
    if r1.returncode==0:
        x=json.load(open(S+'/golden/_m_api.json'));da=[k for k in g_api['api'] if g_api['api'][k]!=x['api'].get(k)]+[k for k in g_api['gateway'] if g_api['gateway'][k]!=x['gateway'].get(k)]+(['api_all_cases_priority'] if g_api['api_all_cases_priority']!=x['api_all_cases_priority'] else [])
    else: da=['CAPTURE-ERROR '+r1.stderr[-150:]]
    if r2.returncode==0:
        y=json.load(open(S+'/golden/_m_batch.json'));db=[k for k in g_b if g_b[k]!=y.get(k)]
    else: db=['CAPTURE-ERROR '+r2.stderr[-150:]]
    res.append({'id':mid,'file':f,'killed_by_golden':bool(da or db),'api_diffs':da[:6],'batch_diffs':db[:6]})
    print(mid,'KILLED' if (da or db) else 'SURVIVED',da[:3],db[:3],flush=True)
json.dump(res,open(S+f'/evidence/golden_mutation_replay_{lo}_{hi}.json','w'),indent=1)
