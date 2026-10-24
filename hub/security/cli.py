"""`python -m hub.security <command>` - Stage 24 security operator commands (DW-19). Host operator only; read-only except `seal`. No store, no network.

  controls                                  the register of security control values (hub/security/controls.py): shipped value, floor, status PROPOSED, drift
  tables                                    the table disposition register (hub/security/tables.py): retained / mutable / derived, and the count per disposition
  seal --anchor-path P [--seal-path S]      opt-in HMAC seal of the audit anchor file; key from the environment variable HUB_ANCHOR_SEAL_KEY
  check-seal --anchor-path P [--seal-path S]  verify the seal (exit 17 = E-SEC-AUDIT-TAMPER-DETECTED if an anchor line was altered / the anchor truncated)
Exit codes are the existing registry ones (ConfigInvalid, E-SEC-AUDIT-TAMPER-DETECTED 17). Same egress guard as hub.admin. The key is never echoed or logged.
"""
import argparse
import json
import os
import sys

from hub.core.errors import HubError


def _dump(obj):
    return json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False, default=str)


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.security", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("controls")
    sub.add_parser("tables")
    for name in ("seal", "check-seal"):
        p = sub.add_parser(name)
        p.add_argument("--anchor-path", required=True)
        p.add_argument("--seal-path", default=None)
    return ap


def _cmd(a):
    from hub.security import anchor_seal, controls, tables
    if a.cmd == "controls":
        return controls.report(), 1 if controls.drift() else 0
    if a.cmd == "tables":
        counts = {}
        for _t, (d, _r) in tables.TABLES.items():
            counts[d] = counts.get(d, 0) + 1
        return {"label": "synthetic, unvalidated", "counts": counts,
                "tables": [{"table": t, "disposition": d, "reason": r} for t, (d, r) in sorted(tables.TABLES.items())],
                "reviewed_delete_sites": [{"file": f, "table": t, "statements": n} for (f, t), n in sorted(tables.REVIEWED_DELETE_SITES.items())]}, 0
    key = anchor_seal.load_key()
    path = os.path.abspath(a.anchor_path)
    sp = os.path.abspath(a.seal_path) if a.seal_path else None
    if a.cmd == "seal":
        return anchor_seal.seal(path, key, sp), 0
    rep = anchor_seal.check(path, key, sp)
    if rep["status"] != "ok":
        from hub.security.errors import AuditTamperDetected
        raise AuditTamperDetected(rep)
    return rep, 0


def main(argv=None):
    from hub.guards import egress
    egress.install()
    ap = _parser()
    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_help()
        return 2
    try:
        out, rc = _cmd(args)
        print(_dump(out))
        return rc
    except HubError as e:
        sys.stderr.write(_dump(e.envelope()) + "\n")
        return e.exit_code
    except (OSError, ValueError) as e:
        sys.stderr.write(_dump(HubError({"error": type(e).__name__}).envelope()) + "\n")
        return 1
