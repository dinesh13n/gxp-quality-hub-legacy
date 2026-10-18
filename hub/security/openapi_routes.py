"""Minimal, stdlib-only reader of the route table in docs/12-specs/contracts/openapi.yaml (OpenAPI 3.0.3 as
written by Stage 12): path -> method -> {x-op-id, x-roles}. Used to (re)generate and cross-check
hub/security/route_registry.json (BEH-SEC-01 route-registry test, AC-SEC-01). Not a general YAML parser."""
import re

_PATH = re.compile(r"^  (/\S*):\s*$")
_METHOD = re.compile(r"^    (get|post|put|patch|delete|head|options):\s*$")
_OPID = re.compile(r"^      x-op-id:\s*(\S+)\s*$")
_ROLES = re.compile(r"^      x-roles:\s*$")
_ITEM = re.compile(r"^      - (\S+)\s*$")


def parse(text):
    routes, path, cur, in_roles, in_paths = [], None, None, False, False
    for line in text.splitlines():
        if line.startswith("paths:"):
            in_paths = True
            continue
        if in_paths and line and not line.startswith(" "):
            in_paths = False
        if not in_paths:
            continue
        m = _PATH.match(line)
        if m:
            path, cur, in_roles = m.group(1), None, False
            continue
        m = _METHOD.match(line)
        if m and path:
            cur = {"path": path, "method": m.group(1).upper(), "op_id": None, "roles": []}
            routes.append(cur)
            in_roles = False
            continue
        if cur is None:
            continue
        m = _OPID.match(line)
        if m:
            cur["op_id"] = m.group(1)
            in_roles = False
            continue
        if _ROLES.match(line):
            in_roles = True
            continue
        if in_roles:
            m = _ITEM.match(line)
            if m:
                cur["roles"].append(m.group(1))
            else:
                in_roles = False
    for r in routes:
        r["roles"] = sorted(set(r["roles"]))
    return sorted(routes, key=lambda r: (r["path"], r["method"]))
