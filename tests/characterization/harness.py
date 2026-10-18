"""Stage 15 INC-01 characterisation harness - sandbox, fixture and comparison library.

Design (approved OD-11 E-1, HD-1 option B): the UNMODIFIED legacy code is executed only in child
processes whose working directory is a FULL COPY of the repository placed OUTSIDE the working tree.
Nothing in this module imports legacy code. Standard library only.

Safety rules enforced here (OD-03a, Stage 0B STOP-01/02, BEH-CO-04 / AC-CO-06):
  * the sandbox root must not resolve inside the repository working tree, inside the fixture
    source, or be an ancestor of either (E-CO-NOT-SANDBOX);
  * the fixture (data/) is copied from a fixture source (default: the Stage 0A backup) and every
    file is hash-verified against fixtures/FX-BASE125.sha256 before any capture runs (CT-H1);
  * directories are only ever deleted when they are inside the guarded sandbox root.
"""
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.realpath(os.path.join(HERE, '..', '..'))
# The protected working tree. In child processes (which run from the sandbox copy) the runner passes
# the real working-tree path via CHAR_WORKTREE_ROOT so the guard still protects the right directory.
WORKTREE_ROOT = os.path.realpath(os.environ.get('CHAR_WORKTREE_ROOT', REPO_ROOT))
GOLDEN_DIR = os.path.join(HERE, 'golden')
FIXTURE_MANIFEST = os.path.join(HERE, 'fixtures', 'FX-BASE125.sha256')
DEFAULT_SANDBOX_ROOT = os.path.expanduser('~/fde_sbx/s15-inc01')
DEFAULT_FIXTURE_SOURCE = os.environ.get('CHAR_FIXTURE_SOURCE',
                                        os.path.join(os.path.dirname(WORKTREE_ROOT), '_data-backup-2026-10-17'))
BASELINE_DB_SHA256 = 'c254649f57e2f05a0b54229923597a5a82a37633d455270b9ee40577071d70aa'  # OD-09
# top-level entries never copied from the working tree into the sandbox code copy
COPY_EXCLUDE_TOP = {'.git', 'data'}
COPY_EXCLUDE_ANY = shutil.ignore_patterns('__pycache__', '*.pyc', '*.class')


class SandboxGuardError(RuntimeError):
    """E-CO-NOT-SANDBOX: refusing to run because the target is not a safe sandbox."""


class FixtureError(RuntimeError):
    """E-FX-HASH: fixture missing or does not match FX-BASE125 manifest."""


def _real(p):
    return os.path.realpath(os.path.abspath(os.path.expanduser(p)))


def _inside(child, parent):
    child, parent = _real(child), _real(parent)
    return child == parent or child.startswith(parent.rstrip(os.sep) + os.sep)


def assert_safe_sandbox(target, fixture_source=None):
    """Raise SandboxGuardError unless `target` is a safe place to run legacy code."""
    t = _real(target)
    fx = fixture_source or DEFAULT_FIXTURE_SOURCE
    protected = [WORKTREE_ROOT, _real(fx)]
    for p in protected:
        if _inside(t, p):
            raise SandboxGuardError('E-CO-NOT-SANDBOX: %s resolves inside protected path %s' % (t, p))
        if _inside(p, t):
            raise SandboxGuardError('E-CO-NOT-SANDBOX: %s is an ancestor of protected path %s' % (t, p))
    if t in ('/', _real('~')):
        raise SandboxGuardError('E-CO-NOT-SANDBOX: refusing filesystem/home root %s' % t)
    return t


def safe_rmtree(path, sandbox_root):
    """Delete `path` only if it is strictly inside the (guarded) sandbox root."""
    root = assert_safe_sandbox(sandbox_root)
    p = _real(path)
    if p == root or not _inside(p, root):
        raise SandboxGuardError('refusing to delete %s (not strictly inside sandbox %s)' % (p, root))
    assert_safe_sandbox(p)
    shutil.rmtree(p, ignore_errors=True)


def sha256_file(path, bufsize=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(bufsize), b''):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path=FIXTURE_MANIFEST):
    out = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            digest, rel = line.split(None, 1)
            rel = rel.lstrip('*')
            out[rel[2:] if rel.startswith('./') else rel] = digest
    return out


