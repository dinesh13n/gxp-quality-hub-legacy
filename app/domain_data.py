import json,random,datetime
from .store import connect,setup

def generate_domain(count=6000,seed=4100):
    r=random.Random(seed+9211)
    sites=['IN-BLR','US-TX','DE-BY','JP-KN','GB-ENG','BR-SP']
    with connect() as c:
        c.execute('CREATE TABLE IF NOT EXISTS materials(material_id TEXT PRIMARY KEY, material_name TEXT NOT NULL, source_site TEXT NOT NULL, spec_version TEXT NOT NULL)')
        c.execute('CREATE TABLE IF NOT EXISTS batch_records(batch_id TEXT PRIMARY KEY, material_id TEXT NOT NULL REFERENCES materials(material_id), batch_site TEXT NOT NULL, observed_assay REAL NOT NULL, assay_unit TEXT NOT NULL, qa_status TEXT NOT NULL)')
        c.execute('DELETE FROM batch_records')
        c.execute('DELETE FROM materials')
        n=max(30,count//8)
        parents=[]
        for i in range(n):
            row=(f'M{i:07d}',r.choice(['active ingredient','excipient','binder','coating']),r.choice(sites),r.choice(['SOP-1','SOP-2']))
            c.execute('INSERT INTO materials VALUES ({})'.format(','.join('?'*len(row))),row)
            parents.append(row[0])
        for i in range(count):
            material_id=r.choice(parents)
            day=(datetime.date(2023,1,1)+datetime.timedelta(days=r.randint(0,1090))).isoformat()
            row=(f'BT{i:08d}',material_id,r.choice(sites),round(r.gauss(99,2.8),3),r.choice(['pct','percent']),r.choice(['REVIEW','QA_HOLD','CLOSED']))
            c.execute('INSERT INTO batch_records VALUES ({})'.format(','.join('?'*len(row))),row)
    return {'entity':'materials','entity_count':n,'detail':'batch_records','detail_count':count}

if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser(); a.add_argument('--count',type=int,default=6000); a.add_argument('--seed',type=int,default=4100); args=a.parse_args()
 print(json.dumps(generate_domain(args.count,args.seed)))
