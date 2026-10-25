---
stage: "27 — Production Hardening"
artifact: "secrets-hardening.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["hub/security/scan.py", "hub/security/auth.py", "hub/security/anchor_seal.py", "hub/store/db.py", "hub/security/audit.py", "docs/27-hardening/evidence/secret-and-deletion-scan.json", "tests/hub/test_tst_hub_stg27_store.py", "tests/hub/test_tst_hub_stg26_input.py"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW: nothing here is an approval and no risk is accepted. Every acceptance, every decision and every sign-off named below is Dinesh Naik's (Engagement lead) and is not recorded by this stage. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
No credential, key or token is stored in the repository, in the shipped configuration or in the hub's logs, and the stage's scans found none (0 findings in `hub`, `tests`, `ci`, `docs`, all legacy source directories and the container files). Secrets at rest in the hub are hashes or digests; the two operator secrets that must exist (`HUB_ANCHOR_SEAL_KEY`, and the password passed to scripted CLI commands) are read from the environment and never echoed. Stage 27 added owner-only file modes for the store, its directory and a new audit anchor file. Key custody, rotation and a secret manager are not built and are decisions for Dinesh.

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SH-1 Secret inventory [Verified Fact: from the code]
| Secret | Where it lives | Form at rest | Handling |
|---|---|---|---|
| user password | `principal.pw_hash`, `pw_salt` | PBKDF2-HMAC-SHA256, 600,000 iterations, 16-byte salt | never logged; leakage sweep B07 found 0 hits in 469 responses |
| session token | `session.token_sha256` | sha256 of the token | token returned once at login |
| service token | `service_token` | `svc_` + 48 hex, sha256 stored | revocable; expiry optional (RS-08) |
| re-authentication proof | derived, not stored | sha256 of 'reauth:' + session digest + ':' + reauth time | window 300 s |
| audit anchor | file at `audit.anchor_path`, outside the DB directory | JSON lines (hash, seq, time) | NEW file created 0600 (S27-DEV-14) |
| anchor seal key | environment variable `HUB_ANCHOR_SEAL_KEY` | HMAC key, opt-in seal | read by `anchor_seal.load_key`, never echoed |
| scripted passwords | `HUB_NEW_USER_PASSWORD`, `HUB_RUN_PASSWORD` | environment variables | used by two CLIs; interactive `getpass` otherwise |
| store file | `<data-dir>/hub.sqlite3` | holds the hashes above | group / other bits removed on open; data directory created 0700 (S27-DEV-14) |

### SH-2 What Stage 27 changed [Verified Fact]
- `open_hub` creates a new data directory 0700 and removes group and other bits from the store file. It never adds a bit: the Stage 26 test C01 made the file read-only on purpose and a first draft that forced 0600 silently made it writable again; the shipped rule only tightens (test `STG27_H04` covers 0666 -> 0600 and 0444 -> 0400).
- `audit.write_anchor` creates a new anchor file with mode 0600 (existing files keep their mode); content and fsync are unchanged.
- The H001 ledger and the rate limiter store no secret.

### SH-3 Scans [Verified Fact]
- Secret scan (`hub.security.scan`, regex heuristic: private-key blocks, cloud / API token shapes, literal credential assignments): 0 findings over `hub`, `tests/hub` (the product scan) and 0 over the wide scan of 26 paths (`evidence/secret-and-deletion-scan.json`).
- Deletion-path grep: 0 SQL deletes or drops of a retained table in product code.
- Test secrets: the synthetic holders `holder-1`, `holder-2` and the test passwords exist only inside sandbox stores built by the tests; the shipped config keeps `zone_h.holders` empty (test A02 runs with exactly that).
- Debug behaviour: no debug flag, no `eval` / `exec` / `shell=True` / `pickle`, 17 `print` statements (CLI output) in `hub/` ([Verified Fact]: grep, `hub/` only).

### SH-4 Gaps [Inference unless marked]
- RS-03 the anchor is on the same host and unsealed by default: a host-level attacker can rewrite chain and anchor (S26 C03 shows it). The opt-in seal exists; key custody is not decided (DQ-S24-02).
- Environment variables are visible to other processes of the same user and in crash dumps on some systems [Inference].
- No secret manager, no rotation procedure for the seal key, no scan of git history [Unknown].

## Evidence References
- `docs/27-hardening/evidence/secret-and-deletion-scan.json`
- `tests/hub/test_tst_hub_stg27_store.py` H04; `tests/hub/test_tst_hub_stg26_input.py` B07 (leakage sweep)
- `hub/security/controls.py` SC-01 .. SC-26 (values unchanged)

## Assumptions
- A-27-08 owner-only modes are right for a single-user host.
- The regex scan is a heuristic (Stage 24 said so); a clean result is evidence of no known pattern, not of no secret.

## Unknowns
- U-27-07 Where a real deployment keeps the seal key and the operator passwords.
- U-27-08 Whether git history holds secrets (not scanned).

## Unresolved Issues
- DQ-S24-02 anchor strength (A unsealed / B opt-in seal with key custody / C external witness) is open; recommended default B.

## Residual Risks
- Host-level access defeats the audit chain (RS-03, RTR-11).
- Environment-variable secrets are a convenience, not a vault.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 27 BUILD). |
