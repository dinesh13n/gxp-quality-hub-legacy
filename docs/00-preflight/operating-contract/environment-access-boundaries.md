---
stage: "0B — Provisional Operating Contract & Engineering Boundaries"
artifact: "environment-access-boundaries.md"
version: "v0.1"
date: "2026-10-17"
author_agent: "claude-fde-agent"
status: "DRAFT"
evidence_sources: ["environments/dev.env.example", "environments/staging.env.example", "environments/production-like.env.example", "compose.yaml", "Dockerfile", ".github/workflows/verify.yml", "operations/runbook.md L5", "docs/00-preflight/discovery/system-landscape.md", "docs/00-preflight/discovery/security-observability-overview.md SO-01..SO-03, SO-07"]
supersedes: "none"
---
## Summary

**No real dev/test/stage/production environment exists for this engagement.** The repo contains only example env files (`environments/*.env.example`), a Compose topology never evidenced as executed (U-09), and a CI workflow never evidenced as run (U-20). Services have no authentication and the staging / production-like examples bind `0.0.0.0` (SO-01, SO-03). Therefore the contract defines engagement tiers E0–E4 and **prohibits any production access by default**; any tier above E2 requires human approval and does not yet exist.

## Findings

### Environment evidence

| ID | Finding | Class | Evidence | Impact | Confidence |
|---|---|---|---|---|---|
| ENV-F1 | Three env examples: `dev` HOST=127.0.0.1 LOG_LEVEL=DEBUG; `staging` HOST=0.0.0.0 LOG_LEVEL=INFO; `production-like` HOST=0.0.0.0 LOG_LEVEL=WARN (PORT 8080, SOURCE_PORT 8090 in all) | [Verified Fact] | `environments/*.env.example` | Non-dev profiles expose unauthenticated services on all interfaces | High |
| ENV-F2 | `LOG_LEVEL` is unused by code | [Verified Fact] | SO-12 | Env profiles differ only by bind address in practice | High |
| ENV-F3 | Compose publishes 8080/8090 on host (`${HOST_PORT:-8080}:8080`), container runs as root, image copies whole build context incl. `data/` | [Verified Fact] | `compose.yaml` L8-9, L24-25; `Dockerfile`; `.dockerignore` | Building an image embeds the baseline DB; publishing ports exposes all data | High |
| ENV-F4 | CI (`verify.yml`) runs `unittest` then `app.generate --count 6000 --seed 4326 --reset` on push/PR | [Verified Fact] | `.github/workflows/verify.yml` | Pushing to a GitHub remote (OD-05) will trigger CI on GitHub-hosted runners — acceptable only because data is git-ignored and synthetic; still an egress/compute event | High |
| ENV-F5 | No component contacts any real external system | [Verified Fact] | `system-landscape.md` Summary; `operations/runbook.md` L5 | Production blast radius today = none | High |
| ENV-F6 | Docker is not installed on the inspection device | [Verified Fact] (0A) | `system-landscape.md` Unresolved Issues | E2 not yet available | High |

### Engagement environment tiers (PROVISIONAL — confirm Stage 25; production rules Stage 23/25; close Stage 37)

| Tier | Definition | Who / what may access | Permitted actions | Prohibited |
|---|---|---|---|---|
| E0 | Repository working tree on the engagement lead's device | Stage agents (read; write per `repository-write-boundaries.md`); orchestrator (git) | Read, grep, read-only git, read-only SQLite queries (`mode=ro` / `?immutable=1`), sha256 verification | Executing app code, tests, generators, servers; any write to `data/` |
| E1 | Disposable sandbox: full repo copy outside the working tree on the same device | Stage agents | Execute anything in the repo, regenerate data, run tests, start servers bound to **127.0.0.1 only** | Binding 0.0.0.0; outbound network calls from app code to non-local hosts |
| E2 | Local Docker/Compose on an isolated host network (not yet available) | Stage agents with HAR-05 approval | Compose up/down with ports bound to 127.0.0.1 | Publishing to LAN/internet; pushing images to registries |
| E3 | Shared/hosted test or staging environment (cloud, CI runners other than GitHub Actions on the private repo) | Nobody until approved | — | Everything until Stage 25 approval and an environment owner exists |
| E4 | Any production / real client system (MES/EBR, LIMS-QMS, partner gateway, real IdP) | **Nobody. Production write access is not granted to any person, tool or agent.** Read access also denied. | — | All access |

### Rules

- ENV-R1: Default bind address for anything the engagement runs is `127.0.0.1` (the `dev.env.example` profile). Using `staging`/`production-like` profiles requires HAR-05.
- ENV-R2: No credentials, tokens or secrets may be introduced to reach any environment; none are needed (SO-04).
- ENV-R3: E3/E4 access requests must name an environment owner — none exists (U-05) → GD-06.
- ENV-R4: GitHub Actions on the private remote is the only permitted hosted compute, contingent on OD-05 (remote creation) — PROVISIONAL, Stage 25.

## Evidence References

As cited. 0A execution evidence (sandbox `$HOME/fde_sbx/repo`, servers on 127.0.0.1) demonstrates E1 is workable.

## Assumptions

- A-05 (0A): Compose is the best proxy for "production-like" runtime — carried; confirm Stage 5.
- A-0B-03: The engagement lead's device is a single-user workstation, not a shared server. Confirm: Engagement lead (Dinesh Naik), Stage 2.

## Unknowns

- U-05 real deployment topology; U-09 Compose works; U-20 CI ever ran; U-22 identity provider.

## Unresolved Issues

- No environment owner exists for any tier (GD-06).

## Residual Risks

- R-04: unauthenticated services; residual if a later stage binds 0.0.0.0 on a shared network.

## Change History

| Version | Date | Author/agent | Change |
|---|---|---|---|
| v0.1 | 2026-10-17 | claude-fde-agent | Initial provisional environment tiers. |
