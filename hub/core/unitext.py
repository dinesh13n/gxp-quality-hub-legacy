"""Unicode text checks shared by the wire layer and intake validation (Stage 27, S26-F-03).

`json.loads` accepts a lone UTF-16 surrogate escape (the JSON text "\\ud800") and returns a str that can NOT be encoded to UTF-8; SQLite and the canonical
audit encoding then fail with an unhandled UnicodeEncodeError. The hub refuses such text where it first sees it: HTTP 400 (hub.web.wire.parse_json) and the
reason INVALID_JSON for an intake payload (hub.intake.validate.parse_object). Pure, iterative (no recursion depth), no I/O.
"""
import re

_SURROGATE = re.compile("[\ud800-\udfff]")


def has_lone_surrogate(doc):
    """True when any str, dict key or nested list / dict value of `doc` holds a code point in U+D800..U+DFFF."""
    stack = [doc]
    while stack:
        v = stack.pop()
        if isinstance(v, str):
            if _SURROGATE.search(v):
                return True
        elif isinstance(v, dict):
            stack.extend(v.keys())
            stack.extend(v.values())
        elif isinstance(v, (list, tuple)):
            stack.extend(v)
    return False