def verify_fixture(copy_root, manifest=None):
    """CT-H1 hash gate: every manifest file must exist under copy_root with the pinned sha256,
    and data/ must contain no extra file. Returns a summary dict; raises FixtureError on mismatch."""
    manifest = manifest or load_manifest()
    bad, missing = [], []
    for rel, digest in sorted(manifest.items()):
        p = os.path.join(copy_root, rel)
        if not os.path.isfile(p):
            missing.append(rel)
        elif sha256_file(p) != digest:
            bad.append(rel)
    extra = []
    for d, _, files in os.walk(os.path.join(copy_root, 'data')):
        for fn in files:
            rel = os.path.relpath(os.path.join(d, fn), copy_root)
            if rel not in manifest:
                extra.append(rel)
    if bad or missing or extra:
        raise FixtureError('E-FX-HASH: fixture mismatch missing=%d bad=%d extra=%d first=%s' % (
            len(missing), len(bad), len(extra), (missing + bad + extra)[:5]))
    return {'files_verified': len(manifest), 'legacy_db_sha256': manifest.get('data/legacy.sqlite3')}


def build_pristine(sandbox_root, name, fixture_source=DEFAULT_FIXTURE_SOURCE, source_root=WORKTREE_ROOT):
    """Create <sandbox_root>/<name>: code copied from the working tree (read-only, excluding .git
    and data/), data/ copied from the fixture source, then hash-gated. Returns its path."""
    root = assert_safe_sandbox(sandbox_root, fixture_source)
    os.makedirs(root, exist_ok=True)
    dest = os.path.join(root, name)
    if os.path.exists(dest):
        safe_rmtree(dest, root)
    os.makedirs(dest)
    for entry in sorted(os.listdir(source_root)):
        if entry in COPY_EXCLUDE_TOP:
            continue
        s, d = os.path.join(source_root, entry), os.path.join(dest, entry)
        if os.path.isdir(s) and not os.path.islink(s):
            shutil.copytree(s, d, symlinks=True, ignore=COPY_EXCLUDE_ANY)
        else:
            shutil.copy2(s, d, follow_symlinks=False)
    fx_data = os.path.join(fixture_source, 'data')
    if not os.path.isdir(fx_data):
        raise FixtureError('E-FX-MISSING: fixture source has no data/: %s' % fixture_source)
    shutil.copytree(fx_data, os.path.join(dest, 'data'), symlinks=True)
    verify_fixture(dest)
    if sha256_file(os.path.join(dest, 'data', 'legacy.sqlite3')) != BASELINE_DB_SHA256:
        raise FixtureError('E-FX-HASH: legacy.sqlite3 is not the OD-09 baseline')
    return dest


def clone(pristine, sandbox_root, name):
    root = assert_safe_sandbox(sandbox_root)
    dest = os.path.join(root, name)
    if os.path.exists(dest):
        safe_rmtree(dest, root)
    shutil.copytree(pristine, dest, symlinks=True)
    return dest


def child_env(extra=None):
    """Environment for every legacy child process: deterministic hashing, no bytecode, and no
    inherited LEGACY_DB/HOST/PORT that could point at the working tree."""
    env = dict(os.environ)
    for k in ('LEGACY_DB', 'HOST', 'PORT', 'SOURCE_PORT', 'PYTHONPATH'):
        env.pop(k, None)
    env.update({'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1'})
    if extra:
        env.update(extra)
    return env


# ---------------------------------------------------------------- CT-H3 normalisation
# Every rule below is a D1 NORMALISED class (Stage 14 TG-4). Changing this list needs a reviewed PR.
NORMALISATION_RULES = [
    ('N1', 'absolute sandbox copy paths (Stage 7 ~/fde_sbx/stage7/c_*, INC-01 ~/fde_sbx/<run>/c_*) -> <SBX>'),
    ('N2', 'python interpreter path in recorded command lines (sys.executable / /usr/bin/python3) -> <PY>'),
    ('N3', 'JVM banner line "Picked up JAVA_TOOL_OPTIONS: ..." (device proxy agent, environment-only) removed'),
    ('N4', 'tail-truncated stderr fields (stderr[-800:], err[-200:], stderr[-200:]): compared on the common '
           'suffix after N1-N3 when the raw capture hit the truncation cap (window start shifts with path length)'),
]
_SBX_RE = re.compile(r"/[^\s\"'\\:]*?/fde_sbx/(?:[^\s\"'\\:/]+/)*?c_[A-Za-z0-9_]+(?=[/\s\"'\\:]|$)")
_JTO_RE = re.compile(r'Picked up JAVA_TOOL_OPTIONS:[^\n]*\n?')
_PY_RE = re.compile(r'(?<![\w/])(?:/usr/bin/python3(?:\.10)?|' + re.escape(sys.executable) + r')(?= -m | -c |\s)')


