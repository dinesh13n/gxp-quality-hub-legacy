# Orchestrator decisions log (engagement lead: Dinesh Naik; orchestrated by claude-fde-agent)

Every stage agent MUST read this file and honour it.

| ID | Date | Decision | Status |
|---|---|---|---|
| OD-01 | 2026-10-17 | Run all 46 stages sequentially; stop only on BLOCKED. BUILD stages run on branch `stage-NN-*`, merged to main by the orchestrator after review. | Approved by Dinesh |
| OD-02 | 2026-10-17 | Baseline dataset (Stage 0A C-1): the shipped `data/legacy.sqlite3` (125 cases, sha256 c254649f…d70aa) is the as-found baseline; the README's 6,000-case dataset (seed 4326) is recorded as an alternative/regenerable dataset. | Provisional default — Dinesh may override |
| OD-03 | 2026-10-17 | Data backup (Stage 0A C-2): `data/` copied to `../_data-backup-2026-10-17/` with SHA256SUMS.txt. NEVER run tests/preflights against the working-tree `data/` — always copy to a temp dir and point env vars there, or restore from backup afterwards and verify checksums. | Done |
| OD-04 | 2026-10-17 | No real stakeholders or production telemetry exist. Use repo evidence only; never fabricate approvals, KPIs or data. Missing evidence → Unknown/Assumption with owner "Engagement lead (Dinesh Naik)". | Approved |
| OD-05 | 2026-10-17 | GitHub remote: dinesh13n/gxp-quality-hub-legacy (private). Push handled by orchestrator. | Pending repo creation |
