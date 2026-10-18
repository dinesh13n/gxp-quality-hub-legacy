"""Shared helpers for capture scripts. Capture scripts run ONLY as child processes started by
run_characterization.py, from the sandbox copy of tests/characterization (never the working tree)."""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import harness  # noqa: E402


def args():
    """argv: SRC (hash-gated pristine copy) WORK (scratch dir inside sandbox) OUT (json path)."""
    if len(sys.argv) != 4:
        sys.exit('usage: %s SRC WORK OUT' % sys.argv[0])
    src, work, out = (os.path.realpath(a) for a in sys.argv[1:4])
    harness.assert_safe_sandbox(HERE)  # the capture code itself must be running from a sandbox copy
    harness.assert_safe_sandbox(src)
    harness.assert_safe_sandbox(work)
    os.makedirs(work, exist_ok=True)
    return src, work, out
