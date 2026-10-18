"""CT HTTP capture - port of Stage 7 evidence/scripts/capture_api.py (same requests, same keys).
Port changes: runs both servers in their own fresh sandbox copy (WORK/c_api) instead of the source
copy; servers bound to 127.0.0.1 on ephemeral ports (CT-H2) and always terminated."""
import hashlib
import json
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter

from _common import args, harness

SRC, WORK, OUT = args()
ROOT = harness.clone(SRC, WORK, 'c_api')


def freeport():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p


PROCS = []


def start(mod, envname, port):
    env = harness.child_env({'HOST': '127.0.0.1', envname: str(port)})
    p = subprocess.Popen([sys.executable, '-m', mod], cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    PROCS.append(p)
    for _ in range(80):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=1).read(); return p
        except Exception:
            time.sleep(.1)
    raise RuntimeError('no start ' + mod)


def get(port, path, method='GET', data=None):
    req = urllib.request.Request(f'http://127.0.0.1:{port}' + path, method=method, data=data)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            st, body, ct = r.status, r.read(), r.headers.get('Content-Type')
    except urllib.error.HTTPError as e:
        st, body, ct = e.code, e.read(), e.headers.get('Content-Type')
    return st, ct, body


try:
    api = freeport(); gw = freeport()
    start('app.server', 'PORT', api); start('services.source_gateway.server', 'SOURCE_PORT', gw)
    c = sqlite3.connect(f'file:{ROOT}/data/legacy.sqlite3?mode=ro', uri=True)

    def pick(where):
        r = c.execute(f'select id from cases where {where} order by id limit 1').fetchone()
        return r[0] if r else None
    case_ids = [pick("1=1"), pick("severity='CRITICAL'"), pick("status='CLOSED'"), pick("status='ESCALATED'"), pick("status='REOPENED'"), pick("amount>50000 and status!='CLOSED' and severity='LOW'"), pick("severity='HIGH' and status='OPEN'")]
    api_paths = ['/health', '/', '/api/incidents', '/api/metrics', '/api/cases', '/api/cases?limit=3&offset=2', '/api/cases?limit=1000', '/api/cases?limit=0', '/api/cases?limit=-5', '/api/cases?offset=-1&limit=2', '/api/cases?limit=abc', '/api/cases?offset=9999', '/api/cases/NOPE', "/api/cases/C00000001'%20OR%201=1--", '/nope', '/api/cases/']
    case_ids = [i for i in case_ids if i]
    api_paths += ['/api/cases/' + i for i in case_ids]
    api_paths += ['/api/partners/' + t for t in ['partner_feeds', 'reference_versions', 'policy_exceptions', 'upstream_outages', 'batch_runs', 'bogus']]
    api_paths += ['/api/partners/partner_feeds?limit=2&offset=8566', '/api/partners/partner_feeds?limit=x']
    api_paths += ['/api/domain/' + t for t in ['deviations', 'lab_results', 'capa_actions', 'sop_versions', 'bogus']]
    api_paths += ['/api/domain/lab_results?limit=3&offset=0']
    golden = {'meta': {'python': sys.version.split()[0], 'cases_sample_ids': case_ids}, 'api': {}, 'gateway': {}}
    for p in api_paths:
        st, ct, b = get(api, p); golden['api'][p] = {'status': st, 'content_type': ct, 'sha256': hashlib.sha256(b).hexdigest(), 'body': json.loads(b) if len(b) < 20000 else '<<truncated %d bytes; see sha256>>' % len(b)}
    for m in ['POST', 'PUT', 'DELETE', 'HEAD']:
        try:
            st, ct, b = get(api, '/api/cases', method=m, data=b'{}' if m in ('POST', 'PUT') else None)
        except Exception as e:
            st, ct, b = 'EXC:' + type(e).__name__, None, b''
        golden['api']['METHOD ' + m + ' /api/cases'] = {'status': st, 'body_prefix': b[:120].decode('utf8', 'replace')}
    allc = []; off = 0
    while True:
        st, ct, b = get(api, f'/api/cases?limit=100&offset={off}'); items = json.loads(b)['items']
        if not items:
            break
        allc += items; off += 100
    golden['api_all_cases_priority'] = [[i['id'], i['status'], i['severity'], i['amount'], i['priority']] for i in allc]
    golden['api_priority_distribution'] = dict(Counter(i['priority'] for i in allc))
    gw_paths = ['/health', '/api/catalog', '/api/events?limit=5', '/api/events?limit=3&offset=18', '/api/events?limit=3&source=mes', '/api/events?source=bogus', '/api/events?limit=x', '/api/events?limit=1000&offset=0', '/api/record/' + c.execute('select batch_id from batch_records order by batch_id limit 1').fetchone()[0], '/api/record/NOPE', '/api/failure', '/api/failure?mode=timeout', '/api/failure?mode=schema', '/api/failure?mode=rate_limit', '/api/failure?mode=weird', '/nope']
    for p in gw_paths:
        st, ct, b = get(gw, p); golden['gateway'][p] = {'status': st, 'content_type': ct, 'sha256': hashlib.sha256(b).hexdigest(), 'body': json.loads(b) if len(b) < 30000 else '<<truncated %d bytes; see sha256>>' % len(b)}
    c.close()
    json.dump(golden, open(OUT, 'w'), indent=1, sort_keys=True)
    print('captured', len(golden['api']), 'api', len(golden['gateway']), 'gateway', golden['api_priority_distribution'])
finally:
    for p in PROCS:
        p.terminate()
        try:
            p.wait(timeout=10)
        except Exception:
            p.kill()
