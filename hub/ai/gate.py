"""The gate in front of every model path (Stage 44, OD-40). Order of refusals, all BEFORE the store is opened and before any socket exists:

  1. hub.kill true                  -> E-HUB-KILLED (exit 3)
  2. ai.enabled false (the default) -> E-AI-DISABLED (exit 40)
  3. data_origin not synthetic      -> E-AI-NON-SYNTHETIC (exit 40)
  4. provider settings missing      -> E-AI-NOT-CONFIGURED (exit 40; names only, never values)
`ai.enabled` is also a decision flag (hub.control.flags): a config that sets it true without approval_refs["ai.enabled"] is refused at load.
"""
from hub.adapters import azure_openai
from hub.ai import settings
from hub.core.ai_errors import AiDisabled, AiNonSynthetic
from hub.core.errors import HubKilled


def check(cfg, environ=None):
    """-> (ai settings, ProviderSettings). Raises the refusal errors above."""
    if (cfg.get("hub") or {}).get("kill"):
        raise HubKilled()
    s = settings.resolve(cfg)
    if not s["enabled"]:
        raise AiDisabled({"hint": "ai.enabled is false (the shipped default); see docs/44-genai-qa/setup-runbook.md"})
    if cfg.get("data_origin") != "synthetic":
        raise AiNonSynthetic({"data_origin": str(cfg.get("data_origin"))[:40]})
    return s, azure_openai.resolve(s["azure_openai"], environ)


def client(s, provider):
    """The only construction of the model client: enabled=True is produced here, after check()."""
    az = s["azure_openai"]
    return azure_openai.AzureOpenAIClient(provider, enabled=True, timeout=az["timeout_seconds"], token_param=az["token_param"])
