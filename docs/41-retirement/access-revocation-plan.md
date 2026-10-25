---
stage: "41 — Retirement / Decommissioning"
artifact: "access-revocation-plan.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/27-hardening/identity-rbac-hardening.md", "docs/24-security-privacy/{security-control-matrix,authentication-map,residual-security-risks}.md", "docs/21-integration/authentication-map.md", "docs/37-operating-model/{target-operating-model,security-ownership,service-ownership-map}.md", "docs/00-preflight/operating-contract/provisional-tool-agent-permissions.md", "docs/33-vendor-risk/vendor-inventory.md", "hub/security/{auth,tables,zone_h}.py", "hub/web/tokens.py", "hub/admin/cli.py", "hub/store/db.py", "app/server.py", "services/source_gateway/server.py", ".fde/orchestrator-decisions.md (OD-17, OD-28, OD-31, OD-33, OD-34)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. DOCUMENTATION ONLY. No account, token, role, permission or grant is changed. There are no real users and no real credentials (OD-04, OD-28). Revocation is planned for the day real access exists; it is executed only with owner approval and rehearsed on a copy first.**

## Summary
Access revocation answers: **who or what can reach each asset, how is that access ended, in what order, and how is the end proven.** Findings:

1. **Almost nothing needs revoking today.** The hub binds loopback only (CR-5), `zone_h.holders` is empty (OD-31), no real principal exists, the legacy API and gateway default to 127.0.0.1 (`app/server.py` L63, `services/source_gateway/server.py` L43), and there is no SSO, no cloud role and no network exposure. The real access today is **OS-level** (the device user, the cloud workspace account, the code-host account, the assistant account), all held by Dinesh Naik. [Verified Fact]
2. **The hub has no "disable user" operation.** `principal` is a retained table whose rule is "no deletion, status change only" (`hub/security/tables.py`), but no code path changes `principal.status` (grep for `UPDATE principal` in `hub/`: none) and the admin CLI offers `user create` and `user list` only. Human accounts can therefore be neutralised only by other means (stop the service, archive the store, rotate nothing). This is a gap to close before real users exist, not a defect today. [Verified Fact: grep and CLI listing; Inference: consequence]
3. **Service tokens and sessions are revocable** (`service_token_revocation` rows; session `revoked_at`). [Verified Fact]
4. **Revocation order matters:** stop writers first, then revoke machine access, then human access, then toolchain accounts, and keep read access for the archive custodian until the archive is verified.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### AC-1 Access inventory and revocation method
| ID | Access path | Holder today | Asset | Revocation method (proposed, not executed) | Proof of revocation | Gap | Tag |
|---|---|---|---|---|---|---|---|
| AC-01 | Hub human principals (roles reviewer, quality_lead, compliance, dispositioner, finance_read) | none real; synthetic ones only in sandbox stores built by tests (SH-3) | RA-15 | Stop the service; archive store; for a live store, a "disable principal" operation would be needed (not built) | store archived; service not running; `user list` shows state | no disable operation | [Verified Fact] |
| AC-02 | Hub service principal and `svc_` tokens (role `integration`) | none issued in the repo | RA-15, RA-22 | `hub.web token` revoke (insert-only revocation row); then revoke the service principal | revocation row present; token refused (401) on a copy | principal disable missing | [Verified Fact] |
| AC-03 | Active sessions (idle 30 min, absolute 8 h) | none | RA-15 | End by stopping the service; `revoked_at` set on logout; absolute expiry ends the rest | `session.revoked_at` or expiry | no "revoke all sessions" command found | [Verified Fact] limits; [Inference] gap |
| AC-04 | Zone H holders (`zone_h.holders`) | EMPTY by decision (OD-17, OD-31) | RA-15 | Nothing to revoke; keep empty; any non-empty list is removed by a flag-and-config change with `approval_ref` | config shows empty list | none | [Verified Fact] |
| AC-05 | Host operator (OS user running the CLI, owner of the store file 0600) | Dinesh Naik | RA-15, RA-11, RA-21 | End by archive and OS account removal on the host; keep the custodian's read access to the archive until verified | OS-level; Unknown tooling | custodian continuity | [Verified Fact] store mode; [Unknown] OS account process |
| AC-06 | Legacy API (port 8080, GET only) and gateway (port 8090) | local processes started manually (RC-5 of Stage 7: no scheduler) | RA-01, RA-04 | Stop the processes; remove run.sh from use; no accounts exist | no listener on 8080/8090 on the host | Compose publishes ports in the container variant (`environments/production-like.env.example` has `HOST=0.0.0.0`): never run (HAR-05) | [Verified Fact] |
| AC-07 | Legacy batch/Java/Node jobs | manual CLI invocations | RA-02, RA-05, RA-06 | Stop invoking; archive code; there is no scheduler to disable | no cron or service unit in repo | scheduler outside the repo Unknown | [Verified Fact] / [Unknown] |
| AC-08 | Git remote access (`origin` github.com/dinesh13n/gxp-quality-hub-legacy, private) | Dinesh Naik; collaborator list not in the repo | RA-20 | After AU-4 mirror verified: change repo to archived/read-only at the host (owner decision); remove collaborators if any; do not delete the repo | host settings screenshot or export; `git ls-remote` | collaborator list, 2FA and branch protection Unknown (VA-02) | [Verified Fact] remote; [Unknown] settings |
| AC-09 | Orchestrator cloud workspace (V-05) | Dinesh Naik's account; provider Unknown | RA-18 | Delete workspace data copy and end the workspace after AU-2 verified; provider terms decide proof | provider deletion record (Unknown form) | provider unknown | [Verified Fact] usage; [Unknown] |
| AC-10 | AI coding assistant sessions and any repo access granted to it (V-04) | Dinesh Naik's account | RA-19 | End tool access to the repo and remote; remove any app/token authorisation at the code host | host authorised-apps list | terms, retained context Unknown (LR-3) | [Verified Fact] usage; [Unknown] |
| AC-11 | Reference laptop / device VM and connected folders (V-10) | Dinesh Naik | RA-25 | Disconnect folders; wipe per owner's device policy after archive verified; deletion needs HAR-03 for repo/backup files | owner attestation | device policy Unknown | [Verified Fact] |
| AC-12 | Hosting, DNS, certificates, secrets store, monitoring, ticketing | none evidenced | n/a | none known | n/a | Unknown whether any exists (U-37-SO-2) | [Unknown] |

