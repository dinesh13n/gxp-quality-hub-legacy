---
stage: "29 — AI Incident Response + BC/DR"
artifact: "containment-procedures.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent (Stage 29 run)"
status: "DRAFT"
evidence_sources: ["docs/29-incident-bcdr/ai-incident-playbook.md", "docs/29-incident-bcdr/evidence/s29-log-07..13", "hub/admin/cli.py", "hub/control/cli.py", "hub/control/switch.py", "hub/config.py", "hub/guards/", "docs/23-human-control/human-override-policy.md", "docs/00-preflight/operating-contract/stop-conditions.md", "docs/00-preflight/operating-contract/provisional-human-approval-rules.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Documentation only (Stage 29 VALIDATE mode, docs-only authorisation). Nothing here is an approval, a commitment by any person, or an acceptance of a risk (HAR-11, TP-14, OD-32). The only named human is Dinesh Naik, Engagement lead (OD-04); every other role is VACANT or Unknown. Procedures are written for a loopback, No-AI (OD-08), synthetic-data product and have not been exercised by a team. All RTO/RPO figures are TARGETS or ASSUMPTIONS, not measurements.**

## Summary
Containment steps for every scenario IS-01..IS-12. Principle: **contain by stopping and isolating, never by repairing in place** (STOP rules; no self-repair). Where a command is given it exists in the repo today (`hub/admin/cli.py`, `hub/control/cli.py`) and, where noted, was run in a sandbox rehearsal on 2026-10-25. No step here deletes anything: hold-all is the interim retention rule (OD-15, HAR-03). Several steps need a human approval that only Dinesh can give; the agent prepares, it does not approve.

Sandbox note: the hub refuses to run inside a git worktree or against the baseline backup (`hub/guards/sandbox.py`), so every hub command in these procedures runs against a hub data directory **outside the working tree** (`--data-dir`) with the config file that sets `audit.anchor_path` (E-CFG-INVALID otherwise, rehearsal step 01 first attempt).

## Findings
### CT-0 Common first five minutes (all scenarios) [Inference: sequence; each command Verified Fact]
1. **Stop the activity** that raised the signal. A running local server: stop that process by its PID (no `pkill -f`); a running agent task: halt it and tell the orchestrator.
2. **Set the kill switch** if the hub could still be started by anyone: edit the config FILE key `hub.kill` to `true` by hand and record the reason in the incident record. `hub.kill` is an "other control", not a registered decision flag, so `python -m hub.control set-flag` refuses it; stopping needs no approval (`hub/control/flags.py`, FF-2 rule 6) [Verified Fact]; clearing it is Dinesh's decision [Assumption]. Effect observed in the sandbox: any `hub.admin` command then exits 3 with `E-HUB-KILLED` (rehearsal step 12, 0.06 s). **Limit:** the flag is read when a command starts; whether a server already running re-reads it is not shown [Unknown, PBF-05], so stopping the process is the sure step. A hand edit is not audited by the hub (only `set-flag`/`flip-to-shadow` write `CONFIG_CHANGED`); the next start records `CONFIG_LOADED` with the config hash.
3. **Capture volatile evidence now** (stderr output of the terminal, `git status --porcelain`, `ls -l` and `sha256sum` of the store, anchor and config) into a new folder outside the working tree. Product logs are not persisted (DEV-70).
4. **Do not run `verify-audit`, `backup`, `anchor` or `restore` on the live store yet**; each appends an audit record and rewrites the anchor (rehearsal steps 03-06: record count rises with every command). Copy first (`forensics-evidence-policy.md` FE-03).
5. **Open the incident record** (playbook PB-5) and tell Dinesh (comms CM-01).

### CT-1 .. CT-12 by scenario
| CT | Scenario | Contain (in order) | Approval needed | Verify containment | Evidence |
|---|---|---|---|---|---|
| CT-01 | IS-01 hostile text | (1) Leave the item stored as Untrusted; do not edit or delete it; (2) if an agent read it as an instruction, stop that agent task (STOP-05) and quote the source path; (3) confirm no state change: `git status --porcelain` clean outside the stage path and `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0; (4) mark the source file/item reference in the incident record | none to contain; HAR-14 to continue a stage that raised STOP-05 | checksum rc 0; diff shows only permitted paths | S40 corpus (SCM-10..12), `docs/26-tevv/red-team-findings.md` |
| CT-02 | IS-02 unsafe action | (1) Halt the actor; (2) `git status`/`git diff` and checksum to list what changed; (3) do NOT revert by hand; (4) set `hub.kill`; (5) for a Zone H act: confirm `zone_h.holders` is still empty (shipped state) and list `ZONE_H_ATTEMPT`/Zone H audit rows from a COPY of the store; (6) for a merge/push: record the SHA, tag or branch it, do not force-push or rewrite history (CC-01) | Revert/restore of `data/` is HAR-01; deleting is HAR-03; both Dinesh | checksum rc 0 again after approved restore; `git log` shows no unapproved commit on `main` | HAR-01, HAR-04, HAR-12, STOP-01/03/07 |
| CT-03 | IS-03 compromised tool | (1) Stop using the tool; (2) rotate nothing automatically (no secrets are held by the product; the host/tooling credentials are Unknown); (3) pin: no new dependency or Action may be added (stdlib only, HAR-07/08); (4) freeze `main` (stop merges) and tag HEAD per exit-plan common steps; (5) compare the tool's recent output against the golden/regression baseline in a sandbox | HAR-07, HAR-08, HAR-09 for any change | orchestrator full regression executed = expected; goldens unchanged | `docs/33-vendor-risk/exit-plan.md`, `supply-chain-controls.md` |
| CT-04 | IS-04 data leakage | (1) Stop the egress path or the commit; (2) if in git and not pushed: do not push; record the commit id, leave it (no history rewrite without Dinesh); if pushed to the private remote: tell Dinesh, no force-push; (3) secret-like value: treat as exposed even if synthetic until shown otherwise; list where (audit, log, doc); (4) restricted evidence read by wrong role: list the audit rows (C3 reason recorded) | HAR-09 (off-device), HAR-03 (any removal) | `scan`/secret regex over hub, tests/hub, docs (S33); `git diff` for DB/lake files | `hub/security/scan.py`, `E-SEC-SECRET-IN-AUDIT` |
| CT-05 | IS-05 bad retrieval | (1) Record query, expected and actual; (2) if a decision was taken on it, mark that decision for human re-review (no edit; history is insert-only); (3) do not rebuild the search index on the live store before copying | Rebuild of any index: operator under change governance | repeat the query in a sandbox copy | `hub/search/` |
| CT-06 | IS-06 provider/tool unavailability | (1) Pause build work; (2) write the state into the OD log via the orchestrator; (3) failover FO-3/FO-4 only with Dinesh; (4) nothing in the product depends on a provider | Dinesh for any vendor switch (HAR-11) | tests unchanged and green on the replacement | exit-plan V-04, V-05 |
| CT-07 | IS-07 cost runaway | (1) Stop the runaway job/session; (2) read `model_calls_total` and `egress_attempts_total`; non-zero = SEV-B; (3) record spend if visible to Dinesh (Unknown to the agent); (4) free disk by moving, not deleting, sandbox copies into a `_to_delete/` folder until Dinesh approves deletion | HAR-03 for deletion | disk and counters re-read | OD-16, STOP-10 |
| CT-08 | IS-08 corrupted configuration | (1) Do not start the hub; (2) compare config file to the last committed or recorded version (location of production config is Unknown); (3) refuse any flag/authority value without `approval_ref` (the hub refuses at start-up: E-CFG-INVALID); (4) `python -m hub.control --config FILE flip-to-shadow --capability X --reason R --data-dir D` returns a capability to shadow; it needs a non-empty reason, opens the store and writes a `CONFIG_CHANGED` audit record, and needs no approval_ref because it moves to the default (`hub/control/cli.py` `_change`) | Setting an `authoritative` value needs approval_ref (HAR-11); flip-to-shadow is a safe-direction action; the code needs no approval, so L1 may run it [Assumption on who is L1] | `python -m hub.control flags` shows shadow; start-up refuses bad config | `hub/control/`, EH-07, EH-10 |
| CT-09 | IS-09 infrastructure outage | (1) Check which of repo, store, backup, `data/` are reachable; (2) copy what is reachable to a second location before any retry; (3) do not run generators or tests against `data/` to "test the fix" (STOP-02) | none to copy; HAR-01 to restore | checksum rc 0 on reachable copies | exit-plan V-10, V-03, V-05 |
| CT-10 | IS-10 disaster | (1) Stop everything that writes; (2) establish which copies survive: laptop/VM disk, GitHub private remote (code only, `data/` is git-ignored), cloud workspace (checksum-gated copy of data per OD-23) ; (3) preserve whatever survives read-only; (4) go to RV-10 | Dinesh; off-device copies need HAR-09 | survivor list written with sha256 | `RC-7`, `RC-8` |
| CT-11 | IS-11 chain break | (1) Stop the hub (process by PID) and set `hub.kill`; (2) copy `hub.sqlite3`, `-wal`, `-shm`, the anchor and the config; hash them; (3) run `verify-audit` ONLY on the copy in a sandbox to learn `kind` and `first_broken_seq`; (4) never "fix" the chain; (5) escalate to Dinesh (and RL-05/RL-06 when staffed) | Restore only with approval (HAR-01) | sandbox `verify-audit` on the copy; result recorded | EH-03, rehearsal steps 07-09 |
| CT-12 | IS-12 feed delay/divergence | (1) Keep the run record (RUN_FAILED/mismatch); (2) do not reconcile by spreadsheet and overwrite; (3) late items need a manual catch-up run (FG-02; scheduler OFF, OD-28); (4) disputed root cause: escalate to L3 for tie-break (ER-12) | none for catch-up (idempotent); owner of the feed is VACANT | next run totals = source count (PNFR-11) | `failure-semantics.md` FS-STALE-02, INC-2025-014 |

### CT-13 Containment capability gaps
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| CTF-01 | [Verified Fact] A malformed anchor line makes `verify-audit` print the correct tamper envelope but then crash with a KeyError in the end-of-run anchor write; the process exits 1, not the documented 17 | `evidence/s29-log-07-verify-audit-after-damage.txt`; `hub/security/audit.py` `read_anchors` line 119 via `hub/admin/cli.py` `close` line 122 | A wrapper keyed on exit 17 would mis-classify; direction is still fail-closed (non-zero) | Medium-Low | High | Fix in Stage 30 or accept? (not fixed here: VALIDATE mode) |
| CTF-02 | [Inference] No automated barrier stops an agent writing `data/`; protection is rule + before/after checksum | STOP-01, HAR-01 | A write is noticed after, not prevented | Medium | Medium | Read-only mount or OS permission for `data/`? [Unknown] |
| CTF-03 | [Verified Fact] No new-incident folder or ticketing exists | support-model SM-3 | Records may be ad hoc | Low | High | where records live |
| CTF-04 | [Unknown] Whether a running server honours `hub.kill` | PBF-05 | Containment of a running server relies on stopping the process | Medium | Medium | sandbox check |

## Evidence References
`docs/29-incident-bcdr/evidence/` logs 07-13; `hub/admin/cli.py`; `hub/control/cli.py`; `docs/23-human-control/human-override-policy.md`; `docs/21-integration/failure-semantics.md`.

## Assumptions
- A-29-CT-1 [Assumption] flip-to-shadow may be run by L1 without separate approval because it moves toward the safe state. Confirm: Dinesh.
- A-29-CT-2 [Assumption] Stopping a process by PID is available to the operator on the host.

## Unknowns
- U-29-CT-1 Whether a running server re-reads `hub.kill`.
- U-29-CT-2 Where a production config file would live and who may edit it.
- U-29-CT-3 Credentials held by tooling accounts (assistant, GitHub, workspace): not visible to the agent.

## Unresolved Issues
- CTF-01 exit-code defect; CTF-02 no barrier on `data/`; owners vacant for CT-12.

## Residual Risks
- RR-29-CT-1 Containment depends on the operator noticing in time (no alerting).
- RR-29-CT-2 A set-aside copy is still on the same device as the thing it protects.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent (Stage 29 run) | First issue (Stage 29). |
