"""Untrusted text type (ADR-002 option B(3), BEH-INT-09, SBR-INT-06, INV-10).

All free text derived from external or legacy content (feed notes, document bodies, gateway payloads,
deviation justifications copied from legacy) is wrapped in `Untrusted`. It can be stored verbatim and
rendered escaped, but it can never be passed to a decision / status / priority / queue / approval /
disposition parameter: `require_trusted` and the `decision_params` decorator raise E-INT-UNTRUSTED-USE.
The text is never parsed for commands (planted prompt-injection strings in the data are data).
"""
import functools
import html

from hub.core.errors import UntrustedUse


class Untrusted(object):
    __slots__ = ("_text", "source")

    def __init__(self, text, source="unknown"):
        if isinstance(text, Untrusted):
            text = text._text
        if not isinstance(text, str):
            raise TypeError("Untrusted wraps str only")
        object.__setattr__(self, "_text", text)
        object.__setattr__(self, "source", source)

    def __setattr__(self, name, value):
        raise AttributeError("Untrusted is immutable")

    def for_storage(self):
        """Verbatim text, only for persistence into a free-text column."""
        return self._text

    def escaped(self):
        return html.escape(self._text, quote=True)

    def to_wire(self):
        """api-contracts.md: free-text positions are returned as {text, trust: untrusted}."""
        return {"text": self._text, "trust": "untrusted"}

    def __str__(self):
        return self.escaped()

    def __repr__(self):
        return "Untrusted(len=%d, source=%r)" % (len(self._text), self.source)

    def __len__(self):
        return len(self._text)

    def __eq__(self, other):
        return isinstance(other, Untrusted) and other._text == self._text

    def __hash__(self):
        return hash(("Untrusted", self._text))

    # no __add__/__format__ helpers: concatenating into trusted strings must be explicit (escaped()).


def require_trusted(value, param="value"):
    if isinstance(value, Untrusted):
        raise UntrustedUse({"param": param})
    if isinstance(value, (list, tuple, set, frozenset)):
        for v in value:
            require_trusted(v, param)
    elif isinstance(value, dict):
        for k, v in value.items():
            require_trusted(k, param)
            require_trusted(v, param)
    return value


def decision_params(func):
    """Decorator for functions whose parameters drive decisions: rejects any Untrusted argument."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for i, a in enumerate(args):
            require_trusted(a, "%s[arg%d]" % (func.__name__, i))
        for k, v in kwargs.items():
            require_trusted(v, "%s[%s]" % (func.__name__, k))
        return func(*args, **kwargs)
    return wrapper
