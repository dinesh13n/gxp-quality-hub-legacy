---
stage: "38 — Handover + Knowledge Transfer"
artifact: "operator-exercises.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/30-release/evidence/s30-rehearse.sh", "docs/30-release/evidence/s30-rehearsal-summary.txt", "docs/30-release/evidence/s30-log-01..33", "docs/29-incident-bcdr/tabletop-results.md (RH-01..RH-13)", "docs/31-observability/operational-runbook.md", "docs/30-release/rollback-plan.md", "docs/30-release/deployment-strategy.md", "hub/admin/cli.py", "hub/control/cli.py", "hub/obs/cli.py", "hub/cli.py", ".fde/orchestrator-decisions.md (OD-03a, OD-16, OD-34, OD-35, OD-37)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. Documentation only. This is the handover of a PREPARED-BUT-UNRELEASED system: Stage 30 is BLOCKED (0 of 40 approvals), no cutover, authority flip, tag or release happened, and the hub is not deployed beyond loopback. The only human is Dinesh Naik, Engagement lead (OD-04). No receiving team, trainee, walkthrough audience, exercise result, sign-off or approval is invented here; vacant roles stay vacant (Stage 37). Nothing here accepts a risk (HAR-11). The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
Ten operator exercises (OX-01..OX-10) covering the five capabilities the stage requires: **deploy, observe, diagnose, roll back, recover**. They are written so that a *receiving operator* can do them on a **sandbox copy** with the existing CLIs and compare against the expected output that the Stage 29 and Stage 30 agent rehearsals already recorded. This document is the exercise *definition*. Nobody has done these exercises as a receiving operator; see `operator-exercise-results.md` for the honest status (0 of 10 passed by a receiving team, because no receiving team exists).

Pass rule (proposed, [Assumption] A-38-OX-1): an exercise PASSES only when a named receiving operator, who is not the author of the procedure, performs every step without prompting from the author, produces the expected exit codes and states, writes the observation in the results file, and an accepting owner counter-signs. An agent running a command is a **mechanical precedent**, not a pass.

## Findings
### OX-0 Ground rules for every exercise [Verified Fact: OD-03a, OD-16, OD-35]
1. Run only on a **full sandbox copy outside the working tree** (for example `git archive HEAD | tar -x -C ~/fde_sbx/<x>/repo`, then copy the verified baseline backup over `data/`). Never run against the working-tree `data/`.
2. Before and after: `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` from the repo root must return rc 0.
3. Delete the sandbox afterwards (device VM disk is about 9.8 GB, OD-16).
4. `verify-audit` and `backup` **append audit records and rewrite the anchor** (F-29-04): do not run them in place on a store that must stay untouched as evidence.
5. The shipped config is never edited; use a scratch config JSON (for example `{"audit": {"anchor_path": "<scratch>/anchor/audit-anchor.jsonl"}}`) as in `docs/30-release/evidence/s30-rehearse.sh`.
6. No exercise may add a Zone H holder, activate a rule set, switch a scheduler on, expose a non-loopback bind, or use a real approval reference. OX-09 uses a marker that is explicitly a rehearsal marker.

### Exercise table
Let `A = python3 -B -m hub.admin --config CFG`, `C = python3 -B -m hub.control --config CFG`, `D` = scratch data dir.

