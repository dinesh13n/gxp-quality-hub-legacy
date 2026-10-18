"""Sandbox guard (BEH-CO-04, AC-CO-06, OD-03a, Stage 0B WB-06/STOP-01/STOP-02).

A hub data directory, a run directory or a legacy source used by an adapter must NOT resolve inside a
protected location:
  * the original repository working tree (HUB_WORKTREE_ROOT, and any ancestor directory holding `.git`);
  * the package root when it is itself a git working tree (i.e. code not running from a sandbox copy);
  * the Stage 0A backup (`<worktree>/../_data-backup-2026-10-17`, or HUB_BACKUP_ROOT);
and must not be an ancestor of one of them, the filesystem root or $HOME. Violations raise E-CO-NOT-SANDBOX
(exit 7) before anything is created.
"""
import hashlib
import os

from hub.core.errors import NotSandbox

PACKAGE_ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BACKUP_DIRNAME = "_data-backup-2026-10-17"


def real(p):
    return os.path.realpath(os.path.abspath(os.path.expanduser(p)))


def inside(child, parent):
    child, parent = real(child), real(parent)
    return child == parent or child.startswith(parent.rstrip(os.sep) + os.sep)


def _git_ancestor(path):
    p = real(path)
    while True:
        if os.path.exists(os.path.join(p, ".git")):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            return None
        p = parent


def worktree_root():
    env = os.environ.get("HUB_WORKTREE_ROOT")
    if env:
        return real(env)
    return _git_ancestor(PACKAGE_ROOT)


def protected_roots():
    roots = []
    wt = worktree_root()
    if wt:
        roots.append(wt)
        roots.append(real(os.path.join(os.path.dirname(wt), BACKUP_DIRNAME)))
    if os.environ.get("HUB_BACKUP_ROOT"):
        roots.append(real(os.environ["HUB_BACKUP_ROOT"]))
    if os.path.exists(os.path.join(PACKAGE_ROOT, ".git")):
        roots.append(PACKAGE_ROOT)
    out = []
    for r in roots:
        if r not in out:
            out.append(r)
    return out


def assert_safe_path(path, what="data directory"):
    """Raise E-CO-NOT-SANDBOX unless `path` is outside every protected root. Returns the real path."""
    t = real(path)
    if t in ("/", real("~")):
        raise NotSandbox({"what": what, "path": t, "reason": "filesystem or home root"})
    ga = _git_ancestor(t)
    if ga:
        raise NotSandbox({"what": what, "path": t, "reason": "inside a git working tree", "root": ga})
    for root in protected_roots():
        if inside(t, root):
            raise NotSandbox({"what": what, "path": t, "reason": "inside protected path", "root": root})
        if inside(root, t):
            raise NotSandbox({"what": what, "path": t, "reason": "ancestor of protected path", "root": root})
    return t


def running_from_sandbox_copy():
    """True when the hub package itself is not loaded from the original working tree."""
    if os.path.exists(os.path.join(PACKAGE_ROOT, ".git")):
        return False
    wt = worktree_root()
    return not (wt and inside(PACKAGE_ROOT, wt))


def assert_running_in_sandbox():
    if not running_from_sandbox_copy():
        raise NotSandbox({"what": "hub code", "path": PACKAGE_ROOT,
                          "reason": "tests/executions must run from a sandbox copy (OD-03a)"})
    return PACKAGE_ROOT


def verify_backup_manifest(worktree):
    """Python equivalent of `sha256sum -c --quiet ../_data-backup-2026-10-17/SHA256SUMS.txt` run from the
    repository root (read-only hashing). Returns (entries, failures)."""
    manifest = os.path.join(os.path.dirname(real(worktree)), BACKUP_DIRNAME, "SHA256SUMS.txt")
    entries, failures = 0, []
    with open(manifest, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            digest, rel = line.split(None, 1)
            rel = rel.lstrip("*")
            entries += 1
            p = os.path.join(real(worktree), rel)
            if not os.path.isfile(p):
                failures.append(rel)
                continue
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
            if h.hexdigest() != digest:
                failures.append(rel)
    return entries, failures
