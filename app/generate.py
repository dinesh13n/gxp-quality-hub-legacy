import argparse, json, random, datetime, sqlite3
from pathlib import Path
from .store import connect, setup
def generate(count=6000, seed=4100, reset=False):
    if count < 1 or count > 250000: raise ValueError('count must be in range 1..250000')
    rng=random.Random(seed)
    setup()
    base=datetime.datetime(2023,1,1,tzinfo=datetime.timezone.utc)
    sites=['IN-BLR','US-TX','DE-BY','JP-KN','GB-ENG','BR-SP']
    segments=['standard','priority','enterprise','regulated','legacy-v1']
    regions=['APAC','AMER','EMEA']
    states=['OPEN','UNDER_REVIEW','CLOSED','ESCALATED','REOPENED']
    notes=['Inspection complete; supporting report not attached.', 'Operator reports intermittent issue during shift change.', 'See older case for original equipment identifier.', 'Recheck previous version of site procedure.', 'Reported value does not match signed PDF attachment.', 'Technician observed unusual noise after maintenance.', 'Customer service notes partial recovery and recurring alert.', 'Manual spreadsheet adjustment applied during month-end close.', 'Aprobación pendiente; revisar informe técnico.', '対応記録と設備番号を照合してください。']
    with connect() as c:
        if reset:
            from .enterprise_data import TABLES
            for t,_ in reversed(TABLES): c.execute('DROP TABLE IF EXISTS '+t)
            for t in ['events','source_messages','cases','operating_costs']: c.execute('DELETE FROM '+t)
        if c.execute('SELECT COUNT(*) FROM cases').fetchone()[0]:
            raise RuntimeError('Database already contains cases; use --reset to replace synthetic data')
        cases=[]; events=[]; messages=[]
        for i in range(count):
            cid=f'C{i+1:08d}'; date=base+datetime.timedelta(hours=rng.randint(0,24*1100))
            severity=rng.choices(['LOW','MEDIUM','HIGH','CRITICAL'],[.55,.30,.12,.03])[0]
            state=rng.choices(states,[.35,.25,.28,.08,.04])[0]
            if severity=='CRITICAL' and rng.random()<.3: state='ESCALATED'
            amount=round(rng.lognormvariate(7.9,1.0),2)
            note=rng.choice(notes)
            if rng.random()<.013: note+=' | legacy source omitted account reference'
            cases.append((cid,f'ACCT-{rng.randrange(1,max(30,count//20)):06d}',rng.choice(segments),rng.choice(sites),rng.choice(regions),date.isoformat(),state,severity,amount,note,1))
            etime=date+datetime.timedelta(minutes=rng.randint(1,300))
            events.append((f'E{i+1:09d}',cid,etime.isoformat(),'CASE_CREATED',json.dumps({'source':'batch-import','status':state})))
            if rng.random()<.17:
                events.append((f'EX{i+1:09d}',cid,(etime+datetime.timedelta(hours=rng.randint(0,24))).isoformat(),'STATUS_REVIEWED',json.dumps({'reviewer':'operations','severity':severity})))
            if rng.random()<.12:
                messages.append((f'M{i+1:09d}','external-feed',etime.isoformat(),json.dumps({'ref':cid,'status':state,'schema_version':rng.choice(['1','1','2'])})))
        c.executemany('INSERT INTO cases VALUES (?,?,?,?,?,?,?,?,?,?,?)',cases)
        c.executemany('INSERT INTO events VALUES (?,?,?,?,?)',events)
        c.executemany('INSERT INTO source_messages VALUES (?,?,?,?)',messages)
        for j in range(36):
            n=max(1,count//36 + rng.randrange(-min(count//100,50),min(count//100,50)+1))
            c.execute('INSERT INTO operating_costs VALUES (?,?,?,?)',(f'{2023+j//12}-{j%12+1:02d}',round(n*rng.uniform(.35,.9),2),n,round(70+n*.07,2)))
    from .domain_data import generate_domain
    domain_summary=generate_domain(count,seed)
    from .enterprise_data import expand
    enterprise_summary=expand(seed)
    return {'enterprise':enterprise_summary,'cases':len(cases),'events':len(events),'messages':len(messages),'seed':seed,'domain':domain_summary}
def main():
    p=argparse.ArgumentParser();p.add_argument('--count',type=int,default=6000);p.add_argument('--seed',type=int,default=4100);p.add_argument('--reset',action='store_true');a=p.parse_args()
    print(json.dumps(generate(a.count,a.seed,a.reset)))
if __name__=='__main__':main()