| ID | Capability | Task for the receiving operator | Commands (existing, from the CLIs) | Expected result | Mechanical precedent (agent, sandbox) | Tag |
|---|---|---|---|---|---|---|
| OX-01 | Deploy | Fresh shadow-mode install on a sandbox | `A migrate --data-dir D --backup-root R`; `A status --data-dir D`; `A startup-check`; `A verify-audit --data-dir D`; `python3 -B -m hub.release posture --config CFG`; `python3 -B -m hub --config CFG golden-compare --json --data-dir G --legacy-root REPO --observe` | rc 0 for the first five; golden-compare **rc 6** (every entry UNAPPROVED because DV-01..DV-11 are proposed) is the expected, documented result; startup-check reports bind 127.0.0.1 | Stage 30 logs 01-06 (rc 0,0,0,0,0,6) | [Verified Fact] precedent |
| OX-02 | Observe | Read health and telemetry and say what is firing | `python3 -B -m hub.obs evaluate --samples NOW.json --previous BEFORE.json`; `hub report health`; `python3 -B -m hub.obs traces --log FILE` | exit 0 clean / 1 = something fires or lint finds / 2 = unreadable input (runbook RB-00); read `alerts.firing`, then `alerts.no_data`, then `slo` | **None as a human run.** Covered by the STG31 tests only. Observability modules are built but **not wired** (S31-DEV-01, D-31-01/02) so live samples do not exist | [Verified Fact] no human run; [Inference] sample files must be hand-made |
| OX-03 | Diagnose | Detect a tampered audit anchor on a COPY and classify severity | copy store+anchor; append a malformed line to the copy's anchor; `A verify-audit --data-dir COPY` | **exit 17** with `E-SEC-AUDIT-TAMPER-DETECTED` (fixed in S30-DEV-01, tests F01..F03); classify SEV-A per `docs/29-incident-bcdr/incident-severity-matrix.md`; follow RB-03/RB-04 | Stage 29 RH-07 saw exit 1 plus a traceback (defect F-29-01); Stage 30 fixed it to exit 17 (tests, not a rehearsal log) | [Verified Fact] defect + fix; [Unknown] fresh end-to-end rerun of the fixed behaviour on a rehearsal log |
| OX-04 | Roll back (L3 authority) | Refuse an authority change with no approval, then flip back to shadow | `C set-flag --flag capability_authority.CUT-2 --value authoritative --data-dir D` (no `--approval-ref`); then, using a clearly labelled **rehearsal marker only**, set it with a marker, then `C flip-to-shadow --capability CUT-2 --reason "exercise" --data-dir D`; `A verify-audit` before and after | first call **rc 2** `E-CFG-INVALID` ("--approval-ref is required for a non-default value"); flip-to-shadow rc 0; two CONFIG_CHANGED records; chain ok | Stage 30 logs 11-19 | [Verified Fact] precedent |
| OX-05 | Roll back (L2 state) | Restore the hub store from the pre-cutover backup | `A backup --data-dir D --dest-root B --label pre`; `sha256sum -c SHA256SUMS` in the backup; make changes; `A restore --data-dir D --backup B/pre`; `A verify-audit` | restore `checksum_match: true`; records written after the backup are **set aside** in `pre-restore/<stamp>/`, not merged (F-29-06); chain ok | Stage 30 logs 07-08, 20-23; Stage 29 RH-04, RH-05, RH-08, RH-09 | [Verified Fact] precedent |
| OX-06 | Roll back (L1 code) | Revert a squash commit in a clone and prove the tree equals the earlier tree | in a **clone**: `git checkout -b x`; `git revert --no-edit <squash>`; `git diff --stat <pre-squash> -- hub tests/hub` ; revert the revert | clean revert; diff rc 0; reverting the revert restores main exactly; never force-push (WB-08) | Stage 30 logs 26-31 (reverted Stage 31 squash d1e3dbb) | [Verified Fact] precedent |
| OX-07 | Recover | Refuse a corrupted backup, then recover from a good one | flip one byte in a COPY of a backup; `A restore --backup BAD`; then restore from the good backup; `A verify-audit` | corrupt restore **rc 21** `E-STORE-BACKUP-INVALID`, live store unchanged, chain ok; good restore rc 0 | Stage 30 logs 24-25; Stage 29 RH-10, RH-11 | [Verified Fact] precedent |
| OX-08 | Contain | Use the kill switch and understand its limit | set `hub.kill: true` in the **scratch** config; run any `A` command | **rc 3** `E-HUB-KILLED`; a running server does **not** re-read the switch (stop the process instead) | Stage 29 RH-12; Stage 30 log 33 (grep: kill switch checked at command start only, DS-6); live-server behaviour NOT run (U-30-04) | [Verified Fact] + [Unknown] |
| OX-09 | Govern | Explain why the release checklist refuses `ready` and who can approve | `A release-checklist --data-dir D --release R --evidence-dir E --scratch-root S --mark-ready` with unevaluated gates | **rc 20** (refuses to mark ready); `go-no-go` = NO-GO; approvals register has 40 OPEN records, 0 APPROVED | Stage 30 logs 09, 09b | [Verified Fact] precedent |
| OX-10 | Assure No-AI | Run the no-AI and egress guards and read the tripwire | `python3 -B -m hub no-ai-check` ; `A scan` | `no-ai-check` exit 9 only on findings; `scan` exit 16 only on findings; `model_calls_total` and `egress_attempts_total` stay 0 | Regression groups incl. TST-CO-11/12 (OD-34, OD-37: 31 groups green on the orchestrator's cloud workspace) | [Verified Fact] precedent (tests); no human run |

### Exercise gaps found while writing these [Inference unless marked]
- OX-G1 [Verified Fact] There is **no single install script**: the install is 8 manual commands plus the rehearsal shell script (`deployment-strategy.md` Unresolved Issues). A receiving operator needs the exercise table above, not a script.
- OX-G2 [Verified Fact] **No read-only `verify-audit`** exists (TF-06 / F-29-04). OX-03 therefore must be done on a copy, and a new operator can easily break the discipline.
- OX-G3 [Verified Fact] OX-02 cannot be done against live telemetry: observability is not wired and there is no telemetry sink. It would be done on hand-made sample files, which exercises the reading skill, not the system.
- OX-G4 [Verified Fact] OX-08 does not cover a running server; the kill switch is checked at command start only.
- OX-G5 [Verified Fact] No exercise exists for **off-device backup** (HAR-09, AP-OPS-04 open): the L2 backup and the baseline share one device (F-29-02). A device-loss recovery exercise is **not possible** with the current plan.
- OX-G6 [Assumption] The expected exit codes above are those documented and logged; a different Python (3.12+, OD-24 target) is untested (no Python 3.12+ evidence exists, OD-33). Characterization goldens are environment-specific to Python 3.10.12 (OD-23).

## Evidence References
`docs/30-release/evidence/s30-rehearse.sh`; `s30-rehearsal-summary.txt` (rc table above); `docs/29-incident-bcdr/tabletop-results.md` TR-1; `docs/31-observability/operational-runbook.md` RB-00..RB-12; `hub/admin/cli.py` docstring (command and exit-code list); `hub/control/cli.py`.

## Assumptions
- A-38-OX-1 Pass rule above is a proposal. Confirm: Engagement lead (Dinesh Naik).
- A-38-OX-2 Command spellings are taken from the CLI parsers (`hub/admin/cli.py`, `hub/control/cli.py`, `hub/obs/cli.py`) and the Stage 30 rehearsal script; they were **not re-executed in Stage 38** (docs-only stage). Confirm: first receiving operator, or Dinesh, on a sandbox.
- A-38-OX-3 Exercises run on the same reference laptop and a sandbox copy; no other environment exists (PA-17, PA-18).

## Unknowns
- U-38-OX-1 Time-to-complete for a person (agent timings are tool time only, not an RTO; Stage 29 TR-1).
- U-38-OX-2 Whether any receiving operator will exist to run them (U-37-TOM-1).

## Unresolved Issues
- OX-G1..OX-G6. Exercise scheduling needs a receiving operator and an accepting owner (see `open-handover-items.md`).

## Residual Risks
- RR-38-OX-1 Exercises pass on a tiny synthetic store (about 100 KB); behaviour on larger stores is Unknown (RB-6). Medium.
- RR-38-OX-2 Exercises are all on the happy path of an inert system; none exercise a live authoritative period. Medium.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 38). |
