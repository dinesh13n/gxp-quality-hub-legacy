"""Retrieve first (Stage 44, OD-40): the model sees ONLY passages that the existing hub search returned for this caller.

* The caller's roles go through hub.search.engine.R2SearchService unchanged: access is applied inside the search (rows the caller may not read are never
  ranked, counted or returned). Restricted (C3) rows are then LEFT OUT of the AI context altogether - a model call is never a justified C3 read, so no
  reason is accepted and no C3_READ record is needed (the service runs with require_c3_reason off; the rows are dropped here and counted in `excluded`).
* The question becomes a search query by a fixed, deterministic rule (stop words removed, longest words first, at most max_query_terms, then fewer terms
  until something matches - at most 4 searches). `query` (the operator's own search grammar) bypasses the rule. No model is involved in retrieval.
* Passage text is read from the derived corpus row of a hit that was just returned (same doc_id + version) - nothing else is read - then sanitised.
"""
from hub.ai import guard
from hub.core.ai_errors import AiNoRetrieval
from hub.review import search as rsearch
from hub.search import engine, text

STOP = frozenset("""a about above after again all also am an and any are as at be because been before being below between both but by can could did do does
doing down during each few for from further had has have having he her here hers him his how i if in into is it its itself just me more most my no nor
not of off on once only or other our out over own same she should so some such than that the their them then there these they this those through to
too under until up very was we were what when where which while who whom why will with would you your tell please explain describe say says said
document documents doc docs record records""".split())
MAX_ATTEMPTS = 4


def keywords(question, max_terms):
    seen, words = set(), []
    for t in text.tokens(question):
        if len(t) >= 3 and t not in STOP and not t.isdigit() and t not in seen:
            seen.add(t)
            words.append(t)
    keep = sorted(words, key=lambda w: (-len(w), words.index(w)))[:max_terms]
    return [w for w in words if w in keep]


def _attempts(terms):
    out, n = [], len(terms)
    while n >= 1 and len(out) < MAX_ATTEMPTS:
        out.append(" ".join(terms[:n]))
        n -= 1 if n <= MAX_ATTEMPTS else n - MAX_ATTEMPTS + 1
    return out


def _passage(body, terms, width):
    low = text.fold(body)
    pos = min([i for i in (low.find(t) for t in terms) if i >= 0] or [0])
    start = max(0, pos - width // 4)
    return body[start:start + width]


def retrieve(con, cfg, session, question, query, s, correlation_id, clock=None, anchor=None):
    """-> dict(query_used, searches, sources=[...], excluded={restricted, instruction_like, unreadable}, total_hits). Raises AiNoRetrieval when nothing usable."""
    r = s["retrieval"]
    scfg = {"search": dict((cfg or {}).get("search") or {}, require_c3_reason=False)}
    svc = engine.R2SearchService(scfg, None, clock, anchor)
    terms = keywords(question, r["max_query_terms"])
    tries = [query] if query else _attempts(terms)
    if not tries:
        raise AiNoRetrieval({"reason": "no searchable word in the question; give --query"})
    hits, used, n = [], None, 0
    for q in tries:
        n += 1
        res = svc.search(session, q, limit=rsearch.LIMIT_MAX, con=con, correlation_id=correlation_id)
        if res["items"]:
            hits, used = res["items"], q
            break
    excluded = {"restricted": 0, "instruction_like": 0, "unreadable": 0}
    sources = []
    qterms = text.tokens(used or "")
    for h in hits:
        if len(sources) >= r["top_k"]:
            break
        if h["access_label"] == "restricted":
            excluded["restricted"] += 1
            continue
        row = con.execute("SELECT body FROM search_doc WHERE doc_id = ? AND version = ?", (h["doc_id"], h["version"])).fetchone()
        if row is None or not isinstance(row[0], str) or not row[0].strip():
            excluded["unreadable"] += 1
            continue
        flags_ = guard.looks_like_instruction(row[0])
        if flags_ and s["injection_policy"] == "exclude":
            excluded["instruction_like"] += 1
            continue
        sources.append({"id": "S%d" % (len(sources) + 1), "doc_id": h["doc_id"], "version": h["version"], "hash_prefix": h["hash_prefix"],
                        "source": h["source"], "effective_at": h["effective_at"], "locale": h["locale"], "access_label": h["access_label"],
                        "linked_case": h["linked_case"], "ocr_low": h["ocr_low"], "instruction_like": bool(flags_),
                        "text": guard.sanitize(_passage(row[0], qterms, r["max_chars_per_source"]), r["max_chars_per_source"] + 200)})
    if not sources:
        raise AiNoRetrieval({"searches": n, "hits": len(hits), "excluded": excluded, "hint": "nothing readable and usable matched; no model call was made"})
    return {"query_used": used, "searches": n, "sources": sources, "excluded": excluded, "total_hits": len(hits)}
