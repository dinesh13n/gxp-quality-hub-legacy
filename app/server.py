import json, os, sys, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .store import connect, setup
from .legacy_logic import priority, manual_review_required
CFG=json.loads((Path(__file__).resolve().parents[1]/'domain.json').read_text())
class Handler(BaseHTTPRequestHandler):
    def respond(self,status,data):
        payload=json.dumps(data,default=str).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
    def do_GET(self):
        u=urllib.parse.urlsplit(self.path);q=urllib.parse.parse_qs(u.query)
        if u.path=='/health':return self.respond(200,{'status':'ok','service':CFG['slug']})
        if u.path=='/':return self.respond(200,{'service':CFG['slug'],'routes':['/health','/api/cases?limit=20','/api/cases/C00000001','/api/metrics','/api/incidents']})
        if u.path=='/api/incidents':return self.respond(200,{'incidents':[{'id':'INC-2019-0082','summary':CFG['legacy_incident'],'state':'investigating'}]})
        if u.path=='/api/metrics':
            with connect() as c:
                total=c.execute('SELECT COUNT(*) FROM cases').fetchone()[0]
                statuses=[dict(r) for r in c.execute('SELECT status,COUNT(*) count FROM cases GROUP BY status')]
                monthly=[dict(r) for r in c.execute('SELECT * FROM operating_costs ORDER BY period')]
            return self.respond(200,{'total_cases':total,'by_status':statuses,'monthly_operating_costs':monthly})
        if u.path.startswith('/api/partners/'):
            table=u.path.rsplit('/',1)[-1]
            allowed={'partner_feeds','reference_versions','policy_exceptions','upstream_outages','batch_runs'}
            if table not in allowed:return self.respond(404,{'error':'unknown partner resource'})
            from .partner_feeds import init
            init()
            try:limit=max(1,min(100,int(q.get('limit',['20'])[0])));offset=max(0,int(q.get('offset',['0'])[0]))
            except ValueError:return self.respond(400,{'error':'invalid pagination'})
            with connect() as c:
                rows=[dict(x) for x in c.execute('SELECT * FROM '+table+' LIMIT ? OFFSET ?',(limit,offset))]
                total=c.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
            return self.respond(200,{'resource':table,'total':total,'items':rows})
        if u.path.startswith('/api/domain/'):
            table=u.path.rsplit('/',1)[-1]
            from .enterprise_data import TABLES
            allowed={t for t,_ in TABLES}
            if table not in allowed:return self.respond(404,{'error':'unknown domain resource'})
            try:limit=max(1,min(100,int(q.get('limit',['20'])[0])));offset=max(0,int(q.get('offset',['0'])[0]))
            except ValueError:return self.respond(400,{'error':'invalid pagination'})
            with connect() as c:
                rows=[dict(x) for x in c.execute('SELECT * FROM '+table+' LIMIT ? OFFSET ?',(limit,offset))]
                total=c.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
            return self.respond(200,{'resource':table,'total':total,'items':rows})
        if u.path=='/api/cases':
            try: limit=max(1,min(100,int(q.get('limit',['20'])[0]))); offset=max(0,int(q.get('offset',['0'])[0]))
            except ValueError:return self.respond(400,{'error':'invalid pagination'})
            with connect() as c:
                items=[dict(r) for r in c.execute('SELECT * FROM cases ORDER BY id LIMIT ? OFFSET ?',(limit,offset))]
            for r in items:r['priority']=priority(r['status'],r['severity'],r['amount'])
            return self.respond(200,{'items':items,'limit':limit,'offset':offset})
        if u.path.startswith('/api/cases/'):
            cid=u.path.rsplit('/',1)[-1]
            with connect() as c:
                row=c.execute('SELECT * FROM cases WHERE id=?',(cid,)).fetchone()
                events=[dict(r) for r in c.execute('SELECT * FROM events WHERE case_id=? ORDER BY recorded_at',(cid,))]
            if not row:return self.respond(404,{'error':'not found'})
            r=dict(row);r['events']=events;r['manual_review_required']=manual_review_required(r['status'],r['severity'])
            return self.respond(200,r)
        return self.respond(404,{'error':'route not found'})
    def log_message(self,fmt,*args):sys.stderr.write('%s %s\n'%(self.address_string(),fmt%args))
def main():
    setup();port=int(os.getenv('PORT','8080')); host=os.getenv('HOST','127.0.0.1')
    print(f'{CFG["slug"]}: http://{host}:{port}',flush=True)
    ThreadingHTTPServer((host,port),Handler).serve_forever()
if __name__=='__main__':main()
