#!/usr/bin/env python3
"""Stage 4 read-only baseline measurement. Usage: python3 -I measure_baseline.py <path-to-legacy.sqlite3>
Opens the DB with mode=ro&immutable=1 (never modifies it). Snapshot reference time AS_OF = max timestamp in
cases/events (NOT wall clock), so results are reproducible. Synthetic data: method validation only."""
import sqlite3, sys, json, statistics as st
from datetime import datetime
db = sys.argv[1]
c = sqlite3.connect(f"file:{db}?mode=ro&immutable=1", uri=True)
P = lambda s: datetime.fromisoformat(s)
def pct(v, p):
    v = sorted(v); k = (len(v)-1)*p/100; f = int(k); cc = min(f+1, len(v)-1)
    return v[f] + (v[cc]-v[f])*(k-f)
def dist(v):
    return None if not v else {"n": len(v), "median": round(st.median(v),2), "p90": round(pct(v,90),2), "mean": round(st.fmean(v),2), "min": round(min(v),2), "max": round(max(v),2)}
q = lambda s: c.execute(s).fetchall()
out = {}
AS_OF = max(q("select max(created_at) from cases")[0][0], q("select max(recorded_at) from events")[0][0])
out["as_of"] = AS_OF
out["population"] = {"cases": q("select count(*) from cases")[0][0], "created_min": q("select min(created_at) from cases")[0][0], "created_max": q("select max(created_at) from cases")[0][0]}
out["status_counts"] = dict(q("select status,count(*) from cases group by 1"))
# K-04/05 availability of closure timestamps
out["event_types"] = dict(q("select event_type,count(*) from events group by 1"))
out["closure_timestamp_available"] = False  # no CLOSED event type; verified by event_types above
# proxy: created -> first STATUS_REVIEWED
rv = [ (P(r[0])-P(r[1])).total_seconds()/3600 for r in q("select e.recorded_at,c.created_at from events e join cases c on c.id=e.case_id where e.event_type='STATUS_REVIEWED'")]
out["P-01_created_to_first_review_hours_all"] = dist(rv)
rvc = [ (P(r[0])-P(r[1])).total_seconds()/3600 for r in q("select e.recorded_at,c.created_at from events e join cases c on c.id=e.case_id where e.event_type='STATUS_REVIEWED' and c.status='CLOSED'")]
out["P-01_created_to_first_review_hours_closed_only"] = dist(rvc)
out["cases_with_review_event"] = q("select count(distinct case_id) from events where event_type='STATUS_REVIEWED'")[0][0]
out["closed_with_review_event"] = q("select count(distinct c.id) from cases c join events e on e.case_id=c.id and e.event_type='STATUS_REVIEWED' where c.status='CLOSED'")[0][0]
sm = [ (P(r[0])-P(r[1])).total_seconds()/3600 for r in q("select m.received_at,c.created_at from source_messages m join cases c on c.id=json_extract(m.body,'$.ref')")]
out["P-02_created_to_external_feed_msg_hours"] = dist(sm)
out["closed_with_external_closed_msg"] = q("select count(*) from source_messages m join cases c on c.id=json_extract(m.body,'$.ref') where c.status='CLOSED' and json_extract(m.body,'$.status')='CLOSED'")[0][0]
# D-EVID structural check
out["cases_columns"] = [r[1] for r in q("pragma table_info(cases)")]
out["closed_cases_total"] = out["status_counts"].get("CLOSED",0)
# K-09 backlog ageing (age of non-CLOSED cases at AS_OF, days) per site
rows = q("select site,status,created_at from cases")
def age_d(s): return (P(AS_OF)-P(s)).total_seconds()/86400
bl = {}
for site,status,cr in rows:
    d = bl.setdefault(site, {"total":0,"open_dops":[], "closed":0})
    d["total"]+=1
    if status!="CLOSED": d["open_dops"].append(age_d(cr))
    else: d["closed"]+=1
out["K-09_backlog_by_site_D-OPS"] = {s: {"total":v["total"],"not_closed":len(v["open_dops"]),"age_days": dist(v["open_dops"])} for s,v in sorted(bl.items())}
allopen=[a for v in bl.values() for a in v["open_dops"]]
out["K-09_backlog_all_D-OPS"] = {"not_closed": len(allopen), "of": len(rows), "age_days": dist(allopen)}
out["K-09_backlog_all_D-EVID_upper_bound"] = {"not_evidence_complete_cannot_be_excluded": len(rows), "note": "no evidence/approver fields in cases; every case, incl. 36 CLOSED, is unverifiable under D-EVID"}
# open ageing buckets
b = {"<=90d":0,"91-365d":0,"366-730d":0,">730d":0}
for a in allopen:
    b["<=90d" if a<=90 else "91-365d" if a<=365 else "366-730d" if a<=730 else ">730d"]+=1
