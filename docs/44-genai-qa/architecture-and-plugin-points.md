# Architecture and plug-in points

## Flow (`python -m hub.ai ask ...`)
question check -> principal session -> gate (kill switch, ai.enabled, env vars) -> synthetic-corpus guard -> retrieve via `hub.search.engine.R2SearchService` (caller-visible only; restricted rows dropped) -> sanitise + injection filter -> build prompt (`hub/ai/prompt.py`) -> rate/budget check from audit log -> audit AI_QA_REQUESTED -> model call -> grounding check -> audit AI_QA_ANSWERED (or AI_QA_PROVIDER_ERROR / AI_QA_REFUSED). If retrieval finds nothing, no model call is made.

## Where the Azure OpenAI model plugs in
| What | Where |
|---|---|
| The ONLY network client (stdlib urllib, chat-completions REST) | `hub/adapters/azure_openai.py` (`AzureOpenAIClient.complete`) |
| Env vars | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_API_KEY` (key is env only, no config fallback) |
| Config keys | `ai.enabled` (false), `ai.provider`, `ai.azure_openai.{endpoint,deployment,api_version,timeout_seconds,token_param}` (endpoint/deployment/api_version are a fallback; env wins), `ai.retrieval.*`, `ai.answer.max_output_tokens`, `ai.budget.*`, `ai.rate_limit.max_requests_per_minute`, `ai.injection_policy`. Shape: hub-config.ai.example.json |
| Approval | `approval_refs["ai.enabled"]` in `hub/control/flags.py` (decision flag) |
| Defaults and ranges | `hub/ai/settings.py` |
| Gate order: kill, disabled, non-synthetic, not configured | `hub/ai/gate.py` |
| Swap the model | change `AZURE_OPENAI_DEPLOYMENT` (and API version); for reasoning-model deployments set `ai.azure_openai.token_param` to `max_completion_tokens` |
| Swap provider | implement the same `complete(messages, max_output_tokens)` interface in a new file under `hub/adapters/`, and select it in `hub/ai/gate.py` (a new provider needs its own re-qualification) |

Endpoint rules: https on `*.openai.azure.com`, `*.cognitiveservices.azure.com`, `*.services.ai.azure.com`, or http/https on loopback only (tests); no userinfo, path, query or non-443 port; no redirects; no env proxy; 1 MiB response cap.

## Package layout
`hub/ai/` : settings, gate, guard, retrieve, prompt, grounding, limits, trail, service, cli. `hub/core/ai_errors.py`: 14 error codes (exit 40 hub refused, 41 provider failure). `hub/guards/egress.py`: `permit(host)` scope used only by the adapter. Tripwires: `model_calls_total` / `egress_attempts_total` stay 0; `record_model_call` is only called from the adapter when used without the enabled gate (which then opens no socket).

## Not built
Web route: skipped because the route registry and OpenAPI are frozen (TST-SEC-01). Streaming, tools/function calling, writes of any kind.
