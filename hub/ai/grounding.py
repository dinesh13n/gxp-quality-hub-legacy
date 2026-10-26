"""Grounding and citation check on the model answer (Stage 44, OD-40). The answer is shown only when ALL of these hold:

  G1  not empty, at most MAX_CHARS, no URL that is not in a cited source, no instruction-like text of its own;
  G2  every sentence that says something carries at least one [S<n>] marker and every marker names a source that was actually supplied;
  G3  every number (digits or number words such as ten) in a sentence appears in the sources that sentence cites;
  G4  at least MIN_OVERLAP of a sentence's content words appear in the sources that sentence cites (lexical, not semantic: it catches invented content,
      it does NOT prove the statement is true or complete - a human still verifies).
INSUFFICIENT_CONTEXT is a valid, grounded "no answer". Deterministic, no model.
"""
import re

from hub.ai import guard, retrieve
from hub.search import text

MAX_CHARS = 2000
MIN_OVERLAP = 0.6
NO_ANSWER = "INSUFFICIENT_CONTEXT"
_CITE = re.compile(r"\[(S[0-9]{1,2})\]")
_SENT = re.compile(r"(?<=[.!?])\s+|\n+")
_NUM = re.compile(r"[0-9]+(?:[.,][0-9]+)*")
_URL = re.compile(r"https?://\S+|www\.\S+", re.I)
_NUMWORDS = frozenset("zero one two three four five six seven eight nine ten eleven twelve twenty thirty forty fifty sixty ninety hundred thousand million "
                      "first second third fourth fifth half double triple never always".split())


def _content(sentence):
    return [t for t in text.tokens(_CITE.sub(" ", sentence)) if len(t) >= 4 and t not in retrieve.STOP and not t.isdigit()]


def _sentences(a, by_id, out):
    """G2 / G3 / G4 per sentence; appends to out["reasons"], counts out["sentences"]; -> the lowest overlap seen."""
    worst = 1.0
    for sent in [x.strip() for x in _SENT.split(a) if x.strip()]:
        words = _content(sent)
        if not words:
            continue
        out["sentences"] += 1
        ids = [c for c in _CITE.findall(sent) if c in by_id]
        if not ids:
            out["reasons"].append("G2 sentence without a valid citation")
            continue
        src_text = " ".join(by_id[c]["text"] for c in ids)
        src_tokens = set(text.tokens(src_text))
        _numbers(sent, src_text, src_tokens, out)
        frac = sum(1 for w in words if w in src_tokens) / float(len(words))
        worst = min(worst, frac)
        if frac < MIN_OVERLAP:
            out["reasons"].append("G4 sentence overlaps %.2f with its cited source (< %.2f)" % (frac, MIN_OVERLAP))
    return worst


def _numbers(sent, src_text, src_tokens, out):
    for n in _NUM.findall(_CITE.sub(" ", sent)):
        if n.replace(",", ".") not in src_text.replace(",", ".") and n not in src_text:
            out["reasons"].append("G3 number %s not in the cited source" % n[:20])
    for w in text.tokens(_CITE.sub(" ", sent)):
        if w in _NUMWORDS and w not in src_tokens:
            out["reasons"].append("G3 number word '%s' not in the cited source" % w[:20])


def check(answer, sources):
    """-> {ok, no_answer, reasons: [...], cited: [ids], sentences, overlap_min}. `sources` as produced by hub.ai.retrieve."""
    by_id = dict((s["id"], s) for s in sources)
    out = {"ok": False, "no_answer": False, "reasons": [], "cited": [], "sentences": 0, "overlap_min": None}
    a = (answer or "").strip()
    if not a:
        out["reasons"].append("G1 empty answer")
        return out
    if a.rstrip(".").strip() == NO_ANSWER:
        out.update(ok=True, no_answer=True)
        return out
    if len(a) > MAX_CHARS:
        out["reasons"].append("G1 answer over %d characters" % MAX_CHARS)
    cited_all = []
    for m in _CITE.findall(a):
        if m not in by_id:
            out["reasons"].append("G2 cites unknown source %s" % m)
        elif m not in cited_all:
            cited_all.append(m)
    out["cited"] = cited_all
    if not cited_all:
        out["reasons"].append("G2 no citation")
    corpus_text = " ".join(s["text"] for s in sources)
    for u in _URL.findall(a):
        if u.rstrip(".,;)") not in corpus_text:
            out["reasons"].append("G1 URL not present in a source")
            break
    if guard.looks_like_instruction(_CITE.sub("", a)) and not guard.looks_like_instruction(" ".join(by_id[c]["text"] for c in cited_all if c in by_id)):
        out["reasons"].append("G1 answer contains instruction-like text that is not in a cited source")
    worst = _sentences(a, by_id, out)
    out["overlap_min"] = round(worst, 3)
    out["reasons"] = out["reasons"][:10]
    out["ok"] = not out["reasons"]
    return out
