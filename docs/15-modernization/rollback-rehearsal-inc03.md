---
stage: "15 — Transform Bad Repo → Good Repo"
artifact: "rollback-rehearsal-inc03.md"
version: "v0.1"
date: "2026-10-18"
author_agent: "claude-fde-agent"
status: "DRAFT"
scope: "INC-03 rollback procedure (hub store + audit anchor) and the FIRST rollback rehearsal (Stage 14 rollback-strategy: 'first rehearsal is INC-03 (G7)'). Stage 15 overall status: IN PROGRESS."
evidence_sources: ["docs/15-modernization/evidence/inc03/rollback-rehearsal-1/ (rehearse.sh, transcript.txt, hub-config.json, checklist + G3/G5/G6/G7 evidence)", "docs/14-transformation/rollback-strategy.md (INC-03 row, L1/L2)", "docs/12-specs/features/f10-coexistence-change-safety.md (BEH-CO-06, AC-CO-09, G7)", "hub/ops/backup.py", "hub/store/migrate.py", "hub/admin/cli.py", "tests/hub/test_inc03_supplementary.py (S01, S02)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. All execution in `~/fde_sbx/s15-inc03/rehearsal-1/` (outside the working tree).**

## Summary
Rollback rehearsal 1 was executed on 2026-10-18 from a written, executable procedure (`rehearse.sh`) in the sandbox. Result: **PASS for every step that INC-03 can exercise** — tamper detected (exit 17), L2 restore of hub store + anchor to a post-release backup (checksum match, audit chain verifies, newer store set aside, not deleted), full increment rollback (L1 code -> `main`/INC-02 via `git archive`, L2 store -> pre-migration backup B0; checksum identical to B0; INC-02 commands work), roll-forward again, forward-compatibility probe, and data checksum rc 0. **Not covered:** the replay-safety suite (G2, AC-CO-09 clause) does not exist yet; no long-running process exists to "stop".

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### RR-1 Rollback procedure for INC-03 (BEH-CO-06; rollback-strategy L1 + L2)
1. **Stop**: no hub daemon exists in INC-03; operators must not run `hub.admin` commands during a restore (procedural; RTD-36).
2. **Choose the backup**: the pre-migration backup written automatically by `python -m hub.admin migrate` (`<backup-root>/pre-migrate-<from>-to-<to>-<ts>/`) for a full increment rollback, or an operator backup (`hub.admin backup --label ...`) for an in-release restore. Each backup holds `hub.sqlite3` (VACUUM INTO snapshot), the anchor file, `MANIFEST.json` and `SHA256SUMS`.
3. **Restore** (L2): `python -m hub.admin --config <cfg> restore --data-dir <data> --backup <dir>` — verifies the backup checksums first (E-STORE-BACKUP-INVALID exit 21, nothing touched), moves the current `hub.sqlite3` and anchor file to `<data>/pre-restore/<ts>/` (hold-all: nothing deleted), copies the backup in, re-verifies checksums, runs `verify-audit` against the restored anchor (exit 17 on mismatch), then records STORE_RESTORED + CONFIG_LOADED.
4. **Code** (L1): redeploy the previous commit (rehearsed with `git archive main hub` into the sandbox; no checkout of the working tree).
5. **Verify + restart**: `hub.admin verify-audit`, `hub.admin status` (no pending/unknown versions), INC-02 `python -m hub deviations` / `selfcheck`.

### RR-2 Rehearsal 1 results (transcript: `evidence/inc03/rollback-rehearsal-1/transcript.txt`; code main=8a01da7, inc03=68b93f3)
| Step | Action | Observed | Result | Tag |
|---|---|---|---|---|
| 1 | INC-02 code `python -m hub init` | M000 store created | rc 0 | [Verified Fact] |
| 2 | INC-03 `migrate` (auto backup B0), 2 users, release checklist, `verify-audit` | M000->M001; B0 = M000 snapshot sha f38e62b9…; checklist G3/G5/G6/G7 pass, G1 fail, others not_run (release blocked); chain ok | rc 0 | [Verified Fact] |
| 3 | operator backup B1, then user `carol` after B1 | B1 audit head seq 11 | rc 0 | [Verified Fact] |
| 4 | INCIDENT: offline edit of audit seq 5 (triggers dropped) | `verify-audit` exit 17, first_broken_seq 5, altered_record | detected | [Verified Fact] |
| 5 | L2 restore to B1 | checksum_match true (hub.sqlite3 78b8b0ea…, anchor 8092005c… = manifest); restored chain ok (11 records, 6 anchors); carol absent (RPO window); tampered store + anchor set aside under `pre-restore/` | PASS | [Verified Fact] |
| 6 | Full increment rollback: restore B0 + INC-02 code | restored sha f38e62b9… == B0 manifest; schema_migrations [M000]; INC-02 `deviations` lists DV-01..09, `selfcheck` ok | PASS | [Verified Fact] |
| 7 | Roll forward again (INC-03 `migrate`) | new pre-migration backup; M001; fresh chain verifies (2 records) | PASS | [Verified Fact] |
| 8 | INC-02 code against an M001 store copy | `deviations` works (INC-02 `open_hub` ignores unknown versions) | PASS (forward compatible) | [Verified Fact] |
| 9 | `sha256sum -c --quiet` backup manifest | rc 0 | PASS | [Verified Fact] |
[Verified Fact] The `restored sha` printed after step 5 differs from the manifest because the `restore` command appends STORE_RESTORED/CONFIG_LOADED after its own checksum comparison; the in-command comparison (`checksum_match: true`, `restored` digests) is the evidence.

### RR-3 Gate G7 / AC-CO-09 coverage
| AC-CO-09 clause | Status | Tag |
|---|---|---|
| store restored | met (steps 5, 6) | [Verified Fact] |
| checksum matches | met | [Verified Fact] |
| audit chain verifies | met (step 5; step 6 store predates the audit table -> not applicable) | [Verified Fact] |
| replay-safety suite passes | NOT RUN - suite does not exist until INC-06 (G2) | [Verified Fact] |
TST-CO-09 is not in the INC-03 test map; mechanics are additionally covered by TST-HUB-INC03-S01/S02 and by the G7 evaluator (`hub/ops/gates.py`).

## Evidence References
- `docs/15-modernization/evidence/inc03/rollback-rehearsal-1/{rehearse.sh,transcript.txt,hub-config.json,checklist-R-inc03-rehearsal.json,G3.json,G5.json,G6.json,G7.json}`.
- `docs/14-transformation/rollback-strategy.md` INC-03 row; `docs/12-specs/features/f10-coexistence-change-safety.md` BEH-CO-06.

## Assumptions
- A-15-RR-1 [Assumption] A CLI-only hub with no daemon makes "stop process" procedural; when a server exists (INC-04+) the procedure needs a real stop/lock step. Confirm: Engagement lead (Dinesh Naik), Stage 28/30.

## Unknowns
- U-15-RR-1 Production RPO/RTO targets for the hub store (no SLO decided; Stage 28/31).

## Unresolved Issues
- G2 replay-safety clause of AC-CO-09 open until INC-06; re-rehearse then (and at every later increment, CG-10).

## Residual Risks
- RR-RB-1 Records written after the restored backup exist only in the set-aside copy; no merge tooling (RTD-33).
- RR-RB-2 After a full rollback to B0 and roll-forward the live audit chain restarts at seq 1; the earlier chain is preserved only in `pre-restore/` (RTD-33).
- RR-RB-3 Rehearsal used synthetic users and the sandbox only; no production-like volume.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-18 | claude-fde-agent | INC-03: procedure + rehearsal 1 (branch `stage-15-inc03-hub-db-audit`). |
