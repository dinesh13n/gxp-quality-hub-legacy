#!/usr/bin/env python3
"""Stage 15 INC-01 executable characterisation harness (CT-01..CT-16 + mutation gate M1..M15).

Usage (from the repository root; nothing legacy is executed in the working tree):
    python3 -B tests/characterization/run_characterization.py                 # CT-01..CT-16 + shipped suite
    python3 -B tests/characterization/run_characterization.py --mutation-gate # + M1..M15 (CT-H6)
Options: --sandbox-root DIR (default ~/fde_sbx/s15-inc01; must be OUTSIDE the working tree)
         --fixture-source DIR (dir containing data/; default ../_data-backup-2026-10-17)
         --label NAME  --mutants M1,M5  --no-legacy-suite  --keep
         --update-golden SOURCE --reviewed-by NAME   (writes a NEW versioned golden file; never overwrites)
Exit codes: 0 all green; 1 characterisation difference / mutant survived / legacy suite deviates;
            2 harness refused to run (E-CO-NOT-SANDBOX, E-FX-HASH, golden manifest mismatch).
"""
import argparse
import concurrent.futures as cf
import datetime
import io
import json
import os
import re
import subprocess
import sys
import time
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

H = harness.HERE
CAPTURES = ('api', 'batch', 'lib', 'supplement')
GOLDEN_INDEX = os.path.join(harness.GOLDEN_DIR, 'INDEX.json')
GOLDEN_MANIFEST = os.path.join(harness.GOLDEN_DIR, 'MANIFEST.sha256')


