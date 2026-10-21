"""`python -m hub.control [--config FILE] <command>` - Stage 23 human-control operator commands (DW-13, DW-17). Host operator only.

  registry [--out DIR | --check DIR]       generate the error-code registry from the code (JSON + Markdown), or diff it against DIR (exit 1 on a difference)
  flags                                    every registered decision flag: default, effective value, approval reference present (read-only)
  set-flag --flag K --value JSON --approval-ref R --data-dir D
                                           change one decision flag in the config FILE: refused without --approval-ref unless the new value is the
                                           default; the new config must validate; a CONFIG_CHANGED audit record (old / new / approval_ref) is written
  flip-to-shadow --capability C --reason T --data-dir D
                                           L3 rollback: capability_authority.C back to `shadow` (no approval needed), audited CONFIG_CHANGED
The approval reference is a pointer to a human decision recorded elsewhere (e.g. an orchestrator-decisions OD id); the hub does not and cannot verify it.
Same guards as hub.admin (egress guard, runtime floor, hub.kill, CONFIG_LOADED audit, anchor at the end). No model call, no network.
"""
import argparse
import copy
import json
import os
import sys

from hub.admin.cli import _Run, _dump
from hub.core.errors import ConfigInvalid, HubError, RuntimeUnsupported


def _parser():
    ap = argparse.ArgumentParser(prog="python -m hub.control", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--correlation-id", default=None)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("registry")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--out", default=None)
    g.add_argument("--check", default=None)
    sub.add_parser("flags")
    p = sub.add_parser("set-flag")
    p.add_argument("--flag", required=True)
    p.add_argument("--value", required=True)
    p.add_argument("--approval-ref", default=None)
    p.add_argument("--data-dir", required=True)
    p = sub.add_parser("flip-to-shadow")
    p.add_argument("--capability", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--data-dir", required=True)
    return ap


def _read_file(path):
    if not path:
        raise ConfigInvalid({"config": None, "reason": "this command edits the config FILE: give --config FILE"})
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _set_path(cfg, path, value):
    cur = cfg
    parts = path.split(".")
    for part in parts[:-1]:
        if not isinstance(cur.get(part), dict):
            cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value


def _write_atomic(path, doc):
    tmp = path + ".new"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, sort_keys=True, indent=1)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _parse_value(text):
    try:
        return json.loads(text)
    except ValueError:
        return text


def _change(r, flag, new, approval_ref, source, extra):
    """Validate the candidate config FILE content, audit CONFIG_CHANGED, then replace the file atomically."""
    from hub import config
    from hub.control import flags, switch
    from hub.security import settings
    doc = _read_file(r.args.config)
    old = flags.effective(r.cfg, flag)
    cand = copy.deepcopy(doc)
    _set_path(cand, flag, new)
    refs = cand.setdefault(flags.APPROVALS_KEY, {})
    to_default = new == flags.default_of(flag) and type(new) is type(flags.default_of(flag))
    if to_default:
        refs.pop(flag, None)
    else:
        if not flags.valid_ref(approval_ref):
            raise ConfigInvalid({"flag": flag, "value": new, "reason": "--approval-ref is required for a non-default value (FF-2 rule 3, HAR-11)"})
        refs[flag] = approval_ref.strip()
    if not refs:
        cand.pop(flags.APPROVALS_KEY)
    new_cfg = config.load(None, cand)  # the candidate must validate exactly as the next start-up will
    if old == new:
        return {"changed": False, "flag": flag, "value": new, "reason": "already at this value"}
    rec = switch.change_record(r.con, r.clock, r.anchor, r.operator, "human", r.cid, flag, old, new, None if to_default else approval_ref.strip(), source,
                               dict(extra, config_hash_before=settings.config_hash(r.cfg), config_hash_after=settings.config_hash(new_cfg), command=r.args.cmd))
    _write_atomic(r.args.config, cand)
    return {"changed": True, "flag": flag, "old": old, "new": new, "approval_ref": None if to_default else approval_ref.strip(),
            "audit_seq": rec["audit_seq"], "direction": "to_default" if to_default else "to_non_default"}


def _cmd(r, a):
    from hub.control import flags, registry
    if a.cmd == "registry":
        reg = registry.build()
        if a.check:
            problems = registry.diff_against(reg, os.path.abspath(a.check)) + reg["exit_code_problems"]
            return {"match": not problems, "problems": problems, "count": reg["count"]}, (0 if not problems else 1)
        if a.out:
            return {"written": [os.path.basename(p) for p in registry.write(reg, os.path.abspath(a.out))], "count": reg["count"],
                    "exit_code_problems": reg["exit_code_problems"]}, 0
        return reg, 0
    if a.cmd == "flags":
        refs = r.cfg.get(flags.APPROVALS_KEY) or {}
        rows = [{"flag": p, "default": d, "value": flags.get(r.cfg, p, d), "approval": link,
                 "approval_ref_present": flags.valid_ref(refs.get(p))} for p, d, link in flags.DECISION_FLAGS]
        caps = r.cfg.get(flags.AUTHORITY_KEY) or {}
        rows += [{"flag": flags.AUTHORITY_KEY + "." + c, "default": flags.AUTHORITY_DEFAULT, "value": v, "approval": flags.AUTHORITY_LINK,
                  "approval_ref_present": flags.valid_ref(refs.get(flags.AUTHORITY_KEY + "." + c))} for c, v in sorted(caps.items())]
        return {"flags": rows, "other_controls": [{"flag": p, "control": c} for p, c in flags.OTHER_CONTROLS],
                "non_default": [p for p, _, _ in flags.nondefault(r.cfg)]}, 0
    if a.cmd == "set-flag":
        if not flags.is_registered(a.flag):
            raise ConfigInvalid({"flag": a.flag[:80], "reason": "not a registered decision flag (python -m hub.control flags)"})
        r.open_store()
        return _change(r, a.flag, _parse_value(a.value), a.approval_ref, "hub.control set-flag", {}), 0
    if a.cmd == "flip-to-shadow":
        if not a.reason.strip():
            raise ConfigInvalid({"reason": "a non-empty --reason is required"})
        r.open_store()
        flag = flags.AUTHORITY_KEY + "." + a.capability
        return _change(r, flag, flags.AUTHORITY_DEFAULT, None, "hub.control flip-to-shadow", {"rollback": "L3", "reason": a.reason.strip()[:300]}), 0
    raise SystemExit(2)


def main(argv=None):
    from hub.guards import egress
    from hub.obs import log as hublog, metrics
    egress.install()
    metrics.reset()
    ap = _parser()
    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_help()
        return 2
    r, rc, cid = None, 0, args.correlation_id
    try:
        r = _Run(args)
        cid = r.cid
        out, rc = _cmd(r, args)
        r.close()
        print(_dump(out))
    except RuntimeUnsupported as e:
        sys.stderr.write(_dump(hublog.envelope_with_correlation(e, cid)) + "\n")
        return e.exit_code
    except HubError as e:
        if r is not None:
            try:
                r.close()
            except Exception:  # noqa: BLE001
                pass
        sys.stderr.write(_dump(hublog.envelope_with_correlation(e, cid)) + "\n")
        rc = e.exit_code
    try:
        metrics.check_tripwires()
    except HubError as e:
        sys.stderr.write(_dump(e.envelope()) + "\n")
        rc = rc or e.exit_code
    return rc
