"""`ai.*` settings (Stage 44, OD-40). Defaults are the safe ones: OFF, no endpoint, small caps.

  ai.enabled                 false   decision flag (hub.control.flags): true needs approval_refs["ai.enabled"]; refused otherwise at config load
  ai.provider                "azure_openai"   the only provider
  ai.azure_openai.endpoint / deployment / api_version   "" placeholders: the AZURE_OPENAI_* environment variables win; these may carry the NON-secret
                             values only. There is NO key setting: the API key is read from AZURE_OPENAI_API_KEY and from nowhere else.
  ai.azure_openai.timeout_seconds   20     hard request timeout (0.2 .. 120)
  ai.azure_openai.token_param       "max_tokens" | "max_completion_tokens" (newer models)
  ai.retrieval.top_k                4      sources passed to the model (1 .. 8)
  ai.retrieval.max_chars_per_source 1200   passage size per source (200 .. 4000)
  ai.retrieval.max_question_chars   300    (10 .. 1000)
  ai.retrieval.max_query_terms      6      keywords derived from the question (1 .. 8); `--query` bypasses the derivation
  ai.answer.max_output_tokens       300    model output cap (16 .. 1000)
  ai.budget.daily_token_budget      20000  prompt+completion units per UTC day, counted from the audit log (1000 .. 1000000)
  ai.budget.max_request_tokens      3000   estimate cap for one request (200 .. 20000)
  ai.rate_limit.max_requests_per_minute  5 (1 .. 60), counted from the audit log
  ai.injection_policy               "exclude" | "flag"   sources that look like instructions are left out of the prompt (default) or kept as flagged data
All numeric defaults are AGENT ASSUMPTIONS (OD-32 style), not approvals.
"""
import copy

from hub.core.errors import ConfigInvalid

DEFAULTS = {
    "enabled": False,
    "provider": "azure_openai",
    "azure_openai": {"endpoint": "", "deployment": "", "api_version": "", "timeout_seconds": 20, "token_param": "max_tokens"},
    "retrieval": {"top_k": 4, "max_chars_per_source": 1200, "max_question_chars": 300, "max_query_terms": 6},
    "answer": {"max_output_tokens": 300},
    "budget": {"daily_token_budget": 20000, "max_request_tokens": 3000},
    "rate_limit": {"max_requests_per_minute": 5},
    "injection_policy": "exclude",
}
# the closed key set for hub.config.KNOWN_KEYS (None = a leaf value)
KEYS = {"enabled": None, "provider": None, "azure_openai": {"endpoint": None, "deployment": None, "api_version": None, "timeout_seconds": None, "token_param": None},
        "retrieval": {"top_k": None, "max_chars_per_source": None, "max_question_chars": None, "max_query_terms": None},
        "answer": {"max_output_tokens": None}, "budget": {"daily_token_budget": None, "max_request_tokens": None},
        "rate_limit": {"max_requests_per_minute": None}, "injection_policy": None}
RANGES = (("retrieval", "top_k", 1, 8), ("retrieval", "max_chars_per_source", 200, 4000), ("retrieval", "max_question_chars", 10, 1000),
          ("retrieval", "max_query_terms", 1, 8), ("answer", "max_output_tokens", 16, 1000), ("budget", "daily_token_budget", 1000, 1000000),
          ("budget", "max_request_tokens", 200, 20000), ("rate_limit", "max_requests_per_minute", 1, 60))


def _merge(base, over):
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _merge(base[k], v)
        else:
            base[k] = v
    return base


def _num(v, lo, hi, integer=True):
    ok = isinstance(v, int) if integer else isinstance(v, (int, float))
    return ok and not isinstance(v, bool) and lo <= v <= hi


def resolve(cfg):
    s = copy.deepcopy(DEFAULTS)
    over = (cfg or {}).get("ai")
    if over is not None:
        if not isinstance(over, dict):
            raise ConfigInvalid({"ai": "must be an object"})
        _merge(s, over)
    if not isinstance(s["enabled"], bool):
        raise ConfigInvalid({"ai.enabled": "must be boolean"})
    if s["provider"] != "azure_openai":
        raise ConfigInvalid({"ai.provider": "only 'azure_openai'"})
    if s["injection_policy"] not in ("exclude", "flag"):
        raise ConfigInvalid({"ai.injection_policy": "exclude | flag"})
    for sec, key, lo, hi in RANGES:
        if not isinstance(s[sec], dict) or not _num(s[sec].get(key), lo, hi):
            raise ConfigInvalid({"ai.%s.%s" % (sec, key): "integer %d .. %d" % (lo, hi)})
    az = s["azure_openai"]
    if not isinstance(az, dict) or not _num(az.get("timeout_seconds"), 0.2, 120, integer=False):
        raise ConfigInvalid({"ai.azure_openai.timeout_seconds": "number 0.2 .. 120"})
    if az.get("token_param") not in ("max_tokens", "max_completion_tokens"):
        raise ConfigInvalid({"ai.azure_openai.token_param": "max_tokens | max_completion_tokens"})
    for k in ("endpoint", "deployment", "api_version"):
        if not isinstance(az.get(k), str) or len(az[k]) > 200:
            raise ConfigInvalid({"ai.azure_openai.%s" % k: "string of at most 200 characters"})
    return s