out["K-09_age_buckets_D-OPS"] = b
out["reopened_rate"] = {"REOPENED": out["status_counts"].get("REOPENED",0), "of": len(rows)}
out["manual_review_required_by_code_rule"] = q("select count(*) from cases where (severity in ('HIGH','CRITICAL') or status in ('ESCALATED','REOPENED'))")[0][0]
# K-06 unmatched references
pf = q("select count(*), sum(ref_id not in (select id from cases)) from partner_feeds")[0]
out["K-06_partner_feeds"] = {"rows": pf[0], "unmatched": pf[1], "pct": round(100*pf[1]/pf[0],2), "by_status": q("select processing_status,count(*),sum(ref_id not in (select id from cases)) from partner_feeds group by 1"), "distinct_ref_ids": q("select count(distinct ref_id) from partner_feeds")[0][0], "source_ts_range": q("select min(source_ts),max(source_ts) from partner_feeds")[0]}
pe = q("select count(*), sum(ref_id not in (select id from cases)) from policy_exceptions")[0]
out["K-06_policy_exceptions"] = {"rows": pe[0], "unmatched": pe[1], "pct": round(100*pe[1]/pe[0],2)}
# K-07 replay presence (not replay safety)
out["K-07_replay_rows_present"] = q("select count(*) from partner_feeds where processing_status='REPLAY'")[0][0]
out["K-07_replay_with_matching_original_feed"] = q("select count(*) from partner_feeds r where r.processing_status='REPLAY' and exists(select 1 from partner_feeds o where o.processing_status<>'REPLAY' and o.ref_id=r.ref_id and o.source_ts=r.source_ts and o.record_kind=r.record_kind)")[0][0]
# K-08 reconciliation delay
dl = [ (P(r[1])-P(r[0])).total_seconds()/3600 for r in q("select source_ts,ingest_ts from partner_feeds")]
out["K-08_ingest_delay_hours_all"] = dist(dl)
out["K-08_within_4h_pct"] = round(100*sum(1 for x in dl if x<=4)/len(dl),2)
out["K-08_negative_delays"] = sum(1 for x in dl if x<0)
for ps in ("NEW","RETRY","REPLAY"):
    v=[ (P(r[1])-P(r[0])).total_seconds()/3600 for r in q(f"select source_ts,ingest_ts from partner_feeds where processing_status='{ps}'")]
    out[f"K-08_delay_{ps}"] = dist(v)
