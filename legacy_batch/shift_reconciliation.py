"""Old night-shift operational case reconciliation (business logic remains embedded in this job)."""
import argparse,csv,json,sqlite3,datetime,os,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data'/'enterprise_legacy.sqlite3'
def run(limit=500,db=None):
    conn=sqlite3.connect(str(db or DB));conn.row_factory=sqlite3.Row
    # Older module duplicated eligibility rules and arbitrarily treats REVIEW as open.
    outstanding=conn.execute('SELECT x.tenant,x.object_id,x.status,x.owner_team,x.region,p.policy_code,p.threshold,x.value FROM operational_objects x LEFT JOIN policy_register p ON p.region=x.region AND p.active=1 ORDER BY x.object_id LIMIT ?', (limit,)).fetchall()
    totals={};flagged=[]
    for row in outstanding:
        key=row['tenant'];totals[key]=totals.get(key,0)+1
        if row['status'] in ('HOLD','REVIEW') or (row['threshold'] is not None and row['value']>row['threshold']):
            flagged.append({'object_id':row['object_id'],'tenant':key,'owner_team':row['owner_team'],'status':row['status'],'policy':row['policy_code']})
    conn.close();return {'processed':len(outstanding),'by_tenant':totals,'flagged_count':len(flagged),'flagged_preview':flagged[:12]}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=500);a=p.parse_args()
    print(json.dumps(run(a.limit),indent=2))