# ------------------------------------------------------------------ goldens
def verify_golden_manifest():
    bad = []
    with open(GOLDEN_MANIFEST, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                digest, rel = line.split(None, 1)
                p = os.path.join(harness.GOLDEN_DIR, rel.strip())
                if not os.path.isfile(p) or harness.sha256_file(p) != digest:
                    bad.append(rel.strip())
    if bad:
        raise harness.FixtureError('E-GOLDEN-HASH: golden files changed outside the reviewed update path: %s' % bad)


def load_goldens():
    idx = harness.load_json(GOLDEN_INDEX)
    g = {}
    for src, rel in idx['sources'].items():
        p = os.path.join(harness.GOLDEN_DIR, rel) if rel else None
        if not p or not os.path.isfile(p):
            g[src] = None
        elif src == 'r7':
            g[src] = parse_r7(open(p, encoding='utf-8').read())
        elif src == 'r1':
            g[src] = parse_unittest_log(open(p, encoding='utf-8').read())
        else:
            g[src] = harness.load_json(p)
            if isinstance(g[src], dict):
                g[src].pop('_golden_meta', None)
    return g


def parse_r7(text):
    out = {}
    for m in re.finditer(r'^## python3 (\S+)\n(.*?)EXIT=(\d+)\n', text, re.S | re.M):
        out[m.group(1)] = {'rc': int(m.group(3)), 'stdout_head6000': m.group(2)}
    return out


def parse_unittest_log(text):
    tests = sorted(re.findall(r'^(test\w+ \([\w.]+\)) \.\.\. (\w+)', text, re.M))
    ran = re.search(r'^Ran (\d+) tests?', text, re.M)
    post = re.search(r'^POST legacy\.sqlite3 ([0-9a-f]{64})', text, re.M)
    result = 'OK' if re.search(r'^OK\b', text, re.M) else ('FAILED' if re.search(r'^FAILED', text, re.M) else 'UNKNOWN')
    return {'tests': [list(t) for t in tests], 'ran': int(ran.group(1)) if ran else None, 'result': result,
            'post_db_sha256': post.group(1) if post else None}


# ------------------------------------------------------------------ capture
def run_captures(src, workroot, outdir, log):
    """Run the four capture scripts as child processes FROM the sandbox copy `src`."""
    os.makedirs(outdir, exist_ok=True)
    env = harness.child_env({'CHAR_WORKTREE_ROOT': harness.WORKTREE_ROOT, 'CHAR_FIXTURE_SOURCE': os.environ['CHAR_FIXTURE_SOURCE']})
    script_dir = os.path.join(src, 'tests', 'characterization', 'capture')
    harness.assert_safe_sandbox(script_dir)

    def one(name):
        t0 = time.time()
        work = os.path.join(workroot, 'w_' + name)
        r = subprocess.run([sys.executable, '-B', os.path.join(script_dir, name + '.py'), src, work, os.path.join(outdir, name + '.json')],
                           cwd=src, env=env, capture_output=True, text=True, timeout=1800)
        return name, {'rc': r.returncode, 'seconds': round(time.time() - t0, 1), 'stdout_tail': r.stdout[-300:], 'stderr_tail': r.stderr[-1500:]}

    with cf.ThreadPoolExecutor(max_workers=len(CAPTURES)) as ex:
        res = dict(ex.map(one, CAPTURES))
    for n in CAPTURES:
        log('  capture %-10s rc=%s %6.1fs' % (n, res[n]['rc'], res[n]['seconds']))
    actual = {}
    for n in CAPTURES:
        try:
            actual[n] = harness.load_json(os.path.join(outdir, n + '.json'))
        except Exception:  # noqa: BLE001  (capture failed or wrote 'ERR ...')
            actual[n] = None
    return actual, res


# ------------------------------------------------------------------ comparisons
def resolve_check(chk, golden, actual):
    """Return (label, golden_value, actual_value) triples for one catalogue check."""
    s = chk['src']
    A = lambda n: actual.get(n) or {}  # noqa: E731
    if s == 'batch':
        return [('batch:' + chk['key'], golden['batch'].get(chk['key'], '<<absent>>'), A('batch').get(chk['key'], '<<absent>>'))]
    if s == 'api':
        return [('api:' + chk['key'], golden['api'].get(chk['key'], '<<absent>>'), A('api').get(chk['key'], '<<absent>>'))]
    if s == 'api_section':
        sec = chk['section']; rx = re.compile(chk['match'])
        gs = golden['api'][sec]; as_ = A('api').get(sec, {})
        keys = sorted(k for k in set(gs) | set(as_) if rx.search(k) and not (chk['match'] == '.*' and k.startswith('METHOD ')))
        return [('api.%s:%s' % (sec, k), gs.get(k, '<<absent>>'), as_.get(k, '<<absent>>')) for k in keys]
    if s == 'lib':
        return [('lib:*', golden['lib'], actual['lib'] if actual.get('lib') is not None else '<<capture failed>>')]
    if s == 'supp':
        g = golden.get('supplement')
        return [('supplement:' + chk['key'], g.get(chk['key'], '<<absent>>') if g else '<<NO GOLDEN>>', A('supplement').get(chk['key'], '<<absent>>'))]
    if s == 'r7':
        a = A('supplement').get('readiness_scripts', {})
        return [('r7:' + k, v, a.get(k, '<<absent>>')) for k, v in sorted(golden['r7'].items())]
    if s == 'invariant' and chk['name'] == 'priority_distribution_36_70_17_2':
        return [('invariant:' + chk['name'], {'archive': 36, 'queue': 70, 'review': 17, 'urgent': 2}, A('api').get('api_priority_distribution'))]
    if s == 'derived' and chk['name'] == 'sql_file_matches_stage7_reports':
        res = A('supplement').get('sql_file_results') or []
        r1 = [r[:3] + [round(r[3], 2)] for r in res[0]] if len(res) > 0 else None
        return [('derived:sql_file_report_1_vs_stage7', golden['batch']['sql_report_1'], r1),
                ('derived:sql_file_report_2_vs_stage7', golden['batch']['sql_report_2'], res[1] if len(res) > 1 else None)]
    raise ValueError('unknown check %r' % chk)


def evaluate(catalogue, golden, actual):
    """Build and run a unittest suite: one TestCase per CT, one subTest per golden element."""
    results = {}

    def make(ct):
        def test(self):
            rows = []
            results[ct['id']] = rows
            for chk in ct['checks']:
                for label, g, a in resolve_check(chk, golden, actual):
                    ok = harness.equal(g, a)
                    rows.append({'check': label, 'pass': ok, 'diff': None if ok else harness.first_diff(g, a)})
                    with self.subTest(check=label):
                        self.assertTrue(ok, rows[-1]['diff'])
        return test

    suite = unittest.TestSuite()
    for ct in catalogue['tests']:
        if not ct['checks']:
            results[ct['id']] = 'NOT-RUN: ' + ct.get('reason', '')
            continue
        name = 'test_' + ct['id'].replace('-', '_')
        cls = type(ct['id'].replace('-', '_'), (unittest.TestCase,), {name: make(ct), '__doc__': ct['title']})
        suite.addTest(cls(name))
    stream = io.StringIO()
    outcome = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return results, outcome.wasSuccessful(), stream.getvalue()


# ------------------------------------------------------------------ shipped suite (as-found)
def run_legacy_suite(pristine, root, golden_r1, log):
    d = harness.clone(pristine, root, 'legacy_suite')
    r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=d, env=harness.child_env(),
                       capture_output=True, text=True, timeout=900)
    text = r.stderr + r.stdout + '\nPOST legacy.sqlite3 %s\n' % harness.sha256_file(os.path.join(d, 'data', 'legacy.sqlite3'))
    got = parse_unittest_log(text)
    same = got == golden_r1
    log('  shipped tests/test_*.py: ran=%s result=%s post_db=%s.. equals Stage 7 R1=%s' % (got['ran'], got['result'], (got['post_db_sha256'] or '')[:12], same))
    harness.safe_rmtree(d, root)
    return {'rc': r.returncode, 'parsed': got, 'equals_stage7_R1': same, 'diff': None if same else harness.first_diff(golden_r1, got)}


