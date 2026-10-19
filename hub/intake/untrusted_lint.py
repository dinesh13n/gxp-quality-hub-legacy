"""Static check for the Untrusted type (AC-INT-23, BEH-INT-09, ADR-002 option B(3)): a heuristic AST pass over product source.

Rules (each finding: path, line, rule, detail):
  U1  a call passes a value derived from `Untrusted(...)` / `untrusted_text(...)` / `.for_storage()` / `.to_wire()` / `.escaped()`
      (directly, or through a local variable assigned from such a value) as a keyword argument whose name is a decision parameter;
  U2  `Untrusted(` is constructed or `.for_storage()` / `._text` is read outside the allow-listed storage / output functions;
  U3  a function that declares a decision parameter (queue, outcome, primary_reason, status, priority, resolution, ...) is neither decorated
      with `decision_params` nor calls `require_trusted`.
Limits (Assumption A-15-06-3): intra-function taint only, keyword arguments only; it is a build-time tripwire next to the runtime guard
(hub.core.untrusted), not a type system.
"""
import ast
import os

DECISION_PARAMS = frozenset(["queue", "outcome", "primary_reason", "status", "priority", "approval", "approver", "disposition",
                             "resolution", "decision", "to_state", "from_state", "gate", "mode_at_write", "closure_check"])
TAINT_CALLS = frozenset(["Untrusted", "untrusted_text"])
TAINT_ATTRS = frozenset(["for_storage", "to_wire", "escaped"])
ALLOWED_FUNCS = frozenset(["untrusted_text", "get_item", "display_notes", "resolve_conflict"])


def _name(node):
    return node.attr if isinstance(node, ast.Attribute) else (node.id if isinstance(node, ast.Name) else None)


def _tainted(node, names):
    if isinstance(node, ast.Call):
        n = _name(node.func)
        if n in TAINT_CALLS or n in TAINT_ATTRS:
            return True
        return any(_tainted(a, names) for a in node.args)
    if isinstance(node, ast.Name):
        return node.id in names
    if isinstance(node, (ast.Attribute, ast.Subscript)):
        return _tainted(node.value, names)
    if isinstance(node, ast.BinOp):
        return _tainted(node.left, names) or _tainted(node.right, names)
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return any(_tainted(e, names) for e in node.elts)
    return False


def check_source(src, path="<memory>"):
    tree = ast.parse(src, filename=path)
    findings = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        names = set()
        calls = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and _tainted(node.value, names):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names.add(t.id)
            if isinstance(node, ast.Call):
                calls.append(node)
        for call in calls:
            for kw in call.keywords:
                if kw.arg in DECISION_PARAMS and _tainted(kw.value, names):
                    findings.append({"path": path, "line": call.lineno, "rule": "U1", "detail": "%s() <- Untrusted-derived %s=" % (_name(call.func), kw.arg)})
            if fn.name not in ALLOWED_FUNCS:
                n = _name(call.func)
                if n == "Untrusted" or n == "for_storage":
                    findings.append({"path": path, "line": call.lineno, "rule": "U2", "detail": "%s used in %s" % (n, fn.name)})
        for node in ast.walk(fn):
            if isinstance(node, ast.Attribute) and node.attr == "_text" and fn.name not in ALLOWED_FUNCS:
                findings.append({"path": path, "line": node.lineno, "rule": "U2", "detail": "_text read in %s" % fn.name})
        params = [a.arg for a in fn.args.args + fn.args.kwonlyargs]
        if any(p in DECISION_PARAMS for p in params):
            decorated = any(_name(d) == "decision_params" for d in fn.decorator_list)
            guarded = any(isinstance(c, ast.Call) and _name(c.func) == "require_trusted" for c in calls)
            if not decorated and not guarded:
                findings.append({"path": path, "line": fn.lineno, "rule": "U3", "detail": "%s declares a decision parameter without a guard" % fn.name})
    return findings


def check_paths(paths):
    out = []
    for root in paths:
        files = [root] if os.path.isfile(root) else [os.path.join(d, f) for d, _, fs in os.walk(root) for f in sorted(fs) if f.endswith(".py")]
        for p in sorted(files):
            with open(p, encoding="utf-8") as fh:
                out.extend(check_source(fh.read(), p))
    return out
