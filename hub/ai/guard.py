"""Untrusted-text handling for the AI path (PNFR-13, BR-AI-3): retrieved text and the question are DATA.

* sanitize()      drops control and invisible / bidirectional-override characters, collapses whitespace, HTML-escapes angle brackets and ampersands
                  (a source cannot close its own <source> element or open a new one) and caps the length.
* looks_like_instruction()   a deliberately simple pattern list. It is a second line of defence (leave suspicious sources out of the prompt), NOT the
                  main control: the main controls are the fixed system rules + delimiting, the grounding / citation check on the answer, and the fact
                  that the model has no tool, no write path and no authority (advisory only).
"""
import html
import re
import unicodedata

_INVISIBLE = re.compile("[​-‏‪-‮⁠-⁤⁦-⁩﻿]")
_WS = re.compile(r"[ \t\r\f\v]+")
_NL = re.compile(r"\n{3,}")
PATTERNS = (
    r"\bignore\b.{0,40}\b(previous|prior|above|earlier|all)\b", r"\bdisregard\b", r"\bsystem (note|prompt|message)\b", r"\byou are now\b",
    r"\b(new|real|updated) (instruction|policy|rule)s?\b", r"\boverride\b", r"\brelease all\b", r"\b(approve|approves|approved) (everything|release|this|on behalf)",
    r"\bact as\b", r"\bassistant\s*:", r"\bsystem\s*:", r"<\|", r"\[/?(inst|sys)\]", r"\bend of (the )?(document|sources?)\b", r"</?\s*(source|untrusted|system)\b",
    r"\b(reveal|print|show|repeat)\b.{0,30}\b(prompt|instructions|key|rules)\b", r"\bcall the .{0,20}(tool|function)\b", r"\bcurl\b.{0,40}\|\s*sh\b",
    r"\bauthority_ref\b", r"\bapproval_ref\b", r"\bzone_h\b", r"\bdelete\b.{0,20}\baudit",
)
_RX = [re.compile(p, re.I | re.S) for p in PATTERNS]


def sanitize(text, max_chars):
    t = unicodedata.normalize("NFC", text if isinstance(text, str) else "")
    t = _INVISIBLE.sub("", t)
    t = "".join(c for c in t if c in "\n\t" or unicodedata.category(c)[0] != "C")
    t = _NL.sub("\n\n", _WS.sub(" ", t)).strip()
    return html.escape(t[:max_chars], quote=False)


def looks_like_instruction(text):
    """-> the list of pattern indices that matched (empty = nothing suspicious found; NOT a guarantee)."""
    t = unicodedata.normalize("NFKC", _INVISIBLE.sub("", text if isinstance(text, str) else ""))
    return [i for i, rx in enumerate(_RX) if rx.search(t)]