# ------------------------------------------------------------------ mutation gate
def mutation_gate(pristine, root, catalogue, golden, ids, log):
    muts = [m for m in harness.load_json(os.path.join(H, 'mutants.json'))['mutants'] if not ids or m['id'] in ids]
    out = []
    for m in muts:
        t0 = time.time()
        d = harness.clone(pristine, root, 'mut_' + m['id'])
        p = os.path.join(d, m['file'])
        text = open(p, encoding='utf-8').read()
        if text.count(m['from']) != 1:
            out.append({'id': m['id'], 'status': 'APPLY-FAILED'}); log('  %s APPLY-FAILED' % m['id']); continue
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text.replace(m['from'], m['to']))
        w, o = os.path.join(root, 'mutw_' + m['id']), os.path.join(root, 'mutout_' + m['id'])
        actual, caps = run_captures(d, w, o, lambda s: None)
        res, ok, _ = evaluate(catalogue, golden, actual)
        failed_cts = sorted(k for k, v in res.items() if isinstance(v, list) and not all(x['pass'] for x in v))
        failed_caps = sorted(n for n, c in caps.items() if c['rc'] != 0)
        killed = bool(failed_cts or failed_caps)
        out.append({'id': m['id'], 'file': m['file'], 'description': m['description'], 'status': 'KILLED' if killed else 'SURVIVED',
                    'failed_cts': failed_cts, 'failed_captures': failed_caps, 'seconds': round(time.time() - t0, 1)})
        log('  %-4s %-8s by %s %s (%.0fs)' % (m['id'], out[-1]['status'], ','.join(failed_cts) or '-',
                                           ('captures:' + ','.join(failed_caps)) if failed_caps else '', time.time() - t0))
        for x in (d, w, o):
            harness.safe_rmtree(x, root)
    return out


