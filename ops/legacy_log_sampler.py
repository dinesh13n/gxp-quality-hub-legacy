import json,random,datetime
r=random.Random(93)
for i in range(300):
 print(json.dumps({'ts':(datetime.datetime(2025,1,1)+datetime.timedelta(hours=i)).isoformat(),'component':['legacy','gateway','batch'][i%3],'correlation_id':f'TR-{i%49:05d}','latency_ms':int(r.lognormvariate(4,1)),'level':['INFO','WARN','ERROR'][i%3]}))
