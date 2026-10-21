"""Stage 20 DW-02 / DW-03 helpers: the hub regression group manifest (regression_groups.json) and a STATIC enumeration of the test
methods in tests/hub/test_*.py (ast only - nothing is imported or run). A test id is `module.Class.method`, exactly what
`unittest` -k matches (`*PATTERN*`, case-sensitive) in _driver.py."""
import ast
import fnmatch
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "regression_groups.json")


def load(path=MANIFEST):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["groups"]


def static_ids(test_dir=HERE):
    ids = []
    for p in sorted(glob.glob(os.path.join(test_dir, "test_*.py"))):
        mod = os.path.basename(p)[:-3]
        with open(p, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for c in tree.body:
            if isinstance(c, ast.ClassDef):
                for fn in c.body:
                    if isinstance(fn, ast.FunctionDef) and fn.name.startswith("test"):
                        ids.append("%s.%s.%s" % (mod, c.name, fn.name))
    return ids


def selects(selectors, test_id):
    return any(fnmatch.fnmatchcase(test_id, "*%s*" % s) for s in selectors)


def coverage(groups=None, ids=None):
    """{test_id: [group ids selecting it]} for every statically discovered test method."""
    groups = groups if groups is not None else load()
    ids = ids if ids is not None else static_ids()
    return dict((i, [g["id"] for g in groups if selects(g["selectors"], i)]) for i in ids)


def expected(group_id, groups=None, ids=None):
    groups = groups if groups is not None else load()
    g = [x for x in groups if x["id"] == group_id][0]
    return sorted(i for i in (ids if ids is not None else static_ids()) if selects(g["selectors"], i))
