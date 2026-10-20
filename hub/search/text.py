"""Shared text rules of both search engines (pure; no I/O, clock or randomness).

fold    NFKD, drop combining marks, casefold: es/de text with diacritics matches without them (AC-REV-13); both the index and the query use it.
tokens  maximal runs of letters / digits (`[^\\W_]+`), the same token boundary as the FTS5 unicode61 tokenizer over folded text.
cjk     a term containing a Han / Kana / Hangul character is a SUBSTRING term (trigram index; AC-REV-13 ja-JP), never word-split.
bm25    the FTS5 bm25() formula (k1 = 1.2, b = 0.75, idf floor 1e-6, negated), so the fallback engine orders exactly like the FTS5 engine.
"""
import math
import re
import unicodedata

_TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
_CJK = re.compile(u"[぀-ヿ㐀-䶿一-鿿가-힯豈-﫿ｦ-ﾟ]")
K1, B = 1.2, 0.75
ROUND = 9


def fold(text):
    d = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in d if not unicodedata.combining(c)).casefold()


def tokens(text):
    return _TOKEN.findall(fold(text))


def is_cjk(term):
    return bool(_CJK.search(term))


def phrase_count(tk, phrase):
    n, k = 0, len(phrase)
    for i in range(len(tk) - k + 1):
        if tk[i:i + k] == phrase:
            n += 1
    return n


def idf(n_rows, n_hit):
    v = math.log((n_rows - n_hit + 0.5) / (n_hit + 0.5))
    return v if v > 0.0 else 1e-6


def bm25(idfs, freqs, doc_len, avgdl):
    score = 0.0
    for w, f in zip(idfs, freqs):
        score += w * (f * (K1 + 1.0)) / (f + K1 * (1 - B + B * doc_len / avgdl))
    return -1.0 * score


def order_key_sort(hits):
    """In place: rounded score ascending (bm25 is negative: best first), then effective_at descending, then doc_id - no randomness."""
    hits.sort(key=lambda h: (h["doc_id"], str(h.get("version"))))
    hits.sort(key=lambda h: h.get("effective_at") or "", reverse=True)
    hits.sort(key=lambda h: round(h["_score"], ROUND))
    return hits