# K-10 ops vs finance month comparability
cm = dict(q("select substr(created_at,1,7),count(*) from cases group by 1"))
oc = {r[0]:(r[1],r[2],r[3]) for r in q("select period,total_cases,labor_hours,infrastructure_usd from operating_costs")}
months = sorted(set(cm)|set(oc))
diff = [(m, cm.get(m,0), oc.get(m,(None,))[0]) for m in months]
out["K-10_months_compared"] = len(months)
out["K-10_months_equal"] = sum(1 for m,a,b in diff if a==b)
out["K-10_total_cases_ops_table"] = sum(v[0] for v in oc.values())
out["K-10_total_cases_cases_table"] = sum(cm.values())
out["K-10_abs_monthly_diff_sum"] = sum(abs(a-(b or 0)) for m,a,b in diff)
out["K-10_first_diffs"] = [d for d in diff if d[1]!=d[2]][:8]
out["K-10_months_with_cases_but_zero_costrow"] = sum(1 for m,a,b in diff if b is None)
# Effort / cost
lh=sum(v[1] for v in oc.values()); tc=sum(v[0] for v in oc.values()); inf=sum(v[2] for v in oc.values())
out["effort_hours_per_case"] = round(lh/tc,3); out["labor_hours_total"]=round(lh,2); out["infra_usd_total"]=round(inf,2); out["infra_usd_per_case_ops_table"]=round(inf/tc,2)
out["throughput_cases_created_per_month_mean"] = round(st.fmean(cm.values()),2)
out["throughput_by_year"] = dict(q("select substr(created_at,1,4),count(*) from cases group by 1"))
# Quality: deviations / CAPA / lab
out["deviations"] = q("select status,count(*),sum(root_cause is null) from deviations group by 1")
out["deviations_closed_without_root_cause"] = q("select count(*) from deviations where status='CLOSED' and root_cause is null")[0][0]
out["capa"] = dict(q("select state,count(*) from capa_actions group by 1"))
out["capa_overdue_pct_of_not_verified"] = round(100*out["capa"].get("OVERDUE",0)/(out["capa"].get("OVERDUE",0)+out["capa"].get("OPEN",0)),2)
out["capa_verified_with_closed_deviation"] = q("select count(*) from capa_actions a join deviations d using(deviation_id) where a.state='VERIFIED' and d.status<>'CLOSED'")[0][0]
out["lab_results"] = dict(q("select test_status,count(*) from lab_results group by 1"))
out["policy_exception_outcomes"] = dict(q("select outcome,count(*) from policy_exceptions group by 1"))
out["policy_exception_range"] = q("select min(recorded_at),max(recorded_at) from policy_exceptions")[0]
# batch runs and outages
br = q("select result,count(*),sum(input_count),sum(accepted_count),sum(rejected_count) from batch_runs group by 1")
ti=sum(r[2] for r in br); tr=sum(r[4] for r in br)
out["batch_runs"] = {"by_result": br, "reject_pct": round(100*tr/ti,2), "runs": sum(r[1] for r in br), "failed_runs_pct": round(100*[r[1] for r in br if r[0]=='FAILED'][0]/sum(r[1] for r in br),2)}
out["batch_runs_inconsistent_count"] = q("select count(*) from batch_runs where input_count<>accepted_count+rejected_count")[0][0]
out["batch_runs_FAILED_with_accepts"] = q("select count(*) from batch_runs where result='FAILED' and accepted_count>0")[0][0]
og = [ (P(r[1])-P(r[0])).total_seconds()/3600 for r in q("select began,resolved from upstream_outages where resolved is not null")]
out["outages"] = {"total": q("select count(*) from upstream_outages")[0][0], "unresolved": q("select count(*) from upstream_outages where resolved is null")[0][0], "mttr_hours": dist(og), "range": q("select min(began),max(began) from upstream_outages")[0]}
# data quality
out["dq_cases_null_note"] = q("select count(*) from cases where note is null or note=''")[0][0]
out["dq_events_case_created_status_mismatch"] = q("select count(*) from events e join cases c on c.id=e.case_id where e.event_type='CASE_CREATED' and json_extract(e.payload,'$.status')<>c.status")[0][0]
out["dq_case_created_event_lag_min"] = dist([ (P(r[0])-P(r[1])).total_seconds()/60 for r in q("select e.recorded_at,c.created_at from events e join cases c on c.id=e.case_id where e.event_type='CASE_CREATED'")])
out["dq_neg_quantity_partner_feed"] = q("select count(*) from partner_feeds where json_extract(raw_json,'$.quantity')<0")[0][0]
out["dq_injection_marker_notes_partner_feed"] = q("select count(*) from partner_feeds where raw_json like '%disregard validation%' or raw_json like '%SYSTEM NOTE%'")[0][0]
out["dq_inconsistent_units_partner_feed"] = q("select json_extract(raw_json,'$.unit'),count(*) from partner_feeds group by 1")
out["dq_currency_partner_feed"] = q("select json_extract(raw_json,'$.currency'),count(*) from partner_feeds group by 1")
out["dq_case_batch_link_columns"] = "none: cases has no batch_id; batch_records/deviations keyed BTnnnnnnnn/DEVnnnnnnnn"
out["dq_cases_by_id_offset_join_BT"] = q("select count(*) from cases c join batch_records b on b.batch_id='BT'||printf('%08d', cast(substr(c.id,2) as integer)-1)")[0][0]
out["dq_period_overlap"] = {"cases": [out["population"]["created_min"], out["population"]["created_max"]], "partner_feeds": out["K-06_partner_feeds"]["source_ts_range"], "policy_exceptions": out["policy_exception_range"], "outages": out["outages"]["range"]}
out["dq_cases_amount_range"] = q("select min(amount),max(amount),avg(amount) from cases")[0]
out["dq_cases_over_50000"] = q("select count(*) from cases where amount>50000")[0][0]
out["priority_distribution_by_code_rule"] = None
print(json.dumps(out, indent=1, default=str))