# ------------------------------------------------------------------ main
def tool_versions():
    import sqlite3

    def v(cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            ls = [x for x in (r.stdout + r.stderr).splitlines() if x.strip() and 'JAVA_TOOL_OPTIONS' not in x]
            return ls[0][:120] if ls else ''
        except Exception as e:  # noqa: BLE001
            return 'unavailable: %s' % e
    return {'python': sys.version.split()[0], 'sqlite': sqlite3.sqlite_version, 'java': v(['java', '-version']), 'node': v(['node', '--version'])}


def write_new_golden(source, actual, label, reviewer, head, log):
    sub = 'inc01' if source == 'supplement' else 'updates'
    n = 1
    while os.path.exists(os.path.join(harness.GOLDEN_DIR, sub, '%s_golden_v%d.json' % (source, n))):
        n += 1
    p = os.path.join(harness.GOLDEN_DIR, sub, '%s_golden_v%d.json' % (source, n))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    body = actual[source]
    if isinstance(body, dict):
        body = dict(body, _golden_meta={'source': source, 'captured_label': label, 'reviewed_by': reviewer, 'worktree_head': head,
                                        'note': 'NEW versioned golden; becomes active only via golden/INDEX.json + MANIFEST.sha256 in a reviewed PR (CT-H4)'})
    with open(p, 'x', encoding='utf-8') as f:  # 'x': never overwrite
        json.dump(body, f, indent=1, sort_keys=True)
    log('  wrote NEW golden %s (NOT activated; reviewed INDEX.json change required)' % os.path.relpath(p, harness.WORKTREE_ROOT))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--sandbox-root', default=os.environ.get('CHAR_SANDBOX_ROOT', harness.DEFAULT_SANDBOX_ROOT))
    ap.add_argument('--fixture-source', default=harness.DEFAULT_FIXTURE_SOURCE)
    ap.add_argument('--label', default=None)
    ap.add_argument('--mutation-gate', action='store_true')
    ap.add_argument('--mutants', default='')
    ap.add_argument('--no-legacy-suite', action='store_true')
    ap.add_argument('--keep', action='store_true', help='keep sandbox copies after the run')
    ap.add_argument('--update-golden', choices=['supplement', 'api', 'batch', 'lib'])
    ap.add_argument('--reviewed-by', default=None)
    a = ap.parse_args(argv)
    lines = []

    def log(s):
        print(s, flush=True); lines.append(s)

    t_start = time.time()
    label = a.label or datetime.datetime.now().strftime('run-%Y%m%dT%H%M%S')
    if a.update_golden and not a.reviewed_by:
        log('REFUSED: --update-golden needs --reviewed-by (CT-H4)'); return 2
    try:
        sroot = harness.assert_safe_sandbox(a.sandbox_root, a.fixture_source)
        os.environ['CHAR_FIXTURE_SOURCE'] = os.path.realpath(a.fixture_source)
        rundir = os.path.join(sroot, label)
        harness.assert_safe_sandbox(rundir, a.fixture_source)
        verify_golden_manifest()
        if os.path.exists(rundir):
            harness.safe_rmtree(rundir, sroot)
        os.makedirs(rundir)
        log('INC-01 characterisation harness  label=%s  sandbox=%s' % (label, rundir))
        log('  protected worktree (never executed in) = %s' % harness.WORKTREE_ROOT)
        pristine = harness.build_pristine(rundir, 'pristine', a.fixture_source)
        log('  FX-BASE125 hash gate: %d files verified, legacy.sqlite3=%s..' % (len(harness.load_manifest()), harness.BASELINE_DB_SHA256[:12]))
    except (harness.SandboxGuardError, harness.FixtureError) as e:
        log('REFUSED: %s' % e)
        return 2
    catalogue = harness.load_json(os.path.join(H, 'catalogue.json'))
    golden = load_goldens()
    actual, caps = run_captures(pristine, os.path.join(rundir, 'work'), os.path.join(rundir, 'out'), log)
    head = subprocess.run(['git', '-C', harness.WORKTREE_ROOT, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    report = {'label': label, 'started': datetime.datetime.now().isoformat(timespec='seconds'), 'tools': tool_versions(), 'worktree_head': head,
              'captures': caps, 'normalisation_rules': harness.NORMALISATION_RULES,
              'capture_digests': {n: (harness.hashlib.sha256(harness.canonical_bytes(actual[n])).hexdigest() if actual[n] is not None else None) for n in CAPTURES}}
    if a.update_golden:
        if actual[a.update_golden] is None:
            log('REFUSED: capture %s failed' % a.update_golden); return 2
        write_new_golden(a.update_golden, actual, label, a.reviewed_by, head, log)
    results, ok, utext = evaluate(catalogue, golden, actual)
    n_checks = sum(len(v) for v in results.values() if isinstance(v, list))
    n_pass = sum(sum(x['pass'] for x in v) for v in results.values() if isinstance(v, list))
    log('  CT checks: %d/%d passed' % (n_pass, n_checks))
    for ct in catalogue['tests']:
        v = results.get(ct['id'], [])
        if isinstance(v, str):
            log('  %-6s %s' % (ct['id'], v))
        else:
            bad = [x for x in v if not x['pass']]
            log('  %-6s %-4s %3d checks%s' % (ct['id'], 'PASS' if not bad else 'FAIL', len(v),
                                              '' if not bad else '  first: %s :: %s' % (bad[0]['check'], (bad[0]['diff'] or '')[:300])))
    report.update({'ct_results': results, 'ct_all_pass': ok, 'checks_total': n_checks, 'checks_passed': n_pass, 'unittest_output': utext})
    all_ok = ok and all(c['rc'] == 0 for c in caps.values())
    if not a.no_legacy_suite:
        report['legacy_suite'] = run_legacy_suite(pristine, rundir, golden['r1'], log)
        all_ok = all_ok and report['legacy_suite']['equals_stage7_R1']
    if a.mutation_gate:
        ids = [x for x in a.mutants.split(',') if x]
        log('  mutation gate (%s):' % (','.join(ids) or 'M1..M15'))
        mg = mutation_gate(pristine, rundir, catalogue, golden, ids, log)
        killed = sum(m['status'] == 'KILLED' for m in mg)
        log('  mutation gate: %d/%d KILLED' % (killed, len(mg)))
        report['mutation_gate'] = {'results': mg, 'killed': killed, 'total': len(mg)}
        all_ok = all_ok and killed == len(mg)
    report['seconds'] = round(time.time() - t_start, 1)
    report['overall'] = 'PASS' if all_ok else 'FAIL'
    log('OVERALL %s  (%.0fs)' % (report['overall'], report['seconds']))
    report['log'] = lines
    with open(os.path.join(rundir, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=1, sort_keys=True, default=str)
    if not a.keep:
        for x in os.listdir(rundir):
            if x not in ('report.json', 'out'):
                harness.safe_rmtree(os.path.join(rundir, x), sroot)
    print('report: %s' % os.path.join(rundir, 'report.json'))
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
