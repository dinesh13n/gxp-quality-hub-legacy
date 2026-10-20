"""Search settings (feature-flag-plan FF row `search.fts`, INC-09). Defaults are the safe R1 behaviour:

  search.enabled         false   OP-REV-03 answers E-REV-SEARCH-DISABLED (INC-08 key, unchanged)
  search.fts             "off"   auto | off. "auto" uses FTS5 + trigram when the runtime offers both AND the derived index exists; anything else is
                                 the fallback engine (same grammar, same ordering formula). Default OFF until FTS5 on the target is confirmed (OD-S12-12).
  search.max_doc_chars   20000   whole-document rows; a longer body is indexed up to this size and counted as `cut` in the load record
  search.require_c3_reason true  a search whose permitted result contains C3 (restricted) rows needs a non-empty reason (BEH-SEC-10, MA-2)
  templates.enabled      false   OP-REV-04 answers E-REV-DRAFTS-DISABLED (BEH-REV-07: deferred by default)
"""
from hub.core.errors import ConfigInvalid

FTS_VALUES = ("auto", "off")
DEFAULTS = {"enabled": False, "fts": "off", "max_doc_chars": 20000, "require_c3_reason": True}


def resolve(cfg):
    s = dict(DEFAULTS)
    s.update((cfg or {}).get("search") or {})
    if s["fts"] not in FTS_VALUES:
        raise ConfigInvalid({"search.fts": str(s["fts"])[:20], "allowed": list(FTS_VALUES)})
    if not isinstance(s["enabled"], bool) or not isinstance(s["require_c3_reason"], bool):
        raise ConfigInvalid({"search": "enabled / require_c3_reason must be boolean"})
    if isinstance(s["max_doc_chars"], bool) or not isinstance(s["max_doc_chars"], int) or s["max_doc_chars"] < 100:
        raise ConfigInvalid({"search.max_doc_chars": "integer >= 100"})
    return s


def templates_enabled(cfg):
    v = ((cfg or {}).get("templates") or {}).get("enabled", False)
    if not isinstance(v, bool):
        raise ConfigInvalid({"templates.enabled": "must be boolean"})
    return v
