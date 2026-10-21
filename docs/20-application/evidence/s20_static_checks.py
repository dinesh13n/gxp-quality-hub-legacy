"""Stage 20 DW-06 static evidence (read-only; AST only - nothing is imported or executed from the scanned tree).

    python3 -B s20_static_checks.py <tree-root containing hub/> [--out <json>]

Reports for hub/:
  * package import graph (package = hub.<first component>; module-level vs function-level imports), 2- and 3-package cycles among the
    module-level edges (same method as Stage 16 evidence/package-graph.txt), and domain -> hub.web edges (any level);
  * unused module-level imports (a pyflakes-F401-like check: an imported name never referenced in the module and not listed in __all__,
    ignoring lines marked `noqa`) and local names assigned but never read inside a function (F841-like, simple assignments / with-as only;
    known false positives: attributes assigned in the body of a class that is defined inside a function, e.g. hub/web/server.py _Handler);
  * cyclomatic complexity per function (McCabe-style, aligned with ruff C901; see _CC) and the functions above 15;
  * Zone H rule copies: functions comparing `principal_id not in holders` (the holder rule).
Synthetic repository; evidence for docs/20-application. Owner: build agent (claude-fde-agent).
"""
import argparse
import ast
import itertools
import json
import os
import sys

WEB = "web"
HTTP_LAYER_ALLOWED = {"web", "r2"}  # r2 contains the R2 HTTP surface (api.py, web.py, cli serve) by design (RTD-81 / DW-30)


def modules(root):
    base = os.path.join(root, "hub")
    for d, dirs, fns in os.walk(base):
        dirs[:] = sorted(x for x in dirs if x != "__pycache__")
        for fn in sorted(fns):
            if fn.endswith(".py"):
                p = os.path.join(d, fn)
                rel = os.path.relpath(p, root).replace(os.sep, "/")
                yield rel, p


def pkg_of(rel):
    parts = rel.split("/")
    return "(root)" if len(parts) == 2 else parts[1]


def _targets(node, rel):
    out = []
    if isinstance(node, ast.Import):
        out = [a.name for a in node.names]
    elif isinstance(node, ast.ImportFrom):
        if node.level:
            base = rel[:-3].split("/")[:-node.level]
            mod = ".".join(base + ([node.module] if node.module else []))
        else:
            mod = node.module or ""
        out = [mod] + ["%s.%s" % (mod, a.name) for a in node.names]
    return [t for t in out if t.startswith("hub.") or t == "hub"]


def graph(root):
    mod_edges, fn_edges, web_users = {}, {}, {}
    for rel, p in modules(root):
        tree = ast.parse(open(p, encoding="utf-8").read())
        src = pkg_of(rel)
        top = set(id(n) for n in tree.body)
        for n in ast.walk(tree):
            if not isinstance(n, (ast.Import, ast.ImportFrom)):
                continue
            for t in _targets(n, rel):
                parts = t.split(".")
                dst = parts[1] if len(parts) > 1 else "(root)"
                if dst == src or dst in ("__init__",):
                    continue
                if os.path.exists(os.path.join(root, "hub", dst + ".py")):
                    dst = "(root)"
                (mod_edges if id(n) in top else fn_edges).setdefault(src, set()).add(dst)
                if dst == WEB and src not in HTTP_LAYER_ALLOWED:
                    web_users.setdefault(rel, set()).add(t)
    pk = sorted(set(mod_edges) | set(x for v in mod_edges.values() for x in v))
    e = lambda a, b: b in mod_edges.get(a, ())  # noqa: E731
    two = [(a, b) for a, b in itertools.combinations(pk, 2) if e(a, b) and e(b, a)]
    three = [(a, b, c) for a, b, c in itertools.combinations(pk, 3)
             if (e(a, b) and e(b, c) and e(c, a)) or (e(a, c) and e(c, b) and e(b, a))]
    return {"module_level_edges": dict((k, sorted(v)) for k, v in sorted(mod_edges.items())),
            "function_level_edges": dict((k, sorted(v - mod_edges.get(k, set()))) for k, v in sorted(fn_edges.items())),
            "two_cycles": two, "three_cycles": three,
            "domain_to_web_imports": dict((k, sorted(v)) for k, v in sorted(web_users.items()))}


