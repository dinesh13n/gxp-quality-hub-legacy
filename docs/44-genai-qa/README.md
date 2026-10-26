# Stage 44 - Optional Azure OpenAI Document Q&A (OFF by default) v0.1

Status: CONDITIONAL PASS (see gate in test-plan-and-evidence.md). Authorised by Dinesh Naik on 2026-10-26 (OD-40).
Nothing here is released, validated or approved. No real Azure call was made; all evidence is from a local fake server.

| Document | Content |
|---|---|
| requalification-record.md | RQ triggers, risk assessment, Part 11 / Annex 11 considerations |
| architecture-and-plugin-points.md | Design and exactly where the Azure OpenAI model plugs in |
| setup-runbook.md | Dinesh: set env vars, enable, test with fake then real, turn off |
| test-plan-and-evidence.md | Tests, groups, results, honest limits |
| rollback.md | Turn it off; nothing is deleted |
| residual-risks-and-open-decisions.md | Dinesh-owned OPEN items |
| hub-config.ai.example.json | Shipped config shape (empty placeholders, enabled=false) |
| evidence/ | Two sample outputs, produced against the local FAKE only |
