"""Shared helpers for the Stage 15 INC-02 hub tests (stdlib unittest).

These tests must only run from a SANDBOX COPY built by tests/hub/run_hub_tests.py (OD-03a): the runner sets
HUB_WORKTREE_ROOT (the original working tree, used read-only for git/sha256 checks), HUB_SANDBOX_ROOT
(scratch space) and HUB_LEGACY_ROOT (the hash-gated FX-BASE125 sandbox copy). `require_sandbox()` refuses
otherwise. This directory has no __init__.py, so the shipped `python -m unittest discover -s tests` (CI,
scripts/verify.sh) does not collect it.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_ROOT = os.path.realpath(os.path.join(HERE, "..", ".."))
if CODE_ROOT not in sys.path:
    sys.path.insert(0, CODE_ROOT)

from hub.guards import sandbox  # noqa: E402

WORKTREE = os.environ.get("HUB_WORKTREE_ROOT")
SANDBOX_ROOT = os.environ.get("HUB_SANDBOX_ROOT")
LEGACY_ROOT = os.environ.get("HUB_LEGACY_ROOT")
BACKUP_MANIFEST_REL = os.path.join("..", "_data-backup-2026-10-17", "SHA256SUMS.txt")
DV_IDS = ["DV-%02d" % i for i in range(1, 10)]


def require_sandbox():
    missing = [k for k in ("HUB_WORKTREE_ROOT", "HUB_SANDBOX_ROOT", "HUB_LEGACY_ROOT") if not os.environ.get(k)]
    if missing:
        raise RuntimeError("run via tests/hub/run_hub_tests.py (missing %s)" % missing)
    sandbox.assert_running_in_sandbox()
    sandbox.assert_safe_path(SANDBOX_ROOT, "sandbox root")
    sandbox.assert_safe_path(LEGACY_ROOT, "legacy root")


def tmpdir(prefix):
    base = os.path.join(SANDBOX_ROOT, "tmp")
    os.makedirs(base, exist_ok=True)
    return tempfile.mkdtemp(prefix=prefix, dir=base)


def child_env(extra=None):
    env = dict(os.environ)
    for k in ("LEGACY_DB", "HOST", "PORT", "SOURCE_PORT", "PYTHONPATH"):
        env.pop(k, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if extra:
        env.update(extra)
    return env


def run_hub(args, extra_env=None, cwd=CODE_ROOT, timeout=150):
    return subprocess.run([sys.executable, "-B", "-m", "hub"] + list(args), cwd=cwd, env=child_env(extra_env),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)


def error_code(proc):
    try:
        return json.loads(proc.stderr)["code"]
    except ValueError:
        return None


def golden_compare(data_dir, *extra, **kw):
    args = ["golden-compare", "--json", "--data-dir", data_dir]
    if kw.get("legacy", True):
        args += ["--legacy-root", LEGACY_ROOT]
    return run_hub(args + list(extra), extra_env=kw.get("env"))


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    with open(path, "rb") as f:
        return sha256_bytes(f.read())
