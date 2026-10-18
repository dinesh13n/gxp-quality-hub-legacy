"""Key registry (match rules are DATA, F05-2): id patterns per object type and the registered link types / type pairs."""
import copy
import json
import os
import re
import unicodedata

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registry.json")


def normalise(value):
    """Exact-key normalisation (BEH-ID-02): Unicode NFC, then trim. Nothing else (no case folding, no punctuation removal)."""
    if not isinstance(value, str):
        return None
    return unicodedata.normalize("NFC", value).strip()


class Registry(object):
    def __init__(self, doc=None):
        self.doc = copy.deepcopy(doc) if doc is not None else json.load(open(PATH, encoding="utf-8"))
        self.patterns = dict((t, re.compile(p)) for t, p in sorted(self.doc["id_types"].items()))
        self.link_types = list(self.doc["link_types"])

    def with_id_type(self, name, pattern):
        """A copy with an additional id pattern (used by the ambiguity test, AC-ID-12)."""
        doc = copy.deepcopy(self.doc)
        doc["id_types"][name] = pattern
        return Registry(doc)

    def link_type(self, code):
        rows = [lt for lt in self.link_types if lt["code"] == code]
        return rows[0] if rows else None

    def pair_registered(self, type_a, type_b):
        return any(set((lt["from_type"], lt["to_type"])) == set((type_a, type_b)) for lt in self.link_types)

    def pair_key_used(self, type_a, type_b):
        for lt in self.link_types:
            if set((lt["from_type"], lt["to_type"])) == set((type_a, type_b)):
                return lt["key_used"], lt["code"]
        return None, None

    def candidates(self, value):
        v = normalise(value)
        if v is None:
            return []
        return [t for t, p in sorted(self.patterns.items()) if p.match(v)]

    def matches(self, id_type, value):
        p = self.patterns.get(id_type)
        v = normalise(value)
        return bool(p and v is not None and p.match(v))
