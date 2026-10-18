"""INC-01 supplementary captures (NOT part of Stage 7 goldens). Their golden is
golden/inc01/supplement_golden_v1.json, created once on the unmodified baseline in INC-01 via the
reviewed --update-golden path (CT-H4) and versioned; it is never edited in place.

  CT-12s  execute the statements of sql/legacy_reports.sql itself (Stage 7 captured an inline copy)
  CT-15s  readiness scripts offline_inventory / verify_preloaded / rehearse_local (Stage 7 R7 log)
  CT-16s  write methods (POST/PUT/DELETE/PATCH) on every GET route of both HTTP services -> status,
          plus a static source scan: which modules contain SQL writes to `cases`, and whether any
          disposition / release / e-signature handler exists (HAR-12 / STOP-07 guard)
"""
import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request

from _common import args, harness

SRC, WORK, OUT = args()
ENV = harness.child_env()
G = {}

# ---- CT-12s: sql/legacy_reports.sql executed statement by statement on a read-only connection
sql_text = open(os.path.join(SRC, 'sql', 'legacy_reports.sql'), encoding='utf-8').read()
stmts = [s.strip() for s in re.sub(r'--[^\n]*', '', sql_text).split(';') if s.strip()]
c = sqlite3.connect(f'file:{SRC}/data/legacy.sqlite3?mode=ro', uri=True)
G['sql_file_statement_count'] = len(stmts)
G['sql_file_results'] = [[list(r) for r in c.execute(s).fetchall()] for s in stmts]
c.close()

# ---- CT-15s: readiness scripts on a fresh pristine copy (same commands as Stage 7 R7)
d = harness.clone(SRC, WORK, 'c_r7')
G['readiness_scripts'] = {}
for s in ('scripts/offline_inventory.py', 'scripts/verify_preloaded.py', 'scripts/rehearse_local.py'):
    r = subprocess.run([sys.executable, s], cwd=d, env=ENV, capture_output=True, timeout=170)
    G['readiness_scripts'][s] = {'rc': r.returncode, 'stdout_head6000': r.stdout[:6000].decode('utf-8', 'replace')}

# ---- CT-16s: write methods on every route, both services
d = harness.clone(SRC, WORK, 'c_m16')
procs = []


def freeport():
    so = socket.socket(); so.bind(('127.0.0.1', 0)); p = so.getsockname()[1]; so.close(); return p


def start(mod, envname, port):
    p = subprocess.Popen([sys.executable, '-m', mod], cwd=d, env=harness.child_env({'HOST': '127.0.0.1', envname: str(port)}),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append(p)
    for _ in range(80):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=1).read(); return
        except Exception:
            time.sleep(.1)
    raise RuntimeError('no start ' + mod)


def call(port, path, method):
    data = b'{}' if method in ('POST', 'PUT', 'PATCH') else None
    req = urllib.request.Request(f'http://127.0.0.1:{port}' + path, method=method, data=data)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # noqa: BLE001
        return 'EXC:' + type(e).__name__


API_ROUTES = ['/', '/health', '/api/incidents', '/api/metrics', '/api/cases', '/api/cases/C00000001', '/api/partners/partner_feeds',
              '/api/partners/batch_runs', '/api/domain/deviations', '/api/domain/capa_actions', '/nope']
GW_ROUTES = ['/health', '/api/catalog', '/api/events', '/api/record/NOPE', '/api/failure', '/nope']
try:
    api, gw = freeport(), freeport()
    start('app.server', 'PORT', api); start('services.source_gateway.server', 'SOURCE_PORT', gw)
    G['write_methods_api'] = {f'{m} {p}': call(api, p, m) for p in API_ROUTES for m in ('POST', 'PUT', 'DELETE', 'PATCH')}
    G['write_methods_gateway'] = {f'{m} {p}': call(gw, p, m) for p in GW_ROUTES for m in ('POST', 'PUT', 'DELETE', 'PATCH')}
finally:
    for p in procs:
        p.terminate()
        try:
            p.wait(timeout=10)
        except Exception:
            p.kill()
d_hash_before = harness.sha256_file(os.path.join(SRC, 'data', 'legacy.sqlite3'))

# static scan (source only; tests/ and docs/ excluded)
WRITE_RE = re.compile(r'\b(INSERT\s+(?:OR\s+\w+\s+)?INTO|REPLACE\s+INTO|UPDATE|DELETE\s+FROM)\s+["`\[]?cases\b', re.I)
DISP_RE = re.compile(r'(batch_disposition|qa_release|e_?signature|def\s+\w*dispos\w*|do_POST|do_PUT|do_DELETE|do_PATCH)', re.I)
writers, disp = [], {}
for base in ('app', 'services', 'legacy_batch', 'legacy_java', 'legacy_js', 'scripts', 'sql', 'integration', 'ops', 'operations'):
    root = os.path.join(SRC, base)
    for dp, dn, fn in os.walk(root):
        dn.sort()
        for f in sorted(fn):
            if not f.endswith(('.py', '.js', '.java', '.sql', '.sh')):
                continue
            rel = os.path.relpath(os.path.join(dp, f), SRC)
            text = open(os.path.join(dp, f), encoding='utf-8', errors='replace').read()
            if WRITE_RE.search(text):
                writers.append(rel)
            hits = sorted(set(m.group(0) for m in DISP_RE.finditer(text)))
            if hits:
                disp[rel] = hits
G['static_cases_writers'] = writers
G['static_disposition_or_write_handlers'] = disp
G['source_db_unchanged_by_supplement'] = d_hash_before == harness.BASELINE_DB_SHA256
json.dump(G, open(OUT, 'w'), indent=1, sort_keys=True)
print('ok', len(G))
