---
stage: "27 — Production Hardening"
artifact: "supply-chain-controls.md"
version: "v0.1"
date: "2026-10-25"
author_agent: "claude-fde-agent"
status: "IN REVIEW"
evidence_sources: ["tests/hub/test_tst_hub_co_05_legacy_paths_unchanged.py", "tests/hub/non_add_edits.json", "hub/security/sbom.py", "ci/hub-hardening.yml", ".github/workflows/verify.yml", "hub/guards/no_ai.py", "hub/store/hardening.py", "docs/27-hardening/evidence/mutation-s27.json", ".fde/orchestrator-decisions.md"]
supersedes: "none"
---
**Label: synthetic repository, unvalidated against any organisation. Status IN REVIEW: nothing here is an approval and no risk is accepted. Every acceptance, every decision and every sign-off named below is Dinesh Naik's (Engagement lead) and is not recorded by this stage. The product is No-AI (OD-08); `zone_h.holders` ships EMPTY.**

## Summary
Source integrity is protected by process and by tests rather than by signing: legacy paths are checked byte-for-byte against the `baseline-as-found` tag (TST-CO-05 a), every change to an existing hub file must be listed with a work item and a deviation (TST-CO-05 c, `non_add_edits.json`, 31 entries this stage), the data backup checksum is verified before and after every run, and all code runs in sandbox copies. Stage 27 adds a reproducible SBOM, a CI job file that gates on it, and a mutation gate script. What is absent is everything that needs infrastructure the repository does not have: signed commits or tags, artifact signing or provenance, SHA-pinned actions, a protected-branch configuration visible to the agent, and a build artifact (the hub is run from source).

## Findings
<!-- each tagged [Verified Fact] / [Inference] / [Assumption] / [Unknown] -->
### SC-1 Controls in place [Verified Fact unless marked]
| ID | Control | Mechanism | Evidence |
|---|---|---|---|
| SCC-01 | legacy code and `data/` byte-identical | TST-CO-05 a (diff vs tag `baseline-as-found`, includes `.github/`); `sha256sum -c ../_data-backup-2026-10-17/SHA256SUMS.txt` rc 0 before and after every run | group B green; every group log shows pre / post rc 0 |
| SCC-02 | every edit to an existing hub / hub-test file is declared | TST-CO-05 c against `main`: only added files plus listed `M` edits under `hub/` or `tests/hub/` | `tests/hub/non_add_edits.json` |
| SCC-03 | no AI / network-client dependency, no `urllib.request` / `http.client` outside `hub/adapters` | `hub.guards.no_ai` (R1 / R2), TST_CO_11, E-groups | `evidence/no-ai-check.json` |
| SCC-04 | SBOM reproducible and free of third-party code | `hub.security.sbom` (CycloneDX 1.5, no clock), B01 / B02, CI step | `sbom-summary.md` |
| SCC-05 | tests run only in sandbox copies outside the tree | `harness.build_pristine`, `assert_safe_sandbox` | all group runs |
| SCC-06 | change history is reviewable | branch `stage-27-hardening` from `main`, small commits, trailers; the orchestrator opens the PR and merges (OD-13) | git log |
| SCC-07 | store schema drift detected | per-component migration ledgers with sha256, `MigrationDrift`; H001 adds insert-only triggers | `STG27_H01..H03` |
| SCC-08 | error-code registry can only grow | regenerated registry compared with v0.2 | `STG27_R01` |
| SCC-09 | hash-pinned test datasets | S26 corpus sha256 (B01 of Stage 26) | S26 |
| SCC-10 | tests can fail (mutation gate) | `docs/27-hardening/evidence/s27_mutation_gate.py`: 13 mutants, 13 killed | `mutation-s27.json` |
| SCC-11 | CI additions as code | `ci/hub-hardening.yml`: read-only token, no secrets, 3.12 and 3.13, floor check, No-AI gate, secret scan, SBOM reproducibility, static-check gate | `STG27_C01` |
| SCC-12 | structure cannot regress silently | static-check ratchet: 0 two-cycles, 0 three-cycles, at most 9 over-complex functions | `STG27_S01` |

### SC-2 Gaps [Inference unless marked]
| ID | Gap | Impact | Risk | Route |
|---|---|---|---|---|
| SCG-01 | GitHub Actions referenced by tag, not by commit SHA ([Verified Fact]: `@v4`, `@v5`) | a moved tag changes what runs | Low-Medium | D-27-03 |
| SCG-02 | the new workflow is not installed (`.github/` is protected, HAR-07) | the 3.12 job and gates do not run on push | Medium | D-27-03 |
| SCG-03 | commits and tags are not signed ([Unknown]: no signing key is configured in this environment) | authorship rests on the git history and the OD log | Low-Medium | Dinesh |
| SCG-04 | no build artifact, no provenance or signing: the hub is deployed from source | nothing to verify at install time | Low (no deployment exists) | Stage 30 |
| SCG-05 | branch protection and required reviews are not visible [Unknown] | an unreviewed merge may be possible | Unknown | Dinesh (U-27-02) |
| SCG-06 | legacy container base image by tag; no image scan tool available | silent image change | Low-Medium | D-27-06 |
| SCG-07 | secret scanning is a regex heuristic and git history is not scanned | an old secret could remain | Low | backlog |
| SCG-08 | this agent cannot push (no credentials), so GitHub-side checks have not run on these commits | none for the content; the PR will run the existing workflow | Info | orchestrator |

### SC-3 Install path for the CI additions [Assumption]
1. Dinesh approves D-27-03 (HAR-07).
2. Copy `ci/hub-hardening.yml` to `.github/workflows/hub-hardening.yml` in a PR; replace `@v4` / `@v5` by the commit SHAs the maintainer looks up.
3. First hosted run produces the 3.12 / 3.13 evidence that RTR-08 needs. The hub-test step warns and skips if the Stage 0A backup is not next to the checkout (a hosted runner will not have it): that data-dependent step needs a decision on where the backup lives in CI [Unknown].

## Evidence References
- `tests/hub/non_add_edits.json`, `tests/hub/test_tst_hub_co_05_*`
- `ci/hub-hardening.yml`, `.github/workflows/verify.yml`
- `docs/27-hardening/evidence/mutation-s27.json`, `s27_mutation_gate.py`
- `docs/23-human-control/operating-contract-updates.md` (HAR-05, HAR-07, HAR-08, HAR-13)

## Assumptions
- A-27-07 `ci/` is a holding place, not a deployment.
- The orchestrator's PR and merge process (OD-13) is the review control.

## Unknowns
- U-27-02 branch protection; U-27-12 signing keys; U-27-13 how CI will get the Stage 0A backup.

## Unresolved Issues
- D-27-03 (install, SHA pinning).

## Residual Risks
- Supply-chain controls that need infrastructure are absent; the compensating controls are tests, process and the OD log.
- A hosted-runner difference (Python patch level, SQLite build) may change a test result; unknown until the first run.

## Change History
| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | claude-fde-agent | First issue (Stage 27 BUILD). |
