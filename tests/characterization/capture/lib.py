"""CT library-level capture - port of Stage 7 evidence/scripts/capture_lib.py (identical code block,
run in a child process whose cwd is a fresh sandbox copy WORK/c_lib)."""
import subprocess
import sys

from _common import args, harness

SRC, WORK, OUT = args()
d = harness.clone(SRC, WORK, 'c_lib')
code = r'''
import json
from app import gateway_bridge as g, integration, baseline
ev=lambda **k:{**{'message_id':'X1','business_key':'BT00000001','system':'mes','event_type':'lab_test','occurred_at':'2025-01-01T00:00:00Z'},**k}
out={}
out['unknown_key']=g.apply([ev(message_id='U1',business_key='NOPE')])
out['missing_field']=g.apply([{'message_id':'bad'}])
out['non_dict']=g.apply(['x',None,5])
out['ok_then_dup']=[g.apply([ev(message_id='OK1')]),g.apply([ev(message_id='OK1')])]
out['same_msg_different_key_is_dup']=g.apply([ev(message_id='OK1',business_key='BT00000002')])
out['empty']=g.apply([])
out['sql_injection_key']=g.apply([ev(message_id='I1',business_key="BT00000001' OR '1'='1")])
out['consume_first3']=integration.consume_source_messages(3)
out['consume_limit0']=integration.consume_source_messages(0)
print(json.dumps(out,sort_keys=True,indent=1))
'''
r = subprocess.run([sys.executable, '-c', code], cwd=d, capture_output=True, text=True, env=harness.child_env(), timeout=170)
open(OUT, 'w').write(r.stdout if r.returncode == 0 else 'ERR ' + r.stderr)
print(r.returncode, r.stdout[:300] if r.returncode == 0 else r.stderr[-500:])
sys.exit(0 if r.returncode == 0 else 1)
