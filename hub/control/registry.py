"""Generated error-code registry (Stage 23 DW-13; IC-1 / IC-2 of the Stage 12 v0.2 addendum).

The authoritative list is the code. This module finds every class that defines an error `code` (AST walk of hub/**/*.py, nothing is run),
imports only those modules, and reads code / exit_code / http / message from the HubError subclasses. The Stage 12 error-handling-spec is
read only to mark which codes the 82-code spec already had. Output is deterministic (no timestamps): the generator test regenerates it and
diffs it against the committed docs/23-human-control/stage12-v0.2/error-code-registry.json (diff 0).

Exit codes: a code shared by more than one error AREA (E-<AREA>-...) is a clash unless it is a documented family. OD-29 (DQ-04): the
clashes on 2 and 9 are DOCUMENTED and the numbers KEPT; the check below fails on any clash that is not in KNOWN_CLASHES, and on a documented
clash that no longer exists (a silent renumbering).
"""
import ast
import importlib
import inspect
import json
import os
import re

KNOWN_CLASHES = {
    2: "usage / E-FX-HASH / E-CFG-INVALID / E-AUTH-PASSWORD-POLICY share exit 2 (INC-02 / INC-03 choices; RTD-21)",
    9: "E-CO-DENYLIST-IMPORT (INC-02) and E-SEC-EXPOSURE-NOT-APPROVED (as specified) share exit 9 (RTD-24, DEV-23)",
}
KNOWN_FAMILIES = {
    19: "access-refusal family: E-AUTH-*, E-GATE-NO-HOLDERS / NOT-AUTHORISED / REAUTH-REQUIRED / UNKNOWN-ACTION, E-SEC-CSRF, E-SEC-REASON-REQUIRED (INC-03 / 04 / 08 / 09)",
    31: "request / gate / reviewer family: E-GATE-* payload and mode errors, E-REQ-*, E-REV-* (INC-08)",
    32: "R2 family: E-R2-INPUT-INVALID, E-REV-INDEX-ABSENT (INC-09)",
}
SPEC_FILE = os.path.join("docs", "12-specs", "error-handling-spec.md")
CODE_RE = re.compile(r"^E-[A-Z0-9]+(?:-[A-Z0-9]+)+$")


def repo_root():
    import hub
    return os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(hub.__file__)), ".."))