### AC-2 Order of operations (per wave, after RC-2 criteria)
1. Announce and freeze (owner decision recorded): stop writers (legacy jobs, hub serve).
2. Take and verify the archive (`archive-plan.md` AR-2).
3. Revoke machine access first: service tokens (AC-02), then listeners (AC-06).
4. Revoke human access: sessions end; principals neutralised by method available at that time (AC-01).
5. Keep one read path for the archive custodian until the restore test passes.
6. Revoke toolchain access (AC-08..AC-11) last, after the archive and evidence are committed and mirrored.
7. Run the proof step for each row; commit the evidence; update `retirement-evidence.md`.

### AC-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| ARF-01 | [Verified Fact] No human-account disable operation exists in the hub; `principal.status` is never updated by code | `hub/security/tables.py` L26; grep `UPDATE principal` in `hub/` = none; `hub/admin/cli.py` subcommands create/list | If real accounts existed, an ex-user could not be disabled by an audited operation | Medium (High with real users) | High | Build under a spec change (D-41-11) |
| ARF-02 | [Verified Fact] All real access is held by one person across five accounts | `service-ownership-map.md` SF-03; `vendor-inventory.md` V-03..V-05, V-10 | Revocation and its proof depend on one person; no independent check | Medium-High | High | Second custodian (D-41-12) |
| ARF-03 | [Verified Fact] Session and token mechanics are revocable and expire; no secret in config | `hub/security/auth.py`, `hub/web/tokens.py` | Machine and session revocation is straightforward | Low | High | none |
| ARF-04 | [Unknown] Collaborators, 2FA, branch protection and authorised apps at the code host | VA-02 | Cannot prove revocation at the host | Medium | High | Owner supplies settings |
| ARF-05 | [Verified Fact] Zone H holder list is empty; the human gate refuses every request on the shipped config | `hub/security/zone_h.py`; OD-31 | No dispositioner access exists to revoke; retiring the hub changes no human authority | Low | High | none |

## Evidence References
See `evidence_sources`. Companion: `secret-key-revocation.md` (credentials and keys), `vendor-termination-plan.md` (accounts at vendors), `decommission-checklist.md` steps B-01..B-10.

## Assumptions
- A-41-AC-1 [Assumption] No access exists beyond AC-01..AC-12 (the repo cannot show external grants). Confirm: Engagement lead (Dinesh Naik).
- A-41-AC-2 [Assumption] The hub's `session` and `service_token` mechanics behave on a real store as described in code; not re-run here. Confirm: Build agent at rehearsal.
- A-41-AC-3 [Assumption] A "disable principal" operation, if built, follows the same audited, insert-only pattern as `USER_CREATED`. Confirm: Stage 12 spec addendum.

## Unknowns
- U-41-AC-1 Code-host collaborators, 2FA, authorised apps (VA-02).
- U-41-AC-2 Any scheduler or process supervisor outside the repo that starts legacy jobs.
- U-41-AC-3 Device and workspace deprovisioning procedures.

## Unresolved Issues
- UI-41-AC-1 D-41-11 (build a disable-principal operation before any real user) and D-41-12 (second custodian). Owner: Engagement lead (Dinesh Naik).

## Residual Risks
- RR-41-AC-1 An unrevoked grant at a third party (Medium).
- RR-41-AC-2 Revocation proof by self-attestation of one person (Medium-High); not accepted.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 41). |
