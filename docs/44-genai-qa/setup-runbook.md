# Setup runbook (Dinesh)

Everything below is for synthetic data only. Do not point it at real data (OPEN decision).

## 0. Default
Nothing to do. Shipped config has `ai.enabled=false`. `python -m hub.ai status --data-dir <dir>` reports state without a model call.

## 1. Test with the local fake (no Azure)
Run the regression group S44 and E44 (see test-plan-and-evidence.md). They start a fake Azure OpenAI server on loopback.

## 2. Real deployment (your decision, your key)
1. Set the four env vars in your own shell session only (PowerShell: `$env:AZURE_OPENAI_ENDPOINT = ...`; cmd: `set ...`). Endpoint form `https://<resource>.openai.azure.com`. Enter the key interactively; never put it in a file, the config, a script in the repo, or chat.
2. Copy hub-config.ai.example.json to your local config; set `ai.enabled` to true. The decision flag needs an approval reference for `ai.enabled`; record your approval per your procedure.
3. Use a SYNTHETIC data directory (origin shipped/synthetic/fixture). A real corpus is refused.
4. `python -m hub.ai --config <cfg> ask --data-dir <dir> --principal <id> --text "Tell me about batch records retention"`.
5. Exit codes: 0 answered; 40 refused by the hub (disabled, not configured, kill switch, non-synthetic, no retrieval, rate/budget, ungrounded); 41 provider failure (timeout, 429, rejected, unavailable, bad response).
6. Check the audit log for AI_QA_* entries; confirm no key appears anywhere.

## 3. Turn off
Set `ai.enabled` to false (or `hub.kill`), and clear the env vars (`Remove-Item Env:AZURE_OPENAI_API_KEY`). See rollback.md.
