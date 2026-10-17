"""Read-only validation of every preloaded synthetic fixture (no generation)."""
from pathlib import Path
import sqlite3,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'data'
DBS=[BASE/'legacy.sqlite3',BASE/'enterprise_legacy.sqlite3',BASE/'lake/tiny/reference.sqlite3',BASE/'lake/tiny/finance.sqlite3',BASE/'lake/bundled/reference.sqlite3',BASE/'lake/bundled/finance.sqlite3']
errors=[];detail={}
for db in DBS:
 name=str(db.relative_to(ROOT))
 if not db.exists() or db.stat().st_size==0:errors.append('missing/empty '+name);continue
 try:
  with sqlite3.connect(f'file:{db.as_posix()}?mode=ro',uri=True) as c:
   integrity=c.execute('PRAGMA integrity_check').fetchone()[0]
   fk=c.execute('PRAGMA foreign_key_check').fetchall()
   tables=c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
   counts={t[0]:c.execute('SELECT COUNT(*) FROM "'+t[0].replace('"','""')+'"').fetchone()[0] for t in tables}
   detail[name]={'tables':counts,'integrity':integrity,'foreign_key_errors':len(fk)}
   if integrity!='ok' or fk or not any(counts.values()):errors.append('invalid '+name)
 except Exception as e:errors.append(name+':'+str(e))
for tier in ('tiny','bundled'):
 folder=BASE/'lake'/tier
 try:
  m=json.loads((folder/'manifest.json').read_text()); csv=folder/'partner_export.csv'
  sha=hashlib.sha256(csv.read_bytes()).hexdigest()
  events=sum(1 for f in (folder/'events').glob('*.jsonl') for _ in f.open(encoding='utf-8'))
  docs=len(list((folder/'documents').glob('DOC-*.json')))
  transactions=sum(1 for _ in csv.open(encoding='utf-8'))-1
  detail[tier]={'transactions':transactions,'events':events,'documents':docs,'manifest':m}
  if (transactions,events,docs)!=(m['transaction_rows'],m['event_rows'],m['documents']):errors.append('count mismatch '+tier)
  if sha!=m['sha256_partner_export']:errors.append('sha mismatch '+tier)
 except Exception as e: errors.append(tier+':'+str(e))
for folder,mincount in [('documents',1),('archive_documents',1)]:
 p=BASE/folder;count=sum(1 for f in p.rglob('*') if f.is_file()); detail[folder]=count
 if count<mincount:errors.append('missing documents '+folder)
print(json.dumps({'ready':not errors,'problems':errors,'inventory':detail},indent=2,default=str))
sys.exit(bool(errors))
