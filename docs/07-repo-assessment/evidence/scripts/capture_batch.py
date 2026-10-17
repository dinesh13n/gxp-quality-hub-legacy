"""Stage 7 golden capture of batch/CLI/library behaviour. SANDBOX ONLY (each mutating step uses its own fresh copy)."""
import json,os,subprocess,sys,shutil,sqlite3,hashlib,socket,time,itertools,urllib.request
S=os.path.expanduser('~/fde_sbx/stage7');SRC=os.environ.get('FDE_SRC',S+'/repo');OUT=sys.argv[1]
ENV={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'}
for k in ('LEGACY_DB','HOST','PORT'):ENV.pop(k,None)
def fresh(name):
    d=f'{S}/{name}';shutil.rmtree(d,ignore_errors=True);shutil.copytree(SRC,d,symlinks=True);return d
def sh(args,cwd,env=None):
    r=subprocess.run(args,cwd=cwd,env=env or ENV,capture_output=True,text=True,timeout=170)
    return {'cmd':' '.join(args),'rc':r.returncode,'stdout':r.stdout,'stderr':r.stderr[-800:]}
def tblhash(db,tables=None,order=True):
    c=sqlite3.connect(f'file:{db}?mode=ro',uri=True)
    names=tables or [r[0] for r in c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by 1")]
    out={}
    for t in names:
        cols=[r[1] for r in c.execute(f'pragma table_info("{t}")')]
        rows=sorted(map(repr,c.execute(f'select * from "{t}"')))
        out[t]={'rows':len(rows),'sha256':hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16]}
    return out
G={}
# 1 decision functions
sys.path.insert(0,SRC)
from app.legacy_logic import priority,manual_review_required
st=['OPEN','UNDER_REVIEW','CLOSED','ESCALATED','REOPENED'];sv=['LOW','MEDIUM','HIGH','CRITICAL'];am=[0,1,50000,50000.01,99999,-1]
G['priority_truth_table']=[[a,b,c,priority(a,b,c)] for a in st for b in sv for c in am]
G['manual_review_truth_table']=[[a,b,manual_review_required(a,b)] for a in st for b in sv]
# 2 baseline + operational report on pristine
d=fresh('c_base');G['app.baseline']=sh([sys.executable,'-m','app.baseline'],d);G['app.operational_report']=sh([sys.executable,'-m','app.operational_report'],d)
G['pristine_db_after_readonly_cli']=hashlib.sha256(open(d+'/data/legacy.sqlite3','rb').read()).hexdigest()
# 3 partner feeds reconcile sequence
d=fresh('c_rec');seq=[]
for i in range(12):
    r=sh([sys.executable,'-m','app.partner_feeds','--reconcile'],d);seq.append(r['stdout'].strip())
    if json.loads(r['stdout'])=={'accepted':0,'rejected':0,'duplicate':0,'skipped':0}:break
G['partner_reconcile_sequence']=seq
c=sqlite3.connect(d+'/data/legacy.sqlite3')
G['partner_status_after_all']=c.execute('select processing_status,count(*) from partner_feeds group by 1 order by 1').fetchall()
G['partner_error_reasons']=c.execute('select error_reason,count(*) from partner_feeds group by 1 order by 1').fetchall()
G['partner_batch_runs_rows_after_reconcile']=c.execute('select count(*) from batch_runs').fetchone()[0]
# 4 partner feed regeneration vs shipped
d=fresh('c_regen');r=sh([sys.executable,'-m','app.partner_feeds'],d);G['partner_regen_default']=r
a=tblhash(SRC+'/data/legacy.sqlite3',['partner_feeds','reference_versions','policy_exceptions','upstream_outages','batch_runs']);b=tblhash(d+'/data/legacy.sqlite3',['partner_feeds','reference_versions','policy_exceptions','upstream_outages','batch_runs'])
G['partner_regen_equals_shipped']={t:(a[t]==b[t]) for t in a};G['partner_regen_hashes']={'shipped':a,'regen':b}
# 5 cases regeneration: which (count,seed) reproduces shipped?
G['cases_regen_match']={}
for cnt,seed in [(125,4100),(125,4326),(6000,4326)]:
    dd=fresh('c_gen');r=sh([sys.executable,'-m','app.generate','--count',str(cnt),'--seed',str(seed),'--reset'],dd)
    h=tblhash(dd+'/data/legacy.sqlite3',['cases','events','source_messages','operating_costs','materials','batch_records','deviations','lab_results','capa_actions','sop_versions'])
    ship=tblhash(SRC+'/data/legacy.sqlite3',['cases','events','source_messages','operating_costs','materials','batch_records','deviations','lab_results','capa_actions','sop_versions'])
    G['cases_regen_match'][f'{cnt}/{seed}']={'rc':r['rc'],'stdout':r['stdout'].strip()[:400],'stderr':r['stderr'][-200:],'equals_shipped':{t:h[t]==ship[t] for t in h},'hashes':h}
    if cnt==6000:
        G['baseline_6000_seed4326']=sh([sys.executable,'-m','app.baseline'],dd)
        G['operational_report_6000']=sh([sys.executable,'-m','app.operational_report'],dd)
G['cases_shipped_hashes']=ship
# 6 gateway bridge against local gateway
d=fresh('c_gw');port=socket.socket();port.bind(('127.0.0.1',0));p=port.getsockname()[1];port.close()
env={**ENV,'HOST':'127.0.0.1','SOURCE_PORT':str(p)}
srv=subprocess.Popen([sys.executable,'-m','services.source_gateway.server'],cwd=d,env=env,stderr=subprocess.DEVNULL)
try:
    for _ in range(80):
        try: urllib.request.urlopen(f'http://127.0.0.1:{p}/health',timeout=1).read();break
        except Exception: time.sleep(.1)
    seqb=[]
    for args in (['--limit','50'],['--limit','50'],['--limit','50','--offset','0'],['--limit','200','--offset','0'],['--limit','50']):
        r=sh([sys.executable,'-m','app.gateway_bridge','--source-url',f'http://127.0.0.1:{p}']+args,d);seqb.append({'args':args,'rc':r['rc'],'out':r['stdout'].strip(),'err':r['stderr'][-200:]})
    G['gateway_bridge_sequence']=seqb
    c=sqlite3.connect(d+'/data/legacy.sqlite3')
    G['gateway_inbox_after']=c.execute('select count(*),count(distinct external_ref),sum(status="RECEIVED") from gateway_inbox').fetchone()
    G['gateway_inbox_event_type_counts']=c.execute('select event_type,count(*) from gateway_inbox group by 1 order by 1').fetchall()
    G['gateway_checkpoint']=c.execute('select stream,next_offset from gateway_checkpoints').fetchall()
    G['gateway_schema_0.9_events_stored']=c.execute("select count(*) from gateway_inbox where raw_payload like '%\"schema_version\"%0.9%'").fetchone()[0]
    # events returned by gateway beyond table size (offset past end)
    G['gateway_offset_past_end']=json.loads(urllib.request.urlopen(f'http://127.0.0.1:{p}/api/events?offset=5000&limit=5').read())
    # bridge with failure endpoint url (non-JSON/err)
    G['gateway_unreachable']=sh([sys.executable,'-m','app.gateway_bridge','--source-url','http://127.0.0.1:1'],d)
finally: srv.terminate()
# 7 vendor file import
d=fresh('c_imp');imp=[]
for f in ('data/lake/tiny/partner_export.csv','data/lake/tiny/partner_export.csv'):
    r=sh([sys.executable,'-m','app.historical_estate',f],d);imp.append(r['stdout'].strip() or r['stderr'])
G['historical_estate_import_on_shipped_db']=imp
d=fresh('c_imp2');c=sqlite3.connect(d+'/data/legacy.sqlite3');c.execute('delete from vendor_file_rows');c.execute('delete from vendor_file_imports');c.commit();c.close()
r1=sh([sys.executable,'-m','app.historical_estate','data/lake/tiny/partner_export.csv'],d);r2=sh([sys.executable,'-m','app.historical_estate','data/lake/tiny/partner_export.csv'],d)
G['historical_estate_import_on_cleared_tables']=[r1['stdout'].strip(),r2['stdout'].strip()]
c=sqlite3.connect(d+'/data/legacy.sqlite3')
G['vendor_rows_after']=c.execute('select count(*),sum(amount_text=""),count(distinct tenant) from vendor_file_rows').fetchone()
G['vendor_import_id_shipped']=sqlite3.connect(SRC+'/data/legacy.sqlite3').execute('select id,source_file,count,state from vendor_file_imports').fetchall()
# 8 night shift reconciliation
d=fresh('c_shift');sr={}
for lim in (500,100,50,12500):
    r=sh([sys.executable,'-m','legacy_batch.shift_reconciliation','--limit',str(lim)],d);sr[str(lim)]=json.loads(r['stdout']) if r['rc']==0 else r
G['shift_reconciliation']=sr
c=sqlite3.connect(f'file:{SRC}/data/enterprise_legacy.sqlite3?mode=ro',uri=True)
G['shift_distinct_objects_in_first_500_joined_rows']=c.execute('select count(distinct object_id) from (select x.object_id from operational_objects x left join policy_register p on p.region=x.region and p.active=1 order by x.object_id limit 500)').fetchone()[0]
G['shift_active_policies_per_region']=c.execute('select region,count(*) from policy_register where active=1 group by 1 order by 1').fetchall()
# 9 java + node
d=fresh('c_jvm')
G['java_tiny']=sh(['java','legacy_java/ReconcileLegacy.java','data/lake/tiny/partner_export.csv'],d)
G['java_bundled']=sh(['java','legacy_java/ReconcileLegacy.java','data/lake/bundled/partner_export.csv'],d)
G['java_noargs']=sh(['java','legacy_java/ReconcileLegacy.java'],d)
G['node_default']=sh(['node','legacy_js/legacy_policy.js'],d)
G['node_cwd_other']=sh(['node',d+'/legacy_js/legacy_policy.js'],'/tmp')
# python reference computation of the CSV total for comparison (float vs decimal)
import csv,decimal
for tier in ('tiny','bundled'):
    tot=0.0;dec=decimal.Decimal(0);n=0;blank=0;bad=0;neg=0
    for row in csv.reader(open(f'{SRC}/data/lake/{tier}/partner_export.csv',encoding='utf-8')):
        if row[0]=='tenant':continue
        try: v=float(row[4]);tot+=v;dec+=decimal.Decimal(row[4]);n+=1;neg+=v<0
        except Exception: blank+=1
    G[f'csv_reference_{tier}']={'summed_rows':n,'unparsable_rows':blank,'negative_rows':neg,'float_total':round(tot,2),'decimal_total':str(dec.quantize(decimal.Decimal('0.01')))}
# 10 JS policy table via node
js='''const p=require("./legacy_js/legacy_policy.js");const fs=require("fs");const pol=JSON.parse(fs.readFileSync("contracts/decision-policies-archive.json","utf8"));
const regs=[...new Set(pol.historical_versions.map(v=>v.region)).add("IN").add("EMEA").add("AMER")];const out={versions:pol.historical_versions.map(v=>[v.region,v.effective_from,v.limit]),keys:Object.keys(pol),table:[]};
for(const r of regs)for(const y of [2019,2021,2022,2023,2024,2025,2026,2027])out.table.push([r,y,p.threshold(r,y)]);
out.allows=[];for(const [a,r,y] of [[27000,"APAC",2026],[26250,"APAC",2026],[26250.01,"APAC",2026],[1e6,"IN",2026],[1e6,"APAC",2021],[0,"APAC",2026],[-5,"APAC",2026],["abc","APAC",2026],[null,"APAC",2026]])out.allows.push([a,r,y,p.legacyAllows(a,r,y)]);
console.log(JSON.stringify(out));'''
r=sh(['node','-e',js],d);G['js_policy_table']=json.loads(r['stdout']) if r['rc']==0 else r
# 11 SQL reports
c=sqlite3.connect(f'file:{SRC}/data/legacy.sqlite3?mode=ro',uri=True)
G['sql_report_1']=c.execute("SELECT c.region, c.status, count(DISTINCT c.id) as cases, round(sum(c.amount),2) as gross_amount FROM cases c LEFT JOIN events e ON e.case_id=c.id GROUP BY c.region,c.status ORDER BY gross_amount DESC").fetchall()
G['sql_report_1_total_gross']=c.execute("select round(sum(g),2) from (SELECT sum(c.amount) g FROM cases c LEFT JOIN events e ON e.case_id=c.id GROUP BY c.region,c.status)").fetchone()[0]
G['true_total_amount']=c.execute("select round(sum(amount),2) from cases").fetchone()[0]
G['sql_report_2']=c.execute("SELECT message_kind, tenant, COUNT(*) AS rows_received FROM vendor_file_rows GROUP BY message_kind,tenant").fetchall()
# 12 other generators: enterprise_legacy default and historical_fixture tiny to temp, archived docs / documents (sandbox)
d=fresh('c_gen2')
G['enterprise_legacy_regen']=sh([sys.executable,'-m','app.enterprise_legacy'],d)
a=tblhash(SRC+'/data/enterprise_legacy.sqlite3');b=tblhash(d+'/data/enterprise_legacy.sqlite3');G['enterprise_legacy_regen_equals_shipped']={t:a[t]==b[t] for t in a};G['enterprise_legacy_shipped_hashes']=a
tmp=S+'/c_gen2/_tiny_out';sh([sys.executable,'-m','app.historical_fixture','--tier','tiny','--destination',tmp],d)
G['historical_fixture_tiny_manifest_equal_shipped']=json.load(open(tmp+'/manifest.json'))==json.load(open(SRC+'/data/lake/tiny/manifest.json'))
import filecmp
G['historical_fixture_tiny_csv_equal_shipped']=filecmp.cmp(tmp+'/partner_export.csv',SRC+'/data/lake/tiny/partner_export.csv',shallow=False)
G['historical_fixture_tiny_events_equal']=all(filecmp.cmp(f'{tmp}/events/{f}',f'{SRC}/data/lake/tiny/events/{f}',shallow=False) for f in os.listdir(tmp+'/events'))
for sub in ('reference','finance'):
    G[f'historical_fixture_tiny_{sub}_table_equal']=tblhash(f'{tmp}/{sub}.sqlite3')==tblhash(f'{SRC}/data/lake/tiny/{sub}.sqlite3')
before=hashlib.sha256(b''.join(sorted(open(f,'rb').read() for f in __import__('glob').glob(SRC+'/data/archive_documents/*')))).hexdigest()
G['archived_documents_regen']=sh([sys.executable,'-m','app.archived_documents'],d)
after=hashlib.sha256(b''.join(sorted(open(f,'rb').read() for f in __import__('glob').glob(d+'/data/archive_documents/*')))).hexdigest()
G['archived_documents_regen_equals_shipped']=(before==after)
G['archived_documents_file_counts']={'shipped':len(os.listdir(SRC+'/data/archive_documents')),'regen':len(os.listdir(d+'/data/archive_documents'))}
G['generate_documents_regen']=sh([sys.executable,'-m','app.generate_documents'],d)
G['generate_documents_equals_shipped']=filecmp.cmp(d+'/data/documents/source_documents.jsonl',SRC+'/data/documents/source_documents.jsonl',shallow=False)
# 13 workshop_check
d=fresh('c_wc');G['workshop_check']=sh([sys.executable,'-m','app.workshop_check'],d);G['workshop_check_empty_db']=sh([sys.executable,'-m','app.workshop_check'],d,env={**ENV,'LEGACY_DB':d+'/empty.sqlite3'})
G['server_on_empty_db_cases_route']=None
json.dump(G,open(OUT,'w'),indent=1,sort_keys=True,default=str)
print('ok',len(G))
