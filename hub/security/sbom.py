"""Stage 27 (DW-25, HAR-04): software bill of materials for the hub, CycloneDX 1.5 JSON, deterministic and offline.

    python -m hub.security.sbom ROOT [--out FILE]      write the SBOM of the tree at ROOT (stdout without --out)
    sbom.build(root)                                   the document as a dict
    sbom.third_party(root)                             top-level imported names that are neither stdlib, hub nor a sibling test helper

What it lists: the application, one library component per hub package (sha256 over its sorted file digests, so a change to any file changes the hash), every
Python standard-library module the product imports (found by AST, never by running code), any third-party import (expected: none) and the pinned base image of
the Dockerfile. It reads files only: no clock, no randomness, no network, no import of hub code, so two runs on the same tree give byte-identical output and the
serial number is derived from the content. The legacy JS / Java files import only their own platform libraries (Node `fs`, `java.nio`, `java.util`), recorded as
properties of the application component, not as separate packages.
"""
import argparse
import ast
import hashlib
import json
import os
import sys

SPEC = "1.5"
PRODUCT_DIRS = ("hub",)
LEGACY_PY_DIRS = ("app",)
HASHED_SUFFIXES = (".py", ".sql", ".json")
STDLIB = frozenset(getattr(sys, "stdlib_module_names", ()))


def _files(root, top):
    out = []
    base = os.path.join(root, top)
    for d, dirs, fs in os.walk(base):
        dirs[:] = sorted(x for x in dirs if x != "__pycache__")
        for f in sorted(fs):
            if f.endswith(HASHED_SUFFIXES):
                out.append(os.path.join(d, f))
    return out


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _imports(path):
    with open(path, "rb") as f:
        tree = ast.parse(f.read(), filename=path)
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            names.add(n.module.split(".")[0])
    return names


def _scan(root):
    pkgs, imported = {}, {}
    for top in PRODUCT_DIRS + LEGACY_PY_DIRS:
        for p in _files(root, top):
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            parts = rel.split("/")
            pkg = ".".join(parts[:2]) if len(parts) > 2 else parts[0]
            pkgs.setdefault(pkg, []).append((rel, _sha(p)))
            if p.endswith(".py"):
                for m in _imports(p):
                    imported.setdefault(m, set()).add(parts[0])
    return pkgs, imported


def third_party(root):
    _, imported = _scan(root)
    return sorted(m for m in imported if m not in STDLIB and m not in ("hub", "app"))


def _dockerfile_base(root):
    p = os.path.join(root, "Dockerfile")
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip().upper().startswith("FROM "):
                return line.split()[1]
    return None


def build(root):
    pkgs, imported = _scan(root)
    comps = []
    for pkg in sorted(pkgs):
        digest = hashlib.sha256("\n".join("%s %s" % (r, h) for r, h in sorted(pkgs[pkg])).encode("utf-8")).hexdigest()
        comps.append({"type": "library", "bom-ref": "src:" + pkg, "name": pkg, "version": "source",
                      "hashes": [{"alg": "SHA-256", "content": digest}],
                      "properties": [{"name": "files", "value": str(len(pkgs[pkg]))}, {"name": "origin", "value": "first-party"}]})
    for m in sorted(imported):
        if m in ("hub", "app"):
            continue
        origin = "python-stdlib" if m in STDLIB else "third-party-UNREVIEWED"
        comps.append({"type": "library", "bom-ref": "py:" + m, "name": m, "scope": "required",
                      "properties": [{"name": "origin", "value": origin}, {"name": "imported-by", "value": ",".join(sorted(imported[m]))}]})
    base = _dockerfile_base(root)
    if base:
        pinned = "@sha256:" in base
        comps.append({"type": "container", "bom-ref": "img:base", "name": base.split(":")[0], "version": base.split(":", 1)[1] if ":" in base else "latest",
                      "properties": [{"name": "digest-pinned", "value": "yes" if pinned else "no"}, {"name": "origin", "value": "container-base-image (legacy Dockerfile)"}]})
    doc = {"bomFormat": "CycloneDX", "specVersion": SPEC, "version": 1,
           "metadata": {"component": {"type": "application", "bom-ref": "app:gxp-quality-hub", "name": "gxp-quality-hub",
                                       "properties": [{"name": "legacy-js-imports", "value": "fs (node builtin)"},
                                                      {"name": "legacy-java-imports", "value": "java.nio.file, java.util"},
                                                      {"name": "third-party-python-packages", "value": str(len(third_party(root)))}]},
                        "properties": [{"name": "label", "value": "synthetic, unvalidated; deterministic (no clock, no randomness)"}]},
           "components": comps}
    body = json.dumps(doc, sort_keys=True, separators=(",", ":"))
    d = hashlib.sha256(body.encode("utf-8")).hexdigest()
    doc["serialNumber"] = "urn:uuid:%s-%s-%s-%s-%s" % (d[:8], d[8:12], d[12:16], d[16:20], d[20:32])
    return doc


def dumps(doc):
    return json.dumps(doc, sort_keys=True, indent=1) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m hub.security.sbom")
    ap.add_argument("root")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    text = dumps(build(a.root))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
