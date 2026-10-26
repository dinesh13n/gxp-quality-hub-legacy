"""Optional, OFF-BY-DEFAULT, ADVISORY-ONLY document Q&A over the existing hub search (Stage 44, OD-40; re-qualification of touchpoint T3 of OD-08).

Retrieve first (hub.search keyword / FTS search, the caller's own access rights), then ask Azure OpenAI to answer ONLY from those passages, then check the
answer is grounded and cited before it is shown. The model path is hub/adapters/azure_openai.py and nothing else; it works only when `ai.enabled` is true
(a decision flag: it needs approval_refs["ai.enabled"]), the four AZURE_OPENAI_* environment variables are set and hub.kill is off. The only thing written
anywhere is the audit log. Synthetic data only. The answer is labelled: "AI-generated, advisory, not a GxP record, human verification required".
Modules: settings (config), guard (untrusted-text handling), retrieve, prompt, grounding, limits (budget + rate), trail (audit), service (orchestration), cli.
"""
LABEL = "AI-generated, advisory, not a GxP record, human verification required"
DATA_LABEL = "synthetic, unvalidated"
PROMPT_VERSION = "p1"