def _defines_code(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for st in node.body:
                if isinstance(st, ast.Assign):
                    for t in st.targets:
                        names = [e.id for e in t.elts if isinstance(e, ast.Name)] if isinstance(t, ast.Tuple) else ([t.id] if isinstance(t, ast.Name) else [])
                        if "code" in names:
                            return True
    return False


def error_modules(root):
    mods = []
    base = os.path.join(root, "hub")
    for d, dirs, fns in os.walk(base):
        dirs[:] = sorted(x for x in dirs if x != "__pycache__")
        for fn in sorted(fns):
            if fn.endswith(".py"):
                p = os.path.join(d, fn)
                with open(p, encoding="utf-8") as f:
                    tree = ast.parse(f.read(), p)
                if _defines_code(tree):
                    rel = os.path.relpath(p, root)[:-3].split(os.sep)
                    mods.append(".".join(rel[:-1] if rel[-1] == "__init__" else rel))
    return sorted(mods)


def spec_codes(root):
    p = os.path.join(root, SPEC_FILE)
    if not os.path.exists(p):
        return None
    out = set()
    with open(p, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\|\s*(E-[A-Z0-9-]+)\s*\|", line)
            if m:
                out.add(m.group(1))
    return out


def collect(root=None):
    from hub.core.errors import HubError
    root = root or repo_root()
    spec = spec_codes(root)
    rows = {}
    for mod in error_modules(root):
        m = importlib.import_module(mod)
        for name, cls in sorted(vars(m).items()):
            if inspect.isclass(cls) and issubclass(cls, HubError) and cls.__module__ == mod and "code" in vars(cls):
                code = cls.code
                if not CODE_RE.match(code):
                    raise ValueError("bad error code %r in %s" % (code, mod))
                if code in rows:  # one code, several classes (E-RUN-UNKNOWN-JOB: unknown job / unknown run id) - same module, same exit and http
                    r = rows[code]
                    if r["module"] != mod or r["exit_code"] != cls.exit_code or r["http"] != getattr(cls, "http", None):
                        raise ValueError("error code %s defined inconsistently (%s, %s)" % (code, r["module"], mod))
                    r["classes"].append(name)
                    r["messages"].append(cls.message)
                    continue
                rows[code] = {"code": code, "classes": [name], "module": mod, "area": code.split("-")[1], "exit_code": cls.exit_code,
                              "http": getattr(cls, "http", None), "messages": [cls.message],
                              "in_stage12_spec": None if spec is None else code in spec}
    return [rows[k] for k in sorted(rows)]


def referenced_only(root, defined):
    """Error-code string literals in hub/**/*.py that are not an error class: {code: [files]} (informational codes, retryable lists)."""
    lit = re.compile(r'"(E-[A-Z0-9]+(?:-[A-Z0-9]+)+)"')
    found = {}
    base = os.path.join(root, "hub")
    for d, dirs, fns in os.walk(base):
        dirs[:] = sorted(x for x in dirs if x != "__pycache__")
        for fn in sorted(fns):
            if fn.endswith(".py"):
                p = os.path.join(d, fn)
                with open(p, encoding="utf-8") as f:
                    for code in lit.findall(f.read()):
                        if code not in defined:
                            found.setdefault(code, set()).add(os.path.relpath(p, root).replace(os.sep, "/"))
    return dict((c, sorted(v)) for c, v in sorted(found.items()))


def exit_table(codes):
    by = {}
    for r in codes:
        by.setdefault(r["exit_code"], []).append(r)
    out = []
    for ex in sorted(by):
        rs = by[ex]
        areas = sorted(set(r["area"] for r in rs))
        if len(areas) > 1:
            cls = "documented_clash" if ex in KNOWN_CLASHES else ("documented_family" if ex in KNOWN_FAMILIES else "UNDOCUMENTED_CLASH")
        else:
            cls = "unique" if len(rs) == 1 else "shared_within_area"
        out.append({"exit_code": ex, "codes": [r["code"] for r in rs], "areas": areas, "classification": cls,
                    "note": KNOWN_CLASHES.get(ex) or KNOWN_FAMILIES.get(ex)})
    return out


def check_exit_codes(codes):
    """Problems with the exit-code map ([] = fine): an undocumented clash, or a documented clash that is gone (silent renumbering)."""
    table = dict((e["exit_code"], e) for e in exit_table(codes))
    problems = ["undocumented clash on exit %d: %s" % (e["exit_code"], e["codes"]) for e in table.values() if e["classification"] == "UNDOCUMENTED_CLASH"]
    for ex in sorted(KNOWN_CLASHES):
        if ex not in table or table[ex]["classification"] != "documented_clash":
            problems.append("documented clash on exit %d no longer present (numbers are KEPT, OD-29)" % ex)
    for ex in sorted(KNOWN_FAMILIES):
        if ex not in table or table[ex]["classification"] != "documented_family":
            problems.append("documented family on exit %d no longer present" % ex)
    return problems


def build(root=None):
    root = root or repo_root()
    codes = collect(root)
    spec = spec_codes(root)
    return {"referenced_only": referenced_only(root, set(r["code"] for r in codes)), "schema": "hub-error-registry/v1", "spec_codes_not_in_code": None if spec is None else sorted(spec - set(r["code"] for r in codes)), "source": "hub/**/*.py: HubError subclasses that define `code` (generated by python -m hub.control registry)",
            "count": len(codes), "in_stage12_spec": sum(1 for r in codes if r["in_stage12_spec"]),
            "added_beyond_stage12_spec": sum(1 for r in codes if r["in_stage12_spec"] is False),
            "codes": codes, "exit_codes": exit_table(codes), "exit_code_problems": check_exit_codes(codes)}


def to_json(reg):
    return json.dumps(reg, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def to_markdown(reg):
    L = ["<!-- generated by `python -m hub.control registry`; do not edit by hand (Stage 23 DW-13) -->", "",
         "Error codes: %d (in the Stage 12 spec: %s, added by the build: %s). Spec codes with no class in the code: %s. Code literals that are not an error class: %s." % (
             reg["count"], reg["in_stage12_spec"], reg["added_beyond_stage12_spec"], ", ".join(reg["spec_codes_not_in_code"] or []) or "none",
             ", ".join(reg["referenced_only"]) or "none"), "",
         "| Code | Exit | HTTP | In Stage 12 spec | Module | Message |", "|---|---|---|---|---|---|"]
    for r in reg["codes"]:
        L.append("| %s | %s | %s | %s | `%s` | %s |" % (r["code"], r["exit_code"], r["http"] if r["http"] is not None else "-",
                                                         {True: "yes", False: "no", None: "?"}[r["in_stage12_spec"]], r["module"], " / ".join(r["messages"])))
    L += ["", "| Exit | Codes | Classification | Note |", "|---|---|---|---|"]
    for e in reg["exit_codes"]:
        L.append("| %d | %s | %s | %s |" % (e["exit_code"], ", ".join(e["codes"]), e["classification"], e["note"] or ""))
    return "\n".join(L) + "\n"


def write(reg, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    paths = (os.path.join(out_dir, "error-code-registry.json"), os.path.join(out_dir, "error-code-registry.md"))
    for p, text in zip(paths, (to_json(reg), to_markdown(reg))):
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
    return paths


def diff_against(reg, out_dir):
    """[] when the committed JSON and Markdown equal the regenerated ones; otherwise a list of differences."""
    problems = []
    for name, text in (("error-code-registry.json", to_json(reg)), ("error-code-registry.md", to_markdown(reg))):
        p = os.path.join(out_dir, name)
        if not os.path.exists(p):
            problems.append("%s missing" % name)
            continue
        with open(p, encoding="utf-8") as f:
            if f.read() != text:
                problems.append("%s differs from the generated registry" % name)
    return problems
