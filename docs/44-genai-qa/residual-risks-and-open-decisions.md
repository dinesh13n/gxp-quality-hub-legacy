# Residual risks and open decisions (all Dinesh-owned, OPEN)
| ID | Item |
|---|---|
| D44-01 | Use with real (non-synthetic) data; would need a new risk assessment and removal/relaxation of the corpus guard |
| D44-02 | Computerised-system validation of the model path and a Part 11 / Annex 11 assessment (only considerations here) |
| D44-03 | Approvals: approval reference for `ai.enabled`; release/sign-off of Stage 44 |
| D44-04 | First test against a real Azure deployment (never done; no claim made) |
| D44-05 | Data-residency / tenant / content-filter settings of the Azure resource |
| D44-06 | Corporate proxy handling (adapter deliberately ignores env proxies) |
| D44-07 | Reasoning-model deployments (`token_param`, no temperature) |
| D44-08 | Web route (blocked by frozen route registry/OpenAPI; needs spec addendum) |
| D44-09 | Concurrency: rate/budget are computed from the audit log, best-effort for one operator |
| D44-10 | SOP wording for the advisory label and human verification |
| Known limit | Grounding is lexical; injection pattern list catches about 12 of 19 test strings; answers can still be wrong |
