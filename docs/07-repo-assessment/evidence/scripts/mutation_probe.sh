#!/bin/bash
# Mutation probe: apply ONE deliberate behavioural change in a sandbox copy; record whether the existing suite still passes (survived = coverage gap)
S=$HOME/fde_sbx/stage7; export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
run(){ id=$1; file=$2; from=$3; to=$4; desc=$5
  rm -rf $S/mut; cp -a $S/repo $S/mut; cd $S/mut
  python3 - "$file" "$from" "$to" <<'PY'
import sys
f,a,b=sys.argv[1:4];s=open(f).read()
assert s.count(a)==1,(f,a,s.count(a));open(f,'w').write(s.replace(a,b))
PY
  [ $? -ne 0 ] && { echo "$id | APPLY-FAILED | $desc"; return; }
  out=$(python3 -m unittest discover -s tests 2>&1 | tail -3 | tr '\n' ' ')
  if echo "$out" | grep -q '^.*OK'; then echo "$id | SURVIVED (suite still green) | $desc | $file"; else echo "$id | KILLED | $desc | $file | $out"; fi
}
run M1 app/legacy_logic.py "amount > 50000" "amount > 1" "urgent amount threshold 50000 -> 1"
run M2 app/legacy_logic.py "if severity=='HIGH' or status=='ESCALATED': return 'review'" "if False: return 'review'" "'review' tier removed"
run M3 app/legacy_logic.py "return severity in ('HIGH','CRITICAL') or status in ('ESCALATED','REOPENED')" "return False" "manual_review_required always False"
run M4 app/legacy_logic.py "if status=='CLOSED': return 'archive'" "if False: return 'archive'" "CLOSED no longer archived"
run M5 app/partner_feeds.py "elif payload.get('quantity',0)<0:" "elif False:" "negative-quantity rejection removed"
run M6 app/partner_feeds.py "elif row['processing_status']=='REPLAY':" "elif False:" "replay duplicate detection removed"
run M7 app/partner_feeds.py "if not key or row['schema_rev']=='unsupported':" "if False:" "schema/key validation removed"
run M8 legacy_batch/shift_reconciliation.py "row['value']>row['threshold']" "row['value']<row['threshold']" "night-shift threshold comparison inverted"
run M9 app/gateway_bridge.py "if not present:" "if False:" "unknown business_key no longer rejected"
run M10 app/server.py "r['manual_review_required']=manual_review_required(r['status'],r['severity'])" "r['manual_review_required']=False" "API manual_review flag hard-wired False"
run M11 app/server.py "limit=max(1,min(100,int(q.get('limit',['20'])[0])));offset=max(0,int(q.get('offset',['0'])[0]))
            except ValueError:return self.respond(400,{'error':'invalid pagination'})
            with connect() as c:
                rows=[dict(x) for x in c.execute('SELECT * FROM '+table+' LIMIT ? OFFSET ?',(limit,offset))]
                total=c.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
            return self.respond(200,{'resource':table,'total':total,'items':rows})
        if u.path.startswith('/api/domain/')" "limit=1;offset=0
            except ValueError:return self.respond(400,{'error':'invalid pagination'})
            with connect() as c:
                rows=[dict(x) for x in c.execute('SELECT * FROM '+table+' LIMIT ? OFFSET ?',(limit,offset))]
                total=c.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
            return self.respond(200,{'resource':table,'total':total,'items':rows})
        if u.path.startswith('/api/domain/')" "partners pagination ignores limit/offset"
run M12 app/baseline.py "'urgent_cases':sum(priority(r['status'],r['severity'],r['amount'])=='urgent' for r in data)" "'urgent_cases':0" "baseline urgent_cases hard-wired 0"
run M13 legacy_js/legacy_policy.js "*1.05" "*1.5" "JS tolerance 5% -> 50% (not Python; suite has no JS tests)"
run M14 app/historical_estate.py "if exists:return {'status':'already_imported','import_id':digest,'rows':0}" "pass" "idempotent file import removed"
run M15 services/source_gateway/server.py "if mode=='timeout':return self.reply(503" "if mode=='timeout':return self.reply(200" "gateway failure-mode 503 -> 200"
