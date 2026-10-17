"""Existing legacy message bridge. Persists idempotency attempts, source offsets and raw evidence."""
import argparse,json,hashlib,sqlite3,os,urllib.request,urllib.error,datetime
from pathlib import Path
from .store import connect,setup
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'integration'/'source-gateway.json').read_text())
def init():
    setup()
    with connect() as c:
        c.executescript("""CREATE TABLE IF NOT EXISTS gateway_inbox(message_id TEXT PRIMARY KEY, external_ref TEXT NOT NULL, source_system TEXT NOT NULL, event_type TEXT NOT NULL, event_time TEXT NOT NULL, received_at TEXT NOT NULL, raw_payload TEXT NOT NULL, status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS gateway_checkpoints(stream TEXT PRIMARY KEY, next_offset INTEGER NOT NULL DEFAULT 0, last_sync TEXT);
CREATE INDEX IF NOT EXISTS idx_gateway_ref ON gateway_inbox(external_ref);""")
def apply(events,stream='primary'):
    init(); result={'accepted':0,'duplicates':0,'invalid':0,'received':len(events)}
    with connect() as c:
        for e in events:
            if not isinstance(e,dict) or not all(e.get(k) for k in ('message_id','business_key','system','event_type','occurred_at')):
                result['invalid']+=1;continue
            present=c.execute('SELECT 1 FROM '+CFG['parent_table']+' WHERE '+CFG['parent_key']+'=?',(e['business_key'],)).fetchone()
            if not present:
                result['invalid']+=1;continue
            try:
                c.execute('INSERT INTO gateway_inbox VALUES(?,?,?,?,?,?,?,?)',(e['message_id'],e['business_key'],e['system'],e['event_type'],e['occurred_at'],datetime.datetime.now(datetime.timezone.utc).isoformat(),json.dumps(e,sort_keys=True),'RECEIVED'))
                result['accepted']+=1
            except sqlite3.IntegrityError:result['duplicates']+=1
    return result
def pull(url,offset=0,limit=40,stream='primary'):
    init()
    with urllib.request.urlopen(url+'/api/events?offset='+str(offset)+'&limit='+str(limit),timeout=5) as response:
        doc=json.load(response)
    report=apply(doc['items'],stream)
    with connect() as c:
        c.execute('INSERT INTO gateway_checkpoints(stream,next_offset,last_sync) VALUES(?,?,?) ON CONFLICT(stream) DO UPDATE SET next_offset=excluded.next_offset,last_sync=excluded.last_sync',(stream,doc['next_offset'],datetime.datetime.now(datetime.timezone.utc).isoformat()))
    return report
def main():
    pa=argparse.ArgumentParser();pa.add_argument('--source-url',default=os.environ.get('SOURCE_URL','http://127.0.0.1:8090'));pa.add_argument('--limit',type=int,default=50);pa.add_argument('--offset',type=int,default=None);x=pa.parse_args()
    init()
    with connect() as c:
        row=c.execute("SELECT next_offset FROM gateway_checkpoints WHERE stream='primary'").fetchone()
    offset=x.offset if x.offset is not None else (row[0] if row else 0)
    print(json.dumps(pull(x.source_url,offset,x.limit)))
if __name__=='__main__':main()
