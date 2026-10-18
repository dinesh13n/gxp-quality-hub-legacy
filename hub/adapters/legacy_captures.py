"""AD-08 legacy output comparator source: reads the active characterisation captures (goldens) produced by
the INC-01 harness (AD-00) - `tests/characterization/golden/INDEX.json`, integrity-checked against
`golden/MANIFEST.sha256` before use. Read only. A missing capture or path yields CaptureMissing, which
golden-compare reports as NOT-RUN (gate fails).
"""
import hashlib
import json
import os
import re

from hub.core.errors import FixtureMismatch
from hub.guards.sandbox import PACKAGE_ROOT

DEFAULT_GOLDEN_DIR = os.path.join(PACKAGE_ROOT, "tests", "characterization", "golden")
JSON_SOURCES = ("api", "batch", "lib", "supplement")


class CaptureMissing(LookupError):
    pass


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


class CaptureSet(object):
    def __init__(self, sources):
        self.sources = sources  # {name: parsed json or None}

    @classmethod
    def from_golden_dir(cls, golden_dir=DEFAULT_GOLDEN_DIR, verify=True):
        if verify:
            bad = []
            with open(os.path.join(golden_dir, "MANIFEST.sha256"), encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        digest, rel = line.split(None, 1)
                        p = os.path.join(golden_dir, rel.strip())
                        if not os.path.isfile(p) or _sha(p) != digest:
                            bad.append(rel.strip())
            if bad:
                raise FixtureMismatch({"golden_manifest": bad})
        with open(os.path.join(golden_dir, "INDEX.json"), encoding="utf-8") as f:
            index = json.load(f)
        sources = {}
        for name, rel in sorted(index["sources"].items()):
            if name not in JSON_SOURCES:
                continue
            p = os.path.join(golden_dir, rel) if rel else None
            if p and os.path.isfile(p):
                with open(p, encoding="utf-8") as f:
                    sources[name] = json.load(f)
            else:
                sources[name] = None
        return cls(sources)

    def extract(self, source, path):
        """path: list of steps - str key, int index, {"as_map": true} (list of pairs -> dict),
        {"slice": [a, b]}, {"regex": "..."} (group 1 of a string)."""
        doc = self.sources.get(source)
        if doc is None:
            raise CaptureMissing("capture source %r not available" % source)
        cur = doc
        for step in path:
            try:
                if isinstance(step, dict):
                    if step.get("as_map"):
                        cur = dict((k if not isinstance(k, list) else json.dumps(k), v) for k, v in cur)
                    elif "slice" in step:
                        a, b = step["slice"]
                        cur = cur[a:b]
                    elif "regex" in step:
                        m = re.search(step["regex"], cur)
                        if not m:
                            raise CaptureMissing("regex %r not found" % step["regex"])
                        cur = m.group(1)
                    else:
                        raise CaptureMissing("unknown step %r" % (step,))
                else:
                    cur = cur[step]
            except (KeyError, IndexError, TypeError) as e:
                raise CaptureMissing("path %r not found in %s (%s)" % (path, source, e))
        return cur
