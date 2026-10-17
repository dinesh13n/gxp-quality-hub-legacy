import json, statistics
from pathlib import Path
from .store import connect, setup
from .legacy_logic import priority
def baseline():
    setup()
    with connect() as c:
        data=list(c.execute('SELECT status,severity,amount,site FROM cases'))
        ops=list(c.execute('SELECT labor_hours,total_cases,infrastructure_usd FROM operating_costs'))
    if not data: raise RuntimeError('No data: run python -m app.generate --reset first')
    out={'records':len(data),'open_cases':sum(r['status']!='CLOSED' for r in data),'urgent_cases':sum(priority(r['status'],r['severity'],r['amount'])=='urgent' for r in data),'mean_amount':round(statistics.fmean(r['amount'] for r in data),2),'sites':len({r['site'] for r in data}),'hours_per_case':round(sum(r['labor_hours'] for r in ops)/sum(r['total_cases'] for r in ops),3)}
    return out
if __name__=='__main__':print(json.dumps(baseline(),indent=2))
