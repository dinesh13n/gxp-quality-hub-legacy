# Orchestrator decisions log (engagement lead: Dinesh Naik; orchestrated by claude-fde-agent)

Every stage agent MUST read this file and honour it.

| ID | Date | Decision | Status |
|---|---|---|---|
| OD-01 | 2026-10-17 | Run all 46 stages sequentially; stop only on BLOCKED. BUILD stages run on branch `stage-NN-*`, merged to main by the orchestrator after review. | Approved by Dinesh |
| OD-02 | 2026-10-17 | Baseline dataset (Stage 0A C-1): the shipped `data/legacy.sqlite3` (125 cases, sha256 c254649f…d70aa) is the as-found baseline; the README's 6,000-case dataset (seed 4326) is recorded as an alternative/regenerable dataset. | Provisional default — Dinesh may override |
| OD-03 | 2026-10-17 | Data backup (Stage 0A C-2): `data/` copied to `../_data-backup-2026-10-17/` with SHA256SUMS.txt. NEVER run tests/preflights against the working-tree `data/` — always copy to a temp dir and point env vars there, or restore from backup afterwards and verify checksums. | Done |
| OD-04 | 2026-10-17 | No real stakeholders or production telemetry exist. Use repo evidence only; never fabricate approvals, KPIs or data. Missing evidence → Unknown/Assumption with owner "Engagement lead (Dinesh Naik)". | Approved |
| OD-03a | 2026-10-17 | Amends OD-03 per Stage 0B CP-1/CP-2: ANY code execution (tests, scripts, server, batch) runs only in a FULL copy of the repo outside the working tree (e.g. ../_sandbox/<stage>), because ≥5 modules write repo-relative data/ paths. Backup SHA256SUMS.txt now covers all backed-up files. Verify with `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` from repo root after any run. | Done |
| OD-06 | 2026-10-17 | Baseline commit a6eb4e8 tagged `baseline-as-found` (Stage 0B GD-08). | Done |
| OD-05 | 2026-10-17 | GitHub remote: dinesh13n/gxp-quality-hub-legacy (private). Push handled by orchestrator. | Pending repo creation |
| OD-07 | 2026-10-17 | Stage 5 refuted Stage 4 assumption A-04-01 (operating_costs.total_cases is random, NOT 'cases created in month'); A-04-03/A-04-05 remain assumptions; no real closure/evidence timestamps exist anywhere in the repo (K-04, K-05 unmeasurable). Stage 4 KPI sheet is NOT edited in place (frozen-provisional); any correction is a Stage 4 v0.2 addendum to be raised at the Stage 34 re-baseline or when Dinesh answers Q-02-04/05. Stages 6+ must cite P-01/P-03/P-04 only as 'generator-bounded proxies', and K-10, K-12/13 as comparing unrelated populations. | Recorded by orchestrator |
