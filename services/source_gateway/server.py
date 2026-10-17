"""Local enterprise source-system simulator. No external network dependency."""
import os, json, datetime, urllib.parse, sqlite3, hashlib
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[2]
CFG=json.loads((ROOT/'integration'/'source-gateway.json').read_text())
DB=Path(os.environ.get('LEGACY_DB',str(ROOT/'data'/'legacy.sqlite3')))
class Handler(BaseHTTPRequestHandler):
    def reply(self,n,v):
        b=json.dumps(v,default=str).encode();self.send_response(n);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        u=urllib.parse.urlsplit(self.path); q=urllib.parse.parse_qs(u.query)
        if u.path=='/health':return self.reply(200,{'status':'ok','service':'source-gateway','domain':CFG['domain']})
        if u.path=='/api/catalog':return self.reply(200,CFG)
        if u.path=='/api/events':
            try: limit=min(200,max(1,int(q.get('limit',['50'])[0])));offset=max(0,int(q.get('offset',['0'])[0]));source=q.get('source',[''])[0]
            except ValueError:return self.reply(400,{'error':'bad pagination'})
            if source and source not in CFG['sources']:return self.reply(400,{'error':'unknown source'})
            # Historical upstream events intentionally include repeated and delayed publication.
            with sqlite3.connect(f'file:{DB}?mode=ro',uri=True) as con:
                con.row_factory=sqlite3.Row
                rows=con.execute('SELECT id FROM '+CFG['parent_table']+' ORDER BY id LIMIT ? OFFSET ?', (limit,offset)).fetchall() if False else con.execute('SELECT '+CFG['parent_key']+' FROM '+CFG['parent_table']+' ORDER BY '+CFG['parent_key']+' LIMIT ? OFFSET ?', (limit,offset)).fetchall()
            records=[]
            for i,r in enumerate(rows):
                key=r[0];src=source or CFG['sources'][(offset+i)%len(CFG['sources'])];typ=CFG['event_types'][(offset+i)%len(CFG['event_types'])];uid=hashlib.sha256((src+key+typ).encode()).hexdigest()[:24]
                records.append({'message_id':uid,'business_key':key,'system':src,'event_type':typ,'schema_version':'1.0' if (offset+i)%19 else '0.9','occurred_at':f'2025-03-{1+(offset+i)%28:02d}T{(offset+i)%24:02d}:00:00Z','published_at':f'2025-03-{1+(offset+i)%28:02d}T{((offset+i)+2)%24:02d}:15:00Z','payload':{'identifier':key,'note':'legacy operational note','source_status':'OPEN' if i%5 else 'HOLD'}})
            return self.reply(200,{'items':records,'count':len(records),'next_offset':offset+len(records)})
        if u.path.startswith('/api/record/'):
            key=u.path.rsplit('/',1)[-1]
            with sqlite3.connect(f'file:{DB}?mode=ro',uri=True) as con:
                con.row_factory=sqlite3.Row
                row=con.execute('SELECT * FROM '+CFG['parent_table']+' WHERE '+CFG['parent_key']+'=?',(key,)).fetchone()
            return self.reply(200,{'record':dict(row),'system':CFG['sources'][0]}) if row else self.reply(404,{'error':'not found'})
        if u.path=='/api/failure':
            mode=q.get('mode',['normal'])[0]
            if mode=='timeout':return self.reply(503,{'error':'upstream unavailable','retryable':True})
            if mode=='schema':return self.reply(200,{'unexpected_schema':'v3','records':None})
            if mode=='rate_limit':return self.reply(429,{'error':'source throttle','retryable':True})
            return self.reply(200,{'mode':'normal'})
        return self.reply(404,{'error':'not found'})
    def log_message(self,*args):pass
def main():
    ThreadingHTTPServer((os.getenv('HOST','127.0.0.1'),int(os.getenv('SOURCE_PORT','8090'))),Handler).serve_forever()
if __name__=='__main__':main()
