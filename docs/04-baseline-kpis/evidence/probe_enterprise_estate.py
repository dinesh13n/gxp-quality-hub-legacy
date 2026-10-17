#!/usr/bin/env python3
"""Stage 4 read-only probe of data/enterprise_legacy.sqlite3 (secondary estate, NOT the OD-02 baseline).
Usage: python3 -I probe_enterprise_estate.py <path>. mode=ro&immutable=1."""
import sqlite3, sys, json, statistics as st
from datetime import datetime
c = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro&immutable=1", uri=True)
q = lambda s: c.execute(s).fetchall(); P = datetime.fromisoformat
def pct(v,p):
    v=sorted(v);k=(len(v)-1)*p/100;f=int(k);cc=min(f+1,len(v)-1);return v[f]+(v[cc]-v[f])*(k-f)
o={}
o["objects"]=q("select count(*) from operational_objects")[0][0]
o["history_rows_per_object_max"]=q("select max(n) from (select count(*) n from state_history group by object_id)")[0][0]
o["history_distinct_transitions"]=q("select from_state,to_state,count(*) from state_history group by 1,2")
o["history_from_state_always_OPEN"]=q("select count(*)=sum(from_state='OPEN') from state_history")[0][0]
o["history_at_equals_object_event_at"]=q("select sum(h.at_utc=ob.event_at),count(*) from state_history h join operational_objects ob using(object_id)")[0]
d=[(P(a)-P(b)).total_seconds()/3600 for a,b in q("select arrival_time,event_time from evidence_events")]
o["evidence_arrival_delay_hours"]={"n":len(d),"median":round(st.median(d),2),"p90":round(pct(d,90),2),"negative":sum(1 for x in d if x<0)}
o["evidence_strength"]=q("select json_extract(payload,'$.evidence_strength'),count(*) from evidence_events group by 1")
o["evidence_events_per_object_max"]=q("select max(n) from (select count(*) n from evidence_events group by object_id)")[0][0]
o["objects_closed_with_strength0_evidence"]=q("select count(*) from operational_objects ob join evidence_events e using(object_id) where ob.status='CLOSED' and json_extract(e.payload,'$.evidence_strength')=0")[0][0]
o["objects_closed"]=q("select count(*) from operational_objects where status='CLOSED'")[0][0]
o["injection_marker_notes"]=q("select count(*) from evidence_events where payload like '%untrusted%' or payload like '%ignore all controls%'")[0][0]
o["workflow_task_status"]=q("select status,count(*) from workflow_tasks group by 1")
o["event_at_range"]=q("select min(event_at),max(event_at) from operational_objects")[0]
o["negative_value_objects"]=q("select count(*) from operational_objects where value<0")[0][0]
print(json.dumps(o,indent=1,default=str))