def unused(root):
    out = []
    for rel, p in modules(root):
        text = open(p, encoding="utf-8").read()
        lines = text.splitlines()
        tree = ast.parse(text)
        names = set()
        allv = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Name):
                names.add(n.id)
            elif isinstance(n, ast.Attribute):
                v = n
                while isinstance(v, ast.Attribute):
                    v = v.value
                if isinstance(v, ast.Name):
                    names.add(v.id)
            elif isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in n.targets):
                if isinstance(n.value, (ast.List, ast.Tuple)):
                    allv |= set(getattr(x, "value", None) for x in n.value.elts)
        if rel.endswith("__init__.py"):
            continue
        for n in tree.body:
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                if "noqa" in lines[n.lineno - 1]:
                    continue
                for a in n.names:
                    nm = (a.asname or a.name).split(".")[0]
                    if nm not in names and nm not in allv and nm != "*":
                        out.append({"file": rel, "line": n.lineno, "kind": "F401-like", "name": a.asname or a.name})
        for f in ast.walk(tree):
            if not isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            stored, loaded = {}, set()
            for n in ast.walk(f):
                if isinstance(n, ast.Name):
                    if isinstance(n.ctx, ast.Store):
                        stored.setdefault(n.id, n.lineno)
                    else:
                        loaded.add(n.id)
            nonlocal_names = set()
            for n in ast.walk(f):
                if isinstance(n, (ast.Global, ast.Nonlocal)):
                    nonlocal_names |= set(n.names)
            for nm, ln in stored.items():
                if nm not in loaded and nm not in nonlocal_names and nm != "_" and not nm.startswith("_"):
                    assigned_simply = any(isinstance(n, (ast.Assign, ast.withitem)) for n in ast.walk(f)
                                          if (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == nm for t in n.targets))
                                          or (isinstance(n, ast.withitem) and isinstance(n.optional_vars, ast.Name) and n.optional_vars.id == nm))
                    if assigned_simply:
                        out.append({"file": rel, "line": ln, "kind": "F841-like", "name": nm, "function": f.name})
    return out


class _CC(ast.NodeVisitor):
    """McCabe-style count aligned with ruff C901 (validated: reproduces the 11 Stage 16 findings on main 41098c0): 1 + if/elif + for/while
    (+1 for an else) + each except handler + each match case; boolean operators, comprehensions and nested functions are not counted."""

    def __init__(self):
        self.n = 1
        self._entered = False

    def generic_visit(self, node):
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While)):
            self.n += 1 + (1 if getattr(node, "orelse", None) and not isinstance(node, ast.If) else 0)
        elif isinstance(node, ast.ExceptHandler):
            self.n += 1
        elif type(node).__name__ == "match_case":
            self.n += 1
        ast.NodeVisitor.generic_visit(self, node)

    def visit_FunctionDef(self, node):
        if self._entered:
            return  # nested functions are measured separately
        self._entered = True
        ast.NodeVisitor.generic_visit(self, node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node):
        return None


def complexity(root, limit=15):
    out = []
    for rel, p in modules(root):
        tree = ast.parse(open(p, encoding="utf-8").read())
        for f in ast.walk(tree):
            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
                v = _CC()
                v.visit(f)
                if v.n > limit:
                    out.append({"file": rel, "line": f.lineno, "function": f.name, "complexity": v.n})
    return sorted(out, key=lambda x: (x["file"], x["line"]))


def holder_rule_copies(root):
    out = []
    for rel, p in modules(root):
        tree = ast.parse(open(p, encoding="utf-8").read())
        for f in ast.walk(tree):
            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for n in ast.walk(f):
                    if isinstance(n, ast.Compare) and any(isinstance(o, ast.NotIn) for o in n.ops):
                        src = ast.get_source_segment(open(p, encoding="utf-8").read(), n) or ""
                        if "principal_id" in src and "holders" in src:
                            out.append({"file": rel, "line": n.lineno, "function": f.name, "expr": src})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    g = graph(a.root)
    rep = {"root_label": os.path.basename(os.path.abspath(a.root)), "python": sys.version.split()[0], "graph": g,
           "counts": {"two_cycles": len(g["two_cycles"]), "three_cycles": len(g["three_cycles"]),
                      "domain_to_web_files": len(g["domain_to_web_imports"])},
           "unused": unused(a.root), "complexity_over_15": complexity(a.root), "holder_rule_copies": holder_rule_copies(a.root)}
    rep["counts"].update(unused=len(rep["unused"]), complexity_over_15=len(rep["complexity_over_15"]),
                         holder_rule_copies=len(rep["holder_rule_copies"]))
    text = json.dumps(rep, indent=1, sort_keys=True)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(json.dumps(rep["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