def norm_str(s):
    s = _SBX_RE.sub('<SBX>', s)
    s = _JTO_RE.sub('', s)
    s = _PY_RE.sub('<PY>', s)
    return s


def normalise(obj):
    if isinstance(obj, str):
        return norm_str(obj)
    if isinstance(obj, list):
        return [normalise(x) for x in obj]
    if isinstance(obj, dict):
        return {k: normalise(v) for k, v in obj.items()}
    return obj


TAIL_KEYS = {'stderr': 800, 'err': 200}


def _tail_equal(a, b):
    a2, b2 = norm_str(a), norm_str(b)
    if a2 == b2:
        return True
    n = min(len(a2), len(b2))
    return n >= 80 and a2[-n:] == b2[-n:]


def equal(golden, actual, key=None, raw_len_cap=None):
    """Deep compare after normalisation; N4 applies only to known tail-truncated keys."""
    if isinstance(golden, dict) and isinstance(actual, dict):
        if set(golden) != set(actual):
            return False
        for k in golden:
            g, a = golden[k], actual[k]
            if k in TAIL_KEYS and isinstance(g, str) and isinstance(a, str):
                if not _tail_equal(g, a):
                    return False
            elif not equal(g, a, k):
                return False
        return True
    if isinstance(golden, list) and isinstance(actual, list):
        return len(golden) == len(actual) and all(equal(g, a) for g, a in zip(golden, actual))
    return normalise(golden) == normalise(actual)


def first_diff(golden, actual, path='$'):
    """Human-readable first difference (for reports)."""
    if isinstance(golden, dict) and isinstance(actual, dict):
        for k in sorted(set(golden) | set(actual)):
            if k not in actual:
                return '%s.%s missing in actual' % (path, k)
            if k not in golden:
                return '%s.%s unexpected in actual' % (path, k)
            if k in TAIL_KEYS and isinstance(golden[k], str) and isinstance(actual[k], str):
                if not _tail_equal(golden[k], actual[k]):
                    return '%s.%s tail differs: golden=%r actual=%r' % (path, k, norm_str(golden[k])[-160:], norm_str(actual[k])[-160:])
                continue
            d = first_diff(golden[k], actual[k], '%s.%s' % (path, k))
            if d:
                return d
        return None
    if isinstance(golden, list) and isinstance(actual, list):
        if len(golden) != len(actual):
            return '%s length golden=%d actual=%d' % (path, len(golden), len(actual))
        for i, (g, a) in enumerate(zip(golden, actual)):
            d = first_diff(g, a, '%s[%d]' % (path, i))
            if d:
                return d
        return None
    if normalise(golden) != normalise(actual):
        return '%s golden=%s actual=%s' % (path, json.dumps(normalise(golden))[:200], json.dumps(normalise(actual))[:200])
    return None


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


DIGEST_TAIL_CHARS = 400


def _canon(obj, key=None):
    if isinstance(obj, str):
        s = norm_str(obj)
        # N4 for digests: a tail-truncated field's window start depends on the sandbox path length,
        # so the run digest keeps only the last DIGEST_TAIL_CHARS normalised characters of such fields.
        return s[-DIGEST_TAIL_CHARS:] if key in TAIL_KEYS else s
    if isinstance(obj, list):
        return [_canon(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _canon(v, k) for k, v in obj.items()}
    return obj


def canonical_bytes(obj):
    """Normalised, path-independent serialisation used for the determinism digest (CG-6)."""
    return json.dumps(_canon(obj), sort_keys=True, indent=1, default=str).encode('utf-8')
