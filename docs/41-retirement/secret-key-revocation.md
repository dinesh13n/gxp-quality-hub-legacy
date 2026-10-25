---
stage: "41 — Retirement / Decommissioning"
artifact: "secret-key-revocation.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["docs/27-hardening/secrets-hardening.md (SH-1..SH-4)", "docs/24-security-privacy/{data-protection-controls,residual-security-risks}.md (RS-03, RS-08, DQ-S24-02)", "hub/security/{auth,anchor_seal,cli,audit}.py", "hub/web/tokens.py", "hub/admin/cli.py", "hub/runs/cli.py", "app/store.py, app/server.py, app/gateway_bridge.py, services/source_gateway/server.py (environment variable reads)", "environments/*.env.example", ".github/workflows/verify.yml", "docs/33-vendor-risk/vendor-inventory.md", "docs/00-preflight/operating-contract/data-use-constraints.md", ".fde/orchestrator-decisions.md (OD-28, OD-32, OD-34)"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated. DOCUMENTATION ONLY. No key, token, password or secret is read, rotated, revoked, printed or destroyed. No secret value appears in this document. There are no real credentials in the repository (OD-28, SH-3: 0 findings in the Stage 27 secret scan). Revocation is planned for the day real secrets exist, with owner approval and a rehearsal on a copy.**

## Summary
The honest position is that **the repository contains no secret to revoke**; what exists is (a) secrets that the *hub design* creates at run time and stores only as hashes or digests, (b) two environment-variable secrets read by operator CLIs, (c) one optional integrity key (`HUB_ANCHOR_SEAL_KEY`) whose custody is undecided, and (d) credentials of the toolchain accounts (code host, cloud workspace, assistant) that live outside the repo and whose form is Unknown. A retirement therefore needs a **secret inventory confirmed by the owner**, a **revocation order**, and one specific rule: **do not destroy the anchor seal key while archived audit evidence still needs verifying.** [Verified Fact for (a)-(c); Unknown for (d)]

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SK-1 Secret inventory and revocation treatment
| ID | Secret / credential | Where it lives | Form at rest | Issued by | Retirement treatment (proposed) | Proof | Tag |
|---|---|---|---|---|---|---|---|
| SK-01 | Human passwords | `principal.pw_hash`, `pw_salt` | PBKDF2-HMAC-SHA256, 600,000 iterations, 16-byte salt | `hub.admin user create` (password from interactive prompt or `HUB_NEW_USER_PASSWORD`) | Not revocable by deleting; neutralise by stopping service and archiving the store; a disable operation does not exist (`access-revocation-plan.md` ARF-01). Hashes stay inside the archive | service stopped; archive verified | [Verified Fact] |
| SK-02 | Session tokens | `session.token_sha256` | sha256 of 256-bit token | login | Expire (idle 30 min, absolute 8 h) or `revoked_at` on logout; stopping the service ends all use | `session` rows | [Verified Fact] |
| SK-03 | Service tokens `svc_...` | `service_token` (+ `service_token_revocation`) | sha256 digest only; plaintext shown once | `hub.web token issue` | Revoke each by inserting a revocation row (`tokens.revoke`); expiry is optional (RS-08, 90 days proposed, not built) | revocation row; 401 on a copy | [Verified Fact] |
| SK-04 | Re-authentication proof | derived, not stored | sha256 of 'reauth:' + session digest + time | login | none needed (derived; 300 s window) | n/a | [Verified Fact] |
| SK-05 | Anchor seal key `HUB_ANCHOR_SEAL_KEY` (opt-in, at least 32 bytes) | operator environment only, never in config, never echoed | HMAC key | operator | **Do not destroy while any archived anchor needs verification.** Stop sealing new anchors (retire the key for signing); keep or escrow the key (or its verification role) for the verification window set by the owner; then destroy per owner decision. Key custody is undecided (DQ-S24-02, U-S24-DP-2) | key custody record (no value) | [Verified Fact] mechanism; custody [Unknown] |
| SK-06 | Audit anchor file | file at `audit.anchor_path`, mode 0600 on creation (S27-DEV-14) | JSON lines (hash, seq, time); not a secret but a tamper-evidence artifact | hub | Not revoked: archived with the chain (NR-2). Treat as evidence, not as a secret | hash in AU-3 manifest | [Verified Fact] |
| SK-07 | Scripted passwords `HUB_NEW_USER_PASSWORD`, `HUB_RUN_PASSWORD` | process environment of the operator | plaintext in the environment while a command runs | operator | Unset in shells and any profile/script that sets them; confirm none is persisted | owner attestation; `env` check on host | [Verified Fact] usage; [Unknown] persistence on the host |
| SK-08 | Store file and data directory | `<data-dir>/hub.sqlite3`, directory mode 0700 | holds hashes | hub | Archived; live copy handled per RL-2/RL-3 rules and HAR-03 | `ls -l` mode; archive manifest | [Verified Fact] |
| SK-09 | Legacy environment variables `LEGACY_DB`, `HOST`, `PORT`, `SOURCE_PORT`, `SOURCE_URL` | environment / `environments/*.env.example` | configuration, not secrets | operator | No revocation; remove from run scripts when the legacy tree is retired | n/a | [Verified Fact] |
| SK-10 | Code-host credentials (login, 2FA, SSH keys or tokens used to push) | outside the repo; no push credential in this session | Unknown | owner | Owner rotates or removes keys/tokens used for the repo after the mirror is verified; revoke authorised apps (AC-08, AC-10) | host settings export | [Unknown] |
| SK-11 | Cloud-workspace and assistant credentials, API keys if any | outside the repo | Unknown | owner | Owner inventories and revokes at the provider; deletion proof per provider terms (Unknown) | provider record | [Unknown] |
| SK-12 | CI secrets | none: `verify.yml` references none; never run | n/a | n/a | none | n/a | [Verified Fact] |
| SK-13 | Test and fixture secrets: synthetic holders `holder-1`, `holder-2`, test passwords | only inside sandbox stores built by tests | throw-away | tests | Disappear with sandbox cleanup (OD-16); not present in shipped config (`zone_h.holders` empty) | sandbox deleted | [Verified Fact] |
| SK-14 | Git history | all commits | plain text | n/a | **Not scanned**: SH-4 notes no scan of git history was done. Run a history secret scan on a clone before archive and before any repo is made visible to anyone else | scan output with hash | [Unknown] (not done) |

### SK-2 Revocation procedure (order, per wave; executed only with owner approval)
1. Stop all writers and listeners (hub serve; legacy 8080/8090).
2. Inventory confirmation: owner lists any secret not in SK-01..SK-14 (SK-10/SK-11 especially) and signs the list. No agent can add real ones.
3. Revoke service tokens (SK-03) one by one; record each revocation row; test 401 on a copy.
4. Neutralise human accounts by service stop and store archive (SK-01/02), or by a disable operation if one has been built (D-41-11).
5. Seal key: stop sealing; decide escrow or destruction of the verification role at the end of the verification window (SK-05); record the decision without the key value.
6. Scrub environments (SK-07); remove scripted-password usage from runbooks.
7. Toolchain credentials (SK-10, SK-11) last, after the archive is mirrored and verified.
8. Run a secret scan over the final tree and a history scan (SK-14); store outputs under `evidence/` with hashes.
9. Record all steps in `retirement-evidence.md`; no secret value is ever written to a document, log or audit row (rule from `auth.py`, `tokens.py`).

### SK-3 Findings
| ID | Finding | Evidence | Impact | Risk | Confidence | Unresolved question |
|---|---|---|---|---|---|---|
| SKF-01 | [Verified Fact] No credential, key or token is stored in the repository, shipped configuration or logs | `secrets-hardening.md` SH-3 (scan: 0 findings in `hub`, `tests/hub`, wide scan of 26 paths) | Nothing to scrub from the tree today | Low | High | History scan (SK-14) not done |
| SKF-02 | [Verified Fact] Anchor seal key custody and rotation are undecided; no secret manager exists | SH-4; DQ-S24-02 | Destroying or losing the key can make a sealed anchor unverifiable; leaking it lets history be forged | Medium | High | D-41-13 |
| SKF-03 | [Inference] Revoking by destruction is unsafe for integrity keys: it trades secrecy for loss of verifiability, so SK-05 needs a documented end-of-life | `anchor_seal.py` (seal verification needs the key) | Archive evidence may become unverifiable | Medium | Medium | Verification window length |
| SKF-04 | [Unknown] Credentials of the three toolchain providers | `vendor-inventory.md` V-03..V-05; U-33-01, U-33-02 | Residual access after retirement | Medium | High | Owner inventory |
| SKF-05 | [Verified Fact] Env-var secrets are visible to other processes of the same OS user and in some crash dumps | SH-4 | Residual exposure on a decommissioned host | Low-Medium | Medium | Host wipe policy |

## Evidence References
See `evidence_sources`. Companion: `access-revocation-plan.md`, `decommission-checklist.md` steps C-01..C-08.

## Assumptions
- A-41-SK-1 [Assumption] The inventory SK-01..SK-14 is complete for the repository; external credentials are inventoried by the owner. Confirm: Engagement lead (Dinesh Naik).
- A-41-SK-2 [Assumption] The seal is not enabled on any store (default is opt-in and unsealed); not verified on a real host. Confirm: owner.
- A-41-SK-3 [Assumption] No credential was ever committed historically (a history scan was not run). Confirm: Build agent at clearance time.

## Unknowns
- U-41-SK-1 Whether `HUB_ANCHOR_SEAL_KEY` has ever been set outside tests.
- U-41-SK-2 Credential forms at the toolchain providers.
- U-41-SK-3 Git-history secret scan result.

## Unresolved Issues
- UI-41-SK-1 D-41-13 (seal key custody and end-of-life). Owner: Engagement lead (Dinesh Naik).

## Residual Risks
- RR-41-SK-1 A forgotten credential at a third party (Medium).
- RR-41-SK-2 Loss of the seal key before archives are verified (Medium).

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 41). |
